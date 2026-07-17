# Auditoria Visual das Datas de 1906 - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Incorporar 27 datas conferidas visualmente, preservar cinco candidatos incorretos do OCR no histórico e produzir 67 datas vigentes observadas, distintas e sem imputação.

**Architecture:** Um módulo isolado valida um manifesto JSON ligado aos hashes dos PDFs. O carregador mantém separadas a leitura do OCR e a leitura visual, grava ambas em `date_records` quando necessário e seleciona explicitamente o registro visual em `current_edition_dates`.

**Tech Stack:** Python 3.12, biblioteca padrão (`dataclasses`, `datetime`, `hashlib`, `json`, `pathlib`, `sqlite3`, `unittest`) e SQLite 3 via `uv run`.

## Global Constraints

- O manifesto contém exatamente 27 registros e usa `schema_version = 1`.
- A evidência é o PDF canônico local identificado por caminho, SHA-256 e página 1.
- A sequência do número da edição é somente controle de qualidade; nunca cria datas.
- As 27 datas têm `status = observed`; nenhuma data é imputada.
- A auditoria é descrita como `ai_assisted_visual_review`, com `independent_human_review = false`.
- Os cinco candidatos errados do OCR permanecem em `date_records`, mas não ficam vigentes.
- PDFs, bancos SQLite e imagens temporárias nunca entram no Git.
- Não adicionar dependências; usar somente a biblioteca padrão já adotada.
- Cada tarefa termina com teste e checkpoint. Executar somente uma tarefa por vez para limitar contexto e risco de interrupção.
- Especificação normativa: `docs/superpowers/specs/2026-07-16-auditoria-visual-datas-1906-design.md`.

## File Map

- Create `pipeline/base/date_audit.py`: tipos, leitura e validação estrita do manifesto.
- Create `pipeline/base/manifests/datas_masthead_1906.json`: 27 decisões auditadas.
- Create `tests/test_date_audit.py`: contrato do manifesto e erros de evidência.
- Modify `pipeline/base/carrega_piloto.py`: candidatos separados, precedência, protocolos e persistência histórica.
- Modify `tests/test_carrega_piloto.py`: descoberta, correções, cardinalidades e idempotência.
- Modify `docs/relatorio-carga-piloto-1906.md`: cobertura final e transparência da auditoria.
- Modify `docs/handoff-2026-07-16-base-corpus.md`: estado operacional e próximo portão.

## Checkpoint Protocol

Depois de cada tarefa:

1. executar somente os testes indicados;
2. executar `git diff --check` nos arquivos da tarefa;
3. revisar o diff sem incluir a especificação v1 não rastreada;
4. criar o commit indicado;
5. informar resultado, hash do commit e próximo checkpoint;
6. parar se houver falha não explicada ou se o orçamento de contexto estiver baixo.

---

### Task 1: Manifesto e validador isolado

**Files:**
- Create: `pipeline/base/date_audit.py`
- Create: `pipeline/base/manifests/datas_masthead_1906.json`
- Create: `tests/test_date_audit.py`

**Interfaces:**
- Consumes: PDFs descritos no Apêndice A e seus hashes já calculados.
- Produces: `ArtifactEvidence`, `DateAuditRecord`, `DateAuditManifest`, `manifest_path(repo_root)` e `load_manifest(path, artifacts)`.

- [ ] **Step 1: Escrever os testes falhos do contrato**

Criar `tests/test_date_audit.py` com helpers que constroem evidências reais e cópias mutáveis do JSON:

```python
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
```

- [ ] **Step 2: Executar os testes e confirmar a falha esperada**

Run:

```powershell
uv run python -m unittest tests.test_date_audit -v
```

Expected: FAIL ao importar `pipeline.base.date_audit`.

- [ ] **Step 3: Criar os tipos e o validador mínimo**

Criar `pipeline/base/date_audit.py` com estas interfaces e validações explícitas:

