PRAGMA foreign_keys = ON;

CREATE TABLE newspapers (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    bn_bib TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    active_from TEXT,
    active_to TEXT,
    created_at TEXT NOT NULL
);

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
        'transcription', 'date_parsing', 'recall_reference',
        'classification'
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

CREATE TABLE calendar_days (
    id INTEGER PRIMARY KEY,
    newspaper_id INTEGER NOT NULL REFERENCES newspapers(id),
    civil_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (newspaper_id, civil_date),
    CHECK (length(civil_date) = 10)
);

CREATE TABLE digital_objects (
    id INTEGER PRIMARY KEY,
    newspaper_id INTEGER NOT NULL REFERENCES newspapers(id),
    source_identifier TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_year INTEGER NOT NULL,
    bn_file_key TEXT NOT NULL,
    bn_file_number_literal TEXT NOT NULL,
    discovered_by_protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    discovered_at TEXT NOT NULL,
    UNIQUE (source_identifier),
    UNIQUE (source_url),
    CHECK (source_year BETWEEN 1800 AND 2100)
);

CREATE TABLE edition_days (
    id INTEGER PRIMARY KEY,
    newspaper_id INTEGER NOT NULL REFERENCES newspapers(id),
    logical_key TEXT NOT NULL,
    edition_kind TEXT NOT NULL,
    sequence_in_day INTEGER,
    identity_status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (newspaper_id, logical_key),
    CHECK (edition_kind IN (
        'regular', 'supplement', 'extraordinary', 'special', 'unknown'
    )),
    CHECK (identity_status IN ('provisional', 'confirmed', 'ambiguous')),
    CHECK (sequence_in_day IS NULL OR sequence_in_day >= 1)
);

CREATE TABLE object_fetches (
    id INTEGER PRIMARY KEY,
    object_id INTEGER NOT NULL REFERENCES digital_objects(id),
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
    CHECK (result IN (
        'ok', 'http_error', 'network_error', 'invalid_pdf', 'storage_error'
    )),
    CHECK (http_status IS NULL OR http_status BETWEEN 100 AND 599),
    CHECK (pdf_sha256 IS NULL OR length(pdf_sha256) = 64),
    CHECK (response_sha256 IS NULL OR length(response_sha256) = 64),
    CHECK (
        result <> 'ok'
        OR (
            (http_status IS NULL OR http_status BETWEEN 200 AND 299)
            AND storage_path IS NOT NULL
            AND pdf_sha256 IS NOT NULL
            AND byte_count IS NOT NULL
            AND byte_count > 0
            AND page_count IS NOT NULL
            AND page_count > 0
        )
    )
);

CREATE TABLE current_object_fetches (
    object_id INTEGER PRIMARY KEY REFERENCES digital_objects(id),
    fetch_id INTEGER NOT NULL,
    selected_at TEXT NOT NULL,
    FOREIGN KEY (object_id, fetch_id)
        REFERENCES object_fetches(object_id, id)
);

CREATE TABLE physical_pages (
    id INTEGER PRIMARY KEY,
    object_id INTEGER NOT NULL REFERENCES digital_objects(id),
    page_number INTEGER NOT NULL,
    source_page_label TEXT,
    visual_path TEXT,
    visual_sha256 TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (object_id, page_number),
    CHECK (page_number >= 1),
    CHECK (visual_sha256 IS NULL OR length(visual_sha256) = 64)
);

CREATE TABLE circulation_assessments (
    id INTEGER PRIMARY KEY,
    calendar_day_id INTEGER NOT NULL REFERENCES calendar_days(id),
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    result TEXT NOT NULL,
    evidence_text TEXT,
    evidence_path TEXT,
    evidence_sha256 TEXT,
    assessed_at TEXT NOT NULL,
    UNIQUE (calendar_day_id, id),
    CHECK (result IN (
        'circulated', 'did_not_circulate', 'unknown', 'error'
    )),
    CHECK (evidence_sha256 IS NULL OR length(evidence_sha256) = 64)
);

