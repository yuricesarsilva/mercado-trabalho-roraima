# Bloco C3 do plano de reforma (docs/plano_reforma_econometrica.md): tendência temporal em R.
# Replica scripts/09_estimate_trends.py (já correto: interações termo:Ano estimadas diretamente
# no microdado, com toda a covariância, não numa segunda regressão sobre coeficientes extraídos)
# usando o desenho amostral completo (bootstrap) e `raca_grupo` no lugar de `preto_pardo`.
#
# Especificação M4 (FE ocupação x atividade) + inclinação linear termo:Ano por termo. Ano não
# entra sozinho como termo principal porque já é absorvido por factor(periodo) (Q4-only, os
# 10 períodos coincidem com os 10 anos).

suppressPackageStartupMessages({
  library(survey)
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

RHS_TENDENCIA <- paste(
  "formal + mulher + formal:mulher",
  "+ factor(raca_grupo) + formal:factor(raca_grupo) + mulher:factor(raca_grupo)",
  "+ idade + idade2 + factor(escolaridade)",
  "+ factor(celula_ocup_ativ) + factor(periodo)",
  "+ formal:Ano + mulher:Ano + factor(raca_grupo):Ano"
)

model <- svyglm_capture_convergence(as.formula(paste("ln_renda_hora_real ~", RHS_TENDENCIA)), design_hora)
cat(sprintf("[convergência bootstrap] tendência linear (hora): svyglm descartou %d/200 réplicas\n", attr(model, "n_replicas_na")))

s <- as.data.frame(summary(model)$coefficients)
s$termo <- rownames(s)
names(s) <- c("coeficiente", "erro_padrao", "t_valor", "p_valor", "termo")
s <- s[, c("termo", "coeficiente", "erro_padrao", "p_valor")]
rownames(s) <- NULL

TREND_TERMS <- c(
  "formal:Ano", "mulher:Ano",
  "factor(raca_grupo)preto:Ano", "factor(raca_grupo)pardo:Ano", "factor(raca_grupo)indigena:Ano"
)
trend <- s[s$termo %in% TREND_TERMS, ]
trend$efeito_percentual_aprox_por_ano <- (exp(trend$coeficiente) - 1) * 100

out_csv <- file.path(tables_dir, "r_tendencia_linear.csv")
write.csv(trend, out_csv, row.names = FALSE)
cat(sprintf("saved: %s\n", out_csv))
cat("\n--- Tendência linear (renda por hora real, R/survey) ---\n")
print(trend, digits = 4, row.names = FALSE)

out_full <- file.path(tables_dir, "r_tendencia_linear_completo.csv")
write.csv(s, out_full, row.names = FALSE)
cat(sprintf("saved: %s\n", out_full))
