"""Checagem mecanica das fichas de leitura.

Uso: uv run python dissertacao/fichamentos/padrao-ouro/verifica_fichas.py [chave ...]
Sem argumento, verifica todas as fichas em fichas/.
Reporta, por ficha: palavras, travessoes, blocos ausentes, citacoes com pagina,
frases proibidas, .bib presente e chave coincidente. Sai com 1 se houver problema.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FICHAS = AQUI / "fichas"

BLOCOS = [
    r"\\ficha\{",
    r"\\begin\{identificacao\}",
    r"\\bloco\{Problema e tese\}",
    r"\\bloco\{Argumento\}",
    r"\\bloco\{Conceitos",
    r"\\bloco\{Evid",
    r"\\bloco\{Agentes",
    r"\\bloco\{Cr[ií]ticas",
    r"\\begin\{dialogo\}",
    r"\\usonocapitulo\{",
]
PROIBIDAS = [
    "cabe ressaltar",
    "é importante destacar",
    "nesse sentido",
    "dinheiros",
    "\\usepackage",
]


def verifica(caminho: Path) -> list[str]:
    texto = caminho.read_text(encoding="utf-8")
    chave = caminho.stem
    problemas: list[str] = []
    n_trav = texto.count("\u2014") + texto.count("\u2013")
    if n_trav:
        problemas.append(f"{n_trav} travessao(oes)")
    for padrao in BLOCOS:
        if not re.search(padrao, texto):
            problemas.append(f"bloco ausente: {padrao}")
    m = re.search(r"\\ficha\{[^}]*\}\{([^}]*)\}", texto)
    if m and m.group(1) != chave:
        problemas.append(f"chave na \\ficha ({m.group(1)}) difere do nome do arquivo")
    for frase in PROIBIDAS:
        if frase.lower() in texto.lower():
            problemas.append(f"frase proibida: {frase}")
    bib = caminho.with_suffix(".bib")
    if not bib.exists():
        problemas.append(".bib ausente")
    else:
        b = bib.read_text(encoding="utf-8")
        if not re.search(r"@\w+\{" + re.escape(chave) + r"\s*,", b):
            problemas.append(f"chave {chave} nao encontrada no .bib")
        if "\u2014" in b or "\u2013" in b:
            problemas.append("travessao no .bib")
    corpo = re.sub(r"%.*", "", texto)
    palavras = len(re.findall(r"[A-Za-zÀ-ÿ]{2,}", corpo))
    paginas = len(re.findall(r"\(p\.\s*\d", texto)) + len(re.findall(r"\\chave\{", texto))
    chaves = len(re.findall(r"\\chave\{", texto))
    print(
        f"{chave:26s} {palavras:5d} palavras  {paginas:3d} ref. com pagina  "
        f"{chaves} citacoes-chave  " + ("OK" if not problemas else "; ".join(problemas))
    )
    return problemas


def main(args: list[str]) -> int:
    alvos = [FICHAS / f"{a}.tex" for a in args] if args else sorted(FICHAS.glob("*.tex"))
    erro = 0
    for alvo in alvos:
        if not alvo.exists():
            print(f"{alvo.stem:26s} AUSENTE")
            erro = 1
            continue
        if verifica(alvo):
            erro = 1
    return erro


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