CREATE TABLE current_circulation_assessments (
    calendar_day_id INTEGER PRIMARY KEY REFERENCES calendar_days(id),
    assessment_id INTEGER NOT NULL,
    selected_at TEXT NOT NULL,
    FOREIGN KEY (calendar_day_id, assessment_id)
        REFERENCES circulation_assessments(calendar_day_id, id)
);

CREATE TABLE population_definitions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    unit_mode TEXT NOT NULL,
    description TEXT NOT NULL,
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    created_at TEXT NOT NULL,
    UNIQUE (name, version),
    CHECK (unit_mode IN (
        'strict_newspaper_day', 'multiple_editions_per_day'
    ))
);

CREATE TABLE population_memberships (
    id INTEGER PRIMARY KEY,
    population_definition_id INTEGER NOT NULL
        REFERENCES population_definitions(id),
    calendar_day_id INTEGER NOT NULL REFERENCES calendar_days(id),
    edition_day_id INTEGER REFERENCES edition_days(id),
    eligibility TEXT NOT NULL,
    reason TEXT NOT NULL,
    assigned_at TEXT NOT NULL,
    CHECK (eligibility IN ('eligible', 'ineligible', 'unknown'))
);

CREATE TABLE edition_identifiers (
    id INTEGER PRIMARY KEY,
    edition_day_id INTEGER NOT NULL REFERENCES edition_days(id),
    identifier_type TEXT NOT NULL,
    literal_value TEXT NOT NULL,
    normalized_value TEXT,
    evidence_page_id INTEGER REFERENCES physical_pages(id),
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    observed_at TEXT NOT NULL,
    CHECK (identifier_type IN (
        'printed_issue_number', 'bn_file_number', 'source_folder',
        'legacy_identifier', 'other'
    ))
);

CREATE TABLE edition_object_links (
    id INTEGER PRIMARY KEY,
    edition_day_id INTEGER NOT NULL REFERENCES edition_days(id),
    object_id INTEGER NOT NULL REFERENCES digital_objects(id),
    link_role TEXT NOT NULL,
    include_in_content INTEGER NOT NULL,
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    linked_at TEXT NOT NULL,
    UNIQUE (edition_day_id, object_id, link_role),
    CHECK (link_role IN (
        'principal', 'continuation', 'supplement', 'extraordinary',
        'duplicate_scan', 'partial_scan', 'unknown'
    )),
    CHECK (include_in_content IN (0, 1))
);

CREATE TABLE search_campaigns (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    objective TEXT NOT NULL,
    newspaper_id INTEGER REFERENCES newspapers(id),
    start_date TEXT,
    end_date TEXT,
    query_text TEXT NOT NULL,
    campaign_role TEXT NOT NULL,
    created_at TEXT NOT NULL,
    CHECK (campaign_role IN (
        'production_retrieval', 'expanded_retrieval',
        'recall_audit', 'legacy_import'
    ))
);

CREATE TABLE search_runs (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES search_campaigns(id),
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    run_status TEXT NOT NULL,
    scope_manifest_sha256 TEXT NOT NULL,
    raw_response_text TEXT,
    raw_response_path TEXT,
    raw_response_sha256 TEXT NOT NULL,
    input_units INTEGER,
    output_hits INTEGER,
    input_tokens INTEGER,
    output_tokens INTEGER,
    input_megapixels REAL,
    cost_micros INTEGER,
    currency TEXT,
    UNIQUE (campaign_id, id),
    CHECK (run_status IN ('ok', 'partial', 'error')),
    CHECK (length(scope_manifest_sha256) = 64),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL OR raw_response_path IS NOT NULL
    ),
    CHECK (cost_micros IS NULL OR cost_micros >= 0)
);

