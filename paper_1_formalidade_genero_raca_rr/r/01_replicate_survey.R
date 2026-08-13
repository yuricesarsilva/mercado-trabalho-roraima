# Réplica do modelo-base em R com o pacote `survey`, usando o desenho amostral
# completo da PNAD Contínua (pesos de replicação bootstrap, 200 réplicas,
# oficialmente distribuídos pelo IBGE nas colunas V1028/V1028001-V1028200).
#
# Verificado empiricamente (ver r/_test_multi_year.R) que, para 2016T4-2025T4,
# PNADcIBGE::pnadc_design() sempre cai no ramo svrepdesign(bootstrap) e que o
# peso "sampling" daí extraído é idêntico a V1028 (diferença máxima = 0). Por
# isso este script lê as colunas de réplica diretamente via read_pnadc(), sem
# precisar rodar pnadc_design() (mais lento) em produção.
#
# Como todos os anos usam o mesmo esquema de réplicas, dá para empilhar os
# 10 anos e declarar UM svrepdesign combinado (cada linha carrega os pesos de
# réplica já calculados nacionalmente para o seu próprio trimestre) -- em vez
# de precisar reconciliar múltiplos tipos de desenho incompatíveis.

suppressPackageStartupMessages({
  library(PNADcIBGE)
  library(survey)
  library(readxl)
  library(dplyr)
})

options(survey.lonely.psu = "adjust")
options(survey.adjust.domain.lonely = TRUE)

get_script_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  match <- grep("^--file=", args)
  if (length(match) > 0) {
    return(dirname(normalizePath(sub("^--file=", "", args[match]))))
  }
  normalizePath(".")
}

r_dir <- get_script_dir()
project_dir <- dirname(r_dir)
raw_dir <- file.path(project_dir, "data", "raw")
input_txt <- file.path(raw_dir, "input_PNADC_trimestral.txt")
tables_dir <- file.path(project_dir, "outputs", "tables")
models_dir <- file.path(project_dir, "outputs", "models")
docs_dir <- file.path(project_dir, "docs")

years <- 2016:2025
quarter <- 4
rr_uf_code <- 14

vars_needed <- c(
  "VD4002", "VD4009", "VD4010", "VD4011", "VD4012", "VD4016", "VD4019",
  "V2007", "V2009", "V2010", "V4019", "V4029", "V4032", "V4039", "VD3004", "VD4035"
)

# ---------------------------------------------------------------------------
# 1. Ler e empilhar os 10 anos (microdado nacional, filtrado para RR depois)
# ---------------------------------------------------------------------------

find_zip <- function(year, quarter) {
  dir <- file.path(raw_dir, as.character(year))
  candidates <- list.files(dir, pattern = sprintf("^PNADC_0%d%d.*\\.zip$", quarter, year), full.names = TRUE)
  if (length(candidates) == 0) stop(sprintf("No zip found for %d Q%d", year, quarter))
  sort(candidates)[length(candidates)]
}

read_year_rr <- function(year, quarter) {
  message(sprintf("Lendo %dT%d...", year, quarter))
  zip_path <- find_zip(year, quarter)
  tmp_dir <- tempfile("pnadc_")
  dir.create(tmp_dir)
  on.exit(unlink(tmp_dir, recursive = TRUE), add = TRUE)

  txt_name <- utils::unzip(zip_path, list = TRUE)$Name
  txt_name <- txt_name[grepl("\\.txt$", txt_name, ignore.case = TRUE)][1]
  utils::unzip(zip_path, files = txt_name, exdir = tmp_dir)
  microdata_path <- file.path(tmp_dir, txt_name)

  df <- read_pnadc(microdata = microdata_path, input_txt = input_txt, vars = vars_needed)
  df$UF <- as.numeric(as.character(df$UF))
  rr <- df[df$UF == rr_uf_code, ]

  repweight_cols <- grep("^V1028[0-9]{3}$", names(rr), value = TRUE)
  keep_cols <- c(
    "Ano", "Trimestre", "UF", "UPA", "Estrato", "V1028", repweight_cols,
    vars_needed
  )
  rr <- rr[, intersect(keep_cols, names(rr))]
  rr$periodo <- sprintf("%dT%d", year, quarter)
  tibble::as_tibble(rr)
}

all_years <- lapply(years, read_year_rr, quarter = quarter)
pooled <- dplyr::bind_rows(all_years)
cat(sprintf("Linhas empilhadas (RR, todos os indivíduos, %d anos): %d\n", length(years), nrow(pooled)))

