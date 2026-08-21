"""Generate figures, LaTeX regression tables, and narrative-number macros for the Beamer
presentation, from the final R/survey-based results (r/02, r/03, r/04, r/05, r/06, r/07 —
ver docs/resultados_finais.md).

Escreve:
- outputs/figures/*.pdf (+ .png): motivação (gaps brutos), sensibilidade da especificação
  (M1->M4), setor público (estrutura salarial por posição), mecanismo de jornada, R$ ajustado,
  robustez (trimestres/pandemia).
- presentation/gerado/*.tex: tabelas de regressão e de contrastes.
- presentation/gerado/numeros.tex: macros \\newcommand com números narrativos.
"""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.labels import ATIVIDADE_LABELS, OCUPACAO_LABELS
from pnadc_rr.paths import (
    FIGURES_DIR,
    PRESENTATION_GERADO_DIR,
    PROCESSED_DIR,
    TABLES_DIR,
    ensure_project_dirs,
)


BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
RED = "#e34948"
PURPLE = "#8858c8"
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

RACA_NIVEIS = ["preto", "pardo", "indigena"]
RACA_LABELS = {"preto": "Preto", "pardo": "Pardo", "indigena": "Ind\\'igena"}
RACA_LABELS_PLAIN = {"preto": "Preto", "pardo": "Pardo", "indigena": "Indígena"}
RACA_COLORS = {"preto": ORANGE, "pardo": AQUA, "indigena": PURPLE}


# ---------------------------------------------------------------------------
# Formatting helpers (pt-BR)
# ---------------------------------------------------------------------------

def fmt_num(x: float, decimals: int = 3, sign: bool = False) -> str:
    text = f"{x:+.{decimals}f}" if sign else f"{x:.{decimals}f}"
    return text.replace(".", ",")


def fmt_pct(x: float, decimals: int = 1, sign: bool = True) -> str:
    return f"{fmt_num(x, decimals, sign=sign)}\\%"


def fmt_brl(x: float, decimals: int = 0) -> str:
    sign = "-" if x < 0 else ""
    whole = f"{abs(x):,.{decimals}f}"
    whole = whole.replace(",", "§").replace(".", ",").replace("§", ".")
    return f"{sign}R\\$\\,{whole}"


def fmt_int(x: float) -> str:
    return f"{int(round(x)):,}".replace(",", ".")


def stars(p: float) -> str:
    if p < 0.01:
        return "$^{***}$"
    if p < 0.05:
        return "$^{**}$"
    if p < 0.10:
        return "$^{*}$"
    return ""


def pct_effect(coef: float) -> float:
    return (np.exp(coef) - 1) * 100


def wavg(values: pd.Series, weights: pd.Series) -> float:
    return float(np.average(values, weights=weights))


# ---------------------------------------------------------------------------
# Data loading (fonte: outputs/tables/r_*.csv, gerados pelos scripts em r/)
# ---------------------------------------------------------------------------

def load_r_nested(amostra: str, dv: str, modelo: str = "M4") -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / f"r_nested_{amostra}_{dv}_{modelo}.csv", index_col="termo")


def load_r_contrastes(amostra: str, dv: str) -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / f"r_contrastes_{amostra}_{dv}.csv", index_col="id")


def load_r_jornada(amostra: str, dv: str) -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / f"r_jornada_{amostra}_{dv}.csv", index_col="termo")


def load_r_jornada_identidade(amostra: str) -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / f"r_jornada_identidade_{amostra}.csv", index_col="termo")


def load_r_tendencia() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "r_tendencia_linear.csv", index_col="termo")


def load_r_tendencia_flexivel() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "r_tendencia_flexivel.csv")


def load_r_robustez_trimestres() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "r_robustez_trimestres.csv")


def load_r_robustez_pandemia() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "r_robustez_pandemia.csv")


def load_r_setor_publico(dv: str) -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / f"r_setor_publico_{dv}.csv", index_col="termo")


def load_r_setor_publico_combinado(dv: str) -> pd.Series:
    return pd.read_csv(TABLES_DIR / f"r_setor_publico_combinado_{dv}.csv").iloc[0]


def load_r_posicao_ocupacao(dv: str) -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / f"r_posicao_ocupacao_{dv}.csv", index_col="termo")


def load_r_posicao_descritivo() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "r_posicao_ocupacao_descritivo.csv")


def load_r_prob_formal_ame(amostra: str) -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / f"r_prob_formal_ame_{amostra}.csv", index_col="termo")


def load_r_decomposicao_genero() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "r_decomposicao_genero.csv", index_col="modelo")


def load_r_decomposicao_raca() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "r_decomposicao_raca.csv")


def load_r_raca_setor_publico_contrastes(dv: str) -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / f"r_raca_setor_publico_contrastes_{dv}.csv", index_col="id")


def load_r_interseccionalidade() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "r_interseccionalidade_genero_raca.csv", index_col="id")


def raca_term(raca: str, prefix: str = "factor(raca_grupo)") -> str:
    return f"{prefix}{raca}"


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def save_fig(fig, name: str) -> None:
    fig.savefig(FIGURES_DIR / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIGURES_DIR / f"{name}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"saved: {FIGURES_DIR / f'{name}.pdf'}")


def fig_motivacao(raw_gaps: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(9.5, 3.4), sharey=True)
    panels = [
        ("Informal", "Formal", raw_gaps["formal"], axes[0]),
        ("Homem", "Mulher", raw_gaps["mulher"], axes[1]),
        ("Branco", "Preto/\npardo", raw_gaps["raca"], axes[2]),
    ]
    for label_a, label_b, (val_a, val_b), ax in panels:
        bars = ax.bar([label_a, label_b], [val_a, val_b], color=[BLUE, ORANGE], width=0.55, zorder=3)
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"R$ {height:,.0f}".replace(",", "."),
                (bar.get_x() + bar.get_width() / 2, height),
                ha="center", va="bottom", fontsize=9.5, color=INK,
            )
        ax.set_ylim(0, max(val_a, val_b) * 1.28)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(left=False, labelleft=(ax is axes[0]))
        ax.grid(axis="x", visible=False)
        ax.grid(axis="y", alpha=0.5, zorder=0)
    axes[0].set_ylabel("R$/hora (real)")
    fig.suptitle("Renda média por hora (real), sem controles — Roraima, 2016T4–2025T4", fontsize=11.5)
    fig.tight_layout()
    save_fig(fig, "motivacao_gaps_brutos")


