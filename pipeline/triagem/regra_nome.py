"""Preditor de triagem por nome: texto de página → spans de "Caixa de
Conversão". Função pura, sem I/O, sem banco. Aqui moram os corner cases de
OCR. Contrato: docs/superpowers/specs/2026-07-20-triagem-nome-pivo-design.md.

Decisão de construto (docs/decisoes.md, 2026-07-20): ancorar no NOME, não em
lista de termos de debate. A regra casa "caixa" seguida, com conector
possivelmente corrompido ou mesclado, do radical "conver". Ancorar no radical
"conver" (não "conv") rejeita de graça toda a família conv+[ei]
(convenio, convite, convidados, convem…) e os falsos amigos "caixa de
correio", "caixa de amortização", "caixa de socorros", que não contêm o
radical. A tolerância do conector foi calibrada contra o OCR real dos
positivos do gabarito 1906 (formas dominantes: "de", mesclado "deconversao",
corrompido "dc"/"do", truncado "conver-"); é escolha de mensuração, não
neutra, e por isso é medida por recall (positivos do gabarito) e por precisão
(amostra sobre os 280 "No Relevant Mentions") em calibra_1906.py.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

PROTOCOL_NAME = "nome-caixa-conversao"
PROTOCOL_VERSION = "1.0.0"
REGRA_VERSAO = f"triagem/{PROTOCOL_NAME} {PROTOCOL_VERSION}"

_CONTEXTO_JANELA = 30

# Quebra de coluna hifenizada: "conver-\nsão" → "conversão". Remove o hífen
# e a quebra (com espaços de recuo da coluna seguinte) ANTES de colapsar o
# espaço em branco, para rejuntar o radical partido.
_HIFEN_QUEBRA = re.compile(r"-[ \t]*\r?\n[ \t]*")
_ESPACO = re.compile(r"\s+")

# Casa "caixa" + conector curto (opcional, começando por 'd': de/do/da/dc/d,
# inclusive mesclado sem espaço, ex. "deconversao") + radical "conver".
# O radical "conver" é o mínimo: pega "conversao", "conversa", "converter" e o
# truncado "conver", mas nunca a família conv+[ei]. A busca roda sobre o texto
# JÁ normalizado (minúsculo, sem diacrítico, espaço colapsado).
_PADRAO = re.compile(r"caixa\s*(?:d\w?\s*)?conver")


@dataclass(frozen=True, slots=True)
class Span:
    """Ocorrência casada no texto normalizado."""

    offset: int
    texto: str
    contexto: str


def _sem_diacritico(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def normaliza(texto: str) -> str:
    """Normalização tolerante a ruído de OCR, determinística.

    Rejunta hifenização de quebra de coluna, baixa a caixa, remove
    acento/cedilha/til (NFKD + descarte de combining marks) e colapsa
    espaço em branco. Sem correção ortográfica nem seleção de conteúdo.
    """
    sem_hifen = _HIFEN_QUEBRA.sub("", texto)
    rebaixado = _sem_diacritico(sem_hifen.casefold())
    return _ESPACO.sub(" ", rebaixado).strip()


def encontra(texto: str) -> list[Span]:
    """Spans de "Caixa de Conversão" no texto (cru) de uma página.

    Normaliza e devolve, em ordem, uma entrada por ocorrência do nome. Lista
    vazia quando não há menção. Determinístico: mesmo texto, mesma saída.
    """
    normalizado = normaliza(texto)
    spans: list[Span] = []
    for encontrado in _PADRAO.finditer(normalizado):
        inicio, fim = encontrado.span()
        ini_ctx = max(0, inicio - _CONTEXTO_JANELA)
        fim_ctx = min(len(normalizado), fim + _CONTEXTO_JANELA)
        spans.append(
            Span(
                offset=inicio,
                texto=encontrado.group(0),
                contexto=normalizado[ini_ctx:fim_ctx],
            )
        )
    return spans