CREATE TABLE current_search_runs (
    campaign_id INTEGER PRIMARY KEY REFERENCES search_campaigns(id),
    search_run_id INTEGER NOT NULL,
    selected_at TEXT NOT NULL,
    FOREIGN KEY (campaign_id, search_run_id)
        REFERENCES search_runs(campaign_id, id)
);

CREATE TABLE search_hits (
    id INTEGER PRIMARY KEY,
    search_run_id INTEGER NOT NULL REFERENCES search_runs(id),
    source_hit_id TEXT NOT NULL,
    hit_rank INTEGER,
    target_url TEXT,
    bn_file_number_literal TEXT,
    source_page_label TEXT,
    matched_text TEXT,
    raw_payload_text TEXT,
    raw_payload_path TEXT,
    raw_payload_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (search_run_id, source_hit_id),
    CHECK (length(raw_payload_sha256) = 64),
    CHECK (
        raw_payload_text IS NOT NULL OR raw_payload_path IS NOT NULL
    )
);

CREATE TABLE search_hit_resolutions (
    id INTEGER PRIMARY KEY,
    search_hit_id INTEGER NOT NULL REFERENCES search_hits(id),
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    resolution_status TEXT NOT NULL,
    object_id INTEGER REFERENCES digital_objects(id),
    edition_day_id INTEGER REFERENCES edition_days(id),
    page_id INTEGER REFERENCES physical_pages(id),
    explanation TEXT NOT NULL,
    resolved_at TEXT NOT NULL,
    UNIQUE (search_hit_id, id),
    CHECK (resolution_status IN (
        'matched', 'unresolved', 'ambiguous', 'invalid_hit'
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
    search_hit_id INTEGER PRIMARY KEY REFERENCES search_hits(id),
    resolution_id INTEGER NOT NULL,
    selected_at TEXT NOT NULL,
    FOREIGN KEY (search_hit_id, resolution_id)
        REFERENCES search_hit_resolutions(search_hit_id, id)
);

CREATE TABLE identification_runs (
    id INTEGER PRIMARY KEY,
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    run_status TEXT NOT NULL,
    scope_manifest_sha256 TEXT NOT NULL,
    raw_response_path TEXT,
    raw_response_sha256 TEXT,
    pages_submitted INTEGER NOT NULL,
    pages_completed INTEGER NOT NULL,
    input_bytes INTEGER,
    input_megapixels REAL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    elapsed_seconds REAL,
    cost_micros INTEGER,
    currency TEXT,
    CHECK (run_status IN ('ok', 'partial', 'error')),
    CHECK (length(scope_manifest_sha256) = 64),
    CHECK (
        raw_response_sha256 IS NULL
        OR length(raw_response_sha256) = 64
    ),
    CHECK (pages_submitted >= 0),
    CHECK (pages_completed >= 0),
    CHECK (pages_completed <= pages_submitted),
    CHECK (cost_micros IS NULL OR cost_micros >= 0)
);

CREATE TABLE page_assessments (
    id INTEGER PRIMARY KEY,
    page_id INTEGER NOT NULL REFERENCES physical_pages(id),
    identification_run_id INTEGER NOT NULL REFERENCES identification_runs(id),
    assessment_level TEXT NOT NULL,
    result TEXT NOT NULL,
    confidence REAL,
    evidence_region_json TEXT,
    rationale TEXT,
    raw_response_text TEXT,
    raw_response_path TEXT,
    raw_response_sha256 TEXT NOT NULL,
    assessed_at TEXT NOT NULL,
    UNIQUE (page_id, assessment_level, id),
    CHECK (assessment_level IN (
        'screening', 'substantive', 'adjudication'
    )),
    CHECK (result IN (
        'relevant', 'not_relevant', 'uncertain', 'error', 'not_assessed'
    )),
    CHECK (confidence IS NULL OR confidence BETWEEN 0.0 AND 1.0),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL OR raw_response_path IS NOT NULL
    )
);

CREATE TABLE current_page_assessments (
    page_id INTEGER NOT NULL REFERENCES physical_pages(id),
    assessment_level TEXT NOT NULL,
    assessment_id INTEGER NOT NULL,
    selected_at TEXT NOT NULL,
    PRIMARY KEY (page_id, assessment_level),
    FOREIGN KEY (page_id, assessment_level, assessment_id)
        REFERENCES page_assessments(page_id, assessment_level, id),
    CHECK (assessment_level IN (
        'screening', 'substantive', 'adjudication'
    ))
);

CREATE TABLE transcription_runs (
    id INTEGER PRIMARY KEY,
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    run_status TEXT NOT NULL,
    scope_manifest_sha256 TEXT NOT NULL,
    pages_submitted INTEGER NOT NULL,
    pages_completed INTEGER NOT NULL,
    input_megapixels REAL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    elapsed_seconds REAL,
    cost_micros INTEGER,
    currency TEXT,
    CHECK (run_status IN ('ok', 'partial', 'error')),
    CHECK (length(scope_manifest_sha256) = 64),
    CHECK (pages_submitted >= 0),
    CHECK (pages_completed >= 0),
    CHECK (pages_completed <= pages_submitted),
    CHECK (cost_micros IS NULL OR cost_micros >= 0)
);

CREATE TABLE transcriptions (
    id INTEGER PRIMARY KEY,
    page_id INTEGER NOT NULL REFERENCES physical_pages(id),
    transcription_run_id INTEGER NOT NULL REFERENCES transcription_runs(id),
    purpose TEXT NOT NULL,
    input_visual_sha256 TEXT NOT NULL,
    evidence_region_json TEXT,
    result_status TEXT NOT NULL,
    transcript_text TEXT,
    transcript_sha256 TEXT,
    raw_response_text TEXT,
    raw_response_path TEXT,
    raw_response_sha256 TEXT NOT NULL,
    export_path TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (page_id, purpose, id),
    CHECK (purpose IN (
        'masthead', 'candidate_content', 'full_page', 'recall_reference'
    )),
    CHECK (result_status IN ('ok', 'empty', 'error')),
    CHECK (length(input_visual_sha256) = 64),
    CHECK (
        transcript_sha256 IS NULL OR length(transcript_sha256) = 64
    ),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL OR raw_response_path IS NOT NULL
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
    page_id INTEGER NOT NULL REFERENCES physical_pages(id),
    purpose TEXT NOT NULL,
    transcription_id INTEGER NOT NULL,
    selected_at TEXT NOT NULL,
    PRIMARY KEY (page_id, purpose),
    FOREIGN KEY (page_id, purpose, transcription_id)
        REFERENCES transcriptions(page_id, purpose, id),
    CHECK (purpose IN (
        'masthead', 'candidate_content', 'full_page', 'recall_reference'
    ))
);

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
    normalized_date TEXT NOT NULL,
    status TEXT NOT NULL,
    imputation_method TEXT,
    confidence REAL,
    notes TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (edition_day_id, id),
    CHECK (length(normalized_date) = 10),
    CHECK (status IN ('observed', 'imputed')),
    CHECK (confidence IS NULL OR confidence BETWEEN 0.0 AND 1.0),
    CHECK (
        status <> 'observed'
        OR (
            evidence_page_id IS NOT NULL
            AND evidence_region_json IS NOT NULL
            AND date_literal IS NOT NULL
        )
    ),
    CHECK (
        status <> 'imputed' OR imputation_method IS NOT NULL
    )
);

