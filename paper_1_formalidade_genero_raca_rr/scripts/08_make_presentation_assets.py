"""Generate figures, LaTeX regression tables, and narrative-number macros for the Beamer presentation.

Reads the already-estimated models in outputs/tables/ and outputs/models/ (produced by
scripts 03, 06 and 07) plus the analytic dataset, and writes:

- outputs/figures/*.pdf (+ .png for quick preview): motivation gaps, coefficient robustness
  forest plot, jornada-mechanism decomposition, R$ gap chart.
- presentation/gerado/tab_mensal.tex, tab_hora.tex, tab_mecanismo.tex: LaTeX regression tables.
- presentation/gerado/numeros.tex: \\newcommand macros with narrative numbers (R$, %, hours,
  sample sizes), so slide prose never hand-transcribes a number that could drift from the data.
"""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

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
GRAY_REF = "#c3c2b7"
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


# ---------------------------------------------------------------------------
# Formatting helpers (pt-BR number style for the .tex output)
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


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_model(label: str) -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / f"modelo_base_{label}.csv", index_col=0)


def load_stats(label: str) -> dict:
    stats = pd.read_csv(TABLES_DIR / f"modelo_base_{label}_estatisticas.csv", index_col="chave")
    return stats["valor"].to_dict()


def wavg(values: pd.Series, weights: pd.Series) -> float:
    return float(np.average(values, weights=weights))


TERMS = ["formal", "mulher", "preto_pardo", "formal:mulher", "formal:preto_pardo"]
TERM_LABELS = {
    "formal": "Formal (ref.: informal)",
    "mulher": "Mulher (ref.: homem)",
    "preto_pardo": "Preto/pardo (ref.: branco/amarelo/ind\\'igena)",
    "formal:mulher": "Formal $\\times$ Mulher",
    "formal:preto_pardo": "Formal $\\times$ Preto/pardo",
}
KEY_TERMS = ["formal", "mulher", "preto_pardo"]
KEY_TERM_LABELS_SHORT = {"formal": "Formal", "mulher": "Mulher", "preto_pardo": "Preto/pardo"}


# ---------------------------------------------------------------------------
# LaTeX regression table
# ---------------------------------------------------------------------------

