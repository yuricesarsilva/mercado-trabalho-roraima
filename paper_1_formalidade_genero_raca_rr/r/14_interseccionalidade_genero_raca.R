# Interseccionalidade gênero x raça: o modelo principal (M4) já tem Mulher:Raça -- este script
# não estima nada novo, só usa o modelo já ajustado para responder, com erro-padrão design-based
# via contrast_combo() (covariância completa, não soma ingênua de variâncias individuais):
#
#   A desvantagem de "mulher X" é maior/menor do que a soma simples dos diferenciais de gênero
#   e de raça X, ou apenas aditiva?
#
# Isso é exatamente o teste de significância do termo mulher:factor(raca_grupo)X, que já está no
# modelo -- aqui só reportamos os 4 grupos (homem branco, mulher branca, homem X, mulher X) e a
# interação de forma explícita, para as três categorias raciais. Ver revisão Eixo 4 (Kolev &
# Robles, 2015; Canedo, 2019; World Bank, 2015).
#
# Renda por hora real, amostra ampla, especificação M4 (mesma de r/02_estimate_nested.R).

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

RACA_NIVEIS <- c("preto", "pardo", "indigena")

# Especificação M4 (idêntica a r/02_estimate_nested.R e r/04_margins_contrasts.R).
RHS_M4 <- paste(
  "formal + mulher + formal:mulher",
  "+ factor(raca_grupo) + formal:factor(raca_grupo) + mulher:factor(raca_grupo)",
  "+ idade + idade2 + factor(escolaridade)",
  "+ factor(celula_ocup_ativ) + factor(periodo)"
)

model <- svyglm_capture_convergence(as.formula(paste("ln_renda_hora_real ~", RHS_M4)), design_hora)
cat(sprintf("[convergência bootstrap] interseccionalidade genero x raca: svyglm descartou %d/200 réplicas\n", attr(model, "n_replicas_na")))

rows <- list()
for (raca in RACA_NIVEIS) {
  termo_raca <- sprintf("factor(raca_grupo)%s", raca)
  termo_inter <- sprintf("mulher:factor(raca_grupo)%s", raca)

  rows[[sprintf("%s_homem_branco", raca)]] <- contrast_combo(
    model, character(0), "Homem branco (referência)"
  )
  rows[[sprintf("%s_mulher_branca", raca)]] <- contrast_combo(
    model, c("mulher"), "Mulher branca"
  )
  rows[[sprintf("%s_homem", raca)]] <- contrast_combo(
    model, c(termo_raca), sprintf("Homem %s", raca)
  )
  rows[[sprintf("%s_mulher", raca)]] <- contrast_combo(
    model, c("mulher", termo_raca, termo_inter), sprintf("Mulher %s", raca)
  )
  rows[[sprintf("%s_interacao", raca)]] <- contrast_combo(
    model, c(termo_inter), sprintf("Interação mulher×%s (heterogeneidade além do aditivo)", raca)
  )
  rows[[sprintf("%s_soma_aditiva_implicaria", raca)]] <- contrast_combo(
    model, c("mulher", termo_raca), sprintf("Soma aditiva (mulher + %s, sem interação)", raca)
  )
}

# contrast_combo com terms=character(0) dá "soma vazia" (estimativa 0, SE 0) -- trata a
# referência à parte para não gerar um teste de hipótese sem sentido (z = 0/0).
result <- dplyr::bind_rows(rows, .id = "id")
result$efeito_percentual_aprox[grepl("_homem_branco$", result$id)] <- 0
result$p_valor[grepl("_homem_branco$", result$id)] <- NA

out_csv <- file.path(tables_dir, "r_interseccionalidade_genero_raca.csv")
write.csv(result, out_csv, row.names = FALSE)
cat(sprintf("saved: %s\n", out_csv))
print(result[, c("id", "contraste", "efeito_percentual_aprox", "p_valor")], digits = 4, row.names = FALSE)
