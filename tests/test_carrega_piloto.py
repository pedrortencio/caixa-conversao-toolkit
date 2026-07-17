from __future__ import annotations

import json
import os
import tempfile
import unittest
from collections import Counter
from contextlib import ExitStack
from dataclasses import replace
from pathlib import Path
import subprocess
import sys

from pipeline.base import carrega_piloto as loader
from pipeline.base import date_audit
from pipeline.base import db as base_db


REPO_ROOT = Path(__file__).resolve().parents[1]


class PilotParserTests(unittest.TestCase):
    def test_analysis_relevance_nao_promove_quote_negativa(self) -> None:
        self.assertFalse(
            loader.analysis_relevance(
                {"relevant_quote": "No relevant quote found."}
            )
        )

    def test_script_pode_ser_executado_diretamente(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "pipeline" / "base" / "carrega_piloto.py"),
                "--help",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_parse_artifact_name(self) -> None:
        self.assertEqual(
            ("178691", 1906, "00001"),
            loader.parse_artifact_name("per178691_1906_00001"),
        )

    def test_parse_artifact_name_rejeita_formato_invalido(self) -> None:
        with self.assertRaises(ValueError):
            loader.parse_artifact_name("opaiz-1906-1")

    def test_parse_transcription_accepts_dois_formatos_de_pagina(self) -> None:
        text = (
            "--- PAGE 1 ---\n"
            "--- PAGE_METADATA START ---\n"
            "RIO DE JANEIRO, 13 DE JANEIRO DE 1906\n"
            "--- PAGE_METADATA END ---\n"
            "--- ARTICLE START ---\nA\n--- ARTICLE END ---\n"
            "--- PAGE per178691_1906_00001.pdf-PAGE2 ---\n"
            "--- ARTICLE START ---\nB\n--- ARTICLE END ---\n"
        )

        pages = loader.parse_transcription(text)

        self.assertEqual([1, 2], sorted(pages))
        self.assertEqual(1, pages[1].article_count)
        self.assertEqual(1, pages[2].article_count)
        self.assertIn("13 DE JANEIRO DE 1906", pages[1].metadata_text)

    def test_parse_transcription_trata_numero_de_edicao_como_pagina_um(self) -> None:
        text = (
            "--- PAGE 7819 ---\n"
            "--- PAGE_METADATA START ---\n"
            "RIO DE JANEIRO, 1 DE MARÇO DE 1906\n"
            "--- PAGE_METADATA END ---\n"
        )

        pages = loader.parse_transcription(text)

        self.assertEqual([1], sorted(pages))
        self.assertEqual("7819", pages[1].label)

    def test_parse_transcription_funde_blocos_duplicados_da_mesma_pagina(self) -> None:
        text = (
            "--- PAGE 1 ---\n"
            "--- ARTICLE START ---\nprimeiro\n--- ARTICLE END ---\n"
            "--- PAGE per178691_1906_08099.pdf-PAGE1 ---\n"
            "--- ARTICLE START ---\nsegundo\n--- ARTICLE END ---\n"
        )

        pages = loader.parse_transcription(text)

        self.assertEqual([1], sorted(pages))
        self.assertEqual(2, pages[1].article_count)
        self.assertIn("primeiro", pages[1].text)
        self.assertIn("segundo", pages[1].text)

    def test_parse_transcription_rejeita_multiplas_edicoes_concatenadas(self) -> None:
        text = (
            "--- PAGE 273 ---\nprimeira edição\n"
            "--- PAGE 274 ---\nsegunda edição\n"
        )

        with self.assertRaisesRegex(ValueError, "múltiplos números de edição"):
            loader.parse_transcription(text)

    def test_parse_observed_date_preserva_literal_e_pagina(self) -> None:
        observed = loader.parse_observed_date(
            "RIO DE JANEIRO-SEGUNDA-FEIRA, 8 DE OUTUBRO DE 1906",
            page_number=1,
        )

        self.assertIsNotNone(observed)
        assert observed is not None
        self.assertEqual("1906-10-08", observed.normalized)
        self.assertIn("8 DE OUTUBRO DE 1906", observed.literal)
        self.assertEqual(1, observed.page_number)

    def test_parse_observed_date_aceita_mes_com_mojibake(self) -> None:
        observed = loader.parse_observed_date(
            "RIO DE JANEIRO, 2 DE MAR\u0102\u2021O DE 1906",
            page_number=1,
        )

        self.assertIsNotNone(observed)
        assert observed is not None
        self.assertEqual("1906-03-02", observed.normalized)

    def test_parse_observed_date_rejeita_data_impossivel(self) -> None:
        observed = loader.parse_observed_date(
            "RIO DE JANEIRO, 31 DE FEVEREIRO DE 1906",
            page_number=1,
        )
        self.assertIsNone(observed)

    def test_count_pdf_pages_rejeita_arquivo_invalido(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            invalid = Path(temporary) / "invalid.pdf"
            invalid.write_bytes(b"nao e pdf")
            with self.assertRaises(ValueError):
                loader.count_pdf_pages(invalid)


class GitCommitTests(unittest.TestCase):
    def _init_repo(self, root: Path) -> None:
        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t.com",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t.com",
        }
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
        (root / "arquivo.txt").write_text("conteudo", encoding="utf-8")
        subprocess.run(
            ["git", "add", "arquivo.txt"], cwd=root, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "inicial"],
            cwd=root,
            check=True,
            capture_output=True,
            env=env,
        )

    def test_git_commit_aceita_arvore_limpa(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._init_repo(root)
            commit = loader.git_commit(root)
            self.assertRegex(commit, r"^[0-9a-f]{40}$")

    def test_git_commit_marca_sujeira_em_modificacao(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._init_repo(root)
            (root / "arquivo.txt").write_text("mudou", encoding="utf-8")
            commit = loader.git_commit(root)
            self.assertRegex(commit, r"^[0-9a-f]{40}-dirty$")

    def test_git_commit_marca_sujeira_em_arquivo_nao_rastreado(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._init_repo(root)
            (root / "novo.txt").write_text("novo", encoding="utf-8")
            commit = loader.git_commit(root)
            self.assertRegex(commit, r"^[0-9a-f]{40}-dirty$")


class PilotDiscoveryTests(unittest.TestCase):
    def test_discover_artifacts_encontra_recorte_canonico(self) -> None:
        artifacts = loader.discover_artifacts(REPO_ROOT)

        self.assertEqual(67, len(artifacts))
        self.assertEqual({"178691"}, {artifact.bib for artifact in artifacts})
        self.assertTrue(all(artifact.txt_path is not None for artifact in artifacts))
        self.assertEqual(
            Counter({4: 3, 6: 41, 8: 20, 10: 2, 12: 1}),
            Counter(artifact.page_count for artifact in artifacts),
        )
        self.assertTrue(all(len(artifact.pdf_sha256) == 64 for artifact in artifacts))
        self.assertTrue(all(artifact.byte_count > 0 for artifact in artifacts))

    def test_fontes_sem_pdf_canonico_sao_reportadas(self) -> None:
        artifacts = loader.discover_artifacts(REPO_ROOT)
        unmatched = loader.find_unmatched_sources(REPO_ROOT, artifacts)

        txt_unmatched = [path for path in unmatched if path.suffix == ".txt"]
        self.assertEqual(474, len(txt_unmatched))
        self.assertTrue(
            any("Estadão" in str(path.parent) for path in txt_unmatched)
        )

    def test_auditoria_visual_resolve_27_casos_sem_apagar_o_ocr(self) -> None:
        artifacts = loader.discover_artifacts(REPO_ROOT)
        self.assertEqual(
            45,
            sum(artifact.ocr_observed_date is not None for artifact in artifacts),
        )
        manifest = date_audit.load_manifest(
            date_audit.manifest_path(REPO_ROOT),
            [loader.artifact_evidence(artifact) for artifact in artifacts],
        )
        audited = loader.attach_date_audit(artifacts, manifest)
        self.assertEqual(67, sum(a.observed_date is not None for a in audited))
        self.assertEqual(27, sum(a.audit_record is not None for a in audited))

    def test_auditoria_prevalece_e_preserva_candidato_ocr(self) -> None:
        artifacts = loader.discover_artifacts(REPO_ROOT)
        manifest = date_audit.load_manifest(
            date_audit.manifest_path(REPO_ROOT),
            [loader.artifact_evidence(artifact) for artifact in artifacts],
        )
        audited = {
            artifact.stem: artifact
            for artifact in loader.attach_date_audit(artifacts, manifest)
        }
        issue = audited["per178691_1906_07959"]
        self.assertEqual("1906-07-10", issue.ocr_observed_date.normalized)
        self.assertEqual("1906-07-19", issue.observed_date.normalized)

    def test_sem_manifesto_nao_imputa_data_pela_sequencia(self) -> None:
        artifacts = {
            artifact.stem: artifact
            for artifact in loader.discover_artifacts(REPO_ROOT)
        }
        issue = artifacts["per178691_1906_08002"]
        self.assertIsNone(issue.ocr_observed_date)
        self.assertIsNone(issue.observed_date)

    def test_rejeita_previous_ocr_date_divergente_do_candidato(self) -> None:
        artifacts = loader.discover_artifacts(REPO_ROOT)
        manifest = date_audit.load_manifest(
            date_audit.manifest_path(REPO_ROOT),
            [loader.artifact_evidence(artifact) for artifact in artifacts],
        )
        identifier = "per178691_1906_07959"
        bad_record = replace(
            manifest.records_by_identifier[identifier],
            previous_ocr_date="1906-07-11",
        )
        bad_manifest = replace(
            manifest,
            records_by_identifier={
                **manifest.records_by_identifier,
                identifier: bad_record,
            },
        )
        with self.assertRaisesRegex(ValueError, "previous_ocr_date"):
            loader.attach_date_audit(artifacts, bad_manifest)


class PilotLoadTests(unittest.TestCase):
    def test_load_materializa_piloto_real_e_e_idempotente(self) -> None:
        with ExitStack() as stack:
            temporary = stack.enter_context(tempfile.TemporaryDirectory())
            database = Path(temporary) / "piloto.db"

            first = loader.load(database, repo_root=REPO_ROOT)
            second = loader.load(database, repo_root=REPO_ROOT)

            self.assertEqual(first, second)
            self.assertEqual(67, first.digital_objects)
            self.assertEqual(67, first.editions)
            self.assertEqual(450, first.physical_pages)
            self.assertEqual(102, first.transcriptions)
            self.assertEqual(67, first.observed_dates)
            self.assertEqual(0, first.imputed_dates)
            self.assertEqual(0, first.unresolved_dates)
            self.assertEqual(474, first.unmatched_transcriptions)

            conn = base_db.connect(database)
            stack.callback(conn.close)
            loader.contract_checks(conn)
            counts = {
                table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                for table in (
                    "digital_objects",
                    "edition_days",
                    "object_fetches",
                    "physical_pages",
                    "transcriptions",
                    "date_records",
                )
            }
            self.assertEqual(
                {
                    "digital_objects": 67,
                    "edition_days": 67,
                    "object_fetches": 67,
                    "physical_pages": 450,
                    "transcriptions": 102,
                    "date_records": 72,
                },
                counts,
            )
            self.assertEqual(
                67,
                conn.execute(
                    "SELECT count(*) FROM current_edition_dates"
                ).fetchone()[0],
            )
            self.assertEqual(
                67,
                conn.execute(
                    """
                    SELECT count(DISTINCT d.normalized_date)
                    FROM current_edition_dates c
                    JOIN date_records d ON d.id=c.date_record_id
                    """
                ).fetchone()[0],
            )
            self.assertEqual(
                67,
                conn.execute(
                    "SELECT count(*) FROM edition_days WHERE identity_status='confirmed'"
                ).fetchone()[0],
            )
            self.assertEqual(
                27,
                conn.execute(
                    """
                    SELECT count(*) FROM date_records d
                    JOIN protocols p ON p.id=d.protocol_id
                    WHERE p.name='masthead_visual_manifest'
                      AND d.evidence_transcription_id IS NULL
                    """
                ).fetchone()[0],
            )
            self.assertEqual(
                67,
                conn.execute(
                    "SELECT count(*) FROM population_memberships"
                ).fetchone()[0],
            )
            protocol = conn.execute(
                """
                SELECT parameters_json FROM protocols
                WHERE stage='date_parsing'
                  AND name='masthead_visual_manifest'
                  AND version='1.0.0'
                """
            ).fetchone()
            self.assertIsNotNone(protocol)
            parameters = json.loads(protocol["parameters_json"])
            self.assertEqual(64, len(parameters["manifest_sha256"]))
            self.assertFalse(parameters["independent_human_review"])
            self.assertEqual(
                "ai_assisted_visual_review",
                parameters["reviewer_type"],
            )
            corrections = {
                "per178691_1906_07943": ("1906-07-03", "1906-07-05"),
                "per178691_1906_07959": ("1906-07-19", "1906-07-10"),
                "per178691_1906_08020": ("1906-09-18", "1906-09-08"),
                "per178691_1906_08028": ("1906-09-26", "1906-09-20"),
                "per178691_1906_08107": ("1906-12-14", "1906-12-08"),
            }
            for logical_key, (current_date, historical_date) in corrections.items():
                rows = conn.execute(
                    """
                    SELECT d.normalized_date,
                           CASE WHEN c.date_record_id=d.id THEN 1 ELSE 0 END AS current
                    FROM edition_days e
                    JOIN date_records d ON d.edition_day_id=e.id
                    LEFT JOIN current_edition_dates c ON c.edition_day_id=e.id
                    WHERE e.logical_key=?
                    ORDER BY d.normalized_date
                    """,
                    (logical_key,),
                ).fetchall()
                observed = {row["normalized_date"]: row["current"] for row in rows}
                self.assertEqual(1, observed[current_date])
                self.assertEqual(0, observed[historical_date])
            self.assertEqual(
                450,
                conn.execute(
                    """
                    SELECT count(*) FROM current_page_assessments
                    WHERE assessment_level='screening' AND assessment_id IN (
                        SELECT id FROM page_assessments
                        WHERE result='not_assessed'
                    )
                    """
                ).fetchone()[0],
            )
            self.assertEqual(
                102,
                conn.execute(
                    "SELECT count(*) FROM current_transcriptions"
                ).fetchone()[0],
            )
            self.assertEqual(
                0,
                conn.execute(
                    """
                    SELECT count(*) FROM object_fetches
                    WHERE result='ok' AND http_status IS NOT NULL
                    """
                ).fetchone()[0],
            )
            conn.close()


class ContractCheckTests(unittest.TestCase):
    def test_contract_check_detecta_pagina_sem_avaliacao_vigente(self) -> None:
        with ExitStack() as stack:
            temporary = stack.enter_context(tempfile.TemporaryDirectory())
            database = Path(temporary) / "piloto.db"
            loader.load(database, repo_root=REPO_ROOT)
            conn = base_db.connect(database)
            stack.callback(conn.close)
            conn.execute(
                """
                DELETE FROM current_page_assessments
                WHERE rowid = (SELECT min(rowid) FROM current_page_assessments)
                """
            )

            with self.assertRaisesRegex(
                AssertionError, "páginas sem avaliação vigente"
            ):
                loader.contract_checks(conn)
            conn.close()


if __name__ == "__main__":
    unittest.main()
