"""Generate the paper's result figures (points + 95% CI, no bars, no significance
stars) from the R/survey-based contrast outputs.

Escreve paper/figures/*.pdf (+ .png), nomes referenciados por \\includegraphics em
paper/artigo.tex:
- fig_formalidade_amostras.pdf: diferencial associado à formalidade (amostra ampla vs. restrita).
- fig_acesso_formalidade.pdf: AME de acesso à formalidade por gênero/raça (ampla vs. restrita).
- fig_gaps_genero_raca_formalidade.pdf: gênero e raça segundo formalidade (dois painéis).
- fig_accounting_genero_raca.pdf: accounting sequencial dos gaps de gênero e raça/cor.
- fig_setor_publico_raca.pdf: estrutura salarial por posição + gaps raciais público/privado.
"""

import math
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.paths import PAPER_FIGURES_DIR, TABLES_DIR, ensure_project_dirs


BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
PURPLE = "#8858c8"
GRAY_GRID = "#e1e0d9"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"

RACA_COLORS = {"preto": ORANGE, "pardo": AQUA, "indigena": PURPLE}
RACA_LABELS = {"preto": "Preto", "pardo": "Pardo", "indigena": "Indígena"}

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


def _save(fig, name: str) -> None:
    fig.savefig(PAPER_FIGURES_DIR / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(PAPER_FIGURES_DIR / f"{name}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"saved: {PAPER_FIGURES_DIR / f'{name}.pdf'}")


def _load_contrastes(amostra: str) -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / f"r_contrastes_{amostra}_ln_renda_hora_real.csv")


def _load_ame(amostra: str) -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / f"r_prob_formal_ame_{amostra}.csv")


def _point_ci_row(ax, y, est, lo, hi, color, marker="o"):
    ax.plot([lo, hi], [y, y], color=color, linewidth=1.6, solid_capstyle="round")
    ax.plot(est, y, marker=marker, color=color, markersize=7, zorder=3)


def _pct_ci_from_coef(coef: float, se: float) -> tuple[float, float, float]:
    """Converte coeficiente/erro-padrão em log para percentual + IC95%,
    via 100*(exp(.)-1), consistente com efeito_percentual_aprox nos CSVs de contraste."""
    pct = 100 * (math.exp(coef) - 1)
    lo = 100 * (math.exp(coef - 1.96 * se) - 1)
    hi = 100 * (math.exp(coef + 1.96 * se) - 1)
    return pct, lo, hi


# ---------------------------------------------------------------------------
# Figura 1 -- diferencial associado à formalidade (ampla vs. restrita)
# ---------------------------------------------------------------------------
def fig1_formalidade_gap():
    rows = []
    for amostra, label in [("ampla", "Amostra ampla"), ("restrita", "Amostra restrita")]:
        df = _load_contrastes(amostra)
        r = df.loc[df["id"] == "formal_gap_geral"].iloc[0]
        rows.append((label, r["efeito_percentual_aprox"], r["ic95_inf"], r["ic95_sup"]))

    fig, ax = plt.subplots(figsize=(7.5, 2.6))
    ax.axvline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", alpha=0.6)
    for i, (label, est, lo, hi) in enumerate(rows):
        _point_ci_row(ax, i, est, lo, hi, BLUE)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlabel("Diferencial percentual associado à formalidade (renda-hora, IC95%)")
    _save(fig, "fig_formalidade_amostras")


