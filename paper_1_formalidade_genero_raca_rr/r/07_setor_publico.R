# Setor público e estrutura salarial por posição na ocupação.
#
# Parte 1: adiciona setor_publico e formal:setor_publico à especificação M4 (amostra restrita
# de empregados) -- testa se o "prêmio de formalidade" reflete em parte um prêmio de ser
# servidor público, e se a formalização paga diferente dentro do setor público vs. privado.
#
# Parte 2: substitui o tratamento binário `formal` por `posicao_ocupacao_grupo` (10 categorias:
# privado/doméstico/público com e sem carteira, militar/estatutário, empregador, conta-própria,
# familiar auxiliar; referência = privado sem carteira) na amostra ampla -- dá a estrutura salarial
# completa por relação de trabalho, controlando por composição (demografia, ocupação x atividade,
# período). Complementado por médias descritivas não condicionais.

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

common <- load_or_build_common(project_dir, years = 2016:2025, quarter = 4, rr_uf_code = 14)
design_full <- build_design(common)

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
# Parte 1: formal x setor_publico, amostra restrita (empregados)
# ---------------------------------------------------------------------------

cat("\n################ Parte 1: formal x setor_publico (amostra restrita) ################\n")

restrita_idx <- common$empregado_restrito == 1
design_restrita <- design_full[restrita_idx, ]
data_restrita <- common[restrita_idx, ]

RHS_SETOR <- paste(
  "formal + mulher + formal:mulher",
  "+ factor(raca_grupo) + formal:factor(raca_grupo) + mulher:factor(raca_grupo)",
  "+ setor_publico + formal:setor_publico",
  "+ idade + idade2 + factor(escolaridade)",
  "+ factor(celula_ocup_ativ) + factor(periodo)"
)

for (dv_info in list(
  list(dv = "ln_renda_mensal_real", valida_col = "valida_mensal"),
  list(dv = "ln_renda_hora_real", valida_col = "valida_hora")
)) {
  idx <- data_restrita[[dv_info$valida_col]]
  design_dv <- design_restrita[idx, ]
  cat(sprintf("\n=== %s | N=%d ===\n", dv_info$dv, sum(idx)))

  model <- svyglm_capture_convergence(as.formula(paste(dv_info$dv, "~", RHS_SETOR)), design_dv)
  cat(sprintf("[convergência bootstrap] setor_publico | %s: svyglm descartou %d/200 réplicas\n", dv_info$dv, attr(model, "n_replicas_na")))

  coef_table <- extract_coef_table(model)
  out_csv <- file.path(tables_dir, sprintf("r_setor_publico_%s.csv", dv_info$dv))
  write.csv(coef_table, out_csv, row.names = FALSE)
  cat(sprintf("saved: %s\n", out_csv))

  destaque <- coef_table[coef_table$termo %in% c("formal", "setor_publico", "formal:setor_publico"), ]
  print(destaque, digits = 4, row.names = FALSE)

  # Efeito combinado (formal + setor_publico + formal:setor_publico) com erro-padrão
  # design-based via contrast_combo() (covariância completa do modelo, não soma ingênua de
  # erros-padrão individuais) -- ver docs/definicao_formalidade.md e revisão de slide 27.
  combinado <- contrast_combo(
    model, c("formal", "setor_publico", "formal:setor_publico"),
    label = "Formal + Setor público + Formal×Setor público"
  )
  out_combinado <- file.path(tables_dir, sprintf("r_setor_publico_combinado_%s.csv", dv_info$dv))
  write.csv(combinado, out_combinado, row.names = FALSE)
  cat(sprintf("saved: %s\n", out_combinado))
  print(combinado[, c("efeito_percentual_aprox", "ic95_inf", "ic95_sup", "p_valor")], digits = 4, row.names = FALSE)
}

# ---------------------------------------------------------------------------
# Parte 2: estrutura salarial por posição na ocupação (amostra ampla, 10 categorias)
# ---------------------------------------------------------------------------

cat("\n################ Parte 2: estrutura salarial por posicao_ocupacao_grupo (amostra ampla) ################\n")

common$posicao_ocupacao_grupo <- relevel(factor(common$posicao_ocupacao_grupo), ref = "privado_sem_carteira")

RHS_POSICAO <- paste(
  "factor(posicao_ocupacao_grupo) + mulher + factor(raca_grupo)",
  "+ idade + idade2 + factor(escolaridade)",
  "+ factor(celula_ocup_ativ) + factor(periodo)"
)

design_full2 <- build_design(common)

for (dv_info in list(
  list(dv = "ln_renda_mensal_real", valida_col = "valida_mensal"),
  list(dv = "ln_renda_hora_real", valida_col = "valida_hora")
)) {
  idx <- common[[dv_info$valida_col]]
  design_dv <- design_full2[idx, ]
  cat(sprintf("\n=== %s | N=%d ===\n", dv_info$dv, sum(idx)))

  model <- svyglm_capture_convergence(as.formula(paste(dv_info$dv, "~", RHS_POSICAO)), design_dv)
  cat(sprintf("[convergência bootstrap] posicao_ocupacao | %s: svyglm descartou %d/200 réplicas\n", dv_info$dv, attr(model, "n_replicas_na")))

  coef_table <- extract_coef_table(model)
  out_csv <- file.path(tables_dir, sprintf("r_posicao_ocupacao_%s.csv", dv_info$dv))
  write.csv(coef_table, out_csv, row.names = FALSE)
  cat(sprintf("saved: %s\n", out_csv))

  destaque <- coef_table[grepl("^factor\\(posicao_ocupacao_grupo\\)", coef_table$termo), ]
  destaque <- destaque[order(-destaque$efeito_percentual_aprox), ]
  print(destaque, digits = 4, row.names = FALSE)
}

# ---------------------------------------------------------------------------
# Descritivo: renda média real por posição na ocupação, sem controles (ponderado)
# ---------------------------------------------------------------------------

cat("\n################ Descritivo: renda por hora real média (ponderada), por posição ################\n")

desc <- common %>%
  filter(valida_hora) %>%
  group_by(posicao_ocupacao_grupo) %>%
  summarise(
    n_amostral = n(),
    n_ponderado = sum(peso),
    renda_hora_media = weighted.mean(renda_hora_real, peso)
  ) %>%
  arrange(desc(renda_hora_media))

print(desc, n = Inf)
out_desc <- file.path(tables_dir, "r_posicao_ocupacao_descritivo.csv")
write.csv(desc, out_desc, row.names = FALSE)
cat(sprintf("saved: %s\n", out_desc))
