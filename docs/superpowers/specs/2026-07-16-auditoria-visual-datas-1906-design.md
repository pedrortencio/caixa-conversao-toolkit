# Auditoria visual das datas de O Paiz em 1906

Data: 16/07/2026

Status: aprovado para especificação em 16/07/2026; implementação ainda não iniciada.

## Decisão

As 27 datas conferidas visualmente serão incorporadas por um manifesto JSON versionado. O manifesto será ligado ao identificador da edição, ao caminho do PDF, ao SHA-256 do PDF e à página do masthead. Ele terá precedência sobre o resultado do OCR apenas para os registros que declarar.

A sequência entre número da edição e dia civil continuará sendo uma verificação de consistência. Ela não será usada para criar datas observadas nem imputadas.

## Contexto

A primeira carga dos 67 PDFs canônicos de O Paiz produziu 45 datas observadas e 22 datas não resolvidas. Duas datas repetidas motivaram a auditoria visual. O cruzamento entre número da edição, data normalizada e dia da semana mostrou que o problema era mais amplo: cinco datas aceitas pelo parser estavam incorretas, e os 22 casos sem data tinham masthead legível no PDF.

Foram renderizadas e inspecionadas as primeiras páginas dos 27 casos críticos. A inspeção confirmou 22 novas datas e cinco correções:

| Edição | Data visual | Tratamento |
|---|---|---|
| `per178691_1906_07890` | `1906-05-11` | preencher ausência do OCR |
| `per178691_1906_07891` | `1906-05-12` | preencher ausência do OCR |
| `per178691_1906_07892` | `1906-05-13` | preencher ausência do OCR |
| `per178691_1906_07943` | `1906-07-03` | corrigir OCR `1906-07-05` |
| `per178691_1906_07958` | `1906-07-18` | preencher ausência do OCR |
| `per178691_1906_07959` | `1906-07-19` | corrigir OCR `1906-07-10` |
| `per178691_1906_07992` | `1906-08-21` | preencher ausência do OCR |
| `per178691_1906_07997` | `1906-08-26` | preencher ausência do OCR |
| `per178691_1906_08002` | `1906-08-31` | preencher ausência do OCR |
| `per178691_1906_08003` | `1906-09-01` | preencher ausência do OCR |
| `per178691_1906_08004` | `1906-09-02` | preencher ausência do OCR |
| `per178691_1906_08006` | `1906-09-04` | preencher ausência do OCR |
| `per178691_1906_08020` | `1906-09-18` | corrigir OCR `1906-09-08` |
| `per178691_1906_08025` | `1906-09-23` | preencher ausência do OCR |
| `per178691_1906_08026` | `1906-09-24` | preencher ausência do OCR |
| `per178691_1906_08027` | `1906-09-25` | preencher ausência do OCR |
| `per178691_1906_08028` | `1906-09-26` | corrigir OCR `1906-09-20` |
| `per178691_1906_08073` | `1906-11-10` | preencher ausência do OCR |
| `per178691_1906_08087` | `1906-11-24` | preencher ausência do OCR |
| `per178691_1906_08091` | `1906-11-28` | preencher ausência do OCR |
| `per178691_1906_08100` | `1906-12-07` | preencher ausência do OCR |
| `per178691_1906_08104` | `1906-12-11` | preencher ausência do OCR |
| `per178691_1906_08107` | `1906-12-14` | corrigir OCR `1906-12-08` |
| `per178691_1906_08111` | `1906-12-18` | preencher ausência do OCR |
| `per178691_1906_08115` | `1906-12-22` | preencher ausência do OCR |
| `per178691_1906_08116` | `1906-12-23` | preencher ausência do OCR |
| `per178691_1906_08124` | `1906-12-31` | preencher ausência do OCR |

## Objetivos

1. Tornar as 27 decisões reproduzíveis e revisáveis sem versionar PDFs ou PNGs derivados.
2. Separar explicitamente o resultado do OCR da leitura visual do masthead.
3. Preservar no histórico os cinco candidatos incorretos gerados pelo OCR.
4. Fazer a carga falhar quando o PDF local não corresponder à evidência auditada.
5. Produzir 67 datas vigentes observadas, 67 dias civis distintos e nenhuma data imputada.

## Fora de escopo

- Generalizar o parser para todo tipo de erro de OCR.
- Inferir datas pelo número da edição.
- Auditar outros jornais ou PDFs que não pertençam aos 67 objetos canônicos atuais.
- Versionar os PNGs temporários usados na inspeção.
- Declarar que houve revisão humana independente. A auditoria atual foi uma leitura visual assistida pelo Codex e deverá ser descrita dessa forma.

