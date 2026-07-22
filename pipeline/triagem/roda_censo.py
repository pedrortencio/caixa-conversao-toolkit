"""Runner da triagem por nome sobre o censo inteiro.

Aplica o preditor `regra_nome.encontra` a cada página da camada de texto
vigente, agrega hit de página a hit de OBJETO DIGITAL (relevante se qualquer
página bate, proxy 1:1 da edição-dia validado no piloto 1906) e emite o
manifesto por página (registro positivo, nunca ausência inferida). Sem LLM,
sem julgamento de posição, custo zero de token.

Contrato: docs/superpowers/specs/2026-07-20-triagem-nome-pivo-design.md.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db
from pipeline.triagem import db_leitura, regra_nome

DIR_MANIFESTO = db.ROOT / "dados" / "triagem"

CABECALHO_MANIFESTO = [
    "bib",
    "source_identifier",
    "page_number",
    "hit",
    "n_matches",
    "primeiro_span_texto",
    "primeiro_span_offset",
    "regra_versao",
    "extraction_run_id",
    "result_status",
]


@dataclass(frozen=True, slots=True)
class DecisaoPagina:
    object_id: int
    bib: str
    source_identifier: str
    source_year: int
    page_number: int
    result_status: str
    hit: bool
    n_matches: int
    primeiro_span_texto: str
    primeiro_span_offset: int | None
    extraction_run_id: int


@dataclass(frozen=True, slots=True)
class DecisaoObjeto:
    object_id: int
    bib: str
    source_identifier: str
    source_year: int
    paginas: int
    paginas_ok: int
    paginas_sem_texto: int
    paginas_hit: int
    n_matches: int
    relevante: bool
    triado_completo: bool


def decide_pagina(pagina: db_leitura.PaginaTexto) -> DecisaoPagina:
    """Decisão de uma página: aplica a regra ao seu texto vigente.

    Página sem camada de texto (`empty`/`error`) nunca é hit e nunca é
    triada com sucesso, mas entra no manifesto como registro positivo de
    "sem texto para triar"."""
    if pagina.result_status == "ok":
        spans = regra_nome.encontra(db_leitura.le_conteudo(pagina))
    else:
        spans = []
    primeiro = spans[0] if spans else None
    return DecisaoPagina(
        object_id=pagina.object_id,
        bib=pagina.bib,
        source_identifier=pagina.source_identifier,
        source_year=pagina.source_year,
        page_number=pagina.page_number,
        result_status=pagina.result_status,
        hit=bool(spans),
        n_matches=len(spans),
        primeiro_span_texto=primeiro.texto if primeiro else "",
        primeiro_span_offset=primeiro.offset if primeiro else None,
        extraction_run_id=pagina.extraction_run_id,
    )


def avalia_paginas(
    conn: sqlite3.Connection,
    *,
    bib: str | None = None,
    ano: int | None = None,
    source_identifiers: list[str] | None = None,
) -> Iterator[DecisaoPagina]:
    for pagina in db_leitura.itera_paginas(
        conn, bib=bib, ano=ano, source_identifiers=source_identifiers
    ):
        yield decide_pagina(pagina)


def agrega_objetos(decisoes: list[DecisaoPagina]) -> list[DecisaoObjeto]:
    """Agrega decisões de página (já computadas) a decisões de objeto.

    Objeto relevante se QUALQUER página bate. `triado_completo` exige todas as
    páginas com `result_status = 'ok'` (o S da cascata, em termos de objeto):
    um objeto com buraco de OCR não conta como triado negativamente."""
    por_objeto: dict[str, list[DecisaoPagina]] = {}
    for d in decisoes:
        por_objeto.setdefault(d.source_identifier, []).append(d)
    resultado: list[DecisaoObjeto] = []
    for source_identifier in sorted(por_objeto):
        paginas = por_objeto[source_identifier]
        referencia = paginas[0]
        paginas_ok = sum(1 for p in paginas if p.result_status == "ok")
        paginas_hit = sum(1 for p in paginas if p.hit)
        resultado.append(
            DecisaoObjeto(
                object_id=referencia.object_id,
                bib=referencia.bib,
                source_identifier=source_identifier,
                source_year=referencia.source_year,
                paginas=len(paginas),
                paginas_ok=paginas_ok,
                paginas_sem_texto=len(paginas) - paginas_ok,
                paginas_hit=paginas_hit,
                n_matches=sum(p.n_matches for p in paginas),
                relevante=paginas_hit > 0,
                triado_completo=paginas_ok == len(paginas),
            )
        )
    return resultado


def avalia_objetos(
    conn: sqlite3.Connection,
    *,
    bib: str | None = None,
    ano: int | None = None,
    source_identifiers: list[str] | None = None,
) -> list[DecisaoObjeto]:
    """Uma passada: lê páginas, decide e agrega a objetos."""
    return agrega_objetos(
        list(
            avalia_paginas(
                conn, bib=bib, ano=ano, source_identifiers=source_identifiers
            )
        )
    )


def escreve_manifesto(
    decisoes: list[DecisaoPagina], caminho: Path
) -> int:
    """Manifesto determinístico por página. Uma linha por página triada."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    ordenadas = sorted(
        decisoes, key=lambda d: (d.source_identifier, d.page_number)
    )
    with caminho.open("w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida, lineterminator="\n")
        escritor.writerow(CABECALHO_MANIFESTO)
        for d in ordenadas:
            escritor.writerow(
                [
                    d.bib,
                    d.source_identifier,
                    d.page_number,
                    1 if d.hit else 0,
                    d.n_matches,
                    d.primeiro_span_texto,
                    "" if d.primeiro_span_offset is None else d.primeiro_span_offset,
                    regra_nome.REGRA_VERSAO,
                    d.extraction_run_id,
                    d.result_status,
                ]
            )
    return len(ordenadas)


def _celulas(
    conn: sqlite3.Connection, *, bib: str | None, ano: int | None
) -> list[tuple[str, int]]:
    clauses: list[str] = []
    values: list[object] = []
    if bib is not None:
        clauses.append("n.bn_bib = ?")
        values.append(bib)
    if ano is not None:
        clauses.append("o.source_year = ?")
        values.append(ano)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return [
        (row["bn_bib"], row["source_year"])
        for row in db.rows(
            conn,
            f"""
            SELECT DISTINCT n.bn_bib, o.source_year
            FROM v_current_page_texts AS v
            JOIN digital_objects AS o ON o.id = v.object_id
            JOIN newspapers AS n ON n.id = o.newspaper_id
            {where}
            ORDER BY n.bn_bib, o.source_year
            """,
            values,
        )
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Triagem por nome do censo (manifesto por página)"
    )
    parser.add_argument("--base", default=str(db.DEFAULT_DATABASE))
    parser.add_argument("--manifesto-dir", default=str(DIR_MANIFESTO))
    parser.add_argument("--bib", default=None)
    parser.add_argument("--ano", type=int, default=None)
    args = parser.parse_args(argv)

    conn = db.connect(args.base, migrate=False)
    try:
        celulas = _celulas(conn, bib=args.bib, ano=args.ano)
        manifesto_dir = Path(args.manifesto_dir)
        for bib, ano in celulas:
            decisoes = list(avalia_paginas(conn, bib=bib, ano=ano))
            caminho = manifesto_dir / f"triagem_nome_{bib}_{ano}.csv"
            linhas = escreve_manifesto(decisoes, caminho)
            objetos = agrega_objetos(decisoes)
            relevantes = sum(1 for o in objetos if o.relevante)
            print(
                f"[{bib} {ano}] paginas={linhas} "
                f"objetos={len(objetos)} relevantes={relevantes}",
                flush=True,
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
