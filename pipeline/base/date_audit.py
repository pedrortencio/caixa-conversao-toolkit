"""Leitura e validação do manifesto de auditoria visual das datas de 1906."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Iterable, Mapping


MANIFEST_RELATIVE_PATH = Path(
    "pipeline/base/manifests/datas_masthead_1906.json"
)
ROOT_KEYS = {
    "schema_version",
    "audit_id",
    "audited_at",
    "newspaper_bib",
    "source_year",
    "verification_method",
    "reviewer_type",
    "reviewer_label",
    "independent_human_review",
    "records",
}
RECORD_KEYS = {
    "source_identifier",
    "normalized_date",
    "date_literal",
    "pdf_path",
    "pdf_sha256",
    "page_number",
    "evidence_region",
    "decision",
    "previous_ocr_date",
    "notes",
}
IDENTIFIER_RE = re.compile(r"^per178691_1906_\d{5}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class ArtifactEvidence:
    source_identifier: str
    pdf_path: str
    pdf_sha256: str
    page_count: int
    source_year: int


@dataclass(frozen=True, slots=True)
class DateAuditRecord:
    source_identifier: str
    normalized_date: str
    date_literal: str
    pdf_path: str
    pdf_sha256: str
    page_number: int
    evidence_region: str
    decision: str
    previous_ocr_date: str | None
    notes: str


@dataclass(frozen=True, slots=True)
class DateAuditManifest:
    schema_version: int
    audit_id: str
    audited_at: str
    newspaper_bib: str
    source_year: int
    verification_method: str
    reviewer_type: str
    reviewer_label: str
    independent_human_review: bool
    records: tuple[DateAuditRecord, ...]
    records_by_identifier: Mapping[str, DateAuditRecord]
    file_sha256: str
    relative_path: str


def manifest_path(repo_root: Path) -> Path:
    return repo_root.resolve() / MANIFEST_RELATIVE_PATH


def _exact_keys(
    payload: dict[str, object],
    expected: set[str],
    context: str,
) -> None:
    if set(payload) != expected:
        missing = sorted(expected - set(payload))
        extra = sorted(set(payload) - expected)
        raise ValueError(f"{context}: campos ausentes={missing}; extras={extra}")


def _iso_1906(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field}: data deve ser texto ISO")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{field}: data ISO inválida: {value!r}") from error
    if parsed.year != 1906:
        raise ValueError(f"{field}: data fora de 1906: {value!r}")
    return value


def _nonempty_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: texto obrigatório vazio ou inválido")
    return value


def load_manifest(
    path: Path,
    artifacts: Iterable[ArtifactEvidence],
) -> DateAuditManifest:
    raw = path.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"manifesto inválido: {path}") from error
    if not isinstance(payload, dict):
        raise ValueError("manifesto: raiz deve ser objeto JSON")
    _exact_keys(payload, ROOT_KEYS, "manifesto")
    if payload["schema_version"] != 1:
        raise ValueError(
            f"schema_version desconhecido: {payload['schema_version']!r}"
        )
    audit_id = _nonempty_text(payload["audit_id"], "audit_id")
    audited_at = _nonempty_text(payload["audited_at"], "audited_at")
    try:
        date.fromisoformat(audited_at)
    except ValueError as error:
        raise ValueError(
            f"audited_at: data ISO inválida: {audited_at!r}"
        ) from error
    reviewer_label = _nonempty_text(
        payload["reviewer_label"], "reviewer_label"
    )
    if payload["newspaper_bib"] != "178691" or payload["source_year"] != 1906:
        raise ValueError("manifesto deve descrever O Paiz/BIB 178691 em 1906")
    if payload["verification_method"] != "visual_masthead":
        raise ValueError("verification_method inválido")
    if payload["reviewer_type"] != "ai_assisted_visual_review":
        raise ValueError("reviewer_type inválido")
    if payload["independent_human_review"] is not False:
        raise ValueError("independent_human_review deve ser false")
    raw_records = payload["records"]
    if not isinstance(raw_records, list) or len(raw_records) != 27:
        raise ValueError("manifesto deve conter exatamente 27 registros")

    evidence = {item.source_identifier: item for item in artifacts}
    records: list[DateAuditRecord] = []
    seen: set[str] = set()
    for index, item in enumerate(raw_records):
        if not isinstance(item, dict):
            raise ValueError(f"records[{index}]: deve ser objeto")
        _exact_keys(item, RECORD_KEYS, f"records[{index}]")
        source_identifier = item["source_identifier"]
        if (
            not isinstance(source_identifier, str)
            or not IDENTIFIER_RE.fullmatch(source_identifier)
        ):
            raise ValueError(f"records[{index}].source_identifier inválido")
        if source_identifier in seen:
            raise ValueError(f"source_identifier duplicado: {source_identifier}")
        seen.add(source_identifier)
        artifact = evidence.get(source_identifier)
        if artifact is None:
            raise ValueError(f"artefato desconhecido: {source_identifier}")
        normalized_date = _iso_1906(
            item["normalized_date"], "normalized_date"
        )
        decision = item["decision"]
        previous = item["previous_ocr_date"]
        if decision not in {"fill_missing_ocr", "correct_ocr"}:
            raise ValueError(f"decision inválida: {decision!r}")
        if decision == "fill_missing_ocr" and previous is not None:
            raise ValueError(
                "previous_ocr_date deve ser null em fill_missing_ocr"
            )
        if decision == "correct_ocr":
            previous = _iso_1906(previous, "previous_ocr_date")
            if previous == normalized_date:
                raise ValueError(
                    "previous_ocr_date deve divergir da correção"
                )
        pdf_path = item["pdf_path"]
        pdf_sha256 = item["pdf_sha256"]
        page_number = item["page_number"]
        if pdf_path != artifact.pdf_path:
            raise ValueError(f"{source_identifier}: pdf_path divergente")
        if (
            not isinstance(pdf_sha256, str)
            or not SHA256_RE.fullmatch(pdf_sha256)
        ):
            raise ValueError(f"{source_identifier}: pdf_sha256 inválido")
        if pdf_sha256 != artifact.pdf_sha256:
            raise ValueError(f"{source_identifier}: pdf_sha256 divergente")
        if (
            not isinstance(page_number, int)
            or not 1 <= page_number <= artifact.page_count
        ):
            raise ValueError(f"{source_identifier}: page_number inexistente")
        if artifact.source_year != 1906:
            raise ValueError(f"{source_identifier}: artefato fora de 1906")
        if item["evidence_region"] != "masthead":
            raise ValueError(f"{source_identifier}: evidence_region inválida")
        if (
            not isinstance(item["date_literal"], str)
            or not item["date_literal"].strip()
        ):
            raise ValueError(f"{source_identifier}: date_literal vazio")
        if not isinstance(item["notes"], str):
            raise ValueError(f"{source_identifier}: notes deve ser texto")
        records.append(DateAuditRecord(**item))

    records.sort(key=lambda record: record.source_identifier)
    by_identifier = MappingProxyType(
        {record.source_identifier: record for record in records}
    )
    return DateAuditManifest(
        schema_version=1,
        audit_id=audit_id,
        audited_at=audited_at,
        newspaper_bib="178691",
        source_year=1906,
        verification_method="visual_masthead",
        reviewer_type="ai_assisted_visual_review",
        reviewer_label=reviewer_label,
        independent_human_review=False,
        records=tuple(records),
        records_by_identifier=by_identifier,
        file_sha256=hashlib.sha256(raw).hexdigest(),
        relative_path=MANIFEST_RELATIVE_PATH.as_posix(),
    )
