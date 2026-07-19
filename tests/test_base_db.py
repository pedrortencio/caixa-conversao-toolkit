from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from pipeline.base import db


HASH_A = "a" * 64
HASH_B = "b" * 64
NOW = "2026-07-16T22:30:00+00:00"


class DatabaseAccessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.db_path = Path(self.temporary.name) / "base" / "test.db"
        self.conn = db.connect(self.db_path)
        self.addCleanup(self.conn.close)

    def migrate(self) -> None:
        self.assertEqual(3, db.migrate(self.conn))

    def seed_inventory(self) -> tuple[int, int, int]:
        self.migrate()
        newspaper_id = db.upsert_newspaper(
            self.conn,
            slug="o_paiz",
            title="O Paiz",
            bn_bib="178691",
            city="Rio de Janeiro",
            active_from="1884-10-01",
            active_to="1934-11-18",
            created_at=NOW,
        )
        protocol_id = db.upsert_protocol(
            self.conn,
            stage="inventory",
            name="teste_inventario",
            version="1.0.0",
            executor_type="deterministic",
            code_commit="abc123",
            parameters={"fonte": "teste"},
            created_at=NOW,
        )
        object_id = db.upsert_digital_object(
            self.conn,
            newspaper_id=newspaper_id,
            source_identifier="per178691_1906_00001",
            source_url="https://example.test/per178691_1906_00001.pdf",
            source_year=1906,
            bn_file_key="178691/per178691_1906_00001.pdf",
            bn_file_number_literal="00001",
            discovered_by_protocol_id=protocol_id,
            discovered_at=NOW,
        )
        return newspaper_id, protocol_id, object_id

    def test_connect_ativa_foreign_keys_e_wal(self) -> None:
        self.assertEqual(
            1, self.conn.execute("PRAGMA foreign_keys").fetchone()[0]
        )
        self.assertEqual(
            "wal", self.conn.execute("PRAGMA journal_mode").fetchone()[0]
        )

    def test_migrate_aplica_migracoes_pendentes_uma_unica_vez(self) -> None:
        self.assertEqual(3, db.migrate(self.conn))
        self.assertEqual(
            3, self.conn.execute("PRAGMA user_version").fetchone()[0]
        )
        before = self.conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]

        self.assertEqual(3, db.migrate(self.conn))
        after = self.conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        self.assertEqual(before, after)

    def test_upserts_de_cadastro_reutilizam_chaves_naturais(self) -> None:
        self.migrate()
        first = db.upsert_newspaper(
            self.conn,
            slug="o_paiz",
            title="O Paiz",
            bn_bib="178691",
            city="Rio de Janeiro",
            created_at=NOW,
        )
        second = db.upsert_newspaper(
            self.conn,
            slug="o_paiz",
            title="O Paiz",
            bn_bib="178691",
            city="Rio de Janeiro",
            created_at=NOW,
        )
        self.assertEqual(first, second)
        self.assertEqual(
            "O Paiz",
            self.conn.execute(
                "SELECT title FROM newspapers WHERE id = ?", (first,)
            ).fetchone()[0],
        )

        with self.assertRaisesRegex(ValueError, "conflito de jornal"):
            db.upsert_newspaper(
                self.conn,
                slug="o_paiz",
                title="O Paiz atualizado",
                bn_bib="178691",
                city="Rio de Janeiro",
                created_at=NOW,
            )

        protocol_first = db.upsert_protocol(
            self.conn,
            stage="inventory",
            name="inventario",
            version="1",
            executor_type="deterministic",
            code_commit="abc",
            parameters={"a": 1},
            created_at=NOW,
        )
        protocol_second = db.upsert_protocol(
            self.conn,
            stage="inventory",
            name="inventario",
            version="1",
            executor_type="deterministic",
            code_commit="abc",
            parameters={"a": 1},
            created_at=NOW,
        )
        self.assertEqual(protocol_first, protocol_second)

        with self.assertRaisesRegex(ValueError, "conflito de protocolo"):
            db.upsert_protocol(
                self.conn,
                stage="inventory",
                name="inventario",
                version="1",
                executor_type="deterministic",
                code_commit="outro-commit",
                parameters={"a": 2},
                created_at=NOW,
            )

    def test_protocolo_reutilizado_ignora_code_commit_na_identidade(self) -> None:
        self.migrate()
        first = db.upsert_protocol(
            self.conn,
            stage="inventory",
            name="inventario",
            version="1",
            executor_type="deterministic",
            code_commit="commit-original",
            parameters={"a": 1},
            created_at=NOW,
        )
        second = db.upsert_protocol(
            self.conn,
            stage="inventory",
            name="inventario",
            version="1",
            executor_type="deterministic",
            code_commit="commit-posterior",
            parameters={"a": 1},
            created_at=NOW,
        )
        self.assertEqual(first, second)
        self.assertEqual(
            "commit-original",
            self.conn.execute(
                "SELECT code_commit FROM protocols WHERE id = ?", (first,)
            ).fetchone()[0],
        )

    def test_objeto_digital_aborta_em_divergencia_de_identidade(self) -> None:
        _, protocol_id, first = self.seed_inventory()
        second = db.upsert_digital_object(
            self.conn,
            newspaper_id=1,
            source_identifier="per178691_1906_00001",
            source_url="https://example.test/per178691_1906_00001.pdf",
            source_year=1906,
            bn_file_key="178691/per178691_1906_00001.pdf",
            bn_file_number_literal="00001",
            discovered_by_protocol_id=protocol_id,
            discovered_at=NOW,
        )
        self.assertEqual(first, second)

        with self.assertRaisesRegex(ValueError, "conflito de objeto digital"):
            db.upsert_digital_object(
                self.conn,
                newspaper_id=1,
                source_identifier="per178691_1906_00001",
                source_url="https://example.test/per178691_1906_00001.pdf",
                source_year=1906,
                bn_file_key="178691/per178691_1906_00001.pdf",
                bn_file_number_literal="00002",
                discovered_by_protocol_id=protocol_id,
                discovered_at=NOW,
            )

    def test_downloads_sao_historicos_e_ponteiro_aponta_para_o_ultimo(self) -> None:
        _, _, object_id = self.seed_inventory()
        first = db.mark_download_status(
            self.conn,
            object_id=object_id,
            result="ok",
            attempted_at=NOW,
            completed_at=NOW,
            http_status=200,
            storage_path="dados/raw_pdf/primeiro.pdf",
            pdf_sha256=HASH_A,
            response_sha256=HASH_A,
            byte_count=1000,
            page_count=8,
        )
        second = db.mark_download_status(
            self.conn,
            object_id=object_id,
            result="ok",
            attempted_at=NOW,
            completed_at=NOW,
            http_status=200,
            storage_path="dados/raw_pdf/segundo.pdf",
            pdf_sha256=HASH_B,
            response_sha256=HASH_B,
            byte_count=2000,
            page_count=9,
        )

        self.assertNotEqual(first, second)
        self.assertEqual(
            2,
            self.conn.execute(
                "SELECT count(*) FROM object_fetches WHERE object_id = ?",
                (object_id,),
            ).fetchone()[0],
        )
        current = db.get_current_fetch(self.conn, object_id)
        self.assertIsNotNone(current)
        self.assertEqual(second, current["id"])
        self.assertEqual(HASH_B, current["pdf_sha256"])
        self.assertEqual("http", current["fetch_mode"])

    def test_fetch_mode_default_e_local_import_sem_response_sha256(self) -> None:
        _, _, object_id = self.seed_inventory()
        http_fetch = db.mark_download_status(
            self.conn,
            object_id=object_id,
            result="ok",
            attempted_at=NOW,
            completed_at=NOW,
            http_status=200,
            storage_path="dados/raw_pdf/http.pdf",
            pdf_sha256=HASH_A,
            response_sha256=HASH_A,
            byte_count=1000,
            page_count=8,
            make_current=False,
        )
        row = self.conn.execute(
            "SELECT fetch_mode FROM object_fetches WHERE id = ?",
            (http_fetch,),
        ).fetchone()
        self.assertEqual("http", row["fetch_mode"])

        import_fetch = db.mark_download_status(
            self.conn,
            object_id=object_id,
            result="ok",
            attempted_at=NOW,
            completed_at=NOW,
            fetch_mode="local_import",
            storage_path="dados/raw_pdf/importado.pdf",
            pdf_sha256=HASH_B,
            byte_count=2000,
            page_count=9,
            make_current=False,
        )
        row = self.conn.execute(
            "SELECT fetch_mode, http_status, response_sha256 "
            "FROM object_fetches WHERE id = ?",
            (import_fetch,),
        ).fetchone()
        self.assertEqual("local_import", row["fetch_mode"])
        self.assertIsNone(row["http_status"])
        self.assertIsNone(row["response_sha256"])

        with self.assertRaises(sqlite3.IntegrityError):
            db.mark_download_status(
                self.conn,
                object_id=object_id,
                result="ok",
                attempted_at=NOW,
                completed_at=NOW,
                fetch_mode="local_import",
                storage_path="dados/raw_pdf/fabricado.pdf",
                pdf_sha256=HASH_B,
                response_sha256=HASH_B,
                byte_count=2000,
                page_count=9,
                make_current=False,
            )

    def test_calendario_e_populacao_sao_idempotentes(self) -> None:
        newspaper_id, protocol_id, _ = self.seed_inventory()
        day_first = db.upsert_calendar_day(
            self.conn,
            newspaper_id=newspaper_id,
            civil_date="1906-01-13",
            created_at=NOW,
        )
        day_second = db.upsert_calendar_day(
            self.conn,
            newspaper_id=newspaper_id,
            civil_date="1906-01-13",
            created_at=NOW,
        )
        self.assertEqual(day_first, day_second)

        population_first = db.upsert_population_definition(
            self.conn,
            name="piloto_1906",
            version="1",
            unit_mode="strict_newspaper_day",
            description="Piloto",
            protocol_id=protocol_id,
            created_at=NOW,
        )
        population_second = db.upsert_population_definition(
            self.conn,
            name="piloto_1906",
            version="1",
            unit_mode="strict_newspaper_day",
            description="Piloto",
            protocol_id=protocol_id,
            created_at=NOW,
        )
        self.assertEqual(population_first, population_second)

        membership_first = db.upsert_population_membership(
            self.conn,
            population_definition_id=population_first,
            calendar_day_id=day_first,
            edition_day_id=None,
            eligibility="eligible",
            reason="teste",
            assigned_at=NOW,
        )
        membership_second = db.upsert_population_membership(
            self.conn,
            population_definition_id=population_first,
            calendar_day_id=day_first,
            edition_day_id=None,
            eligibility="eligible",
            reason="teste",
            assigned_at=NOW,
        )
        self.assertEqual(membership_first, membership_second)

        with self.assertRaisesRegex(ValueError, "conflito de filiação"):
            db.upsert_population_membership(
                self.conn,
                population_definition_id=population_first,
                calendar_day_id=day_first,
                edition_day_id=None,
                eligibility="ineligible",
                reason="mudança sem nova definição",
                assigned_at=NOW,
            )

    def test_transaction_faz_rollback_em_erro(self) -> None:
        self.migrate()
        with self.assertRaises(RuntimeError):
            with db.transaction(self.conn):
                self.conn.execute(
                    """
                    INSERT INTO newspapers(
                        slug, title, bn_bib, city, created_at
                    ) VALUES ('temporario', 'Temporário', 'x', 'x', ?)
                    """,
                    (NOW,),
                )
                raise RuntimeError("falha sintética")

        self.assertEqual(
            0,
            self.conn.execute(
                "SELECT count(*) FROM newspapers WHERE slug='temporario'"
            ).fetchone()[0],
        )


