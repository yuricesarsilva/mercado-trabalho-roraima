# Reforma econométrica do Paper 1 (formalidade, gênero, raça/cor — Roraima)

Plano aprovado em 2026-08-14, a partir de uma revisão rigorosa de 20 pontos feita pelo autor sobre
a versão preliminar do paper/apresentação. Registra as decisões de caminho já tomadas e o
sequenciamento do trabalho. Ver `docs/evolucao_temporal.md`, `docs/mecanismo_jornada.md`,
`docs/replicacao_r_survey.md` e `docs/resumo_resultados_correntes.md` para o estado anterior a esta
reforma.

## Contexto

O paper preliminar (metodologia, tabelas, evolução temporal, cautelas) foi lido e revisado
integralmente, concluindo que a pergunta e os dados são bons (N=23.938 ocupados com renda válida,
~2.400/ano, "Roraima não é pequeno demais"), mas que a **econometria atual** mistura estimando com
interpretação em pelo menos três pontos graves: (1) os coeficientes de `mulher` e `preto_pardo` no
modelo com interações não são o "gap geral", são o gap **entre informais**; (2)
`FE_ocupação + FE_atividade` separados não equivalem a "mesma ocupação e setor"; (3) a categoria de
referência racial (`branco+amarelo+indígena`) não tem leitura socioeconômica coerente, especialmente
em Roraima.

Decisões de caminho já tomadas:
- Excluir `amarelo` da estimação de raça (N pequeno demais), com o motivo explícito no texto.
- **Inverter** a relação principal/restrita da amostra: a definição ampla de formalidade do IBGE
  (todos os ocupados) continua sendo a **amostra principal**; "empregados" vira a **amostra
  restrita**, usada para um resultado mais específico sobre o prêmio salarial estrito.
- Migração **total** para R com desenho amostral exato da PNAD-C (bootstrap, 200 réplicas oficiais)
  — nenhuma especificação nova fica só em Python/WLS.
- Baixar todos os trimestres 2016-2025 (não só um subconjunto de anos).
- Justificativa do recorte Q4-only reformulada: "reduz" a reutilização de UPAs do painel rotativo,
  não "evita" — e a tabela Q4-only × todos-os-trimestres vai para o **corpo principal** do paper
  (não apêndice), porque resolve diretamente uma limitação que a própria apresentação já declara.

Verificado no código e nos dados antes de planejar (não é só teórico):

- `formal` vem de `VD4009` (posição na ocupação) + `V4019` (CNPJ) — `scripts/02_build_analytic.py:13-26`.
  `VD4009` já distingue privado/doméstico/**público**/militar/empregador/conta-própria/familiar
  auxiliar — dá para extrair **setor público** e a amostra restrita de "empregados" **sem baixar
  dado novo**, e o script R já lê `VD4009`, `VD4010`, `VD4011`, `V2010` — nenhuma variável bruta
  nova é necessária para nada do Bloco B abaixo, só para o Bloco C (trimestres completos).
- Contagem real de `V2010` (raça/cor) na amostra atual: branca 5.072, preta 2.390, amarela **69**,
  parda 15.749, indígena 1.134. Amarela é sparse demais para dummy própria; as outras três não.
- Contagem real de `VD4009` nos 24.414 ocupados: privado c/carteira 5.240, privado s/carteira 3.402,
  doméstico c/carteira 315, doméstico s/carteira 1.403, público c/carteira 236, público s/carteira
  1.493, militar/estatutário 4.062, empregador 970, conta-própria 6.833, familiar auxiliar 460.
  Setor público (5+6+7) = 5.791 obs (~24% dos ocupados) — grande demais para ignorar, confirma o
  ponto 9 da revisão. "Empregados" (1-7) = 16.151 obs (66%); conta-própria+empregador = 7.803
  (32%) fica de fora da amostra restrita.
- Células `ocupação × atividade`: 96 de 132 combinações não vazias, mediana de 75,5 obs/célula, mas
  31 células com N<30 e 18 com N<10 — FE conjunto é viável, mas precisa de regra de agregação para
  a cauda esparsa.
- Hoje só o 4º trimestre de cada ano está baixado (~10 arquivos, ~1,7GB). Baixar todos os
  trimestres 2016-2025 = ~40 arquivos, estimativa de 6-9GB.
- `r/01_replicate_survey.R` já implementa desenho `survey` bootstrap (200 réplicas oficiais do
  IBGE) para o modelo atual (5 termos-chave, sem FE conjunto, só Q4) — já validado que os pontos
  estimados batem com Python a 1e-14 e que **74/200 réplicas falham em convergir** (provavelmente
  por esparsidade de alguma célula fina em algumas reamostragens), mesmo com um modelo bem mais
  simples do que o que vamos rodar agora. Isso é sinal de alerta real: FE ocupação×atividade + mais
  categorias de raça + amostra restrita menor devem piorar essa taxa. A taxa de convergência deve
  ser monitorada e reportada a cada rodada relevante.
