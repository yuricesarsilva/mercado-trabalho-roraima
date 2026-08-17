# Resultados do Bloco C — Robustez temporal

Gerado a partir de `r/05_robustez_trimestres_pandemia.R` (C1+C2) e `r/06_tendencia_temporal.R`
(C3) — ver `docs/plano_reforma_econometrica.md`. Todos os modelos são a especificação M4
(FE ocupação×atividade), `svrepdesign` bootstrap (200 réplicas), **0/200 réplicas descartadas em
todas as 20 estimações deste bloco** — a especificação M4 continua sendo a mais estável mesmo com
4x mais observações (todos os trimestres) ou amostras bem menores (recortes de pandemia, N~10 mil).

## Nota técnica: arquivo corrompido encontrado e corrigido

`data/raw/2017/PNADC_022017_20250815.zip` estava truncado (11,5MB em vez de ~230MB) — resíduo da
queda de energia de uma sessão anterior; o script de download pula arquivos que já "existem" sem
checar integridade, então o download completo (C0) reportou sucesso sem perceber. Identificado ao
tentar ler os 40 trimestres (erro de zip inválido), corrigido apagando e rebaixando só esse
arquivo. Os outros 39 arquivos foram verificados (checagem de CRC) e estão íntegros.

## C1: todos os trimestres vs. Q4-only

Amostra ampla, todos os trimestres: **97.187 ocupados** (vs. 24.414 no Q4-only) — quase 4x mais
observações. Renda por hora real, comparação lado a lado:

| Termo | Q4-only | Todos os trimestres |
| --- | ---: | ---: |
| formal | +34,3%*** | +30,6%*** |
| mulher | -17,7%*** | -16,8%*** |
| preto (ref. branco) | -9,6%*** | -9,8%*** |
| pardo (ref. branco) | -9,2%*** | -7,4%*** |
| indígena (ref. branco) | -12,8%*** | -12,4%*** |
| formal:mulher | -0,5% (ns) | +1,9%* |

**Leitura: os achados sobrevivem.** Mesma direção, magnitude parecida (diferenças de 1-4 p.p.),
significância mantida em quase tudo. `formal:mulher` passa a ser marginalmente significativo com
todos os trimestres (p=0,048) mas o efeito é pequeno (+1,9 p.p.) — não muda a conclusão de que o
gap de gênero na renda por hora é essencialmente constante entre formais e informais. Isso resolve
diretamente a limitação que a apresentação já declarava ("robustez com todos os trimestres ainda
não foi feita") — vira tabela para o corpo principal do paper, não nota de rodapé.

Renda mensal real segue o mesmo padrão (ver `outputs/tables/r_robustez_trimestres.csv` para a
tabela completa com as duas variáveis dependentes).

## C2: split de pandemia (Q4-only, três recortes)

`pre_pandemia_2016_2019` (N=10.267), `pos_pandemia_2022_2025` (N=9.922),
`excl_2020_2021` (N=20.189, união dos dois). Renda por hora real:

| Termo | 2016-2019 | 2022-2025 | Excl. 2020-2021 |
| --- | ---: | ---: | ---: |
| formal | +28,4%*** | +31,8%*** | +30,8%*** |
| mulher | -14,0%*** | -18,2%*** | -16,6%*** |
| preto | -8,3% (p=0,069) | -5,4% (ns) | -6,3%* |
| pardo | -9,5%*** | -9,6%*** | -9,4%*** |
| indígena | -14,8%*** | -12,7%** | -14,0%*** |
| formal:mulher | +2,1% (ns) | -3,2% (ns) | -0,8% (ns) |

**Leitura:** prêmio de formalidade, gap de gênero, gap de pardo e gap de indígena são estáveis nos
três recortes — nenhum é artefato do período pandêmico. `formal:mulher` continua não significativo
em nenhum recorte, reforçando que o gap de gênero por hora não varia com formalidade
independentemente do período. **Única fragilidade real:** o gap de **preto** (não pardo) perde
significância no recorte pós-pandemia (p=0,193) — provavelmente falta de poder estatístico com a
amostra menor (N~10 mil por recorte, e preto é a segunda categoria racial menos numerosa), não
evidência de que o gap tenha desaparecido (o sinal e a magnitude continuam negativos e parecidos
em todos os recortes).

Renda mensal real: mesmo padrão geral; `formal:mulher` na renda mensal continua positivo e
significativo nos três recortes (+11% a +20%), consistente com o achado do Bloco B de que é um
efeito quase inteiramente de jornada, não de período.

## C3: tendência linear em R (raça desagregada)

Renda por hora real, especificação M4 + `termo:Ano`:

| Termo | Inclinação (%/ano) | p-valor |
| --- | ---: | ---: |
| formal:Ano | -0,31% | 0,413 (ns) |
| mulher:Ano | -0,34% | 0,245 (ns) |
| preto:Ano | +0,67% | 0,307 (ns) |
| **pardo:Ano** | **+0,96%** | **0,022** (significativo a 5%) |
| indígena:Ano | +0,78% | 0,340 (ns) |

Mais preciso que a versão Python anterior (que só tinha `preto_pardo` agregado, p=0,085
marginal): ao desagregar, o sinal de queda do gap racial vem principalmente de **pardo**
(significativo a 5% com o desenho amostral completo), enquanto preto e indígena isoladamente não
atingem significância — plausivelmente por menor N em cada categoria separada, não por ausência de
tendência. Prêmio de formalidade e gap de gênero seguem sem tendência linear detectável, confirmando
o Bloco B (evolução temporal já reportada em `docs/evolucao_temporal.md`, agora validada com
desenho completo).

## Síntese do Bloco C

Nenhum dos achados centrais do Bloco B foi artefato do recorte Q4-only ou do período pandêmico.
A única ressalva nova é a fragilidade estatística do gap de **preto** especificamente (não pardo)
em amostras menores — vale mencionar como limitação no paper, não como resultado nulo.

## Próximo passo

Checkpoint C: confirmar esta leitura antes do Bloco D (reescrever narrativa/apresentação/docs com
a interpretação corrigida e todos os achados dos Blocos B e C).
