import argparse
import re
import zipfile
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pnadc_rr.config import CORE_COLUMNS, DEFAULT_QUARTERS, DEFAULT_YEARS, RR_UF_CODE
from pnadc_rr.paths import INTERIM_DIR, RAW_DIR, ensure_project_dirs


LAYOUT_FILE = RAW_DIR / "input_PNADC_trimestral.txt"
NUMERIC_COLUMNS = {
    "Ano",
    "Trimestre",
    "UF",
    "V1028",
    "V2007",
    "V2009",
    "V2010",
    "V4019",
    "V4029",
    "V4032",
    "V4039",
    "VD3004",
    "VD4002",
    "VD4009",
    "VD4010",
    "VD4011",
    "VD4012",
    "VD4016",
    "VD4019",
    "VD4035",
}


def parse_ints(values: list[str] | None, default: list[int]) -> list[int]:
    if not values:
        return default
    return [int(value) for value in values]


def parse_sas_layout(layout_path: Path, columns: list[str]) -> tuple[list[tuple[int, int]], list[str]]:
    if not layout_path.exists():
        raise FileNotFoundError(
            f"Missing layout file: {layout_path}. "
            "Download and extract Dicionario_e_input_20221031.zip first."
        )

    desired = set(columns)
    colspecs: list[tuple[int, int]] = []
    names: list[str] = []
    pattern = re.compile(r"@(\d+)\s+([A-Za-z0-9_]+)\s+\$?(\d+)\.")

    for line in layout_path.read_text(encoding="latin-1").splitlines():
        match = pattern.search(line)
        if not match:
            continue
        start = int(match.group(1)) - 1
        name = match.group(2)
        width = int(match.group(3))
        if name in desired:
            colspecs.append((start, start + width))
            names.append(name)

    missing = sorted(desired.difference(names))
    if missing:
        raise ValueError(f"Variables not found in layout: {missing}")

    return colspecs, names


def find_quarter_zip(year: int, quarter: int) -> Path | None:
    candidates = sorted((RAW_DIR / str(year)).glob(f"PNADC_0{quarter}{year}*.zip"))
    return candidates[-1] if candidates else None


def load_quarter(zip_path: Path, colspecs: list[tuple[int, int]], names: list[str]) -> pd.DataFrame:
    chunks: list[pd.DataFrame] = []
    with zipfile.ZipFile(zip_path) as archive:
        txt_members = [name for name in archive.namelist() if name.lower().endswith(".txt")]
        if not txt_members:
            raise FileNotFoundError(f"No txt microdata file inside {zip_path}")
        with archive.open(txt_members[0]) as file:
            reader = pd.read_fwf(
                file,
                colspecs=colspecs,
                names=names,
                dtype=str,
                chunksize=100_000,
            )
            for chunk in reader:
                rr = chunk.loc[chunk["UF"].str.strip() == str(RR_UF_CODE)].copy()
                if not rr.empty:
                    chunks.append(rr)

    if not chunks:
        return pd.DataFrame(columns=names)

    df = pd.concat(chunks, ignore_index=True)
    for column in NUMERIC_COLUMNS.intersection(df.columns):
        df[column] = pd.to_numeric(df[column].str.strip(), errors="coerce")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Roraima-only PNAD-C microdata.")
    parser.add_argument("--years", nargs="*", help="Years to process.")
    parser.add_argument("--quarters", nargs="*", help="Quarters to process.")
    args = parser.parse_args()

    years = parse_ints(args.years, DEFAULT_YEARS)
    quarters = parse_ints(args.quarters, DEFAULT_QUARTERS)

    ensure_project_dirs()
    colspecs, names = parse_sas_layout(LAYOUT_FILE, CORE_COLUMNS)
    frames: list[pd.DataFrame] = []
    for year in years:
        for quarter in quarters:
            zip_path = find_quarter_zip(year, quarter)
            if zip_path is None:
                print(f"missing: {RAW_DIR / str(year) / f'PNADC_0{quarter}{year}*.zip'}")
                continue
            print(f"processing: {zip_path}")
            rr = load_quarter(zip_path, colspecs, names)
            rr = rr.loc[:, CORE_COLUMNS].copy()
            frames.append(rr)

    if not frames:
        raise SystemExit("No quarterly files were processed.")

    output = INTERIM_DIR / "pnadc_rr_microdata.parquet"
    pd.concat(frames, ignore_index=True).to_parquet(output, index=False)
    print(f"saved: {output}")


if __name__ == "__main__":
    main()