repweight_cols <- grep("^V1028[0-9]{3}$", names(pooled), value = TRUE)
cat(sprintf("Colunas de réplica encontradas: %d (esperado 200)\n", length(repweight_cols)))
stopifnot(length(repweight_cols) == 200)

# ---------------------------------------------------------------------------
# 2. Deflator oficial (mesmo arquivo já baixado por scripts/00_download_pnadc.py)
# ---------------------------------------------------------------------------

deflator_dir <- file.path(raw_dir, "documentacao")
deflator_path <- list.files(deflator_dir, pattern = "^deflator_.*\\.xls$", full.names = TRUE)[1]
stopifnot(!is.na(deflator_path))

trimestre_to_trim <- c("1" = "01-02-03", "2" = "04-05-06", "3" = "07-08-09", "4" = "10-11-12")

deflator_raw <- readxl::read_excel(deflator_path, sheet = "deflator")
deflator_rr <- deflator_raw[deflator_raw$UF == rr_uf_code, ]
trim_to_quarter <- setNames(names(trimestre_to_trim), trimestre_to_trim)
deflator_rr$Trimestre <- as.integer(trim_to_quarter[deflator_rr$trim])
deflator_rr <- deflator_rr[!is.na(deflator_rr$Trimestre), c("Ano", "Trimestre", "Habitual")]
names(deflator_rr) <- c("Ano", "Trimestre", "deflator_habitual")
deflator_rr$Ano <- as.integer(deflator_rr$Ano)

# ---------------------------------------------------------------------------
# 3. Variáveis derivadas (replicando src/pnadc_rr/*.py)
# ---------------------------------------------------------------------------

pooled$Ano <- as.integer(pooled$Ano)
pooled$Trimestre <- as.integer(pooled$Trimestre)

occupied <- pooled[!is.na(pooled$V2009) & pooled$V2009 >= 14 & !is.na(pooled$VD4002) & pooled$VD4002 == 1, ]

# VD4009/VD4010/VD4011 chegam do read_pnadc como strings de largura fixa
# zero-padded ("01".."11"), não como números -- por isso a conversão explícita
# para inteiro antes de qualquer comparação numérica (%in%, ==).
build_formality <- function(vd4009, v4019) {
  vd4009 <- as.integer(vd4009)
  v4019 <- as.integer(v4019)
  formal <- rep(NA_real_, length(vd4009))
  formal[vd4009 %in% c(1, 3, 5, 7)] <- 1
  formal[vd4009 %in% c(2, 4, 6, 10)] <- 0
  cnpj_known <- vd4009 %in% c(8, 9) & !is.na(v4019)
  formal[cnpj_known & v4019 == 1] <- 1
  formal[cnpj_known & v4019 == 2] <- 0
  formal
}

occupied$formal <- build_formality(occupied$VD4009, occupied$V4019)
occupied$mulher <- as.integer(as.integer(occupied$V2007) == 2)
occupied$preto_pardo <- as.integer(as.integer(occupied$V2010) %in% c(2, 4))
occupied$idade <- occupied$V2009
occupied$idade2 <- occupied$idade^2
occupied$peso <- occupied$V1028
occupied$escolaridade <- as.character(as.integer(occupied$VD3004))
occupied$atividade_grupo <- as.character(as.integer(occupied$VD4010))
occupied$ocupacao_grupo <- as.character(as.integer(occupied$VD4011))
occupied$horas_semanais_principal <- as.numeric(occupied$V4039)
occupied$renda_mensal <- occupied$VD4016
occupied$renda_hora <- occupied$renda_mensal / (occupied$horas_semanais_principal * 4.33)
occupied$renda_hora[!is.na(occupied$renda_hora) & occupied$renda_hora <= 0] <- NA

occupied <- dplyr::left_join(occupied, deflator_rr, by = c("Ano", "Trimestre"))
stopifnot(!any(is.na(occupied$deflator_habitual)))

occupied$renda_mensal_real <- occupied$renda_mensal * occupied$deflator_habitual
occupied$renda_hora_real <- occupied$renda_hora * occupied$deflator_habitual
occupied$renda_hora_real[!is.na(occupied$renda_hora_real) & occupied$renda_hora_real <= 0] <- NA
occupied$ln_renda_mensal_real <- ifelse(occupied$renda_mensal_real > 0, log(occupied$renda_mensal_real), NA)
occupied$ln_renda_hora_real <- ifelse(occupied$renda_hora_real > 0, log(occupied$renda_hora_real), NA)

