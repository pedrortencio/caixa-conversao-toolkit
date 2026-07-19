-- Migração 003: camada de texto embutido (OCR da BN).
-- Design e contrato: docs/superpowers/specs/2026-07-18-camada-texto-embutido-design.md.
--
-- Aditiva: cria text_extraction_runs, page_text_extractions e
-- current_page_text_extractions (padrão runs + registros append-only +
-- ponteiro de vigência), índices e a view v_current_page_texts.
--
-- protocols ganha o estágio 'text_extraction' na lista do CHECK. SQLite não
-- permite ALTER de CHECK; a tabela é reconstruída pelo padrão da migração
-- 002 (tabela de retenção + DROP + CREATE sob o nome final, nunca RENAME;
-- ver o comentário da 002 e o desligamento de PRAGMA foreign_keys em
-- apply_migrations). Nenhuma view lê protocols, então não há views a
-- derrubar. O texto do CREATE é idêntico ao de schema.sql (teste de
-- paridade via sqlite_master).

CREATE TABLE _migration_003_protocols_holding AS
SELECT * FROM protocols;

DROP TABLE protocols;

CREATE TABLE protocols (
    id INTEGER PRIMARY KEY,
    stage TEXT NOT NULL,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    executor_type TEXT NOT NULL,
    code_commit TEXT NOT NULL,
    model_provider TEXT,
    model_name TEXT,
    model_version TEXT,
    prompt_version TEXT,
    prompt_sha256 TEXT,
    prompt_path TEXT,
    parameters_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (stage, name, version),
    CHECK (stage IN (
        'inventory', 'circulation', 'search', 'identification',
        'transcription', 'text_extraction', 'date_parsing',
        'recall_reference', 'classification'
    )),
    CHECK (executor_type IN (
        'deterministic', 'manual', 'model', 'external_service'
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
    CHECK (prompt_sha256 IS NULL OR length(prompt_sha256) = 64)
);

INSERT INTO protocols(
    id, stage, name, version, executor_type, code_commit,
    model_provider, model_name, model_version, prompt_version,
    prompt_sha256, prompt_path, parameters_json, created_at
)
SELECT
    id, stage, name, version, executor_type, code_commit,
    model_provider, model_name, model_version, prompt_version,
    prompt_sha256, prompt_path, parameters_json, created_at
FROM _migration_003_protocols_holding;

DROP TABLE _migration_003_protocols_holding;

CREATE TABLE text_extraction_runs (
    id INTEGER PRIMARY KEY,
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    run_status TEXT NOT NULL,
    scope_manifest_sha256 TEXT NOT NULL,
    pages_submitted INTEGER NOT NULL,
    pages_completed INTEGER NOT NULL,
    elapsed_seconds REAL,
    CHECK (run_status IN ('ok', 'partial', 'error')),
    CHECK (length(scope_manifest_sha256) = 64),
    CHECK (pages_submitted >= 0),
    CHECK (pages_completed >= 0),
    CHECK (pages_completed <= pages_submitted)
);

CREATE TABLE page_text_extractions (
    id INTEGER PRIMARY KEY,
    page_id INTEGER NOT NULL REFERENCES physical_pages(id),
    extraction_run_id INTEGER NOT NULL REFERENCES text_extraction_runs(id),
    source_pdf_sha256 TEXT NOT NULL,
    result_status TEXT NOT NULL,
    text_path TEXT,
    text_sha256 TEXT,
    char_count INTEGER,
    error_class TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (page_id, id),
    CHECK (length(source_pdf_sha256) = 64),
    CHECK (result_status IN ('ok', 'empty', 'error')),
    CHECK (text_sha256 IS NULL OR length(text_sha256) = 64),
    CHECK (char_count IS NULL OR char_count >= 0),
    CHECK (
        result_status <> 'ok'
        OR (
            text_path IS NOT NULL
            AND text_sha256 IS NOT NULL
            AND char_count IS NOT NULL
            AND char_count > 0
        )
    ),
    -- Página sem camada de texto é registro positivo com char_count = 0,
    -- nunca um arquivo vazio nem hash fabricado (contrato do design de
    -- 2026-07-18, camada de texto embutido).
    CHECK (
        result_status <> 'empty'
        OR (
            char_count = 0
            AND text_path IS NULL
            AND text_sha256 IS NULL
        )
    ),
    CHECK (result_status <> 'error' OR error_class IS NOT NULL)
);

CREATE TABLE current_page_text_extractions (
    page_id INTEGER PRIMARY KEY REFERENCES physical_pages(id),
    extraction_id INTEGER NOT NULL,
    selected_at TEXT NOT NULL,
    FOREIGN KEY (page_id, extraction_id)
        REFERENCES page_text_extractions(page_id, id)
);

CREATE INDEX ix_text_extraction_runs_protocol
    ON text_extraction_runs(protocol_id);
CREATE INDEX ix_page_text_extractions_page
    ON page_text_extractions(page_id);
CREATE INDEX ix_page_text_extractions_run
    ON page_text_extractions(extraction_run_id);

CREATE VIEW v_current_page_texts AS
SELECT
    p.id AS page_id,
    p.object_id,
    p.page_number,
    x.result_status,
    x.char_count,
    x.text_path,
    x.text_sha256,
    x.source_pdf_sha256,
    x.extraction_run_id
FROM physical_pages AS p
JOIN current_page_text_extractions AS c ON c.page_id = p.id
JOIN page_text_extractions AS x ON x.id = c.extraction_id;
