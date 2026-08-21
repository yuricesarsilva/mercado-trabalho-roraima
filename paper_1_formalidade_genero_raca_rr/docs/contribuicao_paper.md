# Contribuição do artigo

## Frase de contribuição

**Versão curta (espinha dorsal — introdução/conclusão):**

> O artigo mostra que, em Roraima, diferentes desigualdades são produzidas por estruturas distintas: a vantagem educacional feminina mascara o gap de gênero, a desvantagem educacional amplia o gap racial bruto, e a maior magnitude dos diferenciais raciais está concentrada no setor público — tanto entre trabalhadores formais quanto informais.

**Versão estendida (para desenvolvimento no corpo do texto):**

> Em um mercado de trabalho periférico e fortemente estatal como o de Roraima, os diferenciais de rendimento associados a formalidade, gênero e raça/cor operam por **mecanismos de composição distintos**: a escolaridade **oculta** o hiato de gênero — estatisticamente nulo em termos brutos, mas de cerca de -17% quando comparamos trabalhadores com a mesma escolaridade, ocupação e setor — enquanto **explica apenas parte** do hiato racial, que permanece grande e significativo (entre -10% e -14%) mesmo após o conjunto completo de controles; a desigualdade racial condicional é substancialmente maior no setor público do que no privado (diferença de 13 a 20 pontos percentuais entre os grupos de cor/raça, presente tanto entre formais quanto informais); e a penalidade combinada de ser mulher indígena é **menor** do que a soma das penalidades isoladas de gênero e de raça sugeriria — um padrão que se afasta da desvantagem composta reportada na literatura internacional sobre mulheres indígenas.

*Nota de precisão sobre "a desvantagem educacional amplia o gap racial bruto": grupos não-brancos têm, em média, menos escolaridade; essa diferença de composição contribui para abrir o hiato observado sem controles (bruto: preto -30,0%, pardo -26,8%, indígena -39,7%). Ao equalizar estatisticamente a escolaridade (e demais controles), o hiato cai bastante mas não desaparece (condicional: -11% a -14% após M6). Ou seja, a escolaridade **explica parte, não a maioria persistente, e não amplia o coeficiente condicional** — amplia é a leitura do hiato bruto em relação ao que seria observado com escolaridade equalizada.

Números de referência (conferidos em `outputs/tables/r_decomposicao_genero.csv`, `r_decomposicao_raca.csv`, `r_raca_setor_publico_contrastes_ln_renda_hora_real.csv` e `r_interseccionalidade_genero_raca.csv`):

- **Gênero**: hiato bruto M0 = +3,3% (não indica desvantagem; se torna negativo assim que entra escolaridade). Hiato condicional completo (M7) = -18,2%. A guinada ocorre inteira em M2 (+educação): -16,4%.
- **Raça**: hiato bruto M0 = preto -30,0%, pardo -26,8%, indígena -39,7%. Após educação (M2): -13,3%, -12,2%, -18,7%. Do M2 ao M6 (setor público) o hiato muda pouco — a educação absorve a maior parte do que vai ser absorvido, mas um resíduo grande e significativo permanece.
- **Setor público × raça** (diferença público−privado, condicional): preto -18,4 p.p., pardo -12,9 p.p., indígena -20,4 p.p. (todos p < 0,0001).
- **Interação mulher×raça** (heterogeneidade além do aditivo, ln renda-hora): indígena +12,3% (p = 0,004, IC95% [3,7%; 21,6%]) — a única das três interações estatisticamente significativa. Preto +5,4% (p = 0,18) e pardo +4,3% (p = 0,10) apontam na mesma direção mas não são significativas isoladamente.
- **Mecanismo jornada (`Formal×Mulher`)**: renda mensal +13,8% (p<0,001); renda-hora -1,4% (p=0,53, nulo); horas semanais +3,65h/semana (p<0,001). O "prêmio" de formalidade para mulheres na renda mensal é inteiramente explicado por jornada, não por valor-hora — precisa aparecer no corpo para não sugerir um prêmio salarial que não existe.
- **Acesso à formalidade (AME de P(Formal=1))**: gaps de gênero e raça estatisticamente nulos nas duas amostras (p entre 0,21 e 0,73 em todos os termos, amostra ampla e restrita). Sustenta que os hiatos de renda documentados não refletem seleção diferencial para o emprego formal — vale uma frase e uma linha de tabela no corpo, não apenas o apêndice.

