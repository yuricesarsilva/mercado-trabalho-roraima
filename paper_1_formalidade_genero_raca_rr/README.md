# Paper 1: formalidade, gênero, raça/cor e renda em Roraima

## Pergunta central

Mantidas constantes a ocupação, a atividade econômica, escolaridade, idade, jornada e período, persistem diferenciais de rendimento associados à formalidade, gênero e raça/cor no mercado de trabalho de Roraima?

## Hipóteses iniciais

1. Trabalhadores formais recebem prêmio salarial positivo em relação a trabalhadores informais comparáveis.
2. Mulheres recebem menos que homens, mesmo dentro de grandes grupos ocupacionais e setoriais.
3. Pessoas pretas e pardas recebem menos que pessoas brancas, mesmo após controles observáveis.
4. A formalização pode atenuar ou ampliar os diferenciais de gênero e raça/cor.

## Estrutura

- `data/raw/`: arquivos oficiais baixados do IBGE.
- `data/interim/`: microdados extraídos e filtrados preliminarmente.
- `data/processed/`: bases analíticas prontas para estimação.
- `docs/`: plano, dicionário de variáveis e decisões metodológicas.
- `notebooks/`: exploração visual ou diagnósticos interativos.
- `outputs/tables/`: tabelas finais e diagnósticos amostrais.
- `outputs/figures/`: figuras finais.
- `outputs/models/`: resultados serializados dos modelos.
- `scripts/`: rotinas executáveis de ponta a ponta.
- `src/pnadc_rr/`: funções reutilizáveis do projeto.
- `tests/`: testes de consistência das funções.

## Pipeline previsto

```powershell
python scripts/00_download_pnadc.py --years 2024 --quarters 4
python scripts/01_build_rr_microdata.py --years 2024 --quarters 4
python scripts/02_build_analytic.py
python scripts/02_sample_audit.py
python scripts/03_estimate_baseline.py
python scripts/04_make_tables.py
python scripts/05_summarize_results.py
```

O primeiro alvo empírico é a auditoria amostral. Ela decidirá o nível máximo de desagregação viável para Roraima.

Para a especificação principal, usar quartos trimestres anuais:

```powershell
python scripts/00_download_pnadc.py --years 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 --quarters 4
python scripts/01_build_rr_microdata.py --years 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 --quarters 4
python scripts/02_build_analytic.py
python scripts/02_sample_audit.py
python scripts/03_estimate_baseline.py
python scripts/05_summarize_results.py
```
