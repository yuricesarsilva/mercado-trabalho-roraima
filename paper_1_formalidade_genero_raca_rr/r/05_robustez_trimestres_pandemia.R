# Bloco C1+C2 do plano de reforma (docs/plano_reforma_econometrica.md): robustez temporal.
#
# C1: reestima a especificação M4 (a preferida, ver docs/resultados_bloco_b.md) na base com
# TODOS os trimestres 2016-2025 (não só o 4o), com FE de periodo (ano x trimestre, 40 níveis em
# vez de 10) -- e compara lado a lado com o resultado Q4-only já salvo pelo Bloco B. Justificativa
# do desenho Q4-only: mantém comparabilidade sazonal entre os cortes e reduz a intensidade de
# reutilização das unidades amostrais do painel rotativo; esta é a robustez que testa se esse
# recorte é responsável pelos achados.
#
# C2: reestima M4 em três recortes de ano (Q4-only, mesma amostra do Bloco B) -- 2016-2019,
# 2022-2025, e todos os anos exceto 2020-2021 -- para checar se os achados sobre formal/mulher/
# raça são artefato do período pandêmico.

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

tables_dir <- file.path(project_dir, "outputs", "tables")

options(survey.lonely.psu = "adjust")
options(survey.adjust.domain.lonely = TRUE)

rr_uf_code <- 14

RHS_M4 <- paste(
  "formal + mulher + formal:mulher",
  "+ factor(raca_grupo) + formal:factor(raca_grupo) + mulher:factor(raca_grupo)",
  "+ idade + idade2 + factor(escolaridade)",
  "+ factor(celula_ocup_ativ) + factor(periodo)"
)

KEY_TERMS <- c(
  "formal", "mulher", "formal:mulher",
  "factor(raca_grupo)preto", "factor(raca_grupo)pardo", "factor(raca_grupo)indigena"
)

extract_coef_table <- function(model, label) {
  s <- as.data.frame(summary(model)$coefficients)
  s$termo <- rownames(s)
  names(s) <- c("coeficiente", "erro_padrao", "t_valor", "p_valor", "termo")
  s <- s[s$termo %in% KEY_TERMS, c("termo", "coeficiente", "erro_padrao", "p_valor")]
  s$efeito_percentual_aprox <- (exp(s$coeficiente) - 1) * 100
  s$especificacao <- label
  rownames(s) <- NULL
  s
}

fit_and_extract <- function(dv, design, label) {
  formula_str <- paste(dv, "~", RHS_M4)
  model <- svyglm_capture_convergence(as.formula(formula_str), design)
  cat(sprintf(
    "[convergência bootstrap] %s | %s: svyglm descartou %d/200 réplicas\n",
    label, dv, attr(model, "n_replicas_na")
  ))
  tbl <- extract_coef_table(model, label)
  tbl$dv <- dv
  tbl$n_replicas_descartadas <- attr(model, "n_replicas_na")
  tbl
}

# ---------------------------------------------------------------------------
# C1: todos os trimestres vs. Q4-only
# ---------------------------------------------------------------------------

cat("\n################ C1: todos os trimestres vs. Q4-only ################\n")

common_todos <- load_or_build_common(
  project_dir, years = 2016:2025, quarter = 1:4, rr_uf_code = rr_uf_code,
  cache_name = "pnadc_rr_r_common_todos_trimestres.rds"
)
cat(sprintf("Amostra ampla, todos os trimestres: %d\n", nrow(common_todos)))
cat(sprintf(
  "Células ocupação x atividade (todos os trimestres): %d níveis (incl. 'outras', N=%d)\n",
  length(unique(common_todos$celula_ocup_ativ)), attr(common_todos, "celula_ocup_ativ_n_outras")
))

design_todos <- build_design(common_todos)

