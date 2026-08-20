# Decomposição sequencial do gap racial (equivalente ao exercício de gênero em
# r/11_decomposicao_sequencial_genero.R): accounting exercise para descobrir qual dimensão de
# composição explica a queda do gap racial bruto (~-35%, preto/pardo vs. branco) ao condicional
# (~-8%). Sequência de modelos M0->M6, cada um adicionando UMA dimensão à anterior, só com
# `factor(raca_grupo)` como tratamento (sem formal/mulher, para isolar o efeito de cada
# controle sobre os três coeficientes raciais simultaneamente); M4 (ocupação, FE separado) é
# computado para robustez/apoio, não faz parte do gráfico principal.
#
# M0: factor(raca_grupo)
# M1: M0 + idade + idade^2                         (demografia)
# M2: M1 + escolaridade                            (educação)
# M3: M2 + atividade_grupo                         (atividade)
# M4: M3 + ocupacao_grupo                          (ocupação, FE separado -- robustez/apoio)
# M5: M2 + célula ocupação x atividade (conjunta)  (ocupação x atividade)
# M6: M5 + setor_publico                           (setor público)
#
# Hipótese da literatura (Eixo 3: Soares 2000; Campante, Crespo & Leite; Arcand & d'Hombres):
# ao contrário do gênero (onde a vantagem educacional feminina MASCARA o gap), a desigualdade
# educacional pode AMPLIFICAR o gap racial bruto -- ou seja, esperamos que `educação` REDUZA
# (não amplie) o coeficiente racial ao entrar no modelo. Testado empiricamente abaixo, não
# assumido.
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

RACA_NIVEIS <- c("preto", "pardo", "indigena")
RACA_TERMS <- sprintf("factor(raca_grupo)%s", RACA_NIVEIS)

rhs_list <- list(
  M0 = "factor(raca_grupo)",
  M1 = "factor(raca_grupo) + idade + idade2",
  M2 = "factor(raca_grupo) + idade + idade2 + factor(escolaridade)",
  M3 = "factor(raca_grupo) + idade + idade2 + factor(escolaridade) + factor(atividade_grupo)",
  M4 = "factor(raca_grupo) + idade + idade2 + factor(escolaridade) + factor(atividade_grupo) + factor(ocupacao_grupo)",
  M5 = "factor(raca_grupo) + idade + idade2 + factor(escolaridade) + factor(celula_ocup_ativ)",
  M6 = "factor(raca_grupo) + idade + idade2 + factor(escolaridade) + factor(celula_ocup_ativ) + setor_publico"
)

rotulos <- c(
  M0 = "Bruto (só raça)", M1 = "+ Demografia", M2 = "+ Educação",
  M3 = "+ Atividade", M4 = "+ Ocupação (FE separado)",
  M5 = "+ Ocupação×Atividade", M6 = "+ Setor público"
)

extract_raca <- function(model, m_label) {
  s <- summary(model)$coefficients
  rows <- lapply(RACA_NIVEIS, function(r) {
    termo <- sprintf("factor(raca_grupo)%s", r)
    v <- s[termo, ]
    data.frame(
      modelo = m_label, rotulo = rotulos[[m_label]], raca = r,
      coeficiente = v["Estimate"], erro_padrao = v["Std. Error"], p_valor = v["Pr(>|t|)"],
      efeito_percentual_aprox = (exp(v["Estimate"]) - 1) * 100,
      row.names = NULL
    )
  })
  dplyr::bind_rows(rows)
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

  row_ <- extract_raca(model, m_label)
  rows[[m_label]] <- row_
  print(row_[, c("modelo", "raca", "efeito_percentual_aprox", "p_valor")], digits = 4, row.names = FALSE)
}

result <- dplyr::bind_rows(rows)
out_csv <- file.path(tables_dir, "r_decomposicao_raca.csv")
write.csv(result, out_csv, row.names = FALSE)
cat(sprintf("\nsaved: %s\n", out_csv))
print(result[, c("modelo", "raca", "efeito_percentual_aprox", "p_valor")], digits = 4, row.names = FALSE)
