import zipfile
from pathlib import Path

import pandas as pd
import requests

from .config import RR_UF_CODE
from .paths import RAW_DIR


DEFLATOR_URL = (
    "https://ftp.ibge.gov.br/Trabalho_e_Rendimento/"
    "Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/"
    "Trimestral/Microdados/Documentacao/Deflatores.zip"
)

DEFLATOR_DIR = RAW_DIR / "documentacao"

# The official deflator table indexes quarters as "MM-MM-MM" month ranges.
# These four values are the ones that coincide with the fixed calendar
# quarters (Trimestre 1-4) used by the quarterly PNAD-C microdata.
TRIMESTRE_TO_TRIM = {
    1: "01-02-03",
    2: "04-05-06",
    3: "07-08-09",
    4: "10-11-12",
}


def download_deflator(overwrite: bool = False) -> Path:
    DEFLATOR_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DEFLATOR_DIR / "Deflatores.zip"
    if not zip_path.exists() or overwrite:
        response = requests.get(DEFLATOR_URL, timeout=120)
        response.raise_for_status()
        zip_path.write_bytes(response.content)

    with zipfile.ZipFile(zip_path) as archive:
        xls_members = [name for name in archive.namelist() if name.lower().endswith(".xls")]
        if not xls_members:
            raise FileNotFoundError(f"No xls deflator file inside {zip_path}")
        member = xls_members[0]
        archive.extract(member, DEFLATOR_DIR)
        return DEFLATOR_DIR / member


def find_deflator_xls() -> Path:
    candidates = sorted(DEFLATOR_DIR.glob("deflator_*.xls"))
    if not candidates:
        raise FileNotFoundError(
            f"Missing deflator file in {DEFLATOR_DIR}. Run scripts/00_download_pnadc.py first."
        )
    return candidates[-1]


def load_deflator(uf: int = RR_UF_CODE) -> pd.DataFrame:
    xls_path = find_deflator_xls()
    raw = pd.read_excel(xls_path, sheet_name="deflator")
    raw = raw.loc[raw["UF"] == uf].copy()

    trim_to_quarter = {value: key for key, value in TRIMESTRE_TO_TRIM.items()}
    raw["Trimestre"] = raw["trim"].map(trim_to_quarter)
    raw = raw.dropna(subset=["Trimestre"]).copy()
    raw["Trimestre"] = raw["Trimestre"].astype(int)
    raw["Ano"] = raw["Ano"].astype(int)

    return raw.rename(
        columns={"Habitual": "deflator_habitual", "Efetivo": "deflator_efetivo"}
    )[["Ano", "Trimestre", "deflator_habitual", "deflator_efetivo"]]