CREATE TABLE date_record_sources (
    date_record_id INTEGER NOT NULL REFERENCES date_records(id),
    source_date_record_id INTEGER NOT NULL REFERENCES date_records(id),
    source_role TEXT NOT NULL,
    PRIMARY KEY (date_record_id, source_date_record_id, source_role),
    CHECK (source_role IN (
        'previous_issue', 'next_issue', 'same_object',
        'calendar_evidence', 'manual_reference'
    )),
    CHECK (date_record_id <> source_date_record_id)
);

CREATE TABLE current_edition_dates (
    edition_day_id INTEGER PRIMARY KEY REFERENCES edition_days(id),
    date_record_id INTEGER NOT NULL,
    selected_at TEXT NOT NULL,
    FOREIGN KEY (edition_day_id, date_record_id)
        REFERENCES date_records(edition_day_id, id)
);

CREATE TABLE phase_schemes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT NOT NULL,
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    created_at TEXT NOT NULL,
    UNIQUE (name, version)
);

CREATE TABLE phase_definitions (
    id INTEGER PRIMARY KEY,
    phase_scheme_id INTEGER NOT NULL REFERENCES phase_schemes(id),
    phase_code TEXT NOT NULL,
    phase_label TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    UNIQUE (phase_scheme_id, phase_code),
    CHECK (start_date <= end_date)
);

