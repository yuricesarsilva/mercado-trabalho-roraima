import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from .labels import coefficient_label, coefficient_short_label, reference_label
from .paths import MODELS_DIR, TABLES_DIR


MINIMAL_FORMULA_RHS = "formal + mulher + preto_pardo + formal:mulher + formal:preto_pardo"

BASE_FORMULA_RHS = (
    f"{MINIMAL_FORMULA_RHS} "
    "+ idade + idade2 + C(escolaridade) "
    "+ C(ocupacao_grupo) + C(atividade_grupo) + C(periodo)"
)


def markdown_table(df: pd.DataFrame, floatfmt: str = ".4f") -> str:
    formatted = df.copy()
    for column in formatted.select_dtypes(include="number").columns:
        formatted[column] = formatted[column].map(lambda value: format(value, floatfmt))
    formatted = formatted.astype(str)
    header = "| " + " | ".join(formatted.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(formatted.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in formatted.to_numpy()]
    return "\n".join([header, separator, *rows])


def estimate(
    df: pd.DataFrame,
    dependent: str,
    label: str,
    title: str,
    rhs: str = BASE_FORMULA_RHS,
    extra_rhs: str = "",
    log_dependent: bool = True,
) -> None:
    if extra_rhs:
        rhs = f"{rhs} + {extra_rhs}"
    formula = f"{dependent} ~ {rhs}"

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
    if log_dependent:
        coef["efeito_percentual_aprox"] = (np.exp(coef["coeficiente"]) - 1) * 100
    else:
        coef["efeito_absoluto_aprox"] = coef["coeficiente"]
    coef.to_csv(TABLES_DIR / f"modelo_base_{label}.csv", encoding="utf-8")
    coef.to_csv(MODELS_DIR / f"modelo_base_{label}_rotulado.csv", encoding="utf-8")

    stats = pd.DataFrame(
        {"chave": ["nobs", "rsquared"], "valor": [model.nobs, model.rsquared]}
    )
    stats.to_csv(TABLES_DIR / f"modelo_base_{label}_estatisticas.csv", index=False, encoding="utf-8")

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

    labelled = coef.reset_index(names="termo_original")
    labelled_output = MODELS_DIR / f"modelo_base_{label}_rotulado.md"
    labelled_output.write_text(
        "\n".join(
            [
                f"# {title}",
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
