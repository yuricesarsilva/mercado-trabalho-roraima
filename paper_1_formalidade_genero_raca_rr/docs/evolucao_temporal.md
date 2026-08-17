# Evolução Temporal dos Diferenciais (2016T4-2025T4)

Este arquivo é gerado por `scripts/09_estimate_trends.py`. Parte do modelo-base (log do rendimento por hora real, mesmos controles de `03_estimate_baseline.py`) e adiciona interações `formal:C(periodo)`, `mulher:C(periodo)` e `preto_pardo:C(periodo)`, permitindo que cada diferencial varie livremente ano a ano em vez de ser constante no tempo. O coeficiente de cada ano é a soma do termo-base (ano de referência, 2016T4) com a interação correspondente; o erro-padrão usa a covariância completa (`var(a+b) = var(a) + var(b) + 2·cov(a,b)`), com erros clusterizados por UPA.

## Efeito Percentual Aproximado por Ano

| ano | termo | efeito_percentual_aprox | ic95_inf | ic95_sup | p_valor |
| --- | --- | --- | --- | --- | --- |
| 2016 | formal | 25.73 | 16.19 | 36.06 | 0.00 |
| 2017 | formal | 30.05 | 20.14 | 40.77 | 0.00 |
| 2018 | formal | 42.98 | 32.44 | 54.37 | 0.00 |
| 2019 | formal | 45.93 | 33.74 | 59.24 | 0.00 |
| 2020 | formal | 30.35 | 20.27 | 41.27 | 0.00 |
| 2021 | formal | 32.61 | 16.64 | 50.77 | 0.00 |
| 2022 | formal | 27.09 | 15.64 | 39.67 | 0.00 |
| 2023 | formal | 31.59 | 19.22 | 45.25 | 0.00 |
| 2024 | formal | 32.85 | 22.93 | 43.57 | 0.00 |
| 2025 | formal | 29.65 | 19.49 | 40.67 | 0.00 |
| 2016 | mulher | -13.68 | -18.77 | -8.27 | 0.00 |
| 2017 | mulher | -14.81 | -20.16 | -9.09 | 0.00 |
| 2018 | mulher | -9.14 | -14.48 | -3.47 | 0.00 |
| 2019 | mulher | -15.09 | -19.75 | -10.16 | 0.00 |
| 2020 | mulher | -14.52 | -20.67 | -7.89 | 0.00 |
| 2021 | mulher | -12.25 | -18.06 | -6.03 | 0.00 |
| 2022 | mulher | -16.07 | -20.69 | -11.18 | 0.00 |
| 2023 | mulher | -14.79 | -19.52 | -9.78 | 0.00 |
| 2024 | mulher | -16.01 | -19.98 | -11.85 | 0.00 |
| 2025 | mulher | -13.50 | -18.41 | -8.29 | 0.00 |
| 2016 | preto_pardo | -13.22 | -18.66 | -7.41 | 0.00 |
| 2017 | preto_pardo | -3.32 | -10.43 | 4.35 | 0.39 |
| 2018 | preto_pardo | -5.93 | -13.00 | 1.72 | 0.13 |
| 2019 | preto_pardo | -5.49 | -13.18 | 2.87 | 0.19 |
| 2020 | preto_pardo | -9.16 | -17.34 | -0.16 | 0.05 |
| 2021 | preto_pardo | -13.91 | -25.61 | -0.38 | 0.04 |
| 2022 | preto_pardo | -3.07 | -11.03 | 5.59 | 0.48 |
| 2023 | preto_pardo | -4.15 | -9.75 | 1.81 | 0.17 |
| 2024 | preto_pardo | -2.14 | -8.60 | 4.77 | 0.53 |
| 2025 | preto_pardo | -2.79 | -9.04 | 3.90 | 0.41 |

## Tendência Linear (robustez)

Modelo alternativo com uma única inclinação `termo:Ano` (contínuo) por termo, resumindo a direção e a magnitude média da tendência em um número — não captura reversões ano a ano, só a direção geral.

- **formal**: a tendência linear é diminuindo em -0.30 pontos percentuais aproximados por ano (não significativo aos níveis usuais).
- **mulher**: a tendência linear é diminuindo em -0.23 pontos percentuais aproximados por ano (não significativo aos níveis usuais).
- **preto_pardo**: a tendência linear é aumentando em +0.78 pontos percentuais aproximados por ano (significativo a 10%).

## Figura

`outputs/figures/tendencia_temporal.png` — pequenos múltiplos com IC 95% por termo.

## Leitura

- Estes coeficientes ainda são diferenciais condicionais (mesmos controles do modelo-base: ocupação, atividade, escolaridade, idade e idade²), não efeitos causais.
- Com uma amostra de ~2 a 3 mil observações por ano em Roraima, os IC 95% ano a ano tendem a ser largos — a tendência linear é o resumo mais estável para dizer se um prêmio/penalidade está estruturalmente aumentando ou diminuindo; o gráfico ano a ano serve para checar se essa tendência é consistente ou dominada por um ou dois anos atípicos (ex.: pandemia).
