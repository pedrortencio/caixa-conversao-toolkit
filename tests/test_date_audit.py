from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pipeline.base import carrega_piloto as loader
from pipeline.base import date_audit


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = date_audit.manifest_path(REPO_ROOT)


def real_evidence() -> list[date_audit.ArtifactEvidence]:
    return [
        date_audit.ArtifactEvidence(
            source_identifier=artifact.stem,
            pdf_path=artifact.relative_pdf_path,
            pdf_sha256=artifact.pdf_sha256,
            page_count=artifact.page_count,
            source_year=artifact.year,
        )
        for artifact in loader.discover_artifacts(REPO_ROOT)
    ]


class DateAuditManifestTests(unittest.TestCase):
    def write_variant(self, mutate) -> Path:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        mutate(payload)
        temporary = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", encoding="utf-8", delete=False
        )
        with temporary:
            json.dump(payload, temporary, ensure_ascii=False, sort_keys=True)
        self.addCleanup(Path(temporary.name).unlink, missing_ok=True)
        return Path(temporary.name)

    def test_manifesto_real_tem_27_registros_ligados_aos_pdfs(self) -> None:
        manifest = date_audit.load_manifest(MANIFEST, real_evidence())
        self.assertEqual(1, manifest.schema_version)
        self.assertEqual(27, len(manifest.records))
        self.assertEqual(64, len(manifest.file_sha256))
        self.assertFalse(manifest.independent_human_review)
        self.assertEqual(
            "1906-07-19",
            manifest.records_by_identifier[
                "per178691_1906_07959"
            ].normalized_date,
        )

    def test_rejeita_schema_desconhecido(self) -> None:
        path = self.write_variant(lambda payload: payload.update(schema_version=2))
        with self.assertRaisesRegex(ValueError, "schema_version"):
            date_audit.load_manifest(path, real_evidence())

    def test_rejeita_identificador_duplicado(self) -> None:
        def duplicate(payload):
            payload["records"][-1] = dict(payload["records"][0])

        path = self.write_variant(duplicate)
        with self.assertRaisesRegex(ValueError, "duplicado"):
            date_audit.load_manifest(path, real_evidence())

    def test_rejeita_hash_divergente(self) -> None:
        def corrupt(payload):
            payload["records"][0]["pdf_sha256"] = "0" * 64

        path = self.write_variant(corrupt)
        with self.assertRaisesRegex(ValueError, "pdf_sha256"):
            date_audit.load_manifest(path, real_evidence())

    def test_rejeita_data_fora_de_1906(self) -> None:
        def corrupt(payload):
            payload["records"][0]["normalized_date"] = "1907-05-11"

        path = self.write_variant(corrupt)
        with self.assertRaisesRegex(ValueError, "1906"):
            date_audit.load_manifest(path, real_evidence())

    def test_rejeita_previous_ocr_incoerente(self) -> None:
        def corrupt(payload):
            payload["records"][0]["previous_ocr_date"] = "1906-05-10"

        path = self.write_variant(corrupt)
        with self.assertRaisesRegex(ValueError, "previous_ocr_date"):
            date_audit.load_manifest(path, real_evidence())


if __name__ == "__main__":
    unittest.main()
