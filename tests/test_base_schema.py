from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "pipeline" / "base" / "schema.sql"
MIGRATION_PATH = (
    REPO_ROOT / "pipeline" / "base" / "migrations" / "001_init.sql"
)

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

    def test_migracao_e_autocontida_e_equivale_ao_schema(self) -> None:
        schema_conn = apply_sql(SCHEMA_PATH)
        migration_conn = apply_sql(MIGRATION_PATH)
        self.addCleanup(schema_conn.close)
        self.addCleanup(migration_conn.close)

        self.assertEqual(0, schema_conn.execute("PRAGMA user_version").fetchone()[0])
        self.assertEqual(
            1, migration_conn.execute("PRAGMA user_version").fetchone()[0]
        )
        self.assertEqual(
            database_objects(schema_conn), database_objects(migration_conn)
        )


if __name__ == "__main__":
    unittest.main()
