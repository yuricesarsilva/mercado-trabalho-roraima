# Bloco B2 do plano de reforma (docs/plano_reforma_econometrica.md): interpretação correta
# das interações. No modelo com `formal + mulher + formal:mulher`, o coeficiente de `mulher`
# sozinho é o gap mulher-homem ENTRE INFORMAIS, não o gap geral; o gap entre formais é
# `mulher + formal:mulher`. Este script calcula os 4 grupos previstos (Homem/Mulher x
# Informal/Formal) e o equivalente por raça, com erro-padrão design-based
# (contrast_combo() em lib_pnadc.R, mesma técnica de soma de coeficientes com covariância já
# usada em scripts/09_estimate_trends.py::year_effects()), para a especificação M4 (FE
# ocupação x atividade) de cada amostra x variável dependente.
#
# O modelo também tem Mulher:Raça e Formal:Raça -- por isso `mulher` sozinho é o gap de
# gênero só para a raça de referência (branco), e `factor(raca_grupo)r` é o gap racial só
# para homens. Os contrastes de gênero e raça abaixo usam contrast_weighted() (average
# marginal contrast, ponderado pela distribuição observada de raça/gênero na amostra) para
# reportar um gap populacional, não o de um subgrupo específico -- ver revisão de slides 19/38.

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

    # Shares populacionais (ponderadas, amarelo excluído) da amostra efetivamente estimada --
    # usadas para os "average marginal contrasts" abaixo. Como o modelo tem Mulher:Raça e
    # Formal:Raça, o coeficiente de `mulher` sozinho é o gap de gênero só para a raça de
    # referência (branco), e o de `factor(raca_grupo)r` é o gap racial só para homens (mulher
    # de referência); sem essa ponderação, "gap de gênero"/"gap racial" mistura a estimativa de
    # um subgrupo com uma manchete que soa geral -- ver revisão de slides 19/38.
    data_dv <- data_amostra[idx, ]
    data_dv_raca <- data_dv[!is.na(data_dv$raca_grupo), ]
    peso_total <- sum(data_dv_raca$peso)
    share_raca <- stats::setNames(
      sapply(RACA_NIVEIS, function(r) sum(data_dv_raca$peso[data_dv_raca$raca_grupo == r]) / peso_total),
      RACA_NIVEIS
    )
    share_mulher <- sum(data_dv_raca$peso[data_dv_raca$mulher == 1]) / peso_total
    cat(sprintf(
      "  shares (ponderados): mulher=%.3f, preto=%.3f, pardo=%.3f, indigena=%.3f\n",
      share_mulher, share_raca["preto"], share_raca["pardo"], share_raca["indigena"]
    ))

    rows <- list()

    # Gênero: gap entre informais vs. gap entre formais, MÉDIA ponderada pela distribuição
    # racial observada (average marginal contrast) -- não só o gap para brancos.
    pesos_raca_mulher <- stats::setNames(
      as.numeric(share_raca), sprintf("mulher:factor(raca_grupo)%s", names(share_raca))
    )
    rows[["genero_gap_informal"]] <- contrast_weighted(
      model, c(mulher = 1, pesos_raca_mulher),
      "Mulher vs. homem, entre informais (média ponderada por raça)"
    )
    rows[["genero_gap_formal"]] <- contrast_weighted(
      model, c(mulher = 1, `formal:mulher` = 1, pesos_raca_mulher),
      "Mulher vs. homem, entre formais (média ponderada por raça)"
    )
    rows[["genero_diferenca_formal_informal"]] <- contrast_combo(model, c("formal:mulher"), "Diferença do gap de gênero (formal - informal)")

    # Raça: gap entre informais vs. gap entre formais, por categoria (ref.: branco), MÉDIA
    # ponderada pela distribuição de gênero observada -- não só o gap para homens.
    for (raca in RACA_NIVEIS) {
      termo_raca <- sprintf("factor(raca_grupo)%s", raca)
      termo_inter <- sprintf("formal:factor(raca_grupo)%s", raca)
      termo_mulher_raca <- sprintf("mulher:factor(raca_grupo)%s", raca)
      rows[[sprintf("raca_%s_gap_informal", raca)]] <- contrast_weighted(
        model, stats::setNames(c(1, share_mulher), c(termo_raca, termo_mulher_raca)),
        sprintf("%s vs. branco, entre informais (média ponderada por gênero)", raca)
      )
      rows[[sprintf("raca_%s_gap_formal", raca)]] <- contrast_weighted(
        model, stats::setNames(c(1, 1, share_mulher), c(termo_raca, termo_inter, termo_mulher_raca)),
        sprintf("%s vs. branco, entre formais (média ponderada por gênero)", raca)
      )
      rows[[sprintf("raca_%s_diferenca_formal_informal", raca)]] <- contrast_combo(
        model, c(termo_inter), sprintf("Diferença do gap de %s (formal - informal)", raca)
      )
    }

    # Prêmio de formalidade populacional: `formal` sozinho interage com Mulher e Raça também,
    # então seu coeficiente puro é o prêmio só para homem branco -- média ponderada pelas
    # distribuições de gênero e raça observadas (sem termo triplo formal:mulher:raça no
    # modelo, os pesos marginais de gênero e raça se somam independentemente ao termo-base).
    pesos_raca_formal <- stats::setNames(
      as.numeric(share_raca), sprintf("formal:factor(raca_grupo)%s", names(share_raca))
    )
    rows[["formal_gap_geral"]] <- contrast_weighted(
      model, c(formal = 1, `formal:mulher` = share_mulher, pesos_raca_formal),
      "Formal vs. informal (média ponderada por gênero e raça)"
    )

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