## Contribuição vs. resultado

Os números acima são **resultados**. A **contribuição** do artigo é o que esses resultados, tomados em conjunto, acrescentam ao que já se sabia:

1. **Estuda um mercado de trabalho regional pouco investigado.** Roraima combina alta participação do setor público, fronteira internacional (migração venezuelana) e presença indígena expressiva — uma combinação que a literatura de formalidade/gênero/raça, concentrada em regiões metropolitanas do Centro-Sul, não cobre. Moriconi et al. (2009) já haviam sinalizado um diferencial público/privado atípico em Roraima há mais de uma década; o artigo atualiza e aprofunda esse achado com dados recentes e desenho amostral correto (bootstrap replicado).
2. **Mostra que gênero e raça não operam pelo mesmo mecanismo de composição.** Não é "o mesmo resultado com números diferentes": para gênero, controlar por escolaridade *revela* um hiato que a composição escondia (mulheres mais escolarizadas, mas o retorno não compensa a penalidade condicional, e o "prêmio" mensal da formalidade para mulheres é efeito de jornada, não de valor-hora); para raça, controlar por escolaridade *absorve* boa parte do hiato bruto, mas não o elimina. São histórias diferentes sobre como a composição observável se relaciona com a desigualdade salarial.
3. **Trata indígenas como grupo racial próprio, não agregado a "outros".** Isso permite estimar diretamente o hiato indígena e sua interação com gênero — raro na literatura brasileira. O achado de uma interação mulher×indígena positiva e significativa dialoga diretamente com (e se afasta de) Kolev & Robles (2015), que reportam desvantagem composta para mulheres indígenas na América Latina.
4. **Revela a centralidade do setor público na heterogeneidade racial.** Não é um achado óbvio a priori: a literatura de segregação (ex. Cardoso et al., 2025) discute segregação horizontal/vertical de forma geral, sem apontar o setor público como o locus específico onde a desigualdade racial condicional se concentra em um mercado como o de Roraima — e o achado vale tanto entre formais quanto informais.

**O que a contribuição não é**: não é "estimamos gaps de formalidade/gênero/raça para Roraima" — isso é o resultado. A contribuição é o argumento de que esses gaps têm origens (mecanismos) diferentes entre si, e que o setor público — a característica mais distintiva do mercado de trabalho local — é onde a desigualdade racial condicional se manifesta com mais força.

## Organização dos resultados em 3 blocos (evita "catálogo de regressões")

O artigo não deve ter seis achados independentes soltos; devem ser três grandes blocos, cada um com subresultados:

1. **Formalidade e estrutura do mercado**: prêmio de rendimento associado à formalidade (M4) + acesso à formalidade não é diferencial por gênero/raça (AME nulo — bridging paragraph, não pertence a gênero nem a raça especificamente, serve de premissa antes dos dois blocos seguintes) + papel peculiar do setor público no mercado local.
2. **Gênero**: hiato bruto mascarado pela escolaridade (M0→M7) + formalidade não reduz o hiato de valor-hora (`Formal×Mulher` nulo em renda-hora) + jornada explica a diferença observada na renda mensal (`Formal×Mulher` positivo e grande em horas semanais).
3. **Raça/cor**: escolaridade amplia o hiato bruto observado, mas não elimina o hiato condicional (M0→M6) + formalidade não elimina o hiato racial + magnitude maior no setor público (formal e informal) + especificidade indígena via interação mulher×raça.

O resultado de acesso à formalidade (item 1) funciona melhor como parágrafo de abertura da seção de Resultados — antes dos blocos de gênero e raça — do que encaixado dentro de um dos dois, porque sua função é de premissa metodológica (os hiatos não refletem seleção diferencial), não de achado substantivo por grupo.