class MigrationForeignKeySafetyTests(unittest.TestCase):
    """apply_migrations precisa desligar FK só durante a reconstrução de
    tabela (RENAME/CREATE/DROP), religar sempre e nunca deixar a conexão
    com FK desligado ou uma transação pendente após uma migração falha."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.migrations_dir = Path(self.temporary.name) / "migrations"
        self.migrations_dir.mkdir()
        self.conn = sqlite3.connect(":memory:")
        self.addCleanup(self.conn.close)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def write_migration(self, version: int, sql: str) -> None:
        path = self.migrations_dir / f"{version:03d}_teste.sql"
        path.write_text(sql, encoding="utf-8")

    def test_reconstrucao_de_tabela_preserva_fk_dos_filhos(self) -> None:
        self.write_migration(
            1,
            """
            CREATE TABLE parent (id INTEGER PRIMARY KEY, val TEXT);
            CREATE TABLE child (
                parent_id INTEGER PRIMARY KEY REFERENCES parent(id),
                note TEXT
            );
            INSERT INTO parent(id, val) VALUES (1, 'a');
            INSERT INTO child(parent_id, note) VALUES (1, 'x');
            """,
        )
        self.write_migration(
            2,
            """
            CREATE TABLE parent_new (
                id INTEGER PRIMARY KEY, val TEXT, extra TEXT
            );
            INSERT INTO parent_new(id, val) SELECT id, val FROM parent;
            DROP TABLE parent;
            ALTER TABLE parent_new RENAME TO parent;
            """,
        )
        self.assertEqual(2, db.apply_migrations(self.conn, self.migrations_dir))
        self.assertEqual(
            1, self.conn.execute("PRAGMA foreign_keys").fetchone()[0]
        )
        self.assertEqual([], self.conn.execute("PRAGMA foreign_key_check").fetchall())
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO child(parent_id, note) VALUES (999, 'orphan')"
            )

    def test_migracao_falha_restaura_fk_e_desfaz_transacao(self) -> None:
        self.write_migration(
            1,
            """
            CREATE TABLE t(id INTEGER PRIMARY KEY, v TEXT UNIQUE);
            INSERT INTO t(id, v) VALUES (1, 'x');
            """,
        )
        self.write_migration(
            2,
            """
            INSERT INTO t(id, v) VALUES (2, 'y');
            INSERT INTO t(id, v) VALUES (3, 'x');
            """,
        )
        with self.assertRaises(sqlite3.IntegrityError):
            db.apply_migrations(self.conn, self.migrations_dir)

        self.assertEqual(
            1, self.conn.execute("PRAGMA foreign_keys").fetchone()[0]
        )
        self.assertFalse(self.conn.in_transaction)
        self.assertEqual(
            [(1, "x")],
            [tuple(row) for row in self.conn.execute("SELECT * FROM t")],
        )
        self.assertEqual(
            1, self.conn.execute("PRAGMA user_version").fetchone()[0]
        )


if __name__ == "__main__":
    unittest.main()
