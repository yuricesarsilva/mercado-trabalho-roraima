# Biblioteca compartilhada para os scripts de estimação em R (Bloco B da reforma,
# ver docs/plano_reforma_econometrica.md). Centraliza leitura do microdado nacional,
# construção das variáveis derivadas (replicando src/pnadc_rr/*.py e
# scripts/02_build_analytic.py) e utilitários de diagnóstico do desenho bootstrap.
#
# Usado por r/02_estimate_nested.R e demais scripts do Bloco B/C.

suppressPackageStartupMessages({
  library(PNADcIBGE)
  library(survey)
  library(readxl)
  library(dplyr)
})

VARS_NEEDED <- c(
  "VD4002", "VD4009", "VD4010", "VD4011", "VD4012", "VD4016", "VD4019",
  "V2007", "V2009", "V2010", "V4019", "V4029", "V4032", "V4039", "VD3004", "VD4035"
)

# ---------------------------------------------------------------------------
# Leitura do microdado nacional, filtrado para Roraima
# ---------------------------------------------------------------------------

find_zip <- function(raw_dir, year, quarter) {
  dir <- file.path(raw_dir, as.character(year))
  candidates <- list.files(dir, pattern = sprintf("^PNADC_0%d%d.*\\.zip$", quarter, year), full.names = TRUE)
  if (length(candidates) == 0) stop(sprintf("No zip found for %d Q%d", year, quarter))
  sort(candidates)[length(candidates)]
}

read_year_rr <- function(raw_dir, input_txt, year, quarter, rr_uf_code = 14, vars_needed = VARS_NEEDED) {
  message(sprintf("Lendo %dT%d...", year, quarter))
  zip_path <- find_zip(raw_dir, year, quarter)
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
  keep_cols <- c("Ano", "Trimestre", "UF", "UPA", "Estrato", "V1028", repweight_cols, vars_needed)
  rr <- rr[, intersect(keep_cols, names(rr))]
  rr$periodo <- sprintf("%dT%d", year, quarter)
  tibble::as_tibble(rr)
}

read_pooled_rr <- function(raw_dir, input_txt, years, quarters, rr_uf_code = 14) {
  combos <- expand.grid(year = years, quarter = quarters)
  frames <- Map(function(y, q) read_year_rr(raw_dir, input_txt, y, q, rr_uf_code), combos$year, combos$quarter)
  pooled <- dplyr::bind_rows(frames)
  repweight_cols <- grep("^V1028[0-9]{3}$", names(pooled), value = TRUE)
  if (length(repweight_cols) != 200) {
    warning(sprintf("Esperava 200 colunas de réplica, encontrou %d", length(repweight_cols)))
  }
  pooled
}

# ---------------------------------------------------------------------------
# Deflator oficial (mesmo arquivo baixado por scripts/00_download_pnadc.py)
# ---------------------------------------------------------------------------

load_deflator_rr <- function(raw_dir, rr_uf_code = 14) {
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
  deflator_rr
}

# ---------------------------------------------------------------------------
# Variáveis derivadas -- replica scripts/02_build_analytic.py (Bloco A da reforma)
# ---------------------------------------------------------------------------

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

# amarelo (V2010==3) fica NA -- excluído da estimação de raça, ver docs/definicao_raca.md.
RACA_GRUPO_LABELS <- c("1" = "branco", "2" = "preto", "4" = "pardo", "5" = "indigena")
POSICAO_OCUPACAO_LABELS <- c(
  "1" = "privado_com_carteira", "2" = "privado_sem_carteira",
  "3" = "domestico_com_carteira", "4" = "domestico_sem_carteira",
  "5" = "publico_com_carteira", "6" = "publico_sem_carteira",
  "7" = "militar_estatutario", "8" = "empregador",
  "9" = "conta_propria", "10" = "familiar_auxiliar"
)
PUBLICO_VD4009 <- c(5, 6, 7)
EMPREGADOS_VD4009 <- c(1, 2, 3, 4, 5, 6, 7)

build_derived_variables <- function(pooled) {
  pooled$Ano <- as.integer(pooled$Ano)
  pooled$Trimestre <- as.integer(pooled$Trimestre)

  occupied <- pooled[!is.na(pooled$V2009) & pooled$V2009 >= 14 & !is.na(pooled$VD4002) & pooled$VD4002 == 1, ]

  occupied$VD4009_int <- as.integer(occupied$VD4009)
  occupied$formal <- build_formality(occupied$VD4009, occupied$V4019)
  occupied$mulher <- as.integer(as.integer(occupied$V2007) == 2)
  occupied$preto_pardo <- as.integer(as.integer(occupied$V2010) %in% c(2, 4))
  occupied$raca_grupo <- unname(RACA_GRUPO_LABELS[as.character(as.integer(occupied$V2010))])
  occupied$setor_publico <- as.integer(occupied$VD4009_int %in% PUBLICO_VD4009)
  occupied$posicao_ocupacao_grupo <- unname(POSICAO_OCUPACAO_LABELS[as.character(occupied$VD4009_int)])
  occupied$empregado_restrito <- as.integer(occupied$VD4009_int %in% EMPREGADOS_VD4009)
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
  occupied
}

