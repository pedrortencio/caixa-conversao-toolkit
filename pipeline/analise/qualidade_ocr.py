"""Qualidade do OCR embutido por célula jornal-ano (custo zero, sem API).

Pré-requisito 4 de `docs/todo-fightin-words.md`. A análise lexical distintiva
compara grupos por contagem de palavra, então diferença de qualidade de
digitalização entre grupos vira "palavra distintiva" do grupo pior digitalizado.
Medir o ruído por célula é o que permite dizer se uma comparação é sobre o
jornal ou sobre o scanner.

As métricas são propositalmente cruas e auditáveis, sem léxico externo, porque
léxico moderno rejeitaria a ortografia da época (hontem, cambio, actual) e
mediria anacronismo em vez de ruído:

  - `taxa_sem_vogal`: proporção de tokens sem nenhuma vogal, que em português
    é quase sempre lixo de OCR ("xhtq", "lll");
  - `taxa_hapax`: proporção do vocabulário que aparece uma única vez na célula.
    OCR sujo explode o vocabulário criando variantes únicas;
  - `comprimento_medio`: cai quando o OCR fragmenta palavra em pedaços.

Uso: uv run python pipeline/analise/qualidade_ocr.py
"""

from __future__ import annotations

import argparse
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence, TypeVar

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db
from pipeline.triagem import db_leitura

TOKEN = re.compile(r"[^\W\d_]+", re.UNICODE)
# `y` entra como vogal: era vogal na ortografia da época (Nictheroy, Bahya), e
# tratá-la como ruído puniria justamente o texto mais antigo do corpus.
VOGAIS = frozenset("aeiouyáàâãéêíìóôõúùü")
N_AMOSTRA = 25
SEMENTE = 20260725
RELATORIO = db.ROOT / "docs" / "relatorio-qualidade-ocr.md"

T = TypeVar("T")


def _frequencias(textos: Iterable[str]) -> Counter:
    freq: Counter = Counter()
    for texto in textos:
        freq.update(t.lower() for t in TOKEN.findall(texto))
    return freq


def _das_frequencias(freq: Counter) -> dict:
    n = sum(freq.values())
    if not n:
        return {
            "n_tokens": 0, "n_vocabulario": 0, "taxa_sem_vogal": 0.0,
            "taxa_hapax": 0.0, "comprimento_medio": 0.0,
        }
    sem_vogal = sum(c for t, c in freq.items() if not (set(t) & VOGAIS))
    hapax = sum(1 for c in freq.values() if c == 1)
    return {
        "n_tokens": n,
        "n_vocabulario": len(freq),
        "taxa_sem_vogal": sem_vogal / n,
        "taxa_hapax": hapax / len(freq),
        "comprimento_medio": sum(len(t) * c for t, c in freq.items()) / n,
    }


def metricas(texto: str) -> dict:
    """Métricas de ruído de um texto."""
    return _das_frequencias(_frequencias([texto]))


def agrega(textos: Sequence[str]) -> dict:
    """Métricas da célula. O vocabulário é o somado: medir hapax página a
    página inflaria a taxa só porque página é curta."""
    return {**_das_frequencias(_frequencias(textos)), "n_paginas": len(textos)}


def amostra(populacao: Sequence[T], n: int, *, chave: str) -> list[T]:
    """Amostra determinística por célula. A chave entra na semente para que
    células diferentes não sorteiem as mesmas posições."""
    if len(populacao) <= n:
        return list(populacao)
    return random.Random(f"{SEMENTE}-{chave}").sample(list(populacao), n)


