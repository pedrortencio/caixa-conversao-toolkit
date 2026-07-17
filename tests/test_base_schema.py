from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

from pipeline.base import db


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "pipeline" / "base" / "schema.sql"
MIGRATIONS_DIR = REPO_ROOT / "pipeline" / "base" / "migrations"

EXPECTED_TABLES = {
    "audit_cases",
    "audit_findings",
    "calendar_days",
    "circulation_assessments",
    "classification_inputs",
    "classification_runs",
    "current_audit_findings",
    "current_circulation_assessments",
    "current_edition_classifications",
    "current_edition_dates",
    "current_object_fetches",
    "current_page_assessments",
    "current_phase_schemes",
    "current_search_hit_resolutions",
    "current_search_runs",
    "current_transcriptions",
    "date_record_sources",
    "date_records",
    "digital_objects",
    "edition_classifications",
    "edition_days",
    "edition_identifiers",
    "edition_object_links",
    "identification_runs",
    "newspapers",
    "object_fetches",
    "page_assessments",
    "phase_definitions",
    "phase_schemes",
    "physical_pages",
    "population_definitions",
    "population_memberships",
    "protocols",
    "recall_audits",
    "recall_gate_results",
    "recall_reference_labels",
    "recall_sample_units",
    "recall_strata",
    "search_campaigns",
    "search_hit_resolutions",
    "search_hits",
    "search_runs",
    "transcription_runs",
    "transcriptions",
}

EXPECTED_VIEWS = {
    "v_current_edition_dates",
    "v_current_edition_phases",
    "v_current_page_assessments",
    "v_digital_object_inventory",
}