merge_deflator <- function(occupied, deflator_rr) {
  occupied <- dplyr::left_join(occupied, deflator_rr, by = c("Ano", "Trimestre"))
  stopifnot(!any(is.na(occupied$deflator_habitual)))

  occupied$renda_mensal_real <- occupied$renda_mensal * occupied$deflator_habitual
  occupied$renda_hora_real <- occupied$renda_hora * occupied$deflator_habitual
  occupied$renda_hora_real[!is.na(occupied$renda_hora_real) & occupied$renda_hora_real <= 0] <- NA
  occupied$ln_renda_mensal_real <- ifelse(occupied$renda_mensal_real > 0, log(occupied$renda_mensal_real), NA)
  occupied$ln_renda_hora_real <- ifelse(occupied$renda_hora_real > 0, log(occupied$renda_hora_real), NA)
  occupied$ln_horas_semanais_principal <- ifelse(
    !is.na(occupied$horas_semanais_principal) & occupied$horas_semanais_principal > 0,
    log(occupied$horas_semanais_principal), NA
  )
  occupied
}

# ---------------------------------------------------------------------------
# Célula ocupação x atividade com pooling de células esparsas em "outras"
# (ver Checkpoint A, docs/plano_reforma_econometrica.md) -- o limiar é aplicado
# UMA VEZ sobre a amostra completa (pesos originais), nunca recalculado por
# réplica bootstrap, para que a variável em si seja fixa entre réplicas e só a
# estimação varie.
# ---------------------------------------------------------------------------

build_celula_ocup_ativ <- function(df, min_n = 30) {
  cell_raw <- paste(df$ocupacao_grupo, df$atividade_grupo, sep = "_")
  counts <- table(cell_raw)
  sparse <- names(counts[counts < min_n])
  cell <- ifelse(cell_raw %in% sparse, "outras", cell_raw)
  df$celula_ocup_ativ <- cell
  attr(df, "celula_ocup_ativ_sparse") <- sparse
  attr(df, "celula_ocup_ativ_n_outras") <- sum(cell_raw %in% sparse)
  df
}

# ---------------------------------------------------------------------------
# Diagnóstico de convergência das réplicas bootstrap: refita a mesma
# especificação (WLS) com cada uma das 200 colunas de réplica e conta quantas
# produzem um ajuste de posto completo (sem coeficiente NA/alias) para os
# termos-chave. Mais rápido que inspecionar por dentro do svyglm porque usa
# lm() diretamente (equivalente a svyglm(family=gaussian()) para o ponto
# estimado; só a variância é tratada depois, pelo desenho completo).
# ---------------------------------------------------------------------------

check_replicate_convergence <- function(formula, data, repweight_cols, key_terms) {
  n_total <- length(repweight_cols)
  n_ok <- 0
  failures <- character(0)
  for (col in repweight_cols) {
    # lm() resolve `weights=` como uma "extra variable" do model.frame: se não for
    # encontrada em `data`, cai para o ambiente onde a FÓRMULA foi criada (não o frame
    # local desta função) -- por isso o peso precisa ser uma coluna literal de `data`,
    # nunca um símbolo solto (`weights = w`), senão dá "objeto 'w' não encontrado" e o
    # tryCatch abaixo contaria toda réplica como falha de convergência silenciosamente.
    data$.replicate_weight <- data[[col]]
    fit <- tryCatch(
      stats::lm(formula, data = data, weights = .replicate_weight),
      error = function(e) NULL
    )
    if (is.null(fit)) {
      failures <- c(failures, col)
      next
    }
    coefs <- stats::coef(fit)
    present <- intersect(key_terms, names(coefs))
    if (length(present) < length(key_terms) || any(is.na(coefs[present]))) {
      failures <- c(failures, col)
      next
    }
    n_ok <- n_ok + 1
  }
  list(n_total = n_total, n_ok = n_ok, n_falhas = n_total - n_ok, colunas_falhas = failures)
}

# svyglm() com svrepdesign emite um warning "N replicates gave NA results and were
# discarded" quando alguma réplica bootstrap fica com coeficiente não identificável em
# QUALQUER termo do modelo (não só nos termos de interesse) -- essa contagem é a
# autoritativa, é o que de fato entra no erro-padrão reportado. check_replicate_convergence()
# acima é mais estreito (só formal/mulher) e serve como checagem secundária; esta função
# captura o número real do svyglm.
svyglm_capture_convergence <- function(formula, design, family = stats::gaussian()) {
  n_na <- 0L
  model <- withCallingHandlers(
    survey::svyglm(formula, design = design, family = family),
    warning = function(w) {
      if (grepl("replicates gave NA results", conditionMessage(w))) {
        n_na <<- as.integer(regmatches(conditionMessage(w), regexpr("[0-9]+", conditionMessage(w))))
        invokeRestart("muffleWarning")
      }
    }
  )
  attr(model, "n_replicas_na") <- n_na
  model
}