def por_celula(conn, n_amostra: int = N_AMOSTRA) -> list[dict]:
    """Uma linha por célula jornal-ano, sobre amostra de páginas."""
    celulas = [
        (r["bib"], r["jornal"], r["ano"])
        for r in conn.execute(
            """SELECT n.bn_bib bib, n.slug jornal, o.source_year ano
               FROM digital_objects o JOIN newspapers n ON n.id = o.newspaper_id
               GROUP BY 1, 2, 3 ORDER BY 2, 3"""
        )
    ]
    linhas = []
    for bib, jornal, ano in celulas:
        paginas = [
            p for p in db_leitura.itera_paginas(conn, bib=bib, ano=ano)
            if p.result_status == "ok"
        ]
        if not paginas:
            continue
        sorteadas = amostra(paginas, n_amostra, chave=f"{bib}-{ano}")
        textos = [db_leitura.le_conteudo(p) for p in sorteadas]
        linhas.append({
            "jornal": jornal, "ano": ano, "paginas_na_celula": len(paginas),
            "chars_por_pagina": sum(len(t) for t in textos) / len(textos),
            **agrega(textos),
        })
    return linhas


def relatorio(linhas: list[dict]) -> str:
    """Markdown com a tabela por célula e a amplitude dentro de cada jornal."""
    partes = [
        "# Qualidade do OCR embutido por célula jornal-ano",
        "",
        "Medida determinística (`pipeline/analise/qualidade_ocr.py`), sem API e "
        "sem léxico externo, sobre amostra determinística de "
        f"{N_AMOSTRA} páginas por célula (semente {SEMENTE}). Serve de controle "
        "para a análise lexical distintiva: diferença de digitalização entre "
        "grupos vira palavra distintiva do grupo pior digitalizado.",
        "",
        "`sem_vogal` = tokens sem nenhuma vogal, quase sempre lixo de OCR. "
        "`hapax` = proporção do vocabulário que ocorre uma só vez. `compr` = "
        "comprimento médio do token, que cai quando o OCR fragmenta palavra.",
        "",
        "| jornal | ano | páginas | chars/pág | sem_vogal | hapax | compr |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in linhas:
        partes.append(
            f"| {r['jornal']} | {r['ano']} | {r['paginas_na_celula']} | "
            f"{r['chars_por_pagina']:.0f} | {100*r['taxa_sem_vogal']:.2f}% | "
            f"{100*r['taxa_hapax']:.1f}% | {r['comprimento_medio']:.2f} |"
        )
    por_jornal: dict[str, list[dict]] = {}
    for r in linhas:
        por_jornal.setdefault(r["jornal"], []).append(r)
    partes += [
        "",
        "## Amplitude dentro de cada jornal",
        "",
        "A variação de um jornal entre seus próprios anos é o que decide se a "
        "comparação entre FASES (rodada 2) também está confundida, e não só a "
        "comparação entre jornais (rodada 3).",
        "",
        "| jornal | sem_vogal mín | sem_vogal máx | razão máx/mín |",
        "|---|---|---|---|",
    ]
    for jornal, rs in por_jornal.items():
        taxas = [r["taxa_sem_vogal"] for r in rs]
        lo, hi = min(taxas), max(taxas)
        anos_lo = [r["ano"] for r in rs if r["taxa_sem_vogal"] == lo][0]
        anos_hi = [r["ano"] for r in rs if r["taxa_sem_vogal"] == hi][0]
        partes.append(
            f"| {jornal} | {100*lo:.2f}% ({anos_lo}) | {100*hi:.2f}% "
            f"({anos_hi}) | {hi/lo:.1f}x |"
        )
    return "\n".join(partes) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Qualidade do OCR por célula")
    parser.add_argument("--amostra", type=int, default=N_AMOSTRA)
    parser.add_argument("--relatorio", default=str(RELATORIO))
    args = parser.parse_args(argv)

    conn = db.connect(db.DEFAULT_DATABASE, migrate=False)
    linhas = por_celula(conn, args.amostra)
    conn.close()
    texto = relatorio(linhas)
    Path(args.relatorio).write_text(texto, encoding="utf-8")
    print(texto)
    print(f"escrito: {args.relatorio}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
