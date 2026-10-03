"""Monta o caderno a partir das fichas existentes.

1. Gera `fichas-novas.bib` com as entradas de `fichas/*.bib` cujas chaves NAO
   existem em `bibliografia/referencias.bib` (as existentes ficam para conferencia).
2. Descomenta em `main.tex` o \\input de cada ficha que existe em `fichas/`.
Uso: uv run python dissertacao/fichamentos/padrao-ouro/monta_caderno.py
"""

from __future__ import annotations

import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FICHAS = AQUI / "fichas"
REFERENCIAS = AQUI.parent.parent / "bibliografia" / "referencias.bib"
SAIDA = AQUI / "fichas-novas.bib"
MAIN = AQUI / "main.tex"


def chaves_de(texto: str) -> set[str]:
    return set(re.findall(r"@\w+\{\s*([^,\s]+)\s*,", texto))


def main() -> None:
    existentes = chaves_de(REFERENCIAS.read_text(encoding="utf-8"))
    blocos: list[str] = []
    vistas: set[str] = set()
    for bib in sorted(FICHAS.glob("*.bib")):
        texto = bib.read_text(encoding="utf-8").strip()
        for chave in chaves_de(texto):
            if chave in existentes:
                print(f"{chave}: ja existe em referencias.bib, nao duplicada")
            elif chave in vistas:
                print(f"{chave}: repetida entre fichas, ignorada")
            else:
                vistas.add(chave)
                blocos.append(texto)
    SAIDA.write_text("\n\n".join(blocos) + "\n", encoding="utf-8")
    print(f"{SAIDA.name}: {len(vistas)} entradas novas")

    main_tex = MAIN.read_text(encoding="utf-8")
    ligadas = 0
    for tex in sorted(FICHAS.glob("*.tex")):
        chave = tex.stem
        padrao = re.compile(r"^% \\input\{fichas/" + re.escape(chave) + r"\}$", re.M)
        if padrao.search(main_tex):
            main_tex = padrao.sub(r"\\input{fichas/" + chave + "}", main_tex)
            ligadas += 1
        elif f"\\input{{fichas/{chave}}}" not in main_tex:
            print(f"AVISO: {chave} nao consta do main.tex, incluir a mao na parte certa")
    MAIN.write_text(main_tex, encoding="utf-8")
    print(f"main.tex: {ligadas} \\input descomentados")


if __name__ == "__main__":
    main()
