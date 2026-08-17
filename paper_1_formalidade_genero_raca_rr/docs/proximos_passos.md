# Próximos Passos

Última atualização: 2026-08-14.

## 5. Evolução temporal dos diferenciais — concluído

`scripts/09_estimate_trends.py` estende o modelo-base de renda por hora real com interações
`formal:C(periodo)`, `mulher:C(periodo)` e `preto_pardo:C(periodo)`, permitindo que cada
diferencial varie ano a ano (2016T4-2025T4) em vez de ser constante no tempo. Também estima um
modelo de robustez com inclinação linear (`termo:Ano`) por termo. Ver `docs/evolucao_temporal.md`
para a tabela completa e `outputs/figures/tendencia_temporal.png` para o gráfico.

Achado: nenhuma das três tendências lineares é claramente forte — o prêmio de formalidade e a
penalidade de gênero por hora oscilam ano a ano sem uma direção linear significativa (formal:
-0,30 p.p./ano; mulher: -0,23 p.p./ano; ambos não significativos), enquanto o diferencial de
raça/cor mostra uma tendência de queda (em módulo) marginalmente significativa a 10%
(+0,78 p.p./ano, ou seja, a penalidade está diminuindo). Os IC 95% ano a ano são largos (amostra
de ~2-3 mil pessoas ocupadas com renda válida por ano em Roraima), então a leitura ano a ano deve
ser tratada com cautela; a inclinação linear é o resumo mais estável.

## 3. Réplica em R com `survey` (desenho amostral completo) — concluído

`r/01_replicate_survey.R` lê o microdado nacional de cada trimestre (2016T4-2025T4) diretamente com
`PNADcIBGE::read_pnadc()`, filtra para Roraima e declara **um único** `svrepdesign` (bootstrap, 200
réplicas oficiais do IBGE) empilhando os 10 anos — validado empiricamente que todos usam o mesmo
esquema de pesos e que o peso final coincide exatamente com `V1028` (já usado em Python). Ver
`docs/replicacao_r_survey.md` para a comparação completa.

Achado: coeficientes idênticos ao WLS em Python (~1e-14 de diferença); erros-padrão do desenho
bootstrap oficial sistematicamente menores que os do erro clusterizado por UPA (Taylor sobre peso
pós-estratificado é conservador) — sem mudar a significância dos termos principais.

## 4. Identificação causal — pendente (discutido, não implementado)

Registrado a partir de uma pergunta sobre usar GMM: GMM não ajuda sem instrumentos, e não há
instrumento óbvio para `formal` (e instrumentar `mulher`/`preto_pardo` não faz sentido — a
preocupação ali é variável omitida/alocação não aleatória entre ocupações, não simultaneidade).
Alternativas mais promissoras, em ordem de custo/benefício, se o objetivo for fortalecer a
identificação causal:

1. Efeito fixo de indivíduo explorando o painel rotativo da PNAD-C (5 trimestres por domicílio) —
   comparar o mesmo trabalhador antes/depois de mudar de formal para informal.
2. Decomposição de Oaxaca-Blinder, complementar à regressão com interações.
3. Heckman em duas etapas para a seleção em emprego formal.
4. GMM-IV, só se surgir um instrumento defensável para `formal`.

## 1. Deflacionar rendimentos — concluído

`scripts/00_download_pnadc.py` agora baixa `Deflatores.zip` (IBGE, pasta `Microdados/Documentacao/`) e
`src/pnadc_rr/deflator.py` lê a aba `deflator`, filtra Roraima (`UF=14`) e mapeia os trimestres móveis
`01-02-03`/`04-05-06`/`07-08-09`/`10-11-12` para `Trimestre` 1-4. `scripts/02_build_analytic.py` faz o merge
por `Ano`/`Trimestre` e cria:

- `renda_mensal_real`;
- `renda_hora_real`;
- `ln_renda_mensal_real`;
- `ln_renda_hora_real`.

`scripts/03_estimate_baseline.py` agora estima os modelos principais com rendimento real; os modelos em
valores nominais (`ln_renda_hora`, `ln_renda_mensal`) continuam sendo gerados apenas como comparação/robustez.
Pipeline completo já rodado (`00` a `05`); `outputs/` e `docs/resumo_resultados_correntes.md` refletem os
coeficientes deflacionados.

Nota: como o modelo-base já inclui efeitos fixos de ano/trimestre (`C(periodo)`), os coeficientes de
`formal`, `mulher`, `preto_pardo` e suas interações saem numericamente idênticos entre os modelos nominal e
real (diferença de ponto flutuante, ~1e-14) — apenas a constante e os próprios efeitos fixos de período
absorvem o ajuste de preços. Isso é esperado, não um erro: o deflator só varia por ano/trimestre, então seu
efeito é inteiramente capturado pelas dummies de período. A deflação continua sendo necessária para (a)
descrever/plotar a evolução do nível de renda ao longo do tempo e (b) qualquer especificação que não sature
os efeitos fixos de período (por exemplo, robustez com trimestres empilhados sem `C(periodo)` completo, ou
comparações de nível entre anos específicos).

## 2. Explorar jornada de trabalho — concluído

`scripts/06_estimate_jornada.py` estima, na mesma amostra (renda mensal real e horas semanais habituais
válidas), os quatro modelos da estratégia sugerida:

1. `ln(renda mensal real)` sem controlar por horas (reestimado na amostra do mecanismo, para comparabilidade).
2. `ln(renda mensal real)` controlando por horas (`modelo_base_ln_renda_mensal_real_com_horas`).
3. `ln(renda hora real)` (reestimado na amostra do mecanismo).
4. `horas semanais habituais` como variável dependente (`modelo_base_horas_semanais`; coeficientes em
   horas/semana, não em log — a coluna `efeito_percentual_aprox` não se aplica a este modelo, apenas
   `efeito_absoluto_aprox`/`coeficiente`).

O comparativo e a interpretação ficam em `docs/mecanismo_jornada.md`. Resultado central: para mulheres, o
gap mensal real cai de -28,5% (sem horas) para -22,0% (com horas), o gap por hora é -14,1%, e mulheres
trabalham em média 4,73 horas/semana a menos — ou seja, o diferencial de gênero é parcialmente efeito-preço
(remuneração por hora menor) e parcialmente efeito-quantidade (jornadas mais curtas). Para raça/cor o padrão
é qualitativamente parecido, mas de magnitude bem menor. Manteve-se a ressalva do plano: horas não entram
como controle no modelo-base principal (`03_estimate_baseline.py`), só nesta análise de mecanismo.
