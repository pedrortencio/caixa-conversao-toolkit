# Esquema da base do corpus, `caixa_conversao.db`, design v2

Data: 2026-07-16
Status: proposta v2 pronta para revisão independente por Claude e decisão final de Pedro
Substitui: `docs/superpowers/specs/2026-07-16-esquema-base-corpus-design.md`

## 1. Objetivo

Este documento define o contrato da base operacional do corpus da Hemeroteca Digital da Biblioteca Nacional para o período de 1906 a 1914.

O esquema deve preservar, sem compressão indevida, quatro universos distintos:

1. O que existe ou deveria existir no acervo e no calendário de circulação.
2. O que cada protocolo de busca ou triagem recuperou.
3. O que cada execução de identificação avaliou como relevante, não relevante, incerto ou erro.
4. O que foi efetivamente transcrito e classificado.

A base deve permitir reconstruir qualquer corpus produzido pelo pipeline, explicar inclusões e exclusões, reprocessar os PDFs com novos modelos e auditar as falhas do piloto de 1906.

O princípio central é:

> A camada bruta deve ser completa, durável e reprocessável. Se a transcrição for seletiva, o produto textual deve ser chamado de subcorpus recuperado segundo um protocolo explicitamente versionado.

A base não terá colunas nucleares como `is_hit`, `relevante` ou `fase`. Resultados mutáveis entram em execuções append-only, em classificações versionadas ou em visões derivadas.

## 2. Decisões de arquitetura

### 2.1 Banco e acesso

O banco operacional permanece em:

```text
dados/base/caixa_conversao.db
```

O acesso será feito com `sqlite3` da biblioteca padrão, sem ORM.

Toda conexão deve executar:

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
```

O banco fica fora do git e é preservado pelo backup do OneDrive. Transcrições, respostas textuais que constituam dados de pesquisa, prompts, protocolos, manifestos e classificações exportadas permanecem versionados no git.

### 2.2 Layout

```text
pipeline/base/
├── db.py
├── schema.sql
└── migrations/
    ├── 001_init.sql   (schema completo v2, com as views)
    ├── 002_fetch_mode_and_unresolved_dates.sql
    └── ...
```

`schema.sql` contém o contrato canônico para um banco novo. As migrações numeradas transformam bancos existentes.

O migrador lê `PRAGMA user_version`, executa cada migração em uma transação e só incrementa a versão após sucesso integral.

Mudanças de tipo, nulabilidade, chave, enum ou semântica são mudanças incompatíveis e exigem migração documentada. Não haverá `DROP`, `RENAME` ou reconstrução silenciosa de tabela.

### 2.3 Imutabilidade e vigência

Execuções e resultados históricos são append-only. Não se usa `UPSERT` para alterar resultados de busca, identificação, transcrição, data, auditoria ou classificação.

Quando uma execução é substituída:

1. Insere-se uma nova execução.
2. Inserem-se novos resultados.
3. Atualiza-se somente a tabela de ponteiro vigente.
4. As linhas anteriores permanecem intactas.

As tabelas de ponteiro vigente podem ser atualizadas. As tabelas históricas não possuem `updated_at`.

## 3. Modelo conceitual

```text
jornal
  |
  + calendário de circulação
  |
  + objeto digital da BN
        |
        + obtenções do objeto
        |
        + páginas físicas
        |
        + vínculos com edição-dia lógica
              |
              + identificadores impressos
              + registros de data
              + transcrições
              + classificações a jusante

protocolo
  |
  + busca
  |    + hits
  |         + resolução para objeto, edição e página
  |
  + identificação
  |    + avaliações de página
  |
  + transcrição
  |    + versões de texto
  |
  + auditoria de recall
  |
  + classificação
```

Um PDF não é presumido como equivalente a uma edição nem a uma edição-dia. O piloto deve testar as cardinalidades reais.

## 4. Contrato SQL

### 4.1 Jornais e protocolos

```sql
CREATE TABLE newspapers (
    id                  INTEGER PRIMARY KEY,
    slug                TEXT NOT NULL UNIQUE,
    title               TEXT NOT NULL,
    bn_bib               TEXT NOT NULL UNIQUE,
    city                 TEXT NOT NULL,
    active_from          TEXT,
    active_to            TEXT,
    created_at           TEXT NOT NULL
);

CREATE TABLE protocols (
    id                  INTEGER PRIMARY KEY,
    stage               TEXT NOT NULL,
    name                TEXT NOT NULL,
    version             TEXT NOT NULL,
    executor_type       TEXT NOT NULL,
    code_commit         TEXT NOT NULL,
    model_provider      TEXT,
    model_name          TEXT,
    model_version       TEXT,
    prompt_version      TEXT,
    prompt_sha256       TEXT,
    prompt_path         TEXT,
    parameters_json     TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    UNIQUE (stage, name, version),
    CHECK (stage IN (
        'inventory',
        'circulation',
        'search',
        'identification',
        'transcription',
        'date_parsing',
        'recall_reference',
        'classification'
    )),
    CHECK (executor_type IN (
        'deterministic',
        'manual',
        'model',
        'external_service'
    )),
    CHECK (
        executor_type <> 'model'
        OR (
            model_provider IS NOT NULL
            AND model_name IS NOT NULL
            AND model_version IS NOT NULL
            AND prompt_version IS NOT NULL
            AND prompt_sha256 IS NOT NULL
        )
    ),
    CHECK (
        prompt_sha256 IS NULL
        OR length(prompt_sha256) = 64
    )
);
```

Nomes genéricos de modelo não satisfazem `model_version`. Cada execução com modelo deve registrar a versão exata devolvida pelo provedor ou uma identificação imutável equivalente.

### 4.2 Calendário, circulação e população elegível

`calendar_days` contém o calendário civil, não uma afirmação de que o jornal circulou.

```sql
CREATE TABLE calendar_days (
    id                  INTEGER PRIMARY KEY,
    newspaper_id        INTEGER NOT NULL
                            REFERENCES newspapers(id),
    civil_date          TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    UNIQUE (newspaper_id, civil_date),
    CHECK (length(civil_date) = 10)
);

CREATE TABLE circulation_assessments (
    id                  INTEGER PRIMARY KEY,
    calendar_day_id     INTEGER NOT NULL
                            REFERENCES calendar_days(id),
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    result              TEXT NOT NULL,
    evidence_text       TEXT,
    evidence_path       TEXT,
    evidence_sha256     TEXT,
    assessed_at         TEXT NOT NULL,
    UNIQUE (calendar_day_id, id),
    CHECK (result IN (
        'circulated',
        'did_not_circulate',
        'unknown',
        'error'
    )),
    CHECK (
        evidence_sha256 IS NULL
        OR length(evidence_sha256) = 64
    )
);

CREATE TABLE current_circulation_assessments (
    calendar_day_id     INTEGER PRIMARY KEY
                            REFERENCES calendar_days(id),
    assessment_id       INTEGER NOT NULL,
    selected_at         TEXT NOT NULL,
    FOREIGN KEY (calendar_day_id, assessment_id)
        REFERENCES circulation_assessments(calendar_day_id, id)
);
```

A elegibilidade analítica é versionada, pois pode mudar com decisões sobre período, jornais e unidade.

```sql
CREATE TABLE population_definitions (
    id                  INTEGER PRIMARY KEY,
    name                TEXT NOT NULL,
    version             TEXT NOT NULL,
    unit_mode           TEXT NOT NULL,
    description         TEXT NOT NULL,
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    created_at          TEXT NOT NULL,
    UNIQUE (name, version),
    CHECK (unit_mode IN (
        'strict_newspaper_day',
        'multiple_editions_per_day'
    ))
);

