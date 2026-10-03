"""Conferencia mecanica das citacoes verbatim das fichas.

Extrai cada \\chave{texto}{p. N} de fichas/*.tex e confronta o texto, normalizado,
com o texto de origem em `Referencias Ivan/Padrao Ouro/_texto/`.

Tres vereditos, na mesma logica do protocolo de conferencia de citacao do projeto:

  casada          substring literal da fonte normalizada.
  com_lacuna      prefixo e sufixo casam e cobrem >= 90% das palavras, mas ha
                  material intercalado na fonte. Causa tipica: quebra de pagina,
                  cabecalho, chamada de nota, ou elipse deliberada da citacao.
                  Nao e aprovacao, e pendencia de conferencia na imagem.
  rejeitada       o resto.

Citacao que nao casa e rejeitada, nunca corrigida. A taxa e metrica do lote.

Uso: uv run python dissertacao/fichamentos/padrao-ouro/confere_citacoes.py [chave ...]
Sai com 1 se houver rejeitada.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FICHAS = AQUI / "fichas"
TEXTO = Path(
    r"C:\Users\pedro\OneDrive\Documentos\Acadêmico\Dissertação Mestrado"
    r"\Referencias Ivan\Padrão Ouro\_texto"
)

ORIGENS: dict[str, list[str]] = {
    "bordokydland1990": ["Bordo e Kydland (1990) - Gold Standard as a Rule (NBER w3367)"],
    "bordoschwartz1994": ["Bordo e Schwartz (1994) - Specie Standard as a Contingent Rule (NBER w4860)"],
    "bordorockoff1996": ["Bordo e Rockoff (1996) - Good Housekeeping Seal (NBER w5340)"],
    "fergusonschularick2012": ["Ferguson e Schularick (2008) - Thin Film of Gold (NBER w13918)"],
    "obstfeldtaylor2003": ["Obstfeld e Taylor (2003) - Sovereign Risk, Credibility and the Gold Standard (NBER w9345)"],
    "meissner2005": ["Meissner (2005) - Diffusion of the Gold Standard (NBER w9233)"],
    "eichengreen1996": ["Eichengreen (1996) - Globalizing Capital"],
    "marcondes1998": ["Marcondes (1998) - Estabilidade PO"],
    "franco1988": ["Franco (1988) - Assimetrias PO"],
    "gontijo2014": ["Gontijo (2014) - PO"],
    "germerouro": ["Germer (s.d.) - PO I GM"],
    "flandreauflores2012": ["Flandreau e Flores (2012) - Bondholders versus bond-sellers (EREH)"],
    "flandreauflores2012io": ["Flandreau e Flores (2012) - The Peaceful Conspiracy (IO)"],
    "weller2015": ["Weller (2015) - Rothschilds Delicate and Difficult Task (Enterprise and Society)"],
    "weller2018": ["Weller (2018) - Sovereign Debt Crises and Negotiations in Brazil and Mexico"],
    "fritschfranco1992": ["Fritsch e Franco (1992) - Aspects of the Brazilian Experience under the Gold Standard (PUC-Rio TD 286)"],
    "topik1987": ["Topik (1987) - The Political Economy of the Brazilian State 1889-1930"],
    "summerhill2015": ["Summerhill (2015) - Inglorious Revolution"],
    "flandreauzumer2004": ["Flandreau e Zumer (2004) - The Making of Global Finance 1880-1913"],
    "floreszendejas2016": ["Flores Zendejas (2016) - Financial markets, international organizations and conditional lending"],
    "triner1996": ["Triner (1996) - Banking, economic growth and industrialization Brazil 1906-30 (RBE)"],
    "fonsecamollo2012": ["Fonseca e Mollo (2012) - Metalismo x Papelismo"],
    "mollo1994": ["Mollo (1994) - Controvérsias monetárias XIX"],
    "salomao2017": ["Salomão (2017) - Controvérsias monetárias Império"],
    "villela2001": ["Villela (2001) - Debate monetário XIX"],
    "gremaud1997": ["Gremaud (1997) - Controvérsias monetárias"],
    "gambi2015": ["Gambi (2015) - Metalismo x papelismo no II BB"],
    "abreu2014": ["Abreu (2014) - A disputa monetaria na Primeira Republica 1890-1906 (dissertacao USP)"],
    "marinho2021": ["Marinho (2021) - Metalismo x Papelismo"],
    "taosalomao2020": ["Tao e Salomão (2020) - PO século XIX"],
    "almeida2010": ["Almeida (2010) - PE Império"],
    "hankeschuler2015": ["Hanke e Schuler (2015) - Currency Boards for Developing Countries"],
    "dellapaolerataylor2001": [
        "della Paolera e Taylor (2001) - cap 00 Introduction (NBER c8834)",
        "della Paolera e Taylor (2001) - cap 01 Anchors Aweigh 1880s (NBER c8835)",
        "della Paolera e Taylor (2001) - cap 03 Baring Crisis 1890-91 (NBER c8837)",
        "della Paolera e Taylor (2001) - cap 06 Relaunching the Gold Standard 1891-99 (NBER c8840)",
        "della Paolera e Taylor (2001) - cap 07 Calm before the Storm 1899-1914 (NBER c8841)",
        "della Paolera e Taylor (2001) - cap 10 Internal versus External Convertibility (NBER c8844)",
    ],
}

LATEX = re.compile(r"\\(textit|textbf|emph|textquotedblleft|textquotedblright)\b|[{}]")
PAD_CHAVE = re.compile(r"\\chave\{(.+?)\}\{([^}]*)\}", re.S)
COBERTURA_MINIMA = 0.90


def normaliza(s: str) -> str:
    s = LATEX.sub(" ", s)
    s = s.replace("``", '"').replace("''", '"').replace("\\%", "%").replace("\\&", "&")
    # Hifenizacao de fim de linha: "litera- ture" volta a ser "literature".
    s = re.sub(r"-\s+", "", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^A-Za-z0-9]+", " ", s)
    return s.lower().strip()


def le(p: Path) -> str:
    """pdftotext grava latin-1 nos textos em portugues e utf-8 nos demais."""
    dados = p.read_bytes()
    for cod in ("utf-8", "cp1252", "latin-1"):
        try:
            return dados.decode(cod)
        except UnicodeDecodeError:
            continue
    return dados.decode("latin-1", errors="replace")


def carrega(chave: str) -> str | None:
    nomes = ORIGENS.get(chave)
    if not nomes:
        return None
    partes = [le(TEXTO / f"{n}.txt") for n in nomes if (TEXTO / f"{n}.txt").exists()]
    return normaliza(" ".join(partes)) if partes else None


def maior_casamento(pal: list[str], fonte: str, sufixo: bool = False) -> int:
    lo, hi = 0, len(pal)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        trecho = " ".join(pal[-mid:] if sufixo else pal[:mid])
        if trecho in fonte:
            lo = mid
        else:
            hi = mid - 1
    return lo


def avalia(texto: str, fonte: str) -> tuple[str, str]:
    alvo = normaliza(texto)
    if not alvo:
        return "rejeitada", "citacao vazia"
    if alvo in fonte:
        return "casada", ""
    pal = alvo.split()
    pre = maior_casamento(pal, fonte)
    suf = maior_casamento(pal, fonte, sufixo=True)
    cobertura = min(pre + suf, len(pal)) / len(pal)
    if pre and suf and cobertura >= COBERTURA_MINIMA:
        meio = " ".join(pal[pre : len(pal) - suf]) or "(sem palavra solta)"
        return "com_lacuna", f"cobertura {cobertura:.0%}, material intercalado perto de: {meio}"
    return "rejeitada", f"cobertura {cobertura:.0%} (prefixo {pre}, sufixo {suf} de {len(pal)})"


def main(args: list[str]) -> int:
    alvos = [FICHAS / f"{a}.tex" for a in args] if args else sorted(FICHAS.glob("*.tex"))
    contagem = {"casada": 0, "com_lacuna": 0, "rejeitada": 0}
    sem_origem = 0
    for alvo in alvos:
        if not alvo.exists():
            continue
        chave = alvo.stem
        fonte = carrega(chave)
        if fonte is None:
            print(f"{chave}: SEM ORIGEM MAPEADA, citacoes nao conferidas")
            sem_origem += 1
            continue
        for texto, pagina in PAD_CHAVE.findall(alvo.read_text(encoding="utf-8")):
            veredito, nota = avalia(texto, fonte)
            contagem[veredito] += 1
            if veredito != "casada":
                print(f"{veredito.upper():11s} {chave} ({pagina}): {nota}")
                print(f"            {' '.join(texto.split())[:100]}")
    total = sum(contagem.values())
    if total:
        print(
            f"\n{total} citacoes: {contagem['casada']} casadas, "
            f"{contagem['com_lacuna']} com lacuna, {contagem['rejeitada']} rejeitadas "
            f"({contagem['rejeitada'] / total:.1%})"
        )
    if sem_origem:
        print(f"{sem_origem} fichas sem origem mapeada")
    return 1 if contagem["rejeitada"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
