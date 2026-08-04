import argparse
from pathlib import Path

import requests

from pnadc_rr.config import DEFAULT_QUARTERS, DEFAULT_YEARS, IBGE_PNADC_MICRODATA_BASE_URL
from pnadc_rr.paths import RAW_DIR, ensure_project_dirs


def parse_ints(values: list[str] | None, default: list[int]) -> list[int]:
    if not values:
        return default
    return [int(value) for value in values]


def pnadc_zip_url(year: int, quarter: int) -> str:
    filename = f"PNADC_0{quarter}{year}.zip"
    return f"{IBGE_PNADC_MICRODATA_BASE_URL}/{year}/{filename}"


def download_file(url: str, destination: Path, overwrite: bool = False) -> None:
    if destination.exists() and not overwrite:
        print(f"exists: {destination}")
        return

    print(f"downloading: {url}")
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with destination.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)
    print(f"saved: {destination}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download PNAD-C quarterly microdata from IBGE.")
    parser.add_argument("--years", nargs="*", help="Years to download, e.g. 2024 2025.")
    parser.add_argument("--quarters", nargs="*", help="Quarters to download, e.g. 1 2 3 4.")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    years = parse_ints(args.years, DEFAULT_YEARS)
    quarters = parse_ints(args.quarters, DEFAULT_QUARTERS)

    ensure_project_dirs()
    for year in years:
        year_dir = RAW_DIR / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)
        for quarter in quarters:
            url = pnadc_zip_url(year, quarter)
            destination = year_dir / f"PNADC_0{quarter}{year}.zip"
            download_file(url, destination, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
