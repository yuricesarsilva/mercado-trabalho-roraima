# Execução piloto: PNAD-C 2024T4

Data da execução: 2026-08-04.

## Arquivos oficiais usados

- Microdados: `PNADC_042024_20250815.zip`, baixado do FTP do IBGE.
- Layout: `Dicionario_e_input_20221031.zip`, baixado do FTP do IBGE.

Os arquivos brutos não são versionados no Git por tamanho e reprodutibilidade.

## Auditoria amostral inicial

Filtro: Roraima (`UF = 14`), pessoas ocupadas de 14 anos ou mais.

- Pessoas na amostra de Roraima: 5.756.
- Pessoas com 14 anos ou mais: 4.377.
- Ocupados: 2.524.
- Ocupados com rendimento válido: 2.499.
- Ocupados classificados como informais: 1.410.
- Ocupados classificados como formais: 1.114.

## Células principais

Contagem por formalidade, gênero e raça/cor agregada:

| formal | mulher | preto/pardo | n |
| --- | --- | --- | ---: |
| 0 | 0 | 1 | 683 |
| 1 | 0 | 1 | 431 |
| 0 | 1 | 1 | 376 |
| 1 | 1 | 1 | 369 |
| 0 | 0 | 0 | 209 |
| 1 | 0 | 0 | 162 |
| 1 | 1 | 0 | 152 |
| 0 | 1 | 0 | 142 |

## Regressão de fumaça

Modelo piloto: WLS para `ln_renda_hora`, com peso amostral, erros clusterizados por UPA, controles de idade, idade ao quadrado, escolaridade, ocupação, atividade e período.

Coeficientes-chave do piloto:

| variável | coeficiente | p-valor |
| --- | ---: | ---: |
| formal | 0,233 | 0,001 |
| mulher | -0,148 | 0,000 |
| preto_pardo | -0,074 | 0,102 |
| formal × mulher | -0,087 | 0,112 |
| formal × preto/pardo | 0,063 | 0,258 |

Esses coeficientes não devem ser interpretados como resultado final. Eles validam a esteira de dados e indicam que o modelo é estimável mesmo em um único trimestre.

## Próxima decisão

Baixar e empilhar múltiplos anos/trimestres para estabilizar as interações e permitir especificações com efeitos fixos mais ricos.

Após revisão do desenho, a especificação principal do paper deve usar o 4º trimestre de cada ano. O empilhamento de todos os trimestres fica reservado para teste de robustez.
