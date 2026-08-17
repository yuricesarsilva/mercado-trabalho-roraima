"""Evolução temporal dos diferenciais de formalidade, gênero e raça/cor.

Estende o modelo-base (rendimento por hora real) com interações `termo:C(periodo)`
para `formal`, `mulher` e `preto_pardo`, permitindo que cada diferencial varie
livremente ano a ano (2016T4-2025T4) em vez de ser constante no tempo, como no
modelo-base de `scripts/03_estimate_baseline.py`.

Gera:
- outputs/tables/tendencia_anual.csv: efeito percentual aproximado por termo e ano,
  com IC 95%.
- outputs/tables/tendencia_linear.csv: robustez com uma única inclinação linear
  (termo:Ano) por termo, para resumir "aumentando" vs. "diminuindo" em um número.
- outputs/figures/tendencia_temporal.(pdf|png): gráfico de pequenos múltiplos.
- docs/evolucao_temporal.md: tabela e interpretação.
"""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.estimation import BASE_FORMULA_RHS, estimate, markdown_table
from pnadc_rr.paths import (
    FIGURES_DIR,
    PROCESSED_DIR,
    PROJECT_DIR,
    TABLES_DIR,
    ensure_project_dirs,
)


BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
GRAY_GRID = "#e1e0d9"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial"],
        "axes.edgecolor": GRAY_GRID,
        "axes.labelcolor": INK_SECONDARY,
        "xtick.color": INK_SECONDARY,
        "ytick.color": INK,
        "text.color": INK,
        "axes.grid": True,
        "grid.color": GRAY_GRID,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "font.size": 11,
    }
)

TERMS = ["formal", "mulher", "preto_pardo"]
TERM_COLORS = {"formal": BLUE, "mulher": ORANGE, "preto_pardo": AQUA}
TERM_TITLES = {
    "formal": "Prêmio de formalidade\n(ref.: informal)",
    "mulher": "Diferencial de gênero\n(ref.: homem)",
    "preto_pardo": "Diferencial de raça/cor\n(ref.: branco/amarelo/indígena)",
}


def build_sample(df: pd.DataFrame) -> pd.DataFrame:
    common = df.loc[
        df["formal"].notna()
        & df["mulher"].notna()
        & df["preto_pardo"].notna()
        & df["peso"].notna()
        & df["upa"].notna()
        & (df["renda_hora_real"] > 0)
    ].copy()
    common["ln_renda_hora_real"] = np.log(common["renda_hora_real"])
    return common


def year_effects(model, periods: list[str], term: str) -> pd.DataFrame:
    """Coeficiente acumulado (base + interação com o período) por ano, com
    erro-padrão obtido via var(a+b) = var(a) + var(b) + 2*cov(a,b)."""
    reference = periods[0]
    cov = model.cov_params()
    rows = []
    for periodo in periods:
        if periodo == reference:
            coef = model.params[term]
            se = model.bse[term]
        else:
            inter_name = f"{term}:C(periodo)[T.{periodo}]"
            coef = model.params[term] + model.params[inter_name]
            var = (
                cov.loc[term, term]
                + cov.loc[inter_name, inter_name]
                + 2 * cov.loc[term, inter_name]
            )
            se = np.sqrt(var)
        p_valor = 2 * (1 - stats.norm.cdf(abs(coef / se)))
        rows.append(
            {
                "periodo": periodo,
                "ano": int(periodo[:4]),
                "termo": term,
                "coeficiente": coef,
                "erro_padrao": se,
                "p_valor": p_valor,
            }
        )
    result = pd.DataFrame(rows)
    result["efeito_percentual_aprox"] = (np.exp(result["coeficiente"]) - 1) * 100
    result["ic95_inf"] = (np.exp(result["coeficiente"] - 1.96 * result["erro_padrao"]) - 1) * 100
    result["ic95_sup"] = (np.exp(result["coeficiente"] + 1.96 * result["erro_padrao"]) - 1) * 100
    return result