CREATE TABLE current_phase_schemes (
    context_name TEXT PRIMARY KEY,
    phase_scheme_id INTEGER NOT NULL REFERENCES phase_schemes(id),
    selected_at TEXT NOT NULL
);

CREATE TABLE recall_audits (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    target_stage TEXT NOT NULL,
    population_definition_id INTEGER NOT NULL
        REFERENCES population_definitions(id),
    evaluated_protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    reference_protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    confidence_level REAL NOT NULL,
    minimum_recall_lcb REAL NOT NULL,
    sampling_method TEXT NOT NULL,
    created_at TEXT NOT NULL,
    CHECK (target_stage IN (
        'search', 'screening', 'substantive_identification'
    )),
    CHECK (confidence_level > 0.0 AND confidence_level < 1.0),
    CHECK (minimum_recall_lcb > 0.0 AND minimum_recall_lcb <= 1.0),
    CHECK (sampling_method IN (
        'stratified_srswor', 'two_phase_stratified_srswor'
    ))
);

CREATE TABLE recall_strata (
    id INTEGER PRIMARY KEY,
    recall_audit_id INTEGER NOT NULL REFERENCES recall_audits(id),
    newspaper_id INTEGER NOT NULL REFERENCES newspapers(id),
    phase_definition_id INTEGER NOT NULL REFERENCES phase_definitions(id),
    retrieval_stratum TEXT NOT NULL,
    frame_size INTEGER NOT NULL,
    planned_sample_size INTEGER NOT NULL,
    random_seed INTEGER NOT NULL,
    selection_code_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (
        recall_audit_id, newspaper_id,
        phase_definition_id, retrieval_stratum
    ),
    CHECK (retrieval_stratum IN ('recovered', 'not_recovered')),
    CHECK (frame_size >= 0),
    CHECK (planned_sample_size >= 0),
    CHECK (planned_sample_size <= frame_size),
    CHECK (length(selection_code_sha256) = 64)
);

CREATE TABLE recall_sample_units (
    id INTEGER PRIMARY KEY,
    recall_stratum_id INTEGER NOT NULL REFERENCES recall_strata(id),
    edition_day_id INTEGER NOT NULL REFERENCES edition_days(id),
    draw_order INTEGER NOT NULL,
    random_value REAL NOT NULL,
    inclusion_probability REAL NOT NULL,
    selected_at TEXT NOT NULL,
    UNIQUE (recall_stratum_id, edition_day_id),
    UNIQUE (recall_stratum_id, draw_order),
    CHECK (draw_order >= 1),
    CHECK (
        inclusion_probability > 0.0
        AND inclusion_probability <= 1.0
    )
);