# ---------------------------------------------------------------------------
# Figura 2 -- acesso à formalidade (AME, ampla vs. restrita)
# ---------------------------------------------------------------------------
def fig2_acesso_formalidade():
    termos = ["mulher", "preto", "pardo", "indigena"]
    labels = {"mulher": "Mulher", "preto": "Preto", "pardo": "Pardo", "indigena": "Indígena"}
    ame_ampla = _load_ame("ampla").set_index("termo")
    ame_restrita = _load_ame("restrita").set_index("termo")

    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ax.axvline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", alpha=0.6)
    offsets = {"Ampla": 0.15, "Restrita": -0.15}
    colors = {"Ampla": BLUE, "Restrita": ORANGE}
    for i, termo in enumerate(termos):
        for amostra_label, df in [("Ampla", ame_ampla), ("Restrita", ame_restrita)]:
            row = df.loc[termo]
            est = row["ame_pp"]
            se = row["erro_padrao_pp"]
            lo, hi = est - 1.96 * se, est + 1.96 * se
            y = i + offsets[amostra_label]
            _point_ci_row(ax, y, est, lo, hi, colors[amostra_label])
    ax.set_yticks(range(len(termos)))
    ax.set_yticklabels([labels[t] for t in termos])
    ax.set_ylim(-0.6, len(termos) - 0.4)
    ax.set_xlabel("Efeito marginal médio sobre P(Formal=1), em pontos percentuais (IC95%)")

    handles = [
        plt.Line2D([0], [0], color=BLUE, marker="o", linestyle="-", label="Amostra ampla"),
        plt.Line2D([0], [0], color=ORANGE, marker="o", linestyle="-", label="Amostra restrita"),
    ]
    ax.legend(
        handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.02),
        ncol=2, frameon=False,
    )
    _save(fig, "fig_acesso_formalidade")


# ---------------------------------------------------------------------------
# Figura 3 -- gênero e raça segundo formalidade (dois painéis)
# ---------------------------------------------------------------------------
def fig3_genero_raca_formalidade():
    df = _load_contrastes("ampla")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8), width_ratios=[1, 1.4])

    # Painel (a): gênero, informal vs. formal
    genero_rows = [
        ("Informais", df.loc[df["id"] == "genero_gap_informal"].iloc[0]),
        ("Formais", df.loc[df["id"] == "genero_gap_formal"].iloc[0]),
    ]
    ax1.axvline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", alpha=0.6)
    for i, (label, r) in enumerate(genero_rows):
        _point_ci_row(ax1, i, r["efeito_percentual_aprox"], r["ic95_inf"], r["ic95_sup"], BLUE)
    ax1.set_yticks(range(len(genero_rows)))
    ax1.set_yticklabels([g[0] for g in genero_rows])
    ax1.set_ylim(-0.7, len(genero_rows) - 0.3)
    ax1.set_xlim(-30, 5)
    ax1.set_xlabel("Diferencial de gênero (%, IC95%)")
    ax1.set_title("(a) Gênero", loc="left", fontsize=11)

    # Painel (b): raça, informal vs. formal, 3 grupos
    racas = ["preto", "pardo", "indigena"]
    raca_labels = {"preto": "Preto", "pardo": "Pardo", "indigena": "Indígena"}
    ax2.axvline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", alpha=0.6)
    offsets = {"Informal": 0.15, "Formal": -0.15}
    colors = {"Informal": BLUE, "Formal": ORANGE}
    for i, raca in enumerate(racas):
        for status_label, id_suffix in [("Informal", "informal"), ("Formal", "formal")]:
            r = df.loc[df["id"] == f"raca_{raca}_gap_{id_suffix}"].iloc[0]
            y = i + offsets[status_label]
            _point_ci_row(
                ax2, y, r["efeito_percentual_aprox"], r["ic95_inf"], r["ic95_sup"],
                colors[status_label],
            )
    ax2.set_yticks(range(len(racas)))
    ax2.set_yticklabels([raca_labels[r] for r in racas])
    ax2.set_ylim(-0.6, len(racas) - 0.4)
    ax2.set_xlim(-30, 5)
    ax2.set_xlabel("Diferencial racial em relação a brancos (%, IC95%)")
    ax2.set_title("(b) Raça/cor", loc="left", fontsize=11)
    handles = [
        plt.Line2D([0], [0], color=BLUE, marker="o", linestyle="-", label="Informal"),
        plt.Line2D([0], [0], color=ORANGE, marker="o", linestyle="-", label="Formal"),
    ]
    ax2.legend(
        handles=handles, loc="upper right", bbox_to_anchor=(1.0, 1.16),
        ncol=2, frameon=False,
    )

    fig.tight_layout()
    _save(fig, "fig_gaps_genero_raca_formalidade")