def make_regression_table(label_sem: str, label_com: str, caption: str) -> str:
    sem = load_model(label_sem)
    com = load_model(label_com)
    stats_sem = load_stats(label_sem)
    stats_com = load_stats(label_com)

    lines = [
        "\\begin{tabular}{lcc}",
        "\\toprule",
        " & (1) Sem controles & (2) Com controles \\\\",
        "\\midrule",
    ]
    for term in TERMS:
        row_sem = sem.loc[term]
        row_com = com.loc[term]
        lines.append(
            f"{TERM_LABELS[term]} & "
            f"{fmt_num(row_sem['coeficiente'], sign=True)}{stars(row_sem['p_valor'])} & "
            f"{fmt_num(row_com['coeficiente'], sign=True)}{stars(row_com['p_valor'])} \\\\"
        )
        lines.append(
            f" & ({fmt_num(row_sem['erro_padrao'])}) & ({fmt_num(row_com['erro_padrao'])}) \\\\"
        )
    lines.append("\\midrule")
    lines.append("Controles (ocup., ativ., escol., idade, per\\'iodo) & N\\~ao & Sim \\\\")
    lines.append(f"Observa\\c{{c}}\\~oes & {fmt_int(stats_sem['nobs'])} & {fmt_int(stats_com['nobs'])} \\\\")
    lines.append(f"R$^2$ & {fmt_num(stats_sem['rsquared'], 3)} & {fmt_num(stats_com['rsquared'], 3)} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def make_mecanismo_table() -> str:
    sem_horas = load_model("ln_renda_mensal_real_amostra_jornada")
    com_horas = load_model("ln_renda_mensal_real_com_horas")
    hora = load_model("ln_renda_hora_real_amostra_jornada")
    horas_dv = load_model("horas_semanais")

    lines = [
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        " & \\shortstack{Mensal\\\\sem horas} & \\shortstack{Mensal\\\\com horas} & "
        "\\shortstack{Por\\\\hora} & \\shortstack{Horas\\\\semanais} \\\\",
        "\\midrule",
    ]
    for term in KEY_TERMS:
        e_sem = pct_effect(sem_horas.loc[term, "coeficiente"])
        e_com = pct_effect(com_horas.loc[term, "coeficiente"])
        e_hora = pct_effect(hora.loc[term, "coeficiente"])
        e_horas = horas_dv.loc[term, "coeficiente"]
        lines.append(
            f"{KEY_TERM_LABELS_SHORT[term]} & "
            f"{fmt_pct(e_sem)}{stars(sem_horas.loc[term, 'p_valor'])} & "
            f"{fmt_pct(e_com)}{stars(com_horas.loc[term, 'p_valor'])} & "
            f"{fmt_pct(e_hora)}{stars(hora.loc[term, 'p_valor'])} & "
            f"{fmt_num(e_horas, 2, sign=True)} h/sem{stars(horas_dv.loc[term, 'p_valor'])} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Figures
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
        ("Branco/\noutros", "Preto/\npardo", raw_gaps["preto_pardo"], axes[2]),
    ]
    for label_a, label_b, (val_a, val_b), ax in panels:
        bars = ax.bar([label_a, label_b], [val_a, val_b], color=[BLUE, ORANGE], width=0.55, zorder=3)
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"R$ {height:,.0f}".replace(",", "."),
                (bar.get_x() + bar.get_width() / 2, height),
                ha="center",
                va="bottom",
                fontsize=9.5,
                color=INK,
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


def fig_coef_forest() -> None:
    # Small multiples: one independent x-scale per (termo, especificação da renda),
    # porque o prêmio de formalidade é ~5-10x maior que os gaps de gênero/raça — um
    # eixo único espremeria mulher/preto_pardo perto de zero.
    col_specs = [
        ("ln_renda_mensal_real_sem_controles", "ln_renda_mensal_real", "Renda mensal real"),
        ("ln_renda_hora_real_sem_controles", "ln_renda_hora_real", "Renda por hora real"),
    ]
    fig, axes = plt.subplots(len(KEY_TERMS), 2, figsize=(10, 5.6))

    for col, (label_sem, label_com, col_title) in enumerate(col_specs):
        sem = load_model(label_sem)
        com = load_model(label_com)
        for row, term in enumerate(KEY_TERMS):
            ax = axes[row, col]
            for y, (model_df, color, model_label) in enumerate(
                [(sem, ORANGE, "Sem controles"), (com, BLUE, "Com controles")]
            ):
                r = model_df.loc[term]
                point = pct_effect(r["coeficiente"])
                low = pct_effect(r["coeficiente"] - 1.96 * r["erro_padrao"])
                high = pct_effect(r["coeficiente"] + 1.96 * r["erro_padrao"])
                ax.errorbar(
                    [point],
                    [y],
                    xerr=[[point - low], [high - point]],
                    fmt="o",
                    color=color,
                    ecolor=color,
                    elinewidth=1.6,
                    capsize=3,
                    markersize=6,
                    label=model_label,
                )
            ax.axvline(0, color=INK_SECONDARY, linewidth=1, linestyle="--", zorder=0)
            ax.set_ylim(-0.7, 1.7)
            ax.set_yticks([0, 1])
            ax.set_yticklabels(["Sem\ncontroles", "Com\ncontroles"], fontsize=8.5)
            ax.spines[["top", "right"]].set_visible(False)
            ax.tick_params(axis="x", labelsize=9)
            if row == 0:
                ax.set_title(col_title, fontsize=11.5)
            if col == 0:
                ax.annotate(
                    KEY_TERM_LABELS_SHORT[term],
                    xy=(-0.32, 0.5),
                    xycoords="axes fraction",
                    rotation=90,
                    va="center",
                    ha="center",
                    fontsize=11,
                    fontweight="bold",
                )
            if row == len(KEY_TERMS) - 1:
                ax.set_xlabel("Efeito percentual aprox. (%)", fontsize=9.5)

    fig.suptitle("Coeficientes-chave: sem controles vs. com controles (IC 95%)", fontsize=12)
    fig.tight_layout(rect=(0.02, 0, 1, 1))
    save_fig(fig, "coef_forest")


def fig_mecanismo() -> None:
    sem_horas = load_model("ln_renda_mensal_real_amostra_jornada")
    com_horas = load_model("ln_renda_mensal_real_com_horas")
    hora = load_model("ln_renda_hora_real_amostra_jornada")
    horas_dv = load_model("horas_semanais")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.6), width_ratios=[2, 1])
    y_positions = np.arange(len(KEY_TERMS))
    bar_height = 0.24
    series = [
        (sem_horas, BLUE, "Mensal, sem horas"),
        (com_horas, ORANGE, "Mensal, com horas"),
        (hora, AQUA, "Por hora"),
    ]
    for i, (model_df, color, series_label) in enumerate(series):
        values = [pct_effect(model_df.loc[t, "coeficiente"]) for t in KEY_TERMS]
        offset = (1 - i) * bar_height
        ax1.barh(y_positions + offset, values, height=bar_height, color=color, label=series_label, zorder=3)
    ax1.axvline(0, color=INK_SECONDARY, linewidth=1, zorder=0)
    ax1.set_yticks(y_positions)
    ax1.set_yticklabels([KEY_TERM_LABELS_SHORT[t] for t in KEY_TERMS])
    ax1.set_xlabel("Efeito percentual aprox. (%)")
    ax1.invert_yaxis()
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.legend(loc="lower right", frameon=False, fontsize=9)
    ax1.set_title("Renda: efeito-preço vs. efeito-jornada", fontsize=11)

    horas_values = [horas_dv.loc[t, "coeficiente"] for t in KEY_TERMS]
    colors = [BLUE if v >= 0 else RED for v in horas_values]
    ax2.barh(y_positions, horas_values, height=0.5, color=colors, zorder=3)
    ax2.axvline(0, color=INK_SECONDARY, linewidth=1, zorder=0)
    ax2.set_yticks(y_positions)
    ax2.set_yticklabels([])
    ax2.tick_params(left=False)
    ax2.invert_yaxis()
    ax2.set_xlabel("Horas/semana")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.set_title("Horas semanais\n(var. dependente)", fontsize=11)
    span = max(abs(v) for v in horas_values) * 1.6
    ax2.set_xlim(-span, span)
    for y, v in zip(y_positions, horas_values):
        ax2.annotate(
            fmt_num(v, 2, sign=True).replace("\\", ""),
            (v, y),
            ha="left" if v >= 0 else "right",
            va="center",
            fontsize=9,
            xytext=(6 if v >= 0 else -6, 0),
            textcoords="offset points",
        )

    fig.suptitle("Decomposição do mecanismo de jornada (mesma amostra nas 4 colunas)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "mecanismo_jornada")


def fig_gap_reais(mean_mensal: float, mean_hora: float) -> None:
    com_mensal = load_model("ln_renda_mensal_real")
    com_hora = load_model("ln_renda_hora_real")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.4))
    y_positions = np.arange(len(KEY_TERMS))

    for ax, model_df, base, title in [
        (ax1, com_mensal, mean_mensal, "R$/mês (na renda média real)"),
        (ax2, com_hora, mean_hora, "R$/hora (na renda média real)"),
    ]:
        values = [(np.exp(model_df.loc[t, "coeficiente"]) - 1) * base for t in KEY_TERMS]
        colors = [BLUE if v >= 0 else RED for v in values]
        ax.barh(y_positions, values, color=colors, height=0.55, zorder=3)
        ax.axvline(0, color=INK_SECONDARY, linewidth=1, zorder=0)
        ax.set_yticks(y_positions)
        ax.set_yticklabels([KEY_TERM_LABELS_SHORT[t] for t in KEY_TERMS])
        ax.invert_yaxis()
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_title(title, fontsize=11)
        span = max(abs(v) for v in values) * 1.35
        ax.set_xlim(-span, span)
        for y, v in zip(y_positions, values):
            ax.annotate(
                f"R$ {v:,.0f}".replace(",", ".").replace("R$ -", "-R$ "),
                (v, y),
                ha="left" if v >= 0 else "right",
                va="center",
                fontsize=9,
                xytext=(5 if v >= 0 else -5, 0),
                textcoords="offset points",
            )

    fig.suptitle("Diferencial ajustado, convertido em R$ (com controles)", fontsize=12)
    fig.tight_layout()
    save_fig(fig, "gap_reais")


