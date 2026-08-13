from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.estimation import MINIMAL_FORMULA_RHS, estimate
from pnadc_rr.paths import PROCESSED_DIR, ensure_project_dirs


def main() -> None:
    ensure_project_dirs()
    input_path = PROCESSED_DIR / "pnadc_rr_analitica.parquet"
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    df = pd.read_parquet(input_path)
    common = df.loc[
        df["formal"].notna()
        & df["mulher"].notna()
        & df["preto_pardo"].notna()
        & df["peso"].notna()
        & df["upa"].notna()
    ].copy()

    # Robustez: mesma amostra e mesma variável dependente do modelo-base, mas sem
    # nenhum controle além dos próprios tratamentos (formal, mulher, preto_pardo)
    # e suas interações. Serve para mostrar o quanto os coeficientes de interesse
    # mudam quando passamos a controlar por composição (ocupação, atividade,
    # escolaridade, idade, período).
    hourly_real = common.loc[common["renda_hora_real"] > 0].copy()
    hourly_real["ln_renda_hora_real"] = np.log(hourly_real["renda_hora_real"])
    estimate(
        hourly_real,
        "ln_renda_hora_real",
        "ln_renda_hora_real_sem_controles",
        "Robustez: log do rendimento por hora (real), sem controles",
        rhs=MINIMAL_FORMULA_RHS,
    )

    monthly_real = common.loc[common["renda_mensal_real"] > 0].copy()
    monthly_real["ln_renda_mensal_real"] = np.log(monthly_real["renda_mensal_real"])
    estimate(
        monthly_real,
        "ln_renda_mensal_real",
        "ln_renda_mensal_real_sem_controles",
        "Robustez: log do rendimento mensal (real), sem controles",
        rhs=MINIMAL_FORMULA_RHS,
    )


if __name__ == "__main__":
    main()
