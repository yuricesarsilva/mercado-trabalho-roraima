# Plano do Paper 1

## 1. Objetivo

Estimar diferenciais condicionais de rendimento por formalidade, gênero e raça/cor no mercado de trabalho de Roraima, usando microdados individuais da PNAD Contínua.

## 2. Perguntas de pesquisa

1. Qual é o diferencial de rendimento entre trabalhadores formais e informais em Roraima?
2. Quanto dos diferenciais de rendimento por gênero e raça/cor persiste quando controlamos por ocupação, atividade econômica, escolaridade, idade, jornada e tempo?
3. A formalização atenua ou amplia os diferenciais salariais de gênero e raça/cor?
4. O resultado muda quando usamos rendimento mensal versus rendimento por hora?

## 3. Base de dados

Fonte: PNAD Contínua trimestral, microdados oficiais do IBGE.

Unidade de análise: indivíduo ocupado em Roraima.

Período inicial recomendado:

- diagnóstico rápido: 2024, 4º trimestre;
- base principal: 2016-2025 ou 2012-2025, após auditoria de compatibilidade das variáveis.

## 4. Variáveis

Dependentes:

- log do rendimento habitual mensal do trabalho principal;
- log do rendimento habitual por hora do trabalho principal.

Tratamentos/interesses:

- formalidade;
- mulher;
- raça/cor, inicialmente branco versus preto/pardo;
- interações entre formalidade e mulher;
- interações entre formalidade e raça/cor.

Controles:

- idade;
- idade ao quadrado;
- escolaridade;
- horas trabalhadas;
- posição na ocupação, quando não for usada para construir formalidade;
- efeitos fixos de ocupação;
- efeitos fixos de atividade econômica;
- efeitos fixos de ano/trimestre.

## 5. Auditoria amostral

Antes dos modelos, contar para Roraima:

- total de pessoas;
- pessoas de 14 anos ou mais;
- ocupados;
- ocupados com rendimento válido;
- formais e informais;
- homens e mulheres;
- brancos, pretos, pardos, indígenas e amarelos;
- atividade econômica;
- ocupação;
- atividade por formalidade;
- ocupação por formalidade;
- formalidade por gênero e raça/cor;
- ocupação por formalidade, gênero e raça/cor.

Também registrar, quando disponível, quantidade de UPA/PSU por célula.

## 6. Modelo-base

```text
ln(w_it) =
  beta_1 formal_it
  + beta_2 mulher_i
  + beta_3 preto_pardo_i
  + beta_4 formal_it * mulher_i
  + beta_5 formal_it * preto_pardo_i
  + X_it gamma
  + FE_ocupacao
  + FE_atividade
  + FE_tempo
  + erro_it
```

`w_it` será estimado como rendimento mensal e rendimento por hora.

## 7. Inferência

A PNAD-C tem desenho amostral complexo. A inferência deve considerar pesos, estratos e conglomerados. Como primeira aproximação operacional em Python, usar WLS com pesos e erros-padrão clusterizados por UPA quando as variáveis de desenho estiverem disponíveis. Em etapa posterior, replicar as estimativas principais em R com `survey` caso R esteja disponível no ambiente.

## 8. Produtos

1. Tabela de auditoria amostral.
2. Tabela de estatísticas descritivas.
3. Tabelas de modelos para renda mensal.
4. Tabelas de modelos para renda/hora.
5. Figuras com diferenciais ajustados por grupo.
6. Apêndice de robustez por período e por agregação ocupacional/setorial.

## 9. Critérios de decisão

O paper 1 avança se a auditoria mostrar amostra suficiente para:

- formal versus informal;
- homem versus mulher;
- branco versus preto/pardo;
- grandes grupos de atividade;
- grandes grupos ocupacionais;
- interações principais entre formalidade, gênero e raça/cor.

Se células muito finas forem instáveis, elas serão usadas apenas de forma descritiva ou agrupadas.
