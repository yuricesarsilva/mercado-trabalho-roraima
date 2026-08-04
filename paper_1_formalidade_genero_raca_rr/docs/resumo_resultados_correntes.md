# Resumo dos Resultados Correntes

Este arquivo é gerado a partir das tabelas em `outputs/tables/`.

## Auditoria Amostral

| tabela | n_total | n_14_mais | n_ocupados | n_ocupados_renda_valida |
| --- | --- | --- | --- | --- |
| totais | 59630 | 45013 | 24414 | 23938 |

## Formalidade

| tabela | formal | n_amostral | n_upa |
| --- | --- | --- | --- |
| formalidade | 0.0 | 13282 | 405 |
| formalidade | 1.0 | 11132 | 395 |

## Formalidade, Gênero e Raça/Cor

| tabela | formal | mulher | preto_pardo | n_amostral | n_upa |
| --- | --- | --- | --- | --- | --- |
| formalidade_genero_raca | 0.0 | 0 | 1 | 6450 | 399 |
| formalidade_genero_raca | 1.0 | 0 | 1 | 4468 | 376 |
| formalidade_genero_raca | 1.0 | 1 | 1 | 3639 | 373 |
| formalidade_genero_raca | 0.0 | 1 | 1 | 3582 | 381 |
| formalidade_genero_raca | 0.0 | 0 | 0 | 1963 | 358 |
| formalidade_genero_raca | 1.0 | 0 | 0 | 1561 | 312 |
| formalidade_genero_raca | 1.0 | 1 | 0 | 1464 | 296 |
| formalidade_genero_raca | 0.0 | 1 | 0 | 1287 | 323 |

## Coeficientes-Chave

| variavel | rotulo | referencia | modelo | coeficiente | erro_padrao | p_valor | efeito_percentual_aprox |
| --- | --- | --- | --- | --- | --- | --- | --- |
| formal | Trabalhador formal | Referência: trabalhador informal | ln_renda_hora | 0.2832 | 0.0306 | 0.0000 | 32.7314 |
| mulher | Mulher | Referência: homem | ln_renda_hora | -0.1523 | 0.0175 | 0.0000 | -14.1246 |
| preto_pardo | Pessoa preta ou parda | Referência: branco, amarelo ou indígena | ln_renda_hora | -0.0626 | 0.0189 | 0.0010 | -6.0659 |
| formal:mulher | Trabalhador formal x mulher | Diferença adicional para mulheres formais | ln_renda_hora | -0.0139 | 0.0219 | 0.5265 | -1.3773 |
| formal:preto_pardo | Trabalhador formal x pessoa preta ou parda | Diferença adicional para pessoas pretas/pardas formais | ln_renda_hora | -0.0362 | 0.0254 | 0.1554 | -3.5506 |
| formal | Trabalhador formal | Referência: trabalhador informal | ln_renda_mensal | 0.3532 | 0.0302 | 0.0000 | 42.3663 |
| mulher | Mulher | Referência: homem | ln_renda_mensal | -0.3350 | 0.0189 | 0.0000 | -28.4634 |
| preto_pardo | Pessoa preta ou parda | Referência: branco, amarelo ou indígena | ln_renda_mensal | -0.0968 | 0.0208 | 0.0000 | -9.2223 |
| formal:mulher | Trabalhador formal x mulher | Diferença adicional para mulheres formais | ln_renda_mensal | 0.1380 | 0.0224 | 0.0000 | 14.7988 |
| formal:preto_pardo | Trabalhador formal x pessoa preta ou parda | Diferença adicional para pessoas pretas/pardas formais | ln_renda_mensal | -0.0161 | 0.0263 | 0.5414 | -1.5927 |

## Interpretação Sintética

A interpretação abaixo resume a execução corrente do pipeline. Ela não substitui a especificação final do paper.

- No modelo de ln renda hora, para a formalidade, em relação à informalidade, observa-se rendimento 32.7% maior, e o coeficiente é estatisticamente diferente de zero ao nível de 1%.
- No modelo de ln renda hora, para ser mulher, em relação a ser homem, observa-se rendimento 14.1% menor, e o coeficiente é estatisticamente diferente de zero ao nível de 1%.
- No modelo de ln renda hora, para ser pessoa preta ou parda, em relação aos demais grupos de raça/cor, observa-se rendimento 6.1% menor, e o coeficiente é estatisticamente diferente de zero ao nível de 1%.
- No modelo de ln renda mensal, para ser mulher, quando a variável dependente é rendimento mensal, observa-se rendimento 28.5% menor, e o coeficiente é estatisticamente diferente de zero ao nível de 1%.
- A diferença entre os modelos de rendimento mensal e rendimento por hora é substantiva: quando usamos renda mensal, parte do diferencial de gênero também reflete diferenças de jornada; quando usamos renda por hora, a comparação se aproxima mais do preço do trabalho.
- Estes resultados ainda devem ser lidos como diferenciais condicionais, não como efeitos causais. Eles controlam por ocupação, atividade, escolaridade, idade e período, mas a seleção para o emprego formal continua potencialmente endógena.

## Próximos Ajustes

- Deflacionar os rendimentos antes de tratar os resultados de `2016T4-2025T4` como finais.
- Explorar jornada de trabalho como mecanismo, estimando modelos para renda mensal, renda mensal com controle de horas, renda por hora e horas semanais.