def apply_sql(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(path.read_text(encoding="utf-8"))
    return conn


def database_objects(conn: sqlite3.Connection) -> dict[tuple[str, str], str]:
    return {
        (object_type, name): sql
        for object_type, name, sql in conn.execute(
            """
            SELECT type, name, sql
            FROM sqlite_master
            WHERE type IN ('table', 'view', 'index')
              AND name NOT LIKE 'sqlite_%'
            ORDER BY type, name
            """
        )
    }


class SchemaTests(unittest.TestCase):
    def test_schema_cria_contrato_completo_e_integro(self) -> None:
        conn = apply_sql(SCHEMA_PATH)
        self.addCleanup(conn.close)

        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        views = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='view'"
            )
        }

        self.assertEqual(EXPECTED_TABLES, tables)
        self.assertEqual(EXPECTED_VIEWS, views)
        self.assertEqual(1, conn.execute("PRAGMA foreign_keys").fetchone()[0])
        self.assertEqual(
            "ok", conn.execute("PRAGMA integrity_check").fetchone()[0]
        )
        self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())

    def test_checks_rejeitam_enum_invalido(self) -> None:
        conn = apply_sql(SCHEMA_PATH)
        self.addCleanup(conn.close)

        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO protocols(
                    stage, name, version, executor_type, code_commit,
                    parameters_json, created_at
                ) VALUES ('etapa_invalida', 'teste', '1', 'deterministic',
                          'abc', '{}', '2026-07-16T00:00:00Z')
                """
            )

    def seed_object_and_edition(self, conn: sqlite3.Connection) -> tuple[int, int, int]:
        conn.execute(
            """
            INSERT INTO newspapers(id, slug, title, bn_bib, city, created_at)
            VALUES (1, 'o_paiz', 'O Paiz', '178691', 'Rio de Janeiro',
                    '2026-07-17T00:00:00Z')
            """
        )
        conn.execute(
            """
            INSERT INTO protocols(
                id, stage, name, version, executor_type, code_commit,
                parameters_json, created_at
            ) VALUES (1, 'inventory', 'teste', '1', 'deterministic', 'abc',
                      '{}', '2026-07-17T00:00:00Z')
            """
        )
        conn.execute(
            """
            INSERT INTO digital_objects(
                id, newspaper_id, source_identifier, source_url,
                source_year, bn_file_key, bn_file_number_literal,
                discovered_by_protocol_id, discovered_at
            ) VALUES (1, 1, 'per178691_1906_00001',
                      'https://example.test/per178691_1906_00001.pdf', 1906,
                      '178691/per178691_1906_00001.pdf', '00001', 1,
                      '2026-07-17T00:00:00Z')
            """
        )
        conn.execute(
            """
            INSERT INTO edition_days(
                id, newspaper_id, logical_key, edition_kind,
                identity_status, created_at
            ) VALUES (1, 1, 'per178691_1906_00001', 'regular',
                      'provisional', '2026-07-17T00:00:00Z')
            """
        )
        return 1, 1, 1

    def test_checks_rejeitam_fetch_mode_invalido(self) -> None:
        conn = apply_sql(SCHEMA_PATH)
        self.addCleanup(conn.close)
        self.seed_object_and_edition(conn)

        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO object_fetches(
                    object_id, fetch_mode, attempted_at, result
                ) VALUES (1, 'ftp', '2026-07-17T00:00:00Z', 'network_error')
                """
            )

    def test_checks_rejeitam_response_sha256_em_importacao_local(self) -> None:
        conn = apply_sql(SCHEMA_PATH)
        self.addCleanup(conn.close)
        self.seed_object_and_edition(conn)

        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO object_fetches(
                    object_id, fetch_mode, attempted_at, result,
                    response_sha256
                ) VALUES (
                    1, 'local_import', '2026-07-17T00:00:00Z',
                    'network_error', ?
                )
                """,
                ("a" * 64,),
            )

    def test_checks_aceitam_status_unresolved_sem_data(self) -> None:
        conn = apply_sql(SCHEMA_PATH)
        self.addCleanup(conn.close)
        _, protocol_id, _ = self.seed_object_and_edition(conn)
        conn.execute(
            """
            INSERT INTO physical_pages(
                object_id, page_number, created_at
            ) VALUES (1, 1, '2026-07-17T00:00:00Z')
            """
        )
        page_id = conn.execute(
            "SELECT id FROM physical_pages WHERE object_id = 1"
        ).fetchone()[0]

        conn.execute(
            """
            INSERT INTO date_records(
                edition_day_id, protocol_id, evidence_page_id,
                parser_name, parser_version, status, notes, created_at
            ) VALUES (
                1, ?, ?, 'masthead_visual_manifest', '1.0.0', 'unresolved',
                'masthead ilegível', '2026-07-17T00:00:00Z'
            )
            """,
            (protocol_id, page_id),
        )
        row = conn.execute(
            "SELECT normalized_date, status FROM date_records"
        ).fetchone()
        self.assertIsNone(row[0])
        self.assertEqual("unresolved", row[1])

        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO date_records(
                    edition_day_id, protocol_id, evidence_page_id,
                    normalized_date, parser_name, parser_version, status,
                    created_at
                ) VALUES (
                    1, ?, ?, '1906-01-13', 'masthead_visual_manifest',
                    '1.0.0', 'unresolved', '2026-07-17T00:00:00Z'
                )
                """,
                (protocol_id, page_id),
            )

    def test_migracao_e_autocontida_e_equivale_ao_schema(self) -> None:
        schema_conn = apply_sql(SCHEMA_PATH)
        migration_conn = sqlite3.connect(":memory:")
        migration_conn.execute("PRAGMA foreign_keys = ON")
        self.addCleanup(schema_conn.close)
        self.addCleanup(migration_conn.close)

        latest_version = db.apply_migrations(migration_conn, MIGRATIONS_DIR)

        self.assertEqual(0, schema_conn.execute("PRAGMA user_version").fetchone()[0])
        self.assertGreaterEqual(latest_version, 1)
        self.assertEqual(
            latest_version,
            migration_conn.execute("PRAGMA user_version").fetchone()[0],
        )
        self.assertEqual(
            database_objects(schema_conn), database_objects(migration_conn)
        )


if __name__ == "__main__":
    unittest.main()