CREATE TABLE recall_reference_labels (
    id INTEGER PRIMARY KEY,
    sample_unit_id INTEGER NOT NULL REFERENCES recall_sample_units(id),
    page_id INTEGER REFERENCES physical_pages(id),
    reference_result TEXT NOT NULL,
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    reviewer_id TEXT NOT NULL,
    evidence_text TEXT,
    evidence_region_json TEXT,
    raw_response_text TEXT,
    raw_response_path TEXT,
    raw_response_sha256 TEXT NOT NULL,
    adjudication_status TEXT NOT NULL,
    assessed_at TEXT NOT NULL,
    CHECK (reference_result IN (
        'relevant', 'not_relevant', 'uncertain', 'error'
    )),
    CHECK (adjudication_status IN (
        'single_review', 'double_agreement', 'adjudicated'
    )),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL OR raw_response_path IS NOT NULL
    )
);

CREATE TABLE recall_gate_results (
    id INTEGER PRIMARY KEY,
    recall_audit_id INTEGER NOT NULL REFERENCES recall_audits(id),
    newspaper_id INTEGER NOT NULL REFERENCES newspapers(id),
    phase_definition_id INTEGER NOT NULL REFERENCES phase_definitions(id),
    computed_at TEXT NOT NULL,
    estimator TEXT NOT NULL,
    interval_method TEXT NOT NULL,
    sampled_units INTEGER NOT NULL,
    reference_relevant_units INTEGER NOT NULL,
    recovered_relevant_units INTEGER NOT NULL,
    estimated_recall REAL NOT NULL,
    lower_confidence_bound REAL NOT NULL,
    upper_confidence_bound REAL NOT NULL,
    effective_sample_size REAL NOT NULL,
    computation_code_sha256 TEXT NOT NULL,
    result TEXT NOT NULL,
    CHECK (estimator IN ('horvitz_thompson', 'hajek')),
    CHECK (interval_method IN (
        'rao_wu_bootstrap', 'exact_hypergeometric'
    )),
    CHECK (estimated_recall BETWEEN 0.0 AND 1.0),
    CHECK (lower_confidence_bound BETWEEN 0.0 AND 1.0),
    CHECK (upper_confidence_bound BETWEEN 0.0 AND 1.0),
    CHECK (lower_confidence_bound <= estimated_recall),
    CHECK (estimated_recall <= upper_confidence_bound),
    CHECK (sampled_units >= 0),
    CHECK (reference_relevant_units >= 0),
    CHECK (recovered_relevant_units >= 0),
    CHECK (length(computation_code_sha256) = 64),
    CHECK (result IN ('pass', 'fail', 'insufficient_sample'))
);

CREATE TABLE classification_runs (
    id INTEGER PRIMARY KEY,
    classification_family TEXT NOT NULL,
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    run_status TEXT NOT NULL,
    scope_manifest_sha256 TEXT NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_micros INTEGER,
    currency TEXT,
    CHECK (run_status IN ('ok', 'partial', 'error')),
    CHECK (length(scope_manifest_sha256) = 64),
    CHECK (cost_micros IS NULL OR cost_micros >= 0)
);

CREATE TABLE edition_classifications (
    id INTEGER PRIMARY KEY,
    edition_day_id INTEGER NOT NULL REFERENCES edition_days(id),
    classification_run_id INTEGER NOT NULL REFERENCES classification_runs(id),
    classification_family TEXT NOT NULL,
    result_status TEXT NOT NULL,
    output_json TEXT,
    raw_response_text TEXT,
    raw_response_path TEXT,
    raw_response_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (edition_day_id, classification_family, id),
    CHECK (result_status IN ('ok', 'abstained', 'error')),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL OR raw_response_path IS NOT NULL
    ),
    CHECK (result_status <> 'ok' OR output_json IS NOT NULL)
);

CREATE TABLE classification_inputs (
    classification_id INTEGER NOT NULL
        REFERENCES edition_classifications(id),
    transcription_id INTEGER NOT NULL REFERENCES transcriptions(id),
    PRIMARY KEY (classification_id, transcription_id)
);

