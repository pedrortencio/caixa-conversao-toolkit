"""Extrai o texto completo das secoes da Caixa no Retrospecto Commercial do JC.

EXPLORATORIO (2026-07-23). Nao e o instrumento de stance nem parte do censo
dos 4 jornais; e extracao/OCR com proveniencia, de uma fonte candidata cujo
estatuto no desenho ainda esta em aberto (ver docs/decisoes.md 2026-07-23).
Sem testes ainda: a productizacao (home no pipeline, testes) segue a decisao
de como o Retrospecto entra.

Fonte: Jornal do Commercio : Retrospecto Commercial (RJ), bib 180688, um PDF
anual no host estatico da BN:
  https://hemeroteca-pdf.bn.gov.br/180688/per180688_{ano}_00001.pdf
Os PDFs vivem em dados/raw_pdf/jc_retrospecto/ (gitignored).

Metodo: le a camada de texto (pypdf), acha as paginas que mencionam a Caixa
(regra de nome da triagem, tolerante a OCR) e agrupa em SECOES contiguas
(mencoes proximas, gap <= GAP, com as paginas-ponte). Extrai todas as paginas
de cada secao (inclui as sem o nome: sao a continuacao do argumento). Saida:
CSV estruturado (uma linha por pagina) + um .txt por ano para leitura.
Deterministico, sem API.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if __package__ in {None, ""}:
    sys.path.insert(0, str(RAIZ))

from pypdf import PdfReader

from pipeline.triagem import regra_nome

PDF_DIR = RAIZ / "dados" / "raw_pdf" / "jc_retrospecto"
OUT_DIR = RAIZ / "dados" / "retrospecto_jc"
GAP = 2  # paginas sem mencao toleradas dentro de uma secao continua

CABECALHO = [
    "bib", "ano", "secao_id", "page_number", "tem_mencao",
    "n_mencoes", "char_count", "texto",
]


def secoes(mencao_pags: list[int]) -> list[tuple[int, int]]:
    """Agrupa paginas de mencao (ordenadas) em faixas [inicio, fim] contiguas."""
    if not mencao_pags:
        return []
    faixas: list[tuple[int, int]] = []
    ini = prev = mencao_pags[0]
    for p in mencao_pags[1:]:
        if p - prev <= GAP + 1:
            prev = p
        else:
            faixas.append((ini, prev))
            ini = prev = p
    faixas.append((ini, prev))
    return faixas


def processa(pdf_path: Path, escritor: csv.writer, resumo: list) -> None:
    ano = int(pdf_path.stem.split("_")[1])
    bib = pdf_path.stem.split("_")[0].removeprefix("per")
    reader = PdfReader(str(pdf_path))

    textos: dict[int, str] = {}
    mencoes: dict[int, int] = {}
    for i, page in enumerate(reader.pages, start=1):
        try:
            t = page.extract_text() or ""
        except Exception:  # pagina problematica nao aborta a extracao
            t = ""
        textos[i] = t
        spans = regra_nome.encontra(t)
        if spans:
            mencoes[i] = len(spans)

    paginas = 0
    total_chars = 0
    partes_txt: list[str] = []
    for secao_id, (ini, fim) in enumerate(secoes(sorted(mencoes)), start=1):
        for p in range(ini, fim + 1):
            t = textos[p]
            escritor.writerow([
                bib, ano, secao_id, p,
                1 if p in mencoes else 0, mencoes.get(p, 0), len(t), t,
            ])
            paginas += 1
            total_chars += len(t)
            marca = "MENCAO" if p in mencoes else "ponte"
            partes_txt.append(
                f"\n\n----- Ano {ano} | secao {secao_id} | pagina {p} "
                f"| {marca} -----\n{t}"
            )

    (OUT_DIR / f"retrospecto_{ano}_caixa.txt").write_text(
        "".join(partes_txt), encoding="utf-8"
    )
    resumo.append((ano, paginas, total_chars, len(mencoes)))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "retrospecto_caixa_paginas.csv"
    resumo: list = []
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(CABECALHO)
        for pdf in sorted(PDF_DIR.glob("per180688_*_00001.pdf")):
            processa(pdf, escritor, resumo)

    print(f"{'ano':>4} {'pags':>5} {'kchars':>7} {'pags_menc':>9}")
    for ano, pags, chars, nmenc in resumo:
        print(f"{ano:>4} {pags:>5} {chars // 1000:>7} {nmenc:>9}")
    print(f"TOTAL paginas={sum(r[1] for r in resumo)} "
          f"kchars={sum(r[2] for r in resumo) // 1000}")
    print(f"CSV: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
