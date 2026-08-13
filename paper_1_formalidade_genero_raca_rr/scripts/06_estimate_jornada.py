from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.estimation import estimate, markdown_table
from pnadc_rr.paths import PROCESSED_DIR, PROJECT_DIR, TABLES_DIR, ensure_project_dirs


KEY_TERMS = [
    "formal",
    "mulher",
    "preto_pardo",
    "formal:mulher",
    "formal:preto_pardo",
]

MODEL_ORDER = [
    ("ln_renda_mensal_real", "Renda mensal real, sem controle de horas"),
    ("ln_renda_mensal_real_com_horas", "Renda mensal real, controlando por horas"),
    ("ln_renda_hora_real", "Renda por hora real"),
    ("horas_semanais", "Horas semanais habituais (variável dependente)"),
]


def build_jornada_sample(df: pd.DataFrame) -> pd.DataFrame:
    common = df.loc[
        df["formal"].notna()
        & df["mulher"].notna()
        & df["preto_pardo"].notna()
        & df["peso"].notna()
        & df["upa"].notna()
        & (df["renda_mensal_real"] > 0)
        & df["horas_semanais_principal"].notna()
        & (df["horas_semanais_principal"] > 0)
    ].copy()
    return common


def pvalue_text(p_value: float) -> str:
    if p_value < 0.01:
        return "significativo a 1%"
    if p_value < 0.05:
        return "significativo a 5%"
    if p_value < 0.10:
        return "significativo a 10%"
    return "não significativo aos níveis usuais"


def comparison_row(models: dict[str, pd.DataFrame], term: str) -> dict:
    row = {"termo": term}
    for label, _ in MODEL_ORDER:
        coef_row = models[label].loc[term]
        if label == "horas_semanais":
            row[f"{label}"] = f"{coef_row['coeficiente']:+.2f} h/sem ({pvalue_text(coef_row['p_valor'])})"
        else:
            effect = coef_row["efeito_percentual_aprox"]
            row[f"{label}"] = f"{effect:+.1f}% ({pvalue_text(coef_row['p_valor'])})"
    return row


def mechanism_sentence(models: dict[str, pd.DataFrame], term: str, subject: str) -> str:
    sem_horas = models["ln_renda_mensal_real"].loc[term]
    com_horas = models["ln_renda_mensal_real_com_horas"].loc[term]
    hora = models["ln_renda_hora_real"].loc[term]
    horas_dv = models["horas_semanais"].loc[term]

    effect_sem = (np.exp(sem_horas["coeficiente"]) - 1) * 100
    effect_com = (np.exp(com_horas["coeficiente"]) - 1) * 100
    effect_hora = (np.exp(hora["coeficiente"]) - 1) * 100
    effect_horas_dv = horas_dv["coeficiente"]

    return (
        f"Para {subject}: o diferencial de renda mensal real é {effect_sem:+.1f}% sem controlar por horas "
        f"e {effect_com:+.1f}% controlando por horas; o diferencial de renda por hora real é {effect_hora:+.1f}%; "
        f"e a diferença nas horas semanais habituais é {effect_horas_dv:+.2f} horas/semana "
        f"({pvalue_text(horas_dv['p_valor'])})."
    )


def main() -> None:
    ensure_project_dirs()
    input_path = PROCESSED_DIR / "pnadc_rr_analitica.parquet"
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    df = pd.read_parquet(input_path)
    sample = build_jornada_sample(df)

    monthly_with_hours = sample.copy()
    monthly_with_hours["ln_renda_mensal_real"] = np.log(monthly_with_hours["renda_mensal_real"])
    estimate(
        monthly_with_hours,
        "ln_renda_mensal_real",
        "ln_renda_mensal_real_com_horas",
        "Mecanismo de jornada: log do rendimento mensal real, controlando por horas",
        extra_rhs="horas_semanais_principal",
    )

    hours_model = sample.copy()
    estimate(
        hours_model,
        "horas_semanais_principal",
        "horas_semanais",
        "Mecanismo de jornada: horas semanais habituais como variável dependente",
        log_dependent=False,
    )

    # Modelos de referência (já estimados por scripts/03_estimate_baseline.py), reestimados
    # na mesma amostra usada aqui para manter a decomposição comparável.
    monthly_no_hours = sample.copy()
    monthly_no_hours["ln_renda_mensal_real"] = np.log(monthly_no_hours["renda_mensal_real"])
    estimate(
        monthly_no_hours,
        "ln_renda_mensal_real",
        "ln_renda_mensal_real_amostra_jornada",
        "Referência (amostra do mecanismo): log do rendimento mensal real, sem controle de horas",
    )

    hourly = sample.loc[sample["renda_hora_real"] > 0].copy()
    hourly["ln_renda_hora_real"] = np.log(hourly["renda_hora_real"])
    estimate(
        hourly,
        "ln_renda_hora_real",
        "ln_renda_hora_real_amostra_jornada",
        "Referência (amostra do mecanismo): log do rendimento por hora real",
    )

    models = {
        "ln_renda_mensal_real": pd.read_csv(
            TABLES_DIR / "modelo_base_ln_renda_mensal_real_amostra_jornada.csv", index_col=0
        ),
        "ln_renda_mensal_real_com_horas": pd.read_csv(
            TABLES_DIR / "modelo_base_ln_renda_mensal_real_com_horas.csv", index_col=0
        ),
        "ln_renda_hora_real": pd.read_csv(
            TABLES_DIR / "modelo_base_ln_renda_hora_real_amostra_jornada.csv", index_col=0
        ),
        "horas_semanais": pd.read_csv(TABLES_DIR / "modelo_base_horas_semanais.csv", index_col=0),
    }

    comparison = pd.DataFrame([comparison_row(models, term) for term in KEY_TERMS])
    comparison.columns = ["termo"] + [label for label, _ in MODEL_ORDER]

    sentences = [
        mechanism_sentence(models, "formal", "a formalidade, em relação à informalidade"),
        mechanism_sentence(models, "mulher", "ser mulher, em relação a ser homem"),
        mechanism_sentence(models, "preto_pardo", "ser pessoa preta ou parda, em relação aos demais grupos de raça/cor"),
    ]

    output = PROJECT_DIR / "docs" / "mecanismo_jornada.md"
    lines = [
        "# Mecanismo de Jornada: Preço do Trabalho vs. Horas Trabalhadas",
        "",
        "Este arquivo é gerado por `scripts/06_estimate_jornada.py` e decompõe os diferenciais de "
        "rendimento mensal real em efeito-preço (renda por hora) e efeito-quantidade (horas semanais). "
        "Todos os modelos usam a mesma amostra: pessoas ocupadas com renda mensal real e horas semanais "
        "habituais válidas (`>0`), com os mesmos controles do modelo-base "
        "(idade, idade², escolaridade, ocupação, atividade e efeitos fixos de ano/trimestre).",
        "",
        "## Comparação dos Coeficientes-Chave",
        "",
        markdown_table(comparison),
        "",
        "## Interpretação",
        "",
        *[f"- {sentence}" for sentence in sentences],
        "",
        (
            "- Leitura: se o efeito de renda mensal muda pouco entre `sem controle de horas` e "
            "`com controle de horas`, e se aproxima do efeito de renda por hora, o diferencial é "
            "majoritariamente um efeito-preço (o grupo ganha menos por hora trabalhada). Se o efeito de "
            "horas semanais é grande e estatisticamente significativo, parte do diferencial de renda "
            "mensal decorre de jornadas mais curtas (efeito-quantidade), não apenas do preço do trabalho."
        ),
        "",
    ]
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved: {output}")


if __name__ == "__main__":
    main()
