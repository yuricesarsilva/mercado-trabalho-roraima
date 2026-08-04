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

ESCOLARIDADE_LABELS = {
    "1": "Sem instrução ou fundamental incompleto",
    "2": "Fundamental incompleto ou equivalente",
    "3": "Fundamental completo ou equivalente",
    "4": "Médio incompleto ou equivalente",
    "5": "Médio completo ou equivalente",
    "6": "Superior incompleto ou equivalente",
    "7": "Superior completo",
}

OCUPACAO_LABELS = {
    "1": "Diretores e gerentes",
    "2": "Profissionais das ciências e intelectuais",
    "3": "Técnicos e profissionais de nível médio",
    "4": "Trabalhadores de apoio administrativo",
    "5": "Trabalhadores dos serviços e vendedores",
    "6": "Trabalhadores agropecuários, florestais, da caça e pesca",
    "7": "Trabalhadores qualificados da indústria, construção e artes",
    "8": "Operadores de instalações, máquinas e montadores",
    "9": "Ocupações elementares",
    "10": "Forças armadas, policiais e bombeiros",
}

ATIVIDADE_LABELS = {
    "1": "Agropecuária",
    "2": "Indústria geral",
    "3": "Construção",
    "4": "Comércio e reparação",
    "5": "Transporte, armazenagem e correio",
    "6": "Alojamento e alimentação",
    "7": "Informação, comunicação, financeiro, imobiliário, profissional e administrativo",
    "8": "Administração pública, educação, saúde e serviços sociais",
    "9": "Outros serviços",
    "10": "Serviços domésticos",
    "11": "Atividades mal definidas",
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