def fig_sensibilidade() -> None:
    # Sensibilidade da especificação M1->M4 (amostra ampla, renda por hora real) para
    # formal, mulher e pardo (maior subgrupo racial, estimativa mais precisa).
    modelos = ["M1", "M2", "M3", "M4"]
    modelo_labels = ["M1\ntratamentos", "M2\n+ativ.", "M3\n+ocup.", "M4\ncélula\nconjunta"]
    termos = [("formal", "Formal", BLUE), ("mulher", "Mulher", ORANGE), (raca_term("pardo"), "Pardo", AQUA)]

    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.6))
    for ax, (termo, label, color) in zip(axes, termos):
        pontos, baixos, altos = [], [], []
        for m in modelos:
            tbl = load_r_nested("ampla", "ln_renda_hora_real", m)
            r = tbl.loc[termo]
            pontos.append(pct_effect(r["coeficiente"]))
            baixos.append(pct_effect(r["coeficiente"] - 1.96 * r["erro_padrao"]))
            altos.append(pct_effect(r["coeficiente"] + 1.96 * r["erro_padrao"]))
        x = np.arange(len(modelos))
        ax.errorbar(
            x, pontos, yerr=[np.array(pontos) - np.array(baixos), np.array(altos) - np.array(pontos)],
            fmt="o-", color=color, ecolor=color, elinewidth=1.6, capsize=3, markersize=6, zorder=3,
        )
        ax.axhline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", zorder=0)
        ax.set_xticks(x)
        ax.set_xticklabels(modelo_labels, fontsize=8.5)
        ax.set_title(label, fontsize=11.5)
        ax.spines[["top", "right"]].set_visible(False)
        if ax is axes[0]:
            ax.set_ylabel("Efeito percentual aprox. (%)")
    fig.suptitle("Sensibilidade à especificação — renda por hora real, amostra ampla (IC 95%)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "sensibilidade_especificacao")


def fig_setor_publico() -> None:
    desc = load_r_posicao_descritivo().sort_values("renda_hora_media")
    cond = load_r_posicao_ocupacao("ln_renda_hora_real")

    labels_map = {
        "militar_estatutario": "Militar/estatutário", "empregador": "Empregador",
        "publico_com_carteira": "Público, c/carteira", "publico_sem_carteira": "Público, s/carteira",
        "privado_com_carteira": "Privado, c/carteira", "privado_sem_carteira": "Privado, s/carteira\n(referência)",
        "conta_propria": "Conta-própria", "domestico_com_carteira": "Doméstico, c/carteira",
        "domestico_sem_carteira": "Doméstico, s/carteira",
    }

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6))

    labels1 = [labels_map[p] for p in desc["posicao_ocupacao_grupo"]]
    is_public = desc["posicao_ocupacao_grupo"].isin(["publico_com_carteira", "publico_sem_carteira", "militar_estatutario"])
    colors1 = [AQUA if pub else BLUE for pub in is_public]
    ax1.barh(labels1, desc["renda_hora_media"], color=colors1, zorder=3)
    ax1.set_xlabel("R$/hora (real, sem controles)")
    ax1.set_title("Renda média por hora, por posição", fontsize=11)
    ax1.spines[["top", "right"]].set_visible(False)
    for y, v in enumerate(desc["renda_hora_media"]):
        ax1.annotate(f"R$ {v:.2f}", (v, y), ha="left", va="center", fontsize=8.5, xytext=(4, 0), textcoords="offset points")

    ordem = cond.filter(like="factor(posicao_ocupacao_grupo)", axis=0)
    ordem = ordem.assign(efeito=lambda d: (np.exp(d["coeficiente"]) - 1) * 100).sort_values("efeito")
    posicoes = [i.replace("factor(posicao_ocupacao_grupo)", "") for i in ordem.index]
    labels2 = [labels_map.get(p, p) for p in posicoes]
    is_public2 = [p in {"publico_com_carteira", "publico_sem_carteira", "militar_estatutario"} for p in posicoes]
    colors2 = [AQUA if pub else (RED if v < 0 else BLUE) for pub, v in zip(is_public2, ordem["efeito"])]
    ax2.barh(labels2, ordem["efeito"], color=colors2, zorder=3)
    ax2.axvline(0, color=INK_SECONDARY, linewidth=1, zorder=0)
    ax2.set_xlabel("Efeito condicional aprox. (%), ref.: privado s/carteira")
    ax2.set_title("Estrutura salarial condicional", fontsize=11)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.set_xlim(min(ordem["efeito"]) * 1.35, max(ordem["efeito"]) * 1.2)
    for y, v in enumerate(ordem["efeito"]):
        ax2.annotate(f"{v:+.0f}%", (v, y), ha="left" if v >= 0 else "right", va="center", fontsize=8.5,
                     xytext=(4 if v >= 0 else -4, 0), textcoords="offset points")

    fig.suptitle("Setor público e estrutura salarial por posição na ocupação (renda por hora real)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "setor_publico")


def fig_informalidade_publica(common: pd.DataFrame) -> dict:
    # Caracteriza quem são os "público sem carteira" (VD4009=6) -- não é o padrão intuitivo
    # de informalidade (elementar/braçal); ver docs/definicao_formalidade.md.
    sub = common.loc[common["posicao_ocupacao_grupo"] == "publico_sem_carteira"].copy()

    ocup_pct = sub.groupby("ocupacao_grupo")["peso"].sum().sort_values(ascending=False)
    ocup_pct = (ocup_pct / ocup_pct.sum()) * 100
    ativ_pct_full = sub.groupby("atividade_grupo")["peso"].sum().sort_values(ascending=False)
    ativ_pct_full = (ativ_pct_full / ativ_pct_full.sum()) * 100
    # Só duas atividades concentram quase tudo (administração pública, educação/saúde);
    # o restante vira "Outras" para não poluir o painel com rótulos longos e fatias residuais.
    ativ_pct = ativ_pct_full[ativ_pct_full >= 3].copy()
    if ativ_pct_full[ativ_pct_full < 3].sum() > 0:
        ativ_pct["outras"] = ativ_pct_full[ativ_pct_full < 3].sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 3.4))

    labels1 = [OCUPACAO_LABELS.get(c, c) for c in ocup_pct.index]
    ax1.barh(labels1, ocup_pct.values, color=BLUE, zorder=3)
    ax1.invert_yaxis()
    ax1.set_xlabel("% dos ocupados \"público sem carteira\"", fontsize=9)
    ax1.set_title("Por grupo ocupacional", fontsize=11)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.tick_params(axis="both", labelsize=8.5)
    ax1.set_xlim(0, max(ocup_pct.values) * 1.22)
    for y, v in enumerate(ocup_pct.values):
        ax1.annotate(f"{v:.1f}%", (v, y), ha="left", va="center", fontsize=8,
                     xytext=(4, 0), textcoords="offset points")

    labels2 = ["Outras atividades" if c == "outras" else ATIVIDADE_LABELS.get(c, c) for c in ativ_pct.index]
    ax2.barh(labels2, ativ_pct.values, color=ORANGE, zorder=3)
    ax2.invert_yaxis()
    ax2.set_xlabel("% dos ocupados \"público sem carteira\"", fontsize=9)
    ax2.set_title("Por atividade econômica", fontsize=11)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.tick_params(axis="both", labelsize=8.5)
    ax2.set_xlim(0, max(ativ_pct.values) * 1.22)
    for y, v in enumerate(ativ_pct.values):
        ax2.annotate(f"{v:.1f}%", (v, y), ha="left", va="center", fontsize=8,
                     xytext=(4, 0), textcoords="offset points")

    fig.suptitle("Composição da informalidade no setor público (posição = público sem carteira)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "informalidade_publica")

    return {
        "n_naopond": len(sub),
        "n_pond": sub["peso"].sum(),
        "ocup_top3_pct": ocup_pct.iloc[:3].sum(),
        "ativ_admpub_pct": ativ_pct_full.get("8", 0.0),
        "ativ_educsaude_pct": ativ_pct_full.get("9", 0.0),
    }


POSICOES_PUBLICAS = ["publico_sem_carteira", "publico_com_carteira", "militar_estatutario"]
POSICOES_PUBLICAS_LABELS = {
    "publico_sem_carteira": "Público\nsem carteira", "publico_com_carteira": "Público\ncom carteira",
    "militar_estatutario": "Militar/\nestatutário",
}
RACA_TODAS = ["branco", "preto", "pardo", "indigena"]
RACA_TODAS_LABELS = {"branco": "Branco", "preto": "Preto", "pardo": "Pardo", "indigena": "Indígena"}
RACA_TODAS_COLORS = {"branco": BLUE, "preto": ORANGE, "pardo": AQUA, "indigena": PURPLE}


def fig_composicao_racial_publico(common: pd.DataFrame) -> dict:
    # Checagem direcionada (sem regressão nova): quem são racialmente os trabalhadores nas
    # diferentes posições públicas? Testa se a composição racial das posições públicas de
    # maior rendimento (militar/estatutário, ver setor_publico.pdf) já explica boa parte do
    # gap racial "entre formais" documentado em raca_setor_publico.pdf -- ou se o gap é
    # sobretudo "preço" (mesma posição, remuneração diferente por raça).
    sub = common.loc[common["posicao_ocupacao_grupo"].isin(POSICOES_PUBLICAS) & common["raca_grupo"].notna()].copy()

    n_naopond = sub.groupby(["posicao_ocupacao_grupo", "raca_grupo"]).size().unstack(fill_value=0)
    n_naopond = n_naopond.reindex(index=POSICOES_PUBLICAS, columns=RACA_TODAS)

    composicao = {}
    for pos in POSICOES_PUBLICAS:
        s = sub.loc[sub["posicao_ocupacao_grupo"] == pos]
        w = s.groupby("raca_grupo")["peso"].sum()
        composicao[pos] = (w / w.sum() * 100).reindex(RACA_TODAS).fillna(0.0)
    comp_df = pd.DataFrame(composicao)

    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    x = np.arange(len(POSICOES_PUBLICAS))
    width = 0.19
    for i, r in enumerate(RACA_TODAS):
        offset = (i - 1.5) * width
        valores = [comp_df.loc[r, pos] for pos in POSICOES_PUBLICAS]
        ax.bar(x + offset, valores, width, color=RACA_TODAS_COLORS[r], label=RACA_TODAS_LABELS[r], zorder=3)
        for xi, v in zip(x + offset, valores):
            ax.annotate(f"{v:.0f}%", (xi, v), ha="center", va="bottom", fontsize=8, xytext=(0, 2),
                         textcoords="offset points")
    ax.set_xticks(x)
    ax.set_xticklabels([POSICOES_PUBLICAS_LABELS[p] for p in POSICOES_PUBLICAS], fontsize=10)
    ax.set_ylabel("% da posição (composição racial ponderada)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper right", frameon=False, fontsize=9.5, ncol=4)
    ax.set_ylim(0, 75)
    fig.suptitle("Composição racial por posição no setor público", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "composicao_racial_publico")

    return {"comp": comp_df, "n": n_naopond}


def fig_mecanismo() -> None:
    termos = [("formal", "Formal", BLUE), ("mulher", "Mulher", ORANGE)] + [
        (raca_term(r), RACA_LABELS_PLAIN[r], RACA_COLORS[r]) for r in RACA_NIVEIS
    ]
    mensal = load_r_jornada("ampla", "ln_renda_mensal_real")
    hora = load_r_jornada("ampla", "ln_renda_hora_real")
    horas_dv = load_r_jornada("ampla", "ln_horas_semanais_principal")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4), width_ratios=[2, 1])
    y_positions = np.arange(len(termos))
    bar_height = 0.24
    series = [(mensal, BLUE, "Mensal"), (hora, AQUA, "Por hora (preço)")]
    for i, (model_df, color, series_label) in enumerate(series):
        values = [pct_effect(model_df.loc[t, "coeficiente"]) for t, _, _ in termos]
        offset = (0.5 - i) * bar_height
        ax1.barh(y_positions + offset, values, height=bar_height, color=color, label=series_label, zorder=3)
    ax1.axvline(0, color=INK_SECONDARY, linewidth=1, zorder=0)
    ax1.set_yticks(y_positions)
    ax1.set_yticklabels([lbl for _, lbl, _ in termos])
    ax1.set_xlabel("Efeito percentual aprox. (%)")
    ax1.invert_yaxis()
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.legend(loc="lower right", frameon=False, fontsize=9)
    ax1.set_title("Renda mensal vs. por hora (preço)", fontsize=11)

    horas_values = [horas_dv.loc[t, "coeficiente"] * 100 for t, _, _ in termos]
    colors = [BLUE if v >= 0 else RED for v in horas_values]
    ax2.barh(y_positions, horas_values, height=0.5, color=colors, zorder=3)
    ax2.axvline(0, color=INK_SECONDARY, linewidth=1, zorder=0)
    ax2.set_yticks(y_positions)
    ax2.set_yticklabels([])
    ax2.tick_params(left=False)
    ax2.invert_yaxis()
    ax2.set_xlabel("Efeito aprox. em horas (%)")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.set_title("Jornada (quantidade)", fontsize=11)
    span = max(abs(v) for v in horas_values) * 1.5
    ax2.set_xlim(-span, span)
    for y, v in zip(y_positions, horas_values):
        ax2.annotate(f"{v:+.1f}%", (v, y), ha="left" if v >= 0 else "right", va="center", fontsize=9,
                     xytext=(6 if v >= 0 else -6, 0), textcoords="offset points")

    fig.suptitle("Decomposição exata: efeito-preço vs. efeito-jornada (amostra ampla)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "mecanismo_jornada")


def fig_gap_reais(mean_mensal: float, mean_hora: float) -> None:
    termos = [("formal", "Formal", BLUE), ("mulher", "Mulher", ORANGE)] + [
        (raca_term(r), RACA_LABELS_PLAIN[r], RACA_COLORS[r]) for r in RACA_NIVEIS
    ]
    com_mensal = load_r_nested("ampla", "ln_renda_mensal_real", "M4")
    com_hora = load_r_nested("ampla", "ln_renda_hora_real", "M4")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    y_positions = np.arange(len(termos))

    for ax, model_df, base, title in [
        (ax1, com_mensal, mean_mensal, "R$/mês (na renda média real)"),
        (ax2, com_hora, mean_hora, "R$/hora (na renda média real)"),
    ]:
        values = [(np.exp(model_df.loc[t, "coeficiente"]) - 1) * base for t, _, _ in termos]
        colors = [RED if v < 0 else BLUE for v in values]
        ax.barh(y_positions, values, color=colors, height=0.55, zorder=3)
        ax.axvline(0, color=INK_SECONDARY, linewidth=1, zorder=0)
        ax.set_yticks(y_positions)
        ax.set_yticklabels([lbl for _, lbl, _ in termos])
        ax.invert_yaxis()
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_title(title, fontsize=11)
        span = max(abs(v) for v in values) * 1.35
        ax.set_xlim(-span, span)
        for y, v in zip(y_positions, values):
            ax.annotate(
                f"R$ {v:,.0f}".replace(",", ".").replace("R$ -", "-R$ "), (v, y),
                ha="left" if v >= 0 else "right", va="center", fontsize=9,
                xytext=(5 if v >= 0 else -5, 0), textcoords="offset points",
            )

    fig.suptitle("Diferencial condicional, convertido em R$ (amostra ampla, especificação M4)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "gap_reais")


def fig_robustez() -> None:
    trimestres = load_r_robustez_trimestres()
    pandemia = load_r_robustez_pandemia()
    termos = ["formal", "mulher", raca_term("pardo")]
    termo_labels = {"formal": "Formal", "mulher": "Mulher", raca_term("pardo"): "Pardo"}

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))

    ax = axes[0]
    sub = trimestres[(trimestres["dv"] == "ln_renda_hora_real") & (trimestres["termo"].isin(termos))]
    x = np.arange(len(termos))
    width = 0.35
    for i, esp in enumerate(["q4_only", "todos_trimestres"]):
        vals = [sub[(sub["termo"] == t) & (sub["especificacao"] == esp)]["efeito_percentual_aprox"].iloc[0] for t in termos]
        ax.bar(x + (i - 0.5) * width, vals, width, label="Q4-only" if esp == "q4_only" else "Todos os trimestres",
               color=BLUE if esp == "q4_only" else ORANGE, zorder=3)
    ax.axhline(0, color=INK_SECONDARY, linewidth=1, zorder=0)
    ax.set_xticks(x)
    ax.set_xticklabels([termo_labels[t] for t in termos])
    ax.set_ylabel("Efeito percentual aprox. (%)")
    ax.set_title("Q4-only vs. todos os trimestres", fontsize=11)
    ax.legend(frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    sub = pandemia[(pandemia["dv"] == "ln_renda_hora_real") & (pandemia["termo"].isin(termos))]
    recortes = ["pre_pandemia_2016_2019", "excl_2020_2021", "pos_pandemia_2022_2025"]
    recorte_labels = ["2016-2019", "Excl.\n2020-2021", "2022-2025"]
    width = 0.25
    colors = [BLUE, AQUA, ORANGE]
    for i, esp in enumerate(recortes):
        vals = [sub[(sub["termo"] == t) & (sub["especificacao"] == esp)]["efeito_percentual_aprox"].iloc[0] for t in termos]
        ax.bar(x + (i - 1) * width, vals, width, label=recorte_labels[i], color=colors[i], zorder=3)
    ax.axhline(0, color=INK_SECONDARY, linewidth=1, zorder=0)
    ax.set_xticks(x)
    ax.set_xticklabels([termo_labels[t] for t in termos])
    ax.set_title("Split de pandemia", fontsize=11)
    ax.legend(frameon=False, fontsize=8.5)
    ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Robustez temporal (renda por hora real, especificação M4)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "robustez_temporal")


