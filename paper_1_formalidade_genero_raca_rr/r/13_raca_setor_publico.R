# Raça x Setor público: o gap racial (em particular indígena) é diferente no setor público vs.
# privado? Pergunta motivada pela revisão do Eixo 3 -- o gap indígena mais que dobra entre
# formais (r/04_margins_contrasts.R), e Roraima tem peso atípico do setor público (23,7% dos
# ocupados). Sem essa interação, não dá para saber se o gap "entre formais" maior é uma
# característica da formalidade em si, ou da composição público/privado dentro da formalidade.
#
# Especificação: adiciona factor(raca_grupo):setor_publico ao modelo de setor público
# (r/07_setor_publico.R), SEM interação tripla formal:raça:setor_publico -- a amostra de
# Roraima (sobretudo indígena) não sustenta uma tripla com precisão razoável. A interação dupla
# já responde a pergunta central: o gap racial (mantendo formal fixo) difere por setor?
#
# Amostra restrita (empregados) -- mesma da análise de setor público original.

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
restrita_idx <- common$empregado_restrito == 1
design_restrita <- design_full[restrita_idx, ]
data_restrita <- common[restrita_idx, ]

RACA_NIVEIS <- c("preto", "pardo", "indigena")

RHS <- paste(
  "formal + mulher + formal:mulher",
  "+ factor(raca_grupo) + formal:factor(raca_grupo) + mulher:factor(raca_grupo)",
  "+ setor_publico + formal:setor_publico + factor(raca_grupo):setor_publico",
  "+ idade + idade2 + factor(escolaridade)",
  "+ factor(celula_ocup_ativ) + factor(periodo)"
)

extract_coef_table <- function(model) {
  s <- as.data.frame(summary(model)$coefficients)
  s$termo <- rownames(s)
  names(s) <- c("coeficiente", "erro_padrao", "t_valor", "p_valor", "termo")
  s <- s[, c("termo", "coeficiente", "erro_padrao", "p_valor")]
  rownames(s) <- NULL
  s
}

all_contrasts <- list()

for (dv_info in list(
  list(dv = "ln_renda_mensal_real", valida_col = "valida_mensal"),
  list(dv = "ln_renda_hora_real", valida_col = "valida_hora")
)) {
  idx <- data_restrita[[dv_info$valida_col]]
  design_dv <- design_restrita[idx, ]
  cat(sprintf("\n=== Raça x Setor público | %s | N=%d ===\n", dv_info$dv, sum(idx)))

  model <- svyglm_capture_convergence(as.formula(paste(dv_info$dv, "~", RHS)), design_dv)
  cat(sprintf("[convergência bootstrap] raca_setor_publico | %s: svyglm descartou %d/200 réplicas\n", dv_info$dv, attr(model, "n_replicas_na")))

  coef_table <- extract_coef_table(model)
  out_csv <- file.path(tables_dir, sprintf("r_raca_setor_publico_%s.csv", dv_info$dv))
  write.csv(coef_table, out_csv, row.names = FALSE)
  cat(sprintf("saved: %s\n", out_csv))

  destaque <- coef_table[grepl("factor\\(raca_grupo\\).*setor_publico|setor_publico.*factor\\(raca_grupo\\)", coef_table$termo), ]
  print(destaque, digits = 4, row.names = FALSE)

  # Tabela 2x2 por raça: gap (informal/formal) x (privado/público), com erro-padrão
  # design-based via contrast_combo() -- responde diretamente "o gap indígena maior entre
  # formais é uma característica da formalidade ou do setor onde os formais indígenas estão
  # concentrados?".
  rows <- list()
  for (raca in RACA_NIVEIS) {
    termo_raca <- sprintf("factor(raca_grupo)%s", raca)
    termo_formal_raca <- sprintf("formal:factor(raca_grupo)%s", raca)
    termo_publico_raca <- sprintf("factor(raca_grupo)%s:setor_publico", raca)

    rows[[sprintf("%s_informal_privado", raca)]] <- contrast_combo(
      model, c(termo_raca), sprintf("%s vs. branco, informal, privado/doméstico", raca)
    )
    rows[[sprintf("%s_formal_privado", raca)]] <- contrast_combo(
      model, c(termo_raca, termo_formal_raca), sprintf("%s vs. branco, formal, privado/doméstico", raca)
    )
    rows[[sprintf("%s_informal_publico", raca)]] <- contrast_combo(
      model, c(termo_raca, termo_publico_raca), sprintf("%s vs. branco, informal, público", raca)
    )
    rows[[sprintf("%s_formal_publico", raca)]] <- contrast_combo(
      model, c(termo_raca, termo_formal_raca, termo_publico_raca), sprintf("%s vs. branco, formal, público", raca)
    )
    rows[[sprintf("%s_diferenca_publico_privado", raca)]] <- contrast_combo(
      model, c(termo_publico_raca), sprintf("Diferença do gap de %s (público - privado)", raca)
    )
  }
  contrast_table <- dplyr::bind_rows(rows, .id = "id")
  contrast_table$dv <- dv_info$dv
  all_contrasts[[dv_info$dv]] <- contrast_table

  print(contrast_table[, c("contraste", "efeito_percentual_aprox", "p_valor")], digits = 4, row.names = FALSE)

  out_contrastes <- file.path(tables_dir, sprintf("r_raca_setor_publico_contrastes_%s.csv", dv_info$dv))
  write.csv(contrast_table, out_contrastes, row.names = FALSE)
  cat(sprintf("saved: %s\n", out_contrastes))
}

final <- dplyr::bind_rows(all_contrasts)
out_final <- file.path(tables_dir, "r_raca_setor_publico_contrastes_todos.csv")
write.csv(final, out_final, row.names = FALSE)
cat(sprintf("\nsaved: %s\n", out_final))
