"""Janela de leitura em torno de cada mencao, em coordenadas do texto CRU.

Motivo de existir (docs/exploracao-base-2026-07-28.md, secao 2): a coluna
`texto` da amostra e reconstrucao por modelo e falha de tres maneiras
medidas: interpola resumo entre colchetes, sangra para a coluna vizinha e,
em ao menos um caso, entrega artigo diferente. Uma janela deterministica em
torno do offset da mencao nao pode fazer nenhuma das tres.

A janela sai em texto CRU, com acento e caixa preservados, para que a
citacao devolvida pelo anotador seja apresentavel numa dissertacao. A
conferencia da citacao normaliza os dois lados (pipeline/catalogo/verifica.py),
entao a apresentacao nao enfraquece a verificacao.

O par offset-normalizado -> offset-cru vem de `normaliza_com_indice`, que
reproduz passo a passo a normalizacao de `regra_nome.normaliza` guardando a
posicao de origem de cada caractere. A garantia de que as duas nao divergem
e um teste: `normaliza_com_indice(t)[0] == regra_nome.normaliza(t)`.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from pipeline.triagem import regra_nome

LARGURA_PADRAO = 6000

_HIFEN_QUEBRA = re.compile(r"-[ \t]*\r?\n[ \t]*")
_UM_ESPACO = re.compile(r"\s")


@dataclass(frozen=True, slots=True)
class Janela:
    """Trecho cru da pagina que contem uma ou mais mencoes."""

    inicio: int
    fim: int
    texto: str
    mencoes: tuple[int, ...]

    @property
    def n_mencoes(self) -> int:
        return len(self.mencoes)


def normaliza_com_indice(texto: str) -> tuple[str, list[int]]:
    """Igual a `regra_nome.normaliza`, mais o indice de origem de cada char.

    Devolve (normalizado, indices), com `len(indices) == len(normalizado)` e
    `indices[i]` = posicao no texto cru do caractere que originou o caractere
    i do normalizado. Espaco colapsado aponta para o primeiro da sequencia.
    """
    # Passo 1: rejuntar hifenizacao de quebra de coluna.
    sem_hifen: list[tuple[str, int]] = []
    i = 0
    while i < len(texto):
        casado = _HIFEN_QUEBRA.match(texto, i)
        if casado is not None and casado.end() > i:
            i = casado.end()
            continue
        sem_hifen.append((texto[i], i))
        i += 1

    # Passo 2: caixa baixa e remocao de diacritico, preservando a origem.
    sem_acento: list[tuple[str, int]] = []
    for caractere, origem in sem_hifen:
        for decomposto in unicodedata.normalize(
            "NFKD", caractere.casefold()
        ):
            if unicodedata.combining(decomposto):
                continue
            sem_acento.append((decomposto, origem))

    # Passo 3: colapsar espaco em branco.
    colapsado: list[tuple[str, int]] = []
    vinha_espaco = False
    for caractere, origem in sem_acento:
        if _UM_ESPACO.match(caractere):
            if not vinha_espaco:
                colapsado.append((" ", origem))
            vinha_espaco = True
            continue
        colapsado.append((caractere, origem))
        vinha_espaco = False

    # Passo 4: strip.
    inicio = 0
    fim = len(colapsado)
    while inicio < fim and colapsado[inicio][0] == " ":
        inicio += 1
    while fim > inicio and colapsado[fim - 1][0] == " ":
        fim -= 1
    recortado = colapsado[inicio:fim]

    return "".join(c for c, _ in recortado), [o for _, o in recortado]


def janelas(texto: str, largura: int = LARGURA_PADRAO) -> list[Janela]:
    """Janelas cruas de `largura` caracteres em torno de cada mencao.

    Janelas que se sobrepoem sao fundidas, para nao mandar o mesmo trecho
    duas vezes ao anotador. Lista vazia quando a pagina nao tem mencao.
    """
    spans = regra_nome.encontra(texto)
    if not spans:
        return []

    normalizado, indices = normaliza_com_indice(texto)
    if len(indices) != len(normalizado):  # pragma: no cover - invariante
        raise RuntimeError("indice dessincronizado do texto normalizado")

    metade = largura // 2
    brutas: list[tuple[int, int, int]] = []
    for span in spans:
        if span.offset >= len(indices):
            continue
        centro = indices[span.offset]
        brutas.append(
            (max(0, centro - metade), min(len(texto), centro + metade), span.offset)
        )

    fundidas: list[Janela] = []
    for inicio, fim, offset in brutas:
        if fundidas and inicio <= fundidas[-1].fim:
            ultima = fundidas[-1]
            novo_fim = max(ultima.fim, fim)
            fundidas[-1] = Janela(
                inicio=ultima.inicio,
                fim=novo_fim,
                texto=texto[ultima.inicio:novo_fim],
                mencoes=ultima.mencoes + (offset,),
            )
            continue
        fundidas.append(
            Janela(
                inicio=inicio,
                fim=fim,
                texto=texto[inicio:fim],
                mencoes=(offset,),
            )
        )
    return fundidas


def janela_id(source_identifier: str, page_number: int, janela: Janela) -> str:
    """Identificador estavel e rastreavel ate o intervalo de caracteres."""
    return (
        f"{source_identifier}:p{page_number:03d}"
        f":c{janela.inicio}-{janela.fim}"
    )