# ---------------------------------------------------------------------------
# Figura 4 -- accounting sequencial dos gaps de gênero e raça/cor
# ---------------------------------------------------------------------------
# Etapas principais (M4 "Ocupação FE separado" e M7 "Horas" ficam de fora do
# gráfico principal -- tratadas como apoio/robustez, não como parte da
# sequência de composição reportada no corpo do texto).
ETAPAS = ["M0", "M1", "M2", "M3", "M5", "M6"]
ETAPA_LABELS = {
    "M0": "Bruto",
    "M1": "+ Demografia",
    "M2": "+ Escolaridade",
    "M3": "+ Atividade",
    "M5": "+ Ocupação×atividade",
    "M6": "+ Setor público",
}


def fig4_accounting_genero_raca():
    genero = pd.read_csv(TABLES_DIR / "r_decomposicao_genero.csv").set_index("modelo")
    raca = pd.read_csv(TABLES_DIR / "r_decomposicao_raca.csv")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6), width_ratios=[1, 1.3])

    # Painel (a): gênero, uma série
    ax1.axvline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", alpha=0.6)
    for i, etapa in enumerate(ETAPAS):
        row = genero.loc[etapa]
        pct, lo, hi = _pct_ci_from_coef(row["coeficiente"], row["erro_padrao"])
        y = len(ETAPAS) - 1 - i
        _point_ci_row(ax1, y, pct, lo, hi, BLUE)
    ax1.set_yticks(range(len(ETAPAS)))
    ax1.set_yticklabels([ETAPA_LABELS[e] for e in reversed(ETAPAS)])
    ax1.set_ylim(-0.6, len(ETAPAS) - 0.4)
    ax1.set_xlabel("Diferencial mulher–homem (%, IC95%)")
    ax1.set_title("(a) Gênero", loc="left", fontsize=11)

    # Painel (b): raça, três séries com pequeno deslocamento vertical por etapa
    racas = ["preto", "pardo", "indigena"]
    offsets = {"preto": 0.22, "pardo": 0.0, "indigena": -0.22}
    ax2.axvline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", alpha=0.6)
    for i, etapa in enumerate(ETAPAS):
        y = len(ETAPAS) - 1 - i
        for r in racas:
            row = raca.loc[(raca["modelo"] == etapa) & (raca["raca"] == r)].iloc[0]
            pct, lo, hi = _pct_ci_from_coef(row["coeficiente"], row["erro_padrao"])
            _point_ci_row(ax2, y + offsets[r], pct, lo, hi, RACA_COLORS[r], marker="o")
    ax2.set_yticks(range(len(ETAPAS)))
    ax2.set_yticklabels([ETAPA_LABELS[e] for e in reversed(ETAPAS)])
    ax2.set_ylim(-0.6, len(ETAPAS) - 0.4)
    ax2.set_xlabel("Diferencial racial em relação a brancos (%, IC95%)")
    ax2.set_title("(b) Raça/cor", loc="left", fontsize=11)
    handles = [
        plt.Line2D([0], [0], color=RACA_COLORS[r], marker="o", linestyle="-",
                   label=RACA_LABELS[r])
        for r in racas
    ]
    ax2.legend(
        handles=handles, loc="upper right", bbox_to_anchor=(1.0, 1.16),
        ncol=3, frameon=False,
    )

    fig.tight_layout()
    _save(fig, "fig_accounting_genero_raca")


