from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.paths import INTERIM_DIR, PROCESSED_DIR, TABLES_DIR, ensure_project_dirs


def count_table(df: pd.DataFrame, columns: list[str], name: str) -> pd.DataFrame:
    grouped = df.groupby(columns, dropna=False)
    table = grouped.size().reset_index(name="n_amostral")
    if "UPA" in df.columns:
        table["n_upa"] = grouped["UPA"].nunique().to_numpy()
    elif "upa" in df.columns:
        table["n_upa"] = grouped["upa"].nunique().to_numpy()
    table = table.sort_values("n_amostral", ascending=False)
    table.insert(0, "tabela", name)
    return table


def main() -> None:
    ensure_project_dirs()
    raw_rr_path = INTERIM_DIR / "pnadc_rr_microdata.parquet"
    analytic_path = PROCESSED_DIR / "pnadc_rr_analitica.parquet"
    if not raw_rr_path.exists():
        raise SystemExit(f"Missing input file: {raw_rr_path}")

    raw_rr = pd.read_parquet(raw_rr_path)
    if analytic_path.exists():
        occupied = pd.read_parquet(analytic_path)
    else:
        occupied = raw_rr.loc[raw_rr["VD4002"] == 1].copy()

    tables = [
        pd.DataFrame(
            {
                "tabela": ["totais"],
                "n_total": [len(raw_rr)],
                "n_14_mais": [(raw_rr["V2009"] >= 14).sum()],
                "n_ocupados": [len(occupied)],
                "n_ocupados_renda_valida": [(occupied["VD4016"] > 0).sum()],
            }
        ),
        count_table(occupied, ["VD4009"], "posicao_ocupacao"),
        count_table(occupied, ["V2007"], "sexo"),
        count_table(occupied, ["V2010"], "raca_cor"),
        count_table(occupied, ["VD4010"], "atividade"),
        count_table(occupied, ["VD4011"], "ocupacao"),
        count_table(occupied, ["VD4010", "VD4011"], "atividade_ocupacao"),
        count_table(occupied, ["VD4009", "V2007", "V2010"], "posicao_sexo_raca"),
    ]

    if {"formal", "mulher", "preto_pardo"}.issubset(occupied.columns):
        tables.extend(
            [
                count_table(occupied, ["formal"], "formalidade"),
                count_table(occupied, ["formal", "mulher"], "formalidade_genero"),
                count_table(occupied, ["formal", "preto_pardo"], "formalidade_raca"),
                count_table(occupied, ["formal", "mulher", "preto_pardo"], "formalidade_genero_raca"),
                count_table(occupied, ["atividade_grupo", "formal"], "atividade_formalidade"),
                count_table(occupied, ["ocupacao_grupo", "formal"], "ocupacao_formalidade"),
            ]
        )

    for table in tables:
        name = str(table["tabela"].iloc[0])
        output = TABLES_DIR / f"auditoria_{name}.csv"
        table.to_csv(output, index=False, encoding="utf-8")
        print(f"saved: {output}")


if __name__ == "__main__":
    main()
