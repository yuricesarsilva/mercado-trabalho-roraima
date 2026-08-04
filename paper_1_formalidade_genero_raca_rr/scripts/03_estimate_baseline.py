import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from pnadc_rr.paths import MODELS_DIR, PROCESSED_DIR, TABLES_DIR, ensure_project_dirs


def main() -> None:
    ensure_project_dirs()
    input_path = PROCESSED_DIR / "pnadc_rr_analitica.parquet"
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    df = pd.read_parquet(input_path)
    df = df.loc[df["renda_hora"] > 0].copy()
    df["ln_renda_hora"] = np.log(df["renda_hora"])

    formula = (
        "ln_renda_hora ~ formal + mulher + preto_pardo "
        "+ formal:mulher + formal:preto_pardo "
        "+ idade + idade2 + C(escolaridade) "
        "+ C(ocupacao_grupo) + C(atividade_grupo) + C(periodo)"
    )

    model = smf.wls(formula=formula, data=df, weights=df["peso"]).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["upa"]},
    )

    txt_output = MODELS_DIR / "modelo_base_ln_renda_hora.txt"
    txt_output.write_text(model.summary().as_text(), encoding="utf-8")

    coef = model.params.rename("coeficiente").to_frame()
    coef["erro_padrao"] = model.bse
    coef["p_valor"] = model.pvalues
    coef.to_csv(TABLES_DIR / "modelo_base_ln_renda_hora.csv", encoding="utf-8")
    print(f"saved: {txt_output}")


if __name__ == "__main__":
    main()