# ---------------------------------------------------------------------------
# Figura 5 -- setor público: estrutura salarial por posição + raça
# ---------------------------------------------------------------------------
def fig5_setor_publico_raca():
    posicao = pd.read_csv(TABLES_DIR / "r_posicao_ocupacao_ln_renda_hora_real.csv")
    posicao = posicao[posicao["termo"].str.startswith("factor(posicao_ocupacao_grupo)")].copy()
    posicao["categoria"] = posicao["termo"].str.replace(
        "factor(posicao_ocupacao_grupo)", "", regex=False
    )
    cat_labels = {
        "militar_estatutario": "Militar/estatutário",
        "empregador": "Empregador",
        "publico_com_carteira": "Público com carteira",
        "publico_sem_carteira": "Público sem carteira",
        "privado_com_carteira": "Privado com carteira",
        "conta_propria": "Conta própria",
        "domestico_com_carteira": "Doméstico com carteira",
        "domestico_sem_carteira": "Doméstico sem carteira",
    }
    posicao["pct"] = posicao["efeito_percentual_aprox"]
    posicao = posicao.sort_values("pct", ascending=True).reset_index(drop=True)

    df_raca = pd.read_csv(TABLES_DIR / "r_raca_setor_publico_contrastes_ln_renda_hora_real.csv")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.2), width_ratios=[1.1, 1])

    # Painel (a): estrutura salarial por posição (referência: privado sem carteira)
    ax1.axvline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", alpha=0.6)
    for i, r in posicao.iterrows():
        pct, lo, hi = _pct_ci_from_coef(r["coeficiente"], r["erro_padrao"])
        _point_ci_row(ax1, i, pct, lo, hi, BLUE)
    ax1.set_yticks(range(len(posicao)))
    ax1.set_yticklabels([cat_labels[c] for c in posicao["categoria"]])
    ax1.set_ylim(-0.6, len(posicao) - 0.4)
    ax1.set_xlabel("Diferencial vs. privado sem carteira (%, IC95%)")
    ax1.set_title("(a) Estrutura salarial por posição", loc="left", fontsize=11)

    # Painel (b): gaps raciais entre formais, privado/doméstico vs. público
    racas = ["preto", "pardo", "indigena"]
    offsets = {"Privado/doméstico": 0.15, "Público": -0.15}
    colors = {"Privado/doméstico": BLUE, "Público": ORANGE}
    ax2.axvline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", alpha=0.6)
    for i, r in enumerate(racas):
        for status_label, id_suffix in [
            ("Privado/doméstico", "formal_privado"), ("Público", "formal_publico"),
        ]:
            row = df_raca.loc[df_raca["id"] == f"{r}_{id_suffix}"].iloc[0]
            y = i + offsets[status_label]
            _point_ci_row(
                ax2, y, row["efeito_percentual_aprox"], row["ic95_inf"], row["ic95_sup"],
                colors[status_label],
            )
    ax2.set_yticks(range(len(racas)))
    ax2.set_yticklabels([RACA_LABELS[r] for r in racas])
    ax2.set_ylim(-0.6, len(racas) - 0.4)
    ax2.set_xlabel("Diferencial racial entre formais (%, IC95%)")
    ax2.set_title("(b) Raça × setor, entre formais", loc="left", fontsize=11)
    handles = [
        plt.Line2D([0], [0], color=BLUE, marker="o", linestyle="-", label="Privado/doméstico"),
        plt.Line2D([0], [0], color=ORANGE, marker="o", linestyle="-", label="Público"),
    ]
    ax2.legend(
        handles=handles, loc="upper right", bbox_to_anchor=(1.0, 1.16),
        ncol=2, frameon=False,
    )

    fig.tight_layout()
    _save(fig, "fig_setor_publico_raca")


def main():
    ensure_project_dirs()
    fig1_formalidade_gap()
    fig2_acesso_formalidade()
    fig3_genero_raca_formalidade()
    fig4_accounting_genero_raca()
    fig5_setor_publico_raca()


if __name__ == "__main__":
    main()
