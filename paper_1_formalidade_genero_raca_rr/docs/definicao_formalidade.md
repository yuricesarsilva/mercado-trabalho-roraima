# Definição de formalidade e das amostras principal/restrita

Construídas em `scripts/02_build_analytic.py` a partir de `VD4009` (posição na ocupação no
trabalho principal) e `V4019` (CNPJ do negócio/empresa do trabalho principal), PNAD Contínua.

## Mapeamento `VD4009`/`V4019` → `formal`

| `VD4009` | Categoria oficial PNAD-C | `posicao_ocupacao_grupo` | `formal` | Critério | N (não pond.) | N (ponderado) |
| --- | --- | --- | --- | --- | ---: | ---: |
| 1 | Empregado do setor privado, com carteira | `privado_com_carteira` | 1 | posição | 5.240 | 576.926 |
| 2 | Empregado do setor privado, sem carteira | `privado_sem_carteira` | 0 | posição | 3.402 | 332.088 |
| 3 | Trabalhador doméstico, com carteira | `domestico_com_carteira` | 1 | posição | 315 | 28.286 |
| 4 | Trabalhador doméstico, sem carteira | `domestico_sem_carteira` | 0 | posição | 1.403 | 129.997 |
| 5 | Empregado do setor público, com carteira | `publico_com_carteira` | 1 | posição | 236 | 24.886 |
| 6 | Empregado do setor público, sem carteira | `publico_sem_carteira` | 0 | posição | 1.493 | 145.430 |
| 7 | Militar e servidor estatutário | `militar_estatutario` | 1 | posição | 4.062 | 413.384 |
| 8 | Empregador | `empregador` | CNPJ (`V4019`) | 567 com CNPJ / 403 sem | 970 | 85.111 |
| 9 | Conta-própria | `conta_propria` | CNPJ (`V4019`) | 712 com CNPJ / 6.121 sem | 6.833 | 633.563 |
| 10 | Trabalhador familiar auxiliar | `familiar_auxiliar` | 0 (sempre informal) | posição | 460 | 32.224 |

Total: 24.414 ocupados; `formal`=1 em 11.132 (45,6%), `formal`=0 em 13.282 (54,4%).

Para empregador/conta-própria (`VD4009 ∈ {8,9}`), a posição na ocupação por si só não define
formal/informal — usa-se `V4019` (o negócio tem CNPJ?) como critério: CNPJ=1 → formal; CNPJ=2 →
informal. É por isso que essas duas categorias têm uma coluna "critério" diferente das demais na
tabela acima.

Esta definição segue a mesma lógica da taxa de informalidade oficial do IBGE (que soma empregados
sem carteira do setor privado, trabalhadores domésticos sem carteira, empregadores e contas-própria
sem CNPJ, e trabalhadores familiares auxiliares).

## Duas amostras

**Principal (ampla)**: todos os 24.414 ocupados, definição de `formal` acima — é a especificação
usada no corpo principal do paper e nas figuras/tabelas gerais.

**Restrita (`empregado_restrito` = 1)**: `VD4009 ∈ {1,2,3,4,5,6,7}` — privado, doméstico, público e
militar/estatutário; exclui empregador, conta-própria e familiar auxiliar (`VD4009 ∈ {8,9,10}`,
7.803 obs., 32% dos ocupados). Usada para um resultado mais específico de "prêmio salarial da
formalidade": nesta amostra, `formal`/`informal` significa exclusivamente carteira assinada, sem
misturar com a lógica de CNPJ que define formalidade para empregador/conta-própria — 16.151
observações (66,2%).

Trabalhador doméstico entra na amostra restrita (é `empregado` por definição legal — CLT/LC
150/2015), mas é um segmento com dinâmica de jornada/remuneração bem distinta (1.718 obs., 315
formais + 1.403 informais); `posicao_ocupacao_grupo` permite testar como robustez se excluí-lo muda
o resultado da amostra restrita.

## Terminologia usada no paper

- **"Diferencial de rendimento associado à formalidade"**: amostra principal (ampla) — inclui
  relações de trabalho estruturalmente diferentes (assalariado, doméstico, empregador,
  conta-própria), então "salarial" seria impreciso.
- **"Prêmio salarial da formalidade"**: reservado para a amostra restrita de empregados, onde a
  comparação é estritamente entre ter ou não carteira assinada dentro de uma relação de emprego.

## Uso

- Estimação (R, `r/*.R`): `data[data$empregado_restrito == 1, ]` para a amostra restrita.
- `setor_publico` (1 se `VD4009 ∈ {5,6,7}`, 5.791 obs./23,7% dos ocupados) fica disponível como
  controle/interação em ambas as amostras — ver `docs/plano_reforma_econometrica.md`, item A2/B.
