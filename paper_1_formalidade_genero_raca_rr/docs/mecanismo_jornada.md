# Mecanismo de Jornada: Preço do Trabalho vs. Horas Trabalhadas

Este arquivo é gerado por `scripts/06_estimate_jornada.py` e decompõe os diferenciais de rendimento mensal real em efeito-preço (renda por hora) e efeito-quantidade (horas semanais). Todos os modelos usam a mesma amostra: pessoas ocupadas com renda mensal real e horas semanais habituais válidas (`>0`), com os mesmos controles do modelo-base (idade, idade², escolaridade, ocupação, atividade e efeitos fixos de ano/trimestre).

## Comparação dos Coeficientes-Chave

| termo | ln_renda_mensal_real | ln_renda_mensal_real_com_horas | ln_renda_hora_real | horas_semanais |
| --- | --- | --- | --- | --- |
| formal | +42.4% (significativo a 1%) | +37.0% (significativo a 1%) | +32.7% (significativo a 1%) | +2.10 h/sem (significativo a 1%) |
| mulher | -28.5% (significativo a 1%) | -22.0% (significativo a 1%) | -14.1% (significativo a 1%) | -4.73 h/sem (significativo a 1%) |
| preto_pardo | -9.2% (significativo a 1%) | -7.8% (significativo a 1%) | -6.1% (significativo a 1%) | -0.87 h/sem (significativo a 1%) |
| formal:mulher | +14.8% (significativo a 1%) | +7.4% (significativo a 1%) | -1.4% (não significativo aos níveis usuais) | +3.65 h/sem (significativo a 1%) |
| formal:preto_pardo | -1.6% (não significativo aos níveis usuais) | -2.2% (não significativo aos níveis usuais) | -3.6% (não significativo aos níveis usuais) | +0.33 h/sem (não significativo aos níveis usuais) |

## Interpretação

- Para a formalidade, em relação à informalidade: o diferencial de renda mensal real é +42.4% sem controlar por horas e +37.0% controlando por horas; o diferencial de renda por hora real é +32.7%; e a diferença nas horas semanais habituais é +2.10 horas/semana (significativo a 1%).
- Para ser mulher, em relação a ser homem: o diferencial de renda mensal real é -28.5% sem controlar por horas e -22.0% controlando por horas; o diferencial de renda por hora real é -14.1%; e a diferença nas horas semanais habituais é -4.73 horas/semana (significativo a 1%).
- Para ser pessoa preta ou parda, em relação aos demais grupos de raça/cor: o diferencial de renda mensal real é -9.2% sem controlar por horas e -7.8% controlando por horas; o diferencial de renda por hora real é -6.1%; e a diferença nas horas semanais habituais é -0.87 horas/semana (significativo a 1%).

- Leitura: se o efeito de renda mensal muda pouco entre `sem controle de horas` e `com controle de horas`, e se aproxima do efeito de renda por hora, o diferencial é majoritariamente um efeito-preço (o grupo ganha menos por hora trabalhada). Se o efeito de horas semanais é grande e estatisticamente significativo, parte do diferencial de renda mensal decorre de jornadas mais curtas (efeito-quantidade), não apenas do preço do trabalho.
