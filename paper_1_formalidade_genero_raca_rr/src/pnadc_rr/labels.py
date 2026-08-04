from __future__ import annotations

import re


BASE_LABELS = {
    "Intercept": "Constante",
    "formal": "Trabalhador formal",
    "mulher": "Mulher",
    "preto_pardo": "Pessoa preta ou parda",
    "formal:mulher": "Trabalhador formal x mulher",
    "formal:preto_pardo": "Trabalhador formal x pessoa preta ou parda",
    "idade": "Idade",
    "idade2": "Idade ao quadrado",
}

BASE_SHORT_LABELS = {
    "Intercept": "const",
    "formal": "formal",
    "mulher": "mulher",
    "preto_pardo": "preto_pardo",
    "formal:mulher": "formal_mulher",
    "formal:preto_pardo": "formal_preto_pardo",
    "idade": "idade",
    "idade2": "idade2",
}

ESCOLARIDADE_LABELS = {
    "1": "Sem instrução ou fundamental incompleto",
    "2": "Fundamental incompleto ou equivalente",
    "3": "Fundamental completo ou equivalente",
    "4": "Médio incompleto ou equivalente",
    "5": "Médio completo ou equivalente",
    "6": "Superior incompleto ou equivalente",
    "7": "Superior completo",
}

ESCOLARIDADE_SHORT_LABELS = {
    "1": "esc_sem_fund_inc",
    "2": "esc_fund_inc",
    "3": "esc_fund_comp",
    "4": "esc_med_inc",
    "5": "esc_med_comp",
    "6": "esc_sup_inc",
    "7": "esc_sup_comp",
}

OCUPACAO_LABELS = {
    "1": "Dirigentes e gerentes",
    "2": "Profissionais das ciências e intelectuais",
    "3": "Técnicos e profissionais de nível médio",
    "4": "Trabalhadores de apoio administrativo",
    "5": "Trabalhadores dos serviços e vendedores",
    "6": "Trabalhadores agropecuários, florestais, da caça e pesca",
    "7": "Trabalhadores qualificados da indústria, construção e artes",
    "8": "Operadores de instalações, máquinas e montadores",
    "9": "Ocupações elementares",
    "10": "Membros das forças armadas, policiais e bombeiros militares",
    "11": "Ocupações mal definidas",
}

OCUPACAO_SHORT_LABELS = {
    "1": "ocup_dir_ger",
    "2": "ocup_prof_cien",
    "3": "ocup_tec_med",
    "4": "ocup_apoio_adm",
    "5": "ocup_serv_vend",
    "6": "ocup_agro",
    "7": "ocup_ind_constr",
    "8": "ocup_oper_maq",
    "9": "ocup_elementar",
    "10": "ocup_forcas",
    "11": "ocup_mal_def",
}

ATIVIDADE_LABELS = {
    "1": "Agropecuária",
    "2": "Indústria geral",
    "3": "Construção",
    "4": "Comércio e reparação",
    "5": "Transporte, armazenagem e correio",
    "6": "Alojamento e alimentação",
    "7": "Informação, comunicação, financeiro, imobiliário, profissional e administrativo",
    "8": "Administração pública, defesa e seguridade social",
    "9": "Educação, saúde humana e serviços sociais",
    "10": "Outros serviços",
    "11": "Serviços domésticos",
    "12": "Atividades mal definidas",
}

ATIVIDADE_SHORT_LABELS = {
    "1": "ativ_agro",
    "2": "ativ_ind",
    "3": "ativ_constr",
    "4": "ativ_comercio",
    "5": "ativ_transp",
    "6": "ativ_aloj_alim",
    "7": "ativ_info_fin",
    "8": "ativ_pub_def",
    "9": "ativ_educ_saude",
    "10": "ativ_out_serv",
    "11": "ativ_dom",
    "12": "ativ_mal_def",
}


def _clean_category(value: str) -> str:
    if value.endswith(".0"):
        return value[:-2]
    return value


def coefficient_label(term: str) -> str:
    if term in BASE_LABELS:
        return BASE_LABELS[term]

    categorical = re.fullmatch(r"C\(([^)]+)\)\[T\.(.+)\]", term)
    if not categorical:
        return term

    variable, value = categorical.groups()
    value = _clean_category(value)

    if variable == "escolaridade":
        return f"Escolaridade: {ESCOLARIDADE_LABELS.get(value, value)}"
    if variable == "ocupacao_grupo":
        return f"Ocupação: {OCUPACAO_LABELS.get(value, value)}"
    if variable == "atividade_grupo":
        return f"Atividade: {ATIVIDADE_LABELS.get(value, value)}"
    if variable == "periodo":
        return f"Período: {value}"
    return f"{variable}: {value}"


def coefficient_short_label(term: str) -> str:
    if term in BASE_SHORT_LABELS:
        return BASE_SHORT_LABELS[term]

    categorical = re.fullmatch(r"C\(([^)]+)\)\[T\.(.+)\]", term)
    if not categorical:
        return term

    variable, value = categorical.groups()
    value = _clean_category(value)

    if variable == "escolaridade":
        return ESCOLARIDADE_SHORT_LABELS.get(value, f"esc_{value}")
    if variable == "ocupacao_grupo":
        return OCUPACAO_SHORT_LABELS.get(value, f"ocup_{value}")
    if variable == "atividade_grupo":
        return ATIVIDADE_SHORT_LABELS.get(value, f"ativ_{value}")
    if variable == "periodo":
        return f"ano{value}"
    return f"{variable}_{value}"


def reference_label(term: str) -> str:
    if term.startswith("C(escolaridade)"):
        return f"Referência: {ESCOLARIDADE_LABELS['1']}"
    if term.startswith("C(ocupacao_grupo)"):
        return f"Referência: {OCUPACAO_LABELS['1']}"
    if term.startswith("C(atividade_grupo)"):
        return f"Referência: {ATIVIDADE_LABELS['1']}"
    if term.startswith("C(periodo)"):
        return "Referência: primeiro período da amostra"
    if term == "formal":
        return "Referência: trabalhador informal"
    if term == "mulher":
        return "Referência: homem"
    if term == "preto_pardo":
        return "Referência: branco, amarelo ou indígena"
    if term == "formal:mulher":
        return "Diferença adicional para mulheres formais"
    if term == "formal:preto_pardo":
        return "Diferença adicional para pessoas pretas/pardas formais"
    return ""
