"""Carga auditável das fontes canônicas do piloto de 1906."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import date_audit
from pipeline.base import db as base_db


PDF_NAME_RE = re.compile(
    r"^per(?P<bib>\d+)_(?P<year>\d{4})_(?P<number>\d+)$"
)
PAGE_RE = re.compile(
    r"(?m)^--- PAGE (?:(?P<label>.+?)-PAGE)?(?P<number>\d+) ---\s*$"
)
METADATA_RE = re.compile(
    r"--- PAGE_METADATA START ---(.*?)--- PAGE_METADATA END ---",
    re.DOTALL,
)
ARTICLE_RE = re.compile(
    r"--- ARTICLE START ---(.*?)--- ARTICLE END ---",
    re.DOTALL,
)

MONTHS = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}

NEWSPAPERS = {
    "178691": {
        "slug": "o_paiz",
        "title": "O Paiz",
        "bn_bib": "178691",
        "city": "Rio de Janeiro",
    },
    "090972": {
        "slug": "correio_paulistano",
        "title": "Correio Paulistano",
        "bn_bib": "090972",
        "city": "São Paulo",
    },
    "103730": {
        "slug": "gazeta_noticias",
        "title": "Gazeta de Notícias",
        "bn_bib": "103730",
        "city": "Rio de Janeiro",
    },
    "089842": {
        "slug": "correio_manha",
        "title": "Correio da Manhã",
        "bn_bib": "089842",
        "city": "Rio de Janeiro",
    },
    "estadao": {
        "slug": "estadao",
        "title": "O Estado de S. Paulo",
        "bn_bib": "acervo-proprio-estadao",
        "city": "São Paulo",
    },
}


@dataclass(frozen=True, slots=True)
class PageText:
    number: int
    label: str
    text: str
    article_ordinals: tuple[int, ...]
    metadata_text: str

    @property
    def article_count(self) -> int:
        return len(self.article_ordinals)


@dataclass(frozen=True, slots=True)
class ObservedDate:
    literal: str
    normalized: str
    page_number: int


@dataclass(frozen=True, slots=True)
class Artifact:
    pdf_path: Path
    relative_pdf_path: str
    stem: str
    bib: str
    year: int
    file_number: str
    pdf_sha256: str
    byte_count: int
    page_count: int
    txt_path: Path | None
    pages_text: dict[int, PageText]
    ocr_observed_date: ObservedDate | None
    audit_record: date_audit.DateAuditRecord | None = None

    @property
    def observed_date(self) -> ObservedDate | None:
        if self.audit_record is not None:
            return ObservedDate(
                literal=self.audit_record.date_literal,
                normalized=self.audit_record.normalized_date,
                page_number=self.audit_record.page_number,
            )
        return self.ocr_observed_date


@dataclass(frozen=True, slots=True)
class CoverageReport:
    canonical_pdfs: int
    digital_objects: int
    editions: int
    physical_pages: int
    transcriptions: int
    observed_dates: int
    imputed_dates: int
    unresolved_dates: int
    editions_without_date_pointer: int
    unmatched_transcriptions: int
    assessment_results: tuple[tuple[str, str, int], ...]


def parse_artifact_name(stem: str) -> tuple[str, int, str]:
    """Decompõe a identidade canônica de um PDF da Hemeroteca."""
    match = PDF_NAME_RE.fullmatch(stem)
    if not match:
        raise ValueError(f"nome de artefato inválido: {stem}")
    return match.group("bib"), int(match.group("year")), match.group("number")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def count_pdf_pages(path: Path) -> int:
    """Conta páginas nos PDFs do piloto sem introduzir dependência externa."""
    data = path.read_bytes()
    if not data.startswith(b"%PDF-"):
        raise ValueError(f"arquivo sem assinatura PDF: {path}")

    direct = len(re.findall(rb"/Type\s*/Page(?!s)\b", data))
    if direct:
        return direct

    counts = [
        int(raw)
        for raw in re.findall(rb"/Count\s+([0-9]+)\b", data)
        if 0 < int(raw) < 10_000
    ]
    if counts:
        return max(counts)
    raise ValueError(f"não foi possível contar as páginas de {path}")


def repair_mojibake(value: str) -> str:
    """Reverte a dupla interpretação UTF-8/Latin-1 observada no legado."""
    repaired = value
    for corrupted, correct in (
        ("\u0102\u2021", "\u00c7"),
        ("\u0102\u00a7", "\u00e7"),
        ("\u00c3\u2021", "\u00c7"),
        ("\u00c3\u00a7", "\u00e7"),
    ):
        repaired = repaired.replace(corrupted, correct)
    for _ in range(2):
        if "Ã" not in repaired and "Â" not in repaired:
            break
        try:
            candidate = repaired.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if candidate == repaired:
            break
        repaired = candidate
    return repaired


def normalize_ocr(value: str) -> str:
    repaired = repair_mojibake(value)
    decomposed = unicodedata.normalize("NFKD", repaired)
    without_marks = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )
    return re.sub(r"\s+", " ", without_marks).strip().lower()


def parse_observed_date(
    metadata_text: str,
    *,
    page_number: int,
) -> ObservedDate | None:
    """Extrai uma data observada no masthead, sem imputação."""
    month_pattern = "|".join(MONTHS)
    pattern = re.compile(
        rf"\b(?P<day>[0-3]?\d)\s+"
        rf"(?:de\s+)?(?P<month>{month_pattern})\s+"
        rf"(?:de\s+)?(?P<year>1906)\b",
        re.IGNORECASE,
    )
    for original_line in metadata_text.splitlines():
        match = pattern.search(normalize_ocr(original_line))
        if not match:
            continue
        try:
            candidate = date(
                int(match.group("year")),
                MONTHS[match.group("month").lower()],
                int(match.group("day")),
            )
        except ValueError:
            continue
        return ObservedDate(
            literal=original_line.strip(),
            normalized=candidate.isoformat(),
            page_number=page_number,
        )
    return None


def parse_transcription(text: str) -> dict[int, PageText]:
    """Separa uma transcrição legada em páginas físicas."""
    matches = list(PAGE_RE.finditer(text))
    if not matches:
        raise ValueError("transcrição sem marcadores PAGE")

    result: dict[int, PageText] = {}
    article_ordinal = 0
    legacy_issue_numbers: set[int] = set()
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip() + "\n"
        marker_number = int(match.group("number"))
        legacy_issue_marker = match.group("label") is None and marker_number > 100
        if legacy_issue_marker:
            legacy_issue_numbers.add(marker_number)
            if len(legacy_issue_numbers) > 1:
                raise ValueError(
                    "transcrição com múltiplos números de edição concatenados: "
                    f"{sorted(legacy_issue_numbers)}"
                )
        number = 1 if legacy_issue_marker else marker_number
        ordinals: list[int] = []
        for _ in ARTICLE_RE.finditer(block):
            article_ordinal += 1
            ordinals.append(article_ordinal)
        metadata_match = METADATA_RE.search(block)
        metadata = metadata_match.group(1).strip() if metadata_match else ""
        page = PageText(
            number=number,
            label=match.group("label") or str(marker_number),
            text=block,
            article_ordinals=tuple(ordinals),
            metadata_text=metadata,
        )
        previous = result.get(number)
        if previous is None:
            result[number] = page
        else:
            result[number] = PageText(
                number=number,
                label=previous.label,
                text=previous.text.rstrip() + "\n\n" + page.text,
                article_ordinals=(
                    previous.article_ordinals + page.article_ordinals
                ),
                metadata_text=previous.metadata_text or page.metadata_text,
            )
    return result


def observed_date_from_pages(
    pages: dict[int, PageText],
) -> ObservedDate | None:
    for page_number in sorted(pages):
        metadata = pages[page_number].metadata_text
        if not metadata:
            continue
        observed = parse_observed_date(metadata, page_number=page_number)
        if observed is not None:
            return observed
    return None


def source_paths(repo_root: Path) -> tuple[Path, Path, Path]:
    transcriptions = repo_root / "dados" / "piloto_1906" / "data_processed"
    pdfs = repo_root / "dados" / "raw_pdf" / "piloto_1906" / "data_tests"
    analyses = repo_root / "dados" / "piloto_1906" / "analises_json"
    return transcriptions, pdfs, analyses


def transcription_index(repo_root: Path) -> dict[str, Path]:
    transcriptions, _, _ = source_paths(repo_root)
    result: dict[str, Path] = {}
    for path in sorted(transcriptions.rglob("*.txt")):
        if PDF_NAME_RE.fullmatch(path.stem):
            result[path.stem] = path
    return result


def discover_artifacts(repo_root: Path) -> list[Artifact]:
    """Descobre a interseção materializável entre PDF e transcrição."""
    _, pdf_root, _ = source_paths(repo_root)
    txt_by_stem = transcription_index(repo_root)
    artifacts: list[Artifact] = []

    for pdf_path in sorted(pdf_root.glob("per*_1906_*.pdf")):
        bib, year, file_number = parse_artifact_name(pdf_path.stem)
        txt_path = txt_by_stem.get(pdf_path.stem)
        pages: dict[int, PageText] = {}
        if txt_path is not None:
            pages = parse_transcription(txt_path.read_text(encoding="utf-8"))

        page_count = count_pdf_pages(pdf_path)
        if pages and max(pages) > page_count:
            raise ValueError(
                f"{txt_path}: PAGE{max(pages)} excede as {page_count} páginas do PDF"
            )
        artifacts.append(
            Artifact(
                pdf_path=pdf_path,
                relative_pdf_path=pdf_path.relative_to(repo_root).as_posix(),
                stem=pdf_path.stem,
                bib=bib,
                year=year,
                file_number=file_number,
                pdf_sha256=sha256_file(pdf_path),
                byte_count=pdf_path.stat().st_size,
                page_count=page_count,
                txt_path=txt_path,
                pages_text=pages,
                ocr_observed_date=observed_date_from_pages(pages),
            )
        )
    return artifacts


def artifact_evidence(artifact: Artifact) -> date_audit.ArtifactEvidence:
    return date_audit.ArtifactEvidence(
        source_identifier=artifact.stem,
        pdf_path=artifact.relative_pdf_path,
        pdf_sha256=artifact.pdf_sha256,
        page_count=artifact.page_count,
        source_year=artifact.year,
    )


def attach_date_audit(
    artifacts: list[Artifact],
    manifest: date_audit.DateAuditManifest,
) -> list[Artifact]:
    result: list[Artifact] = []
    for artifact in artifacts:
        record = manifest.records_by_identifier.get(artifact.stem)
        if record is not None:
            ocr_date = (
                artifact.ocr_observed_date.normalized
                if artifact.ocr_observed_date is not None
                else None
            )
            if record.decision == "fill_missing_ocr" and ocr_date is not None:
                raise ValueError(
                    f"{artifact.stem}: fill_missing_ocr encontrou candidato OCR"
                )
            if (
                record.decision == "correct_ocr"
                and ocr_date != record.previous_ocr_date
            ):
                raise ValueError(
                    f"{artifact.stem}: previous_ocr_date diverge do candidato OCR"
                )
        result.append(replace(artifact, audit_record=record))
    return result


def find_unmatched_sources(
    repo_root: Path,
    artifacts: list[Artifact],
) -> list[Path]:
    """Lista fontes textuais sem PDF canônico no recorte autorizado."""
    transcriptions, _, analyses = source_paths(repo_root)
    matched = {artifact.stem for artifact in artifacts}
    paths = [
        path
        for path in transcriptions.rglob("*.txt")
        if path.stem not in matched
    ]
    paths.extend(analyses.glob("*.json"))
    return sorted(paths)


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def git_commit(repo_root: Path) -> str:
    """Devolve o commit vigente; sufixa '-dirty' se a árvore tiver mudança
    não commitada, em vez de abortar (achado E.4: o censo escreve
    manifestos versionados continuamente por horas, então a árvore fica
    legitimamente suja durante toda a operação normal)."""
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    commit = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RuntimeError(f"commit Git inválido: {commit!r}")
    if status.stdout.strip():
        return f"{commit}-dirty"
    return commit


def relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def manifest_sha256(artifacts: list[Artifact], repo_root: Path) -> str:
    manifest = [
        {
            "path": artifact.relative_pdf_path,
            "sha256": artifact.pdf_sha256,
            "page_count": artifact.page_count,
            "transcription": (
                relative(artifact.txt_path, repo_root)
                if artifact.txt_path is not None
                else None
            ),
        }
        for artifact in artifacts
    ]
    raw = json.dumps(manifest, ensure_ascii=False, sort_keys=True)
    return sha256_text(raw)


def get_or_create_run(
    conn: sqlite3.Connection,
    *,
    table: str,
    protocol_id: int,
    scope_hash: str,
    submitted: int,
    completed: int,
    timestamp: str,
) -> int:
    if table not in {"identification_runs", "transcription_runs"}:
        raise ValueError(f"tabela de execução não permitida: {table}")
    row = conn.execute(
        f"""
        SELECT id FROM {table}
        WHERE protocol_id = ? AND scope_manifest_sha256 = ?
        ORDER BY id DESC LIMIT 1
        """,
        (protocol_id, scope_hash),
    ).fetchone()
    if row is not None:
        return int(row["id"])
    cursor = conn.execute(
        f"""
        INSERT INTO {table}(
            protocol_id, started_at, completed_at, run_status,
            scope_manifest_sha256, pages_submitted, pages_completed
        ) VALUES (?, ?, ?, 'ok', ?, ?, ?)
        """,
        (
            protocol_id,
            timestamp,
            timestamp,
            scope_hash,
            submitted,
            completed,
        ),
    )
    return int(cursor.lastrowid)


def upsert_edition(
    conn: sqlite3.Connection,
    *,
    newspaper_id: int,
    logical_key: str,
    confirmed: bool,
    timestamp: str,
) -> int:
    conn.execute(
        """
        INSERT INTO edition_days(
            newspaper_id, logical_key, edition_kind,
            sequence_in_day, identity_status, created_at
        ) VALUES (?, ?, 'unknown', NULL, ?, ?)
        ON CONFLICT(newspaper_id, logical_key) DO UPDATE SET
            identity_status = excluded.identity_status
        """,
        (
            newspaper_id,
            logical_key,
            "confirmed" if confirmed else "provisional",
            timestamp,
        ),
    )
    row = conn.execute(
        """
        SELECT id FROM edition_days
        WHERE newspaper_id = ? AND logical_key = ?
        """,
        (newspaper_id, logical_key),
    ).fetchone()
    assert row is not None
    return int(row["id"])


def current_fetch(
    conn: sqlite3.Connection,
    *,
    object_id: int,
    pdf_sha256: str,
    storage_path: str,
) -> int | None:
    row = conn.execute(
        """
        SELECT id FROM object_fetches
        WHERE object_id = ? AND result = 'ok'
          AND pdf_sha256 = ? AND storage_path = ?
        ORDER BY id DESC LIMIT 1
        """,
        (object_id, pdf_sha256, storage_path),
    ).fetchone()
    return int(row["id"]) if row is not None else None


def upsert_page(
    conn: sqlite3.Connection,
    *,
    object_id: int,
    page_number: int,
    pdf_path: str,
    pdf_sha256: str,
    timestamp: str,
) -> int:
    conn.execute(
        """
        INSERT INTO physical_pages(
            object_id, page_number, source_page_label,
            visual_path, visual_sha256, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(object_id, page_number) DO UPDATE SET
            source_page_label = excluded.source_page_label,
            visual_path = excluded.visual_path,
            visual_sha256 = excluded.visual_sha256
        """,
        (
            object_id,
            page_number,
            str(page_number),
            f"{pdf_path}#page={page_number}",
            pdf_sha256,
            timestamp,
        ),
    )
    row = conn.execute(
        """
        SELECT id FROM physical_pages
        WHERE object_id = ? AND page_number = ?
        """,
        (object_id, page_number),
    ).fetchone()
    assert row is not None
    return int(row["id"])


def ensure_identifier(
    conn: sqlite3.Connection,
    *,
    edition_id: int,
    literal_value: str,
    normalized_value: str,
    protocol_id: int,
    timestamp: str,
) -> int:
    row = conn.execute(
        """
        SELECT id FROM edition_identifiers
        WHERE edition_day_id = ? AND identifier_type = 'bn_file_number'
          AND literal_value = ? AND protocol_id = ?
        ORDER BY id DESC LIMIT 1
        """,
        (edition_id, literal_value, protocol_id),
    ).fetchone()
    if row is not None:
        return int(row["id"])
    cursor = conn.execute(
        """
        INSERT INTO edition_identifiers(
            edition_day_id, identifier_type, literal_value,
            normalized_value, protocol_id, observed_at
        ) VALUES (?, 'bn_file_number', ?, ?, ?, ?)
        """,
        (
            edition_id,
            literal_value,
            normalized_value,
            protocol_id,
            timestamp,
        ),
    )
    return int(cursor.lastrowid)


def ensure_assessment(
    conn: sqlite3.Connection,
    *,
    page_id: int,
    run_id: int,
    level: str,
    result: str,
    raw_text: str,
    rationale: str,
    evidence_json: str | None,
    confidence: float | None,
    timestamp: str,
) -> int:
    raw_hash = sha256_text(raw_text)
    row = conn.execute(
        """
        SELECT id FROM page_assessments
        WHERE page_id = ? AND identification_run_id = ?
          AND assessment_level = ? AND raw_response_sha256 = ?
        ORDER BY id DESC LIMIT 1
        """,
        (page_id, run_id, level, raw_hash),
    ).fetchone()
    if row is None:
        cursor = conn.execute(
            """
            INSERT INTO page_assessments(
                page_id, identification_run_id, assessment_level,
                result, confidence, evidence_region_json, rationale,
                raw_response_text, raw_response_sha256, assessed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                page_id,
                run_id,
                level,
                result,
                confidence,
                evidence_json,
                rationale,
                raw_text,
                raw_hash,
                timestamp,
            ),
        )
        assessment_id = int(cursor.lastrowid)
    else:
        assessment_id = int(row["id"])
    conn.execute(
        """
        INSERT INTO current_page_assessments(
            page_id, assessment_level, assessment_id, selected_at
        ) VALUES (?, ?, ?, ?)
        ON CONFLICT(page_id, assessment_level) DO UPDATE SET
            assessment_id = excluded.assessment_id,
            selected_at = excluded.selected_at
        """,
        (page_id, level, assessment_id, timestamp),
    )
    return assessment_id


