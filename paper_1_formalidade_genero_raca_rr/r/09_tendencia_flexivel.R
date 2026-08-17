# Evolução temporal ano a ano (não só a inclinação linear de r/06_tendencia_temporal.R),
# com raça desagregada (branco = referência; preto, pardo, indígena separados) e desenho
# amostral completo -- substitui a figura antiga (scripts/09_estimate_trends.py, Python/WLS,
# baseada em preto_pardo agregado com referência branco/amarelo/indígena) por uma versão
# consistente com a especificação principal M4.
#
# Interações termo:factor(periodo) estimadas diretamente no microdado (mesma lógica de
# r/06_tendencia_temporal.R); o efeito de cada ano é a soma do termo-base (ano de referência,
# 2016T4) com a interação correspondente, com erro-padrão via contrast_combo() (cov_params
# completa do modelo).

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
cat(sprintf("N (renda por hora real): %d\n", sum(idx_hora)))

RHS_FLEX <- paste(
  "formal + mulher + formal:mulher",
  "+ factor(raca_grupo) + formal:factor(raca_grupo) + mulher:factor(raca_grupo)",
  "+ idade + idade2 + factor(escolaridade)",
  "+ factor(celula_ocup_ativ) + factor(periodo)",
  "+ formal:factor(periodo) + mulher:factor(periodo) + factor(raca_grupo):factor(periodo)"
)

model <- svyglm_capture_convergence(as.formula(paste("ln_renda_hora_real ~", RHS_FLEX)), design_hora)
cat(sprintf(
  "[convergência bootstrap] tendência flexível (hora, raça desagregada): svyglm descartou %d/200 réplicas\n",
  attr(model, "n_replicas_na")
))

periods <- sort(unique(common$periodo))
reference <- periods[1]
cat(sprintf("Períodos: %s (referência: %s)\n", paste(periods, collapse = ", "), reference))

TERMS <- c("formal", "mulher", paste0("factor(raca_grupo)", c("preto", "pardo", "indigena")))

rows <- list()
for (termo in TERMS) {
  for (periodo in periods) {
    if (periodo == reference) {
      combo <- contrast_combo(model, termo, label = termo)
    } else {
      inter_name <- paste0(termo, ":factor(periodo)", periodo)
      combo <- contrast_combo(model, c(termo, inter_name), label = termo)
    }
    combo$termo <- termo
    combo$periodo <- periodo
    combo$ano <- as.integer(substr(periodo, 1, 4))
    rows[[paste(termo, periodo)]] <- combo
  }
}

result <- dplyr::bind_rows(rows)
result <- result[order(result$termo, result$ano), ]

out_csv <- file.path(tables_dir, "r_tendencia_flexivel.csv")
write.csv(result, out_csv, row.names = FALSE)
cat(sprintf("saved: %s\n", out_csv))
print(result[, c("termo", "ano", "efeito_percentual_aprox", "p_valor")], digits = 4, row.names = FALSE)
