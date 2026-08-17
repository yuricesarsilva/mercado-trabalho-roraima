# Definição de `raca_grupo`

Construída em `scripts/02_build_analytic.py` a partir de `V2010` (cor ou raça, autodeclarada,
PNAD Contínua). Substitui a variável binária `preto_pardo` (mantida no dataset só para comparação
com resultados anteriores) como especificação principal de raça/cor a partir da reforma registrada
em `docs/plano_reforma_econometrica.md`.

## Por que não `preto_pardo` com referência `branco+amarelo+indígena`

A especificação anterior definia `preto_pardo` = 1 para pretos/pardos, com todo o resto (brancos,
amarelos e indígenas) como grupo de referência único. Essa categoria de referência não tem leitura
socioeconômica coerente — agrupa grupos racial e historicamente muito distintos só porque nenhum
deles é preto/pardo. `raca_grupo` corrige isso: `branco` vira a referência sozinho, e `preto`,
`pardo` e `indigena` entram como dummies próprias.

## Mapeamento `V2010` → `raca_grupo`

| `V2010` | Categoria oficial PNAD-C | `raca_grupo` | N (não ponderado, ocupados) | % da amostra |
| --- | --- | --- | --- | --- |
| 1 | Branca | `branco` (referência) | 5.072 | 20,8% |
| 2 | Preta | `preto` | 2.390 | 9,8% |
| 3 | Amarela | **excluído** (`NaN`) | 69 | 0,3% |
| 4 | Parda | `pardo` | 15.749 | 64,5% |
| 5 | Indígena | `indigena` | 1.134 | 4,6% |

Total de ocupados: 24.414.

## Por que excluir `amarelo` em vez de agrupá-lo em algum lugar

Com N=69 (0,3% da amostra), uma dummy própria para `amarelo` não teria poder estatístico
utilizável, e agrupá-la com qualquer outra categoria (branco, indígena, ou um resíduo "outros") por
conveniência reintroduziria o mesmo problema que motivou abandonar a referência antiga
(`branco+amarelo+indígena`): uma categoria sem leitura socioeconômica coerente, só que menor. A
opção adotada é excluir essas 69 observações da estimação de raça (ficam de fora de qualquer modelo
que use `raca_grupo`/`C(raca_grupo)`), mantendo-as nas estatísticas descritivas gerais (auditoria
amostral, N total do paper) onde a variável racial não é o foco.

## Uso

- Estimação (R, `r/*.R`): `factor(raca_grupo)`, com `branco` como nível de referência.
- Rótulos para tabelas/figuras: `src/pnadc_rr/labels.py` (`RACA_GRUPO_LABELS`,
  `RACA_GRUPO_SHORT_LABELS`).
- `preto_pardo` (binária) permanece no dataset processado, sem uso na especificação principal — só
  para comparação com a apresentação/resultados anteriores à reforma.
