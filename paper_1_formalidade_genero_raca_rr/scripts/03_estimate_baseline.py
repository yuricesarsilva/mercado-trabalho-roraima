from pathlib import Path
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.labels import coefficient_label, reference_label
from pnadc_rr.paths import MODELS_DIR, PROCESSED_DIR, TABLES_DIR, ensure_project_dirs


def estimate(df: pd.DataFrame, dependent: str, label: str) -> None:
    formula = (
        f"{dependent} ~ formal + mulher + preto_pardo "
        "+ formal:mulher + formal:preto_pardo "
        "+ idade + idade2 + C(escolaridade) "
        "+ C(ocupacao_grupo) + C(atividade_grupo) + C(periodo)"
    )

    model = smf.wls(formula=formula, data=df, weights=df["peso"]).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["upa"]},
    )

    txt_output = MODELS_DIR / f"modelo_base_{label}.txt"
    txt_output.write_text(model.summary().as_text(), encoding="utf-8")

    coef = model.params.rename("coeficiente").to_frame()
    coef.insert(0, "rotulo", [coefficient_label(term) for term in coef.index])
    coef.insert(1, "referencia", [reference_label(term) for term in coef.index])
    coef["erro_padrao"] = model.bse
    coef["p_valor"] = model.pvalues
    coef["efeito_percentual_aprox"] = (np.exp(coef["coeficiente"]) - 1) * 100
    coef.to_csv(TABLES_DIR / f"modelo_base_{label}.csv", encoding="utf-8")
    print(f"saved: {txt_output}")


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

    hourly = common.loc[common["renda_hora"] > 0].copy()
    hourly["ln_renda_hora"] = np.log(hourly["renda_hora"])
    estimate(hourly, "ln_renda_hora", "ln_renda_hora")

    monthly = common.loc[common["renda_mensal"] > 0].copy()
    monthly["ln_renda_mensal"] = np.log(monthly["renda_mensal"])
    estimate(monthly, "ln_renda_mensal", "ln_renda_mensal")


if __name__ == "__main__":
    main()