CREATE TABLE current_edition_classifications (
    edition_day_id INTEGER NOT NULL REFERENCES edition_days(id),
    classification_family TEXT NOT NULL,
    classification_id INTEGER NOT NULL,
    selected_at TEXT NOT NULL,
    PRIMARY KEY (edition_day_id, classification_family),
    FOREIGN KEY (
        edition_day_id, classification_family, classification_id
    ) REFERENCES edition_classifications(
        edition_day_id, classification_family, id
    )
);

CREATE TABLE audit_cases (
    id INTEGER PRIMARY KEY,
    case_type TEXT NOT NULL,
    legacy_identifier TEXT NOT NULL,
    edition_day_id INTEGER REFERENCES edition_days(id),
    search_hit_id INTEGER REFERENCES search_hits(id),
    page_id INTEGER REFERENCES physical_pages(id),
    imported_at TEXT NOT NULL,
    UNIQUE (case_type, legacy_identifier),
    CHECK (case_type IN (
        'p0_no_relevant_mention_1906', 'p0_missing_date_1906'
    ))
);

CREATE TABLE audit_findings (
    id INTEGER PRIMARY KEY,
    audit_case_id INTEGER NOT NULL REFERENCES audit_cases(id),
    protocol_id INTEGER NOT NULL REFERENCES protocols(id),
    finding TEXT NOT NULL,
    explanation TEXT NOT NULL,
    raw_response_text TEXT,
    raw_response_path TEXT,
    raw_response_sha256 TEXT NOT NULL,
    assessed_at TEXT NOT NULL,
    UNIQUE (audit_case_id, id),
    CHECK (finding IN (
        'substantively_not_relevant', 'wrong_page', 'wrong_object',
        'transcription_omission', 'transcription_truncation',
        'reading_failure', 'classification_failure',
        'unresolved_search_hit', 'date_parser_failure',
        'masthead_unreadable', 'other', 'pending'
    )),
    CHECK (length(raw_response_sha256) = 64),
    CHECK (
        raw_response_text IS NOT NULL OR raw_response_path IS NOT NULL
    )
);

CREATE TABLE current_audit_findings (
    audit_case_id INTEGER PRIMARY KEY REFERENCES audit_cases(id),
    audit_finding_id INTEGER NOT NULL,
    selected_at TEXT NOT NULL,
    FOREIGN KEY (audit_case_id, audit_finding_id)
        REFERENCES audit_findings(audit_case_id, id)
);

CREATE UNIQUE INDEX ux_population_membership_without_edition
    ON population_memberships(population_definition_id, calendar_day_id)
    WHERE edition_day_id IS NULL;

CREATE UNIQUE INDEX ux_population_membership_with_edition
    ON population_memberships(
        population_definition_id, calendar_day_id, edition_day_id
    )
    WHERE edition_day_id IS NOT NULL;

CREATE INDEX ix_calendar_days_date
    ON calendar_days(civil_date);
CREATE INDEX ix_circulation_protocol
    ON circulation_assessments(protocol_id);
CREATE INDEX ix_digital_objects_newspaper_year
    ON digital_objects(newspaper_id, source_year);
CREATE INDEX ix_digital_objects_protocol
    ON digital_objects(discovered_by_protocol_id);
CREATE INDEX ix_object_fetches_object_result
    ON object_fetches(object_id, result);
CREATE INDEX ix_edition_days_newspaper
    ON edition_days(newspaper_id);
CREATE INDEX ix_edition_identifiers_edition
    ON edition_identifiers(edition_day_id);
CREATE INDEX ix_edition_identifiers_page
    ON edition_identifiers(evidence_page_id);
CREATE INDEX ix_edition_identifiers_protocol
    ON edition_identifiers(protocol_id);
CREATE INDEX ix_edition_object_links_object
    ON edition_object_links(object_id);
CREATE INDEX ix_edition_object_links_protocol
    ON edition_object_links(protocol_id);
