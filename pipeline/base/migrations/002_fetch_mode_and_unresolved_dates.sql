-- Migração 002: achados B, D e E.1 da revisão independente de 2026-07-17
-- (docs/revisao-independente-claude-2026-07-17.md).
--
-- D: object_fetches ganha fetch_mode ('http' | 'local_import'), formalizando
-- a relaxação do CHECK que hoje só vive no DDL: um download HTTP real com
-- http_status nulo não passa mais despercebido.
-- E.1: corrige o response_sha256 fabricado (= pdf_sha256) das obtenções
-- importadas localmente, antes de travar a regra por CHECK.
-- B: date_records passa a admitir status 'unresolved' com normalized_date
-- nulo, um registro positivo para falha de parse de data (em vez de
-- ausência silenciosa de ponteiro em current_edition_dates).
--
-- SQLite não permite ALTER de CHECK/NOT NULL; as duas tabelas são
-- reconstruídas via tabela de retenção (CREATE TABLE ... AS SELECT, sem
-- vínculo de FK) e um DROP+CREATE direto sob o nome final, nunca um
-- RENAME da tabela original: RENAME reescreve o texto da FK dos filhos
-- para o nome antigo (current_object_fetches/date_record_sources/
-- current_edition_dates ficariam órfãos ao sumir a tabela renomeada) e
-- também passa a citar o nome final entre aspas em sqlite_master,
-- divergindo do texto de schema.sql. Ver apply_migrations em
-- pipeline/base/db.py para o desligamento de PRAGMA foreign_keys que essa
-- reconstrução exige.
--
-- As views que leem essas tabelas também precisam ser derrubadas antes (o
-- SQLite reavalia o schema entre statements do script e quebra numa view
-- órfã se a tabela some, mesmo que reapareça mais adiante no mesmo
-- script) e recriadas ao final com o texto idêntico ao de schema.sql.

DROP VIEW v_digital_object_inventory;
DROP VIEW v_current_edition_phases;
DROP VIEW v_current_edition_dates;

CREATE TABLE _migration_002_object_fetches_holding AS
SELECT * FROM object_fetches;

DROP TABLE object_fetches;

CREATE TABLE object_fetches (
    id INTEGER PRIMARY KEY,
    object_id INTEGER NOT NULL REFERENCES digital_objects(id),
    fetch_mode TEXT NOT NULL DEFAULT 'http',
    attempted_at TEXT NOT NULL,
    completed_at TEXT,
    result TEXT NOT NULL,
    http_status INTEGER,
    storage_path TEXT,
    pdf_sha256 TEXT,
    response_sha256 TEXT,
    byte_count INTEGER,
    page_count INTEGER,
    error_class TEXT,
    error_message TEXT,
    UNIQUE (object_id, id),
    CHECK (fetch_mode IN ('http', 'local_import')),
    CHECK (result IN (
        'ok', 'http_error', 'network_error', 'invalid_pdf', 'storage_error'
    )),
    CHECK (http_status IS NULL OR http_status BETWEEN 100 AND 599),
    CHECK (pdf_sha256 IS NULL OR length(pdf_sha256) = 64),
    CHECK (response_sha256 IS NULL OR length(response_sha256) = 64),
    -- Só resposta HTTP real produz hash de resposta; importação local não
    -- fabrica um response_sha256 (achado E.1 do parecer de 2026-07-17).
    CHECK (fetch_mode = 'http' OR response_sha256 IS NULL),
    CHECK (
        result <> 'ok'
        OR (
            (
                (fetch_mode = 'http' AND http_status BETWEEN 200 AND 299)
                OR (fetch_mode = 'local_import' AND http_status IS NULL)
            )
            AND storage_path IS NOT NULL
            AND pdf_sha256 IS NOT NULL
            AND byte_count IS NOT NULL
            AND byte_count > 0
            AND page_count IS NOT NULL
            AND page_count > 0
        )
    )
);

INSERT INTO object_fetches (
    id, object_id, fetch_mode, attempted_at, completed_at, result,
    http_status, storage_path, pdf_sha256, response_sha256, byte_count,
    page_count, error_class, error_message
)
SELECT
    id,
    object_id,
    CASE WHEN http_status IS NULL THEN 'local_import' ELSE 'http' END,
    attempted_at,
    completed_at,
    result,
    http_status,
    storage_path,
    pdf_sha256,
    CASE WHEN http_status IS NULL THEN NULL ELSE response_sha256 END,
    byte_count,
    page_count,
    error_class,
    error_message
FROM _migration_002_object_fetches_holding;

DROP TABLE _migration_002_object_fetches_holding;

CREATE INDEX ix_object_fetches_object_result
    ON object_fetches(object_id, result);

CREATE TABLE _migration_002_date_records_holding AS
SELECT * FROM date_records;

DROP TABLE date_records;

CREATE TABLE date_records (
    id INTEGER PRIMARY KEY,
    edition_day_id INTEGER NOT NULL REFERENCES edition_days(id),
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    evidence_page_id INTEGER REFERENCES physical_pages(id),
    evidence_transcription_id INTEGER REFERENCES transcriptions(id),
    evidence_region_json TEXT,
    date_literal TEXT,
    parser_name TEXT NOT NULL,
    parser_version TEXT NOT NULL,
    normalized_date TEXT,
    status TEXT NOT NULL,
    imputation_method TEXT,
    confidence REAL,
    notes TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (edition_day_id, id),
    CHECK (normalized_date IS NULL OR length(normalized_date) = 10),
    CHECK (status IN ('observed', 'imputed', 'unresolved')),
    CHECK (confidence IS NULL OR confidence BETWEEN 0.0 AND 1.0),
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
    -- Falha de parse é registro positivo, não ausência de ponteiro
    -- (achado B do parecer de 2026-07-17): a página examinada fica
    -- registrada mesmo quando nenhuma data pôde ser normalizada.
    CHECK (
        status <> 'unresolved'
        OR (normalized_date IS NULL AND evidence_page_id IS NOT NULL)
    )
);

INSERT INTO date_records SELECT * FROM _migration_002_date_records_holding;

DROP TABLE _migration_002_date_records_holding;

CREATE INDEX ix_date_records_edition
    ON date_records(edition_day_id);
CREATE INDEX ix_date_records_protocol
    ON date_records(protocol_id);
CREATE INDEX ix_date_records_page
    ON date_records(evidence_page_id);
CREATE INDEX ix_date_records_transcription
    ON date_records(evidence_transcription_id);

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
JOIN newspapers AS n ON n.id = o.newspaper_id
LEFT JOIN current_object_fetches AS cf ON cf.object_id = o.id
LEFT JOIN object_fetches AS f ON f.id = cf.fetch_id;

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
JOIN current_edition_dates AS c ON c.edition_day_id = e.id
JOIN date_records AS d ON d.id = c.date_record_id;

CREATE VIEW v_current_edition_phases AS
SELECT
    d.edition_day_id,
    d.normalized_date,
    s.context_name,
    p.phase_code,
    p.phase_label,
    p.phase_scheme_id
FROM v_current_edition_dates AS d
CROSS JOIN current_phase_schemes AS s
JOIN phase_definitions AS p
  ON p.phase_scheme_id = s.phase_scheme_id
 AND d.normalized_date BETWEEN p.start_date AND p.end_date;
