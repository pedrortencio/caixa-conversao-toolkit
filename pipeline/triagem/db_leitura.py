"""Leitor somente-leitura da camada de texto embutido para a triagem.

Consulta `v_current_page_texts` (migração 003) e resolve bib/jornal/ano por
`digital_objects`/`newspapers`. Não escreve nada, não sabe da regra de
casamento nem do gabarito: só entrega páginas e seus textos, em ordem
determinística. A unidade padrão do censo inteiro é o objeto digital
(`digital_objects`), proxy 1:1 da edição-dia validado no piloto 1906.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence


@dataclass(frozen=True, slots=True)
class PaginaTexto:
    object_id: int
    source_identifier: str
    bib: str
    newspaper: str
    source_year: int
    page_number: int
    result_status: str
    text_path: str | None
    extraction_run_id: int


def itera_paginas(
    conn: sqlite3.Connection,
    *,
    bib: str | None = None,
    ano: int | None = None,
    source_identifiers: Sequence[str] | None = None,
) -> Iterator[PaginaTexto]:
    """Páginas da camada de texto vigente, em ordem (source_identifier,
    page_number). Filtros opcionais por bib, ano e lista de objetos."""
    clauses: list[str] = []
    values: list[object] = []
    if bib is not None:
        clauses.append("n.bn_bib = ?")
        values.append(bib)
    if ano is not None:
        clauses.append("o.source_year = ?")
        values.append(ano)
    if source_identifiers is not None:
        ids = list(source_identifiers)
        if not ids:
            return
        marcadores = ",".join("?" for _ in ids)
        clauses.append(f"o.source_identifier IN ({marcadores})")
        values.extend(ids)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    cursor = conn.execute(
        f"""
        SELECT
            v.object_id,
            o.source_identifier,
            n.bn_bib AS bib,
            n.slug AS newspaper,
            o.source_year,
            v.page_number,
            v.result_status,
            v.text_path,
            v.extraction_run_id
        FROM v_current_page_texts AS v
        JOIN digital_objects AS o ON o.id = v.object_id
        JOIN newspapers AS n ON n.id = o.newspaper_id
        {where}
        ORDER BY o.source_identifier, v.page_number
        """,
        values,
    )
    for row in cursor:
        yield PaginaTexto(
            object_id=row["object_id"],
            source_identifier=row["source_identifier"],
            bib=row["bib"],
            newspaper=row["newspaper"],
            source_year=row["source_year"],
            page_number=row["page_number"],
            result_status=row["result_status"],
            text_path=row["text_path"],
            extraction_run_id=row["extraction_run_id"],
        )


def le_conteudo(pagina: PaginaTexto) -> str:
    """Texto da página. Página sem camada de texto (`empty`/`error`) devolve
    string vazia: nunca inferimos menção onde não há o que triar."""
    if pagina.result_status != "ok" or not pagina.text_path:
        return ""
    return Path(pagina.text_path).read_bytes().decode("utf-8", errors="replace")
