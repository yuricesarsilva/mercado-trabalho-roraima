# Bloco B2 do plano de reforma (docs/plano_reforma_econometrica.md): interpretação correta
# das interações. No modelo com `formal + mulher + formal:mulher`, o coeficiente de `mulher`
# sozinho é o gap mulher-homem ENTRE INFORMAIS, não o gap geral; o gap entre formais é
# `mulher + formal:mulher`. Este script calcula os 4 grupos previstos (Homem/Mulher x
# Informal/Formal) e o equivalente por raça, com erro-padrão design-based
# (contrast_combo() em lib_pnadc.R, mesma técnica de soma de coeficientes com covariância já
# usada em scripts/09_estimate_trends.py::year_effects()), para a especificação M4 (FE
# ocupação x atividade) de cada amostra x variável dependente.

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

years <- 2016:2025
quarter <- 4
rr_uf_code <- 14

common <- load_or_build_common(project_dir, years, quarter, rr_uf_code)
design_full <- build_design(common)
restrita_idx <- common$empregado_restrito == 1
designs <- list(ampla = design_full, restrita = design_full[restrita_idx, ])
samples <- list(ampla = common, restrita = common[restrita_idx, ])

# Especificação M4 (FE ocupação x atividade) -- mesma do Bloco B1.
RHS_M4 <- paste(
  "formal + mulher + formal:mulher",
  "+ factor(raca_grupo) + formal:factor(raca_grupo) + mulher:factor(raca_grupo)",
  "+ idade + idade2 + factor(escolaridade)",
  "+ factor(celula_ocup_ativ) + factor(periodo)"
)

RACA_NIVEIS <- c("preto", "pardo", "indigena")

all_contrasts <- list()

for (amostra in names(designs)) {
  design <- designs[[amostra]]
  data_amostra <- samples[[amostra]]

  for (dv_info in list(
    list(label = "ln_renda_mensal_real", valida_col = "valida_mensal"),
    list(label = "ln_renda_hora_real", valida_col = "valida_hora")
  )) {
    dv_label <- dv_info$label
    idx <- data_amostra[[dv_info$valida_col]]
    design_dv <- design[idx, ]

    formula_str <- paste(dv_label, "~", RHS_M4)
    key <- sprintf("%s_%s", amostra, dv_label)
    cat(sprintf("\n=== Margins/contrasts: %s (M4) ===\n", key))

    model <- svyglm_capture_convergence(as.formula(formula_str), design_dv)
    cat(sprintf("[convergência bootstrap] %s (M4): svyglm descartou %d/200 réplicas\n", key, attr(model, "n_replicas_na")))

    rows <- list()

    # Gênero: gap entre informais vs. gap entre formais
    rows[["genero_gap_informal"]] <- contrast_combo(model, c("mulher"), "Mulher vs. homem, entre informais")
    rows[["genero_gap_formal"]] <- contrast_combo(model, c("mulher", "formal:mulher"), "Mulher vs. homem, entre formais")
    rows[["genero_diferenca_formal_informal"]] <- contrast_combo(model, c("formal:mulher"), "Diferença do gap de gênero (formal - informal)")

    # Raça: gap entre informais vs. gap entre formais, por categoria (ref.: branco)
    for (raca in RACA_NIVEIS) {
      termo_raca <- sprintf("factor(raca_grupo)%s", raca)
      termo_inter <- sprintf("formal:factor(raca_grupo)%s", raca)
      rows[[sprintf("raca_%s_gap_informal", raca)]] <- contrast_combo(
        model, c(termo_raca), sprintf("%s vs. branco, entre informais", raca)
      )
      rows[[sprintf("raca_%s_gap_formal", raca)]] <- contrast_combo(
        model, c(termo_raca, termo_inter), sprintf("%s vs. branco, entre formais", raca)
      )
      rows[[sprintf("raca_%s_diferenca_formal_informal", raca)]] <- contrast_combo(
        model, c(termo_inter), sprintf("Diferença do gap de %s (formal - informal)", raca)
      )
    }

    # Formalidade: prêmio para homem branco vs. mulher preta/parda/indígena (interseccional)
    rows[["formal_homem_branco"]] <- contrast_combo(model, c("formal"), "Prêmio de formalidade, homem branco")
    for (raca in RACA_NIVEIS) {
      termo_raca_mulher <- sprintf("mulher:factor(raca_grupo)%s", raca)
      rows[[sprintf("formal_mulher_%s", raca)]] <- contrast_combo(
        model,
        c("formal", "formal:mulher", sprintf("formal:factor(raca_grupo)%s", raca)),
        sprintf("Prêmio de formalidade, mulher %s", raca)
      )
    }

    contrast_table <- dplyr::bind_rows(rows, .id = "id")
    contrast_table$amostra <- amostra
    contrast_table$dv <- dv_label
    all_contrasts[[key]] <- contrast_table

    print(contrast_table[, c("contraste", "efeito_percentual_aprox", "p_valor")], digits = 4, row.names = FALSE)

    out_csv <- file.path(tables_dir, sprintf("r_contrastes_%s.csv", key))
    write.csv(contrast_table, out_csv, row.names = FALSE)
    cat(sprintf("saved: %s\n", out_csv))
  }
}

final <- dplyr::bind_rows(all_contrasts)
out_final <- file.path(tables_dir, "r_contrastes_todos.csv")
write.csv(final, out_final, row.names = FALSE)
cat(sprintf("\nsaved: %s\n", out_final))
