# Bloco B do plano de reforma (docs/plano_reforma_econometrica.md): sequência de modelos
# aninhados M1->M4 + FE ocupação x atividade, estimados em R com desenho amostral completo
# (svrepdesign, bootstrap, 200 réplicas oficiais do IBGE), para as duas amostras (principal
# ampla e restrita "empregados") e as duas variáveis dependentes (mensal real, hora real).
#
# M1: tratamentos (formal, mulher, formal:mulher, raça, formal:raça, mulher:raça) + idade +
#     escolaridade + período.
# M2: M1 + FE atividade.
# M3: M2 + FE ocupação.
# M4: M1 + FE (ocupação x atividade), célula conjunta com células N<30 agregadas em "outras"
#     (ver build_celula_ocup_ativ em lib_pnadc.R).
#
# Período (ano/trimestre) entra em todos os modelos -- não faz parte da sequência de
# composição ocupacional/setorial que M1->M4 testa.

suppressPackageStartupMessages({
  library(survey)
  library(dplyr)
})

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
source(file.path(r_dir, "lib_pnadc.R"))

raw_dir <- file.path(project_dir, "data", "raw")
input_txt <- file.path(raw_dir, "input_PNADC_trimestral.txt")
tables_dir <- file.path(project_dir, "outputs", "tables")
models_dir <- file.path(project_dir, "outputs", "models")

options(survey.lonely.psu = "adjust")
options(survey.adjust.domain.lonely = TRUE)

years <- 2016:2025
quarter <- 4
rr_uf_code <- 14

# ---------------------------------------------------------------------------
# 1. Dados
# ---------------------------------------------------------------------------

common <- load_or_build_common(project_dir, years, quarter, rr_uf_code)
cat(sprintf("Amostra ampla (comum): %d\n", nrow(common)))
cat(sprintf("Amostra restrita (empregado_restrito==1): %d\n", sum(common$empregado_restrito == 1)))
cat(sprintf(
  "Células ocupação x atividade: %d níveis (incl. 'outras', N=%d de %d células esparsas absorvidas)\n",
  length(unique(common$celula_ocup_ativ)),
  attr(common, "celula_ocup_ativ_n_outras"),
  length(attr(common, "celula_ocup_ativ_sparse"))
))

repweight_cols <- grep("^V1028[0-9]{3}$", names(common), value = TRUE)
stopifnot(length(repweight_cols) == 200)

design_full <- build_design(common)
restrita_idx <- common$empregado_restrito == 1
design_restrita <- design_full[restrita_idx, ]

designs <- list(ampla = design_full, restrita = design_restrita)
samples <- list(ampla = common, restrita = common[restrita_idx, ])

# ---------------------------------------------------------------------------
# 2. Especificações M1->M4
# ---------------------------------------------------------------------------

TREAT_RHS <- paste(
  "formal + mulher + formal:mulher",
  "+ factor(raca_grupo) + formal:factor(raca_grupo) + mulher:factor(raca_grupo)"
)
DEMO_RHS <- "idade + idade2 + factor(escolaridade)"
PERIOD_RHS <- "factor(periodo)"

rhs_list <- list(
  M1 = paste(TREAT_RHS, DEMO_RHS, PERIOD_RHS, sep = " + "),
  M2 = paste(TREAT_RHS, DEMO_RHS, PERIOD_RHS, "factor(atividade_grupo)", sep = " + "),
  M3 = paste(TREAT_RHS, DEMO_RHS, PERIOD_RHS, "factor(atividade_grupo)", "factor(ocupacao_grupo)", sep = " + "),
  M4 = paste(TREAT_RHS, DEMO_RHS, PERIOD_RHS, "factor(celula_ocup_ativ)", sep = " + ")
)

dv_info <- list(
  ln_renda_mensal_real = list(dv = "renda_mensal_real", valida_col = "valida_mensal"),
  ln_renda_hora_real = list(dv = "renda_hora_real", valida_col = "valida_hora")
)

KEY_TERMS_CHECK <- c("formal", "mulher")

extract_coef_table <- function(model) {
  s <- as.data.frame(summary(model)$coefficients)
  s$termo <- rownames(s)
  names(s) <- c("coeficiente", "erro_padrao", "t_valor", "p_valor", "termo")
  s <- s[, c("termo", "coeficiente", "erro_padrao", "p_valor")]
  s$efeito_percentual_aprox <- (exp(s$coeficiente) - 1) * 100
  rownames(s) <- NULL
  s
}

# ---------------------------------------------------------------------------
# 3. Loop de estimação: amostra x variável dependente x modelo
# ---------------------------------------------------------------------------

convergence_log <- list()

for (amostra in names(designs)) {
  design <- designs[[amostra]]
  data_amostra <- samples[[amostra]]

  for (dv_label in names(dv_info)) {
    valida_col <- dv_info[[dv_label]]$valida_col
    idx <- data_amostra[[valida_col]]
    design_dv <- design[idx, ]
    data_dv <- data_amostra[idx, ]

    for (m_label in names(rhs_list)) {
      key <- sprintf("%s_%s_%s", amostra, dv_label, m_label)
      formula_str <- paste(dv_label, "~", rhs_list[[m_label]])
      cat(sprintf("\n=== %s ===\nN = %d\n", key, nrow(data_dv)))

      model <- tryCatch(
        svyglm_capture_convergence(as.formula(formula_str), design_dv),
        error = function(e) {
          cat(sprintf("ERRO ao estimar %s: %s\n", key, conditionMessage(e)))
          NULL
        }
      )
      if (is.null(model)) next

      coef_table <- extract_coef_table(model)
      out_csv <- file.path(tables_dir, sprintf("r_nested_%s.csv", key))
      write.csv(coef_table, out_csv, row.names = FALSE)
      cat(sprintf("saved: %s (N params=%d)\n", out_csv, nrow(coef_table)))

      n_na_real <- attr(model, "n_replicas_na")
      conv <- check_replicate_convergence(as.formula(formula_str), data_dv, repweight_cols, KEY_TERMS_CHECK)
      cat(sprintf(
        "[convergência bootstrap] %s: svyglm descartou %d/200 réplicas (qualquer termo NA); formal/mulher especificamente ficaram bem em %d/200\n",
        key, n_na_real, conv$n_ok
      ))
      convergence_log[[key]] <- data.frame(
        especificacao = key, amostra = amostra, dv = dv_label, modelo = m_label,
        n_obs = nrow(data_dv), n_params = nrow(coef_table),
        n_replicas_descartadas_svyglm = n_na_real,
        n_replicas_ok_formal_mulher = conv$n_ok
      )
    }
  }
}

convergence_df <- dplyr::bind_rows(convergence_log)
conv_out <- file.path(tables_dir, "r_nested_convergencia.csv")
write.csv(convergence_df, conv_out, row.names = FALSE)
cat(sprintf("\nsaved: %s\n", conv_out))
print(convergence_df, digits = 3)
