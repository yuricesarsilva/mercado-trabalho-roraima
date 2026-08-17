# Bloco B4 do plano de reforma (docs/plano_reforma_econometrica.md): decomposição exata do
# mecanismo de jornada. Como ln(renda_mensal) = ln(renda_hora) + ln(horas_semanais) é uma
# identidade algébrica, estimar a MESMA especificação (mesma amostra, mesmos pesos, mesmo
# desenho) para as três variáveis dependentes garante, por construção:
#
#   beta_mensal = beta_hora + beta_ln(horas)
#
# Isso substitui a comparação por mecanismo do antigo scripts/06_estimate_jornada.py (que usava
# horas em nível, não em log, então a soma não batia exatamente) por uma decomposição exata:
# quanto do diferencial mensal é efeito-preço (renda por hora) vs. efeito-quantidade (horas).
#
# horas_semanais NÃO entra como covariável em nenhuma especificação aqui -- é uma das três
# variáveis dependentes, não um controle (ver reenquadramento no plano: jornada é mecanismo,
# pode bloquear o canal gênero->jornada->renda se tratada como covariável).

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

years <- 2016:2025
quarter <- 4
rr_uf_code <- 14

common <- load_or_build_common(project_dir, years, quarter, rr_uf_code)
design_full <- build_design(common)

restrita_idx <- common$empregado_restrito == 1
designs <- list(ampla = design_full, restrita = design_full[restrita_idx, ])
samples <- list(ampla = common, restrita = common[restrita_idx, ])

# Especificação M4 do Bloco B1 (FE conjunto ocupação x atividade, células esparsas agregadas
# em "outras") -- adotada aqui após o Checkpoint B mostrar que M4 tem 0/200 réplicas
# descartadas, contra 74/200 da especificação com FE separados (M3) usada na primeira rodada
# desta decomposição. Mesma escolha já usada em r/02_estimate_nested.R e
# r/04_margins_contrasts.R -- consistência entre os scripts do Bloco B.
RHS <- paste(
  "formal + mulher + formal:mulher",
  "+ factor(raca_grupo) + formal:factor(raca_grupo) + mulher:factor(raca_grupo)",
  "+ idade + idade2 + factor(escolaridade)",
  "+ factor(celula_ocup_ativ) + factor(periodo)"
)

DVS <- c("ln_renda_mensal_real", "ln_renda_hora_real", "ln_horas_semanais_principal")

KEY_TERMS <- c(
  "formal", "mulher", "formal:mulher",
  "factor(raca_grupo)preto", "factor(raca_grupo)pardo", "factor(raca_grupo)indigena"
)

extract_coef_table <- function(model) {
  s <- as.data.frame(summary(model)$coefficients)
  s$termo <- rownames(s)
  names(s) <- c("coeficiente", "erro_padrao", "t_valor", "p_valor", "termo")
  s <- s[, c("termo", "coeficiente", "erro_padrao", "p_valor")]
  rownames(s) <- NULL
  s
}

for (amostra in names(designs)) {
  design <- designs[[amostra]]
  data_amostra <- samples[[amostra]]

  valid <- !is.na(data_amostra$horas_semanais_principal) & data_amostra$horas_semanais_principal > 0 &
    data_amostra$valida_mensal & data_amostra$valida_hora
  design_v <- design[valid, ]
  data_v <- data_amostra[valid, ]
  cat(sprintf("\n=== %s: N (amostra jornada) = %d ===\n", amostra, nrow(data_v)))

  coefs_by_dv <- list()
  for (dv in DVS) {
    formula_str <- paste(dv, "~", RHS)
    model <- svyglm_capture_convergence(as.formula(formula_str), design_v)
    coef_table <- extract_coef_table(model)
    coefs_by_dv[[dv]] <- coef_table

    out_csv <- file.path(tables_dir, sprintf("r_jornada_%s_%s.csv", amostra, dv))
    write.csv(coef_table, out_csv, row.names = FALSE)
    cat(sprintf(
      "saved: %s (réplicas descartadas pelo svyglm: %d/200)\n",
      out_csv, attr(model, "n_replicas_na")
    ))
  }

  mensal <- coefs_by_dv[["ln_renda_mensal_real"]][, c("termo", "coeficiente", "erro_padrao", "p_valor")]
  hora <- coefs_by_dv[["ln_renda_hora_real"]][, c("termo", "coeficiente")]
  horas <- coefs_by_dv[["ln_horas_semanais_principal"]][, c("termo", "coeficiente")]
  names(mensal)[names(mensal) == "coeficiente"] <- "beta_mensal"
  names(hora)[names(hora) == "coeficiente"] <- "beta_hora"
  names(horas)[names(horas) == "coeficiente"] <- "beta_ln_horas"

  check <- merge(mensal, hora, by = "termo")
  check <- merge(check, horas, by = "termo")
  check$soma_hora_mais_horas <- check$beta_hora + check$beta_ln_horas
  check$diferenca_vs_mensal <- check$beta_mensal - check$soma_hora_mais_horas
  check <- check[, c(
    "termo", "beta_mensal", "beta_hora", "beta_ln_horas",
    "soma_hora_mais_horas", "diferenca_vs_mensal", "erro_padrao", "p_valor"
  )]

  cat(sprintf("\n--- Checagem da identidade beta_mensal = beta_hora + beta_ln(horas) -- %s ---\n", amostra))
  print(check[check$termo %in% KEY_TERMS, ], digits = 6, row.names = FALSE)

  out_check <- file.path(tables_dir, sprintf("r_jornada_identidade_%s.csv", amostra))
  write.csv(check, out_check, row.names = FALSE)
  cat(sprintf("saved: %s\n", out_check))
}