CREATE TABLE population_memberships (
    id                      INTEGER PRIMARY KEY,
    population_definition_id INTEGER NOT NULL
                                REFERENCES population_definitions(id),
    calendar_day_id         INTEGER NOT NULL
                                REFERENCES calendar_days(id),
    edition_day_id          INTEGER,
    eligibility             TEXT NOT NULL,
    reason                  TEXT NOT NULL,
    assigned_at             TEXT NOT NULL,
    CHECK (eligibility IN (
        'eligible',
        'ineligible',
        'unknown'
    ))
);
```

A FK de `edition_day_id` é acrescentada depois da criação de `edition_days` por migração de reconstrução, ou a ordem das instruções no `schema.sql` é ajustada para criar `edition_days` antes de `population_memberships`.

### 4.3 Inventário de objetos digitais

`digital_objects` representa a identidade estável de um objeto da BN. Tentativas de obtenção ficam em outra tabela.

```sql
CREATE TABLE digital_objects (
    id                      INTEGER PRIMARY KEY,
    newspaper_id            INTEGER NOT NULL
                                REFERENCES newspapers(id),
    source_identifier       TEXT NOT NULL,
    source_url              TEXT NOT NULL,
    source_year             INTEGER NOT NULL,
    bn_file_key             TEXT NOT NULL,
    bn_file_number_literal  TEXT NOT NULL,
    discovered_by_protocol_id INTEGER NOT NULL
                                REFERENCES protocols(id),
    discovered_at           TEXT NOT NULL,
    UNIQUE (source_identifier),
    UNIQUE (source_url),
    CHECK (source_year BETWEEN 1800 AND 2100)
);

CREATE TABLE object_fetches (
    id                  INTEGER PRIMARY KEY,
    object_id           INTEGER NOT NULL
                            REFERENCES digital_objects(id),
    attempted_at        TEXT NOT NULL,
    completed_at        TEXT,
    result              TEXT NOT NULL,
    fetch_mode          TEXT NOT NULL DEFAULT 'http',
    http_status         INTEGER,
    storage_path        TEXT,
    pdf_sha256          TEXT,
    response_sha256     TEXT,
    byte_count          INTEGER,
    page_count          INTEGER,
    error_class         TEXT,
    error_message       TEXT,
    UNIQUE (object_id, id),
    CHECK (result IN (
        'ok',
        'http_error',
        'network_error',
        'invalid_pdf',
        'storage_error'
    )),
    CHECK (
        http_status IS NULL
        OR http_status BETWEEN 100 AND 599
    ),
    CHECK (
        pdf_sha256 IS NULL
        OR length(pdf_sha256) = 64
    ),
    CHECK (
        response_sha256 IS NULL
        OR length(response_sha256) = 64
    ),
    CHECK (fetch_mode IN ('http', 'local_import')),
    -- Só resposta HTTP real produz hash de resposta (achado E.1).
    CHECK (fetch_mode = 'http' OR response_sha256 IS NULL),
    -- Achado D: a importação local do piloto tem http_status nulo; um
    -- download HTTP real com http_status nulo continua reprovado.
    CHECK (
        result <> 'ok'
        OR (
            (
                (fetch_mode = 'http' AND http_status BETWEEN 200 AND 299)
                OR (fetch_mode = 'local_import' AND http_status IS NULL)
            )
            AND storage_path IS NOT NULL
            AND pdf_sha256 IS NOT NULL
            AND byte_count > 0
            AND page_count > 0
        )
    )
);

CREATE TABLE current_object_fetches (
    object_id           INTEGER PRIMARY KEY
                            REFERENCES digital_objects(id),
    fetch_id            INTEGER NOT NULL,
    selected_at         TEXT NOT NULL,
    FOREIGN KEY (object_id, fetch_id)
        REFERENCES object_fetches(object_id, id)
);
```

A relação canônica de inventário, uma linha por objeto, é uma visão:

```sql
CREATE VIEW v_digital_object_inventory AS
SELECT
    o.id AS object_id,
    n.slug AS newspaper,
    n.bn_bib AS bib,
    o.source_identifier,
    o.source_url,
    o.source_year,
    o.bn_file_key,
    o.bn_file_number_literal,
    f.result AS fetch_result,
    f.http_status,
    f.completed_at AS obtained_at,
    f.storage_path,
    f.pdf_sha256,
    f.byte_count,
    f.page_count
FROM digital_objects AS o
JOIN newspapers AS n
  ON n.id = o.newspaper_id
LEFT JOIN current_object_fetches AS cf
  ON cf.object_id = o.id
LEFT JOIN object_fetches AS f
  ON f.id = cf.fetch_id;
```

A ausência de uma obtenção vigente significa `não tentado`, não `404`.

### 4.4 Edições lógicas e vínculos com objetos

`edition_days` representa uma edição lógica potencialmente analisável. Mais de uma linha pode resolver para a mesma data.

```sql
CREATE TABLE edition_days (
    id                  INTEGER PRIMARY KEY,
    newspaper_id        INTEGER NOT NULL
                            REFERENCES newspapers(id),
    logical_key         TEXT NOT NULL,
    edition_kind        TEXT NOT NULL,
    sequence_in_day     INTEGER,
    identity_status     TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    UNIQUE (newspaper_id, logical_key),
    CHECK (edition_kind IN (
        'regular',
        'supplement',
        'extraordinary',
        'special',
        'unknown'
    )),
    CHECK (identity_status IN (
        'provisional',
        'confirmed',
        'ambiguous'
    )),
    CHECK (
        sequence_in_day IS NULL
        OR sequence_in_day >= 1
    )
);

CREATE TABLE edition_identifiers (
    id                  INTEGER PRIMARY KEY,
    edition_day_id      INTEGER NOT NULL
                            REFERENCES edition_days(id),
    identifier_type     TEXT NOT NULL,
    literal_value       TEXT NOT NULL,
    normalized_value    TEXT,
    evidence_page_id    INTEGER,
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    observed_at         TEXT NOT NULL,
    CHECK (identifier_type IN (
        'printed_issue_number',
        'bn_file_number',
        'source_folder',
        'legacy_identifier',
        'other'
    ))
);

