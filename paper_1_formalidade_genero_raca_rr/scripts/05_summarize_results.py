from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.paths import PROJECT_DIR, TABLES_DIR


KEY_TERMS = [
    "formal",
    "mulher",
    "preto_pardo",
    "formal:mulher",
    "formal:preto_pardo",
]


def markdown_table(df: pd.DataFrame, floatfmt: str | None = None) -> str:
    formatted = df.copy()
    if floatfmt:
        for column in formatted.select_dtypes(include="number").columns:
            formatted[column] = formatted[column].map(lambda value: format(value, floatfmt))
    formatted = formatted.astype(str)
    header = "| " + " | ".join(formatted.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(formatted.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in formatted.to_numpy()]
    return "\n".join([header, separator, *rows])


def read_key_model(label: str) -> pd.DataFrame:
    path = TABLES_DIR / f"modelo_base_{label}.csv"
    df = pd.read_csv(path, index_col=0)
    df = df.loc[df.index.intersection(KEY_TERMS)].copy()
    df.insert(0, "modelo", label)
    return df.reset_index(names="variavel")


def pvalue_text(p_value: float) -> str:
    if p_value < 0.01:
        return "estatisticamente diferente de zero ao nível de 1%"
    if p_value < 0.05:
        return "estatisticamente diferente de zero ao nível de 5%"
    if p_value < 0.10:
        return "estatisticamente diferente de zero ao nível de 10%"
    return "não estatisticamente diferente de zero aos níveis usuais"


def coefficient_sentence(models: pd.DataFrame, model: str, variable: str, subject: str) -> str:
    row = models.loc[(models["modelo"] == model) & (models["variavel"] == variable)].iloc[0]
    effect = (np.exp(row["coeficiente"]) - 1) * 100
    direction = "maior" if effect > 0 else "menor"
    return (
        f"No modelo de {model.replace('_', ' ')}, para {subject}, observa-se rendimento "
        f"{abs(effect):.1f}% {direction}, e o coeficiente é {pvalue_text(row['p_valor'])}."
    )


def interpretation_text(models: pd.DataFrame) -> list[str]:
    return [
        (
            "Os modelos principais abaixo usam rendimento real, deflacionado pelo deflator oficial "
            "trimestral da PNAD Contínua (IBGE), aplicado por UF e trimestre. Os modelos em valores "
            "nominais permanecem disponíveis em `outputs/tables/` apenas para comparação."
        ),
        coefficient_sentence(
            models,
            "ln_renda_hora_real",
            "formal",
            "a formalidade, em relação à informalidade",
        ),
        coefficient_sentence(
            models,
            "ln_renda_hora_real",
            "mulher",
            "ser mulher, em relação a ser homem",
        ),
        coefficient_sentence(
            models,
            "ln_renda_hora_real",
            "preto_pardo",
            "ser pessoa preta ou parda, em relação aos demais grupos de raça/cor",
        ),
        coefficient_sentence(
            models,
            "ln_renda_mensal_real",
            "mulher",
            "ser mulher, quando a variável dependente é rendimento mensal real",
        ),
        (
            "A diferença entre os modelos de rendimento mensal e rendimento por hora é substantiva: "
            "quando usamos renda mensal, parte do diferencial de gênero também reflete diferenças de jornada; "
            "quando usamos renda por hora, a comparação se aproxima mais do preço do trabalho."
        ),
        (
            "Estes resultados ainda devem ser lidos como diferenciais condicionais, não como efeitos causais. "
            "Eles controlam por ocupação, atividade, escolaridade, idade e período, mas a seleção para o emprego formal "
            "continua potencialmente endógena."
        ),
        (
            "Nota metodológica: como o modelo já satura os efeitos fixos de ano/trimestre, deflacionar o "
            "rendimento não altera os coeficientes de formal, mulher, preto/pardo, suas interações ou os "
            "demais controles — o ajuste de preços é absorvido inteiramente pela constante e pelos efeitos "
            "fixos de período, já que o deflator só varia por ano/trimestre. A deflação segue sendo necessária "
            "para descrever a evolução do nível de renda ao longo do tempo e para qualquer especificação de "
            "robustez que não inclua efeitos fixos de período completos."
        ),
    ]


def main() -> None:
    totals = pd.read_csv(TABLES_DIR / "auditoria_totais.csv")
    formality = pd.read_csv(TABLES_DIR / "auditoria_formalidade.csv")
    cells = pd.read_csv(TABLES_DIR / "auditoria_formalidade_genero_raca.csv")
    models = pd.concat(
        [
            read_key_model("ln_renda_hora_real"),
            read_key_model("ln_renda_mensal_real"),
            read_key_model("ln_renda_hora"),
            read_key_model("ln_renda_mensal"),
        ],
        ignore_index=True,
    )

    output = PROJECT_DIR / "docs" / "resumo_resultados_correntes.md"
    lines = [
        "# Resumo dos Resultados Correntes",
        "",
        "Este arquivo é gerado a partir das tabelas em `outputs/tables/`.",
        "",
        "## Auditoria Amostral",
        "",
        markdown_table(totals),
        "",
        "## Formalidade",
        "",
        markdown_table(formality),
        "",
        "## Formalidade, Gênero e Raça/Cor",
        "",
        markdown_table(cells),
        "",
        "## Coeficientes-Chave",
        "",
        markdown_table(
            models[
                [
                    "variavel",
                    "rotulo",
                    "referencia",
                    "modelo",
                    "coeficiente",
                    "erro_padrao",
                    "p_valor",
                    "efeito_percentual_aprox",
                ]
            ],
            floatfmt=".4f",
        ),
        "",
        "## Interpretação Sintética",
        "",
        "A interpretação abaixo resume a execução corrente do pipeline. Ela não substitui a especificação final do paper.",
        "",
        *[f"- {sentence}" for sentence in interpretation_text(models)],
        "",
    ]
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved: {output}")


if __name__ == "__main__":
    main()
