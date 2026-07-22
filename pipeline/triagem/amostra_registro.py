"""Amostra estratificada de contextos de match (Passo 1 da medida de
substância). Enumera os matches do nome no censo com janela de contexto
ampla e sorteia uma amostra por jornal-ano, com semente fixa, para Pedro
rotular o registro (incidental/operacional_rotina/substantivo) antes de
qualquer detector. Contrato: docs/superpowers/specs/
2026-07-21-decomposicao-registro-substancia-design.md.
"""

from __future__ import annotations

import argparse
import csv
import random
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db
from pipeline.triagem import db_leitura, regra_nome
from pipeline.triagem.roda_censo import DIR_MANIFESTO

CONTEXTO_AMPLO = 120
SEMENTE_PADRAO = 20260721
POR_CELULA_PADRAO = 12

CABECALHO_AMOSTRA = [
    "match_id",
    "bib",
    "newspaper",
    "source_year",
    "source_identifier",
    "page_number",
    "offset",
    "texto",
    "contexto",
    "registro",
]


@dataclass(frozen=True, slots=True)
class MatchContexto:
    match_id: str
    bib: str
    newspaper: str
    source_year: int
    source_identifier: str
    page_number: int
    offset: int
    texto: str
    contexto: str


def enumera_matches(
    conn: sqlite3.Connection,
    *,
    bib: str | None = None,
    ano: int | None = None,
) -> Iterator[MatchContexto]:
    """Um MatchContexto por span do nome nas páginas com texto vigente ok."""
    for pagina in db_leitura.itera_paginas(conn, bib=bib, ano=ano):
        if pagina.result_status != "ok":
            continue
        texto = db_leitura.le_conteudo(pagina)
        normalizado = regra_nome.normaliza(texto)
        for span in regra_nome.encontra(texto):
            ini = max(0, span.offset - CONTEXTO_AMPLO)
            fim = min(
                len(normalizado), span.offset + len(span.texto) + CONTEXTO_AMPLO
            )
            yield MatchContexto(
                match_id=(
                    f"{pagina.source_identifier}"
                    f":p{pagina.page_number:03d}:o{span.offset}"
                ),
                bib=pagina.bib,
                newspaper=pagina.newspaper,
                source_year=pagina.source_year,
                source_identifier=pagina.source_identifier,
                page_number=pagina.page_number,
                offset=span.offset,
                texto=span.texto,
                contexto=normalizado[ini:fim],
            )


def amostra_estratificada(
    conn: sqlite3.Connection,
    *,
    por_celula: int = POR_CELULA_PADRAO,
    semente: int = SEMENTE_PADRAO,
) -> list[MatchContexto]:
    """Amostra até `por_celula` matches por (bib, ano), semente fixa.

    População de cada célula ordenada por match_id antes do sorteio, para o
    resultado ser byte-idêntico entre execuções."""
    rng = random.Random(semente)
    por_celula_matches: dict[tuple[str, int], list[MatchContexto]] = {}
    for m in enumera_matches(conn):
        por_celula_matches.setdefault((m.bib, m.source_year), []).append(m)
    escolhidos: list[MatchContexto] = []
    for chave in sorted(por_celula_matches):
        populacao = sorted(
            por_celula_matches[chave], key=lambda m: m.match_id
        )
        cota = min(por_celula, len(populacao))
        escolhidos.extend(rng.sample(populacao, cota))
    return sorted(escolhidos, key=lambda m: m.match_id)


def escreve_amostra(matches: list[MatchContexto], caminho: Path) -> int:
    """CSV determinístico com a coluna `registro` vazia para Pedro rotular."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    ordenados = sorted(matches, key=lambda m: m.match_id)
    with caminho.open("w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida, lineterminator="\n")
        escritor.writerow(CABECALHO_AMOSTRA)
        for m in ordenados:
            escritor.writerow(
                [
                    m.match_id,
                    m.bib,
                    m.newspaper,
                    m.source_year,
                    m.source_identifier,
                    m.page_number,
                    m.offset,
                    m.texto,
                    m.contexto,
                    "",
                ]
            )
    return len(ordenados)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Amostra estratificada de contextos de match (Passo 1)"
    )
    parser.add_argument("--base", default=str(db.DEFAULT_DATABASE))
    parser.add_argument(
        "--saida", default=str(DIR_MANIFESTO / "amostra_registro.csv")
    )
    parser.add_argument("--por-celula", type=int, default=POR_CELULA_PADRAO)
    parser.add_argument("--semente", type=int, default=SEMENTE_PADRAO)
    args = parser.parse_args(argv)

    conn = db.connect(args.base, migrate=False)
    try:
        matches = amostra_estratificada(
            conn, por_celula=args.por_celula, semente=args.semente
        )
    finally:
        conn.close()
    n = escreve_amostra(matches, Path(args.saida))
    celulas = len({(m.bib, m.source_year) for m in matches})
    print(
        f"amostra: {n} contextos, {celulas} celulas, "
        f"semente={args.semente}, por_celula={args.por_celula} -> {args.saida}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