CREATE TABLE edition_object_links (
    id                  INTEGER PRIMARY KEY,
    edition_day_id      INTEGER NOT NULL
                            REFERENCES edition_days(id),
    object_id           INTEGER NOT NULL
                            REFERENCES digital_objects(id),
    link_role           TEXT NOT NULL,
    include_in_content  INTEGER NOT NULL,
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    linked_at           TEXT NOT NULL,
    UNIQUE (edition_day_id, object_id, link_role),
    CHECK (link_role IN (
        'principal',
        'continuation',
        'supplement',
        'extraordinary',
        'duplicate_scan',
        'partial_scan',
        'unknown'
    )),
    CHECK (include_in_content IN (0, 1))
);
```

Regras de identidade:

1. Um suplemento não é absorvido silenciosamente pela edição regular.
2. Uma edição extraordinária recebe identidade própria.
3. Dois objetos que sejam digitalizações duplicadas podem apontar para a mesma edição.
4. Um objeto que contenha mais de uma edição pode ter mais de um vínculo.
5. `bn_file_number_literal` pertence ao objeto.
6. O número impresso pertence a `edition_identifiers`.
7. Divergências entre número da BN e número impresso são preservadas, não corrigidas por sobrescrita.
8. A cardinalidade observada no piloto deve ser reportada antes da escolha da unidade final.

### 4.5 Páginas físicas

Toda página de todo PDF obtido com sucesso recebe uma linha, mesmo que ainda não tenha sido avaliada.

```sql
CREATE TABLE physical_pages (
    id                  INTEGER PRIMARY KEY,
    object_id           INTEGER NOT NULL
                            REFERENCES digital_objects(id),
    page_number         INTEGER NOT NULL,
    source_page_label   TEXT,
    visual_path         TEXT,
    visual_sha256       TEXT,
    created_at          TEXT NOT NULL,
    UNIQUE (object_id, page_number),
    CHECK (page_number >= 1),
    CHECK (
        visual_sha256 IS NULL
        OR length(visual_sha256) = 64
    )
);
```

Após uma obtenção bem-sucedida, o número de linhas em `physical_pages` deve ser exatamente igual a `object_fetches.page_count`.

A criação das páginas e de suas avaliações iniciais com resultado `not_assessed` ocorre na mesma transação. Ausência de avaliação vigente é violação do contrato, nunca evidência de irrelevância.

### 4.6 Busca e recuperação

Uma campanha define objetivo e escopo. Cada reexecução cria um novo `search_run`.

```sql
CREATE TABLE search_campaigns (
    id                  INTEGER PRIMARY KEY,
    name                TEXT NOT NULL,
    objective           TEXT NOT NULL,
    newspaper_id        INTEGER
                            REFERENCES newspapers(id),
    start_date          TEXT,
    end_date            TEXT,
    query_text          TEXT NOT NULL,
    campaign_role       TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    UNIQUE (name),
    CHECK (campaign_role IN (
        'production_retrieval',
        'expanded_retrieval',
        'recall_audit',
        'legacy_import'
    ))
);

CREATE TABLE search_runs (
    id                  INTEGER PRIMARY KEY,
    campaign_id         INTEGER NOT NULL
                            REFERENCES search_campaigns(id),
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    started_at          TEXT NOT NULL,
    completed_at        TEXT NOT NULL,
    run_status          TEXT NOT NULL,
    scope_manifest_sha256 TEXT NOT NULL,
    raw_response_text   TEXT,
    raw_response_path   TEXT,
    raw_response_sha256 TEXT NOT NULL,
    input_units         INTEGER,
    output_hits         INTEGER,
    input_tokens        INTEGER,
    output_tokens       INTEGER,
    input_megapixels    REAL,
    cost_micros         INTEGER,
    currency            TEXT,
    UNIQUE (campaign_id, id),
    CHECK (run_status IN (
        'ok',
        'partial',
        'error'
    )),
    CHECK (length(scope_manifest_sha256) = 64),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL
        OR raw_response_path IS NOT NULL
    ),
    CHECK (
        cost_micros IS NULL
        OR cost_micros >= 0
    )
);

CREATE TABLE current_search_runs (
    campaign_id         INTEGER PRIMARY KEY
                            REFERENCES search_campaigns(id),
    search_run_id       INTEGER NOT NULL,
    selected_at         TEXT NOT NULL,
    FOREIGN KEY (campaign_id, search_run_id)
        REFERENCES search_runs(campaign_id, id)
);

CREATE TABLE search_hits (
    id                  INTEGER PRIMARY KEY,
    search_run_id       INTEGER NOT NULL
                            REFERENCES search_runs(id),
    source_hit_id       TEXT NOT NULL,
    hit_rank            INTEGER,
    target_url          TEXT,
    bn_file_number_literal TEXT,
    source_page_label   TEXT,
    matched_text        TEXT,
    raw_payload_text    TEXT,
    raw_payload_path    TEXT,
    raw_payload_sha256  TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    UNIQUE (search_run_id, source_hit_id),
    CHECK (length(raw_payload_sha256) = 64),
    CHECK (
        raw_payload_text IS NOT NULL
        OR raw_payload_path IS NOT NULL
    )
);

CREATE TABLE search_hit_resolutions (
    id                  INTEGER PRIMARY KEY,
    search_hit_id       INTEGER NOT NULL
                            REFERENCES search_hits(id),
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    resolution_status   TEXT NOT NULL,
    object_id           INTEGER
                            REFERENCES digital_objects(id),
    edition_day_id      INTEGER
                            REFERENCES edition_days(id),
    page_id             INTEGER
                            REFERENCES physical_pages(id),
    explanation         TEXT NOT NULL,
    resolved_at         TEXT NOT NULL,
    UNIQUE (search_hit_id, id),
    CHECK (resolution_status IN (
        'matched',
        'unresolved',
        'ambiguous',
        'invalid_hit'
    )),
    CHECK (
        resolution_status <> 'matched'
        OR (
            object_id IS NOT NULL
            AND edition_day_id IS NOT NULL
            AND page_id IS NOT NULL
        )
    )
);

CREATE TABLE current_search_hit_resolutions (
    search_hit_id       INTEGER PRIMARY KEY
                            REFERENCES search_hits(id),
    resolution_id       INTEGER NOT NULL,
    selected_at         TEXT NOT NULL,
    FOREIGN KEY (search_hit_id, resolution_id)
        REFERENCES search_hit_resolutions(search_hit_id, id)
);
```

Essa cadeia torna reproduzível:

```text
campanha → execução → hit bruto → resolução → objeto → edição lógica → página física
```

Um hit não resolvido permanece registrado como não resolvido. Ele não pode ser convertido em negativo substantivo.

### 4.7 Identificação e avaliação de páginas

A identificação barata e a avaliação substantiva são níveis distintos.

```sql
CREATE TABLE identification_runs (
    id                  INTEGER PRIMARY KEY,
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    started_at          TEXT NOT NULL,
    completed_at        TEXT NOT NULL,
    run_status          TEXT NOT NULL,
    scope_manifest_sha256 TEXT NOT NULL,
    raw_response_path   TEXT,
    raw_response_sha256 TEXT,
    pages_submitted     INTEGER NOT NULL,
    pages_completed     INTEGER NOT NULL,
    input_bytes         INTEGER,
    input_megapixels    REAL,
    input_tokens        INTEGER,
    output_tokens       INTEGER,
    elapsed_seconds     REAL,
    cost_micros         INTEGER,
    currency            TEXT,
    CHECK (run_status IN (
        'ok',
        'partial',
        'error'
    )),
    CHECK (length(scope_manifest_sha256) = 64),
    CHECK (
        raw_response_sha256 IS NULL
        OR length(raw_response_sha256) = 64
    ),
    CHECK (pages_submitted >= 0),
    CHECK (pages_completed >= 0),
    CHECK (pages_completed <= pages_submitted),
    CHECK (
        cost_micros IS NULL
        OR cost_micros >= 0
    )
);

