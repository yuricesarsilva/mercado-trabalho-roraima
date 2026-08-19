# Decomposição sequencial do gap de gênero: accounting exercise para descobrir qual dimensão
# de composição "esconde" o gap bruto de mulher em Roraima (bruto ~-3% vs. condicional ~-18%
# na renda por hora). Sequência de modelos M0->M6, cada um adicionando UMA dimensão à anterior,
# só com `mulher` como tratamento (sem formal/raça, para isolar o efeito de cada controle sobre
# o coeficiente de gênero); M7 (+horas) é computado separadamente como checagem adicional, não
# faz parte do gráfico principal -- ver Eixo 2 da literatura de revisão.
#
# M0: mulher
# M1: M0 + idade + idade^2                         (demografia)
# M2: M1 + escolaridade                            (educação)
# M3: M2 + atividade_grupo                         (atividade)
# M4: M3 + ocupacao_grupo                          (ocupação, FE separado -- robustez/apoio)
# M5: M2 + célula ocupação x atividade (conjunta)  (ocupação x atividade)
# M6: M5 + setor_publico                           (setor público)
# M7: M6 + horas_semanais_principal                (separado -- accounting adicional)
#
# Renda por hora real, amostra ampla, desenho amostral bootstrap completo (200 réplicas).

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
idx_hora <- common$valida_hora
design_hora <- design_full[idx_hora, ]
cat(sprintf("N (renda por hora real, amostra ampla): %d\n", sum(idx_hora)))

rhs_list <- list(
  M0 = "mulher",
  M1 = "mulher + idade + idade2",
  M2 = "mulher + idade + idade2 + factor(escolaridade)",
  M3 = "mulher + idade + idade2 + factor(escolaridade) + factor(atividade_grupo)",
  M4 = "mulher + idade + idade2 + factor(escolaridade) + factor(atividade_grupo) + factor(ocupacao_grupo)",
  M5 = "mulher + idade + idade2 + factor(escolaridade) + factor(celula_ocup_ativ)",
  M6 = "mulher + idade + idade2 + factor(escolaridade) + factor(celula_ocup_ativ) + setor_publico",
  M7 = "mulher + idade + idade2 + factor(escolaridade) + factor(celula_ocup_ativ) + setor_publico + horas_semanais_principal"
)

rotulos <- c(
  M0 = "Bruto (só mulher)", M1 = "+ Demografia", M2 = "+ Educação",
  M3 = "+ Atividade", M4 = "+ Ocupação (FE separado)",
  M5 = "+ Ocupação×Atividade", M6 = "+ Setor público", M7 = "+ Horas (separado)"
)

extract_mulher <- function(model, m_label) {
  s <- summary(model)$coefficients
  r <- s["mulher", ]
  data.frame(
    modelo = m_label, rotulo = rotulos[[m_label]],
    coeficiente = r["Estimate"], erro_padrao = r["Std. Error"], p_valor = r["Pr(>|t|)"],
    efeito_percentual_aprox = (exp(r["Estimate"]) - 1) * 100,
    row.names = NULL
  )
}

rows <- list()
for (m_label in names(rhs_list)) {
  formula_str <- paste("ln_renda_hora_real ~", rhs_list[[m_label]])
  cat(sprintf("\n=== %s: %s ===\n", m_label, rotulos[[m_label]]))

  model <- svyglm_capture_convergence(as.formula(formula_str), design_hora)
  cat(sprintf(
    "[convergência bootstrap] %s: svyglm descartou %d/200 réplicas\n",
    m_label, attr(model, "n_replicas_na")
  ))

  row_ <- extract_mulher(model, m_label)
  rows[[m_label]] <- row_
  print(row_[, c("modelo", "rotulo", "efeito_percentual_aprox", "p_valor")], digits = 4, row.names = FALSE)
}

result <- dplyr::bind_rows(rows)
out_csv <- file.path(tables_dir, "r_decomposicao_genero.csv")
write.csv(result, out_csv, row.names = FALSE)
cat(sprintf("\nsaved: %s\n", out_csv))
print(result[, c("modelo", "rotulo", "efeito_percentual_aprox", "p_valor")], digits = 4, row.names = FALSE)
