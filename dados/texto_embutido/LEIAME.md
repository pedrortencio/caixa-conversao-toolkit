# Manifestos da camada de texto embutido (OCR da BN)

Contrato completo: `docs/superpowers/specs/2026-07-18-camada-texto-embutido-design.md`.

O que é: texto extraído deterministicamente (pypdf, protocolo
`text_extraction/texto-embutido-pypdf`) da camada embutida nos PDFs do host
estático da BN. É o OCR DA PRÓPRIA HEMEROTECA, sujo, sem qualquer correção,
normalização ou seleção nossa. NÃO é transcrição do projeto (essa é outro
produto, tabela `transcriptions`) e NÃO é o instrumento de mensuração.

- Arquivos de texto: `C:\dados-caixa\texto_embutido\{bib}\{source_identifier}\pNNN.txt`
  (fora do git e do OneDrive, como os PDFs; backup via robocopy junto do raw_pdf).
- Estes CSVs (`extracao_{bib}_{ano}.csv`): export determinístico das extrações
  vigentes por página, com `text_sha256` (hash dos bytes UTF-8 do arquivo) e
  `source_pdf_sha256` (hash do PDF de origem). Regeneráveis do banco;
  versionados para auditoria.
- Statuses: `ok` (texto com 1+ caractere), `empty` (página sem camada de texto,
  registro positivo, sem arquivo), `error` (falha de abertura/extração, com
  classe).
- Logs `log_*.txt` são transitórios e não entram no git.

Uso previsto: pilotos da rodada metodológica (dicionários, tópicos, ensaios de
triagem) e comparação "OCR da BN vs transcrição LLM". Qualquer consumo que
selecione ou estruture segundo o construto segue as regras do
`docs/contexto-debate-metodologico-mensuracao.md`.