CREATE TABLE page_assessments (
    id                  INTEGER PRIMARY KEY,
    page_id             INTEGER NOT NULL
                            REFERENCES physical_pages(id),
    identification_run_id INTEGER NOT NULL
                            REFERENCES identification_runs(id),
    assessment_level    TEXT NOT NULL,
    result              TEXT NOT NULL,
    confidence          REAL,
    evidence_region_json TEXT,
    rationale           TEXT,
    raw_response_text   TEXT,
    raw_response_path   TEXT,
    raw_response_sha256 TEXT NOT NULL,
    assessed_at         TEXT NOT NULL,
    UNIQUE (page_id, assessment_level, id),
    CHECK (assessment_level IN (
        'screening',
        'substantive',
        'adjudication'
    )),
    CHECK (result IN (
        'relevant',
        'not_relevant',
        'uncertain',
        'error',
        'not_assessed'
    )),
    CHECK (
        confidence IS NULL
        OR confidence BETWEEN 0.0 AND 1.0
    ),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL
        OR raw_response_path IS NOT NULL
    )
);

CREATE TABLE current_page_assessments (
    page_id             INTEGER NOT NULL
                            REFERENCES physical_pages(id),
    assessment_level    TEXT NOT NULL,
    assessment_id       INTEGER NOT NULL,
    selected_at         TEXT NOT NULL,
    PRIMARY KEY (page_id, assessment_level),
    FOREIGN KEY (page_id, assessment_level, assessment_id)
        REFERENCES page_assessments(page_id, assessment_level, id),
    CHECK (assessment_level IN (
        'screening',
        'substantive',
        'adjudication'
    ))
);
```

A visão vigente não cria um bit permanente de relevância:

```sql
CREATE VIEW v_current_page_assessments AS
SELECT
    p.id AS page_id,
    p.object_id,
    p.page_number,
    c.assessment_level,
    a.result,
    a.confidence,
    a.identification_run_id,
    a.assessed_at
FROM physical_pages AS p
JOIN current_page_assessments AS c
  ON c.page_id = p.id
JOIN page_assessments AS a
  ON a.id = c.assessment_id;
```

Para uma página ser considerada efetivamente avaliada em um nível, o resultado vigente deve ser `relevant` ou `not_relevant`. `uncertain`, `error`, `not_assessed` e ausência de ponteiro impedem o fechamento da edição.

### 4.8 Transcrições versionadas

```sql
CREATE TABLE transcription_runs (
    id                  INTEGER PRIMARY KEY,
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    started_at          TEXT NOT NULL,
    completed_at        TEXT NOT NULL,
    run_status          TEXT NOT NULL,
    scope_manifest_sha256 TEXT NOT NULL,
    pages_submitted     INTEGER NOT NULL,
    pages_completed     INTEGER NOT NULL,
    input_megapixels    REAL,
    input_tokens        INTEGER,
    output_tokens       INTEGER,
    elapsed_seconds     REAL,
    cost_micros         INTEGER,
    currency            TEXT,
    CHECK (run_status IN (
        'ok',
        'partial',
        'error'
    )),
    CHECK (length(scope_manifest_sha256) = 64),
    CHECK (pages_submitted >= 0),
    CHECK (pages_completed >= 0),
    CHECK (pages_completed <= pages_submitted)
);

CREATE TABLE transcriptions (
    id                  INTEGER PRIMARY KEY,
    page_id             INTEGER NOT NULL
                            REFERENCES physical_pages(id),
    transcription_run_id INTEGER NOT NULL
                            REFERENCES transcription_runs(id),
    purpose             TEXT NOT NULL,
    input_visual_sha256 TEXT NOT NULL,
    evidence_region_json TEXT,
    result_status       TEXT NOT NULL,
    transcript_text     TEXT,
    transcript_sha256   TEXT,
    raw_response_text   TEXT,
    raw_response_path   TEXT,
    raw_response_sha256 TEXT NOT NULL,
    export_path         TEXT,
    created_at          TEXT NOT NULL,
    UNIQUE (page_id, purpose, id),
    CHECK (purpose IN (
        'masthead',
        'candidate_content',
        'full_page',
        'recall_reference'
    )),
    CHECK (result_status IN (
        'ok',
        'empty',
        'error'
    )),
    CHECK (length(input_visual_sha256) = 64),
    CHECK (
        transcript_sha256 IS NULL
        OR length(transcript_sha256) = 64
    ),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL
        OR raw_response_path IS NOT NULL
    ),
    CHECK (
        result_status <> 'ok'
        OR (
            transcript_text IS NOT NULL
            AND transcript_sha256 IS NOT NULL
        )
    )
);

CREATE TABLE current_transcriptions (
    page_id             INTEGER NOT NULL
                            REFERENCES physical_pages(id),
    purpose             TEXT NOT NULL,
    transcription_id   INTEGER NOT NULL,
    selected_at         TEXT NOT NULL,
    PRIMARY KEY (page_id, purpose),
    FOREIGN KEY (page_id, purpose, transcription_id)
        REFERENCES transcriptions(page_id, purpose, id),
    CHECK (purpose IN (
        'masthead',
        'candidate_content',
        'full_page',
        'recall_reference'
    ))
);
```

Uma mudança de modelo, versão, prompt, recorte visual ou imagem de entrada sempre cria nova transcrição.

O arquivo exportado deve incorporar uma identidade estável, por exemplo:

```text
dados/transcricoes/{jornal}/{edition_logical_key}/page_{page_number}/{transcription_id}.txt
```

O hash do arquivo deve ser igual a `transcript_sha256`.

### 4.9 Data como sub-registro

A data nunca é uma coluna sobrescrita em `edition_days`.

```sql
CREATE TABLE date_records (
    id                  INTEGER PRIMARY KEY,
    edition_day_id      INTEGER NOT NULL
                            REFERENCES edition_days(id),
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    evidence_page_id    INTEGER
                            REFERENCES physical_pages(id),
    evidence_transcription_id INTEGER
                            REFERENCES transcriptions(id),
    evidence_region_json TEXT,
    date_literal        TEXT,
    parser_name         TEXT NOT NULL,
    parser_version      TEXT NOT NULL,
    normalized_date     TEXT,
    status              TEXT NOT NULL,
    imputation_method   TEXT,
    confidence          REAL,
    notes               TEXT,
    created_at          TEXT NOT NULL,
    UNIQUE (edition_day_id, id),
    CHECK (normalized_date IS NULL OR length(normalized_date) = 10),
    CHECK (status IN (
        'observed',
        'imputed',
        'unresolved'
    )),
    CHECK (
        confidence IS NULL
        OR confidence BETWEEN 0.0 AND 1.0
    ),
    CHECK (
        status <> 'observed'
        OR (
            evidence_page_id IS NOT NULL
            AND evidence_region_json IS NOT NULL
            AND date_literal IS NOT NULL
            AND normalized_date IS NOT NULL
        )
    ),
    CHECK (
        status <> 'imputed'
        OR (imputation_method IS NOT NULL AND normalized_date IS NOT NULL)
    ),
    -- Achado B: falha de parse de data é registro positivo, não ausência
    -- de ponteiro. A página examinada fica registrada mesmo sem data.
    CHECK (
        status <> 'unresolved'
        OR (normalized_date IS NULL AND evidence_page_id IS NOT NULL)
    )
);