```python
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
    "schema_version", "audit_id", "audited_at", "newspaper_bib",
    "source_year", "verification_method", "reviewer_type",
    "reviewer_label", "independent_human_review", "records",
}
RECORD_KEYS = {
    "source_identifier", "normalized_date", "date_literal", "pdf_path",
    "pdf_sha256", "page_number", "evidence_region", "decision",
    "previous_ocr_date", "notes",
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


def _exact_keys(payload: dict[str, object], expected: set[str], context: str) -> None:
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
        raise ValueError(f"schema_version desconhecido: {payload['schema_version']!r}")
    audit_id = _nonempty_text(payload["audit_id"], "audit_id")
    audited_at = _nonempty_text(payload["audited_at"], "audited_at")
    try:
        date.fromisoformat(audited_at)
    except ValueError as error:
        raise ValueError(f"audited_at: data ISO inválida: {audited_at!r}") from error
    reviewer_label = _nonempty_text(payload["reviewer_label"], "reviewer_label")
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
        if not isinstance(source_identifier, str) or not IDENTIFIER_RE.fullmatch(source_identifier):
            raise ValueError(f"records[{index}].source_identifier inválido")
        if source_identifier in seen:
            raise ValueError(f"source_identifier duplicado: {source_identifier}")
        seen.add(source_identifier)
        artifact = evidence.get(source_identifier)
        if artifact is None:
            raise ValueError(f"artefato desconhecido: {source_identifier}")
        normalized_date = _iso_1906(item["normalized_date"], "normalized_date")
        decision = item["decision"]
        previous = item["previous_ocr_date"]
        if decision not in {"fill_missing_ocr", "correct_ocr"}:
            raise ValueError(f"decision inválida: {decision!r}")
        if decision == "fill_missing_ocr" and previous is not None:
            raise ValueError("previous_ocr_date deve ser null em fill_missing_ocr")
        if decision == "correct_ocr":
            previous = _iso_1906(previous, "previous_ocr_date")
            if previous == normalized_date:
                raise ValueError("previous_ocr_date deve divergir da correção")
        pdf_path = item["pdf_path"]
        pdf_sha256 = item["pdf_sha256"]
        page_number = item["page_number"]
        if pdf_path != artifact.pdf_path:
            raise ValueError(f"{source_identifier}: pdf_path divergente")
        if not isinstance(pdf_sha256, str) or not SHA256_RE.fullmatch(pdf_sha256):
            raise ValueError(f"{source_identifier}: pdf_sha256 inválido")
        if pdf_sha256 != artifact.pdf_sha256:
            raise ValueError(f"{source_identifier}: pdf_sha256 divergente")
        if not isinstance(page_number, int) or not 1 <= page_number <= artifact.page_count:
            raise ValueError(f"{source_identifier}: page_number inexistente")
        if artifact.source_year != 1906:
            raise ValueError(f"{source_identifier}: artefato fora de 1906")
        if item["evidence_region"] != "masthead":
            raise ValueError(f"{source_identifier}: evidence_region inválida")
        if not isinstance(item["date_literal"], str) or not item["date_literal"].strip():
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
```

Durante a implementação, manter as validações acima em helpers menores se isso reduzir o tamanho da função, sem alterar as assinaturas públicas.

- [ ] **Step 4: Criar o manifesto com os 27 registros exatos**

Criar `pipeline/base/manifests/datas_masthead_1906.json` com a raiz:

```json
{
  "schema_version": 1,
  "audit_id": "o-paiz-1906-masthead-2026-07-16",
  "audited_at": "2026-07-16",
  "newspaper_bib": "178691",
  "source_year": 1906,
  "verification_method": "visual_masthead",
  "reviewer_type": "ai_assisted_visual_review",
  "reviewer_label": "Codex",
  "independent_human_review": false,
  "records": []
}
```

Substituir a lista vazia pelos 27 registros do Apêndice A. Cada registro segue este formato exato:

```json
{
  "source_identifier": "per178691_1906_07890",
  "normalized_date": "1906-05-11",
  "date_literal": "RIO DE JANEIRO, Sexta-feira 11 de Maio de 1906",
  "pdf_path": "dados/raw_pdf/piloto_1906/data_tests/per178691_1906_07890.pdf",
  "pdf_sha256": "5183f46b24d27865f89135b0190894eabba2e1e618cf384c19db417908f16232",
  "page_number": 1,
  "evidence_region": "masthead",
  "decision": "fill_missing_ocr",
  "previous_ocr_date": null,
  "notes": "Masthead conferido visualmente na página 1."
}
```

Para `correct_ocr`, usar o valor do Apêndice A em `previous_ocr_date` e a nota `Corrige candidato aceito pelo OCR legado.`.

- [ ] **Step 5: Executar testes do módulo**

Run:

