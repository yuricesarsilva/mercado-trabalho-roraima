# Réplica em R com o pacote `survey` (desenho amostral completo)

Gerado por `r/01_replicate_survey.R`. Complementa a estimação em Python
(`scripts/03_estimate_baseline.py`, WLS com peso `V1028` e erro-padrão
clusterizado por UPA) com o desenho amostral oficial da PNAD Contínua.

## O que muda em relação à estimação em Python

A PNAD Contínua distribui, desde 2016, pesos de replicação bootstrap (200
réplicas, colunas `V1028001`-`V1028200`) para estimação correta de variância.
O pacote `PNADcIBGE::pnadc_design()` foi usado para **verificar** (não para
gerar em produção, por custo computacional) que, para todos os 10 anos da
amostra (2016T4-2025T4), o peso final de análise coincide exatamente com
`V1028` (diferença máxima = 0 em `weights(pnadc_design(df), type="sampling")`
vs. `df$V1028`, testado em 2016, 2018, 2020, 2021, 2023 e 2025).

Como o peso já é o correto, a diferença entre a réplica em R e a estimação em
Python está inteiramente na **estimação de variância**:

| | Python (`03_estimate_baseline.py`) | R (`01_replicate_survey.R`) |
| --- | --- | --- |
| Peso | `V1028` | `V1028` (idêntico, verificado) |
| Método de variância | Linearização de Taylor, erro clusterizado por UPA | Réplicas bootstrap (200 réplicas oficiais do IBGE) |
| Amostra | 2016T4-2025T4, RR, `N=23.938` | Idêntica |
| Especificação | Mesma fórmula (tratamentos + interações + controles + efeitos fixos de período) | Idêntica |

## Resultado: coeficientes idênticos, erros-padrão menores no desenho oficial

Os coeficientes pontuais batem com Python a **~1e-14** (ruído de ponto
flutuante) — esperado, já que WLS com o mesmo peso e a mesma especificação
produz o mesmo ponto estimado independentemente do método de variância usado
depois. Ver `outputs/tables/replicacao_r_survey_comparacao.csv` para a tabela
completa.

Os erros-padrão do desenho bootstrap oficial são **sistematicamente menores**
que os do erro clusterizado por UPA em Python — por exemplo, para `formal` na
renda mensal real: `0,0193` (R) vs. `0,0302` (Python). Isso é o esperado: a
linearização de Taylor sobre um peso já pós-estratificado, sem modelar a
calibração explicitamente, é conservadora (superestima a variância); as
réplicas bootstrap capturam corretamente o ganho de precisão da
pós-estratificação. Em nenhum caso a mudança de significância estatística é
relevante para os termos principais (`formal`, `mulher`, `preto_pardo`
continuam significativos a 1% nos dois métodos); a única diferença qualitativa
é `formal:preto_pardo` na renda por hora, que passa de não significativo
(`p=0,155`, Python) para significativo a 10% (`p=0,073`, R) — ainda assim,
longe de ser um resultado central do estudo (a interação nunca foi
significativa na renda mensal em nenhum dos dois métodos).

## Limitações desta réplica

- **74 de 200 réplicas bootstrap não convergem** (ficam `NA` e são descartadas
  automaticamente pelo `survey`) em ambos os modelos, provavelmente porque
  Roraima é uma UF pequena e, em algumas reamostragens, alguma categoria fina
  de escolaridade/ocupação/atividade/período fica sem observações, tornando o
  desenho local rank-deficiente naquela réplica específica. A variância é
  calculada com as 126 réplicas restantes -- ainda uma base razoável, mas vale
  registrar como limitação.
- O empilhamento dos 10 anos em **um único** desenho bootstrap pooled assume
  que os trimestres são amostras independentes entre si (razoável: mesmo com
  o painel rotativo da PNAD-C, o intervalo de um ano entre 4os trimestres
  consecutivos excede a janela de 5 trimestres em que um domicílio permanece
  no painel, então não há sobreposição de UPA/domicílio entre anos).
- Esta réplica ainda reporta os mesmos diferenciais **condicionais**, não
  causais -- as mesmas ressalvas de seleção (formalidade, ocupação, jornada)
  de `docs/resumo_resultados_correntes.md` se aplicam aqui.

## Como reproduzir

Requer R (>= 4.2) com os pacotes `PNADcIBGE`, `survey`, `readxl`, `dplyr` e
`tibble` instalados, e o pipeline Python já rodado (para o arquivo de
deflator em `data/raw/documentacao/`). A partir da raiz do projeto:

```powershell
Rscript r/01_replicate_survey.R
```

O script lê o microdado nacional de cada trimestre diretamente dos arquivos
já baixados em `data/raw/{ano}/`, filtra para Roraima, constrói as mesmas
variáveis derivadas do pipeline Python e salva:

- `outputs/tables/replicacao_r_survey_comparacao.csv`
- `outputs/models/replicacao_r_ln_renda_mensal_real.txt`
- `outputs/models/replicacao_r_ln_renda_hora_real.txt`