CREATE TABLE date_record_sources (
    date_record_id      INTEGER NOT NULL
                            REFERENCES date_records(id),
    source_date_record_id INTEGER NOT NULL
                            REFERENCES date_records(id),
    source_role         TEXT NOT NULL,
    PRIMARY KEY (
        date_record_id,
        source_date_record_id,
        source_role
    ),
    CHECK (source_role IN (
        'previous_issue',
        'next_issue',
        'same_object',
        'calendar_evidence',
        'manual_reference'
    )),
    CHECK (date_record_id <> source_date_record_id)
);

CREATE TABLE current_edition_dates (
    edition_day_id      INTEGER PRIMARY KEY
                            REFERENCES edition_days(id),
    date_record_id      INTEGER NOT NULL,
    selected_at         TEXT NOT NULL,
    FOREIGN KEY (edition_day_id, date_record_id)
        REFERENCES date_records(edition_day_id, id)
);

CREATE VIEW v_current_edition_dates AS
SELECT
    e.id AS edition_day_id,
    e.newspaper_id,
    d.normalized_date,
    d.date_literal,
    d.status,
    d.parser_name,
    d.parser_version,
    d.confidence,
    d.evidence_page_id,
    d.evidence_region_json
FROM edition_days AS e
JOIN current_edition_dates AS c
  ON c.edition_day_id = e.id
JOIN date_records AS d
  ON d.id = c.date_record_id;
```

Regras obrigatórias:

1. O masthead deve ser transcrito para toda edição com objeto disponível, independentemente da recuperação temática.
2. A data observada deve preservar texto literal, página e região visual.
3. Uma data inferida pela vizinhança é `imputed`.
4. Uma data imputada nunca é promovida a `observed`.
5. Se uma observação posterior resolver a data, cria-se novo registro e muda-se o ponteiro vigente.
6. A cobertura de datas observadas e imputadas deve ser reportada separadamente.
7. A extração de data não pode depender de a edição ter conteúdo sobre a Caixa.

### 4.10 Fases como classificação versionada a jusante

```sql
CREATE TABLE phase_schemes (
    id                  INTEGER PRIMARY KEY,
    name                TEXT NOT NULL,
    version             TEXT NOT NULL,
    description         TEXT NOT NULL,
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    created_at          TEXT NOT NULL,
    UNIQUE (name, version)
);

CREATE TABLE phase_definitions (
    id                  INTEGER PRIMARY KEY,
    phase_scheme_id     INTEGER NOT NULL
                            REFERENCES phase_schemes(id),
    phase_code          TEXT NOT NULL,
    phase_label         TEXT NOT NULL,
    start_date          TEXT NOT NULL,
    end_date            TEXT NOT NULL,
    UNIQUE (phase_scheme_id, phase_code),
    CHECK (start_date <= end_date)
);

CREATE TABLE current_phase_schemes (
    context_name        TEXT PRIMARY KEY,
    phase_scheme_id     INTEGER NOT NULL
                            REFERENCES phase_schemes(id),
    selected_at         TEXT NOT NULL
);

CREATE VIEW v_current_edition_phases AS
SELECT
    d.edition_day_id,
    d.normalized_date,
    s.context_name,
    p.phase_code,
    p.phase_label,
    p.phase_scheme_id
FROM v_current_edition_dates AS d
JOIN current_phase_schemes AS s
JOIN phase_definitions AS p
  ON p.phase_scheme_id = s.phase_scheme_id
 AND d.normalized_date BETWEEN p.start_date AND p.end_date;
```

Nenhuma tabela nuclear recebe uma coluna `fase`.

### 4.11 Auditoria de recall

A auditoria deve ser vinculada ao protocolo avaliado, à população, à amostra sorteada e ao padrão de referência.

```sql
CREATE TABLE recall_audits (
    id                  INTEGER PRIMARY KEY,
    name                TEXT NOT NULL,
    target_stage        TEXT NOT NULL,
    population_definition_id INTEGER NOT NULL
                            REFERENCES population_definitions(id),
    evaluated_protocol_id INTEGER NOT NULL
                            REFERENCES protocols(id),
    reference_protocol_id INTEGER NOT NULL
                            REFERENCES protocols(id),
    confidence_level    REAL NOT NULL,
    minimum_recall_lcb  REAL NOT NULL,
    sampling_method     TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    UNIQUE (name),
    CHECK (target_stage IN (
        'search',
        'screening',
        'substantive_identification'
    )),
    CHECK (confidence_level > 0.0 AND confidence_level < 1.0),
    CHECK (minimum_recall_lcb > 0.0 AND minimum_recall_lcb <= 1.0),
    CHECK (sampling_method IN (
        'stratified_srswor',
        'two_phase_stratified_srswor'
    ))
);

CREATE TABLE recall_strata (
    id                  INTEGER PRIMARY KEY,
    recall_audit_id     INTEGER NOT NULL
                            REFERENCES recall_audits(id),
    newspaper_id        INTEGER NOT NULL
                            REFERENCES newspapers(id),
    phase_definition_id INTEGER NOT NULL
                            REFERENCES phase_definitions(id),
    retrieval_stratum   TEXT NOT NULL,
    frame_size          INTEGER NOT NULL,
    planned_sample_size INTEGER NOT NULL,
    random_seed         INTEGER NOT NULL,
    selection_code_sha256 TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    UNIQUE (
        recall_audit_id,
        newspaper_id,
        phase_definition_id,
        retrieval_stratum
    ),
    CHECK (retrieval_stratum IN (
        'recovered',
        'not_recovered'
    )),
    CHECK (frame_size >= 0),
    CHECK (planned_sample_size >= 0),
    CHECK (planned_sample_size <= frame_size),
    CHECK (length(selection_code_sha256) = 64)
);

CREATE TABLE recall_sample_units (
    id                  INTEGER PRIMARY KEY,
    recall_stratum_id   INTEGER NOT NULL
                            REFERENCES recall_strata(id),
    edition_day_id      INTEGER NOT NULL
                            REFERENCES edition_days(id),
    draw_order          INTEGER NOT NULL,
    random_value        REAL NOT NULL,
    inclusion_probability REAL NOT NULL,
    selected_at         TEXT NOT NULL,
    UNIQUE (recall_stratum_id, edition_day_id),
    UNIQUE (recall_stratum_id, draw_order),
    CHECK (draw_order >= 1),
    CHECK (
        inclusion_probability > 0.0
        AND inclusion_probability <= 1.0
    )
);

CREATE TABLE recall_reference_labels (
    id                  INTEGER PRIMARY KEY,
    sample_unit_id      INTEGER NOT NULL
                            REFERENCES recall_sample_units(id),
    page_id             INTEGER
                            REFERENCES physical_pages(id),
    reference_result    TEXT NOT NULL,
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    reviewer_id         TEXT NOT NULL,
    evidence_text       TEXT,
    evidence_region_json TEXT,
    raw_response_text   TEXT,
    raw_response_path   TEXT,
    raw_response_sha256 TEXT NOT NULL,
    adjudication_status TEXT NOT NULL,
    assessed_at         TEXT NOT NULL,
    CHECK (reference_result IN (
        'relevant',
        'not_relevant',
        'uncertain',
        'error'
    )),
    CHECK (adjudication_status IN (
        'single_review',
        'double_agreement',
        'adjudicated'
    )),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL
        OR raw_response_path IS NOT NULL
    )
);

