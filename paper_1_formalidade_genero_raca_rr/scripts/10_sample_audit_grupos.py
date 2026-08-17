"""Tabela de N (não ponderado, ponderado, nº de UPAs) por grupo -- item 5 da revisão
econométrica (`docs/plano_reforma_econometrica.md`, Bloco A4).

Cruza formal x sexo x raca_grupo x setor_publico (e a amostra restrita `empregado_restrito`),
para: (i) decidir se `mulher x raca_grupo` é estimável, (ii) informar a regra de agregação de
células esparsas em `ocupação x atividade` para o Bloco B, (iii) preencher a tabela de N que falta
no paper.
"""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.paths import PROCESSED_DIR, TABLES_DIR, ensure_project_dirs


def count_table(df: pd.DataFrame, columns: list[str], name: str) -> pd.DataFrame:
    grouped = df.groupby(columns, dropna=False)
    table = grouped.size().reset_index(name="n_amostral")
    table["n_ponderado"] = grouped["peso"].sum().to_numpy().round(0).astype(int)
    table["n_upa"] = grouped["upa"].nunique().to_numpy()
    table = table.sort_values("n_amostral", ascending=False)
    table.insert(0, "tabela", name)
    return table


def main() -> None:
    ensure_project_dirs()
    input_path = PROCESSED_DIR / "pnadc_rr_analitica.parquet"
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    df = pd.read_parquet(input_path)
    common = df.loc[
        df["formal"].notna() & df["mulher"].notna() & df["peso"].notna() & df["upa"].notna()
    ].copy()
    com_raca = common.loc[common["raca_grupo"].notna()].copy()
    restrita = common.loc[common["empregado_restrito"] == 1].copy()
    restrita_raca = com_raca.loc[com_raca["empregado_restrito"] == 1].copy()

    tables = [
        count_table(common, ["formal"], "formalidade_ampla"),
        count_table(common, ["formal", "mulher"], "formalidade_genero_ampla"),
        count_table(com_raca, ["formal", "raca_grupo"], "formalidade_raca_ampla"),
        count_table(com_raca, ["formal", "mulher", "raca_grupo"], "formalidade_genero_raca_ampla"),
        count_table(com_raca, ["mulher", "raca_grupo"], "genero_raca_ampla"),
        count_table(common, ["formal", "setor_publico"], "formalidade_setor_publico"),
        count_table(common, ["setor_publico"], "setor_publico"),
        count_table(common, ["posicao_ocupacao_grupo"], "posicao_ocupacao"),
        count_table(restrita, ["formal"], "formalidade_restrita"),
        count_table(restrita, ["formal", "mulher"], "formalidade_genero_restrita"),
        count_table(restrita_raca, ["formal", "raca_grupo"], "formalidade_raca_restrita"),
        count_table(
            restrita_raca, ["formal", "mulher", "raca_grupo"], "formalidade_genero_raca_restrita"
        ),
    ]

    for table in tables:
        name = str(table["tabela"].iloc[0])
        output = TABLES_DIR / f"auditoria_grupos_{name}.csv"
        table.to_csv(output, index=False, encoding="utf-8")
        print(f"saved: {output}")


if __name__ == "__main__":
    main()