```powershell
uv run python -m unittest tests.test_date_audit -v
```

Expected: 6 testes PASS.

- [ ] **Step 6: Verificar e commitar o checkpoint**

Run:

```powershell
git diff --check -- pipeline/base/date_audit.py pipeline/base/manifests/datas_masthead_1906.json tests/test_date_audit.py
git add -- pipeline/base/date_audit.py pipeline/base/manifests/datas_masthead_1906.json tests/test_date_audit.py
git commit -m "feat: adiciona manifesto auditável de datas"
```

Expected: commit contém somente os três arquivos desta tarefa.

**STOP CHECKPOINT 1:** reportar testes, commit e qualquer diferença entre plano e implementação.

---

### Task 2: Separar OCR, auditoria e data vigente no artefato

**Files:**
- Modify: `pipeline/base/carrega_piloto.py:10-125,297-365`
- Modify: `tests/test_carrega_piloto.py:141-165`

**Interfaces:**
- Consumes: `date_audit.DateAuditManifest` e `date_audit.DateAuditRecord` da Task 1.
- Produces: `Artifact.ocr_observed_date`, `Artifact.audit_record`, propriedade `Artifact.observed_date`, `artifact_evidence()` e `attach_date_audit()`.

- [ ] **Step 1: Escrever testes falhos de precedência**

Acrescentar a `PilotDiscoveryTests`:

```python
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
```

Adicionar `from dataclasses import replace` e
`from pipeline.base import date_audit` no topo do teste.

- [ ] **Step 2: Executar e confirmar a falha**

Run:

```powershell
uv run python -m unittest tests.test_carrega_piloto.PilotDiscoveryTests -v
```

Expected: FAIL porque `Artifact` ainda não separa as duas fontes.

- [ ] **Step 3: Alterar o modelo do artefato**

Em `pipeline/base/carrega_piloto.py`, importar `replace` e `date_audit`:

```python
from dataclasses import dataclass, replace
from pipeline.base import date_audit
```

Substituir o último campo atual de `Artifact` por:

```python
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
```

Em `discover_artifacts`, trocar o argumento de construção:

```python
                ocr_observed_date=observed_date_from_pages(pages),
```

Adicionar funções puras depois de `discover_artifacts`:

```python
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
```

Não chamar `attach_date_audit` dentro de `load()` nesta tarefa. O comportamento operacional somente muda junto com a proveniência da Task 3.

- [ ] **Step 4: Executar testes direcionados e regressão do parser**

Run:

```powershell
uv run python -m unittest tests.test_carrega_piloto.PilotDiscoveryTests tests.test_carrega_piloto.PilotParserTests -v
```

Expected: PASS; os quatro testes novos confirmam precedência, coerência histórica
e ausência de imputação implícita.

- [ ] **Step 5: Verificar e commitar o checkpoint**

Run:

```powershell
git diff --check -- pipeline/base/carrega_piloto.py tests/test_carrega_piloto.py
git add -- pipeline/base/carrega_piloto.py tests/test_carrega_piloto.py
git commit -m "refactor: separa fontes de data do piloto"
```

**STOP CHECKPOINT 2:** reportar testes e commit. Não iniciar persistência no mesmo checkpoint.

---

### Task 3: Persistir histórico e selecionar a data visual

**Files:**
- Modify: `pipeline/base/carrega_piloto.py:850-930,1195-1535`
- Modify: `tests/test_carrega_piloto.py:166-238`

**Interfaces:**
- Consumes: `Artifact.observed_date`, `Artifact.ocr_observed_date`, `Artifact.audit_record` e `DateAuditManifest.file_sha256`.
- Produces: `ensure_date_record(...) -> int`, `select_current_date(...) -> None`, protocolo `masthead_visual_manifest/1.0.0` e banco com 72 registros históricos/67 vigentes.

- [ ] **Step 1: Atualizar o teste de carga para o resultado final**

No teste `test_load_materializa_piloto_real_e_e_idempotente`, alterar:

```python
            self.assertEqual(67, first.observed_dates)
            self.assertEqual(0, first.imputed_dates)
            self.assertEqual(0, first.unresolved_dates)
```

Adicionar `import json` no topo de `tests/test_carrega_piloto.py`.

Alterar a cardinalidade esperada de `date_records` para `72` e acrescentar:

```python
            self.assertEqual(
                67,
                conn.execute("SELECT count(*) FROM current_edition_dates").fetchone()[0],
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
```

Acrescentar um helper SQL no teste para validar as cinco correções:

```python
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
```

- [ ] **Step 2: Executar e confirmar a falha de integração**

Run:

```powershell
uv run python -m unittest tests.test_carrega_piloto.PilotLoadTests -v
```

Expected: FAIL com 45 datas observadas em vez de 67.

- [ ] **Step 3: Tornar a inserção histórica independente da seleção vigente**

Refatorar `ensure_date_record` para esta assinatura:

```python
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
```

A função retorna o registro histórico sem alterar `current_edition_dates`.

Extrair a seleção atual para:

```python
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
```

- [ ] **Step 4: Carregar e versionar o protocolo visual antes da transação**

Logo após `discover_artifacts(root)` em `load()`:

```python
    audit_path = date_audit.manifest_path(root)
    audit_manifest = date_audit.load_manifest(
        audit_path,
        [artifact_evidence(artifact) for artifact in artifacts],
    )
    artifacts = attach_date_audit(artifacts, audit_manifest)
```

Depois do protocolo regex, criar:

```python
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
```

- [ ] **Step 5: Inserir candidatos e escolher a fonte vigente**

Substituir o bloco único de data por esta ordem lógica:

```python
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
```

Manter `confirmed=artifact.observed_date is not None` na criação da edição; depois de anexar o manifesto isso confirma as 67 edições.

- [ ] **Step 6: Executar integração, idempotência e suíte completa**

Run:

```powershell
uv run python -m unittest tests.test_carrega_piloto.PilotLoadTests -v
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q pipeline/base tests
```

Expected: carga executada duas vezes sem alterar cardinalidades; todos os testes PASS; compilação sem saída.

- [ ] **Step 7: Verificar e commitar o checkpoint**

Run:

```powershell
git diff --check -- pipeline/base/carrega_piloto.py tests/test_carrega_piloto.py
git add -- pipeline/base/carrega_piloto.py tests/test_carrega_piloto.py
git commit -m "feat: preserva histórico e seleciona datas auditadas"
```

**STOP CHECKPOINT 3:** reportar 72 registros históricos, 67 vigentes, testes e commit.

---

### Task 4: Atualizar relatório e handoff

**Files:**
- Modify: `docs/relatorio-carga-piloto-1906.md`
- Modify: `docs/handoff-2026-07-16-base-corpus.md`

**Interfaces:**
- Consumes: resultados verificados da Task 3.
- Produces: documentação coerente com 67 datas observadas e transparência da revisão assistida.

- [ ] **Step 1: Atualizar as cardinalidades e divergências**

No relatório, substituir a cobertura de datas por:

```markdown
| Datas observadas vigentes | 67 |
| Datas imputadas vigentes | 0 |
| Datas não resolvidas | 0 |
| Dias civis distintos | 67 |
| Registros históricos de data | 72 |
```

Substituir a pendência dos pares duplicados por uma seção que liste as cinco correções:

```markdown
- `07943`: `1906-07-05` -> `1906-07-03`;
- `07959`: `1906-07-10` -> `1906-07-19`;
- `08020`: `1906-09-08` -> `1906-09-18`;
- `08028`: `1906-09-20` -> `1906-09-26`;
- `08107`: `1906-12-08` -> `1906-12-14`.
```

Declarar que a auditoria foi assistida pelo Codex, não teve revisão humana independente e está vinculada ao manifesto e aos hashes dos PDFs.

- [ ] **Step 2: Atualizar o handoff**

Registrar no topo do handoff:

```markdown
O manifesto visual resolveu as 22 lacunas e corrigiu cinco candidatos do OCR.
A carga limpa agora produz 72 registros históricos, 67 datas vigentes observadas,
67 dias civis distintos, zero datas imputadas e zero datas não resolvidas.
A próxima revisão recomendada é humana e independente, por amostra ou pelos 27 casos.
```

- [ ] **Step 3: Executar a verificação completa antes do commit documental**

Run:

```powershell
uv run python -m unittest discover -s tests -v
git diff --check -- docs/relatorio-carga-piloto-1906.md docs/handoff-2026-07-16-base-corpus.md
```

Expected: todos os testes PASS e nenhum erro de whitespace.

- [ ] **Step 4: Commitar o checkpoint documental**