common <- occupied[
  !is.na(occupied$formal) & !is.na(occupied$mulher) & !is.na(occupied$preto_pardo) & !is.na(occupied$peso),
]
cat(sprintf("Amostra comum (RR, ocupados, tratamentos válidos): %d\n", nrow(common)))

# ---------------------------------------------------------------------------
# 4. Desenho amostral (bootstrap replicate, pooled) e modelos
# ---------------------------------------------------------------------------

design_full <- svrepdesign(
  data = common,
  weights = ~peso,
  type = "bootstrap",
  repweights = "V1028[0-9]+",
  mse = TRUE,
  replicates = 200,
  df = 200
)

rhs <- paste(
  "formal + mulher + preto_pardo + formal:mulher + formal:preto_pardo",
  "+ idade + idade2 + factor(escolaridade)",
  "+ factor(ocupacao_grupo) + factor(atividade_grupo) + factor(periodo)"
)

design_mensal <- subset(design_full, !is.na(renda_mensal_real) & renda_mensal_real > 0)
design_hora <- subset(design_full, !is.na(renda_hora_real) & renda_hora_real > 0)

cat("Estimando modelo de renda mensal real (svyglm, bootstrap replicate)...\n")
model_mensal <- svyglm(as.formula(paste("ln_renda_mensal_real ~", rhs)), design = design_mensal, family = gaussian())

cat("Estimando modelo de renda por hora real (svyglm, bootstrap replicate)...\n")
model_hora <- svyglm(as.formula(paste("ln_renda_hora_real ~", rhs)), design = design_hora, family = gaussian())

# ---------------------------------------------------------------------------
# 5. Extrair coeficientes-chave e comparar com as estimativas em Python
# ---------------------------------------------------------------------------

key_terms <- c("formal", "mulher", "preto_pardo", "formal:mulher", "formal:preto_pardo")

extract_key <- function(model) {
  s <- summary(model)$coefficients
  s <- as.data.frame(s)
  s$termo <- rownames(s)
  s <- s[s$termo %in% key_terms, c("termo", "Estimate", "Std. Error", "Pr(>|t|)")]
  names(s) <- c("termo", "coeficiente_r", "erro_padrao_r", "p_valor_r")
  s
}

compare_with_python <- function(r_coefs, python_label, dv_label) {
  python_path <- file.path(tables_dir, sprintf("modelo_base_%s.csv", python_label))
  py <- read.csv(python_path, row.names = 1)
  py$termo <- rownames(py)
  py <- py[py$termo %in% key_terms, c("termo", "coeficiente", "erro_padrao", "p_valor")]
  names(py) <- c("termo", "coeficiente_python", "erro_padrao_python", "p_valor_python")

  merged <- merge(r_coefs, py, by = "termo")
  merged$diff_absoluta <- merged$coeficiente_r - merged$coeficiente_python
  merged$dv <- dv_label
  merged[, c(
    "dv", "termo", "coeficiente_r", "erro_padrao_r", "p_valor_r",
    "coeficiente_python", "erro_padrao_python", "p_valor_python", "diff_absoluta"
  )]
}

cmp_mensal <- compare_with_python(extract_key(model_mensal), "ln_renda_mensal_real", "ln_renda_mensal_real")
cmp_hora <- compare_with_python(extract_key(model_hora), "ln_renda_hora_real", "ln_renda_hora_real")
comparison <- rbind(cmp_mensal, cmp_hora)

print(comparison, digits = 4)

write.csv(comparison, file.path(tables_dir, "replicacao_r_survey_comparacao.csv"), row.names = FALSE)
capture.output(summary(model_mensal), file = file.path(models_dir, "replicacao_r_ln_renda_mensal_real.txt"))
capture.output(summary(model_hora), file = file.path(models_dir, "replicacao_r_ln_renda_hora_real.txt"))

cat(sprintf("\nsaved: %s\n", file.path(tables_dir, "replicacao_r_survey_comparacao.csv")))
cat(sprintf("saved: %s\n", file.path(models_dir, "replicacao_r_ln_renda_mensal_real.txt")))
cat(sprintf("saved: %s\n", file.path(models_dir, "replicacao_r_ln_renda_hora_real.txt")))
