from pathlib import Path

from pnadc_rr.paths import TABLES_DIR


def main() -> None:
    files = sorted(TABLES_DIR.glob("*"))
    print("Generated tables:")
    for file in files:
        print(f"- {file.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
