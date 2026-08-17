# Resultados do Bloco B — Estimação em R, desenho amostral completo

Gerado a partir de `r/02_estimate_nested.R`, `r/03_jornada_decomposicao.R` e
`r/04_margins_contrasts.R` (ver `docs/plano_reforma_econometrica.md`). Todos os modelos usam
`svrepdesign` (bootstrap, 200 réplicas oficiais do IBGE), amostra 2016T4-2025T4, RR.

## 1. Convergência bootstrap por especificação (M1→M4)

Número de réplicas descartadas pelo `svyglm` (qualquer coeficiente do modelo ficou não
identificável naquela réplica) — idêntico nas 2 amostras e nas 2 variáveis dependentes:

| Modelo | Parâmetros | Réplicas descartadas |
| --- | ---: | ---: |
| M1 (tratamentos + idade + escolaridade + período) | 30 | 0/200 |
| M2 (M1 + FE atividade) | 41 | 32/200 |
| M3 (M2 + FE ocupação) | 51 | 74/200 |
| **M4 (tratamentos + FE ocupação×atividade com "outras")** | 95 | **0/200** |

M4 é a especificação mais estável de todas, apesar de ter mais parâmetros que M1-M3 — a
agregação das 31 células esparsas (`ocupação×atividade` com N<30) em um bucket único "outras"
(N=344, 201 UPAs) resolveu o problema de convergência que M2/M3 têm (as células individuais
esparsas, algumas com N=1, desapareciam em boa parte das reamostragens bootstrap). **M4 é a
especificação preferida do paper daqui para frente.**

A decomposição de jornada (Bloco B4, abaixo) foi refeita com a especificação M4 (FE conjunto)
depois deste checkpoint — confirmado: também caiu para 0/200 réplicas descartadas (era 74/200 com
FE separados). Como bônus, os coeficientes da decomposição agora coincidem exatamente com os do
modelo M4 da seção 2 (antes havia pequena divergência por usarem especificações diferentes).

## 2. Coeficientes-chave, especificação M4

`outputs/tables/r_nested_{amostra}_{dv}_M4.csv` tem a tabela completa. Efeito percentual
aproximado (`(exp(coef)-1)*100`):

| Termo | Ampla, mensal | Ampla, hora | Restrita, mensal | Restrita, hora |
| --- | ---: | ---: | ---: | ---: |
| formal | +41,4%*** | +34,3%*** | +32,0%*** | +29,3%*** |
| mulher | -28,8%*** | -17,7%*** | -21,2%*** | -12,5%*** |
| preto (ref. branco) | -12,9%*** | -9,6%** | -10,6%** | -6,0% (ns) |
| pardo (ref. branco) | -11,7%*** | -9,2%*** | -9,9%*** | -7,0%* |
| indígena (ref. branco) | -16,6%*** | -12,8%*** | -11,2%* | -7,8% (ns) |
| formal:mulher | +15,8%*** | -0,5% (ns) | +6,9%** | -4,4%* |

`*p<0,10; **p<0,05; ***p<0,01`. Termos completos (incl. `formal:raça`, `mulher:raça`) nos CSVs.

## 3. Margins/contrasts corrigidos (Bloco B2) — a leitura certa das interações

Ver `outputs/tables/r_contrastes_todos.csv`. Cada célula é o gap **dentro** do status de
formalidade indicado (`mulher` sozinho = gap entre informais; `mulher + formal:mulher` = gap
entre formais), não um número genérico.

### Renda por hora real, amostra ampla (a especificação mais citada na apresentação)

