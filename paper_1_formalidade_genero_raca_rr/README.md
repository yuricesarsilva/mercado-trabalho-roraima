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
- `presentation/`: slides Beamer (`apresentacao.tex`) e `presentation/gerado/`, com tabelas e macros
  gerados automaticamente a partir de `outputs/`.
- `r/`: réplica das estimativas principais em R com o pacote `survey` (desenho amostral oficial).
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
python scripts/06_estimate_jornada.py
python scripts/07_estimate_robustness.py
python scripts/08_make_presentation_assets.py
```

`00_download_pnadc.py` também baixa o deflator oficial trimestral da PNAD Contínua (IBGE), usado em
`02_build_analytic.py` para gerar `renda_mensal_real`/`renda_hora_real`. Os modelos principais em
`03_estimate_baseline.py` usam rendimento real; `06_estimate_jornada.py` decompõe os diferenciais de
renda mensal em efeito-preço (renda por hora) e efeito-quantidade (horas semanais);
`07_estimate_robustness.py` reestima os modelos principais sem nenhum controle, para comparação de
robustez. `08_make_presentation_assets.py` lê todos esses resultados e gera as figuras
(`outputs/figures/`) e as tabelas/macros LaTeX (`presentation/gerado/`) usadas pelos slides.

### Gerar os slides (Beamer)

Depois de rodar o pipeline acima, compile a apresentação:

```powershell
cd presentation
pdflatex apresentacao.tex
pdflatex apresentacao.tex  # segunda passada, para sumário e numeração
```

O PDF (`presentation/apresentacao.pdf`) e as figuras/tabelas em `presentation/gerado/` e
`outputs/figures/` são inteiramente regenerados a partir dos dados — nenhum número é digitado à mão
nos slides.

### Réplica em R (desenho amostral completo)

Requer R (>= 4.2) com os pacotes `PNADcIBGE`, `survey`, `readxl`, `dplyr` e `tibble`. Lê o microdado
nacional diretamente dos arquivos já baixados por `00_download_pnadc.py` (não precisa rodar o
restante do pipeline Python antes, exceto pelo deflator, também baixado por aquele script):

```powershell
Rscript r/01_replicate_survey.R
```

Usa os pesos de replicação bootstrap oficiais da PNAD-C (200 réplicas) em vez da aproximação por
erro clusterizado por UPA usada em `03_estimate_baseline.py`. Ver `docs/replicacao_r_survey.md` para
a comparação dos resultados entre os dois métodos.