## Alternativas consideradas

### Manifesto versionado

É a solução escolhida. Mantém as decisões fora do código, liga cada decisão à evidência física e permite revisão futura sem reproduzir heurísticas frágeis.

### Novas heurísticas de OCR

Foram rejeitadas como fonte das 27 decisões. Regras para `100G`, `1900`, `i8`, `1.º` e outros ruídos resolveriam parte dos casos, mas continuariam sujeitas a aceitar datas plausíveis e erradas, como ocorreu nas cinco correções.

### Correção direta no SQLite

Foi rejeitada porque não seria reproduzível após a recriação do banco e esconderia a relação entre decisão e PDF.

## Componentes

### Manifesto

O arquivo será `pipeline/base/manifests/datas_masthead_1906.json`. A raiz terá:

- `schema_version`: inteiro igual a `1`;
- `audit_id`: identificador estável da auditoria;
- `audited_at`: data da inspeção;
- `newspaper_bib`: `178691`;
- `source_year`: `1906`;
- `verification_method`: `visual_masthead`;
- `reviewer_type`: `ai_assisted_visual_review`;
- `reviewer_label`: `Codex`;
- `independent_human_review`: `false`;
- `records`: lista dos 27 registros.

Cada registro terá:

- `source_identifier`: chave `per178691_1906_NNNNN`;
- `normalized_date`: data ISO confirmada;
- `date_literal`: transcrição fiel da linha do masthead;
- `pdf_path`: caminho relativo do PDF canônico;
- `pdf_sha256`: hash do PDF completo;
- `page_number`: inteiro igual a `1` nesta auditoria;
- `evidence_region`: `masthead`;
- `decision`: `fill_missing_ocr` ou `correct_ocr`;
- `previous_ocr_date`: data anterior somente para `correct_ocr`, nula nos demais casos;
- `notes`: observação curta quando houver ruído relevante.

O JSON será gravado com UTF-8, chaves estáveis e ordenação determinística dos registros por `source_identifier`.

### Leitura e validação

O carregador terá uma unidade isolada para ler e validar o manifesto. A validação ocorrerá antes de abrir a transação de carga e exigirá:

1. versão de schema conhecida;
2. exatamente 27 identificadores únicos;
3. identificadores pertencentes aos 67 artefatos descobertos;
4. datas ISO válidas de 1906;
5. caminho relativo igual ao PDF descoberto;
6. SHA-256 igual ao hash calculado do PDF;
7. página existente no PDF;
8. valores fechados para método, tipo de revisor, região e decisão;
9. `previous_ocr_date` coerente com `decision`;
10. ausência de campos obrigatórios vazios.

Qualquer divergência será erro fatal com identificação do registro e do campo. O carregador não deverá ignorar silenciosamente registro inválido, PDF ausente ou hash divergente.

### Resolução da data

Para cada artefato, o carregador conservará separadamente:

- o candidato extraído do `PAGE_METADATA` pelo parser atual;
- o registro visual do manifesto, quando houver.

A precedência será:

1. registro visual válido do manifesto;
2. candidato válido do OCR;
3. ausência de data.

Se OCR e manifesto concordarem, o manifesto continuará sendo a fonte vigente para os 27 registros auditados. Se divergirem, o candidato do OCR permanecerá histórico e o manifesto será vigente. O número da edição poderá ser usado para emitir relatório de consistência, mas nunca para preencher `normalized_date`.

## Proveniência no SQLite

O carregador criará um protocolo imutável com:

- `stage = date_parsing`;
- `name = masthead_visual_manifest`;
- `version = 1.0.0`;
- `executor_type = external_service`;
- parâmetros que identifiquem o manifesto, seu SHA-256, o tipo de revisão assistida e a inexistência de revisão humana independente.

O tipo `external_service` evita representar a auditoria como manual e evita inventar uma versão exata do modelo que não está disponível no ambiente.

Os registros visuais serão inseridos em `date_records` com:

- o protocolo visual;
- `evidence_page_id` da primeira página;
- `evidence_transcription_id = NULL`;
- `evidence_region_json` com página, região semântica, caminho do PDF, SHA-256 e caminho do manifesto;
- `date_literal` do masthead;
- `parser_name = masthead_visual_manifest`;
- `parser_version = 1.0.0`;
- `status = observed`;
- `imputation_method = NULL`;
- notas transparentes sobre o tipo de revisão.