CREATE TABLE recall_gate_results (
    id                  INTEGER PRIMARY KEY,
    recall_audit_id     INTEGER NOT NULL
                            REFERENCES recall_audits(id),
    newspaper_id        INTEGER NOT NULL
                            REFERENCES newspapers(id),
    phase_definition_id INTEGER NOT NULL
                            REFERENCES phase_definitions(id),
    computed_at         TEXT NOT NULL,
    estimator           TEXT NOT NULL,
    interval_method     TEXT NOT NULL,
    sampled_units       INTEGER NOT NULL,
    reference_relevant_units INTEGER NOT NULL,
    recovered_relevant_units INTEGER NOT NULL,
    estimated_recall    REAL NOT NULL,
    lower_confidence_bound REAL NOT NULL,
    upper_confidence_bound REAL NOT NULL,
    effective_sample_size REAL NOT NULL,
    computation_code_sha256 TEXT NOT NULL,
    result              TEXT NOT NULL,
    CHECK (estimator IN (
        'horvitz_thompson',
        'hajek'
    )),
    CHECK (interval_method IN (
        'rao_wu_bootstrap',
        'exact_hypergeometric'
    )),
    CHECK (estimated_recall BETWEEN 0.0 AND 1.0),
    CHECK (lower_confidence_bound BETWEEN 0.0 AND 1.0),
    CHECK (upper_confidence_bound BETWEEN 0.0 AND 1.0),
    CHECK (lower_confidence_bound <= estimated_recall),
    CHECK (estimated_recall <= upper_confidence_bound),
    CHECK (length(computation_code_sha256) = 64),
    CHECK (result IN (
        'pass',
        'fail',
        'insufficient_sample'
    ))
);
```

#### Dimensionamento do gate

O gate recomendado é:

```text
Limite inferior unilateral de 95% para recall maior ou igual a 0,90,
separadamente para cada jornal e cada fase.
```

A amostra não será um número fixo de edições negativas. Será uma amostra probabilística de edição-dias elegíveis, estratificada por jornal, fase e resultado de recuperação, com probabilidades de inclusão preservadas.

Cada edição sorteada será lida integralmente para formar a referência.

A coleta continua até que cada combinação de jornal e fase tenha:

1. Tamanho efetivo de pelo menos 29 unidades realmente relevantes na referência.
2. Limite inferior de confiança maior ou igual a 0,90.
3. Nenhum estrato com resultado `insufficient_sample`.

Com zero perdas entre 29 unidades relevantes, o limite inferior unilateral exato de 95% fica aproximadamente em 0,90. Se houver uma ou mais perdas, a amostra deve crescer até o intervalo satisfazer o gate ou o protocolo deve ser rejeitado.

A alternativa mais rigorosa é exigir limite inferior de 0,95. Com zero perdas, ela exige pelo menos 59 unidades relevantes por jornal e fase. Essa alternativa tem custo substancialmente maior e depende de decisão de Pedro.

Quinze edições negativas por jornal não constituem o gate. Mesmo sem falhas observadas, esse tamanho deixa compatível uma taxa de falha próxima de 20%.

### 4.12 Classificações versionadas a jusante

A tabela abaixo fornece somente a interface de proveniência. Os rótulos substantivos e regras de agregação serão fechados na rodada metodológica.

```sql
CREATE TABLE classification_runs (
    id                  INTEGER PRIMARY KEY,
    classification_family TEXT NOT NULL,
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    started_at          TEXT NOT NULL,
    completed_at        TEXT NOT NULL,
    run_status          TEXT NOT NULL,
    scope_manifest_sha256 TEXT NOT NULL,
    input_tokens        INTEGER,
    output_tokens       INTEGER,
    cost_micros         INTEGER,
    currency            TEXT,
    CHECK (run_status IN (
        'ok',
        'partial',
        'error'
    )),
    CHECK (length(scope_manifest_sha256) = 64)
);

CREATE TABLE edition_classifications (
    id                  INTEGER PRIMARY KEY,
    edition_day_id      INTEGER NOT NULL
                            REFERENCES edition_days(id),
    classification_run_id INTEGER NOT NULL
                            REFERENCES classification_runs(id),
    classification_family TEXT NOT NULL,
    result_status       TEXT NOT NULL,
    output_json         TEXT,
    raw_response_text   TEXT,
    raw_response_path   TEXT,
    raw_response_sha256 TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    UNIQUE (edition_day_id, classification_family, id),
    CHECK (result_status IN (
        'ok',
        'abstained',
        'error'
    )),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL
        OR raw_response_path IS NOT NULL
    ),
    CHECK (
        result_status <> 'ok'
        OR output_json IS NOT NULL
    )
);

CREATE TABLE classification_inputs (
    classification_id  INTEGER NOT NULL
                            REFERENCES edition_classifications(id),
    transcription_id   INTEGER NOT NULL
                            REFERENCES transcriptions(id),
    PRIMARY KEY (classification_id, transcription_id)
);

CREATE TABLE current_edition_classifications (
    edition_day_id      INTEGER NOT NULL
                            REFERENCES edition_days(id),
    classification_family TEXT NOT NULL,
    classification_id  INTEGER NOT NULL,
    selected_at         TEXT NOT NULL,
    PRIMARY KEY (edition_day_id, classification_family),
    FOREIGN KEY (
        edition_day_id,
        classification_family,
        classification_id
    )
    REFERENCES edition_classifications(
        edition_day_id,
        classification_family,
        id
    )
);
```

Uma classificação pode ser reproduzida porque referencia exatamente as versões de transcrição que recebeu.

## 5. Auditoria dos casos P0 de 1906

Os 280 casos classificados como sem menção relevante e os 169 casos com data ausente devem ter identidade própria de auditoria.

```sql
CREATE TABLE audit_cases (
    id                  INTEGER PRIMARY KEY,
    case_type           TEXT NOT NULL,
    legacy_identifier   TEXT NOT NULL,
    edition_day_id      INTEGER
                            REFERENCES edition_days(id),
    search_hit_id       INTEGER
                            REFERENCES search_hits(id),
    page_id             INTEGER
                            REFERENCES physical_pages(id),
    imported_at         TEXT NOT NULL,
    UNIQUE (case_type, legacy_identifier),
    CHECK (case_type IN (
        'p0_no_relevant_mention_1906',
        'p0_missing_date_1906'
    ))
);

CREATE TABLE audit_findings (
    id                  INTEGER PRIMARY KEY,
    audit_case_id       INTEGER NOT NULL
                            REFERENCES audit_cases(id),
    protocol_id         INTEGER NOT NULL
                            REFERENCES protocols(id),
    finding             TEXT NOT NULL,
    explanation         TEXT NOT NULL,
    raw_response_text   TEXT,
    raw_response_path   TEXT,
    raw_response_sha256 TEXT NOT NULL,
    assessed_at         TEXT NOT NULL,
    UNIQUE (audit_case_id, id),
    CHECK (finding IN (
        'substantively_not_relevant',
        'wrong_page',
        'wrong_object',
        'transcription_omission',
        'transcription_truncation',
        'reading_failure',
        'classification_failure',
        'unresolved_search_hit',
        'date_parser_failure',
        'masthead_unreadable',
        'other',
        'pending'
    )),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL
        OR raw_response_path IS NOT NULL
    )
);

