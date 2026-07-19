"""Extração da camada de texto embutido (OCR da BN) dos PDFs do censo.

Contrato: docs/superpowers/specs/2026-07-18-camada-texto-embutido-design.md.
O texto é o retorno bruto de ``extract_text()`` do pypdf, sem normalização;
página sem camada é registro positivo ``empty``; falha é ``error`` com
classe. Uma run por célula (bib, ano); resume pelo banco (página com
extração vigente do mesmo protocolo e mesmo hash de PDF é pulada).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
import time
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path

from pypdf import PdfReader

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db
from pipeline.base.carrega_piloto import git_commit

PROTOCOL_NAME = "texto-embutido-pypdf"
PROTOCOL_VERSION = "1.0.0"
DEFAULT_RAIZ_TEXTO = Path(r"C:\dados-caixa\texto_embutido")
DEFAULT_MANIFESTO_DIR = db.ROOT / "dados" / "texto_embutido"

CABECALHO_MANIFESTO = [
    "source_identifier",
    "page_number",
    "result_status",
    "char_count",
    "text_sha256",
    "source_pdf_sha256",
    "text_relpath",
]


@dataclass(frozen=True, slots=True)
class CellStats:
    bib: str
    ano: int
    pages_submitted: int
    ok: int
    empty: int
    error: int
    run_id: int | None


@dataclass(frozen=True, slots=True)
class _Registro:
    page_id: int
    source_pdf_sha256: str
    result_status: str
    text_path: str | None
    text_sha256: str | None
    char_count: int | None
    error_class: str | None
    error_message: str | None


def garante_protocolo(conn: sqlite3.Connection) -> int:
    """Protocolo determinístico com a versão do pypdf pinada.

    Se o pypdf instalado mudar, o guard de identidade do upsert_protocol
    aborta e força bump consciente de PROTOCOL_VERSION.
    """
    protocol_id = db.upsert_protocol(
        conn,
        stage="text_extraction",
        name=PROTOCOL_NAME,
        version=PROTOCOL_VERSION,
        executor_type="deterministic",
        code_commit=git_commit(db.ROOT),
        parameters={
            "biblioteca": "pypdf",
            "versao_pypdf": metadata.version("pypdf"),
            "fonte_texto": "camada embutida do PDF (OCR da Hemeroteca BN)",
            "normalizacao": "nenhuma",
            "codificacao": "utf-8",
        },
    )
    conn.commit()
    return protocol_id


def _alvos_da_celula(
    conn: sqlite3.Connection, *, bib: str, ano: int, protocol_id: int
) -> list[sqlite3.Row]:
    """Páginas da célula ainda sem extração vigente deste protocolo
    sobre o PDF vigente."""
    return db.rows(
        conn,
        """
        SELECT
            o.id AS object_id,
            o.source_identifier,
            f.storage_path,
            f.pdf_sha256,
            p.id AS page_id,
            p.page_number
        FROM digital_objects AS o
        JOIN newspapers AS n ON n.id = o.newspaper_id
        JOIN current_object_fetches AS cf ON cf.object_id = o.id
        JOIN object_fetches AS f ON f.id = cf.fetch_id AND f.result = 'ok'
        JOIN physical_pages AS p ON p.object_id = o.id
        LEFT JOIN current_page_text_extractions AS cx ON cx.page_id = p.id
        LEFT JOIN page_text_extractions AS x
               ON x.id = cx.extraction_id
              AND x.source_pdf_sha256 = f.pdf_sha256
              AND x.extraction_run_id IN (
                  SELECT id FROM text_extraction_runs
                  WHERE protocol_id = ?
              )
        WHERE n.bn_bib = ? AND o.source_year = ? AND x.id IS NULL
        ORDER BY o.source_identifier, p.page_number
        """,
        (protocol_id, bib, ano),
    )


def _extrai_paginas_do_objeto(
    alvos: list[sqlite3.Row], raiz_texto: Path, bib: str
) -> list[_Registro]:
    """Extrai as páginas-alvo de um único objeto digital."""
    source_identifier = alvos[0]["source_identifier"]
    pdf_sha = alvos[0]["pdf_sha256"]
    registros: list[_Registro] = []

    reader: PdfReader | None = None
    erro_abertura: Exception | None = None
    try:
        reader = PdfReader(alvos[0]["storage_path"])
    except Exception as exc:  # registro positivo por página, nunca aborto
        erro_abertura = exc

    for alvo in alvos:
        if reader is None:
            assert erro_abertura is not None
            registros.append(
                _Registro(
                    page_id=alvo["page_id"],
                    source_pdf_sha256=pdf_sha,
                    result_status="error",
                    text_path=None,
                    text_sha256=None,
                    char_count=None,
                    error_class=type(erro_abertura).__name__,
                    error_message=str(erro_abertura)[:500],
                )
            )
            continue
        indice = alvo["page_number"] - 1
        try:
            if indice >= len(reader.pages):
                raise IndexError(
                    f"página {alvo['page_number']} fora do PDF "
                    f"({len(reader.pages)} páginas)"
                )
            texto = reader.pages[indice].extract_text() or ""
        except Exception as exc:
            registros.append(
                _Registro(
                    page_id=alvo["page_id"],
                    source_pdf_sha256=pdf_sha,
                    result_status="error",
                    text_path=None,
                    text_sha256=None,
                    char_count=None,
                    error_class=type(exc).__name__,
                    error_message=str(exc)[:500],
                )
            )
            continue
        if texto == "":
            registros.append(
                _Registro(
                    page_id=alvo["page_id"],
                    source_pdf_sha256=pdf_sha,
                    result_status="empty",
                    text_path=None,
                    text_sha256=None,
                    char_count=0,
                    error_class=None,
                    error_message=None,
                )
            )
            continue
        conteudo = texto.encode("utf-8")
        destino = (
            raiz_texto
            / bib
            / source_identifier
            / f"p{alvo['page_number']:03d}.txt"
        )
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(conteudo)
        registros.append(
            _Registro(
                page_id=alvo["page_id"],
                source_pdf_sha256=pdf_sha,
                result_status="ok",
                text_path=str(destino),
                text_sha256=hashlib.sha256(conteudo).hexdigest(),
                char_count=len(texto),
                error_class=None,
                error_message=None,
            )
        )
    return registros


def extrai_celula(
    conn: sqlite3.Connection,
    *,
    bib: str,
    ano: int,
    raiz_texto: Path,
    protocol_id: int | None = None,
) -> CellStats:
    if protocol_id is None:
        protocol_id = garante_protocolo(conn)

    alvos = _alvos_da_celula(conn, bib=bib, ano=ano, protocol_id=protocol_id)
    if not alvos:
        return CellStats(bib, ano, 0, 0, 0, 0, None)

    started_at = db.utc_now()
    inicio = time.monotonic()
    escopo = [[a["source_identifier"], a["page_number"]] for a in alvos]
    escopo_sha = hashlib.sha256(
        json.dumps(escopo, ensure_ascii=False).encode("utf-8")
    ).hexdigest()

    registros: list[_Registro] = []
    por_objeto: dict[int, list[sqlite3.Row]] = {}
    for alvo in alvos:
        por_objeto.setdefault(alvo["object_id"], []).append(alvo)
    for alvos_objeto in por_objeto.values():
        registros.extend(
            _extrai_paginas_do_objeto(alvos_objeto, raiz_texto, bib)
        )

    elapsed = time.monotonic() - inicio
    with db.transaction(conn):
        cursor = conn.execute(
            """
            INSERT INTO text_extraction_runs(
                protocol_id, started_at, completed_at, run_status,
                scope_manifest_sha256, pages_submitted, pages_completed,
                elapsed_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                protocol_id,
                started_at,
                db.utc_now(),
                "ok" if len(registros) == len(alvos) else "partial",
                escopo_sha,
                len(alvos),
                len(registros),
                elapsed,
            ),
        )
        run_id = int(cursor.lastrowid)
        timestamp = db.utc_now()
        for registro in registros:
            cursor = conn.execute(
                """
                INSERT INTO page_text_extractions(
                    page_id, extraction_run_id, source_pdf_sha256,
                    result_status, text_path, text_sha256, char_count,
                    error_class, error_message, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    registro.page_id,
                    run_id,
                    registro.source_pdf_sha256,
                    registro.result_status,
                    registro.text_path,
                    registro.text_sha256,
                    registro.char_count,
                    registro.error_class,
                    registro.error_message,
                    timestamp,
                ),
            )
            conn.execute(
                """
                INSERT INTO current_page_text_extractions(
                    page_id, extraction_id, selected_at
                ) VALUES (?, ?, ?)
                ON CONFLICT(page_id) DO UPDATE SET
                    extraction_id = excluded.extraction_id,
                    selected_at = excluded.selected_at
                """,
                (registro.page_id, int(cursor.lastrowid), timestamp),
            )

    contagem = {"ok": 0, "empty": 0, "error": 0}
    for registro in registros:
        contagem[registro.result_status] += 1
    return CellStats(
        bib,
        ano,
        len(alvos),
        contagem["ok"],
        contagem["empty"],
        contagem["error"],
        run_id,
    )


def _vigentes_da_celula(
    conn: sqlite3.Connection, *, bib: str, ano: int
) -> list[sqlite3.Row]:
    return db.rows(
        conn,
        """
        SELECT
            o.source_identifier,
            v.page_number,
            v.result_status,
            v.char_count,
            v.text_path,
            v.text_sha256,
            v.source_pdf_sha256
        FROM v_current_page_texts AS v
        JOIN digital_objects AS o ON o.id = v.object_id
        JOIN newspapers AS n ON n.id = o.newspaper_id
        WHERE n.bn_bib = ? AND o.source_year = ?
        ORDER BY o.source_identifier, v.page_number
        """,
        (bib, ano),
    )


def exporta_manifesto(
    conn: sqlite3.Connection,
    *,
    bib: str,
    ano: int,
    caminho: Path,
    raiz_texto: Path,
) -> int:
    """Export determinístico das extrações vigentes da célula."""
    vigentes = _vigentes_da_celula(conn, bib=bib, ano=ano)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida, lineterminator="\n")
        escritor.writerow(CABECALHO_MANIFESTO)
        for linha in vigentes:
            relpath = ""
            if linha["text_path"]:
                relpath = (
                    Path(linha["text_path"]).relative_to(raiz_texto).as_posix()
                )
            escritor.writerow(
                [
                    linha["source_identifier"],
                    linha["page_number"],
                    linha["result_status"],
                    linha["char_count"] if linha["char_count"] is not None else "",
                    linha["text_sha256"] or "",
                    linha["source_pdf_sha256"],
                    relpath,
                ]
            )
    return len(vigentes)


def verifica_celula(
    conn: sqlite3.Connection, *, bib: str, ano: int
) -> list[str]:
    """Replay determinístico: reextrai e compara com o vigente, sem
    escrever nada. Devolve a lista de divergências."""
    divergencias: list[str] = []
    leitores: dict[str, PdfReader | Exception] = {}
    caminhos = {
        row["source_identifier"]: row["storage_path"]
        for row in db.rows(
            conn,
            """
            SELECT o.source_identifier, f.storage_path
            FROM digital_objects AS o
            JOIN newspapers AS n ON n.id = o.newspaper_id
            JOIN current_object_fetches AS cf ON cf.object_id = o.id
            JOIN object_fetches AS f ON f.id = cf.fetch_id
            WHERE n.bn_bib = ? AND o.source_year = ? AND f.result = 'ok'
            """,
            (bib, ano),
        )
    }
    for linha in _vigentes_da_celula(conn, bib=bib, ano=ano):
        rotulo = f"{linha['source_identifier']} p{linha['page_number']:03d}"
        if linha["result_status"] != "ok":
            continue
        arquivo = Path(linha["text_path"])
        if not arquivo.is_file():
            divergencias.append(f"{rotulo}: arquivo ausente ({arquivo})")
            continue
        sha_disco = hashlib.sha256(arquivo.read_bytes()).hexdigest()
        if sha_disco != linha["text_sha256"]:
            divergencias.append(
                f"{rotulo}: hash do arquivo difere do banco"
            )
            continue
        identificador = linha["source_identifier"]
        if identificador not in leitores:
            try:
                leitores[identificador] = PdfReader(caminhos[identificador])
            except Exception as exc:
                leitores[identificador] = exc
        leitor = leitores[identificador]
        if isinstance(leitor, Exception):
            divergencias.append(
                f"{rotulo}: PDF não abre no replay ({type(leitor).__name__})"
            )
            continue
        texto = leitor.pages[linha["page_number"] - 1].extract_text() or ""
        sha_replay = hashlib.sha256(texto.encode("utf-8")).hexdigest()
        if sha_replay != linha["text_sha256"]:
            divergencias.append(
                f"{rotulo}: reextração produziu hash diferente"
            )
    return divergencias


def _celulas(
    conn: sqlite3.Connection, *, bib: str | None, ano: int | None
) -> list[tuple[str, int]]:
    clauses = ["f.result = 'ok'"]
    values: list[object] = []
    if bib is not None:
        clauses.append("n.bn_bib = ?")
        values.append(bib)
    if ano is not None:
        clauses.append("o.source_year = ?")
        values.append(ano)
    return [
        (row["bn_bib"], row["source_year"])
        for row in db.rows(
            conn,
            f"""
            SELECT DISTINCT n.bn_bib, o.source_year
            FROM digital_objects AS o
            JOIN newspapers AS n ON n.id = o.newspaper_id
            JOIN current_object_fetches AS cf ON cf.object_id = o.id
            JOIN object_fetches AS f ON f.id = cf.fetch_id
            WHERE {' AND '.join(clauses)}
            ORDER BY n.bn_bib, o.source_year
            """,
            values,
        )
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extrai a camada de texto embutido (OCR da BN) do censo"
    )
    parser.add_argument("--base", default=str(db.DEFAULT_DATABASE))
    parser.add_argument("--raiz-texto", default=str(DEFAULT_RAIZ_TEXTO))
    parser.add_argument(
        "--manifesto-dir", default=str(DEFAULT_MANIFESTO_DIR)
    )
    parser.add_argument("--bib", default=None)
    parser.add_argument("--ano", type=int, default=None)
    parser.add_argument(
        "--verificar",
        action="store_true",
        help="replay determinístico sem escrita, compara com o vigente",
    )
    args = parser.parse_args(argv)

    conn = db.connect(args.base)
    try:
        raiz_texto = Path(args.raiz_texto)
        celulas = _celulas(conn, bib=args.bib, ano=args.ano)
        total_divergencias = 0
        protocol_id = None if args.verificar else garante_protocolo(conn)
        for bib, ano in celulas:
            if args.verificar:
                divergencias = verifica_celula(conn, bib=bib, ano=ano)
                total_divergencias += len(divergencias)
                for divergencia in divergencias:
                    print(f"[{bib} {ano}] DIVERGÊNCIA: {divergencia}")
                print(
                    f"[{bib} {ano}] verificação: "
                    f"{len(divergencias)} divergência(s)",
                    flush=True,
                )
                continue
            stats = extrai_celula(
                conn,
                bib=bib,
                ano=ano,
                raiz_texto=raiz_texto,
                protocol_id=protocol_id,
            )
            manifesto = (
                Path(args.manifesto_dir) / f"extracao_{bib}_{ano}.csv"
            )
            linhas = exporta_manifesto(
                conn, bib=bib, ano=ano, caminho=manifesto, raiz_texto=raiz_texto
            )
            print(
                f"[{bib} {ano}] alvos={stats.pages_submitted} "
                f"ok={stats.ok} empty={stats.empty} error={stats.error} "
                f"manifesto={linhas} linha(s)",
                flush=True,
            )
        return 1 if total_divergencias else 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
