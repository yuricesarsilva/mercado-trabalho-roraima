import argparse
from pathlib import Path

import pandas as pd

from pnadc_rr.config import CORE_COLUMNS, DEFAULT_QUARTERS, DEFAULT_YEARS, RR_UF_CODE
from pnadc_rr.paths import INTERIM_DIR, RAW_DIR, ensure_project_dirs


def parse_ints(values: list[str] | None, default: list[int]) -> list[int]:
    if not values:
        return default
    return [int(value) for value in values]


def load_quarter_placeholder(zip_path: Path) -> pd.DataFrame:
    raise NotImplementedError(
        "Extraction depends on the official fixed-width layout for the selected year. "
        "Add the IBGE layout parser before running this step."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Roraima-only PNAD-C microdata.")
    parser.add_argument("--years", nargs="*", help="Years to process.")
    parser.add_argument("--quarters", nargs="*", help="Quarters to process.")
    args = parser.parse_args()

    years = parse_ints(args.years, DEFAULT_YEARS)
    quarters = parse_ints(args.quarters, DEFAULT_QUARTERS)

    ensure_project_dirs()
    frames: list[pd.DataFrame] = []
    for year in years:
        for quarter in quarters:
            zip_path = RAW_DIR / str(year) / f"PNADC_0{quarter}{year}.zip"
            if not zip_path.exists():
                print(f"missing: {zip_path}")
                continue
            df = load_quarter_placeholder(zip_path)
            rr = df.loc[df["UF"].astype(int) == RR_UF_CODE, CORE_COLUMNS].copy()
            frames.append(rr)

    if not frames:
        raise SystemExit("No quarterly files were processed.")

    output = INTERIM_DIR / "pnadc_rr_microdata.parquet"
    pd.concat(frames, ignore_index=True).to_parquet(output, index=False)
    print(f"saved: {output}")


if __name__ == "__main__":
    main()
