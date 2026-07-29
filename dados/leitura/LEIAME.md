# Registros da leitura

Quatro arquivos, três estatutos diferentes. Nenhum deles é instrumento de medição.

## `fichas_leitura.csv`

Amostra de leitura gerada por `pipeline/triagem/amostra_leitura.py`, semente 20260728.
185 peças com identificação pré-preenchida e 15 campos a preencher na leitura.
Protocolo em `docs/plano-leitura-fases.md`.

Ler na página, não na coluna `texto` de `amostra_para_rotular.csv`. Essa coluna é
reconstrução do `claude-sonnet-5` e falha de três maneiras medidas em 2026-07-28:
interpola resumo próprio entre colchetes (3,8% das peças, 13,3% dos editoriais), sangra
para a coluna vizinha da página e, em ao menos um caso, entrega artigo diferente. O
campo `ocr_contexto` é a âncora confiável, por ser OCR determinístico da Hemeroteca.

## `auditoria_recall_edicoes.csv`

64 edições sem nenhuma menção no censo, sorteadas por fase e jornal. Base da auditoria
de falso negativo prevista na CLAUDE.md.

## `marcos_cronologicos.csv` e `debates.csv`

**Sementes, não inventários.** Foram extraídos da leitura das 28 peças de editorial
substantivo em 2026-07-28 e cobrem só o que essas peças mostraram. Crescem por adição a
cada rodada de leitura, do corpus e da literatura.

Campo `status`:

- `confirmado`: afirmado explicitamente na fonte citada em `fonte_ref`;
- `a_confirmar`: a fonte afirma, mas há divergência de data, número de lei ou valor que
  exige conferência na página ou na literatura;
- `aberto` (só em `debates.csv`): debate com os dois polos documentados;
- `pouco_documentado`: debate identificado a partir de uma única peça, sem contraditório
  observado ainda.

`fonte_ref` aponta para `item_id` de `dados/triagem/amostra_para_rotular.csv`, que por
sua vez leva a `source_identifier` e página.

O propósito destes dois registros é o mapeamento exaustivo de debates, agentes,
posições e marcos ao longo do tempo. Promover esse mapeamento a estimando da
dissertação é decisão de Pedro e precisa de registro em `docs/decisoes.md`, porque muda
o construto e não apenas a organização do material.
