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
- `ln_renda_mensal`: log do rendimento mensal.
- `ln_renda_hora`: log do rendimento por hora.
