---
name: text-as-data
description: Use em qualquer trabalho metodológico ou estatístico sobre a base de classificações — validação, ponte entre modelos, DSL, bootstrap, agregação, reporte de métricas — e ao redigir a seção de método do artigo.
---

# Text-as-data para a Caixa de Conversão

## Enquadramento (usar esta linguagem no artigo)

A tarefa é **stance detection** (posição frente a um alvo definido), não análise de sentimento. O pipeline é um instrumento de medição em 4 estágios, cada um com erro medido, não assumido: recuperação (recall auditado), digitalização (spot-check de transcrição), medição (validação humana por fase + ponte entre modelos), agregação (bootstrap + DSL).

## Receitas

### Validação contra humano (replicar o protocolo do piloto)
Piloto 1906 (gemini-1.5-pro): κ de Cohen = 0.712, ρ de Spearman = 0.670, viés Bland-Altman -0.22 n.s. Qualquer validação nova reporta as três estatísticas, na mesma ordem, com n da amostra.

### Ponte entre modelos (obrigatória após troca de modelo)
Reclassificar ~40-50 edições de 1906 já classificadas pelo modelo antigo. Reportar: concordância novo×antigo (κ, ρ) E novo×humano (κ, ρ). A segunda importa mais: o modelo novo precisa concordar com o humano pelo menos tanto quanto o antigo concordava.

### Validação por fase do codebook
~30 edições por fase (1907-09, 1910-13, 1914) codificadas pelo Pedro a partir das transcrições, cegas ao rótulo do modelo. κ por fase. Se κ de uma fase < ~0.6, revisar o bloco do codebook daquela fase ANTES de rodar o lote completo.

### Auditoria de recall
~15 edições sem hit por jornal, estratificadas por fase. Taxa de falso negativo por jornal. Se > ~10% em algum jornal, ampliar termos de busca antes de fechar o corpus.

### DSL (design-based supervised learning; Egami et al. 2023)
Para estatísticas descritivas finais (shares, médias por jornal×período): tratar rótulos do LLM como surrogate e os códigos humanos (amostra aleatória, ~130 edições acumuladas) como gold. Estimador corrige o viés de classificação e dá erros-padrão válidos. Implementação: pacote `dsl` (R) ou implementação própria em Python (momento amostral: gold - surrogate na amostra dourada).

### Bootstrap
Reamostrar edições (não dias de calendário) com reposição, por jornal; IC de 95% para shares e médias mensais. Séries suavizadas (média móvel/loess) sempre com banda.

### Agregação
Resultado principal em shares por categoria (5 categorias; "Neutral/Factual" ≠ "Mixed/Ambiguous", nunca fundir). Média do score como resumo secundário. Não interpretar diferenças pequenas de média de escala ordinal sem olhar os shares.

## Referências canônicas (para a seção de método)

Grimmer, Roberts & Stewart (2022) *Text as Data* · Gentzkow, Kelly & Taddy (2019, *JEL*) · Gilardi, Alizadeh & Kubli (2023, *PNAS*) · Ziems et al. (2024, *Computational Linguistics*) · Egami et al. (2023, NeurIPS; DSL) · Spirling (2023, *Nature*; reprodutibilidade de modelos fechados) · Eric Brasil (pyHDB; metodologia de busca na HDB).

## Regras de reporte

Versão exata do modelo + data + temperatura em toda tabela de resultados. Prompts citados por caminho no repo e hash do commit. Limitações com número, não com adjetivo.