Run:

```powershell
git add -- docs/relatorio-carga-piloto-1906.md docs/handoff-2026-07-16-base-corpus.md
git commit -m "docs: registra auditoria visual das datas"
```

**STOP CHECKPOINT 4:** reportar diff documental, testes e commit.

---

### Task 5: Reconstruir e auditar os bancos operacionais

**Files:**
- Recreate ignored artifact: `dados/base/caixa_conversao_piloto_verificacao.db`
- Recreate ignored artifact: `dados/base/caixa_conversao.db`
- No tracked file changes expected.

**Interfaces:**
- Consumes: HEAD final das Tasks 1-4.
- Produces: dois bancos íntegros cuja proveniência aponta para o commit final.

- [ ] **Step 1: Confirmar estado e alvos exatos**

Run:

```powershell
git status --short --branch
git log -1 --oneline
Resolve-Path -LiteralPath 'dados\base'
Get-ChildItem -LiteralPath 'dados\base' -Force | Select-Object Name, Length
```

Expected: somente a especificação v1 antiga permanece não rastreada; os alvos estão dentro de `dados/base`.

- [ ] **Step 2: Remover somente os dois bancos reproduzíveis**

Run:

```powershell
$baseDir = (Resolve-Path -LiteralPath 'dados\base').Path
$targets = @(
    (Join-Path $baseDir 'caixa_conversao_piloto_verificacao.db'),
    (Join-Path $baseDir 'caixa_conversao.db')
)
foreach ($target in $targets) {
    if (-not $target.StartsWith(
        $baseDir + [IO.Path]::DirectorySeparatorChar,
        [StringComparison]::OrdinalIgnoreCase
    )) {
        throw "Alvo fora de dados/base: $target"
    }
    if (Test-Path -LiteralPath $target -PathType Leaf) {
        Remove-Item -LiteralPath $target -Force
    }
}
```

Não remover `dados/base` nem usar glob recursivo.

- [ ] **Step 3: Criar e repetir o banco de verificação**

Run duas vezes:

```powershell
uv run python pipeline/base/carrega_piloto.py --db dados/base/caixa_conversao_piloto_verificacao.db
```

Expected em ambas:

```text
PDFs canônicos: 67
Objetos digitais: 67
Edições lógicas: 67
Páginas físicas: 450
Transcrições de página: 102
Datas observadas: 67
Datas imputadas: 0
Datas não resolvidas: 0
Contract checks: OK
```

- [ ] **Step 4: Criar o banco operacional**

Run:

```powershell
uv run python pipeline/base/carrega_piloto.py --db dados/base/caixa_conversao.db
```

Expected: mesmas cardinalidades e contract checks.

- [ ] **Step 5: Auditar integridade, proveniência e cardinalidades**

Run:

```powershell
@'
import sqlite3
import subprocess
from pathlib import Path

head = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()
for path in (
    Path("dados/base/caixa_conversao_piloto_verificacao.db"),
    Path("dados/base/caixa_conversao.db"),
):
    conn = sqlite3.connect(path)
    assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM date_records").fetchone()[0] == 72
    assert conn.execute("SELECT count(*) FROM current_edition_dates").fetchone()[0] == 67
    assert conn.execute(
        """
        SELECT count(DISTINCT d.normalized_date)
        FROM current_edition_dates c
        JOIN date_records d ON d.id=c.date_record_id
        """
    ).fetchone()[0] == 67
    assert conn.execute(
        "SELECT count(*) FROM date_records WHERE status='imputed'"
    ).fetchone()[0] == 0
    assert {
        row[0] for row in conn.execute("SELECT DISTINCT code_commit FROM protocols")
    } == {head}
    assert conn.execute(
        "SELECT count(*) FROM object_fetches WHERE http_status IS NOT NULL"
    ).fetchone()[0] == 0
    print(path.name, "OK", head)
    conn.close()
'@ | uv run python -
```

Expected: duas linhas `OK` com o mesmo hash de `HEAD`.

- [ ] **Step 6: Verificação final do repositório**

Run:

```powershell
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q pipeline/base tests
git status --short --branch
git check-ignore -v dados/base/caixa_conversao.db dados/base/caixa_conversao_piloto_verificacao.db
```

Expected: todos os testes PASS; compilação limpa; bancos ignorados; somente a especificação v1 antiga não rastreada; nenhum push.