Nos cinco casos corrigidos, o candidato do OCR também será inserido com o protocolo `masthead_pt_regex`, mas `current_edition_dates` apontará para o registro visual. Nada será apagado. Nos 22 preenchimentos, haverá somente o registro visual. Nos outros 40 casos haverá somente o registro do OCR.

Cardinalidades esperadas após uma carga limpa:

- 72 linhas em `date_records`: 45 candidatos do OCR e 27 registros visuais;
- 67 linhas em `current_edition_dates`;
- 67 datas vigentes com `status = observed`;
- zero datas vigentes imputadas;
- zero edições sem data vigente;
- 67 dias civis distintos;
- 67 edições com `identity_status = confirmed`.

## Fluxo operacional

1. Descobrir os 67 PDFs e calcular seus hashes.
2. Ler e validar integralmente o manifesto.
3. Extrair candidatos do OCR sem alterá-los.
4. Carregar objetos, páginas e transcrições como hoje.
5. Inserir candidatos do OCR disponíveis.
6. Inserir registros visuais auditados.
7. Selecionar a fonte vigente conforme a precedência definida.
8. Atualizar identidade e população com base na data vigente.
9. Executar contract checks e relatório de cobertura.
10. Remover os PNGs temporários após a verificação final; os PDFs continuam locais e ignorados pelo Git.

## Tratamento de erros

- Manifesto ausente: erro fatal, porque a carga passará a depender dele.
- JSON inválido ou schema desconhecido: erro fatal antes da transação.
- Identificador duplicado ou desconhecido: erro fatal.
- PDF ausente, caminho divergente ou SHA-256 divergente: erro fatal.
- Data inválida, fora de 1906 ou página inexistente: erro fatal.
- Divergência entre `previous_ocr_date` e o candidato histórico: erro fatal na primeira versão, para impedir correção atribuída ao caso errado.
- Reexecução com o mesmo manifesto: idempotente.
- Alteração posterior do manifesto: exige nova versão do protocolo e decisão explícita sobre qual registro será vigente.

## Testes

### Unidade

- leitura do manifesto válido;
- rejeição de schema desconhecido;
- rejeição de campos ausentes e valores fechados inválidos;
- rejeição de identificadores duplicados;
- rejeição de data inválida ou fora de 1906;
- rejeição de hash, caminho ou página divergentes;
- precedência do manifesto sobre OCR divergente;
- preservação do OCR quando o manifesto concorda ou corrige;
- ausência de qualquer imputação por sequência numérica.

### Integração

- carga limpa com 72 registros históricos e 67 registros vigentes;
- verificação das cinco correções exatas;
- verificação dos 22 preenchimentos;
- 67 datas observadas distintas e zero não resolvidas;
- `identity_status = confirmed` para as 67 edições;
- protocolo visual com SHA-256 do manifesto;
- idempotência em segunda execução;
- `PRAGMA integrity_check = ok` e `PRAGMA foreign_key_check` vazio.

### Regressão

Todos os testes existentes do schema, acesso SQLite, parser, carga piloto e higiene do repositório continuarão passando. PDFs, bancos e PNGs permanecerão fora do commit.

## Critérios de aceitação

1. O manifesto contém exatamente os 27 registros da tabela desta especificação.
2. Cada registro está ligado ao PDF real por caminho e SHA-256.
3. As cinco interpretações erradas do OCR permanecem históricas e deixam de ser vigentes.
4. As 22 edições antes não resolvidas recebem data visual observada.
5. A carga produz 67 datas vigentes, todas distintas e nenhuma imputada.
6. Nenhuma data é criada a partir da sequência numérica.
7. A segunda carga não altera cardinalidades.
8. Toda divergência de evidência interrompe a carga com mensagem acionável.
9. A documentação declara explicitamente que não houve revisão humana independente.

## Riscos e mitigação

- Erro na transcrição visual: mitigado pelo vínculo ao PDF e pela possibilidade de revisão independente futura.
- Mudança do PDF local: detectada pelo SHA-256 e tratada como erro fatal.
- Manifesto tornar-se uma lista opaca de exceções: mitigado por campos de evidência, decisão e protocolo próprios.
- Correções futuras sobrescreverem história: evitado pela natureza histórica de `date_records` e pelo ponteiro explícito em `current_edition_dates`.
- Confusão entre observação e imputação: evitada porque todas as 27 datas vêm do masthead; a sequência é apenas controle de qualidade.

## Resultado esperado

A auditoria transforma uma carga com 22 lacunas e cinco datas incorretas em uma carga com 67 datas observadas verificáveis. A alteração melhora a cobertura sem ampliar o parser de forma arriscada, sem imputar datas e sem esconder os resultados anteriores do OCR.