CREATE INDEX ix_physical_pages_object
    ON physical_pages(object_id);
CREATE INDEX ix_population_memberships_calendar
    ON population_memberships(calendar_day_id);
CREATE INDEX ix_population_memberships_edition
    ON population_memberships(edition_day_id);
CREATE INDEX ix_search_campaigns_newspaper
    ON search_campaigns(newspaper_id);
CREATE INDEX ix_search_runs_protocol
    ON search_runs(protocol_id);
CREATE INDEX ix_search_hits_run
    ON search_hits(search_run_id);
CREATE INDEX ix_search_resolutions_hit
    ON search_hit_resolutions(search_hit_id);
CREATE INDEX ix_search_resolutions_object
    ON search_hit_resolutions(object_id);
CREATE INDEX ix_search_resolutions_edition
    ON search_hit_resolutions(edition_day_id);
CREATE INDEX ix_search_resolutions_page
    ON search_hit_resolutions(page_id);
CREATE INDEX ix_page_assessments_page_level
    ON page_assessments(page_id, assessment_level);
CREATE INDEX ix_page_assessments_run
    ON page_assessments(identification_run_id);
CREATE INDEX ix_transcription_runs_protocol
    ON transcription_runs(protocol_id);
CREATE INDEX ix_transcriptions_page_purpose
    ON transcriptions(page_id, purpose);
CREATE INDEX ix_transcriptions_run
    ON transcriptions(transcription_run_id);
CREATE INDEX ix_date_records_edition
    ON date_records(edition_day_id);
CREATE INDEX ix_date_records_protocol
    ON date_records(protocol_id);
CREATE INDEX ix_date_records_page
    ON date_records(evidence_page_id);
CREATE INDEX ix_date_records_transcription
    ON date_records(evidence_transcription_id);
CREATE INDEX ix_date_record_sources_source
    ON date_record_sources(source_date_record_id);
CREATE INDEX ix_phase_definitions_dates
    ON phase_definitions(phase_scheme_id, start_date, end_date);
CREATE INDEX ix_recall_audits_protocols
    ON recall_audits(evaluated_protocol_id, reference_protocol_id);
CREATE INDEX ix_recall_strata_audit
    ON recall_strata(recall_audit_id);
CREATE INDEX ix_recall_strata_newspaper
    ON recall_strata(newspaper_id);
CREATE INDEX ix_recall_strata_phase
    ON recall_strata(phase_definition_id);
CREATE INDEX ix_recall_sample_units_edition
    ON recall_sample_units(edition_day_id);
CREATE INDEX ix_recall_reference_sample
    ON recall_reference_labels(sample_unit_id);
CREATE INDEX ix_recall_reference_page
    ON recall_reference_labels(page_id);
CREATE INDEX ix_recall_gate_audit
    ON recall_gate_results(recall_audit_id);
CREATE INDEX ix_classification_runs_protocol
    ON classification_runs(protocol_id);
CREATE INDEX ix_edition_classifications_edition
    ON edition_classifications(edition_day_id, classification_family);
CREATE INDEX ix_edition_classifications_run
    ON edition_classifications(classification_run_id);
CREATE INDEX ix_classification_inputs_transcription
    ON classification_inputs(transcription_id);
CREATE INDEX ix_audit_cases_edition
    ON audit_cases(edition_day_id);
CREATE INDEX ix_audit_cases_hit
    ON audit_cases(search_hit_id);
CREATE INDEX ix_audit_cases_page
    ON audit_cases(page_id);
CREATE INDEX ix_audit_findings_case
    ON audit_findings(audit_case_id);
CREATE INDEX ix_audit_findings_protocol
    ON audit_findings(protocol_id);

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
JOIN current_page_assessments AS c ON c.page_id = p.id
JOIN page_assessments AS a ON a.id = c.assessment_id;

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

PRAGMA user_version = 1;