- O ponto 13 da revisão (regredir tendência sobre os coeficientes extraídos) **já está resolvido
  corretamente em Python**: `scripts/09_estimate_trends.py` estima `formal:Ano`, `mulher:Ano`,
  `preto_pardo:Ano` diretamente no microdado (WLS com toda a covariância), não numa segunda regressão
  sobre os 10 coeficientes extraídos. A única coisa que falta é reestimar essa mesma lógica em R,
  o que já está coberto pelo Bloco C.

## Como este plano funciona

Organizado em 4 blocos (A-D), sequenciados por dependência técnica. Cada bloco termina num
checkpoint de revisão antes do próximo — nada roda "tudo de uma vez".

**Divisão de responsabilidades Python × R** (mudou com a decisão de migração total):
- **R** (`r/*.R`, estendendo `r/01_replicate_survey.R`) passa a ser a **fonte oficial de todos os
  coeficientes/erros-padrão/testes** do paper — desenho bootstrap completo (200 réplicas), para
  toda especificação (M1-M4, amostra ampla e restrita, margins/contrasts, mulher×raça, decomposição
  de jornada, tendência temporal, robustez de trimestres/pandemia).
- **Python** continua responsável por: baixar/extrair o microdado bruto (scripts `00`-`02`, que o
  R também usa como fonte), a tabela descritiva de N (não é questão de variância, então weighted
  count simples já é correto), e as figuras/tabelas do Beamer (lendo os CSVs de coeficientes que o
  R vai exportar — mesmo padrão que `presentation/apresentacao.tex` já usa hoje via `outputs/tables/`).
  Os scripts Python de modelagem (`03`, `06`, `07`, `09`) continuam no repositório como checagem
  rápida de ponto estimado (já validados a bater com R a 1e-14), mas deixam de ser citados como os
  números oficiais do paper.
- Risco de performance a monitorar: 200 refits por especificação, multiplicado por várias
  especificações (M1-M4 × 2 amostras × 2 variáveis dependentes × robustez), e depois × ~4 no Bloco C
  com todos os trimestres — pode ficar lento. Avaliar e, se necessário, paralelizar os replicate
  fits (o pacote `survey` e o R base suportam isso) e informar o tempo real antes de rodar tudo.

---

## Bloco A — Higiene de variáveis e amostra (Python, sem novo download)

Prepara as variáveis que tanto o pipeline Python (descritivas/figuras) quanto o R (estimação)
vão usar — mantendo o padrão já existente de duplicar a lógica de construção de variáveis em R
(comentário em `r/01_replicate_survey.R:116`: "replicando `src/pnadc_rr/*.py`").

**A1. Raça/cor: `branco` como referência, categorias separadas**
- Nova variável `raca_grupo` categórica: `branco` (ref.), `preto`, `pardo`, `indigena`. `amarelo`
  (N=69, ~0,3% da amostra) excluído da estimação de raça — motivo (N pequeno demais para uma dummy
  própria) documentado explicitamente em `docs/definicao_raca.md`, não escondido.
- Mantém `preto_pardo` binária como variável derivada (não removida) só para comparação com os
  resultados já publicados na apresentação atual.
- Arquivos: `scripts/02_build_analytic.py` (nova variável), `src/pnadc_rr/labels.py` (rótulos).

**A2. Setor público e posição na ocupação detalhada**
- `setor_publico` (1 se `VD4009 ∈ {5,6,7}`) e `posicao_ocupacao_grupo` categórica (privado
  c/carteira, privado s/carteira, doméstico c/carteira, doméstico s/carteira, público c/carteira,
  público s/carteira, militar/estatutário, empregador, conta-própria, familiar auxiliar) — direto
  de `VD4009`, sem dado novo.
- Arquivo: `scripts/02_build_analytic.py`.

**A3. Amostra principal (ampla, definição IBGE) e amostra restrita ("empregados")**
- **Principal**: todos os ocupados com `formal`/`informal` pela definição atual (IBGE) — sem
  mudança em relação a hoje.
- **Restrita**: `VD4009 ∈ {1,...,7}` (privado + doméstico + público + militar/estatutário),
  excluindo empregador/conta-própria/familiar auxiliar (32% dos ocupados) — dá o "prêmio salarial da
  formalidade" estrito, sem misturar CNPJ (empregador/conta-própria) com carteira assinada
  (empregado). Doméstico entra na amostra restrita (é `empregado` por lei — CLT/LC 150/2015), com
  `posicao_ocupacao_grupo` disponível para checar se o resultado muda ao excluí-lo.
