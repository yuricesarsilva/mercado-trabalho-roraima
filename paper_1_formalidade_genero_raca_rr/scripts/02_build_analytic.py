from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.paths import INTERIM_DIR, PROCESSED_DIR, ensure_project_dirs


FORMAL_VD4009 = {1, 3, 5, 7}
INFORMAL_VD4009 = {2, 4, 6, 10}
EMPLOYER_SELF_EMPLOYED = {8, 9}


def build_formality(df: pd.DataFrame) -> pd.Series:
    formal = pd.Series(np.nan, index=df.index, dtype="float")
    formal[df["VD4009"].isin(FORMAL_VD4009)] = 1
    formal[df["VD4009"].isin(INFORMAL_VD4009)] = 0

    cnpj_known = df["VD4009"].isin(EMPLOYER_SELF_EMPLOYED) & df["V4019"].notna()
    formal[cnpj_known & (df["V4019"] == 1)] = 1
    formal[cnpj_known & (df["V4019"] == 2)] = 0
    return formal


def main() -> None:
    ensure_project_dirs()
    input_path = INTERIM_DIR / "pnadc_rr_microdata.parquet"
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    df = pd.read_parquet(input_path)
    occupied = df.loc[(df["V2009"] >= 14) & (df["VD4002"] == 1)].copy()
    occupied["V2007"] = pd.to_numeric(occupied["V2007"], errors="coerce")
    occupied["V2010"] = pd.to_numeric(occupied["V2010"], errors="coerce")

    occupied["formal"] = build_formality(occupied)
    occupied["mulher"] = (occupied["V2007"] == 2).astype(int)
    occupied["preto_pardo"] = occupied["V2010"].isin([2, 4]).astype(int)
    occupied["idade"] = occupied["V2009"]
    occupied["idade2"] = occupied["idade"] ** 2
    occupied["peso"] = occupied["V1028"]
    occupied["upa"] = occupied["UPA"].astype(str)
    occupied["estrato"] = occupied["Estrato"].astype(str)
    occupied["periodo"] = occupied["Ano"].astype("Int64").astype(str) + "T" + occupied["Trimestre"].astype("Int64").astype(str)
    occupied["escolaridade"] = occupied["VD3004"].astype("Int64").astype(str)
    occupied["atividade_grupo"] = occupied["VD4010"].astype("Int64").astype(str)
    occupied["ocupacao_grupo"] = occupied["VD4011"].astype("Int64").astype(str)
    occupied["horas_semanais_principal"] = occupied["V4039"]
    occupied["renda_mensal"] = occupied["VD4016"]
    occupied["renda_hora"] = occupied["renda_mensal"] / (occupied["horas_semanais_principal"] * 4.33)
    occupied.loc[occupied["renda_hora"] <= 0, "renda_hora"] = np.nan
    occupied["ln_renda_mensal"] = np.log(occupied["renda_mensal"].where(occupied["renda_mensal"] > 0))
    occupied["ln_renda_hora"] = np.log(occupied["renda_hora"])

    output = PROCESSED_DIR / "pnadc_rr_analitica.parquet"
    occupied.to_parquet(output, index=False)
    print(f"saved: {output}")
    print(f"rows: {len(occupied)}")
    print(f"rows with valid formality: {occupied['formal'].notna().sum()}")
    print(f"rows with valid hourly income: {occupied['renda_hora'].notna().sum()}")


if __name__ == "__main__":
    main()
