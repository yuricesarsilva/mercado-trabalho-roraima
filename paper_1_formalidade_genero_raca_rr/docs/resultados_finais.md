# Formalidade, Gênero e Raça/Cor no Mercado de Trabalho de Roraima — Resultados

Análise dos diferenciais de rendimento associados à formalidade, ao gênero e à raça/cor entre
pessoas ocupadas em Roraima, com microdados da PNAD Contínua (IBGE), 2016T4-2025T4.

## 1. Dados e amostra

Microdados trimestrais da PNAD Contínua, Roraima (UF 14). Recorte principal: 4º trimestre de cada
ano entre 2016 e 2025 (dez cortes) — mesmo trimestre em todos os anos para manter comparabilidade
sazonal e reduzir a intensidade de reutilização das unidades amostrais do painel rotativo (um
domicílio permanece no painel por até 5 trimestres consecutivos; o intervalo de um ano entre
quartos trimestres consecutivos excede essa janela). A estabilidade dos resultados a esse recorte
é testada diretamente na Seção 6.

Funil amostral (não ponderado): 59.630 pessoas entrevistadas → 45.013 com 14 anos ou mais →
24.414 ocupadas → 23.938 ocupadas com rendimento habitual válido.

Duas amostras de trabalho, conforme a pergunta:

- **Amostra ampla** (N=23.938): todos os ocupados com rendimento válido. `formal` segue a lógica
  de informalidade do IBGE — combina posição na ocupação (carteira assinada para empregados,
  incluindo domésticos e servidores públicos) com CNPJ do negócio para empregadores e
  conta-própria. Usada para o diferencial geral de rendimento associado à formalidade.
- **Amostra restrita** (N=16.135, 66,2% da ampla): só relações de emprego assalariado — privado,
  doméstico, público e militar/servidor estatutário (exclui empregador, conta-própria e
  trabalhador familiar auxiliar, 32% dos ocupados, onde "formal" depende de CNPJ e não de
  carteira). Usada para o prêmio salarial estrito da formalização.

Raça/cor (`V2010`): branca (referência), preta, parda, indígena. Pessoas amarelas (69 de 24.414,
0,3%) ficam fora da estimação de raça por N insuficiente para uma categoria própria; entram nas
estatísticas gerais de amostra.

## 2. Metodologia

### 2.1 Especificação

$$
\ln(w_{it}) = \beta_1 Formal_{it} + \beta_2 Mulher_i + \beta_3 (Formal_{it}\times Mulher_i)
+ \sum_{r} \beta_{4r} Raça_{ri} + \sum_r \beta_{5r} (Formal_{it}\times Raça_{ri}) + \sum_r \beta_{6r} (Mulher_i\times Raça_{ri})
$$
$$
+ \gamma_1 Idade_{it} + \gamma_2 Idade^2_{it} + \sum_e \delta_e Escolaridade_{ei}
+ \sum_c \theta_c Célula_{ci} + \sum_t \lambda_t Período_{ti} + \varepsilon_{it}
$$

onde $w_{it}$ é o rendimento real (mensal ou por hora, deflacionado pelo deflator oficial
trimestral da PNAD Contínua, específico de UF e trimestre) da pessoa $i$ no período $t$; $r$
indexa preta/parda/indígena (branca = referência); $c$ indexa 66 células de
**ocupação × atividade** (grupamento ocupacional de 11 categorias × grupamento de atividade de 12
categorias, com as combinações de N<30 agregadas numa categoria residual "outras" — necessário
para estabilidade estatística, ver Seção 2.3); $t$ indexa os 10 períodos (ano-trimestre).

Efeitos fixos de célula ocupação×atividade (em vez de ocupação e atividade separados) garantem
que a comparação seja, de fato, entre pessoas na mesma combinação de ocupação e setor — não apenas
controlando os dois marginalmente. Para a amostra restrita, uma extensão inclui `setor_publico` e
sua interação com `Formal` (Seção 4.4).

### 2.2 Interpretação dos coeficientes de interação

Como o modelo tem `Mulher` e `Formal×Mulher` simultaneamente, **o coeficiente de `Mulher` isolado
não é o gap de gênero geral — é o gap entre pessoas informais**. O gap entre formais é a soma
`Mulher + Formal×Mulher`. O mesmo vale para raça: `Raça_r` é o gap entre informais, `Raça_r +
Formal×Raça_r` é o gap entre formais. Todos os resultados abaixo já usam essa combinação correta,
com erro-padrão obtido da matriz de covariância completa do modelo (não da soma ingênua dos
erros-padrão individuais) e teste de hipótese formal para a diferença entre os dois gaps.

### 2.3 Estimação e inferência

