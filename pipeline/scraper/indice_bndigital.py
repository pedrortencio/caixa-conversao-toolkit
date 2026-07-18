"""Extração e verificação do índice bndigital a partir de snapshots HTML.

Segunda passagem da extração do índice (recomendação 2 do parecer do Codex,
18/07/2026): o snapshot do DOM salvo pelo navegador é a evidência primária.
Este módulo expande os links `per{bib}_{ano}_{numero}.pdf` de um snapshot e
compara com o manifesto `dados/censo/indice_bndigital_{bib}.csv` da primeira
passagem, reportando divergências item a item.

Uso:
    uv run python pipeline/scraper/indice_bndigital.py \
        --snapshots dados/censo/snapshots_bndigital --censo dados/censo
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

BIBS = ("089842", "090972", "103730", "178691")
ANO_MIN = 1906
ANO_MAX = 1914


@dataclass(frozen=True)
class ResultadoVerificacao:
    bib: str
    total_snapshot: int
    total_manifesto: int
    so_snapshot: list[tuple[int, int]]
    so_manifesto: list[tuple[int, int]]

    @property
    def identicos(self) -> bool:
        return not self.so_snapshot and not self.so_manifesto


def extrai_edicoes(
    html: str, bib: str, ano_min: int = ANO_MIN, ano_max: int = ANO_MAX
) -> set[tuple[int, int]]:
    """Conjunto (ano, numero) dos links do bib no HTML, dentro do recorte."""
    padrao = re.compile(rf"per{re.escape(bib)}_(\d{{4}})_(\d{{5}})\.pdf")
    edicoes: set[tuple[int, int]] = set()
    for m in padrao.finditer(html):
        ano, numero = int(m.group(1)), int(m.group(2))
        if ano_min <= ano <= ano_max:
            edicoes.add((ano, numero))
    return edicoes


def le_manifesto_csv(caminho: Path) -> set[tuple[int, int]]:
    """Conjunto (ano, numero) de um manifesto com cabeçalho ano,numero."""
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        return {(int(l["ano"]), int(l["numero"])) for l in leitor}


def compara(
    snapshot: set[tuple[int, int]], manifesto: set[tuple[int, int]]
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Divergências ordenadas: (só no snapshot, só no manifesto)."""
    return sorted(snapshot - manifesto), sorted(manifesto - snapshot)


def verifica_bib(bib: str, snapshot: Path, manifesto: Path) -> ResultadoVerificacao:
    edicoes_snapshot = extrai_edicoes(
        snapshot.read_text(encoding="utf-8"), bib
    )
    edicoes_manifesto = le_manifesto_csv(manifesto)
    so_snapshot, so_manifesto = compara(edicoes_snapshot, edicoes_manifesto)
    return ResultadoVerificacao(
        bib=bib,
        total_snapshot=len(edicoes_snapshot),
        total_manifesto=len(edicoes_manifesto),
        so_snapshot=so_snapshot,
        so_manifesto=so_manifesto,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshots", type=Path, required=True,
        help="pasta com snapshot_bndigital_{bib}_*.html",
    )
    parser.add_argument(
        "--censo", type=Path, required=True,
        help="pasta com indice_bndigital_{bib}.csv",
    )
    argumentos = parser.parse_args(argv)

    divergencia_total = 0
    for bib in BIBS:
        candidatos = sorted(
            argumentos.snapshots.glob(f"snapshot_bndigital_{bib}_*.html")
        )
        if not candidatos:
            print(f"[{bib}] SEM SNAPSHOT em {argumentos.snapshots}")
            divergencia_total += 1
            continue
        resultado = verifica_bib(
            bib=bib,
            snapshot=candidatos[-1],
            manifesto=argumentos.censo / f"indice_bndigital_{bib}.csv",
        )
        veredito = "IDENTICOS" if resultado.identicos else "DIVERGEM"
        print(
            f"[{bib}] snapshot={resultado.total_snapshot} "
            f"manifesto={resultado.total_manifesto} -> {veredito}"
        )
        for ano, numero in resultado.so_snapshot:
            print(f"  so no snapshot: {ano}_{numero:05d}")
        for ano, numero in resultado.so_manifesto:
            print(f"  so no manifesto: {ano}_{numero:05d}")
        divergencia_total += len(resultado.so_snapshot)
        divergencia_total += len(resultado.so_manifesto)
    return 0 if divergencia_total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
