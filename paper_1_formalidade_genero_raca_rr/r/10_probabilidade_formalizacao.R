# Probabilidade condicional de inserção formal: P(Formal_i=1) = F(Mulher_i, Raça_i,
# Escolaridade_i, Idade_i, FE_ocupação×atividade, FE_período), logit ponderado, com efeitos
# marginais médios (AME, em pontos percentuais) via desenho bootstrap completo (200 réplicas).
#
# Distingue "acesso à formalidade" (este script) de "retorno associado à formalidade" (o modelo
# de rendimentos em r/02_estimate_nested.R) -- ver docs/definicao_formalidade.md e a literatura de
# segmentação/seleção do mercado de trabalho (Eixo 1). Não é uma leitura causal: escolaridade,
# ocupação e setor são potencialmente endógenos à própria decisão de formalização.
#
# Efeitos marginais médios (AME): para cada termo de interesse (mulher, raça), a mudança
# discreta média na probabilidade prevista de ser formal -- refita o modelo e recalcula o AME em
# cada uma das 200 réplicas bootstrap via survey::withReplicates(), a mesma lógica de variância
# design-based já usada em contrast_combo() (lib_pnadc.R), mas aqui aplicada a uma estatística
# não-linear (diferença de probabilidades previstas) em vez de soma de coeficientes.

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

RACA_NIVEIS <- c("preto", "pardo", "indigena")

RHS_ACESSO <- paste(
  "mulher + factor(raca_grupo)",
  "+ idade + idade2 + factor(escolaridade)",
  "+ factor(celula_ocup_ativ) + factor(periodo)"
)
FORMULA_ACESSO <- as.formula(paste("formal ~", RHS_ACESSO))

# ---------------------------------------------------------------------------
# 1. Dados e desenhos amostrais (mesma amostra comum e células do modelo de rendimentos)
# ---------------------------------------------------------------------------

common <- load_or_build_common(project_dir, years, quarter, rr_uf_code)
design_full <- build_design(common)
restrita_idx <- common$empregado_restrito == 1

designs <- list(ampla = design_full, restrita = design_full[restrita_idx, ])

# ---------------------------------------------------------------------------
# 2. Logit ponderado (coeficientes em log-odds, robustez/transparência) -- desenho completo
# ---------------------------------------------------------------------------

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
  cat(sprintf("\n=== Logit (log-odds) probabilidade de formalização: %s | N=%d ===\n", amostra, nrow(design$variables)))

  model <- svyglm_capture_convergence(FORMULA_ACESSO, design, family = quasibinomial())
  cat(sprintf(
    "[convergência bootstrap] prob_formal_logit | %s: svyglm descartou %d/200 réplicas\n",
    amostra, attr(model, "n_replicas_na")
  ))

  coef_table <- extract_coef_table(model)
  out_csv <- file.path(tables_dir, sprintf("r_prob_formal_logit_%s.csv", amostra))
  write.csv(coef_table, out_csv, row.names = FALSE)
  cat(sprintf("saved: %s\n", out_csv))

  destaque <- coef_table[coef_table$termo %in% c(
    "mulher", "factor(raca_grupo)preto", "factor(raca_grupo)pardo", "factor(raca_grupo)indigena"
  ), ]
  print(destaque, digits = 4, row.names = FALSE)
}

# ---------------------------------------------------------------------------
# 3. Efeitos marginais médios (AME, p.p.) -- mudança discreta média na probabilidade prevista,
#    refeita em cada réplica bootstrap via withReplicates().
# ---------------------------------------------------------------------------

