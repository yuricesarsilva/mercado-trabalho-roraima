import pandas as pd

from pnadc_rr.paths import INTERIM_DIR, TABLES_DIR, ensure_project_dirs


def count_table(df: pd.DataFrame, columns: list[str], name: str) -> pd.DataFrame:
    table = (
        df.groupby(columns, dropna=False)
        .size()
        .reset_index(name="n_amostral")
        .sort_values("n_amostral", ascending=False)
    )
    table.insert(0, "tabela", name)
    return table


def main() -> None:
    ensure_project_dirs()
    input_path = INTERIM_DIR / "pnadc_rr_microdata.parquet"
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    df = pd.read_parquet(input_path)
    occupied = df.loc[df["VD4002"] == 1].copy()

    tables = [
        pd.DataFrame(
            {
                "tabela": ["totais"],
                "n_total": [len(df)],
                "n_14_mais": [(df["V2009"] >= 14).sum()],
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

    output = TABLES_DIR / "auditoria_amostral_rr.xlsx"
    with pd.ExcelWriter(output) as writer:
        for table in tables:
            sheet = str(table["tabela"].iloc[0])[:31]
            table.to_excel(writer, sheet_name=sheet, index=False)
    print(f"saved: {output}")


if __name__ == "__main__":
    main()