Mínimos quadrados ponderados pelo peso amostral (`V1028`), dentro do desenho de réplicas bootstrap
oficial da PNAD Contínua (200 réplicas, distribuídas pelo IBGE desde 2016) — pacote `survey` em R
(`svrepdesign` + `svyglm`), que produz erros-padrão consistentes com o desenho amostral complexo
(estratificação, conglomeração em UPAs, pós-estratificação).

A agregação de células esparsas de ocupação×atividade em "outras" não é só uma escolha de
parcimônia: sem ela, o modelo com 96 células individuais tem uma taxa de falha de réplicas
bootstrap de até 74/200 (algumas células, com N tão baixo quanto 1, ficam vazias em boa parte das
reamostragens, tornando o modelo localmente não identificável naquela réplica). Com a agregação
(31 células de N<30, somando N=344 e 201 UPAs, viram uma única categoria "outras"), a taxa de
falha cai para 0/200 em toda especificação estimada neste documento — validado também nas
variações de amostra e período das Seções 5-6 (nenhuma das ~30 especificações estimadas para este
documento perde qualquer réplica bootstrap).

## 3. Motivação: gap bruto vs. condicional

Sem nenhum controle, os diferenciais de rendimento por hora são:

| Comparação | Grupo de referência | Grupo comparado | Gap bruto |
| --- | ---: | ---: | ---: |
| Formalidade | Informal: R$ 12,99/h | Formal: R$ 24,88/h | +91,5% |
| Gênero | Homem: R$ 19,10/h | Mulher: R$ 18,59/h | -2,7% |
| Raça/cor | Branco: R$ 26,22/h | Preto/pardo: R$ 17,06/h | -34,9% |

O gap de gênero bruto é pequeno porque mistura dois efeitos que puxam em direções opostas:
mulheres em Roraima têm, em média, atributos observáveis (escolaridade, alocação
ocupacional/setorial) associados a rendimentos mais altos, mas recebem menos dentro dessas
mesmas condições — o gap condicional (Seção 4.2) é bem maior que o bruto. Já o gap racial bruto é
grande e, ao condicionar, cai bastante (Seção 4.3) — indício de que grande parte da desigualdade
racial bruta opera via composição (escolaridade, alocação ocupacional/setorial), não só via preço
dentro da mesma posição.

## 4. Resultados

### 4.1 Formalidade

Diferencial de rendimento associado à formalidade, condicional a idade, escolaridade, célula
ocupação×atividade e período:

| | Amostra ampla | Amostra restrita (empregados) |
| --- | ---: | ---: |
| Renda mensal real | +41,4% | +32,0% |
| Renda por hora real | +34,3% | +29,3% |

(p<0,001 em todos os casos.) É o maior diferencial condicional identificado no estudo — maior que
gênero ou raça/cor isoladamente — e não se explica por jornada mais curta dos informais: pessoas
formais trabalham, em média, **mais** horas (Seção 4.6), então o diferencial de renda por hora
já isola o efeito-preço puro.

O prêmio de formalidade não é uniforme entre grupos demográficos (Seção 4.5): varia de +34,3%
(homens brancos) a +18,4% (mulheres indígenas) na renda por hora.

### 4.2 Gênero

Gap de gênero condicional na renda por hora real, separado por status de formalidade (ver Seção
2.2):

| | Entre informais | Entre formais | Diferença |
| --- | ---: | ---: | ---: |
| Amostra ampla | -17,7%*** | -18,1%*** | -0,5 p.p. (p=0,78, ns) |
| Amostra restrita | -12,5%*** | -16,3%*** | -4,4 p.p. (p=0,024) |

`***p<0,01`. Na amostra ampla, **o gap de gênero por hora é estatisticamente indistinguível entre
formais e informais** — o diferencial de preço da hora entre mulheres e homens não difere conforme
o status de formalidade. Na renda **mensal**, por outro lado, a interação `Formal×Mulher` é positiva e
significativa (+15,8% na amostra ampla, +6,9% na restrita) — mas a decomposição exata (Seção 4.6)
mostra que isso é **inteiramente efeito de jornada**: a diferença de jornada entre mulheres e
homens é menor entre pessoas formais; o diferencial de preço da hora permanece o mesmo.

### 4.3 Raça/cor

Gap racial condicional na renda por hora real (amostra ampla), por status de formalidade:

| Grupo (ref.: branco) | Entre informais | Entre formais | Diferença |
| --- | ---: | ---: | ---: |
| Preto | -9,6%*** | -15,5%*** | -6,5 p.p. (p=0,071) |
| Pardo | -9,2%*** | -12,9%*** | -4,1 p.p. (p=0,152, ns) |
| Indígena | -12,8%*** | -22,7%*** | -11,3 p.p. (p=0,0099) |

