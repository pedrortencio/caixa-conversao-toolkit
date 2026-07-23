"""Sonda de densidade: quanto texto sobre a Caixa ha em cada Retrospecto anual.

EXPLORATORIO (2026-07-23). Backing dos numeros de densidade reportados em
docs/decisoes.md. Le a camada de texto (pypdf) de cada PDF anual em
dados/raw_pdf/jc_retrospecto/, roda a regra de nome da triagem e imprime, por
arquivo: paginas totais, paginas com texto, paginas com mencao, mencoes.
Sem API. Ver extrai_secoes.py para a extracao propriamente dita.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if __package__ in {None, ""}:
    sys.path.insert(0, str(RAIZ))

from pypdf import PdfReader

from pipeline.triagem import regra_nome

PDF_DIR = RAIZ / "dados" / "raw_pdf" / "jc_retrospecto"


def main() -> int:
    pdfs = sorted(PDF_DIR.glob("per180688_*_00001.pdf"))
    if not pdfs:
        print("nenhum PDF em", PDF_DIR)
        return 1
    print(f"{'arquivo':28} {'pag':>4} {'txt':>4} {'menc_pag':>8} {'menc':>5} {'kchars':>7}")
    for pdf in pdfs:
        reader = PdfReader(str(pdf))
        n_pag = len(reader.pages)
        com_texto = com_mencao = mencoes = chars = 0
        for page in reader.pages:
            try:
                t = page.extract_text() or ""
            except Exception:
                t = ""
            if t.strip():
                com_texto += 1
            chars += len(t)
            spans = regra_nome.encontra(t)
            if spans:
                com_mencao += 1
                mencoes += len(spans)
        print(f"{pdf.name:28} {n_pag:>4} {com_texto:>4} "
              f"{com_mencao:>8} {mencoes:>5} {chars // 1000:>7}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