**STOP CHECKPOINT 5:** entregar resumo final, commits, cardinalidades e ressalva sobre revisão humana independente.

---

## Appendix A: Exact Audit Records

Cada linha fornece `source_identifier`, `normalized_date`, `date_literal`, `pdf_sha256`, `decision` e `previous_ocr_date`. O `pdf_path` é sempre `dados/raw_pdf/piloto_1906/data_tests/<source_identifier>.pdf`; `page_number` é `1`; `evidence_region` é `masthead`.

| source_identifier | normalized_date | date_literal | pdf_sha256 | decision | previous_ocr_date |
|---|---|---|---|---|---|
| `per178691_1906_07890` | `1906-05-11` | `RIO DE JANEIRO, Sexta-feira 11 de Maio de 1906` | `5183f46b24d27865f89135b0190894eabba2e1e618cf384c19db417908f16232` | `fill_missing_ocr` | `null` |
| `per178691_1906_07891` | `1906-05-12` | `RIO DE JANEIRO, Sabbado 12 de Maio de 1906` | `bdd9f4fe6f57872418330f7c9f642158a3f9fc6b4c2a9b26b3799f4388de26b4` | `fill_missing_ocr` | `null` |
| `per178691_1906_07892` | `1906-05-13` | `RIO DE JANEIRO, Domingo 13 de Maio de 1906` | `5818d9c89e786aa86a35fbc739ca2e1476949c2738c19fe38d5bbcc2c7c69986` | `fill_missing_ocr` | `null` |
| `per178691_1906_07943` | `1906-07-03` | `RIO DE JANEIRO, Terça-feira 3 de Julho de 1906` | `b53ccbd05469f9cf78dbdfd54052438f0e09e68673c9622a6e32c45203bafe05` | `correct_ocr` | `1906-07-05` |
| `per178691_1906_07958` | `1906-07-18` | `RIO DE JANEIRO, Quarta-feira 18 de Julho de 1906` | `0f34d649a979da77f872e26f497464891249fab1f2b8ffa8cc4a19ad8d2ae200` | `fill_missing_ocr` | `null` |
| `per178691_1906_07959` | `1906-07-19` | `RIO DE JANEIRO, Quinta-feira 19 de Julho de 1906` | `b92baec1d2539a301423d4b9d338d1feb3fc617b5b4a4611c21bc74cd09ac476` | `correct_ocr` | `1906-07-10` |
| `per178691_1906_07992` | `1906-08-21` | `RIO DE JANEIRO, Terça-feira 21 de Agosto de 1906` | `4b76d529fd05def75aeeb82a1ad055115d69d0c8fb7f1bb75ab98523aa98459a` | `fill_missing_ocr` | `null` |
| `per178691_1906_07997` | `1906-08-26` | `RIO DE JANEIRO, Domingo 26 de Agosto de 1906` | `d57ac642645496664e48e0bf6429c4c7e9fc6aff761d8277e8c12aaa0122157b` | `fill_missing_ocr` | `null` |
| `per178691_1906_08002` | `1906-08-31` | `RIO DE JANEIRO, Sexta-feira 31 de Agosto de 1906` | `a837d2f19a22c9180a97cfb43bcff2241a112101707d192f4ea21323ff31af50` | `fill_missing_ocr` | `null` |
| `per178691_1906_08003` | `1906-09-01` | `RIO DE JANEIRO, Sabbado 1 de Setembro de 1906` | `658a9a9c849297eb28f2442a2e7e63bbeb8abbfedf009bff2ccfdd49d3e40fc7` | `fill_missing_ocr` | `null` |
| `per178691_1906_08004` | `1906-09-02` | `RIO DE JANEIRO, Domingo 2 de Setembro de 1906` | `77ed0c82e88b0206414253e52eda6098519910c8758eeb7747ca37e11d587b51` | `fill_missing_ocr` | `null` |
| `per178691_1906_08006` | `1906-09-04` | `RIO DE JANEIRO, Terça-feira 4 de Setembro de 1906` | `32deb87d3fda13e68392e7e0218a1f9f1018b9ebaba9936c4f0ece70de05638a` | `fill_missing_ocr` | `null` |
| `per178691_1906_08020` | `1906-09-18` | `RIO DE JANEIRO, Terça-feira 18 de Setembro de 1906` | `c3877d2e8be03f6e53f26a598e10a0e21187dbbcc9c0c6787cfe676a7138fc2e` | `correct_ocr` | `1906-09-08` |
| `per178691_1906_08025` | `1906-09-23` | `RIO DE JANEIRO, Domingo 23 de Setembro de 1906` | `075f5e3acdb3268975b10ea6c98e707f989d5bf04d1c33d095c06c38dade6062` | `fill_missing_ocr` | `null` |
| `per178691_1906_08026` | `1906-09-24` | `RIO DE JANEIRO, Segunda-feira 24 de Setembro de 1906` | `fe5333dc0f91fea88ccce192e137732eb702d7d43459ee0359d1c0f54840cb8f` | `fill_missing_ocr` | `null` |
| `per178691_1906_08027` | `1906-09-25` | `RIO DE JANEIRO, Terça-feira 25 de Setembro de 1906` | `40f732e92b5effe6e1f7c9ac4e612694c301c4b795362e3fb9357cf394f0c1ad` | `fill_missing_ocr` | `null` |
| `per178691_1906_08028` | `1906-09-26` | `RIO DE JANEIRO, Quarta-feira 26 de Setembro de 1906` | `2f53c2eb01de1113cdfc7d1a50b68024533d71936fc130570d8cfbcc7c64b3ff` | `correct_ocr` | `1906-09-20` |
| `per178691_1906_08073` | `1906-11-10` | `RIO DE JANEIRO, Sabbado 10 de Novembro de 1906` | `4ba81a18e7ea0d344d94ae3bbc9e656783457f6bcd820e225217b6b90f21dac6` | `fill_missing_ocr` | `null` |
| `per178691_1906_08087` | `1906-11-24` | `RIO DE JANEIRO, Sabbado 24 de Novembro de 1906` | `e7d018bc3910b237187b16c935efe8005b5fe4c54e61f0dcbbdce0a331e815f3` | `fill_missing_ocr` | `null` |
| `per178691_1906_08091` | `1906-11-28` | `RIO DE JANEIRO, Quarta-feira 28 de Novembro de 1906` | `e4028b4b0d09b90bb44c6e0f4af72117a3b236d10f2b4aa89b55df15f4931dcd` | `fill_missing_ocr` | `null` |
| `per178691_1906_08100` | `1906-12-07` | `RIO DE JANEIRO, Sexta-feira 7 de Dezembro de 1906` | `c311db592b80bd57eaeb9495196e617e7fd0caaaf8e637af1aa6da6ebc68b448` | `fill_missing_ocr` | `null` |
| `per178691_1906_08104` | `1906-12-11` | `RIO DE JANEIRO, Terça-feira 11 de Dezembro de 1906` | `a3f03fa5dc24757a14eee1165e2e88f7c2a54a8c311b30523552c88b48aae138` | `fill_missing_ocr` | `null` |
| `per178691_1906_08107` | `1906-12-14` | `RIO DE JANEIRO, Sexta-feira 14 de Dezembro de 1906` | `4eb20d0ff398b9390a9e2d0d83cf8c84fea1cd04651a233667fa2979a68b44fc` | `correct_ocr` | `1906-12-08` |
| `per178691_1906_08111` | `1906-12-18` | `RIO DE JANEIRO, Terça-feira 18 de Dezembro de 1906` | `6b623530c6a4b28c977ac1dbc0e7332ea15c0e4d06acbad0b587b559d7438ca5` | `fill_missing_ocr` | `null` |
| `per178691_1906_08115` | `1906-12-22` | `RIO DE JANEIRO, Sabbado 22 de Dezembro de 1906` | `d64a761e75f929c659e85bf8d3477f94da6fd34fc423650b861493a530060b67` | `fill_missing_ocr` | `null` |
| `per178691_1906_08116` | `1906-12-23` | `RIO DE JANEIRO, Domingo 23 de Dezembro de 1906` | `7743d6ad18659fee2a4a9ae37a088753bd6f431acb5530fb471b4715f44a4225` | `fill_missing_ocr` | `null` |
| `per178691_1906_08124` | `1906-12-31` | `RIO DE JANEIRO, Segunda-feira 31 de Dezembro de 1906` | `bb1a10fb36ea11cb4fff0ee0e20ce4e161e9540a6bfec603d98d829143bd92c2` | `fill_missing_ocr` | `null` |
