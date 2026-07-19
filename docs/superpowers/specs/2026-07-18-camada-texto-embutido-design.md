# Camada de texto embutido (OCR da BN): design e contrato

Data: 2026-07-18. Autor: Claude (sessão Fable 5), aprovação de escopo por Pedro na mesma sessão.

## Estatuto metodológico

Descoberta da sessão: os PDFs do host estático da BN trazem camada de texto embutida
(OCR da própria Hemeroteca), verificada em amostra de 6 objetos de 3 jornais e anos
variados (28 a 44 mil caracteres por página). Este design materializa essa camada
para TODAS as páginas do censo, a custo zero de token.

Pelo `docs/contexto-debate-metodologico-mensuracao.md`, esta é atividade da classe
"pode avançar": reversível, orientada à preservação, com proveniência completa, sem
seleção nem descarte segundo definição substantiva. Não é o instrumento de mensuração
e não o antecipa. O texto embutido é OCR de terceiro (BN), sujo, e entra como:

1. insumo barato para os pilotos da rodada metodológica (dicionários, tópicos,
   ensaios de triagem lexical);
2. baseline observável para a comparação "OCR da BN vs transcrição LLM", que deixa
   de ser pressuposto e vira hipótese testável;
3. camada documental reprocessável, ligada byte a byte ao PDF de origem.

## Contrato do dataset (declarado antes do código)

Produto: **uma extração vigente por página física**, texto bruto do `extract_text()`
do pypdf, sem qualquer normalização, recorte ou correção.

- **Grão**: 1 registro por (página física, execução de extração); ponteiro de vigência
  por página em `current_page_text_extractions` (padrão da casa).
- **População**: todas as `physical_pages` de objetos com obtenção vigente `ok`
  (11.959 objetos, 117.705 páginas em 2026-07-18). O único objeto `invalid_pdf`
  (per178691_1913_10408) fica fora por não ter obtenção ok, documentado no relatório.
- **Statuses** (`result_status`, registro positivo sempre, nunca ausência):
  - `ok`: texto extraído com 1+ caractere; exige `text_path`, `text_sha256`,
    `char_count > 0`.
  - `empty`: extração rodou e devolveu string vazia (página sem camada de texto);
    `char_count = 0`, sem arquivo. String só de espaços é `ok` (nenhuma interpretação
    na camada).
  - `error`: exceção na abertura do PDF ou na extração da página; exige `error_class`.
- **Proveniência**: cada registro grava `source_pdf_sha256` (hash da obtenção vigente
  no momento da extração) e aponta para protocolo com estágio novo `text_extraction`,
  executor `deterministic`, versão do pypdf pinada em `parameters_json`. Mudou o
  pypdf, muda a versão do protocolo (o guard de identidade do `upsert_protocol` força).
- **Determinismo/replay**: mesma versão de pypdf + mesmo PDF ⇒ mesmos bytes e mesmo
  `text_sha256`. Modo `--verificar` reextrai sem escrever e compara com o vigente.
- **Append-only**: reexecução não altera registros; nova extração da mesma página só
  nasce se a obtenção vigente mudou de hash ou sob protocolo novo, e então o ponteiro
  de vigência avança.

### Tabelas novas (migração 003, puramente aditiva)

- `text_extraction_runs(id, protocol_id, started_at, completed_at, run_status,
  scope_manifest_sha256, pages_submitted, pages_completed, elapsed_seconds)` com os
  CHECKs no padrão de `transcription_runs`. Uma run por célula (bib, ano) por
  invocação; escopo = alvos da run (hash da lista ordenada).
- `page_text_extractions(id, page_id, extraction_run_id, source_pdf_sha256,
  result_status, text_path, text_sha256, char_count, error_class, error_message,
  created_at)` com `UNIQUE(page_id, id)` e CHECKs do contrato acima.
- `current_page_text_extractions(page_id PK, extraction_id, selected_at)` com FK
  composta, padrão da casa.
- View `v_current_page_texts` (página, objeto, número, status, chars, path, sha, run).
- `protocols` ganha `text_extraction` na lista de estágios: reconstrução da tabela
  (9 linhas) pelo padrão da migração 002 (tabela de retenção + DROP + CREATE sob o
  nome final, nunca RENAME). `schema.sql` evolui em lockstep byte a byte (o teste de
  paridade `sqlite_master` já cobre).

### Armazenamento

- Texto fora do git e fora do OneDrive, como os PDFs:
  `C:\dados-caixa\texto_embutido\{bib}\{source_identifier}\p{página:03d}.txt`,
  UTF-8, bytes exatos do `extract_text()`. `text_path` absoluto no banco (padrão
  vigente dos fetches do censo). ~3 GB estimados.
- Backup: estender o job robocopy para cobrir `texto_embutido` além de `raw_pdf`
  (nota na retomada; o conteúdo é reconstituível dos PDFs, criticidade menor).
- Manifestos versionados no git: `dados/texto_embutido/extracao_{bib}_{ano}.csv`
  com source_identifier, page_number, result_status,
  char_count, text_sha256, source_pdf_sha256, caminho relativo à raiz de texto.
  Export determinístico a partir do banco ao fim de cada célula (regenerável).
  `LEIAME.md` explica semântica e limites (OCR da BN, não é transcrição do projeto).

### Consumidores nomeados

1. Rodada metodológica (pilotos de desenho de mensuração) — leitura via view/manifesto.
2. Fase B (quando decidida): candidata a insumo da triagem barata.
3. Relatório de cobertura textual (extensão futura do `relatorio_censo.py` ou script
   próprio).

Mudanças de colunas, statuses ou semântica depois do primeiro consumo são breaking e
exigem migração + registro em `docs/decisoes.md`.

## Execução

- `pipeline/base/extrai_texto.py`: CLI com `--bib/--ano` (célula única) ou corpus
  inteiro; transação por célula (run + registros + ponteiros atômicos); resume por
  banco (página com extração vigente do mesmo protocolo e mesmo `source_pdf_sha256`
  é pulada); arquivos escritos antes do commit são idempotentes (bytes
  determinísticos).
- PDF que não abre: todas as páginas do objeto recebem `error` com `error_class`.
  Página individual que falha: `error` só nela.
- Corrida completa local, CPU-bound, sem rate limit; pode rodar de dia, destacada,
  com log em `dados/texto_embutido/log_*.txt` (gitignored).

## Portões de verificação (antes de declarar pronto)

1. Suíte inteira verde, incluindo paridade schema vs migrações e CHECKs novos.
2. Piloto real: célula O Paiz 1906 (79 objetos) extraída; inspecionar distribuição
   de status e `char_count` e conferir 2+ páginas contra o PDF aberto.
3. Replay determinístico na célula piloto: `--verificar` com zero divergência de hash.
4. Corrida completa: 117.705 páginas com registro vigente (ok+empty+error), zero
   página sem registro; banco == manifesto == disco em amostra por célula.
5. Migração 002→003 aplicada ao banco real sem violação de FK e sem alterar
   contagens existentes (objetos, fetches, páginas).

## Não-objetivos

Sem normalização ortográfica, sem dehifenização, sem segmentação de artigos, sem
avaliação de qualidade de OCR (ficam para a rodada metodológica, com registro
próprio), sem tocar em `transcriptions` (produto distinto: instrumento do projeto).
