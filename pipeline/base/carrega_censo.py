"""Carga do censo 1906-1914: varredura do host estático para a base v2.

Cada número sondado vira registro positivo: sucesso vira objeto digital,
obtenção, páginas físicas e avaliação inicial na mesma transação; ausência
vira linha no manifesto CSV versionado em `dados/censo/`. O resume lê o
manifesto e os PDFs já baixados, então a varredura pode ser interrompida a
qualquer momento.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from pypdf import PdfReader

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db as base_db
from pipeline.base.carrega_piloto import (
    NEWSPAPERS,
    ensure_assessment,
    get_or_create_run,
    git_commit,
    now,
    sha256_text,
    upsert_page,
)
from pipeline.scraper import censo
from pipeline.scraper import hemeroteca as H

RAIZ_REPO = Path(__file__).resolve().parents[2]
DIR_CENSO = RAIZ_REPO / "dados" / "censo"
RAW_ROOT_PADRAO = Path(r"C:\dados-caixa\raw_pdf")
BIBS_CENSO = ("178691", "089842", "090972", "103730")
CAMPOS_MANIFESTO = [
    "numero",
    "status",
    "http_status",
    "pdf_sha256",
    "byte_count",
    "page_count",
    "quando",
]
PARADA_404 = 90
CAP_POR_ANO = 600
SEM_SUCESSO = 200


@dataclass(frozen=True, slots=True)
class Protocolos:
    censo: int
    inicial: int


class TransporteComCache:
    """Evita rede quando o PDF canônico já está baixado e válido."""

    def __init__(self, interno: censo.Transporte) -> None:
        self.interno = interno

    def obtem(
        self, bib: str, ano: int, numero: int, destino: Path
    ) -> censo.Resultado:
        if destino.exists() and H.eh_pdf_valido(destino):
            corpo = destino.read_bytes()
            return censo.Resultado(
                bib=bib, ano=ano, numero=numero, status="ok",
                http_status=200,
                pdf_sha256=hashlib.sha256(corpo).hexdigest(),
                byte_count=len(corpo), caminho=destino,
                detalhe="cache local",
            )
        return self.interno.obtem(bib, ano, numero, destino)


def garante_protocolos(
    conn: sqlite3.Connection,
    *,
    commit: str,
    timestamp: str,
) -> Protocolos:
    with base_db.transaction(conn):
        return _garante_protocolos(conn, commit=commit, timestamp=timestamp)


def _garante_protocolos(
    conn: sqlite3.Connection,
    *,
    commit: str,
    timestamp: str,
) -> Protocolos:
    protocolo_censo = base_db.upsert_protocol(
        conn,
        stage="inventory",
        name="censo_host_estatico",
        version="1.0.0",
        executor_type="deterministic",
        code_commit=commit,
        parameters={
            "host": H.HOST_PDF,
            "anos": list(censo.ANOS_CENSO),
            "parada_404_consecutivos": PARADA_404,
            "cap_por_ano": CAP_POR_ANO,
            "sem_sucesso": SEM_SUCESSO,
            "deteccao_regime": "sonda n=1..6 por (bib, ano)",
            "ancoras_1906": censo.ANCORAS_1906,
        },
        created_at=timestamp,
    )
    protocolo_inicial = base_db.upsert_protocol(
        conn,
        stage="identification",
        name="initial_not_assessed",
        version="1.0.0",
        executor_type="deterministic",
        code_commit=commit,
        parameters={"result": "not_assessed"},
        created_at=timestamp,
    )
    return Protocolos(censo=protocolo_censo, inicial=protocolo_inicial)


def garante_cadastro(
    conn: sqlite3.Connection,
    *,
    timestamp: str,
) -> dict[str, int]:
    ids: dict[str, int] = {}
    with base_db.transaction(conn):
        for bib, metadata in NEWSPAPERS.items():
            newspaper_id = base_db.upsert_newspaper(
                conn, **metadata, created_at=timestamp
            )
            if bib in BIBS_CENSO:
                ids[bib] = newspaper_id
    return ids


def garante_calendario(
    conn: sqlite3.Connection,
    newspaper_ids: dict[str, int],
    *,
    timestamp: str,
) -> int:
    primeiro_dia = date(censo.ANOS_CENSO[0], 1, 1)
    ultimo_dia = date(censo.ANOS_CENSO[-1], 12, 31)
    total_dias = (ultimo_dia - primeiro_dia).days + 1
    esperado = total_dias * len(newspaper_ids)
    ids = tuple(newspaper_ids.values())
    marcadores = ",".join("?" for _ in ids)
    atual = int(
        conn.execute(
            f"SELECT count(*) FROM calendar_days WHERE newspaper_id IN ({marcadores})",
            ids,
        ).fetchone()[0]
    )
    if atual >= esperado:
        return atual
    with base_db.transaction(conn):
        for newspaper_id in ids:
            dia = primeiro_dia
            while dia <= ultimo_dia:
                base_db.upsert_calendar_day(
                    conn,
                    newspaper_id=newspaper_id,
                    civil_date=dia.isoformat(),
                    created_at=timestamp,
                )
                dia += timedelta(days=1)
    return int(
        conn.execute(
            f"SELECT count(*) FROM calendar_days WHERE newspaper_id IN ({marcadores})",
            ids,
        ).fetchone()[0]
    )


def persiste_sucesso(
    conn: sqlite3.Connection,
    *,
    resultado: censo.Resultado,
    newspaper_id: int,
    protocolos: Protocolos,
    timestamp: str,
) -> int | None:
    """Materializa objeto, obtenção, páginas e avaliações. Devolve page_count."""
    assert resultado.caminho is not None and resultado.pdf_sha256 is not None
    stem = resultado.caminho.stem
    caminho_absoluto = str(resultado.caminho.resolve())
    try:
        page_count: int | None = len(PdfReader(resultado.caminho).pages)
        erro_pypdf = None
    except Exception as erro:  # pypdf lança várias classes próprias
        page_count = None
        erro_pypdf = str(erro)

    with base_db.transaction(conn):
        object_id = base_db.upsert_digital_object(
            conn,
            newspaper_id=newspaper_id,
            source_identifier=stem,
            source_url=H.url_pdf(resultado.bib, resultado.ano, resultado.numero),
            source_year=resultado.ano,
            bn_file_key=f"{resultado.bib}/{stem}.pdf",
            bn_file_number_literal=f"{resultado.numero:05d}",
            discovered_by_protocol_id=protocolos.censo,
            discovered_at=timestamp,
        )
        existente = conn.execute(
            """
            SELECT id FROM object_fetches
            WHERE object_id=? AND pdf_sha256=? AND storage_path=?
            ORDER BY id DESC LIMIT 1
            """,
            (object_id, resultado.pdf_sha256, caminho_absoluto),
        ).fetchone()
        if existente is not None:
            fetch_id = int(existente["id"])
        elif erro_pypdf is not None:
            fetch_id = base_db.mark_download_status(
                conn,
                object_id=object_id,
                result="invalid_pdf",
                attempted_at=timestamp,
                completed_at=timestamp,
                http_status=resultado.http_status,
                storage_path=caminho_absoluto,
                pdf_sha256=resultado.pdf_sha256,
                response_sha256=resultado.pdf_sha256,
                byte_count=resultado.byte_count,
                error_class="pypdf",
                error_message=erro_pypdf,
                make_current=False,
            )
        else:
            fetch_id = base_db.mark_download_status(
                conn,
                object_id=object_id,
                result="ok",
                attempted_at=timestamp,
                completed_at=timestamp,
                http_status=resultado.http_status,
                storage_path=caminho_absoluto,
                pdf_sha256=resultado.pdf_sha256,
                response_sha256=resultado.pdf_sha256,
                byte_count=resultado.byte_count,
                page_count=page_count,
                make_current=False,
            )
        conn.execute(
            """
            INSERT INTO current_object_fetches(object_id, fetch_id, selected_at)
            VALUES (?, ?, ?)
            ON CONFLICT(object_id) DO UPDATE SET
                fetch_id = excluded.fetch_id,
                selected_at = excluded.selected_at
            """,
            (object_id, fetch_id, timestamp),
        )
        if erro_pypdf is not None or page_count is None:
            return None

        escopo = sha256_text(
            json.dumps(
                {
                    "bib": resultado.bib,
                    "ano": resultado.ano,
                    "numero": resultado.numero,
                    "pdf_sha256": resultado.pdf_sha256,
                },
                sort_keys=True,
            )
        )
        run_id = get_or_create_run(
            conn,
            table="identification_runs",
            protocol_id=protocolos.inicial,
            scope_hash=escopo,
            submitted=page_count,
            completed=page_count,
            timestamp=timestamp,
        )
        for numero_pagina in range(1, page_count + 1):
            page_id = upsert_page(
                conn,
                object_id=object_id,
                page_number=numero_pagina,
                pdf_path=resultado.caminho.resolve().as_posix(),
                pdf_sha256=resultado.pdf_sha256,
                timestamp=timestamp,
            )
            ensure_assessment(
                conn,
                page_id=page_id,
                run_id=run_id,
                level="screening",
                result="not_assessed",
                raw_text=json.dumps(
                    {
                        "source": "censo_initial_materialization",
                        "page_number": numero_pagina,
                        "result": "not_assessed",
                    },
                    sort_keys=True,
                ),
                rationale="Avaliação inicial obrigatória da página.",
                evidence_json=None,
                confidence=None,
                timestamp=timestamp,
            )
    return page_count


def registra_manifesto(
    caminho: Path,
    resultado: censo.Resultado,
    *,
    page_count: int | None,
) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    novo = not caminho.exists()
    with open(caminho, "a", encoding="utf-8", newline="") as saida:
        escritor = csv.DictWriter(saida, fieldnames=CAMPOS_MANIFESTO)
        if novo:
            escritor.writeheader()
        escritor.writerow(
            {
                "numero": resultado.numero,
                "status": resultado.status,
                "http_status": resultado.http_status or "",
                "pdf_sha256": resultado.pdf_sha256 or "",
                "byte_count": resultado.byte_count or "",
                "page_count": page_count if page_count is not None else "",
                "quando": now(),
            }
        )


def numeros_sondados(caminho: Path) -> dict[int, str]:
    if not caminho.exists():
        return {}
    with open(caminho, encoding="utf-8", newline="") as entrada:
        return {
            int(linha["numero"]): linha["status"]
            for linha in csv.DictReader(entrada)
        }


def caminho_manifesto(bib: str, ano: int) -> Path:
    return DIR_CENSO / f"varredura_{bib}_{ano}.csv"


def _fim_do_ano_anterior(bib: str, ano: int) -> int | None:
    sondados = numeros_sondados(caminho_manifesto(bib, ano - 1))
    numeros_ok = [n for n, status in sondados.items() if status == "ok"]
    return max(numeros_ok) if numeros_ok else None


def pausa_automatica() -> float:
    hora = datetime.now().hour
    return 2.5 if hora >= 23 or hora < 7 else 4.0


def _persiste_resultado(
    conn: sqlite3.Connection,
    resultado: censo.Resultado,
    *,
    manifesto: Path,
    newspaper_id: int,
    protocolos: Protocolos,
) -> bool:
    """Persiste um resultado da varredura. Devolve True para sucesso ok."""
    page_count = None
    if resultado.status in {"ok", "pdf_invalido"}:
        page_count = persiste_sucesso(
            conn,
            resultado=resultado,
            newspaper_id=newspaper_id,
            protocolos=protocolos,
            timestamp=now(),
        )
    registra_manifesto(manifesto, resultado, page_count=page_count)
    rotulo = {
        "ok": "[ok]  ",
        "ausente": "[404] ",
        "erro": "[ERRO]",
        "pdf_invalido": "[PDF?]",
    }[resultado.status]
    print(
        f"  {rotulo} {H.nome_pdf(resultado.bib, resultado.ano, resultado.numero)}"
        f"  {resultado.detalhe or (f'{page_count} páginas' if page_count else '')}",
        flush=True,
    )
    return resultado.status == "ok" and page_count is not None


def executa_censo(
    *,
    db: Path,
    raw_root: Path,
    bibs: tuple[str, ...],
    anos: tuple[int, ...],
    pausa: float | None,
    limite: int,
    ate_horario: str | None,
) -> None:
    prazo = None
    if ate_horario is not None:
        hora, minuto = (int(parte) for parte in ate_horario.split(":"))
        prazo = datetime.now().replace(
            hour=hora, minute=minuto, second=0, microsecond=0
        )
        if prazo <= datetime.now():
            prazo += timedelta(days=1)

    transporte = TransporteComCache(
        censo.TransporteHttp(pausa if pausa is not None else pausa_automatica)
    )
    conn = base_db.connect(db)
    try:
        commit = git_commit(RAIZ_REPO)
        protocolos = garante_protocolos(conn, commit=commit, timestamp=now())
        newspaper_ids = garante_cadastro(conn, timestamp=now())
        garante_calendario(conn, newspaper_ids, timestamp=now())

        sucessos = 0
        for bib in bibs:
            destino_dir = raw_root / bib
            for ano in anos:
                marcador = DIR_CENSO / f"concluido_{bib}_{ano}.txt"
                if marcador.exists():
                    continue
                manifesto = caminho_manifesto(bib, ano)
                sidecar = DIR_CENSO / f"inicio_{bib}_{ano}.txt"
                print(f"== {H.slug_por_bib(bib)} {ano} ==", flush=True)

                if sidecar.exists():
                    inicio = int(sidecar.read_text(encoding="utf-8").strip())
                elif ano == censo.ANOS_CENSO[0]:
                    inicio, resultados = censo.inicio_continuo_1906(
                        transporte,
                        bib,
                        ancora=censo.ANCORAS_1906[bib],
                        destino_dir=destino_dir,
                        parada=PARADA_404,
                    )
                    for resultado in resultados:
                        if _persiste_resultado(
                            conn, resultado, manifesto=manifesto,
                            newspaper_id=newspaper_ids[bib],
                            protocolos=protocolos,
                        ):
                            sucessos += 1
                    sidecar.parent.mkdir(parents=True, exist_ok=True)
                    sidecar.write_text(str(inicio), encoding="utf-8")
                else:
                    regime, resultados = censo.detecta_regime(
                        transporte, bib, ano, destino_dir
                    )
                    for resultado in resultados:
                        if _persiste_resultado(
                            conn, resultado, manifesto=manifesto,
                            newspaper_id=newspaper_ids[bib],
                            protocolos=protocolos,
                        ):
                            sucessos += 1
                    if regime == "anual":
                        inicio = 1
                    else:
                        fim_anterior = _fim_do_ano_anterior(bib, ano)
                        if fim_anterior is None:
                            print(
                                f"  AVISO: {bib} {ano} é contínuo sem ano "
                                "anterior varrido; pulando por ora.",
                                flush=True,
                            )
                            continue
                        inicio = fim_anterior + 1
                    sidecar.parent.mkdir(parents=True, exist_ok=True)
                    sidecar.write_text(str(inicio), encoding="utf-8")

                ja_sondados = numeros_sondados(manifesto)
                for resultado in censo.varre_ano(
                    transporte,
                    bib,
                    ano,
                    inicio=inicio,
                    ja_sondados=ja_sondados,
                    destino_dir=destino_dir,
                    cap=CAP_POR_ANO,
                    parada=PARADA_404,
                    sem_sucesso=SEM_SUCESSO,
                ):
                    if _persiste_resultado(
                        conn, resultado, manifesto=manifesto,
                        newspaper_id=newspaper_ids[bib],
                        protocolos=protocolos,
                    ):
                        sucessos += 1
                    if limite and sucessos >= limite:
                        print(f"Limite de {limite} sucessos atingido.", flush=True)
                        return
                    if prazo is not None and datetime.now() >= prazo:
                        print(f"Prazo {ate_horario} atingido; parando.", flush=True)
                        return
                marcador.parent.mkdir(parents=True, exist_ok=True)
                marcador.write_text(now(), encoding="utf-8")
                print(f"  varredura de {bib} {ano} CONCLUÍDA.", flush=True)
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Censo 1906-1914 do host estático da Hemeroteca (Fase A)"
    )
    parser.add_argument("--db", type=Path, default=base_db.DEFAULT_DATABASE)
    parser.add_argument("--raw-root", type=Path, default=RAW_ROOT_PADRAO)
    parser.add_argument(
        "--bib", action="append", choices=BIBS_CENSO, default=None,
        help="restringe a um bib (repetível); padrão todos",
    )
    parser.add_argument(
        "--ano", action="append", type=int, default=None,
        help="restringe a um ano (repetível); padrão 1906-1914",
    )
    parser.add_argument(
        "--pausa", type=float, default=None,
        help="segundos entre requisições; padrão automático (4.0 dia, 2.5 madrugada)",
    )
    parser.add_argument(
        "--limite", type=int, default=0,
        help="parar após N downloads bem-sucedidos (0 = sem limite)",
    )
    parser.add_argument(
        "--ate-horario", type=str, default=None,
        help="parar ao alcançar HH:MM (ex.: 07:00)",
    )
    argumentos = parser.parse_args()
    executa_censo(
        db=argumentos.db.resolve(),
        raw_root=argumentos.raw_root,
        bibs=tuple(argumentos.bib or BIBS_CENSO),
        anos=tuple(argumentos.ano or censo.ANOS_CENSO),
        pausa=argumentos.pausa,
        limite=argumentos.limite,
        ate_horario=argumentos.ate_horario,
    )


if __name__ == "__main__":
    main()