def fig_tendencia_flexivel() -> None:
    # Evolução ano a ano, raça desagregada (branco = referência). Substitui a figura antiga
    # (Python/WLS, preto_pardo agregado com referência branco/amarelo/indígena) -- mesma
    # especificação M4, desenho amostral completo (ver r/09_tendencia_flexivel.R).
    flex = load_r_tendencia_flexivel()
    termos = [
        ("formal", "Prêmio de formalidade\n(ref.: informal)", BLUE),
        ("mulher", "Diferencial de gênero\n(ref.: homem)", ORANGE),
        (raca_term("preto"), "Diferencial racial: preto\n(ref.: branco)", RACA_COLORS["preto"]),
        (raca_term("pardo"), "Diferencial racial: pardo\n(ref.: branco)", RACA_COLORS["pardo"]),
        (raca_term("indigena"), "Diferencial racial: indígena\n(ref.: branco)", RACA_COLORS["indigena"]),
    ]

    fig, axes = plt.subplots(1, 5, figsize=(15, 3.6))
    for ax, (termo, titulo, color) in zip(axes, termos):
        sub = flex.loc[flex["termo"] == termo].sort_values("ano")
        ax.fill_between(sub["ano"], sub["ic95_inf"], sub["ic95_sup"], color=color, alpha=0.18, zorder=1)
        ax.plot(sub["ano"], sub["efeito_percentual_aprox"], color=color, linewidth=2, zorder=3)
        ax.scatter(sub["ano"], sub["efeito_percentual_aprox"], color=color, s=24, zorder=4)
        ax.axhline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", zorder=0)
        ax.set_title(titulo, fontsize=9.5)
        ax.set_xticks(sub["ano"].tolist()[::2])
        ax.set_xticklabels(sub["ano"].tolist()[::2], rotation=45, ha="right", fontsize=7.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="y", labelsize=8)
        if ax is axes[0]:
            ax.set_ylabel("Efeito percentual aprox. (%)", fontsize=9)

    fig.suptitle(
        "Evolução anual dos diferenciais condicionais — renda por hora real, raça desagregada (IC 95%)",
        fontsize=11.5,
    )
    fig.tight_layout()
    save_fig(fig, "tendencia_temporal")