def analysis_relevance(value: Any) -> bool | None:
    if isinstance(value, list):
        if not value:
            return False
        decisions = [analysis_relevance(item) for item in value]
        if True in decisions:
            return True
        if None in decisions:
            return None
        return False
    if not isinstance(value, dict):
        return None

    quote = value.get("relevant_quote")
    if isinstance(quote, str):
        normalized_quote = normalize_ocr(quote)
        negative_quotes = (
            "no relevant quote",
            "no relevant mention",
            "no mention",
            "none found",
            "not applicable",
            "nenhuma mencao",
        )
        if normalized_quote in {"", "none", "n/a", "nao se aplica"}:
            return False
        if normalized_quote.startswith(negative_quotes):
            return False
        if normalized_quote:
            return True

    searchable = normalize_ocr(
        " ".join(
            str(value.get(key, ""))
            for key in ("message", "analysis", "justification")
        )
    )
    negative_markers = (
        "no relevant mention",
        "no relevant mentions",
        "does not mention",
        "nao ha mencao relevante",
        "nenhuma mencao relevante",
    )
    if any(marker in searchable for marker in negative_markers):
        return False
    return None


def page_analysis(
    artifact: Artifact,
    page: PageText,
    *,
    analysis_root: Path,
    repo_root: Path,
) -> tuple[str, str, str, float | None]:
    records: list[dict[str, Any]] = []
    decisions: list[bool | None] = []
    for ordinal in page.article_ordinals:
        path = analysis_root / f"{artifact.stem}_classificacao_{ordinal}.json"
        if not path.exists():
            records.append(
                {
                    "article_ordinal": ordinal,
                    "path": relative(path, repo_root),
                    "status": "missing",
                }
            )
            decisions.append(None)
            continue

        raw = path.read_text(encoding="utf-8")
        try:
            parsed = json.loads(raw)
            decision = analysis_relevance(parsed)
            status = (
                "relevant"
                if decision is True
                else "not_relevant"
                if decision is False
                else "uncertain"
            )
        except json.JSONDecodeError:
            decision = None
            status = "invalid_json"
        records.append(
            {
                "article_ordinal": ordinal,
                "path": relative(path, repo_root),
                "sha256": sha256_text(raw),
                "status": status,
                "raw": raw,
            }
        )
        decisions.append(decision)

    aggregate = json.dumps(
        {
            "source": "analises_json",
            "edition": artifact.stem,
            "page_number": page.number,
            "articles": records,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    if True in decisions:
        return (
            "relevant",
            aggregate,
            "Ao menos um artigo da página teve menção relevante.",
            1.0,
        )
    if decisions and None not in decisions:
        return (
            "not_relevant",
            aggregate,
            "Todos os artigos demarcados tiveram análise legada negativa.",
            1.0,
        )
    return (
        "uncertain",
        aggregate,
        "Há análise ausente, inválida ou semanticamente inconclusiva.",
        None,
    )


def ensure_transcription(
    conn: sqlite3.Connection,
    *,
    page_id: int,
    run_id: int,
    visual_sha256: str,
    page: PageText,
    source_path: str,
    timestamp: str,
) -> int:
    text_hash = sha256_text(page.text)
    row = conn.execute(
        """
        SELECT id FROM transcriptions
        WHERE page_id = ? AND transcription_run_id = ?
          AND purpose = 'full_page' AND transcript_sha256 = ?
        ORDER BY id DESC LIMIT 1
        """,
        (page_id, run_id, text_hash),
    ).fetchone()
    if row is None:
        cursor = conn.execute(
            """
            INSERT INTO transcriptions(
                page_id, transcription_run_id, purpose,
                input_visual_sha256, evidence_region_json,
                result_status, transcript_text, transcript_sha256,
                raw_response_text, raw_response_sha256,
                export_path, created_at
            ) VALUES (?, ?, 'full_page', ?, ?, 'ok', ?, ?, ?, ?, NULL, ?)
            """,
            (
                page_id,
                run_id,
                visual_sha256,
                json.dumps(
                    {
                        "source_txt": source_path,
                        "page_marker": page.label,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                page.text,
                text_hash,
                page.text,
                text_hash,
                timestamp,
            ),
        )
        transcription_id = int(cursor.lastrowid)
    else:
        transcription_id = int(row["id"])
    conn.execute(
        """
        INSERT INTO current_transcriptions(
            page_id, purpose, transcription_id, selected_at
        ) VALUES (?, 'full_page', ?, ?)
        ON CONFLICT(page_id, purpose) DO UPDATE SET
            transcription_id = excluded.transcription_id,
            selected_at = excluded.selected_at
        """,
        (page_id, transcription_id, timestamp),
    )
    return transcription_id


def ensure_date_record(
    conn: sqlite3.Connection,
    *,
    edition_id: int,
    protocol_id: int,
    observed: ObservedDate,
    page_id: int,
    transcription_id: int | None,
    evidence: dict[str, object],
    parser_name: str,
    parser_version: str,
    notes: str,
    timestamp: str,
) -> int:
    row = conn.execute(
        """
        SELECT id FROM date_records
        WHERE edition_day_id=? AND protocol_id=?
          AND normalized_date=? AND date_literal=? AND status='observed'
        ORDER BY id DESC LIMIT 1
        """,
        (
            edition_id,
            protocol_id,
            observed.normalized,
            observed.literal,
        ),
    ).fetchone()
    if row is not None:
        return int(row["id"])
    evidence_json = json.dumps(
        evidence,
        ensure_ascii=False,
        sort_keys=True,
    )
    cursor = conn.execute(
        """
        INSERT INTO date_records(
            edition_day_id, protocol_id, evidence_page_id,
            evidence_transcription_id, evidence_region_json,
            date_literal, parser_name, parser_version,
            normalized_date, status, confidence, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'observed', 1.0, ?, ?)
        """,
        (
            edition_id,
            protocol_id,
            page_id,
            transcription_id,
            evidence_json,
            observed.literal,
            parser_name,
            parser_version,
            observed.normalized,
            notes,
            timestamp,
        ),
    )
    return int(cursor.lastrowid)


def select_current_date(
    conn: sqlite3.Connection,
    *,
    edition_id: int,
    record_id: int,
    timestamp: str,
) -> None:
    conn.execute(
        """
        INSERT INTO current_edition_dates(
            edition_day_id, date_record_id, selected_at
        ) VALUES (?, ?, ?)
        ON CONFLICT(edition_day_id) DO UPDATE SET
            date_record_id=excluded.date_record_id,
            selected_at=excluded.selected_at
        """,
        (edition_id, record_id, timestamp),
    )


def register_unresolved_date(
    conn: sqlite3.Connection,
    *,
    edition_id: int,
    protocol_id: int,
    page_id: int,
    parser_name: str,
    parser_version: str,
    evidence: dict[str, object],
    notes: str,
    timestamp: str,
    transcription_id: int | None = None,
) -> int:
    """Registra positivamente uma falha de parse de data (achado B).

    Uma tentativa de leitura do masthead que não normaliza nenhuma data
    vira um `date_record` com `status='unresolved'` (data nula, página de
    evidência obrigatória), nunca ausência de ponteiro em
    `current_edition_dates`. O consenso da validação, negativo é registro
    positivo, vale para datas tanto quanto para páginas."""
    evidence_json = json.dumps(evidence, ensure_ascii=False, sort_keys=True)
    cursor = conn.execute(
        """
        INSERT INTO date_records(
            edition_day_id, protocol_id, evidence_page_id,
            evidence_transcription_id, evidence_region_json,
            date_literal, parser_name, parser_version,
            normalized_date, status, confidence, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, NULL, ?, ?, NULL, 'unresolved', NULL, ?, ?)
        """,
        (
            edition_id,
            protocol_id,
            page_id,
            transcription_id,
            evidence_json,
            parser_name,
            parser_version,
            notes,
            timestamp,
        ),
    )
    return int(cursor.lastrowid)


ENUMS = {
    ("protocols", "stage"): {
        "inventory",
        "circulation",
        "search",
        "identification",
        "transcription",
        "date_parsing",
        "recall_reference",
        "classification",
    },
    ("protocols", "executor_type"): {
        "deterministic",
        "manual",
        "model",
        "external_service",
    },
    ("object_fetches", "result"): {
        "ok",
        "http_error",
        "network_error",
        "invalid_pdf",
        "storage_error",
    },
    ("edition_days", "edition_kind"): {
        "regular",
        "supplement",
        "extraordinary",
        "special",
        "unknown",
    },
    ("edition_days", "identity_status"): {
        "provisional",
        "confirmed",
        "ambiguous",
    },
    ("page_assessments", "assessment_level"): {
        "screening",
        "substantive",
        "adjudication",
    },
    ("page_assessments", "result"): {
        "relevant",
        "not_relevant",
        "uncertain",
        "error",
        "not_assessed",
    },
    ("transcriptions", "purpose"): {
        "masthead",
        "candidate_content",
        "full_page",
        "recall_reference",
    },
    ("transcriptions", "result_status"): {"ok", "empty", "error"},
    ("date_records", "status"): {"observed", "imputed", "unresolved"},
}


def contract_checks(conn: sqlite3.Connection) -> None:
    table_count = int(
        conn.execute(
            """
            SELECT count(*) FROM sqlite_schema
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """
        ).fetchone()[0]
    )
    if table_count != 44:
        raise AssertionError(f"schema: esperadas 44 tabelas, obtidas {table_count}")
    if int(conn.execute("PRAGMA user_version").fetchone()[0]) != 2:
        raise AssertionError("schema não migrado para user_version 2")
    if int(conn.execute("PRAGMA foreign_keys").fetchone()[0]) != 1:
        raise AssertionError("PRAGMA foreign_keys está desativado")

    foreign_key_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_errors:
        raise AssertionError(f"FKs inválidas: {foreign_key_errors!r}")
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise AssertionError(f"integrity_check: {integrity}")

    for (table, column), allowed in ENUMS.items():
        values = {
            row[0]
            for row in conn.execute(
                f"SELECT DISTINCT {column} FROM {table}"
            ).fetchall()
        }
        invalid = values - allowed
        if invalid:
            raise AssertionError(
                f"enum inválido em {table}.{column}: {sorted(invalid)}"
            )

    conn.execute("SAVEPOINT enum_contract")
    try:
        conn.execute(
            """
            INSERT INTO protocols(
                stage, name, version, executor_type, code_commit,
                parameters_json, created_at
            ) VALUES (
                'valor_invalido', '__contract__', '1',
                'deterministic', 'contract', '{}', ?
            )
            """,
            (now(),),
        )
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("CHECK de enum não rejeitou valor inválido")
    finally:
        conn.execute("ROLLBACK TO enum_contract")
        conn.execute("RELEASE enum_contract")

    mismatched_pages = conn.execute(
        """
        SELECT o.source_identifier, f.page_count, count(p.id)
        FROM current_object_fetches AS current
        JOIN object_fetches AS f ON f.id = current.fetch_id
        JOIN digital_objects AS o ON o.id = current.object_id
        LEFT JOIN physical_pages AS p ON p.object_id = o.id
        WHERE f.result = 'ok'
        GROUP BY o.id, f.id
        HAVING count(p.id) <> f.page_count
        """
    ).fetchall()
    if mismatched_pages:
        raise AssertionError(f"contagem de páginas divergente: {mismatched_pages!r}")

    pages_without_assessment = int(
        conn.execute(
            """
            SELECT count(*) FROM physical_pages AS page
            WHERE NOT EXISTS (
                SELECT 1 FROM current_page_assessments AS current
                WHERE current.page_id = page.id
                  AND current.assessment_level = 'screening'
            )
            """
        ).fetchone()[0]
    )
    if pages_without_assessment:
        raise AssertionError(
            f"{pages_without_assessment} páginas sem avaliação vigente"
        )

    invalid_transcription_inputs = int(
        conn.execute(
            """
            SELECT count(*)
            FROM transcriptions AS transcription
            JOIN physical_pages AS page ON page.id = transcription.page_id
            WHERE transcription.input_visual_sha256 <> page.visual_sha256
            """
        ).fetchone()[0]
    )
    if invalid_transcription_inputs:
        raise AssertionError(
            f"{invalid_transcription_inputs} transcrições com hash visual divergente"
        )
    for row in conn.execute(
        """
        SELECT id, transcript_text, transcript_sha256
        FROM transcriptions WHERE result_status='ok'
        """
    ):
        if sha256_text(row["transcript_text"]) != row["transcript_sha256"]:
            raise AssertionError(
                f"hash textual divergente na transcrição {row['id']}"
            )

    invalid_observed_dates = int(
        conn.execute(
            """
            SELECT count(*) FROM date_records
            WHERE status='observed' AND (
                date_literal IS NULL OR evidence_page_id IS NULL
                OR evidence_region_json IS NULL
            )
            """
        ).fetchone()[0]
    )
    if invalid_observed_dates:
        raise AssertionError(
            f"{invalid_observed_dates} datas observadas sem evidência completa"
        )


def coverage_report(
    conn: sqlite3.Connection,
    *,
    artifacts: list[Artifact],
    unmatched_transcriptions: int,
) -> CoverageReport:
    digital_objects = int(
        conn.execute("SELECT count(*) FROM digital_objects").fetchone()[0]
    )
    editions = int(conn.execute("SELECT count(*) FROM edition_days").fetchone()[0])
    physical_pages = int(
        conn.execute("SELECT count(*) FROM physical_pages").fetchone()[0]
    )
    transcriptions = int(
        conn.execute("SELECT count(*) FROM transcriptions").fetchone()[0]
    )
    observed_dates = int(
        conn.execute(
            """
            SELECT count(*) FROM current_edition_dates AS current
            JOIN date_records AS record ON record.id = current.date_record_id
            WHERE record.status='observed'
            """
        ).fetchone()[0]
    )
    imputed_dates = int(
        conn.execute(
            """
            SELECT count(*) FROM current_edition_dates AS current
            JOIN date_records AS record ON record.id = current.date_record_id
            WHERE record.status='imputed'
            """
        ).fetchone()[0]
    )
    unresolved_dates = int(
        conn.execute(
            """
            SELECT count(*) FROM current_edition_dates AS current
            JOIN date_records AS record ON record.id = current.date_record_id
            WHERE record.status='unresolved'
            """
        ).fetchone()[0]
    )
    assessment_results = tuple(
        (row["assessment_level"], row["result"], int(row["total"]))
        for row in conn.execute(
            """
            SELECT current.assessment_level, assessment.result, count(*) AS total
            FROM current_page_assessments AS current
            JOIN page_assessments AS assessment
              ON assessment.id = current.assessment_id
            GROUP BY current.assessment_level, assessment.result
            ORDER BY current.assessment_level, assessment.result
            """
        )
    )
    return CoverageReport(
        canonical_pdfs=len(artifacts),
        digital_objects=digital_objects,
        editions=editions,
        physical_pages=physical_pages,
        transcriptions=transcriptions,
        observed_dates=observed_dates,
        imputed_dates=imputed_dates,
        unresolved_dates=unresolved_dates,
        editions_without_date_pointer=(
            editions - observed_dates - imputed_dates - unresolved_dates
        ),
        unmatched_transcriptions=unmatched_transcriptions,
        assessment_results=assessment_results,
    )


def print_report(report: CoverageReport) -> None:
    print("\nRelatório de cobertura do piloto")
    print(f"  PDFs canônicos: {report.canonical_pdfs}")
    print(f"  Objetos digitais: {report.digital_objects}")
    print(f"  Edições lógicas: {report.editions}")
    print(f"  Páginas físicas: {report.physical_pages}")
    print(f"  Transcrições de página: {report.transcriptions}")
    print(f"  Datas observadas: {report.observed_dates}")
    print(f"  Datas imputadas: {report.imputed_dates}")
    print(f"  Datas não resolvidas: {report.unresolved_dates}")
    print(
        "  Edições sem ponteiro de data: "
        f"{report.editions_without_date_pointer}"
    )
    print(f"  TXT sem PDF canônico: {report.unmatched_transcriptions}")
    print("  Avaliações vigentes:")
    for level, result, total in report.assessment_results:
        print(f"    {level}/{result}: {total}")
    print("  Estadão: fora do escopo analítico desta carga.")


def load(
    database: Path,
    *,
    repo_root: Path | None = None,
) -> CoverageReport:
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    artifacts = discover_artifacts(root)
    if not artifacts:
        raise RuntimeError("nenhum PDF canônico encontrado para o piloto")
    audit_path = date_audit.manifest_path(root)
    audit_manifest = date_audit.load_manifest(
        audit_path,
        [artifact_evidence(artifact) for artifact in artifacts],
    )
    artifacts = attach_date_audit(artifacts, audit_manifest)
    unmatched = find_unmatched_sources(root, artifacts)
    unmatched_transcriptions = sum(path.suffix == ".txt" for path in unmatched)
    _, _, analysis_root = source_paths(root)

    timestamp = now()
    commit = git_commit(root)
    scope_hash = manifest_sha256(artifacts, root)
    total_pages = sum(artifact.page_count for artifact in artifacts)
    transcribed_pages = sum(len(artifact.pages_text) for artifact in artifacts)

    conn = base_db.connect(database)
    try:
        with base_db.transaction(conn):
            newspaper_ids = {
                bib: base_db.upsert_newspaper(
                    conn,
                    **metadata,
                    created_at=timestamp,
                )
                for bib, metadata in NEWSPAPERS.items()
            }
            inventory_protocol = base_db.upsert_protocol(
                conn,
                stage="inventory",
                name="piloto_1906_pdf_local_import",
                version="1.0.0",
                executor_type="deterministic",
                code_commit=commit,
                parameters={
                    "pdf_root": "dados/raw_pdf/piloto_1906/data_tests",
                    "source_url_template": (
                        "https://hemeroteca-pdf.bn.gov.br/"
                        "{bib}/per{bib}_{year}_{number}.pdf"
                    ),
                    "outside_scope_newspapers": ["estadao"],
                },
                created_at=timestamp,
            )
            initial_protocol = base_db.upsert_protocol(
                conn,
                stage="identification",
                name="initial_not_assessed",
                version="1.0.0",
                executor_type="deterministic",
                code_commit=commit,
                parameters={"result": "not_assessed"},
                created_at=timestamp,
            )
            legacy_analysis_protocol = base_db.upsert_protocol(
                conn,
                stage="identification",
                name="legacy_article_analysis_import",
                version="1.0.0",
                executor_type="external_service",
                code_commit=commit,
                parameters={
                    "source": "dados/piloto_1906/analises_json",
                    "legacy_model_alias": "gemini-1.5-pro-latest",
                    "exact_provider_model_version": None,
                    "aggregation_unit": "physical_page",
                    "warning": (
                        "A fonte legada preserva apenas um alias de modelo. "
                        "Esta operação importa resultados existentes."
                    ),
                },
                created_at=timestamp,
            )
            transcription_protocol = base_db.upsert_protocol(
                conn,
                stage="transcription",
                name="legacy_page_transcription_import",
                version="1.0.0",
                executor_type="external_service",
                code_commit=commit,
                parameters={
                    "source": "dados/piloto_1906/data_processed",
                    "format": "PAGE/PAGE_METADATA/ARTICLE markers",
                    "visual_hash_granularity": (
                        "Hash do PDF contêiner; page_id identifica a página."
                    ),
                },
                created_at=timestamp,
            )
            date_protocol = base_db.upsert_protocol(
                conn,
                stage="date_parsing",
                name="masthead_pt_regex",
                version="1.0.0",
                executor_type="deterministic",
                code_commit=commit,
                parameters={
                    "source_marker": "PAGE_METADATA",
                    "accepted_year": 1906,
                    "months": MONTHS,
                },
                created_at=timestamp,
            )
            visual_date_protocol = base_db.upsert_protocol(
                conn,
                stage="date_parsing",
                name="masthead_visual_manifest",
                version="1.0.0",
                executor_type="external_service",
                code_commit=commit,
                parameters={
                    "manifest_path": audit_manifest.relative_path,
                    "manifest_sha256": audit_manifest.file_sha256,
                    "schema_version": audit_manifest.schema_version,
                    "verification_method": audit_manifest.verification_method,
                    "reviewer_type": audit_manifest.reviewer_type,
                    "reviewer_label": audit_manifest.reviewer_label,
                    "independent_human_review": (
                        audit_manifest.independent_human_review
                    ),
                },
                created_at=timestamp,
            )
            population_protocol = base_db.upsert_protocol(
                conn,
                stage="circulation",
                name="piloto_1906_available_pdf_population",
                version="1.0.0",
                executor_type="deterministic",
                code_commit=commit,
                parameters={
                    "eligibility": "PDF canônico disponível e data observada",
                    "estadao": "fora de escopo",
                },
                created_at=timestamp,
            )
            population_id = base_db.upsert_population_definition(
                conn,
                name="piloto_1906_available_pdf",
                version="1.0.0",
                unit_mode="strict_newspaper_day",
                description=(
                    "Edições do piloto com PDF canônico local e data observada."
                ),
                protocol_id=population_protocol,
                created_at=timestamp,
            )

            initial_run_id = get_or_create_run(
                conn,
                table="identification_runs",
                protocol_id=initial_protocol,
                scope_hash=scope_hash,
                submitted=total_pages,
                completed=total_pages,
                timestamp=timestamp,
            )
            legacy_run_id = get_or_create_run(
                conn,
                table="identification_runs",
                protocol_id=legacy_analysis_protocol,
                scope_hash=scope_hash,
                submitted=transcribed_pages,
                completed=transcribed_pages,
                timestamp=timestamp,
            )
            transcription_run_id = get_or_create_run(
                conn,
                table="transcription_runs",
                protocol_id=transcription_protocol,
                scope_hash=scope_hash,
                submitted=transcribed_pages,
                completed=transcribed_pages,
                timestamp=timestamp,
            )

            for artifact in artifacts:
                newspaper_id = newspaper_ids.get(artifact.bib)
                if newspaper_id is None:
                    raise ValueError(f"BIB desconhecido: {artifact.bib}")
                object_id = base_db.upsert_digital_object(
                    conn,
                    newspaper_id=newspaper_id,
                    source_identifier=artifact.stem,
                    source_url=(
                        f"https://hemeroteca-pdf.bn.gov.br/{artifact.bib}/"
                        f"{artifact.stem}.pdf"
                    ),
                    source_year=artifact.year,
                    bn_file_key=f"{artifact.bib}/{artifact.stem}.pdf",
                    bn_file_number_literal=artifact.file_number,
                    discovered_by_protocol_id=inventory_protocol,
                    discovered_at=timestamp,
                )
                fetch_id = current_fetch(
                    conn,
                    object_id=object_id,
                    pdf_sha256=artifact.pdf_sha256,
                    storage_path=artifact.relative_pdf_path,
                )
                if fetch_id is None:
                    fetch_id = base_db.mark_download_status(
                        conn,
                        object_id=object_id,
                        result="ok",
                        attempted_at=timestamp,
                        fetch_mode="local_import",
                        completed_at=timestamp,
                        http_status=None,
                        storage_path=artifact.relative_pdf_path,
                        pdf_sha256=artifact.pdf_sha256,
                        response_sha256=None,
                        byte_count=artifact.byte_count,
                        page_count=artifact.page_count,
                        make_current=False,
                    )
                conn.execute(
                    """
                    INSERT INTO current_object_fetches(
                        object_id, fetch_id, selected_at
                    ) VALUES (?, ?, ?)
                    ON CONFLICT(object_id) DO UPDATE SET
                        fetch_id = excluded.fetch_id,
                        selected_at = excluded.selected_at
                    """,
                    (object_id, fetch_id, timestamp),
                )

                edition_id = upsert_edition(
                    conn,
                    newspaper_id=newspaper_id,
                    logical_key=artifact.stem,
                    confirmed=artifact.observed_date is not None,
                    timestamp=timestamp,
                )
                conn.execute(
                    """
                    INSERT OR IGNORE INTO edition_object_links(
                        edition_day_id, object_id, link_role,
                        include_in_content, protocol_id, linked_at
                    ) VALUES (?, ?, 'principal', 1, ?, ?)
                    """,
                    (edition_id, object_id, inventory_protocol, timestamp),
                )
                ensure_identifier(
                    conn,
                    edition_id=edition_id,
                    literal_value=artifact.file_number,
                    normalized_value=artifact.file_number.lstrip("0") or "0",
                    protocol_id=inventory_protocol,
                    timestamp=timestamp,
                )

                page_ids: dict[int, int] = {}
                transcription_ids: dict[int, int] = {}
                for page_number in range(1, artifact.page_count + 1):
                    page_id = upsert_page(
                        conn,
                        object_id=object_id,
                        page_number=page_number,
                        pdf_path=artifact.relative_pdf_path,
                        pdf_sha256=artifact.pdf_sha256,
                        timestamp=timestamp,
                    )
                    page_ids[page_number] = page_id
                    initial_raw = json.dumps(
                        {
                            "source": "initial_materialization",
                            "page_number": page_number,
                            "result": "not_assessed",
                        },
                        sort_keys=True,
                    )
                    ensure_assessment(
                        conn,
                        page_id=page_id,
                        run_id=initial_run_id,
                        level="screening",
                        result="not_assessed",
                        raw_text=initial_raw,
                        rationale="Avaliação inicial obrigatória da página.",
                        evidence_json=None,
                        confidence=None,
                        timestamp=timestamp,
                    )

                    page_text = artifact.pages_text.get(page_number)
                    if page_text is None or artifact.txt_path is None:
                        continue
                    source_path = relative(artifact.txt_path, root)
                    transcription_ids[page_number] = ensure_transcription(
                        conn,
                        page_id=page_id,
                        run_id=transcription_run_id,
                        visual_sha256=artifact.pdf_sha256,
                        page=page_text,
                        source_path=source_path,
                        timestamp=timestamp,
                    )
                    if page_text.article_ordinals:
                        result, raw, rationale, confidence = page_analysis(
                            artifact,
                            page_text,
                            analysis_root=analysis_root,
                            repo_root=root,
                        )
                        ensure_assessment(
                            conn,
                            page_id=page_id,
                            run_id=legacy_run_id,
                            level="substantive",
                            result=result,
                            raw_text=raw,
                            rationale=rationale,
                            evidence_json=json.dumps(
                                {"article_ordinals": page_text.article_ordinals},
                                sort_keys=True,
                            ),
                            confidence=confidence,
                            timestamp=timestamp,
                        )

                ocr_record_id: int | None = None
                ocr = artifact.ocr_observed_date
                if (
                    ocr is not None
                    and artifact.txt_path is not None
                    and ocr.page_number in page_ids
                    and ocr.page_number in transcription_ids
                ):
                    ocr_record_id = ensure_date_record(
                        conn,
                        edition_id=edition_id,
                        protocol_id=date_protocol,
                        observed=ocr,
                        page_id=page_ids[ocr.page_number],
                        transcription_id=transcription_ids[ocr.page_number],
                        evidence={
                            "source_txt": relative(artifact.txt_path, root),
                            "marker": "PAGE_METADATA",
                            "page_number": ocr.page_number,
                        },
                        parser_name="masthead_pt_regex",
                        parser_version="1.0.0",
                        notes="Data extraída literalmente de PAGE_METADATA.",
                        timestamp=timestamp,
                    )

                selected_record_id = ocr_record_id
                selected_date = ocr
                audit = artifact.audit_record
                if audit is not None:
                    visual = artifact.observed_date
                    assert visual is not None
                    visual_record_id = ensure_date_record(
                        conn,
                        edition_id=edition_id,
                        protocol_id=visual_date_protocol,
                        observed=visual,
                        page_id=page_ids[visual.page_number],
                        transcription_id=None,
                        evidence={
                            "source_pdf": audit.pdf_path,
                            "pdf_sha256": audit.pdf_sha256,
                            "page_number": audit.page_number,
                            "region": audit.evidence_region,
                            "manifest_path": audit_manifest.relative_path,
                            "manifest_sha256": audit_manifest.file_sha256,
                        },
                        parser_name="masthead_visual_manifest",
                        parser_version="1.0.0",
                        notes=(
                            f"{audit.notes} Revisão ai_assisted_visual_review; "
                            "sem revisão humana independente."
                        ),
                        timestamp=timestamp,
                    )
                    selected_record_id = visual_record_id
                    selected_date = visual

                if selected_record_id is not None and selected_date is not None:
                    select_current_date(
                        conn,
                        edition_id=edition_id,
                        record_id=selected_record_id,
                        timestamp=timestamp,
                    )
                    calendar_day_id = base_db.upsert_calendar_day(
                        conn,
                        newspaper_id=newspaper_id,
                        civil_date=selected_date.normalized,
                        created_at=timestamp,
                    )
                    base_db.upsert_population_membership(
                        conn,
                        population_definition_id=population_id,
                        calendar_day_id=calendar_day_id,
                        edition_day_id=edition_id,
                        eligibility="eligible",
                        reason="PDF canônico disponível e data observada.",
                        assigned_at=timestamp,
                    )
                else:
                    masthead_page_id = page_ids.get(1)
                    if masthead_page_id is not None:
                        unresolved_record_id = register_unresolved_date(
                            conn,
                            edition_id=edition_id,
                            protocol_id=date_protocol,
                            page_id=masthead_page_id,
                            parser_name="masthead_pt_regex",
                            parser_version="1.0.0",
                            evidence={
                                "source": "masthead",
                                "page_number": 1,
                                "reason": "nenhuma data normalizavel no masthead",
                            },
                            notes=(
                                "Masthead sem data normalizavel; registro "
                                "positivo de falha de parse (achado B)."
                            ),
                            timestamp=timestamp,
                            transcription_id=transcription_ids.get(1),
                        )
                        select_current_date(
                            conn,
                            edition_id=edition_id,
                            record_id=unresolved_record_id,
                            timestamp=timestamp,
                        )

        contract_checks(conn)
        report = coverage_report(
            conn,
            artifacts=artifacts,
            unmatched_transcriptions=unmatched_transcriptions,
        )
        return report
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Carrega o piloto canônico de 1906 na base v2"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=base_db.DEFAULT_DATABASE,
        help="Banco SQLite de destino",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Raiz do repositório com as fontes canônicas",
    )
    arguments = parser.parse_args()
    report = load(arguments.db.resolve(), repo_root=arguments.repo_root.resolve())
    print_report(report)
    print("\nContract checks: OK")


if __name__ == "__main__":
    main()