# ---------------------------------------------------------------------------
# Macro file
# ---------------------------------------------------------------------------

def main() -> None:
    ensure_project_dirs()

    df = pd.read_parquet(PROCESSED_DIR / "pnadc_rr_analitica.parquet")
    common = df.loc[
        df["formal"].notna() & df["mulher"].notna() & df["preto_pardo"].notna() & df["peso"].notna()
    ].copy()

    hourly = common.loc[common["renda_hora_real"] > 0].copy()
    monthly = common.loc[common["renda_mensal_real"] > 0].copy()
    hours_valid = common.loc[common["horas_semanais_principal"] > 0].copy()

    mean_hora = wavg(hourly["renda_hora_real"], hourly["peso"])
    mean_mensal = wavg(monthly["renda_mensal_real"], monthly["peso"])
    mean_horas = wavg(hours_valid["horas_semanais_principal"], hours_valid["peso"])

    def group_pair(data: pd.DataFrame, col: str) -> tuple:
        g0 = data.loc[data[col] == 0]
        g1 = data.loc[data[col] == 1]
        return wavg(g0["renda_hora_real"], g0["peso"]), wavg(g1["renda_hora_real"], g1["peso"])

    raw_gaps = {term: group_pair(hourly, term) for term in KEY_TERMS}

    audit_totais = pd.read_csv(TABLES_DIR / "auditoria_totais.csv").iloc[0]

    # --- figures ---
    fig_motivacao(raw_gaps)
    fig_coef_forest()
    fig_mecanismo()
    fig_gap_reais(mean_mensal, mean_hora)

    # --- regression tables ---
    tab_mensal = make_regression_table(
        "ln_renda_mensal_real_sem_controles", "ln_renda_mensal_real", "Rendimento mensal real"
    )
    tab_hora = make_regression_table(
        "ln_renda_hora_real_sem_controles", "ln_renda_hora_real", "Rendimento por hora real"
    )
    tab_mecanismo = make_mecanismo_table()

    (PRESENTATION_GERADO_DIR / "tab_mensal.tex").write_text(tab_mensal, encoding="utf-8")
    (PRESENTATION_GERADO_DIR / "tab_hora.tex").write_text(tab_hora, encoding="utf-8")
    (PRESENTATION_GERADO_DIR / "tab_mecanismo.tex").write_text(tab_mecanismo, encoding="utf-8")
    print(f"saved: {PRESENTATION_GERADO_DIR / 'tab_mensal.tex'}")
    print(f"saved: {PRESENTATION_GERADO_DIR / 'tab_hora.tex'}")
    print(f"saved: {PRESENTATION_GERADO_DIR / 'tab_mecanismo.tex'}")

    # --- narrative macros ---
    com_mensal = load_model("ln_renda_mensal_real")
    com_hora = load_model("ln_renda_hora_real")
    stats_mensal = load_stats("ln_renda_mensal_real")
    stats_hora = load_stats("ln_renda_hora_real")
    sem_horas_j = load_model("ln_renda_mensal_real_amostra_jornada")
    com_horas_j = load_model("ln_renda_mensal_real_com_horas")
    hora_j = load_model("ln_renda_hora_real_amostra_jornada")
    horas_dv = load_model("horas_semanais")
    stats_jornada = load_stats("horas_semanais")

    macros = {}
    macros["NTotal"] = fmt_int(audit_totais["n_total"])
    macros["NQuatorzeMais"] = fmt_int(audit_totais["n_14_mais"])
    macros["NOcupados"] = fmt_int(audit_totais["n_ocupados"])
    macros["NRendaValida"] = fmt_int(audit_totais["n_ocupados_renda_valida"])
    macros["NMensal"] = fmt_int(stats_mensal["nobs"])
    macros["NHora"] = fmt_int(stats_hora["nobs"])
    macros["NJornada"] = fmt_int(stats_jornada["nobs"])
    macros["RdoisMensal"] = fmt_num(stats_mensal["rsquared"], 3)
    macros["RdoisHora"] = fmt_num(stats_hora["rsquared"], 3)

    macros["MediaMensal"] = fmt_brl(mean_mensal)
    macros["MediaHora"] = fmt_brl(mean_hora, 2)
    macros["MediaHoras"] = fmt_num(mean_horas, 1)

    for term, key in [("formal", "Formal"), ("mulher", "Mulher"), ("preto_pardo", "PretoPardo")]:
        row_mensal = com_mensal.loc[term]
        row_hora = com_hora.loc[term]
        pct_mensal = pct_effect(row_mensal["coeficiente"])
        pct_hora = pct_effect(row_hora["coeficiente"])
        macros[f"Pct{key}Mensal"] = fmt_pct(pct_mensal)
        macros[f"Pct{key}Hora"] = fmt_pct(pct_hora)
        macros[f"Reais{key}Mensal"] = fmt_brl(pct_mensal / 100 * mean_mensal)
        macros[f"Reais{key}Hora"] = fmt_brl(pct_hora / 100 * mean_hora, 2)

        row_sem_j = sem_horas_j.loc[term]
        row_com_j = com_horas_j.loc[term]
        row_hora_j = hora_j.loc[term]
        row_horas_dv = horas_dv.loc[term]
        macros[f"Pct{key}MensalSemHorasJornada"] = fmt_pct(pct_effect(row_sem_j["coeficiente"]))
        macros[f"Pct{key}MensalComHorasJornada"] = fmt_pct(pct_effect(row_com_j["coeficiente"]))
        macros[f"Pct{key}HoraJornada"] = fmt_pct(pct_effect(row_hora_j["coeficiente"]))
        macros[f"Horas{key}"] = fmt_num(row_horas_dv["coeficiente"], 2, sign=True)

        g0, g1 = raw_gaps[term]
        macros[f"Bruto{key}GrupoRef"] = fmt_brl(g0, 2)
        macros[f"Bruto{key}GrupoComp"] = fmt_brl(g1, 2)
        macros[f"BrutoGap{key}Pct"] = fmt_pct((g1 / g0 - 1) * 100)

    for term, key in [("formal:mulher", "FormalMulher"), ("formal:preto_pardo", "FormalPretoPardo")]:
        row_mensal = com_mensal.loc[term]
        row_hora = com_hora.loc[term]
        macros[f"Pct{key}Mensal"] = fmt_pct(pct_effect(row_mensal["coeficiente"]))
        macros[f"Pct{key}Hora"] = fmt_pct(pct_effect(row_hora["coeficiente"]))
        macros[f"PValor{key}Mensal"] = fmt_num(row_mensal["p_valor"], 3)
        macros[f"PValor{key}Hora"] = fmt_num(row_hora["p_valor"], 3)

    lines = ["% Gerado automaticamente por scripts/08_make_presentation_assets.py. Não editar à mão.", ""]
    for name, value in macros.items():
        lines.append(f"\\newcommand{{\\{name}}}{{{value}\\xspace}}")
    output = PRESENTATION_GERADO_DIR / "numeros.tex"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved: {output} ({len(macros)} macros)")


if __name__ == "__main__":
    main()
