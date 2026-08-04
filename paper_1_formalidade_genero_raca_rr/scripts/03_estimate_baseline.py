from pathlib import Path
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.labels import coefficient_label, coefficient_short_label, reference_label
from pnadc_rr.paths import MODELS_DIR, PROCESSED_DIR, TABLES_DIR, ensure_project_dirs


def markdown_table(df: pd.DataFrame, floatfmt: str = ".4f") -> str:
    formatted = df.copy()
    for column in formatted.select_dtypes(include="number").columns:
        formatted[column] = formatted[column].map(lambda value: format(value, floatfmt))
    formatted = formatted.astype(str)
    header = "| " + " | ".join(formatted.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(formatted.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in formatted.to_numpy()]
    return "\n".join([header, separator, *rows])


def estimate(df: pd.DataFrame, dependent: str, label: str) -> None:
    formula = (
        f"{dependent} ~ formal + mulher + preto_pardo "
        "+ formal:mulher + formal:preto_pardo "
        "+ idade + idade2 + C(escolaridade) "
        "+ C(ocupacao_grupo) + C(atividade_grupo) + C(periodo)"
    )

    model = smf.wls(formula=formula, data=df, weights=df["peso"]).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["upa"]},
    )

    txt_output = MODELS_DIR / f"modelo_base_{label}.txt"
    summary_text = model.summary().as_text()
    txt_output.write_text(summary_text, encoding="utf-8")

    coef = model.params.rename("coeficiente").to_frame()
    coef.insert(0, "rotulo", [coefficient_label(term) for term in coef.index])
    coef.insert(1, "referencia", [reference_label(term) for term in coef.index])
    coef["erro_padrao"] = model.bse
    coef["p_valor"] = model.pvalues
    coef["efeito_percentual_aprox"] = (np.exp(coef["coeficiente"]) - 1) * 100
    coef.to_csv(TABLES_DIR / f"modelo_base_{label}.csv", encoding="utf-8")
    coef.to_csv(MODELS_DIR / f"modelo_base_{label}_rotulado.csv", encoding="utf-8")

    short_name_map = {
        original: coefficient_short_label(original)
        for original in model.model.exog_names
    }
    original_xnames = list(model.model.data.xnames)
    model.model.data.xnames = [short_name_map[name] for name in original_xnames]
    short_summary_text = model.summary().as_text()
    model.model.data.xnames = original_xnames
    short_txt_output = MODELS_DIR / f"modelo_base_{label}_nomes_curtos.txt"
    short_txt_output.write_text(short_summary_text, encoding="utf-8")

    short_dictionary = (
        pd.DataFrame(
            {
                "nome_original": list(short_name_map.keys()),
                "nome_curto": list(short_name_map.values()),
                "rotulo": [coefficient_label(term) for term in short_name_map.keys()],
                "referencia": [reference_label(term) for term in short_name_map.keys()],
            }
        )
        .sort_values("nome_curto")
    )
    short_dictionary.to_csv(MODELS_DIR / f"dicionario_nomes_curtos_{label}.csv", index=False, encoding="utf-8")

    model_title = {
        "ln_renda_hora": "Modelo-base: log do rendimento por hora",
        "ln_renda_mensal": "Modelo-base: log do rendimento mensal",
    }.get(label, f"Modelo-base: {label}")
    labelled = coef.reset_index(names="termo_original")
    labelled_output = MODELS_DIR / f"modelo_base_{label}_rotulado.md"
    labelled_output.write_text(
        "\n".join(
            [
                f"# {model_title}",
                "",
                f"- Observações usadas: {int(model.nobs)}",
                f"- R²: {model.rsquared:.4f}",
                "- Estimação: WLS com peso amostral e erros-padrão clusterizados por UPA.",
                "",
                "## Coeficientes Rotulados",
                "",
                markdown_table(labelled),
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"saved: {txt_output}")
    print(f"saved: {short_txt_output}")
    print(f"saved: {labelled_output}")


def main() -> None:
    ensure_project_dirs()
    input_path = PROCESSED_DIR / "pnadc_rr_analitica.parquet"
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    df = pd.read_parquet(input_path)
    common = df.loc[
        df["formal"].notna()
        & df["mulher"].notna()
        & df["preto_pardo"].notna()
        & df["peso"].notna()
        & df["upa"].notna()
    ].copy()

    hourly = common.loc[common["renda_hora"] > 0].copy()
    hourly["ln_renda_hora"] = np.log(hourly["renda_hora"])
    estimate(hourly, "ln_renda_hora", "ln_renda_hora")

    monthly = common.loc[common["renda_mensal"] > 0].copy()
    monthly["ln_renda_mensal"] = np.log(monthly["renda_mensal"])
    estimate(monthly, "ln_renda_mensal", "ln_renda_mensal")


if __name__ == "__main__":
    main()