- `docs/definicao_formalidade.md`: tabela `VD4009`/`V4019` → formal/informal/N, citando a definição
  oficial de informalidade do IBGE.
- Terminologia: "diferencial de rendimento associado à formalidade" para a amostra principal
  (ampla); "prêmio salarial da formalidade" reservado para a amostra restrita de empregados.

**A4. Tabela de células (N não ponderado, N ponderado, nº de UPAs)**
- Cruzamento `formal × sexo × raca_grupo × setor_publico`, feito depois de A1-A3. Define: (i) se
  `mulher × raca_grupo` é estimável, (ii) a regra de agregação de células esparsas em `ocupação ×
  atividade` para o Bloco B, (iii) a tabela que falta hoje no paper.
- Arquivo novo: `scripts/10_sample_audit_grupos.py`.

**Checkpoint A:** revisar a tabela de N e a proposta de regra de agregação de células esparsas
(ex.: limiar N<30 → agregação na atividade-mãe) antes de passar para o Bloco B.

---

## Bloco B — Estimação principal em R, desenho amostral completo (depende de A)

Tudo aqui roda com `svrepdesign` (bootstrap, 200 réplicas oficiais do IBGE), estendendo
`r/01_replicate_survey.R` — mesma técnica já validada, agora cobrindo as especificações novas, para
as duas amostras (principal e restrita) e as duas variáveis dependentes (mensal real, hora real).

**B1. Sequência de modelos aninhados M1→M4 + FE ocupação×atividade**
- `M1`: tratamentos (`formal`, `mulher`, `formal:mulher`, `raca_grupo`, `formal:raca_grupo`) + idade
  + escolaridade. `M2`: + `FE_atividade`. `M3`: + `FE_ocupação`. `M4`: + `FE_(ocupação×atividade)`
  (célula conjunta, células esparsas agregadas pela regra definida no Checkpoint A).
- Renomeia "sem controles × com controles" (hoje rotulado "robustez" na apresentação) para
  "sensibilidade à especificação / decomposição condicional" — "robustez" fica reservado para
  variação de amostra/definição/período (Bloco C).
- Mostra, para os 3 tópicos, quanto do gap bruto é absorvido em cada etapa M1→M4 — é a base
  quantitativa da narrativa "espelho" (raça encolhe, gênero emerge) do Bloco D.

**B2. Interpretação correta das interações via contrasts**
- Para cada especificação-chave: os 4 grupos preditos (Homem-Informal, Mulher-Informal,
  Homem-Formal, Mulher-Formal) e o equivalente por `raca_grupo`, com erro-padrão design-based via
  `svycontrast()` (pacote `survey`, já instalado) e teste de Wald formal via `regTermTest()`
  (ex.: H0: `mulher + formal:mulher = 0`).
- Toda a linguagem narrativa passa a especificar o status de formalidade a que o número se refere
  (ex.: "gap entre informais" vs. "gap entre formais"), em vez de um número genérico só.

**B3. Interação mulher × raça**
- Só depois de checar N em A4 (célula por célula). Extensão condicional: `formal × mulher ×
  raca_grupo`, só se as células tiverem N suficiente.

**B4. Decomposição exata do mecanismo de jornada**
- Como `ln(Y_mensal) = ln(w_hora) + ln(H_semanal)` é identidade algébrica, estimar a mesma
  especificação para `ln_renda_mensal_real`, `ln_renda_hora_real` e `ln(horas_semanais_principal)`
  (troca de nível para log em relação ao script Python atual) garante `β_mensal = β_hora +
  β_ln(horas)` por construção, na mesma amostra/desenho — decomposição exata, não só comparação.
- Reenquadra a seção: "renda mensal controlando por horas" deixa de ser chamada de especificação
  "mais controlada" — é uma especificação para investigar mecanismo (pode bloquear o canal
  gênero→jornada→renda).

**Checkpoint B:** revisar os resultados de M1-M4, os grupos preditos, a decomposição exata e a
**taxa de convergência bootstrap** de cada especificação antes de seguir para o Bloco C.

---

## Bloco C — Robustez temporal: trimestres completos e pandemia (depende de B estável)

**C0. Download completo (background, pode começar já — não bloqueia A/B)**
- `python scripts/00_download_pnadc.py` (todos os trimestres) e
  `python scripts/01_build_rr_microdata.py --quarters 1 2 3 4` para os ~40 arquivos 2016-2025
  (~6-9GB).

**C1. Empilhamento com FE ano×trimestre — elevado ao corpo principal do paper**
- Reestima a especificação final do Bloco B na base de todos os trimestres, com
  `FE_(ano×trimestre)` em vez de `FE_periodo` (Q4-only), também em R com desenho completo.
