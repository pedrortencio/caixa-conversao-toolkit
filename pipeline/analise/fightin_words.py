"""Fightin' Words: seleção de atributos lexicais entre dois grupos.

Monroe, Colaresi e Quinn (2008), *Lexical Feature Selection and Evaluation for
Identifying the Content of Political Conflict*, Political Analysis 16(4).

Aprovado em 2026-07-23 como DIAGNÓSTICO e triangulação, nunca como instrumento
de posição: palavra distintiva não é posição, e saco de palavras não vê negação
nem discurso reproduzido. Limites a declarar no artigo estão em
`docs/todo-fightin-words.md`.

Duas peças, nesta ordem de importância:

1. **Prior de Dirichlet informativo.** Cada palavra recebe pseudo-contagem
   proporcional à sua frequência no corpus inteiro, o que encolhe o termo raro
   na direção da média. É isso que impede a lista de palavras distintivas de
   virar lista de erro de OCR, que é sempre raro, e o corpus tem 83% de hapax.
2. **Padronização pelo erro padrão.** A leitura é pelo z, não pelo delta.

Normalização: regime mínimo (minúsculas e remoção de acento), ratificado por
Pedro em 2026-07-25 sobre medida. Ortografia de época é PRESERVADA.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from typing import Iterable

TOKEN = re.compile(r"[^\W\d_]+", re.UNICODE)
# alpha_0 é o único parâmetro de ajuste. Fixar, reportar e apresentar
# sensibilidade em pelo menos dois valores (exigência do to-do).
ALPHA_0 = 1000.0
PISO = 20
# |delta| de 1,0 é razão de chances de e, cerca de 2,7 vezes. Piso de leitura
# para separar termo de conteúdo de palavra gramatical, ver `filtra_conteudo`.
DELTA_CONTEUDO = 1.0


def tokeniza(texto: str) -> list[str]:
    """Tokens sob o regime mínimo: minúsculas, sem acento, sem número.

    Não aplica regras de ortografia de época: `actual` não vira `atual`. A
    decisão foi tomada sobre medida (colapso de apenas 2 pontos de vocabulário
    contra risco de juntar palavras distintas) e está em `docs/decisoes.md`.
    """
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )
    return TOKEN.findall(sem_acento)


def conta(textos: Iterable[str]) -> Counter:
    freq: Counter = Counter()
    for texto in textos:
        freq.update(tokeniza(texto))
    return freq


def _termo(
    termo: str,
    total: int,
    grupo_i: Counter,
    grupo_j: Counter,
    n_i: int,
    n_j: int,
    n_corpus: int,
    alpha_0: float,
) -> dict:
    """Uma linha da tabela. Isolado para o piso e o cálculo principal usarem
    exatamente a mesma aritmética."""
    alpha_w = alpha_0 * total / n_corpus
    y_i = grupo_i.get(termo, 0) + alpha_w
    y_j = grupo_j.get(termo, 0) + alpha_w
    delta = math.log(y_i / (n_i + alpha_0 - y_i)) - math.log(
        y_j / (n_j + alpha_0 - y_j)
    )
    variancia = 1 / y_i + 1 / y_j
    return {
        "termo": termo,
        "n_i": grupo_i.get(termo, 0),
        "n_j": grupo_j.get(termo, 0),
        "n_corpus": total,
        "delta": delta,
        "z": delta / math.sqrt(variancia),
    }


def pior_ruido_abaixo_do_piso(
    grupo_i: Counter,
    grupo_j: Counter,
    *,
    alpha_0: float = ALPHA_0,
    piso: int = PISO,
) -> dict | None:
    """O termo de maior |z| entre os que o piso de frequência descarta.

    Serve para responder se o piso é carga estrutural ou conveniência: se o
    pior termo abaixo dele alcança |z| desprezível perto do fim da tabela
    publicada, então quem suprime o ruído de OCR é a padronização pelo erro
    padrão, e o resultado não depende do corte. Devolve None se nada cai
    abaixo do piso. Não materializa a lista inteira: o corpus tem milhões de
    tipos, quase todos de uma ocorrência só.
    """
    corpus = grupo_i + grupo_j
    n_corpus = sum(corpus.values())
    n_i, n_j = sum(grupo_i.values()), sum(grupo_j.values())
    pior = None
    for termo, total in corpus.items():
        if total >= piso:
            continue
        r = _termo(termo, total, grupo_i, grupo_j, n_i, n_j, n_corpus, alpha_0)
        if pior is None or abs(r["z"]) > abs(pior["z"]):
            pior = r
    return pior


def filtra_conteudo(
    linhas: list[dict], *, delta_minimo: float = DELTA_CONTEUDO
) -> list[dict]:
    """Termos de conteúdo: |delta| acima do piso e mais de uma letra.

    O z mistura tamanho de efeito com tamanho de amostra, e o corpus tem
    dezenas de milhões de tokens, então palavra funcional (`que`, `do`, `ao`)
    sobe ao topo do z com diferença proporcional mínima. O delta é o tamanho do
    efeito e não cresce com a amostra, então é ele que separa conteúdo de
    gramática. Token de uma letra é fragmento de OCR, não palavra.

    Filtro de LEITURA, não de estimação: a tabela completa continua saindo, e
    nenhum z é recalculado depois do corte.
    """
    return [
        r for r in linhas
        if abs(r["delta"]) >= delta_minimo and len(r["termo"]) > 1
    ]


def estatisticas(
    grupo_i: Counter,
    grupo_j: Counter,
    *,
    alpha_0: float = ALPHA_0,
    piso: int = PISO,
) -> list[dict]:
    """Uma linha por termo, ordenada do polo `i` para o polo `j` pelo z.

    z positivo é termo característico do grupo `i`. O piso corta o termo com
    menos de `piso` ocorrências somadas nos dois grupos: o prior já encolhe o
    raro, mas ler mil z-scores de lixo não é uso de ninguém.
    """
    corpus = grupo_i + grupo_j
    n_corpus = sum(corpus.values())
    n_i, n_j = sum(grupo_i.values()), sum(grupo_j.values())
    linhas = [
        _termo(termo, total, grupo_i, grupo_j, n_i, n_j, n_corpus, alpha_0)
        for termo, total in corpus.items()
        if total >= piso
    ]
    return sorted(linhas, key=lambda r: r["z"], reverse=True)