**Os gaps raciais não são reduzidos entre pessoas formais** — para pessoas indígenas, tornam-se
**estatisticamente significativos e maiores** (quase dobram: -12,8% entre informais para -22,7%
entre formais); há evidência mais fraca na mesma direção para pessoas pretas (p=0,071); não há
evidência significativa de diferença para pessoas pardas (p=0,152). Isso é o oposto do padrão
observado para gênero e contraria a expectativa de que relações de trabalho mais padronizadas —
associadas à formalidade — estariam associadas a menor discricionariedade salarial por raça.

Ao mesmo tempo, o gap racial bruto (-34,9% preto/pardo vs. branco) é bem maior que o condicional
(em torno de -9% a -13% entre informais) — grande parte da desigualdade racial observada em
Roraima parece operar via alocação desigual em escolaridade, ocupação e setor, não só via
diferença de preço dentro da mesma posição.

### 4.4 Setor público

Roraima tem uma economia fortemente dependente do setor público: 5.791 dos 24.414 ocupados
(23,7%) estão em posições públicas (`VD4009` ∈ {empregado público com/sem carteira, militar ou
servidor estatutário}). Isso levanta a pergunta de quanto do prêmio de formalidade reflete
especificamente esse peso do setor público.

Estendendo o modelo da amostra restrita com `setor_publico` e sua interação com `Formal`:

| Termo | Renda mensal real | Renda por hora real |
| --- | ---: | ---: |
| Formal (privado/doméstico) | +25,3%*** | +17,7%*** |
| Setor público | +30,8%*** | +26,4%*** |
| Formal × Setor público | +16,8%*** | +33,8%*** |

`***p<0,01`. Setor público e formalidade constituem **dimensões distintas e conjuntamente
associadas aos rendimentos**, não uma explicando a outra: (i) o diferencial associado a ocupar uma
posição pública é grande por si só, mesmo mantendo o
status de formalidade fixo (há informalidade dentro do setor público — 1.493 dos 5.791 postos
públicos são sem carteira); (ii) o diferencial associado à formalidade é **maior no setor público**
do que no setor privado — o efeito combinado de ser formal e público na renda por hora
(soma dos três termos, $\beta_1+\beta_7+\beta_8$) chega a aproximadamente +99% em efeito
aproximado, contra +17,7% de ser só formal (privado/doméstico). Isso significa que o grande prêmio
de formalidade documentado na Seção 4.1 **não é artefato do peso do setor público** — mas o setor
público concentra os maiores prêmios de formalidade observados na economia local.

A estrutura salarial completa por posição na ocupação (amostra ampla, condicional aos mesmos
controles, referência = privado sem carteira) confirma e detalha esse padrão:

| Posição na ocupação | Efeito condicional (renda/hora) | Renda/hora média (bruta, R$) |
| --- | ---: | ---: |
| Militar/servidor estatutário | +92,4%*** | 41,80 |
| Empregador | +90,4%*** | 35,40 |
| Público, com carteira | +32,6%*** | 24,00 |
| Público, sem carteira | +26,0%*** | 23,80 |
| Privado, com carteira | +7,8%*** | 12,00 |
| *(referência: privado, sem carteira)* | — | 11,50 |
| Conta-própria | -2,8% (ns) | 13,10 |
| Doméstico, com carteira | -48,0%*** | 8,65 |
| Doméstico, sem carteira | -55,1%*** | 8,39 |

Dois pontos chamam atenção: (i) **posições públicas sem carteira têm diferencial condicional maior
que posições privadas com carteira** (+26,0% vs. +7,8% em relação à referência) — o "setor" pesa
mais que a "carteira" nesta comparação; (ii) **trabalho doméstico é a posição com menor rendimento
condicional entre as categorias analisadas, com ou sem carteira** — ter carteira quase não altera o
rendimento bruto médio do trabalho doméstico (R$ 8,39/hora sem carteira vs. R$ 8,65/hora com
carteira, ambos muito abaixo da referência), e a diferença associada à carteira assinada não
aproxima essa categoria do patamar salarial de nenhuma outra categoria empregada; a diferença
associada à posição (natureza do trabalho doméstico) domina a diferença associada à carteira
assinada para esse grupo especificamente.

### 4.5 Interseccionalidade: prêmio de formalidade por raça e gênero

Prêmio de formalidade (renda por hora, amostra ampla) para os quatro grupos de
raça/cor × gênero de referência:

| Grupo | Prêmio de formalidade |
| --- | ---: |
| Homem branco | +34,3%*** |
| Mulher parda | +28,1%*** |
| Mulher preta | +24,9%*** |
| Mulher indígena | +18,4%*** |