# theta(w, data): recebe o vetor de pesos da réplica (ou peso amostral, na chamada do ponto
# estimado) e o data.frame do design; reajusta o logit com esse peso e devolve o AME de cada
# termo. Restringe à amostra efetivamente usada na estimação (raca_grupo não-NA, exclui
# amarelo -- ver docs/definicao_raca.md) para que o AME seja calculado sobre as mesmas
# observações do ajuste, não sobre linhas que o modelo descartou por NA.
make_theta_ame <- function(formula_obj) {
  function(w, data) {
    keep <- !is.na(data$raca_grupo)
    data_est <- data[keep, ]
    # glm()/lm() resolvem `weights=` como uma "extra variable" do model.frame: se o símbolo
    # não é uma coluna literal de `data`, cai para o ambiente onde a FÓRMULA foi criada (não
    # o frame local desta closure) -- por isso o peso precisa entrar como coluna de data_est,
    # nunca como símbolo solto (`weights = w_est`); mesma armadilha documentada em
    # check_replicate_convergence() (lib_pnadc.R).
    data_est$.peso_ame <- w[keep]

    # glm() emite warning (não erro) em separação quase-perfeita de alguma célula esparsa --
    # o ajuste ainda é retornado (coeficiente daquela célula só fica inflado), suficiente para
    # calcular probabilidades previstas/AME; só tryCatch(error=) é necessário aqui.
    fit <- tryCatch(
      stats::glm(formula_obj, data = data_est, weights = .peso_ame, family = stats::quasibinomial()),
      error = function(e) NULL
    )
    nomes <- c("mulher", RACA_NIVEIS)
    if (is.null(fit)) {
      out <- rep(NA_real_, length(nomes))
      names(out) <- nomes
      return(out)
    }

    d1 <- data_est
    d1$mulher <- 1
    d0 <- data_est
    d0$mulher <- 0
    # na.rm=TRUE: numa réplica bootstrap específica, uma célula esparsa pode ficar com peso
    # 0 em todas as suas observações, deixando aquele coeficiente não-identificado (NA) só
    # NESSA réplica -- exclui as previsões afetadas do AME dessa réplica em vez de propagar
    # NA para a réplica inteira; withReplicates() ainda usa as demais 199 normalmente.
    ame_mulher <- stats::weighted.mean(
      stats::predict(fit, newdata = d1, type = "response") - stats::predict(fit, newdata = d0, type = "response"),
      data_est$.peso_ame, na.rm = TRUE
    )

    ame_raca <- vapply(RACA_NIVEIS, function(r) {
      d1r <- data_est
      d1r$raca_grupo <- r
      d0r <- data_est
      d0r$raca_grupo <- "branco"
      stats::weighted.mean(
        stats::predict(fit, newdata = d1r, type = "response") - stats::predict(fit, newdata = d0r, type = "response"),
        data_est$.peso_ame, na.rm = TRUE
      )
    }, numeric(1))

    out <- c(ame_mulher, ame_raca)
    names(out) <- nomes
    out
  }
}

ame_resultados <- list()

for (amostra in names(designs)) {
  design <- designs[[amostra]]
  cat(sprintf("\n=== AME (p.p.) probabilidade de formalização: %s ===\n", amostra))

  theta_fn <- make_theta_ame(FORMULA_ACESSO)
  stat <- withReplicates(design, theta_fn)

  est <- as.numeric(stat)
  names(est) <- names(stat)
  se <- sqrt(diag(attr(stat, "var")))
  z <- est / se
  p_valor <- 2 * (1 - stats::pnorm(abs(z)))

  df <- data.frame(
    termo = names(est),
    ame_pp = est * 100,
    erro_padrao_pp = se * 100,
    p_valor = p_valor,
    amostra = amostra,
    row.names = NULL
  )
  ame_resultados[[amostra]] <- df
  print(df, digits = 3, row.names = FALSE)

  out_csv <- file.path(tables_dir, sprintf("r_prob_formal_ame_%s.csv", amostra))
  write.csv(df, out_csv, row.names = FALSE)
  cat(sprintf("saved: %s\n", out_csv))
}

final <- dplyr::bind_rows(ame_resultados)
out_final <- file.path(tables_dir, "r_prob_formal_ame_todos.csv")
write.csv(final, out_final, row.names = FALSE)
cat(sprintf("\nsaved: %s\n", out_final))