CREATE TABLE current_audit_findings (
    audit_case_id       INTEGER PRIMARY KEY
                            REFERENCES audit_cases(id),
    audit_finding_id    INTEGER NOT NULL,
    selected_at         TEXT NOT NULL,
    FOREIGN KEY (audit_case_id, audit_finding_id)
        REFERENCES audit_findings(audit_case_id, id)
);
```

O P0 só fecha quando:

1. Os 280 casos possuem edição, objeto e página resolvidos, ou achado explícito `unresolved_search_hit`.
2. Cada caso possui motivo vigente.
3. Nenhum caso pendente entra em resultado agregado.
4. Os 169 casos de data possuem novo registro observado ou imputado.
5. Observados e imputados são reportados separadamente.

## 6. Cascata de populações

A cascata deve ser calculada para uma combinação explícita de:

1. `population_definition_id`
2. `search_campaign_id`
3. nível de avaliação
4. protocolo de transcrição
5. família de classificação
6. esquema de fases

As populações são:

| Estágio | Definição operacional |
|---|---|
| Inventariadas | Edições elegíveis vinculadas a pelo menos um objeto digital |
| Disponíveis | Inventariadas com obtenção vigente `ok`, hash válido e todas as páginas materializadas |
| Avaliadas | Disponíveis com avaliação vigente resolvida em todas as páginas incluídas |
| Recuperadas | Avaliadas com pelo menos um candidato produzido pela campanha de recuperação vigente |
| Substantivamente relevantes | Recuperadas com pelo menos uma página confirmada como relevante no nível substantivo ou na adjudicação |
| Transcritas | Relevantes cujas páginas relevantes possuem transcrição vigente bem-sucedida |
| Classificadas | Transcritas com classificação vigente bem-sucedida e entradas de transcrição explicitamente vinculadas |

Cada estágio é subconjunto do anterior na cascata de produção. Descobertas feitas somente durante a auditoria de recall não entram retroativamente na cascata. Elas obrigam uma nova execução do protocolo de recuperação, que produz novos hits e uma nova cascata.

### 6.1 Denominador da saliência

O denominador recomendado para saliência é:

```text
edição-dias elegíveis, disponíveis e efetivamente avaliadas
```

Nunca é:

```text
número de hits
```

Uma edição não está efetivamente avaliada se qualquer página incluída estiver como `uncertain`, `error`, `not_assessed` ou sem ponteiro vigente.

A escolha entre edição-dia estrita e múltiplas edições por dia será determinada por `population_definitions.unit_mode`.

### 6.2 Estados de ausência

Os seguintes estados são distintos:

| Estado | Regra |
|---|---|
| Não circulou | Avaliação vigente do calendário igual a `did_not_circulate` |
| Circulou, mas falta no acervo | Calendário igual a `circulated`, sem objeto inventariado correspondente |
| Existe no acervo, mas não foi obtido | Objeto inventariado sem obtenção vigente bem-sucedida |
| Foi obtido, mas falhou no pipeline | PDF disponível com páginas incompletas, avaliação em erro ou outra falha posterior |
| Ainda não foi avaliado | Página com resultado vigente `not_assessed` |
| Avaliação inconclusiva | Página com resultado vigente `uncertain` |
| Negativo substantivo | Avaliação resolvida `not_relevant`, nunca inferida da ausência de linha |

Esses estados devem aparecer separadamente nos relatórios de cobertura.

## 7. Gate de economia da identificação

A arquitetura seletiva não será adotada apenas porque a chamada de transcrição de qualidade parece cara. O custo de leitura das imagens pela triagem pode dominar a economia.

### 7.1 Desenho do benchmark

O benchmark inicial usa 1906 e inclui no mínimo 120 edição-dias:

1. Trinta por jornal.
2. Quinze recuperadas pela busca legada e quinze não recuperadas, quando o frame permitir.
3. Distribuição equilibrada pelos quatro trimestres.
4. Todas as páginas físicas de cada edição selecionada.
5. Leitura integral de referência para medir perdas da triagem.

Devem ser comparados pelo menos:

1. OCR existente da BN.
2. OCR local.
3. Visão de baixo custo.
4. Transcrição de qualidade de todas as páginas, como referência de custo.

Cada alternativa deve registrar:

1. Bytes e megapixels de entrada.
2. Tokens de entrada e saída.
3. Tempo de processamento.
4. Requisições, falhas e novas tentativas.
5. Custo monetário real.
6. Percentual de páginas selecionadas.
7. Recall e precisão contra leitura integral.
8. Custo projetado do lote completo.
9. Custo da auditoria e da adjudicação.

### 7.2 Regra do gate

A identificação seletiva só pode ser escolhida se:

1. Passar o gate de recall por jornal e fase.
2. O limite superior de 95% do custo total projetado da estratégia seletiva for menor ou igual a 70% do custo da transcrição completa.
3. O cálculo incluir triagem, entrada visual, novas tentativas, auditoria, adjudicação e transcrição dos candidatos.
4. A diferença não depender de preços promocionais temporários não registrados.
5. O protocolo conseguir avaliar todas as páginas, não apenas as páginas retornadas pela busca da BN.

Se qualquer condição falhar, a alternativa padrão é transcrever integralmente ou redesenhar a triagem.

## 8. Gate de validação de data

A validação de 1906 deve ocorrer antes da expansão paga.

### 8.1 Procedimento

1. Importar e auditar todos os 169 casos anteriormente marcados como sem data.
2. Conferir manualmente todas as datas imputadas.
3. Sortear 59 datas observadas por jornal entre as datas que o parser considerou válidas, ou todas quando houver menos de 59.
4. Comparar data normalizada, texto literal e região do masthead contra a imagem.
5. Corrigir o parser, criar nova versão e reprocessar toda a população se aparecer erro sistemático.
6. Verificar validade de calendário e coerência de sequência dos números impressos, sem usar sequência para sobrescrever masthead observado.

### 8.2 Regra do gate

Por jornal, o limite inferior unilateral de 95% para a exatidão da data observada deve ser maior ou igual a 0,95.

Com zero erros, 59 casos conferidos atingem aproximadamente esse limite. Havendo erro, a amostra deve crescer e o parser deve ser revisto.

Além disso:

1. Toda edição disponível deve ter tentativa de transcrição do masthead.
2. Toda data vigente deve possuir protocolo e parser versionados.
3. Toda data observada deve apontar para página e região.
4. Toda data imputada deve declarar método e fontes.
5. Não pode haver correlação entre ausência de data e relevância temática causada pelo desenho do pipeline.

O mesmo gate deve ser repetido por jornal e fase antes da classificação substantiva dos anos posteriores.

## 9. Faseamento

### 9.1 Fase A, sem gates metodológicos

A Fase A pode começar após a implementação e teste do contrato mínimo de inventário.

Inclui:

1. Criar o banco e aplicar as migrações.
2. Inserir os quatro jornais.
3. Enumerar o calendário de 1906 a 1914.
4. Registrar avaliações de circulação quando houver evidência.
5. Enumerar todos os objetos digitais encontrados, não apenas hits.
6. Baixar PDFs inteiros.
7. Registrar cada tentativa de obtenção.
8. Calcular hash, tamanho e número de páginas.
9. Materializar uma linha para cada página física.
10. Criar avaliação inicial `not_assessed` para cada página.
11. Preservar os PDFs em `dados/raw_pdf/`.

A Fase A não depende de definição de postura, fase histórica ou protocolo final de recuperação.

A regressão de 1906 e a estimativa de custo continuam obrigatórias antes de lotes grandes.

### 9.2 Fase B, antes da transcrição substantiva em lote

A Fase B inclui:

1. Testar a relação entre objeto, edição lógica, suplemento e edição extraordinária.
2. Resolver divergências entre número da BN e número impresso.
3. Fechar a unidade de população escolhida por Pedro.
4. Executar o benchmark de economia da identificação.
5. Definir a campanha de recuperação de produção.
6. Avaliar todas as páginas com triagem barata.
7. Executar a amostra integral de recall.
8. Passar o gate de recall por jornal e fase.
9. Transcrever mastheads de todas as edições disponíveis.
10. Passar o gate de validação de data.
11. Resolver os 280 casos sem menção do P0.
12. Resolver os 169 casos sem data do P0.
13. Definir o denominador de saliência pela população versionada.
14. Somente então autorizar transcrição substantiva e classificação em lote.

Chamadas pagas limitadas aos benchmarks e validações são permitidas na Fase B após estimativa explícita. Elas não autorizam o lote completo.

## 10. Decisões reservadas a Pedro

### 10.1 Censo textual completo ou subcorpus recuperado

#### Recomendação

Manter completo o inventário, os PDFs e os mastheads, mas fazer a transcrição de qualidade somente das páginas candidatas, desde que os gates de economia e recall sejam aprovados.

O produto deve ser denominado:

> Subcorpus textual recuperado segundo o protocolo X, versão Y, a partir do censo de objetos digitais e edição-dias elegíveis.

Vantagens:

1. Reduz custo de transcrição e revisão.
2. Mantém os PDFs completos para reprocessamento.
3. Permite mudar o protocolo de recuperação sem baixar novamente o acervo.
4. Torna explícita a seleção substantiva.

Custos e vieses:

1. O texto disponível para análise permanece condicionado ao protocolo.
2. Recall imperfeito pode alterar saliência e distribuição de posições.
3. Mudanças terminológicas podem afetar jornais e fases de modo desigual.
4. A incerteza de recuperação deve acompanhar os resultados.

#### Alternativa

Transcrever integralmente todas as páginas de todas as edições disponíveis.

Vantagens:

1. Reduz a dependência de termos e triagem para formar o corpus textual.
2. Permite novas perguntas sem nova transcrição.
3. Facilita auditoria retrospectiva de omissões.

Custos e limitações:

1. O volume é aproximadamente oito a doze vezes o de uma página por edição, segundo os PDFs medidos.
2. O custo de entrada visual, armazenamento, revisão e controle de qualidade cresce na mesma ordem.
3. Transcrição completa não elimina erro de OCR, erro de modelo ou ausência de objetos no acervo.
4. Pode consumir recursos que seriam mais úteis em validação humana e análise.

Em ambos os caminhos, masthead, número impresso e data devem ser extraídos de todas as edições disponíveis.

### 10.2 Edição-dia estrita ou múltiplas edições no mesmo dia

#### Recomendação

Modelar múltiplas edições, suplementos e extraordinárias desde a coleta, mas usar inicialmente a edição-dia estrita como unidade principal de análise, agregando manifestações do mesmo jornal e data por regra pré-registrada.

Essa recomendação preserva a continuidade com o piloto e evita perder variação documental na camada bruta.

Antes da decisão final, o piloto deve informar:

1. Quantos dias têm mais de uma edição.
2. Quantos objetos são suplementos ou extraordinários.
3. Quantos objetos duplicam a mesma edição.
4. Quantos PDFs contêm mais de uma unidade lógica.
5. Se manifestações do mesmo dia apresentam conteúdo substantivamente diferente.
6. Quanto cada regra de agregação altera os resultados.

#### Alternativa

Tratar cada manifestação editorial distinta como unidade analítica, mesmo quando duas pertencem ao mesmo jornal e data.

Essa alternativa preserva diferenças entre edição matutina, vespertina, extraordinária e suplemento, mas muda o estimando. Jornais ou dias com mais manifestações passam a ter maior peso, a menos que a análise aplique ponderação ou agregação posterior.

A escolha será registrada em uma nova versão de `population_definitions`. O esquema não obriga nenhuma das duas decisões.

## 11. Verificações obrigatórias do contrato

Antes de considerar a implementação pronta, os testes devem confirmar:

1. `PRAGMA foreign_keys` está ativo em toda conexão.
2. Enums inválidos falham por `CHECK`.
3. Campos obrigatórios falham por `NOT NULL`.
4. Chaves naturais duplicadas falham por `UNIQUE`.
5. Toda obtenção `ok` possui hash, caminho, tamanho e número de páginas.
6. Toda obtenção `ok` possui exatamente o número esperado de páginas.
7. Toda página possui avaliação vigente, inclusive `not_assessed`.
8. Nenhum negativo é inferido da ausência de linha.
9. Toda execução com modelo registra modelo e versão exatos.
10. Toda decisão de relevância possui protocolo, prompt, resposta ou arquivo bruto, hash e data.
11. Toda transcrição referencia o hash visual de entrada.
12. Alterar modelo ou prompt cria nova transcrição.
13. Toda data observada possui literal, página e região.
14. Toda data imputada permanece distinguível.
15. Todo hit marcado como resolvido alcança objeto, edição e página.
16. Todo input de classificação referencia transcrição exata.
17. A cascata é monotônica para uma configuração de produção.
18. O denominador de saliência nunca usa hits como população.
19. O piloto de 1906 pode ser importado sem perda de proveniência.
20. Reexecutar uma etapa cria novas linhas históricas e muda apenas ponteiros vigentes.
21. O export textual possui o mesmo hash registrado no banco.
22. Banco novo criado por `schema.sql` e banco migrado produzem o mesmo esquema.
23. `PRAGMA integrity_check` retorna `ok`.
24. `PRAGMA foreign_key_check` não retorna linhas.

## 12. Critério de conclusão do design

Este design está pronto para virar plano de implementação quando Pedro decidir:

1. O nível exigido para o gate de recall, recomendação de 0,90 ou alternativa de 0,95.
2. Censo textual completo ou subcorpus recuperado.
3. Edição-dia estrita ou múltiplas manifestações como unidade principal.

A enumeração do censo e o download dos PDFs inteiros não precisam aguardar essas três decisões. A transcrição substantiva e a classificação em lote precisam.

### Decidido em 2026-07-17

As três decisões foram fechadas por Pedro, com análise independente do Claude. Registro em `docs/decisoes.md`, entrada de 2026-07-17:

1. Gate de recall: limite inferior unilateral de 95% maior ou igual a 0,90, por jornal e fase.
2. Censo textual: subcorpus recuperado, com triagem barata em toda página e transcrição de qualidade só nas candidatas; camada bruta completa.
3. Unidade principal: edição-dia estrita, com manifestações modeladas na camada bruta.

O critério de conclusão do design está satisfeito. A Fase B fica desbloqueada no que depende de decisão de Pedro.