def fig_tendencia(trends: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8))
    for ax, term in zip(axes, TERMS):
        sub = trends.loc[trends["termo"] == term].sort_values("ano")
        color = TERM_COLORS[term]
        ax.fill_between(sub["ano"], sub["ic95_inf"], sub["ic95_sup"], color=color, alpha=0.18, zorder=1)
        ax.plot(sub["ano"], sub["efeito_percentual_aprox"], color=color, linewidth=2, zorder=3)
        ax.scatter(sub["ano"], sub["efeito_percentual_aprox"], color=color, s=28, zorder=4)
        ax.axhline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", zorder=0)
        ax.set_title(TERM_TITLES[term], fontsize=10.5)
        ax.set_xticks(sub["ano"].tolist())
        ax.set_xticklabels(sub["ano"].tolist(), rotation=45, ha="right", fontsize=8.5)
        ax.spines[["top", "right"]].set_visible(False)
        if ax is axes[0]:
            ax.set_ylabel("Efeito percentual aprox. (%)")
    fig.suptitle(
        "Evolução anual dos diferenciais condicionais — renda por hora real (IC 95%)",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "tendencia_temporal.pdf", bbox_inches="tight")
    fig.savefig(FIGURES_DIR / "tendencia_temporal.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"saved: {FIGURES_DIR / 'tendencia_temporal.pdf'}")


def main() -> None:
    ensure_project_dirs()
    input_path = PROCESSED_DIR / "pnadc_rr_analitica.parquet"
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    df = pd.read_parquet(input_path)
    sample = build_sample(df)
    periods = sorted(sample["periodo"].unique())

    # Modelo flexível: um coeficiente livre por ano para formal, mulher e preto_pardo.
    flex_extra = "formal:C(periodo) + mulher:C(periodo) + preto_pardo:C(periodo)"
    estimate(
        sample,
        "ln_renda_hora_real",
        "ln_renda_hora_real_tendencia_anual",
        "Tendência anual: log do rendimento por hora real, com interações termo x período",
        extra_rhs=flex_extra,
    )
    flex_model = smf.wls(
        formula=f"ln_renda_hora_real ~ {BASE_FORMULA_RHS} + {flex_extra}",
        data=sample,
        weights=sample["peso"],
    ).fit(cov_type="cluster", cov_kwds={"groups": sample["upa"]})

    trends = pd.concat([year_effects(flex_model, periods, term) for term in TERMS], ignore_index=True)
    trends.to_csv(TABLES_DIR / "tendencia_anual.csv", index=False, encoding="utf-8")
    print(f"saved: {TABLES_DIR / 'tendencia_anual.csv'}")

    # Robustez: uma única inclinação linear por termo (termo:Ano), para resumir a
    # direção da tendência em um número. Ano não entra sozinho pois já é absorvido
    # por C(periodo) no modelo-base.
    linear_extra = "formal:Ano + mulher:Ano + preto_pardo:Ano"
    estimate(
        sample,
        "ln_renda_hora_real",
        "ln_renda_hora_real_tendencia_linear",
        "Tendência linear: log do rendimento por hora real, com inclinação termo x ano",
        extra_rhs=linear_extra,
    )
    linear_model = smf.wls(
        formula=f"ln_renda_hora_real ~ {BASE_FORMULA_RHS} + {linear_extra}",
        data=sample,
        weights=sample["peso"],
    ).fit(cov_type="cluster", cov_kwds={"groups": sample["upa"]})

    linear_rows = []
    for term in TERMS:
        row = linear_model.params.filter(like=f"{term}:Ano")
        name = row.index[0]
        coef = linear_model.params[name]
        se = linear_model.bse[name]
        p_valor = linear_model.pvalues[name]
        linear_rows.append(
            {
                "termo": term,
                "inclinacao_log_por_ano": coef,
                "erro_padrao": se,
                "p_valor": p_valor,
                "efeito_percentual_aprox_por_ano": (np.exp(coef) - 1) * 100,
            }
        )
    linear_trends = pd.DataFrame(linear_rows)
    linear_trends.to_csv(TABLES_DIR / "tendencia_linear.csv", index=False, encoding="utf-8")
    print(f"saved: {TABLES_DIR / 'tendencia_linear.csv'}")

    fig_tendencia(trends)

    # --- docs/evolucao_temporal.md ---
    def pvalue_text(p: float) -> str:
        if p < 0.01:
            return "significativo a 1%"
        if p < 0.05:
            return "significativo a 5%"
        if p < 0.10:
            return "significativo a 10%"
        return "não significativo aos níveis usuais"

    def direction_text(coef: float) -> str:
        return "aumentando" if coef > 0 else "diminuindo"

    display_table = trends[
        ["ano", "termo", "efeito_percentual_aprox", "ic95_inf", "ic95_sup", "p_valor"]
    ].copy()
    display_table = display_table.sort_values(["termo", "ano"])
    display_table["ano"] = display_table["ano"].astype(int).astype(str)

    linear_sentences = []
    for _, row in linear_trends.iterrows():
        linear_sentences.append(
            f"- **{row['termo']}**: a tendência linear é {direction_text(row['inclinacao_log_por_ano'])} "
            f"em {row['efeito_percentual_aprox_por_ano']:+.2f} pontos percentuais aproximados por ano "
            f"({pvalue_text(row['p_valor'])})."
        )

    output = PROJECT_DIR / "docs" / "evolucao_temporal.md"
    lines = [
        "# Evolução Temporal dos Diferenciais (2016T4-2025T4)",
        "",
        "Este arquivo é gerado por `scripts/09_estimate_trends.py`. Parte do modelo-base "
        "(log do rendimento por hora real, mesmos controles de `03_estimate_baseline.py`) e "
        "adiciona interações `formal:C(periodo)`, `mulher:C(periodo)` e `preto_pardo:C(periodo)`, "
        "permitindo que cada diferencial varie livremente ano a ano em vez de ser constante no "
        "tempo. O coeficiente de cada ano é a soma do termo-base (ano de referência, 2016T4) com a "
        "interação correspondente; o erro-padrão usa a covariância completa "
        "(`var(a+b) = var(a) + var(b) + 2·cov(a,b)`), com erros clusterizados por UPA.",
        "",
        "## Efeito Percentual Aproximado por Ano",
        "",
        markdown_table(display_table, floatfmt=".2f"),
        "",
        "## Tendência Linear (robustez)",
        "",
        "Modelo alternativo com uma única inclinação `termo:Ano` (contínuo) por termo, resumindo a "
        "direção e a magnitude média da tendência em um número — não captura reversões ano a ano, "
        "só a direção geral.",
        "",
        *linear_sentences,
        "",
        "## Figura",
        "",
        "`outputs/figures/tendencia_temporal.png` — pequenos múltiplos com IC 95% por termo.",
        "",
        "## Leitura",
        "",
        "- Estes coeficientes ainda são diferenciais condicionais (mesmos controles do modelo-base: "
        "ocupação, atividade, escolaridade, idade e idade²), não efeitos causais.",
        "- Com uma amostra de ~2 a 3 mil observações por ano em Roraima, os IC 95% ano a ano tendem a "
        "ser largos — a tendência linear é o resumo mais estável para dizer se um prêmio/penalidade "
        "está estruturalmente aumentando ou diminuindo; o gráfico ano a ano serve para checar se essa "
        "tendência é consistente ou dominada por um ou dois anos atípicos (ex.: pandemia).",
        "",
    ]
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved: {output}")


if __name__ == "__main__":
    main()