- Texto de justificativa: *"Mantém-se o quarto trimestre de cada ano como desenho principal,
  garantindo comparabilidade sazonal entre os cortes e reduzindo a intensidade de reutilização das
  unidades amostrais do painel rotativo. Como teste de robustez, reestimam-se as especificações
  utilizando todos os trimestres, com efeitos fixos de ano × trimestre."*
- Vai no **corpo principal** do paper como uma tabela curta Q4-only × todos-os-trimestres — resolve
  diretamente a limitação que a apresentação já declara ("fotografias de fim de período... robustez
  ainda não foi feita"), e se os coeficientes se mantiverem, vira evidência de estabilidade, não só
  uma checagem de rodapé.

**C2. Exclusão/split da pandemia**
- Reestima a especificação final em três recortes: 2016-2019, 2022-2025, e
  completo-exceto-2020-2021. Compara magnitude/significância de `formal`, `mulher`, `raça`.

**C3. Tendência temporal em R**
- Replica `scripts/09_estimate_trends.py` (já correto: `formal:Ano`, `mulher:Ano`,
  `raca_grupo:Ano` direto no microdado) em R com desenho bootstrap, usando `raca_grupo` no lugar de
  `preto_pardo`.

**Checkpoint C:** revisar a tabela Q4×todos-os-trimestres e o split de pandemia antes do Bloco D —
é esse número que decide se a tabela "sobrevive" como evidência de estabilidade.

---

## Bloco D — Narrativa, comunicação e literatura (depende de B/C estabilizados)

**D1.** Reescrever `docs/resumo_resultados_correntes.md` e `presentation/apresentacao.tex` com a
interpretação correta das interações (B2) e as novas fontes oficiais (R/survey) — números por
status de formalidade, não genéricos; tabela Q4×todos-os-trimestres no corpo principal.

**D2.** Narrativa "espelho": gap racial **encolhe** fortemente com controles (~-28,8% bruto →
~-6,1% condicional), gap de gênero **emerge/amplia** com controles (~-2,7% bruto → bem mais
negativo condicional). Usa a decomposição M1→M4 (B1) e tabelas descritivas de composição
(escolaridade/ocupação/atividade/setor público/formalidade por gênero e por raça) para sustentar
qual variável produz a inversão — não só inferir da mudança do coeficiente.

**D3.** Conversão em R$ via valores preditos (`E[Y|D=1,X] - E[Y|D=0,X]`), usando a infraestrutura
de contrasts do B2, em vez de aplicar % à renda média amostral.

**D4.** Revisão de literatura ampliada (informalidade + gap de gênero + gap racial no Brasil +
mercado de trabalho Norte/Amazônia/Roraima). Fontes reais buscadas e organizadas via busca web; a
curadoria final de citações acadêmicas fica com o autor.

**D5.** Ajustes finais de terminologia (ponto 20 já refletido em A3).

---

## Ordem de execução recomendada

1. **Bloco A** (A1→A4) — Python, rápido, sem dependência externa.
2. Em paralelo: **C0** (download completo) rodando em background desde o início.
3. **Bloco B** (B1→B4) em R, com Checkpoint A no início e Checkpoint B ao final.
4. **Bloco C** (C1→C3), assim que C0 terminar e B estiver estável.
5. **Bloco D**, por último, quando os números estiverem parados.

## Mapeamento com os 20 pontos da revisão original

| Pontos da revisão | Bloco |
| --- | --- |
| 1 (interações), 17 parcial | B2 |
| 2, 3 | B1 |
| 4 | B (migração total já decidida) |
| 5 | A4 |
| 6 | A1 |
| 7 | B3 |
| 8, 20 | A3 |
| 9 | A2 |
| 10, 11 | B4 |
| 12 | já corrigido (bug de texto vs. gráfico na evolução temporal) |
| 13 | já correto em Python (C3 replica em R) |
| 14, 15 | C0-C2 |
| 16, 17 | D2 |
| 18 | D3 |
| 19 | D4 |

## Verificação

- Cada script novo/alterado (Python ou R) roda isoladamente e imprime `saved:`/`cat()` para seus
  outputs (padrão já usado em todo o pipeline, dos dois lados).
- Depois de cada bloco: recompilar `presentation/apresentacao.tex` com `pdflatex` e conferir
  visualmente as páginas alteradas.
- A cada rodada relevante do R: reportar N de réplicas bootstrap que convergiram (de 200) — sinal de
  alerta se cair muito abaixo do que já é hoje (126/200).
- Checkpoints A, B, C explícitos antes de avançar de bloco — nada roda "tudo de uma vez".