def fig_prob_formal_ame() -> None:
    # Efeitos marginais médios (AME, p.p.) da probabilidade de estar em posição formal --
    # "quem acessa a formalidade", em contraste com o modelo de renda ("quanto formalidade
    # está associada ao rendimento"). Ver r/10_probabilidade_formalizacao.R.
    termos = [("mulher", "Mulher\n(ref.: homem)"), ("preto", "Preto\n(ref.: branco)"),
              ("pardo", "Pardo\n(ref.: branco)"), ("indigena", "Indígena\n(ref.: branco)")]
    y_positions = np.arange(len(termos))
    bar_offset = 0.14

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for i, (amostra, color, label) in enumerate([
        ("ampla", BLUE, "Todos os ocupados"), ("restrita", ORANGE, "Empregados"),
    ]):
        tbl = load_r_prob_formal_ame(amostra)
        offset = (0.5 - i) * bar_offset
        pontos = [tbl.loc[t, "ame_pp"] for t, _ in termos]
        erros = [1.96 * tbl.loc[t, "erro_padrao_pp"] for t, _ in termos]
        ax.errorbar(
            pontos, y_positions + offset, xerr=erros, fmt="o", color=color, ecolor=color,
            elinewidth=1.6, capsize=3, markersize=6, zorder=3, label=label,
        )
    ax.axvline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", zorder=0)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([lbl for _, lbl in termos])
    ax.invert_yaxis()
    ax.set_xlabel("Efeito marginal médio na prob. de ser formal (p.p.)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    fig.suptitle("Quem acessa a formalidade? Efeitos marginais médios (IC 95%)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "prob_formal_ame")


