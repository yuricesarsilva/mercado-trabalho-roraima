from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_DIR / "outputs"
TABLES_DIR = OUTPUTS_DIR / "tables"
FIGURES_DIR = OUTPUTS_DIR / "figures"
MODELS_DIR = OUTPUTS_DIR / "models"
PRESENTATION_DIR = PROJECT_DIR / "presentation"
PRESENTATION_GERADO_DIR = PRESENTATION_DIR / "gerado"
PAPER_DIR = PROJECT_DIR / "paper"
PAPER_FIGURES_DIR = PAPER_DIR / "figures"


def ensure_project_dirs() -> None:
    for path in [
        RAW_DIR,
        INTERIM_DIR,
        PROCESSED_DIR,
        TABLES_DIR,
        FIGURES_DIR,
        MODELS_DIR,
        PRESENTATION_GERADO_DIR,
        PAPER_FIGURES_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