| Contraste | Efeito % | p-valor |
| --- | ---: | ---: |
| Mulher vs. homem, entre **informais** | -17,7% | <0,001 |
| Mulher vs. homem, entre **formais** | -18,1% | <0,001 |
| Diferença do gap de gênero (formal − informal) | -0,5 p.p. | 0,775 (ns) |
| Preto vs. branco, entre informais | -9,6% | <0,001 |
| Preto vs. branco, entre formais | -15,5% | <0,001 |
| Diferença do gap racial preto (formal − informal) | -6,5 p.p. | 0,071 (marginal) |
| Indígena vs. branco, entre informais | -12,8% | <0,001 |
| Indígena vs. branco, entre formais | -22,7% | <0,001 |
| Diferença do gap racial indígena (formal − informal) | -11,3 p.p. | 0,0099 (significativo) |
| Prêmio de formalidade, homem branco | +34,3% | <0,001 |
| Prêmio de formalidade, mulher preta | +24,9% | <0,001 |
| Prêmio de formalidade, mulher parda | +28,1% | <0,001 |
| Prêmio de formalidade, mulher indígena | +18,4% | <0,001 |

**Achados que mudam a narrativa em relação à versão anterior:**

- **Gênero, renda por hora:** o gap de gênero **não muda com a formalidade** (-17,7% vs. -18,1%,
  diferença não significativa). O `formal:mulher` positivo e significativo que aparecia na renda
  **mensal** (+15,8%, atenua o gap) é inteiramente um efeito de **jornada** (formalização
  padroniza as horas de mulheres, não o preço da hora) — ver decomposição no item 4.
- **Raça, renda por hora:** ao contrário da intuição de que formalização reduziria desigualdade,
  a formalização **piora** o gap racial por hora, e para indígenas isso é estatisticamente
  significativo (gap quase dobra: -12,8% informal → -22,7% formal).
- **Interseccionalidade formal×raça×gênero:** o prêmio de formalidade não é uniforme — é maior
  para homens brancos (+34,3%) e menor para mulheres indígenas (+18,4%), quase metade.

(Ver `outputs/tables/r_contrastes_{amostra}_{dv}.csv` para os mesmos contrastes nas outras 3
combinações amostra×variável dependente — o padrão qualitativo se repete: gap de gênero estável
entre formal/informal na renda por hora mas não na mensal; gap racial indígena piora com
formalidade em quase todas as especificações.)

## 4. Decomposição exata do mecanismo de jornada (Bloco B4)

Reestimada com a especificação M4 (FE conjunto ocupação×atividade) após o Checkpoint B —
**0/200 réplicas descartadas** (era 74/200 com FE separados). Identidade
`β_mensal = β_hora + β_ln(horas)` verificada exatamente (diferença ~1e-15, ruído de ponto
flutuante) para todos os termos-chave, nas duas amostras — ver
`outputs/tables/r_jornada_identidade_{amostra}.csv`. Os coeficientes de `β_mensal` e `β_hora`
aqui coincidem exatamente com os da seção 2 (mesma especificação M4).

Decomposição (amostra ampla): quanto do efeito mensal é preço (hora) vs. quantidade (jornada)?

| Termo | β mensal | β hora (preço) | β ln(horas) (quantidade) | % do efeito mensal que é quantidade |
| --- | ---: | ---: | ---: | ---: |
| mulher | -0,340 | -0,194 | -0,146 | 43% |
| formal | +0,347 | +0,295 | +0,052 | 15% (formal trabalha **mais** horas) |
| formal:mulher | +0,147 | -0,005 | +0,152 | ~104% — é **só** efeito-jornada |
| preto | -0,138 | -0,101 | -0,037 | 27% |
| pardo | -0,125 | -0,096 | -0,029 | 23% |
| indígena | -0,182 | -0,137 | -0,045 | 25% |

Confirma a leitura do item 3: o `formal:mulher` positivo na renda mensal é praticamente 100%
efeito-jornada (formalização não muda o preço da hora para mulheres, muda a jornada). Raça segue
majoritariamente efeito-preço (73-77% do efeito mensal), como já indicado antes da reforma.

## Próximo passo

Checkpoint B: confirmar esta leitura antes do Bloco C (robustez de trimestres completos +
pandemia, já com os dados baixados).
