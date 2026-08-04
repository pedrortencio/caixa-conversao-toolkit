"""Quem aparece perto da mencao da Caixa de Conversao, e a que distancia.

ESTATUTO: medida exploratoria do objeto 1 (mapeamento descritivo), no mesmo
patamar de `pipeline/banqueiros/` e de `referente_argentino.py`. NAO e
instrumento de medicao do objeto 2: nao decide posicao, nao atribui voz, nao
distingue quem fala de quem e citado, e nenhuma linha daqui vale como citacao
sem conferencia na pagina.

Por que distancia e nao janela fixa
-----------------------------------
A sondagem de banqueiros de 2026-07-26 mediu que a co-ocorrencia na PAGINA e,
em boa parte, vizinhanca de coluna: a mediana da distancia entre a mencao de
Rothschild e a da Caixa foi de 8.077 caracteres numa pagina de 41.738, e so
5,3% ficaram abaixo de 200. Uma janela larga herda esse defeito e produz um
ranking do que o jornal mais imprime, nao do que o debate discute. Guardando a
distancia minima por par (pagina, ator), o limiar vira consulta e a escolha
fica explicita.

Ressalva que acompanha a medida: distancia em caracteres do texto extraido nao
e distancia fisica na pagina, porque a ordem de leitura do OCR da BN nao
respeita coluna de forma confiavel. Serve para separar adjacencia de
vizinhanca argumentativa e para ordenar candidatos, nao como metrica final.

Casamento tolerante a OCR
-------------------------
Nome proprio em tipo gotico apanha muito mais ruido que frase portuguesa:
`rothschild` na forma exata cobre 48,6% das ocorrencias, o resto se reparte em
125 variantes. Dai o casamento por distancia de edicao. O teto e assimetrico
de proposito: token com 7 caracteres ou mais aceita distancia 1, token com 6
ou menos exige forma exata, porque abaixo disso a vizinhanca lexical do
portugues ja contem palavra corrente (costa/conta/consta, paula/paulo,
ramos/vamos, penna/pensa/perna).

As colisoes que sobram estao em `exclusoes_variantes_nomes.csv`, uma linha por
variante recusada com o motivo. As que mais importam foram medidas nesta base:
carvalhal casa carvalho (2.322), campista casa cambista, pinheiro casa
dinheiro (1.056), sarmento casa sargento (1.204), ellis casa elles (955).
Exclusao e registro positivo, nunca silencio.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from pipeline.triagem import regra_nome

PROTOCOL_NAME = "nomes-no-debate"
PROTOCOL_VERSION = "0.1.0"

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
ELENCO_PADRAO = AQUI / "elenco_debate.csv"
EXCLUSOES_PADRAO = AQUI / "exclusoes_variantes_nomes.csv"

TOKEN = re.compile(r"[a-z]{2,}")

BIBS = {
    "089842": "Correio da Manha",
    "090972": "Correio Paulistano",
    "103730": "Gazeta de Noticias",
    "178691": "O Paiz",
}


@dataclass(frozen=True, slots=True)
class Ator:
    nome: str
    classe: str
    formas: tuple[tuple[str, ...], ...]
    origem: str

    @property
    def tokens(self) -> frozenset[str]:
        return frozenset(t for forma in self.formas for t in forma)


# ---------------------------------------------------------------------------
# Elenco e exclusoes
# ---------------------------------------------------------------------------

def carrega_elenco(caminho: Path = ELENCO_PADRAO) -> tuple[Ator, ...]:
    atores: list[Ator] = []
    vistos: set[str] = set()
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            nome = linha["nome"].strip()
            if not nome:
                continue
            if nome in vistos:
                raise ValueError(f"ator repetido no elenco: {nome}")
            vistos.add(nome)
            formas = tuple(
                tuple(parte.split())
                for parte in linha["formas"].split("|")
                if parte.strip()
            )
            if not formas:
                raise ValueError(f"ator sem forma de busca: {nome}")
            atores.append(
                Ator(nome, linha["classe"].strip(), formas, linha["origem"].strip())
            )
    return tuple(atores)


def carrega_exclusoes(caminho: Path = EXCLUSOES_PADRAO) -> dict[str, str]:
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return {
            linha["variante"].strip(): linha["motivo"].strip()
            for linha in csv.DictReader(arquivo)
            if linha["variante"].strip()
        }


# ---------------------------------------------------------------------------
# Casamento tolerante
# ---------------------------------------------------------------------------

def teto_de(token: str) -> int:
    """Distancia de edicao admitida para um token-chave."""
    return 1 if len(token) >= 7 else 0


def distancia(a: str, b: str, teto: int) -> int:
    """Levenshtein com corte: devolve teto+1 assim que passa do teto."""
    if abs(len(a) - len(b)) > teto:
        return teto + 1
    anterior = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        atual = [i]
        menor = i
        for j, cb in enumerate(b, 1):
            custo = 0 if ca == cb else 1
            atual.append(
                min(anterior[j] + 1, atual[j - 1] + 1, anterior[j - 1] + custo)
            )
            menor = min(menor, atual[-1])
        if menor > teto:
            return teto + 1
        anterior = atual
    return anterior[-1]


def metades(token: str) -> tuple[str, str]:
    """As duas metades de um token, usadas como pre-filtro.

    Se `distancia(a, b) <= 1`, uma unica edicao atinge no maximo uma das
    metades de `a`, entao a outra sobrevive inteira como subcadeia de `b`.
    E condicao necessaria, nao suficiente: barata para descartar, o
    Levenshtein decide o resto.
    """
    meio = len(token) // 2
    return token[:meio], token[meio:]


def descobre_variantes(
    vocabulario: Iterable[str],
    tokens_chave: Iterable[str],
    exclusoes: Mapping[str, str],
) -> dict[str, set[str]]:
    """token-chave -> formas do vocabulario que o representam.

    A forma exata do token-chave entra sempre, mesmo que apareca na lista de
    exclusoes, porque exclusao serve para recusar vizinho e nao o proprio nome.
    """
    chaves = sorted(set(tokens_chave))
    achadas: dict[str, set[str]] = {c: {c} for c in chaves}
    # Token curto tem teto 0: a unica forma que o representa e ele mesmo, e
    # incluir suas metades na peneira ("s", "a" de "sa") faria a peneira casar
    # todo o vocabulario e anular o pre-filtro.
    aproximados = [c for c in chaves if teto_de(c) > 0]
    if not aproximados:
        return achadas
    peneira = re.compile(
        "|".join(sorted({re.escape(m) for c in aproximados for m in metades(c) if m}))
    )
    for tipo in vocabulario:
        if tipo in exclusoes or not peneira.search(tipo):
            continue
        for chave in aproximados:
            if tipo == chave:
                continue
            teto = teto_de(chave)
            if distancia(chave, tipo, teto) <= teto:
                achadas[chave].add(tipo)
    return achadas


def indice_de_formas(variantes: Mapping[str, set[str]]) -> dict[str, frozenset[str]]:
    """forma encontrada no texto -> tokens-chave que ela pode representar."""
    mapa: dict[str, set[str]] = {}
    for chave, formas in variantes.items():
        for forma in formas:
            mapa.setdefault(forma, set()).add(chave)
    return {forma: frozenset(chaves) for forma, chaves in mapa.items()}


@dataclass(frozen=True, slots=True)
class PaginaIndexada:
    """Tokens de uma pagina e onde cada token-chave casou.

    Existe para separar o custo por pagina do custo por ator: sem ela, cada um
    dos 52 atores mandaria tokenizar de novo a mesma pagina de 42 mil
    caracteres, e a varredura do corpus passa de minutos a dezenas de minutos.
    """

    tokens: tuple[tuple[str, int], ...]
    marcas: tuple[frozenset[str] | None, ...]
    onde: Mapping[str, tuple[int, ...]]


def indexa_pagina(texto: str, indice: Mapping[str, frozenset[str]]) -> PaginaIndexada:
    tokens = tuple((m.group(0), m.start()) for m in TOKEN.finditer(texto))
    marcas = tuple(indice.get(t) for t, _ in tokens)
    onde: dict[str, list[int]] = {}
    for i, marca in enumerate(marcas):
        if marca:
            for chave in marca:
                onde.setdefault(chave, []).append(i)
    return PaginaIndexada(tokens, marcas, {k: tuple(v) for k, v in onde.items()})


def posicoes_na_pagina(pagina: PaginaIndexada, ator: Ator) -> list[int]:
    """Offsets onde o nome do ator comeca, numa pagina ja indexada.

    Nome composto exige tokens ADJACENTES, na ordem. Sem isso "Barbosa" e
    "Lima" a paragrafos de distancia virariam Barbosa Lima.
    """
    tokens, marcas, onde = pagina.tokens, pagina.marcas, pagina.onde
    encontrados: list[int] = []
    for forma in ator.formas:
        k = len(forma)
        for i in onde.get(forma[0], ()):
            if i + k > len(tokens):
                continue
            if all(
                marcas[i + j] is not None and forma[j] in marcas[i + j]
                for j in range(1, k)
            ):
                encontrados.append(tokens[i][1])
    return sorted(set(encontrados))


def posicoes(texto: str, ator: Ator, indice: Mapping[str, frozenset[str]]) -> list[int]:
    """Conveniencia para uma pagina so. Em varredura, use `indexa_pagina`."""
    return posicoes_na_pagina(indexa_pagina(texto, indice), ator)


def distancia_minima(posicoes_nome: Sequence[int], mencoes: Sequence[int]) -> int:
    """Menor distancia em caracteres entre uma ocorrencia do nome e uma mencao."""
    if not posicoes_nome or not mencoes:
        raise ValueError("distancia exige ao menos uma posicao de cada lado")
    return min(abs(p - m) for p in posicoes_nome for m in mencoes)


def mencoes_em(texto_normalizado: str) -> list[int]:
    return [m.start() for m in regra_nome._PADRAO.finditer(texto_normalizado)]


# ---------------------------------------------------------------------------
# Varredura do corpus triado
# ---------------------------------------------------------------------------

def paginas_com_mencao(
    raiz: Path = RAIZ, texto_embutido: Path = Path("C:/dados-caixa/texto_embutido")
):
    for manifesto in sorted((raiz / "dados" / "triagem").glob("triagem_nome_*.csv")):
        bib, ano = manifesto.stem.split("_")[-2:]
        with open(manifesto, encoding="utf-8", newline="") as arquivo:
            for registro in csv.DictReader(arquivo):
                if registro["hit"] != "1":
                    continue
                caminho = (
                    texto_embutido
                    / bib
                    / registro["source_identifier"]
                    / f"p{int(registro['page_number']):03d}.txt"
                )
                if caminho.is_file():
                    yield bib, int(ano), registro["source_identifier"], int(
                        registro["page_number"]
                    ), caminho


def main() -> None:  # pragma: no cover - orquestracao com I/O
    import time
    from collections import Counter

    inicio = time.time()
    elenco = carrega_elenco()
    exclusoes = carrega_exclusoes()
    print(f"elenco: {len(elenco)} atores | exclusoes: {len(exclusoes)} variantes")

    # Duas leituras do disco em vez de guardar o corpus em memoria: sao 350
    # milhoes de caracteres normalizados, e o custo de reler e de ~50s.
    vocabulario: Counter[str] = Counter()
    n_paginas = 0
    for *_, caminho in paginas_com_mencao():
        texto = regra_nome.normaliza(caminho.read_text(encoding="utf-8", errors="replace"))
        vocabulario.update(TOKEN.findall(texto))
        n_paginas += 1
    print(
        f"passo 1: {n_paginas} paginas, {len(vocabulario)} tipos, "
        f"{time.time() - inicio:.0f}s",
        flush=True,
    )

    tokens_chave = {t for ator in elenco for t in ator.tokens}
    variantes = descobre_variantes(vocabulario, tokens_chave, exclusoes)
    indice = indice_de_formas(variantes)
    print(f"passo 2: {len(indice)} formas indexadas, {time.time() - inicio:.0f}s", flush=True)

    saida = RAIZ / "dados" / "analise"
    saida.mkdir(parents=True, exist_ok=True)
    with open(saida / "nomes_variantes_ocr.csv", "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(["token_chave", "variante", "ocorrencias"])
        for chave in sorted(variantes):
            for forma in sorted(variantes[chave], key=lambda x: -vocabulario[x]):
                escritor.writerow([chave, forma, vocabulario[forma]])

    registros: list[dict] = []
    for bib, ano, objeto, pagina, caminho in paginas_com_mencao():
        texto = regra_nome.normaliza(caminho.read_text(encoding="utf-8", errors="replace"))
        marcas = mencoes_em(texto)
        if not marcas:
            continue
        indexada = indexa_pagina(texto, indice)
        for ator in elenco:
            achados = posicoes_na_pagina(indexada, ator)
            if not achados:
                continue
            registros.append(
                {
                    "bib": bib,
                    "jornal": BIBS.get(bib, bib),
                    "ano": ano,
                    "objeto": objeto,
                    "pagina": pagina,
                    "nome": ator.nome,
                    "classe": ator.classe,
                    "ocorrencias_na_pagina": len(achados),
                    "distancia_minima": distancia_minima(achados, marcas),
                    "mencoes_na_pagina": len(marcas),
                    "chars_pagina": len(texto),
                }
            )

    destino = saida / "nomes_distancia.csv"
    with open(destino, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(registros[0]), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(registros)
    print(
        f"passo 3: {len(registros)} pares (pagina, ator), {time.time() - inicio:.0f}s"
    )
    print(f"manifesto: {destino}")


if __name__ == "__main__":  # pragma: no cover
    main()
