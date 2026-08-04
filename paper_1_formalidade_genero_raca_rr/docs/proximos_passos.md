# Próximos Passos

Última atualização: 2026-08-04.

## 1. Deflacionar rendimentos

Os resultados correntes ainda usam `VD4016` em valores nominais. Antes de interpretar a série `2016T4-2025T4` como resultado final, incorporar os deflatores oficiais da PNAD Contínua e criar:

- `renda_mensal_real`;
- `renda_hora_real`;
- `ln_renda_mensal_real`;
- `ln_renda_hora_real`.

Depois disso, os modelos principais devem usar os rendimentos reais.

## 2. Explorar jornada de trabalho

Incluir jornada de trabalho pode ajudar a separar três dimensões:

- diferencial total no rendimento mensal;
- diferencial no rendimento por hora;
- diferencial na quantidade de horas trabalhadas.

Estratégia sugerida:

1. Estimar `ln(renda mensal real)` sem controlar por horas.
2. Estimar `ln(renda mensal real)` controlando por horas.
3. Estimar `ln(renda hora real)`.
4. Estimar `horas semanais` como variável dependente.

Essa estrutura permite avaliar se o gap de gênero, raça/cor e formalidade decorre de diferenças no preço do trabalho, na jornada, ou nos dois.

Ressalva: horas trabalhadas não devem entrar automaticamente como controle principal no modelo de renda mensal, porque jornada pode ser mecanismo do próprio diferencial de rendimento.