resultados_c1 <- list()
for (dv_info in list(
  list(dv = "ln_renda_mensal_real", valida_col = "valida_mensal"),
  list(dv = "ln_renda_hora_real", valida_col = "valida_hora")
)) {
  idx <- common_todos[[dv_info$valida_col]]
  design_dv <- design_todos[idx, ]
  cat(sprintf("\n=== todos_trimestres | %s | N=%d ===\n", dv_info$dv, sum(idx)))
  resultados_c1[[dv_info$dv]] <- fit_and_extract(dv_info$dv, design_dv, "todos_trimestres")
}

# Referência Q4-only já estimada no Bloco B (outputs/tables/r_nested_ampla_{dv}_M4.csv)
q4_ref <- list()
for (dv in c("ln_renda_mensal_real", "ln_renda_hora_real")) {
  ref_path <- file.path(tables_dir, sprintf("r_nested_ampla_%s_M4.csv", dv))
  ref <- read.csv(ref_path)
  ref <- ref[ref$termo %in% KEY_TERMS, c("termo", "coeficiente", "erro_padrao", "p_valor", "efeito_percentual_aprox")]
  ref$especificacao <- "q4_only"
  ref$dv <- dv
  ref$n_replicas_descartadas <- NA
  q4_ref[[dv]] <- ref
}

comparacao_c1 <- dplyr::bind_rows(c(resultados_c1, q4_ref))
comparacao_c1 <- comparacao_c1[order(comparacao_c1$dv, comparacao_c1$termo, comparacao_c1$especificacao), ]

out_c1 <- file.path(tables_dir, "r_robustez_trimestres.csv")
write.csv(comparacao_c1, out_c1, row.names = FALSE)
cat(sprintf("\nsaved: %s\n", out_c1))
print(comparacao_c1[, c("especificacao", "dv", "termo", "efeito_percentual_aprox", "p_valor")], digits = 4, row.names = FALSE)

# ---------------------------------------------------------------------------
# C2: split de pandemia (Q4-only, mesma amostra do Bloco B)
# ---------------------------------------------------------------------------

cat("\n################ C2: split de pandemia ################\n")

common_q4 <- load_or_build_common(project_dir, years = 2016:2025, quarter = 4, rr_uf_code = rr_uf_code)
design_q4 <- build_design(common_q4)

recortes <- list(
  pre_pandemia_2016_2019 = common_q4$Ano %in% 2016:2019,
  pos_pandemia_2022_2025 = common_q4$Ano %in% 2022:2025,
  excl_2020_2021 = !(common_q4$Ano %in% 2020:2021)
)

resultados_c2 <- list()
for (recorte_nome in names(recortes)) {
  idx_ano <- recortes[[recorte_nome]]
  design_recorte <- design_q4[idx_ano, ]
  data_recorte <- common_q4[idx_ano, ]

  for (dv_info in list(
    list(dv = "ln_renda_mensal_real", valida_col = "valida_mensal"),
    list(dv = "ln_renda_hora_real", valida_col = "valida_hora")
  )) {
    idx_dv <- data_recorte[[dv_info$valida_col]]
    design_dv <- design_recorte[idx_dv, ]
    label <- recorte_nome
    cat(sprintf("\n=== %s | %s | N=%d ===\n", label, dv_info$dv, sum(idx_dv)))
    resultados_c2[[paste(label, dv_info$dv)]] <- fit_and_extract(dv_info$dv, design_dv, label)
  }
}

comparacao_c2 <- dplyr::bind_rows(resultados_c2)
comparacao_c2 <- comparacao_c2[order(comparacao_c2$dv, comparacao_c2$termo, comparacao_c2$especificacao), ]

out_c2 <- file.path(tables_dir, "r_robustez_pandemia.csv")
write.csv(comparacao_c2, out_c2, row.names = FALSE)
cat(sprintf("\nsaved: %s\n", out_c2))
print(comparacao_c2[, c("especificacao", "dv", "termo", "efeito_percentual_aprox", "p_valor")], digits = 4, row.names = FALSE)