O prêmio de formalidade para mulheres indígenas é quase metade do prêmio para homens brancos —
o diferencial associado à formalidade é positivo para todos os grupos, mas de forma desigual.

### 4.6 Mecanismo: efeito-preço vs. efeito-jornada

Como $\ln(renda\ mensal) = \ln(renda\ por\ hora) + \ln(horas\ semanais)$ é uma identidade
algébrica, estimar a mesma especificação para as três variáveis dependentes decompõe exatamente
(não aproximadamente) o diferencial mensal em efeito-preço e efeito-quantidade — verificado: a
soma dos coeficientes de preço e jornada reproduz o coeficiente mensal com diferença da ordem de
$10^{-15}$ (ruído de ponto flutuante) em todos os termos, nas duas amostras.

**Nota metodológica:** a identidade acima tem uma constante implícita. `renda_hora` é construída
como `renda_mensal / (horas_semanais × 4,33)`, onde 4,33 é o fator de semanas por mês — logo
$\ln(renda\ mensal) = \ln(renda\ por\ hora) + \ln(horas\ semanais) + \ln(4{,}33)$. Como
$\ln(4{,}33)$ é constante para todas as observações, ela é absorvida inteiramente pelo intercepto
do modelo e não afeta nenhum coeficiente de tratamento (`formal`, `mulher`, `raça`) — a
decomposição exata reportada abaixo vale para esses coeficientes, não para o intercepto.

| Termo | % do efeito mensal que é jornada (não preço) |
| --- | ---: |
| Mulher | 43% |
| Formal | 15% (formal trabalha **mais** horas, não menos) |
| Formal × Mulher | ~100% — é só efeito-jornada |
| Preto | 27% |
| Pardo | 23% |
| Indígena | 25% |

O gap de gênero é misto (43% jornada, 57% preço); o prêmio de formalidade e os gaps raciais são
majoritariamente efeito-preço (73-85%). A interação `Formal×Mulher`, positiva na renda mensal
(Seção 4.2), é praticamente 100% explicada por jornada — mulheres formais trabalham jornadas mais
próximas das de homens formais, mas o preço da hora entre formais não converge.

### 4.7 Evolução temporal

Inclinação linear (`termo × Ano`) na renda por hora real, 2016-2025:

| Termo | Inclinação (%/ano) | p-valor |
| --- | ---: | ---: |
| Formal | -0,31% | 0,413 (ns) |
| Mulher | -0,34% | 0,245 (ns) |
| Preto | +0,67% | 0,307 (ns) |
| Pardo | +0,96% | **0,022** |
| Indígena | +0,78% | 0,340 (ns) |

Nem o prêmio de formalidade nem o gap de gênero mostram tendência linear detectável na década —
oscilam ano a ano (ver `outputs/tables/r_tendencia_flexivel.csv` e a figura correspondente para a
série completa, ano a ano, com raça desagregada) sem direção estrutural clara. O gap racial mostra
sinal de redução ao longo do tempo, estatisticamente significativo para pessoas pardas (a maior
subcategoria racial, com mais poder estatístico); preto e indígena isoladamente têm o mesmo sinal
mas não atingem significância própria, plausivelmente por N menor em cada categoria.

## 5. Robustez

**Todos os trimestres (não só o 4º):** reestimando com os quatro trimestres de cada ano
(N=97.187, quase 4x a amostra principal) e efeitos fixos de ano×trimestre em vez de ano, os
resultados da Seção 4 se mantêm em direção e magnitude (diferenças de 1 a 4 pontos percentuais
para os termos principais, significância preservada na quase totalidade dos casos) — ver
`outputs/tables/r_robustez_trimestres.csv`.

**Período pandêmico:** reestimando em 2016-2019, 2022-2025 e no conjunto excluindo 2020-2021, o
prêmio de formalidade, o gap de gênero e os gaps raciais de pardo e indígena são estáveis nos três
recortes. O gap de pessoas pretas especificamente perde significância estatística no recorte
2022-2025 (permanece com o mesmo sinal e magnitude semelhante) — mais provável limitação de poder
estatístico numa subamostra menor (N~10 mil) do que evidência de que o gap tenha desaparecido. Ver
`outputs/tables/r_robustez_pandemia.csv`.

## 6. Cautelas de interpretação

- Estes são **diferenciais condicionais**, não efeitos causais: seleção para emprego formal, para
  ocupação/setor e para jornada permanece potencialmente endógena.
- O gap racial de pessoas pretas (isoladamente) tem menor robustez estatística em subamostras
  menores (Seção 5) — o sinal é consistente, a significância não.
- A conversão de efeitos percentuais em valores absolutos (R$) usa a renda média da amostra como
  referência — é ilustrativa, não uma previsão individual.
