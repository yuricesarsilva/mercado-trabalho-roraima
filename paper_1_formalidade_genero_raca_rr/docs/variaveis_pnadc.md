# Variáveis de Interesse

Esta lista será validada contra o dicionário oficial de cada ano da PNAD Contínua antes da extração final.

## Identificação e desenho amostral

- `Ano`: ano da entrevista.
- `Trimestre`: trimestre da entrevista.
- `UF`: Unidade da Federação; Roraima = `14`.
- `UPA`: unidade primária de amostragem.
- `Estrato`: estrato amostral.
- `V1028`: peso amostral usualmente utilizado nas estimativas trimestrais.

## Mercado de trabalho

- `VD4002`: condição de ocupação.
- `VD4009`: posição na ocupação e categoria do emprego.
- `VD4010`: grupamento de atividade do trabalho principal.
- `VD4011`: grupamento ocupacional do trabalho principal.
- `VD4016`: rendimento habitual do trabalho principal.
- `VD4019`: rendimento habitual de todos os trabalhos.
- `V4019`: CNPJ do negócio/empresa do trabalho principal.
- `V4029`: carteira de trabalho assinada.
- `V4032`: contribuição para instituto de previdência.
- `V4039`: horas habitualmente trabalhadas por semana no trabalho principal.
- `VD4035`: horas efetivas em todos os trabalhos.

## Demografia

- `V2007`: sexo.
- `V2010`: cor ou raça.
- `V2009`: idade.
- `VD3004` ou variável equivalente: nível de instrução.

## Variáveis construídas

- `formal`: trabalhador formal segundo posição na ocupação, carteira, setor público, CNPJ ou contribuição previdenciária, conforme disponibilidade anual.
- `mulher`: indicador para sexo feminino.
- `preto_pardo`: indicador para pessoas pretas ou pardas.
- `renda_hora`: rendimento habitual mensal dividido por horas mensais aproximadas.
- `ln_renda_mensal`: log do rendimento mensal nominal.
- `ln_renda_hora`: log do rendimento por hora nominal.
- `deflator_habitual`: deflator oficial trimestral da PNAD Contínua (IBGE) para rendimento habitual, específico de UF e trimestre.
- `renda_mensal_real`, `renda_hora_real`: rendimentos mensal e por hora deflacionados (`renda * deflator_habitual`).
- `ln_renda_mensal_real`, `ln_renda_hora_real`: logs dos rendimentos reais. Usados nos modelos principais.
- `horas_semanais_principal`: horas habitualmente trabalhadas por semana no trabalho principal (`V4039`). Usada como controle opcional e como variável dependente na análise de mecanismo (`docs/mecanismo_jornada.md`).