def fig_decomposicao_genero() -> None:
    # Accounting exercise: qual dimensão de composição revela o gap de gênero bruto (~+3%,
    # log) ao condicional (~-15/-18%)? Passos principais (M0->M6); M4 (ocupação, FE separado)
    # e M7 (+horas) ficam de fora do gráfico principal -- robustez, ver r_decomposicao_genero.csv.
    tbl = load_r_decomposicao_genero()
    passos = ["M0", "M1", "M2", "M3", "M5", "M6"]
    labels = [tbl.loc[m, "rotulo"] for m in passos]
    valores = [tbl.loc[m, "efeito_percentual_aprox"] for m in passos]
    cores = [BLUE if v >= 0 else RED for v in valores]

    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    x = np.arange(len(passos))
    ax.plot(x, valores, color=INK_SECONDARY, linewidth=1.4, linestyle="--", zorder=2)
    ax.bar(x, valores, color=cores, width=0.55, zorder=3)
    ax.axhline(0, color=INK_SECONDARY, linewidth=1, zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylabel("Efeito de \"mulher\" aprox. (%), renda/hora")
    ax.spines[["top", "right"]].set_visible(False)
    for xi, v in zip(x, valores):
        ax.annotate(f"{v:+.1f}%", (xi, v), ha="center", va="bottom" if v >= 0 else "top",
                     fontsize=9.5, fontweight="bold",
                     xytext=(0, 4 if v >= 0 else -4), textcoords="offset points")
    span = max(abs(v) for v in valores) * 1.35
    ax.set_ylim(-span, span * 0.55)
    fig.suptitle("Decomposição sequencial do gap de gênero (renda por hora real)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "decomposicao_genero")


def fig_decomposicao_raca() -> None:
    # Accounting exercise racial (equivalente ao de gênero, mas testa a hipótese oposta): qual
    # dimensão de composição explica a queda do gap bruto (~-30/-40%) ao condicional (~-10/-14%)?
    # Diferente do gênero (onde a vantagem educacional das mulheres MASCARA o gap), a expectativa
    # da literatura é que desigualdade educacional AMPLIE o gap racial bruto -- i.e., educação
    # deveria REDUZIR o coeficiente ao entrar, não revelar um gap maior.
    tbl = load_r_decomposicao_raca()
    passos = ["M0", "M1", "M2", "M3", "M5", "M6"]
    passo_labels = ["Bruto\n(só raça)", "+ Demografia", "+ Educação", "+ Atividade",
                     "+ Ocup.×Ativ.", "+ Setor\npúblico"]

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    x = np.arange(len(passos))
    # deslocamentos verticais alternados para o rótulo do último ponto -- as três linhas
    # convergem nos passos finais (~-10 a -14%) e ficariam sobrepostas com o mesmo offset.
    offset_final = {"preto": -10, "pardo": 10, "indigena": -24}
    for r in RACA_NIVEIS:
        sub = tbl[tbl["raca"] == r].set_index("modelo")
        valores = [sub.loc[m, "efeito_percentual_aprox"] for m in passos]
        ax.plot(x, valores, color=RACA_COLORS[r], linewidth=2, marker="o", markersize=6,
                 label=RACA_LABELS_PLAIN[r], zorder=3)
        # só rotula primeiro e último ponto -- as três linhas convergem nos passos finais.
        ax.annotate(f"{valores[0]:+.0f}%", (x[0], valores[0]), ha="center", va="top", fontsize=9,
                     color=RACA_COLORS[r], fontweight="bold", xytext=(0, -10), textcoords="offset points")
        va_final = "bottom" if offset_final[r] > 0 else "top"
        ax.annotate(f"{valores[-1]:+.0f}%", (x[-1], valores[-1]), ha="center", va=va_final, fontsize=9,
                     color=RACA_COLORS[r], fontweight="bold", xytext=(0, offset_final[r]), textcoords="offset points")
    ax.axhline(0, color=INK_SECONDARY, linewidth=1, zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(passo_labels, fontsize=9.5)
    ax.set_ylabel("Efeito racial aprox. (%), renda/hora")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="lower left", frameon=False, fontsize=9.5)
    ax.set_ylim(-46, 6)
    fig.suptitle("Decomposição sequencial do gap racial (renda por hora real)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "decomposicao_raca")


def fig_raca_setor_publico() -> None:
    # O gap racial "entre formais" é maior porque a formalidade em si discrimina mais, ou
    # porque formais estão mais concentrados no setor público -- que tem gap racial muito
    # maior? Compara o gap racial (mantendo formal fixo) dentro de privado vs. público.
    hora = load_r_raca_setor_publico_contrastes("ln_renda_hora_real")

    fig, ax = plt.subplots(figsize=(8, 4.4))
    y_positions = np.arange(len(RACA_NIVEIS))
    bar_height = 0.32
    for i, (setor, color, label) in enumerate([("privado", BLUE, "Privado/doméstico"), ("publico", ORANGE, "Público")]):
        offset = (0.5 - i) * bar_height
        pontos, erros = [], []
        for r in RACA_NIVEIS:
            row_ = hora.loc[f"{r}_formal_{setor}"]
            pontos.append(row_["efeito_percentual_aprox"])
            erros.append(1.96 * row_["erro_padrao"] * 100)
        ax.barh(y_positions + offset, pontos, xerr=erros, height=bar_height, color=color,
                label=label, zorder=3, error_kw={"elinewidth": 1.3, "capsize": 3})
    ax.axvline(0, color=INK_SECONDARY, linewidth=1, zorder=1)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([RACA_LABELS_PLAIN[r] for r in RACA_NIVEIS])
    ax.invert_yaxis()
    ax.set_xlabel("Gap racial aprox. (%) entre formais, ref.: branco")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    fig.suptitle("Gap racial entre formais, por setor (renda por hora real)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "raca_setor_publico")


def fig_interseccionalidade_genero_raca() -> None:
    # Mulher preta/parda/indígena: o efeito combinado observado (com a interação Mulher×Raça
    # já presente no modelo M4) é igual à soma aditiva simples dos efeitos de gênero e raça
    # isolados, ou existe heterogeneidade adicional? Compara "soma aditiva" (contrafactual sem
    # interação) com "mulher X" (efeito realmente estimado, com interação).
    tbl = load_r_interseccionalidade()

    fig, ax = plt.subplots(figsize=(8, 4.4))
    y_positions = np.arange(len(RACA_NIVEIS))
    bar_height = 0.32
    for i, (suf, color, label) in enumerate([
        ("soma_aditiva_implicaria", INK_SECONDARY, "Soma aditiva (sem interação)"),
        ("mulher", ORANGE, "Mulher X (observado, com interação)"),
    ]):
        offset = (0.5 - i) * bar_height
        pontos, erros = [], []
        for r in RACA_NIVEIS:
            row_ = tbl.loc[f"{r}_{suf}"]
            pontos.append(row_["efeito_percentual_aprox"])
            erros.append(1.96 * row_["erro_padrao"] * 100)
        ax.barh(y_positions + offset, pontos, xerr=erros, height=bar_height, color=color,
                label=label, zorder=3, error_kw={"elinewidth": 1.3, "capsize": 3})
    ax.axvline(0, color=INK_SECONDARY, linewidth=1, zorder=1)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([f"Mulher {RACA_LABELS_PLAIN[r]}" for r in RACA_NIVEIS])
    ax.invert_yaxis()
    ax.set_xlabel("Efeito aprox. (%) vs. homem branco, renda/hora")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(left=ax.get_xlim()[0] * 1.1)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=2, frameon=False, fontsize=9)
    fig.suptitle("Mulher × raça: soma aditiva vs. efeito observado", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "interseccionalidade_genero_raca")


# ---------------------------------------------------------------------------
# Tabelas LaTeX
# ---------------------------------------------------------------------------

def make_tab_modelo(dv: str, convergencia: pd.DataFrame) -> str:
    ampla = load_r_nested("ampla", dv, "M4")
    restrita = load_r_nested("restrita", dv, "M4")
    termos = [("formal", "Formal (ref.: informal)")] + [
        (raca_term(r), f"{RACA_LABELS[r]} (ref.: branco)") for r in RACA_NIVEIS
    ] + [("mulher", "Mulher (ref.: homem)"), ("formal:mulher", "Formal $\\times$ Mulher")] + [
        (f"formal:{raca_term(r)}", f"Formal $\\times$ {RACA_LABELS[r]}") for r in RACA_NIVEIS
    ]

    lines = ["\\begin{tabular}{lcc}", "\\toprule", " & Amostra ampla & Amostra restrita \\\\", "\\midrule"]
    for termo, label in termos:
        ra = ampla.loc[termo]
        rr = restrita.loc[termo]
        lines.append(
            f"{label} & {fmt_num(ra['coeficiente'], sign=True)}{stars(ra['p_valor'])} ({fmt_num(ra['erro_padrao'])}) & "
            f"{fmt_num(rr['coeficiente'], sign=True)}{stars(rr['p_valor'])} ({fmt_num(rr['erro_padrao'])}) \\\\"
        )
    lines.append("\\midrule")
    n_ampla = convergencia.loc[convergencia["especificacao"] == f"ampla_{dv}_M4", "n_obs"].iloc[0]
    n_restrita = convergencia.loc[convergencia["especificacao"] == f"restrita_{dv}_M4", "n_obs"].iloc[0]
    lines.append(f"Observa\\c{{c}}\\~oes & {fmt_int(n_ampla)} & {fmt_int(n_restrita)} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def make_tab_contrastes() -> str:
    hora_ampla = load_r_contrastes("ampla", "ln_renda_hora_real")

    def row(id_, label):
        r = hora_ampla.loc[id_]
        return f"{label} & {fmt_pct(r['efeito_percentual_aprox'])}{stars(r['p_valor'])} \\\\"

    lines = [
        "\\begin{tabular}{lc}", "\\toprule", " & Efeito \\% (renda/hora) \\\\", "\\midrule",
        "\\multicolumn{2}{l}{\\textit{G\\^enero (ref.: homem)}} \\\\",
        row("genero_gap_informal", "\\quad Mulher, entre informais"),
        row("genero_gap_formal", "\\quad Mulher, entre formais"),
        "\\midrule",
        "\\multicolumn{2}{l}{\\textit{Ra\\c{c}a/cor (ref.: branco)}} \\\\",
    ]
    for r in RACA_NIVEIS:
        lines.append(row(f"raca_{r}_gap_informal", f"\\quad {RACA_LABELS[r]}, entre informais"))
        lines.append(row(f"raca_{r}_gap_formal", f"\\quad {RACA_LABELS[r]}, entre formais"))
    lines += [
        "\\midrule",
        "\\multicolumn{2}{l}{\\textit{Pr\\^emio de formalidade}} \\\\",
        row("formal_homem_branco", "\\quad Homem branco"),
        row("formal_mulher_preto", "\\quad Mulher preta"),
        row("formal_mulher_pardo", "\\quad Mulher parda"),
        row("formal_mulher_indigena", "\\quad Mulher ind\\'igena"),
        "\\bottomrule", "\\end{tabular}",
    ]
    return "\n".join(lines)


def make_tab_prob_formal() -> str:
    # AME (p.p.) da probabilidade de estar em posição formal -- "quem acessa a formalidade",
    # não "quanto formalidade paga" (esse é o modelo de renda, tab_hora/tab_mensal). Nenhum
    # termo é significativo a 10% em nenhuma amostra -- ver r/10_probabilidade_formalizacao.R.
    ampla = load_r_prob_formal_ame("ampla")
    restrita = load_r_prob_formal_ame("restrita")
    termos = [("mulher", "Mulher (ref.: homem)")] + [
        (r, f"{RACA_LABELS[r]} (ref.: branco)") for r in RACA_NIVEIS
    ]

    lines = ["\\begin{tabular}{lcc}", "\\toprule", " & Todos os ocupados & Empregados \\\\", "\\midrule"]
    for termo, label in termos:
        ra = ampla.loc[termo]
        rr = restrita.loc[termo]
        lines.append(
            f"{label} & {fmt_num(ra['ame_pp'], 1, sign=True)}{stars(ra['p_valor'])} p.p. ({fmt_num(ra['erro_padrao_pp'], 1)}) & "
            f"{fmt_num(rr['ame_pp'], 1, sign=True)}{stars(rr['p_valor'])} p.p. ({fmt_num(rr['erro_padrao_pp'], 1)}) \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def make_tab_raca_setor_publico() -> str:
    # Gap racial (entre formais, ref.: branco) por setor -- privado vs. público -- e teste de
    # diferença design-based. Ver r/13_raca_setor_publico.R.
    hora = load_r_raca_setor_publico_contrastes("ln_renda_hora_real")
    lines = [
        "\\begin{tabular}{lccc}", "\\toprule",
        "Ref.: branco, formal & Privado/dom\\'estico & P\\'ublico & Diferen\\c{c}a \\\\", "\\midrule",
    ]
    for r in RACA_NIVEIS:
        priv = hora.loc[f"{r}_formal_privado"]
        pub = hora.loc[f"{r}_formal_publico"]
        dif = hora.loc[f"{r}_diferenca_publico_privado"]
        lines.append(
            f"{RACA_LABELS[r]} & {fmt_pct(priv['efeito_percentual_aprox'])}{stars(priv['p_valor'])} & "
            f"{fmt_pct(pub['efeito_percentual_aprox'])}{stars(pub['p_valor'])} & "
            f"{fmt_pct(dif['efeito_percentual_aprox'])}{stars(dif['p_valor'])} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def make_tab_interseccionalidade() -> str:
    # Mulher X: soma aditiva (contrafactual sem Mulher×Raça) vs. efeito observado (com a
    # interação já presente no modelo M4) -- e o teste direto da interação (heterogeneidade
    # além do aditivo). Ver r/14_interseccionalidade_genero_raca.R.
    tbl = load_r_interseccionalidade()
    lines = [
        "\\begin{tabular}{lcccc}", "\\toprule",
        "Ref.: homem branco & Homem X & Mulher X (aditivo) & Mulher X (observado) & Intera\\c{c}\\~ao \\\\",
        "\\midrule",
    ]
    for r in RACA_NIVEIS:
        homem = tbl.loc[f"{r}_homem"]
        aditivo = tbl.loc[f"{r}_soma_aditiva_implicaria"]
        observado = tbl.loc[f"{r}_mulher"]
        inter = tbl.loc[f"{r}_interacao"]
        lines.append(
            f"{RACA_LABELS[r]} & {fmt_pct(homem['efeito_percentual_aprox'])}{stars(homem['p_valor'])} & "
            f"{fmt_pct(aditivo['efeito_percentual_aprox'])}{stars(aditivo['p_valor'])} & "
            f"{fmt_pct(observado['efeito_percentual_aprox'])}{stars(observado['p_valor'])} & "
            f"{fmt_pct(inter['efeito_percentual_aprox'])}{stars(inter['p_valor'])} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def make_tab_composicao_racial(common: pd.DataFrame) -> str:
    # Tabela puramente descritiva (sem regressão) -- dá ao leitor a matéria-prima para entender
    # POR QUE o gap bruto racial é tão grande e por que educação domina a decomposição
    # sequencial: escolaridade, formalidade, setor público e inserção ocupacional por raça,
    # ponderadas pelo peso amostral. Testa empiricamente a associação indígena com
    # ruralidade/agricultura/informalidade já documentada por Souza (dissertação), Atal, Ñopo &
    # Winder e Canedo (2019) para o contexto de Roraima especificamente.
    def wpct(mask: pd.Series) -> pd.Series:
        peso = common["peso"]
        return (peso[mask].groupby(common.loc[mask, "raca_grupo"]).sum() / peso.groupby(common["raca_grupo"]).sum() * 100).reindex(RACA_TODAS)

    linhas_dados = [
        ("Superior completo", wpct(common["escolaridade"] == "7")),
        ("Sem instr./fund.\\ incompleto", wpct(common["escolaridade"] == "1")),
        ("Formal", wpct(common["formal"] == 1)),
        ("Setor p\\'ublico", wpct(common["setor_publico"] == 1)),
        ("Atividade agr\\'icola", wpct(common["atividade_grupo"] == "1")),
        ("Conta-pr\\'opria", wpct(common["posicao_ocupacao_grupo"] == "conta_propria")),
        ("Empregado (v\\'inculo)", wpct(common["empregado_restrito"] == 1)),
    ]

    lines = [
        "\\begin{tabular}{lcccc}", "\\toprule",
        " & Branco & Preto & Pardo & Ind\\'igena \\\\", "\\midrule",
    ]
    for label, vals in linhas_dados:
        lines.append(
            f"{label} & {fmt_pct(vals['branco'], 1, sign=False)} & {fmt_pct(vals['preto'], 1, sign=False)} & "
            f"{fmt_pct(vals['pardo'], 1, sign=False)} & {fmt_pct(vals['indigena'], 1, sign=False)} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def make_tab_setor_publico() -> str:
    mensal = load_r_setor_publico("ln_renda_mensal_real")
    hora = load_r_setor_publico("ln_renda_hora_real")
    termos = [("formal", "Formal (privado/dom\\'estico)"), ("setor_publico", "Setor p\\'ublico"),
              ("formal:setor_publico", "Formal $\\times$ Setor p\\'ublico")]
    lines = ["\\begin{tabular}{lcc}", "\\toprule", " & Renda mensal & Renda por hora \\\\", "\\midrule"]
    for termo, label in termos:
        rm = mensal.loc[termo]
        rh = hora.loc[termo]
        lines.append(
            f"{label} & {fmt_pct(pct_effect(rm['coeficiente']))}{stars(rm['p_valor'])} & "
            f"{fmt_pct(pct_effect(rh['coeficiente']))}{stars(rh['p_valor'])} \\\\"
        )
    lines.append("\\midrule")
    lines.append("Observa\\c{c}\\~oes & \\multicolumn{2}{c}{16.135 (amostra restrita)} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def make_tab_posicao() -> str:
    hora = load_r_posicao_ocupacao("ln_renda_hora_real")
    desc = load_r_posicao_descritivo().set_index("posicao_ocupacao_grupo")
    labels_map = {
        "militar_estatutario": "Militar/estatut\\'ario", "empregador": "Empregador",
        "publico_com_carteira": "P\\'ublico, c/carteira", "publico_sem_carteira": "P\\'ublico, s/carteira",
        "privado_com_carteira": "Privado, c/carteira", "conta_propria": "Conta-pr\\'opria",
        "domestico_com_carteira": "Dom\\'estico, c/carteira", "domestico_sem_carteira": "Dom\\'estico, s/carteira",
    }
    ordem = hora.filter(like="factor(posicao_ocupacao_grupo)", axis=0)
    ordem = ordem.assign(efeito=lambda d: (np.exp(d["coeficiente"]) - 1) * 100).sort_values("efeito", ascending=False)

    lines = [
        "\\begin{tabular}{lcc}", "\\toprule",
        " & R\\$/h m\\'edio & Efeito condicional \\\\", "\\midrule",
    ]
    for idx, row_ in ordem.iterrows():
        pos = idx.replace("factor(posicao_ocupacao_grupo)", "")
        media = desc.loc[pos, "renda_hora_media"] if pos in desc.index else float("nan")
        lines.append(
            f"{labels_map.get(pos, pos)} & R\\$\\,{fmt_num(media, 2)} & "
            f"{fmt_pct(row_['efeito'])}{stars(row_['p_valor'])} \\\\"
        )
    media_ref = desc.loc["privado_sem_carteira", "renda_hora_media"]
    lines.append(f"Privado, s/carteira (refer\\^encia) & R\\$\\,{fmt_num(media_ref, 2)} & --- \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def make_tab_mecanismo() -> str:
    mensal = load_r_jornada("ampla", "ln_renda_mensal_real")
    hora = load_r_jornada("ampla", "ln_renda_hora_real")
    horas_dv = load_r_jornada("ampla", "ln_horas_semanais_principal")
    termos = [("formal", "Formal"), ("mulher", "Mulher")] + [
        (raca_term(r), RACA_LABELS[r]) for r in RACA_NIVEIS
    ]
    lines = [
        "\\begin{tabular}{lccc}", "\\toprule",
        " & Mensal & Por hora (pre\\c{c}o) & Horas (\\%) \\\\", "\\midrule",
    ]
    for termo, label in termos:
        m = mensal.loc[termo]
        h = hora.loc[termo]
        hd = horas_dv.loc[termo]
        lines.append(
            f"{label} & {fmt_pct(pct_effect(m['coeficiente']))}{stars(m['p_valor'])} & "
            f"{fmt_pct(pct_effect(h['coeficiente']))}{stars(h['p_valor'])} & "
            f"{fmt_pct(pct_effect(hd['coeficiente']))}{stars(hd['p_valor'])} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Macros e main
# ---------------------------------------------------------------------------

def main() -> None:
    ensure_project_dirs()

    df = pd.read_parquet(PROCESSED_DIR / "pnadc_rr_analitica.parquet")
    common = df.loc[df["formal"].notna() & df["mulher"].notna() & df["peso"].notna()].copy()
    hourly = common.loc[common["renda_hora_real"] > 0].copy()
    monthly = common.loc[common["renda_mensal_real"] > 0].copy()

    mean_hora = wavg(hourly["renda_hora_real"], hourly["peso"])
    mean_mensal = wavg(monthly["renda_mensal_real"], monthly["peso"])

    def group_pair(data: pd.DataFrame, col: str, val0=0, val1=1) -> tuple:
        g0 = data.loc[data[col] == val0]
        g1 = data.loc[data[col] == val1]
        return wavg(g0["renda_hora_real"], g0["peso"]), wavg(g1["renda_hora_real"], g1["peso"])

    raw_gaps = {
        "formal": group_pair(hourly, "formal"),
        "mulher": group_pair(hourly, "mulher"),
        "raca": group_pair(hourly, "raca_grupo", "branco", None) if False else (
            wavg(hourly.loc[hourly["raca_grupo"] == "branco", "renda_hora_real"], hourly.loc[hourly["raca_grupo"] == "branco", "peso"]),
            wavg(hourly.loc[hourly["preto_pardo"] == 1, "renda_hora_real"], hourly.loc[hourly["preto_pardo"] == 1, "peso"]),
        ),
    }

    audit_totais = pd.read_csv(TABLES_DIR / "auditoria_totais.csv").iloc[0]

    # --- figuras ---
    fig_motivacao(raw_gaps)
    fig_sensibilidade()
    fig_setor_publico()
    info_publica = fig_informalidade_publica(common)
    comp_racial_publico = fig_composicao_racial_publico(common)
    fig_mecanismo()
    fig_gap_reais(mean_mensal, mean_hora)
    fig_robustez()
    fig_tendencia_flexivel()
    fig_prob_formal_ame()
    fig_decomposicao_genero()
    fig_decomposicao_raca()
    fig_raca_setor_publico()
    fig_interseccionalidade_genero_raca()

    # --- tabelas ---
    convergencia = pd.read_csv(TABLES_DIR / "r_nested_convergencia.csv")
    tabelas = {
        "tab_hora.tex": make_tab_modelo("ln_renda_hora_real", convergencia),
        "tab_mensal.tex": make_tab_modelo("ln_renda_mensal_real", convergencia),
        "tab_contrastes.tex": make_tab_contrastes(),
        "tab_setor_publico.tex": make_tab_setor_publico(),
        "tab_posicao.tex": make_tab_posicao(),
        "tab_mecanismo.tex": make_tab_mecanismo(),
        "tab_prob_formal.tex": make_tab_prob_formal(),
        "tab_raca_setor_publico.tex": make_tab_raca_setor_publico(),
        "tab_interseccionalidade.tex": make_tab_interseccionalidade(),
        "tab_composicao_racial.tex": make_tab_composicao_racial(common),
    }
    for name, content in tabelas.items():
        (PRESENTATION_GERADO_DIR / name).write_text(content, encoding="utf-8")
        print(f"saved: {PRESENTATION_GERADO_DIR / name}")

    # --- macros narrativas ---
    macros = {}
    macros["NTotal"] = fmt_int(audit_totais["n_total"])
    macros["NQuatorzeMais"] = fmt_int(audit_totais["n_14_mais"])
    macros["NOcupados"] = fmt_int(audit_totais["n_ocupados"])
    macros["NRendaValida"] = fmt_int(audit_totais["n_ocupados_renda_valida"])
    macros["NAmpla"] = "23.938"
    macros["NRestrita"] = "16.135"
    macros["NSetorPublico"] = "5.791"
    macros["PctSetorPublico"] = fmt_pct(5791 / 24414 * 100, 1, sign=False)
    macros["MediaMensal"] = fmt_brl(mean_mensal)
    macros["MediaHora"] = fmt_brl(mean_hora, 2)

    for termo_dv_key, (g0, g1) in raw_gaps.items():
        key = {"formal": "Formal", "mulher": "Mulher", "raca": "Raca"}[termo_dv_key]
        macros[f"Bruto{key}GrupoRef"] = fmt_brl(g0, 2)
        macros[f"Bruto{key}GrupoComp"] = fmt_brl(g1, 2)
        macros[f"BrutoGap{key}Pct"] = fmt_pct((g1 / g0 - 1) * 100)

    for amostra, amostra_key in [("ampla", "Ampla"), ("restrita", "Restrita")]:
        for dv, dv_key in [("ln_renda_mensal_real", "Mensal"), ("ln_renda_hora_real", "Hora")]:
            tbl = load_r_nested(amostra, dv, "M4")
            for termo, termo_key in [("formal", "Formal"), ("mulher", "Mulher")] + [
                (raca_term(r), r.capitalize()) for r in RACA_NIVEIS
            ]:
                row_ = tbl.loc[termo]
                macros[f"Pct{termo_key}{dv_key}{amostra_key}"] = fmt_pct(pct_effect(row_["coeficiente"]))
                macros[f"Reais{termo_key}{dv_key}{amostra_key}"] = fmt_brl(
                    pct_effect(row_["coeficiente"]) / 100 * (mean_mensal if dv_key == "Mensal" else mean_hora),
                    0 if dv_key == "Mensal" else 2,
                )

    contrastes_ampla_hora = load_r_contrastes("ampla", "ln_renda_hora_real")
    for id_, key in [
        ("genero_gap_informal", "GeneroInformal"), ("genero_gap_formal", "GeneroFormal"),
        ("genero_diferenca_formal_informal", "GeneroDiferenca"),
    ]:
        r = contrastes_ampla_hora.loc[id_]
        macros[f"Pct{key}"] = fmt_pct(r["efeito_percentual_aprox"])
        macros[f"PValor{key}"] = fmt_num(r["p_valor"], 3)
    for raca in RACA_NIVEIS:
        raca_key = raca.capitalize()
        for suf, key in [("gap_informal", "Informal"), ("gap_formal", "Formal"), ("diferenca_formal_informal", "Diferenca")]:
            r = contrastes_ampla_hora.loc[f"raca_{raca}_{suf}"]
            macros[f"Pct{raca_key}{key}"] = fmt_pct(r["efeito_percentual_aprox"])
            macros[f"PValor{raca_key}{key}"] = fmt_num(r["p_valor"], 3)
    for raca in RACA_NIVEIS:
        r = contrastes_ampla_hora.loc[f"formal_mulher_{raca}"]
        macros[f"PctFormalMulher{raca.capitalize()}"] = fmt_pct(r["efeito_percentual_aprox"])
    r = contrastes_ampla_hora.loc["formal_homem_branco"]
    macros["PctFormalHomemBranco"] = fmt_pct(r["efeito_percentual_aprox"])

    # gap de gênero/formal em R$ (conversão do contraste ponderado, não do coeficiente bruto)
    r = contrastes_ampla_hora.loc["genero_gap_informal"]
    macros["ReaisGeneroInformal"] = fmt_brl(r["efeito_percentual_aprox"] / 100 * mean_hora, 2)

    # prêmio de formalidade populacional (ponderado por gênero e raça, não só homem branco)
    for amostra, amostra_key in [("ampla", "Ampla"), ("restrita", "Restrita")]:
        for dv, dv_key in [("ln_renda_mensal_real", "Mensal"), ("ln_renda_hora_real", "Hora")]:
            contrastes = load_r_contrastes(amostra, dv)
            r = contrastes.loc["formal_gap_geral"]
            macros[f"PctFormalGeral{dv_key}{amostra_key}"] = fmt_pct(r["efeito_percentual_aprox"])
            macros[f"ReaisFormalGeral{dv_key}{amostra_key}"] = fmt_brl(
                r["efeito_percentual_aprox"] / 100 * (mean_mensal if dv_key == "Mensal" else mean_hora),
                0 if dv_key == "Mensal" else 2,
            )

    # efeito combinado formal+setor público, com IC 95% design-based (não soma ingênua de SEs)
    for dv, dv_key in [("ln_renda_mensal_real", "Mensal"), ("ln_renda_hora_real", "Hora")]:
        r = load_r_setor_publico_combinado(dv)
        macros[f"PctFormalPublicoCombinadoIC{dv_key}Inf"] = fmt_pct(r["ic95_inf"])
        macros[f"PctFormalPublicoCombinadoIC{dv_key}Sup"] = fmt_pct(r["ic95_sup"])

    # setor público -- termo "Formal" aqui vem de uma especificação DIFERENTE do M4 principal
    # (inclui setor_publico + formal:setor_publico), então o coeficiente de "formal" não é o
    # mesmo do modelo principal (referência passa a ser privado/doméstico especificamente).
    # Sufixo "SP" evita colidir com Pct{termo_key}{dv_key}{amostra_key} do modelo principal
    # (mesma combinação Formal+Hora/Mensal+Restrita) -- collision silenciosa detectada em
    # revisão: \PctFormalHoraRestrita estava sendo sobrescrito por este bloco.
    for dv, dv_key in [("ln_renda_mensal_real", "Mensal"), ("ln_renda_hora_real", "Hora")]:
        tbl = load_r_setor_publico(dv)
        for termo, key in [("formal", "Formal"), ("setor_publico", "SetorPublico"), ("formal:setor_publico", "FormalSetorPublico")]:
            r = tbl.loc[termo]
            macros[f"Pct{key}{dv_key}RestritaSP"] = fmt_pct(pct_effect(r["coeficiente"]))
            macros[f"PValor{key}{dv_key}RestritaSP"] = fmt_num(r["p_valor"], 3)
        soma = tbl.loc["formal", "coeficiente"] + tbl.loc["setor_publico", "coeficiente"] + tbl.loc["formal:setor_publico", "coeficiente"]
        macros[f"PctFormalPublicoCombinado{dv_key}"] = fmt_pct(pct_effect(soma))

    # informalidade dentro do setor público: composição ocupacional/setorial
    macros["NInformalPublicoNaoPond"] = fmt_int(info_publica["n_naopond"])
    macros["NInformalPublicoPond"] = fmt_int(info_publica["n_pond"])
    n_ocupados = audit_totais["n_ocupados"]
    macros["PctInformalPublicoDoOcupados"] = fmt_pct(info_publica["n_naopond"] / n_ocupados * 100, 1, sign=False)
    macros["PctInformalPublicoOcupPrincipais"] = fmt_pct(info_publica["ocup_top3_pct"], 1, sign=False)
    macros["PctInformalPublicoAtivAdmPub"] = fmt_pct(info_publica["ativ_admpub_pct"], 1, sign=False)
    macros["PctInformalPublicoAtivEducSaude"] = fmt_pct(info_publica["ativ_educsaude_pct"], 1, sign=False)

    # composição racial por posição pública -- checagem de sorting vs. preço
    comp = comp_racial_publico["comp"]
    n_comp = comp_racial_publico["n"]
    for pos, key in [("publico_sem_carteira", "PubSemCarteira"), ("publico_com_carteira", "PubComCarteira"),
                      ("militar_estatutario", "Militar")]:
        for r in RACA_TODAS:
            macros[f"PctComp{r.capitalize()}{key}"] = fmt_pct(comp.loc[r, pos], 1, sign=False)
        macros[f"NComp{key}"] = fmt_int(n_comp.loc[pos].sum())
    macros["NCompIndigenaMilitar"] = fmt_int(n_comp.loc["militar_estatutario", "indigena"])
    macros["NCompIndigenaPubComCarteira"] = fmt_int(n_comp.loc["publico_com_carteira", "indigena"])

    # posição na ocupação: melhor e pior
    hora_pos = load_r_posicao_ocupacao("ln_renda_hora_real")
    ordem = hora_pos.filter(like="factor(posicao_ocupacao_grupo)", axis=0)
    ordem = ordem.assign(efeito=lambda d: (np.exp(d["coeficiente"]) - 1) * 100).sort_values("efeito")
    pior = ordem.iloc[0]
    melhor = ordem.iloc[-1]
    macros["PosicaoPiorNome"] = "trabalhador dom\\'estico sem carteira"
    macros["PosicaoPiorPct"] = fmt_pct(pior["efeito"])
    macros["PosicaoMelhorNome"] = "militar ou servidor estatut\\'ario"
    macros["PosicaoMelhorPct"] = fmt_pct(melhor["efeito"])

    # mecanismo de jornada -- formal/mulher usam as versões "_pop" (média ponderada por
    # gênero/raça via contrast_weighted em r/03_jornada_decomposicao.R): o modelo tem
    # Mulher×Raça e Formal×Raça, então os coeficientes puros "formal"/"mulher" são específicos
    # de homem branco/mulher branca, não a média populacional que o slide de mecanismo relata.
    identidade_ampla = load_r_jornada_identidade("ampla")
    for termo, key in [("formal_pop", "Formal"), ("mulher_pop", "Mulher"), ("formal:mulher", "FormalMulher")] + [
        (raca_term(r), r.capitalize()) for r in RACA_NIVEIS
    ]:
        r = identidade_ampla.loc[termo]
        pct_jornada = r["beta_ln_horas"] / r["beta_mensal"] * 100 if r["beta_mensal"] != 0 else float("nan")
        macros[f"PctJornada{key}"] = fmt_num(pct_jornada, 0, sign=False)
        macros[f"HorasEfeito{key}"] = fmt_pct(pct_effect(r["beta_ln_horas"]))

    # evolução temporal (tendência linear, R/survey)
    trend = load_r_tendencia()
    for termo, key in [("formal:Ano", "Formal"), ("mulher:Ano", "Mulher")] + [
        (f"{raca_term(r)}:Ano", r.capitalize()) for r in RACA_NIVEIS
    ]:
        r = trend.loc[termo]
        macros[f"Incl{key}PctAno"] = fmt_pct(r["efeito_percentual_aprox_por_ano"], 2)
        macros[f"PValorIncl{key}"] = fmt_num(r["p_valor"], 3)

    # robustez
    trimestres = load_r_robustez_trimestres()
    macros["NTodosTrimestres"] = "97.187"
    for termo, key in [("formal", "Formal"), ("mulher", "Mulher")] + [(raca_term(r), r.capitalize()) for r in RACA_NIVEIS]:
        for esp, esp_key in [("q4_only", "QuartoTri"), ("todos_trimestres", "Todos")]:
            row_ = trimestres[(trimestres["termo"] == termo) & (trimestres["dv"] == "ln_renda_hora_real") & (trimestres["especificacao"] == esp)]
            if not row_.empty:
                macros[f"Pct{key}Hora{esp_key}"] = fmt_pct(row_["efeito_percentual_aprox"].iloc[0])

    # probabilidade de formalização (AME, p.p.) -- acesso à formalidade, não retorno
    for amostra, amostra_key in [("ampla", "Ampla"), ("restrita", "Restrita")]:
        tbl = load_r_prob_formal_ame(amostra)
        for termo, termo_key in [("mulher", "Mulher")] + [(r, r.capitalize()) for r in RACA_NIVEIS]:
            row_ = tbl.loc[termo]
            macros[f"AmePp{termo_key}{amostra_key}"] = fmt_num(row_["ame_pp"], 1, sign=True)
            macros[f"PValorAme{termo_key}{amostra_key}"] = fmt_num(row_["p_valor"], 3)

    # decomposição sequencial do gap de gênero
    decomp = load_r_decomposicao_genero()
    for m, key in [
        ("M0", "Bruto"), ("M1", "Demografia"), ("M2", "Educacao"), ("M3", "Atividade"),
        ("M4", "Ocupacao"), ("M5", "OcupAtiv"), ("M6", "SetorPublico"), ("M7", "Horas"),
    ]:
        r = decomp.loc[m]
        macros[f"DecompGenero{key}"] = fmt_pct(r["efeito_percentual_aprox"])
        macros[f"PValorDecompGenero{key}"] = fmt_num(r["p_valor"], 3)

    # decomposição sequencial do gap racial
    decomp_raca = load_r_decomposicao_raca().set_index(["modelo", "raca"])
    for m, key in [
        ("M0", "Bruto"), ("M1", "Demografia"), ("M2", "Educacao"), ("M3", "Atividade"),
        ("M4", "Ocupacao"), ("M5", "OcupAtiv"), ("M6", "SetorPublico"),
    ]:
        for raca in RACA_NIVEIS:
            r = decomp_raca.loc[(m, raca)]
            macros[f"DecompRaca{key}{raca.capitalize()}"] = fmt_pct(r["efeito_percentual_aprox"])
            macros[f"PValorDecompRaca{key}{raca.capitalize()}"] = fmt_num(r["p_valor"], 3)

    # raça x setor público: gap racial entre formais, por setor
    hora_rsp = load_r_raca_setor_publico_contrastes("ln_renda_hora_real")
    for raca in RACA_NIVEIS:
        raca_key = raca.capitalize()
        for suf, key in [
            ("formal_privado", "FormalPrivado"), ("formal_publico", "FormalPublico"),
            ("informal_privado", "InformalPrivado"), ("informal_publico", "InformalPublico"),
            ("diferenca_publico_privado", "DiferencaPublicoPrivado"),
        ]:
            r = hora_rsp.loc[f"{raca}_{suf}"]
            macros[f"PctRacaSP{key}{raca_key}"] = fmt_pct(r["efeito_percentual_aprox"])
            macros[f"PValorRacaSP{key}{raca_key}"] = fmt_num(r["p_valor"], 3)

    # interseccionalidade gênero x raça: soma aditiva vs. observado (interação Mulher×Raça)
    intersecc = load_r_interseccionalidade()
    for raca in RACA_NIVEIS:
        raca_key = raca.capitalize()
        for suf, key in [
            ("homem", "Homem"), ("mulher", "Mulher"),
            ("soma_aditiva_implicaria", "Aditivo"), ("interacao", "Interacao"),
        ]:
            r = intersecc.loc[f"{raca}_{suf}"]
            macros[f"PctIntersecc{key}{raca_key}"] = fmt_pct(r["efeito_percentual_aprox"])
            macros[f"PValorIntersecc{key}{raca_key}"] = fmt_num(r["p_valor"], 3)
    macros["PctInterseccMulherBranca"] = fmt_pct(intersecc.loc["preto_mulher_branca", "efeito_percentual_aprox"])

    # composição racial descritiva -- matéria-prima para "por que o gap bruto racial é grande"
    peso_comp = common["peso"]
    raca_comp = common["raca_grupo"]

    def wpct_macro(mask: pd.Series, raca: str) -> float:
        raca_idx = raca_comp == raca
        return float(peso_comp[mask & raca_idx].sum() / peso_comp[raca_idx].sum() * 100)

    for raca in RACA_TODAS:
        macros[f"PctSuperior{raca.capitalize()}"] = fmt_pct(wpct_macro(common["escolaridade"] == "7", raca), 1, sign=False)
        macros[f"PctAgricola{raca.capitalize()}"] = fmt_pct(wpct_macro(common["atividade_grupo"] == "1", raca), 1, sign=False)
        macros[f"PctFormalBruto{raca.capitalize()}"] = fmt_pct(wpct_macro(common["formal"] == 1, raca), 1, sign=False)

    lines = ["% Gerado automaticamente por scripts/08_make_presentation_assets.py. Não editar à mão.", ""]
    for name, value in macros.items():
        lines.append(f"\\newcommand{{\\{name}}}{{{value}\\xspace}}")
    output = PRESENTATION_GERADO_DIR / "numeros.tex"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved: {output} ({len(macros)} macros)")


if __name__ == "__main__":
    main()
