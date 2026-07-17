"""Acesso SQLite e migrações da base operacional do corpus."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator, Literal, Sequence

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE = ROOT / "dados" / "base" / "caixa_conversao.db"
DEFAULT_MIGRATIONS = Path(__file__).resolve().parent / "migrations"

FetchResult = Literal[
    "ok",
    "http_error",
    "network_error",
    "invalid_pdf",
    "storage_error",
]
CirculationResult = Literal[
    "circulated",
    "did_not_circulate",
    "unknown",
    "error",
]
Eligibility = Literal["eligible", "ineligible", "unknown"]


@dataclass(frozen=True, slots=True)
class DigitalObject:
    id: int
    newspaper_id: int
    source_identifier: str
    source_url: str
    source_year: int
    bn_file_key: str
    bn_file_number_literal: str
    discovered_by_protocol_id: int
    discovered_at: str


@dataclass(frozen=True, slots=True)
class InventoryItem:
    object_id: int
    newspaper: str
    bib: str
    source_identifier: str
    source_url: str
    source_year: int
    bn_file_key: str
    bn_file_number_literal: str
    fetch_result: str | None
    http_status: int | None
    obtained_at: str | None
    storage_path: str | None
    pdf_sha256: str | None
    byte_count: int | None
    page_count: int | None


@dataclass(frozen=True, slots=True)
class CalendarDay:
    id: int
    newspaper_id: int
    civil_date: str
    created_at: str


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def connect(
    database: str | Path = DEFAULT_DATABASE,
    *,
    migrate: bool = True,
    migrations_dir: str | Path = DEFAULT_MIGRATIONS,
) -> sqlite3.Connection:
    path = Path(database)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    if conn.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        conn.close()
        raise RuntimeError("Não foi possível ativar PRAGMA foreign_keys")
    if migrate:
        apply_migrations(conn, migrations_dir)
    return conn


def apply_migrations(
    conn: sqlite3.Connection,
    migrations_dir: str | Path = DEFAULT_MIGRATIONS,
) -> int:
    directory = Path(migrations_dir)
    files: dict[int, Path] = {}

    for path in sorted(directory.glob("*.sql")):
        match = re.fullmatch(r"(\d+)_.*\.sql", path.name)
        if not match:
            continue
        version = int(match.group(1))
        if version in files:
            raise RuntimeError(f"Migração duplicada para a versão {version}")
        files[version] = path

    current = int(conn.execute("PRAGMA user_version").fetchone()[0])
    for version in sorted(v for v in files if v > current):
        if version != current + 1:
            raise RuntimeError(
                f"Lacuna nas migrações: banco={current}, próxima={version}"
            )

        script = files[version].read_text(encoding="utf-8")
        transaction_script = (
            "BEGIN IMMEDIATE;\n"
            f"{script}\n"
            f"PRAGMA user_version = {version};\n"
            "COMMIT;\n"
        )
        try:
            conn.executescript(transaction_script)
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise

        applied = int(conn.execute("PRAGMA user_version").fetchone()[0])
        if applied != version:
            raise RuntimeError(
                f"Migração {version} não atualizou user_version"
            )
        current = version

    return current


def migrate(
    conn: sqlite3.Connection,
    migrations_dir: str | Path = DEFAULT_MIGRATIONS,
) -> int:
    """Aplica migrações pendentes e devolve a versão vigente."""
    return apply_migrations(conn, migrations_dir)


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


def upsert_newspaper(
    conn: sqlite3.Connection,
    *,
    slug: str,
    title: str,
    bn_bib: str,
    city: str,
    active_from: str | None = None,
    active_to: str | None = None,
    created_at: str | None = None,
) -> int:
    timestamp = created_at or utc_now()
    conn.execute(
        """
        INSERT INTO newspapers(
            slug, title, bn_bib, city, active_from, active_to, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            title = excluded.title,
            bn_bib = excluded.bn_bib,
            city = excluded.city,
            active_from = excluded.active_from,
            active_to = excluded.active_to
        """,
        (
            slug,
            title,
            bn_bib,
            city,
            active_from,
            active_to,
            timestamp,
        ),
    )
    row = conn.execute(
        "SELECT id FROM newspapers WHERE slug = ?", (slug,)
    ).fetchone()
    assert row is not None
    return int(row["id"])


def upsert_protocol(
    conn: sqlite3.Connection,
    *,
    stage: str,
    name: str,
    version: str,
    executor_type: str,
    code_commit: str,
    parameters: dict[str, object],
    model_provider: str | None = None,
    model_name: str | None = None,
    model_version: str | None = None,
    prompt_version: str | None = None,
    prompt_sha256: str | None = None,
    prompt_path: str | None = None,
    created_at: str | None = None,
) -> int:
    parameters_json = json.dumps(
        parameters, ensure_ascii=False, sort_keys=True
    )
    conn.execute(
        """
        INSERT INTO protocols(
            stage, name, version, executor_type, code_commit,
            model_provider, model_name, model_version, prompt_version,
            prompt_sha256, prompt_path, parameters_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(stage, name, version) DO NOTHING
        """,
        (
            stage,
            name,
            version,
            executor_type,
            code_commit,
            model_provider,
            model_name,
            model_version,
            prompt_version,
            prompt_sha256,
            prompt_path,
            parameters_json,
            created_at or utc_now(),
        ),
    )
    row = conn.execute(
        """
        SELECT id, executor_type, model_provider, model_name,
               model_version, prompt_version, prompt_sha256, prompt_path,
               parameters_json
        FROM protocols
        WHERE stage = ? AND name = ? AND version = ?
        """,
        (stage, name, version),
    ).fetchone()
    assert row is not None
    # code_commit fica fora da identidade: registra a primeira
    # materialização e não muda em reexecuções sob commits novos.
    expected = {
        "executor_type": executor_type,
        "model_provider": model_provider,
        "model_name": model_name,
        "model_version": model_version,
        "prompt_version": prompt_version,
        "prompt_sha256": prompt_sha256,
        "prompt_path": prompt_path,
        "parameters_json": parameters_json,
    }
    actual = {key: row[key] for key in expected}
    if actual != expected:
        raise ValueError(
            f"conflito de protocolo em {stage}/{name}/{version}: "
            "a chave existente possui outra identidade"
        )
    return int(row["id"])


def upsert_digital_object(
    conn: sqlite3.Connection,
    *,
    newspaper_id: int,
    source_identifier: str,
    source_url: str,
    source_year: int,
    bn_file_key: str,
    bn_file_number_literal: str,
    discovered_by_protocol_id: int,
    discovered_at: str | None = None,
) -> int:
    conn.execute(
        """
        INSERT INTO digital_objects(
            newspaper_id, source_identifier, source_url, source_year,
            bn_file_key, bn_file_number_literal,
            discovered_by_protocol_id, discovered_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_identifier) DO UPDATE SET
            newspaper_id = excluded.newspaper_id,
            source_url = excluded.source_url,
            source_year = excluded.source_year,
            bn_file_key = excluded.bn_file_key,
            bn_file_number_literal = excluded.bn_file_number_literal
        """,
        (
            newspaper_id,
            source_identifier,
            source_url,
            source_year,
            bn_file_key,
            bn_file_number_literal,
            discovered_by_protocol_id,
            discovered_at or utc_now(),
        ),
    )
    row = conn.execute(
        "SELECT id FROM digital_objects WHERE source_identifier = ?",
        (source_identifier,),
    ).fetchone()
    assert row is not None
    return int(row["id"])


def get_digital_object(
    conn: sqlite3.Connection,
    source_identifier: str,
) -> DigitalObject | None:
    row = conn.execute(
        "SELECT * FROM digital_objects WHERE source_identifier = ?",
        (source_identifier,),
    ).fetchone()
    return DigitalObject(**dict(row)) if row else None


def list_digital_objects(
    conn: sqlite3.Connection,
    *,
    newspaper_id: int | None = None,
    source_year: int | None = None,
) -> list[DigitalObject]:
    clauses: list[str] = []
    values: list[object] = []
    if newspaper_id is not None:
        clauses.append("newspaper_id = ?")
        values.append(newspaper_id)
    if source_year is not None:
        clauses.append("source_year = ?")
        values.append(source_year)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = conn.execute(
        f"SELECT * FROM digital_objects{where} ORDER BY source_identifier",
        values,
    ).fetchall()
    return [DigitalObject(**dict(row)) for row in rows]


def mark_download_status(
    conn: sqlite3.Connection,
    *,
    object_id: int,
    result: FetchResult,
    attempted_at: str,
    completed_at: str | None = None,
    http_status: int | None = None,
    storage_path: str | None = None,
    pdf_sha256: str | None = None,
    response_sha256: str | None = None,
    byte_count: int | None = None,
    page_count: int | None = None,
    error_class: str | None = None,
    error_message: str | None = None,
    make_current: bool = True,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO object_fetches(
            object_id, attempted_at, completed_at, result, http_status,
            storage_path, pdf_sha256, response_sha256, byte_count,
            page_count, error_class, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            object_id,
            attempted_at,
            completed_at,
            result,
            http_status,
            storage_path,
            pdf_sha256,
            response_sha256,
            byte_count,
            page_count,
            error_class,
            error_message,
        ),
    )
    fetch_id = int(cursor.lastrowid)
    if make_current:
        conn.execute(
            """
            INSERT INTO current_object_fetches(object_id, fetch_id, selected_at)
            VALUES (?, ?, ?)
            ON CONFLICT(object_id) DO UPDATE SET
                fetch_id = excluded.fetch_id,
                selected_at = excluded.selected_at
            """,
            (object_id, fetch_id, utc_now()),
        )
    return fetch_id


def get_current_fetch(
    conn: sqlite3.Connection,
    object_id: int,
) -> sqlite3.Row | None:
    """Retorna a obtenção vigente de um objeto, quando selecionada."""
    return conn.execute(
        """
        SELECT f.*
        FROM current_object_fetches AS current
        JOIN object_fetches AS f ON f.id = current.fetch_id
        WHERE current.object_id = ?
        """,
        (object_id,),
    ).fetchone()


def list_inventory(
    conn: sqlite3.Connection,
    *,
    newspaper: str | None = None,
    source_year: int | None = None,
) -> list[InventoryItem]:
    clauses: list[str] = []
    values: list[object] = []
    if newspaper is not None:
        clauses.append("newspaper = ?")
        values.append(newspaper)
    if source_year is not None:
        clauses.append("source_year = ?")
        values.append(source_year)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = conn.execute(
        f"""
        SELECT * FROM v_digital_object_inventory
        {where}
        ORDER BY newspaper, source_year, source_identifier
        """,
        values,
    ).fetchall()
    return [InventoryItem(**dict(row)) for row in rows]


def upsert_calendar_day(
    conn: sqlite3.Connection,
    *,
    newspaper_id: int,
    civil_date: str,
    created_at: str | None = None,
) -> int:
    conn.execute(
        """
        INSERT INTO calendar_days(newspaper_id, civil_date, created_at)
        VALUES (?, ?, ?)
        ON CONFLICT(newspaper_id, civil_date) DO NOTHING
        """,
        (newspaper_id, civil_date, created_at or utc_now()),
    )
    row = conn.execute(
        """
        SELECT id FROM calendar_days
        WHERE newspaper_id = ? AND civil_date = ?
        """,
        (newspaper_id, civil_date),
    ).fetchone()
    assert row is not None
    return int(row["id"])


def list_calendar_days(
    conn: sqlite3.Connection,
    newspaper_id: int,
) -> list[CalendarDay]:
    rows = conn.execute(
        """
        SELECT * FROM calendar_days
        WHERE newspaper_id = ?
        ORDER BY civil_date
        """,
        (newspaper_id,),
    ).fetchall()
    return [CalendarDay(**dict(row)) for row in rows]


def add_circulation_assessment(
    conn: sqlite3.Connection,
    *,
    calendar_day_id: int,
    protocol_id: int,
    result: CirculationResult,
    evidence_text: str | None = None,
    evidence_path: str | None = None,
    evidence_sha256: str | None = None,
    assessed_at: str | None = None,
    make_current: bool = True,
) -> int:
    timestamp = assessed_at or utc_now()
    cursor = conn.execute(
        """
        INSERT INTO circulation_assessments(
            calendar_day_id, protocol_id, result, evidence_text,
            evidence_path, evidence_sha256, assessed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            calendar_day_id,
            protocol_id,
            result,
            evidence_text,
            evidence_path,
            evidence_sha256,
            timestamp,
        ),
    )
    assessment_id = int(cursor.lastrowid)
    if make_current:
        conn.execute(
            """
            INSERT INTO current_circulation_assessments(
                calendar_day_id, assessment_id, selected_at
            ) VALUES (?, ?, ?)
            ON CONFLICT(calendar_day_id) DO UPDATE SET
                assessment_id = excluded.assessment_id,
                selected_at = excluded.selected_at
            """,
            (calendar_day_id, assessment_id, timestamp),
        )
    return assessment_id


def upsert_population_definition(
    conn: sqlite3.Connection,
    *,
    name: str,
    version: str,
    unit_mode: Literal[
        "strict_newspaper_day", "multiple_editions_per_day"
    ],
    description: str,
    protocol_id: int,
    created_at: str | None = None,
) -> int:
    conn.execute(
        """
        INSERT INTO population_definitions(
            name, version, unit_mode, description, protocol_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(name, version) DO NOTHING
        """,
        (
            name,
            version,
            unit_mode,
            description,
            protocol_id,
            created_at or utc_now(),
        ),
    )
    row = conn.execute(
        """
        SELECT id FROM population_definitions
        WHERE name = ? AND version = ?
        """,
        (name, version),
    ).fetchone()
    assert row is not None
    return int(row["id"])


def upsert_population_membership(
    conn: sqlite3.Connection,
    *,
    population_definition_id: int,
    calendar_day_id: int,
    edition_day_id: int | None,
    eligibility: Eligibility,
    reason: str,
    assigned_at: str | None = None,
) -> int:
    row = conn.execute(
        """
        SELECT id, eligibility, reason FROM population_memberships
        WHERE population_definition_id = ?
          AND calendar_day_id = ?
          AND edition_day_id IS ?
        """,
        (
            population_definition_id,
            calendar_day_id,
            edition_day_id,
        ),
    ).fetchone()

    timestamp = assigned_at or utc_now()
    if row:
        membership_id = int(row["id"])
        if row["eligibility"] != eligibility or row["reason"] != reason:
            raise ValueError(
                "conflito de filiação: altere a versão da definição "
                "de população antes de mudar elegibilidade ou motivo"
            )
        return membership_id

    cursor = conn.execute(
        """
        INSERT INTO population_memberships(
            population_definition_id, calendar_day_id, edition_day_id,
            eligibility, reason, assigned_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            population_definition_id,
            calendar_day_id,
            edition_day_id,
            eligibility,
            reason,
            timestamp,
        ),
    )
    return int(cursor.lastrowid)


def rows(
    conn: sqlite3.Connection,
    sql: str,
    parameters: Sequence[object] = (),
) -> list[sqlite3.Row]:
    return list(conn.execute(sql, parameters).fetchall())
