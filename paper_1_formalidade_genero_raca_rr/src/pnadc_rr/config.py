IBGE_PNADC_MICRODATA_BASE_URL = (
    "https://ftp.ibge.gov.br/Trabalho_e_Rendimento/"
    "Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/"
    "Trimestral/Microdados"
)

RR_UF_CODE = 14

DEFAULT_YEARS = list(range(2016, 2026))
DEFAULT_QUARTERS = [1, 2, 3, 4]

CORE_COLUMNS = [
    "Ano",
    "Trimestre",
    "UF",
    "UPA",
    "Estrato",
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
]