report_convergence <- function(label, conv) {
  cat(sprintf(
    "[convergência bootstrap] %s: %d/%d réplicas OK (%d falhas)\n",
    label, conv$n_ok, conv$n_total, conv$n_falhas
  ))
}

# ---------------------------------------------------------------------------
# Cache: ler+construir a amostra comum (10 anos de microdado nacional via
# PNADcIBGE::read_pnadc) é a etapa mais lenta de todo script novo. Como vários
# scripts do Bloco B/C partem da mesma amostra ampla, constrói uma vez e
# salva em RDS -- scripts seguintes reusam em segundos em vez de minutos.
# Chame com force_rebuild=TRUE sempre que a lógica de variáveis mudar.
# ---------------------------------------------------------------------------

load_or_build_common <- function(project_dir, years, quarter, rr_uf_code = 14,
                                  min_n_cell = 30, force_rebuild = FALSE,
                                  cache_name = "pnadc_rr_r_common.rds") {
  # cache_name PRECISA mudar sempre que years/quarter mudar (ex.: Bloco C usa
  # quarter=1:4 em vez de 4) -- senão um script reaproveita por engano o cache
  # de outro recorte, ou sobrescreve o cache Q4-only usado pelo Bloco B.
  cache_path <- file.path(project_dir, "data", "interim", cache_name)
  if (!force_rebuild && file.exists(cache_path)) {
    message(sprintf("Usando cache: %s", cache_path))
    return(readRDS(cache_path))
  }

  raw_dir <- file.path(project_dir, "data", "raw")
  input_txt <- file.path(raw_dir, "input_PNADC_trimestral.txt")

  pooled <- read_pooled_rr(raw_dir, input_txt, years, quarter, rr_uf_code)
  occupied <- build_derived_variables(pooled)
  deflator_rr <- load_deflator_rr(raw_dir, rr_uf_code)
  occupied <- merge_deflator(occupied, deflator_rr)

  common <- occupied[!is.na(occupied$formal) & !is.na(occupied$mulher) & !is.na(occupied$peso), ]
  common <- build_celula_ocup_ativ(common, min_n = min_n_cell)
  common$valida_mensal <- !is.na(common$renda_mensal_real) & common$renda_mensal_real > 0
  common$valida_hora <- !is.na(common$renda_hora_real) & common$renda_hora_real > 0

  dir.create(dirname(cache_path), recursive = TRUE, showWarnings = FALSE)
  saveRDS(common, cache_path)
  message(sprintf("saved cache: %s", cache_path))
  common
}

# ---------------------------------------------------------------------------
# Contrasts: soma de coeficientes com erro-padrão design-based via vcov(model)
# -- mesma técnica de var(a+b) = a'Va já usada em
# scripts/09_estimate_trends.py::year_effects() (Python), agora em R (Bloco B2).
# `terms` é o vetor de nomes de coeficientes a somar (ex.: c("mulher",
# "formal:mulher") dá o gap de gênero entre formais).
# ---------------------------------------------------------------------------

contrast_combo <- function(model, terms, label = paste(terms, collapse = " + ")) {
  coefs <- stats::coef(model)
  V <- stats::vcov(model)
  missing_terms <- setdiff(terms, names(coefs))
  if (length(missing_terms) > 0) {
    stop(sprintf("Termos não encontrados no modelo: %s", paste(missing_terms, collapse = ", ")))
  }
  a <- rep(0, length(coefs))
  names(a) <- names(coefs)
  a[terms] <- 1
  estimate <- sum(coefs[terms])
  se <- sqrt(as.numeric(t(a) %*% V %*% a))
  z <- estimate / se
  p_valor <- 2 * (1 - stats::pnorm(abs(z)))
  data.frame(
    contraste = label,
    termos = paste(terms, collapse = " + "),
    estimativa = estimate,
    erro_padrao = se,
    p_valor = p_valor,
    efeito_percentual_aprox = (exp(estimate) - 1) * 100,
    ic95_inf = (exp(estimate - 1.96 * se) - 1) * 100,
    ic95_sup = (exp(estimate + 1.96 * se) - 1) * 100
  )
}

build_design <- function(common) {
  repweight_cols <- grep("^V1028[0-9]{3}$", names(common), value = TRUE)
  stopifnot(length(repweight_cols) == 200)
  svrepdesign(
    data = common, weights = ~peso, type = "bootstrap",
    repweights = "V1028[0-9]+", mse = TRUE, replicates = 200, df = 200
  )
}
