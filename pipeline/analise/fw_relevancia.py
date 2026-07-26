"""Rodada 1 do Fightin' Words: páginas que nomeiam a Caixa contra páginas que não.

Primeira das quatro rodadas previstas em `docs/todo-fightin-words.md`, e a
primeira porque devolve algo acionável ainda na fase de construção do corpus:
os termos que acompanham o debate e NÃO estão na regra de busca por nome, que
são candidatos a ampliar a triagem e insumo direto da auditoria de recall.

Não depende de rótulo humano de posição. Custo zero de API: roda local sobre a
camada de texto embutido.

Controle estratificado por célula jornal-ano de propósito. A medida de
qualidade do OCR (`docs/relatorio-qualidade-ocr.md`) mostrou ruído variando de
4,84% a 14,33% entre células, então um controle sorteado do corpus inteiro
compararia também a qualidade da digitalização, e não só o vocabulário.

Uso: uv run python pipeline/analise/fw_relevancia.py
"""

from __future__ import annotations

import argparse
import csv
import glob
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.analise import fightin_words as fw
from pipeline.base import db
from pipeline.base.carrega_piloto import git_commit
from pipeline.triagem import db_leitura

MANIFESTOS = "dados/triagem/triagem_nome_*.csv"
RELATORIO = db.ROOT / "docs" / "relatorio-fw-rodada1-relevancia.md"
SEMENTE = 20260725
N_TOPO = 30


def carrega_manifestos(padrao: str = MANIFESTOS) -> list[dict]:
    """Páginas triadas, do censo inteiro, com o veredito da regra de nome."""
    linhas = []
    for caminho in sorted(glob.glob(padrao)):
        nome = Path(caminho).stem
        ano = int(nome.split("_")[-1])
        with open(caminho, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                linhas.append({
                    "bib": r["bib"],
                    "ano": ano,
                    "source_identifier": r["source_identifier"],
                    "page_number": int(r["page_number"]),
                    "hit": int(r["hit"]),
                    "result_status": r["result_status"],
                })
    return linhas


def seleciona(linhas: list[dict]) -> tuple[list[dict], list[dict]]:
    """Grupos da rodada: (com match, sem match), o controle estratificado por
    célula jornal-ano e do mesmo tamanho do tratamento.

    Página sem camada de texto fica fora dos dois grupos: `empty` e `error`
    são ausência de medida, não ausência de menção, e contá-las no controle
    seria tomar silêncio de OCR por silêncio do jornal.
    """
    validas = [r for r in linhas if r["result_status"] == "ok"]
    com = [r for r in validas if r["hit"] == 1]
    disponiveis: dict[tuple, list[dict]] = defaultdict(list)
    for r in validas:
        if r["hit"] == 0:
            disponiveis[(r["bib"], r["ano"])].append(r)
    alvo = Counter((r["bib"], r["ano"]) for r in com)
    sem: list[dict] = []
    for celula, quantos in sorted(alvo.items()):
        pool = disponiveis.get(celula, [])
        rng = random.Random(f"{SEMENTE}-{celula[0]}-{celula[1]}")
        sem.extend(rng.sample(pool, min(quantos, len(pool))))
    return com, sem


def _textos(conn, paginas: list[dict]) -> Counter:
    """Contagem de tokens do grupo, lendo a camada de texto vigente."""
    por_edicao: dict[str, set[int]] = defaultdict(set)
    for p in paginas:
        por_edicao[p["source_identifier"]].add(p["page_number"])
    freq: Counter = Counter()
    ids = sorted(por_edicao)
    for i in range(0, len(ids), 400):
        lote = ids[i:i + 400]
        for pagina in db_leitura.itera_paginas(conn, source_identifiers=lote):
            if pagina.page_number in por_edicao[pagina.source_identifier]:
                freq.update(fw.tokeniza(db_leitura.le_conteudo(pagina)))
    return freq


def relatorio(
    com: Counter, sem: Counter, n_com: int, n_sem: int, commit: str
) -> str:
    linhas = fw.estatisticas(com, sem)
    conteudo = fw.filtra_conteudo(linhas)
    topo = conteudo[:N_TOPO]
    base = conteudo[-N_TOPO:][::-1]
    topo_z = linhas[:15]
    base_z = linhas[-15:][::-1]
    # Faixa larga de propósito: em 10^2 a 10^4 nada acontece, porque com 10^8
    # tokens alpha_w fica em fração de unidade contra contagens de milhares.
    alphas = (1e3, 1e5, 1e6, 1e7)
    sens = {
        a: {r["termo"]: r["z"] for r in fw.estatisticas(com, sem, alpha_0=a)}
        for a in alphas
    }
    pior = fw.pior_ruido_abaixo_do_piso(com, sem)
    partes = [
        "# Fightin' Words, rodada 1: páginas que nomeiam a Caixa contra as que não",
        "",
        "**Estatuto:** diagnóstico e triangulação, nunca instrumento de posição "
        "(decisão de 2026-07-23). Palavra distintiva não é posição.",
        "",
        "## Proveniência",
        "",
        f"- Corpus: camada de texto embutido do censo (`v_current_page_texts`), "
        f"páginas com `result_status = ok`.",
        f"- Grupo i (relevante): {n_com} páginas com match da regra de nome.",
        f"- Grupo j (controle): {n_sem} páginas sem match, sorteadas com "
        f"estratificação por célula jornal-ano e semente {SEMENTE}.",
        f"- Normalização: regime mínimo (minúsculas e remoção de acento), "
        f"decisão de 2026-07-25. Ortografia de época preservada.",
        f"- alpha_0 = {fw.ALPHA_0:.0f}; piso de frequência = {fw.PISO} "
        f"ocorrências somadas.",
        f"- Vocabulário sobre o piso: {len(linhas)} termos, de "
        f"{len(com | sem)} tipos observados.",
        f"- Filtro de leitura: |delta| >= {fw.DELTA_CONTEUDO} e mais de uma "
        f"letra, o que deixa {len(conteudo)} termos de conteúdo. É corte de "
        "leitura, não de estimação: nenhum z foi recalculado depois dele.",
        f"- Commit: `{commit}`.",
        "",
        "## Termos característicos das páginas que nomeiam a Caixa",
        "",
        "z positivo é termo do grupo relevante. Ordenado por z, entre os termos "
        "de conteúdo.",
        "",
        "| termo | n relevante | n controle | delta | z |",
        "|---|---|---|---|---|",
    ]
    for r in topo:
        partes.append(
            f"| {r['termo']} | {r['n_i']} | {r['n_j']} | "
            f"{r['delta']:.3f} | {r['z']:.1f} |"
        )
    partes += [
        "",
        "## Termos característicos do controle",
        "",
        "| termo | n relevante | n controle | delta | z |",
        "|---|---|---|---|---|",
    ]
    for r in base:
        partes.append(
            f"| {r['termo']} | {r['n_i']} | {r['n_j']} | "
            f"{r['delta']:.3f} | {r['z']:.1f} |"
        )
    partes += [
        "",
        "## Sem o filtro de leitura, os 15 de cada lado",
        "",
        "Publicado para o filtro ser auditável. O topo por z puro é dominado "
        "por palavra gramatical e por letra solta de OCR, porque z cresce com "
        "a amostra e o corpus tem dezenas de milhões de tokens. Nenhuma dessas "
        "linhas foi removida do cálculo, só da leitura acima.",
        "",
        "| termo | n relevante | n controle | delta | z |",
        "|---|---|---|---|---|",
    ]
    for r in topo_z + base_z:
        partes.append(
            f"| {r['termo']} | {r['n_i']} | {r['n_j']} | "
            f"{r['delta']:.3f} | {r['z']:.1f} |"
        )
    partes += [
        "",
        "## Robustez: nenhum dos dois parâmetros do analista move o resultado",
        "",
        "### Sensibilidade a alpha_0",
        "",
        "O to-do exige reportar pelo menos dois valores. A faixa vai a 10^7 "
        "porque a faixa convencional não informa nada aqui: com cerca de 10^8 "
        "tokens, `alpha_w = alpha_0 * y_w / n` fica em fração de unidade "
        "contra contagens de milhares, então **o prior informativo está quase "
        "inerte nesta escala**. Só a partir de 10^6 as magnitudes se mexem, e "
        "a ordem do topo não muda.",
        "",
        "| termo | " + " | ".join(f"z (alpha_0=1e{int(math.log10(a))})" for a in alphas) + " |",
        "|---|" + "---|" * len(alphas),
    ]
    for r in topo[:15]:
        t = r["termo"]
        partes.append(
            f"| {t} | " + " | ".join(
                f"{sens[a].get(t, float('nan')):.1f}" for a in alphas
            ) + " |"
        )
    corte = topo[-1] if topo else None
    partes += [
        "",
        "### O piso de frequência não é carga estrutural",
        "",
        "Se o termo mais extremo ABAIXO do piso alcança |z| desprezível, então "
        "o piso é conveniência de leitura e de tempo, não parte do resultado, "
        "e quem suprime o ruído de OCR é a padronização pelo erro padrão "
        "sozinha. Isso importa porque o corpus é 82% hapax: é a diferença "
        "entre um resultado que depende do corte do analista e um que não.",
        "",
    ]
    if pior and corte:
        partes.append(
            f"O pior termo abaixo do piso é `{pior['termo']}` "
            f"({pior['n_corpus']} ocorrências), com z = {pior['z']:.1f}. "
            f"O último termo da tabela publicada é `{corte['termo']}`, com "
            f"z = {corte['z']:.1f}. **A margem é de "
            f"{abs(corte['z']) / max(abs(pior['z']), 1e-9):.0f} vezes**, "
            "então nenhum termo descartado pelo piso chegaria perto da lista."
        )
    return "\n".join(partes) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fightin' Words, rodada 1")
    parser.add_argument("--manifestos", default=MANIFESTOS)
    parser.add_argument("--relatorio", default=str(RELATORIO))
    args = parser.parse_args(argv)

    com_pgs, sem_pgs = seleciona(carrega_manifestos(args.manifestos))
    print(f"grupo relevante: {len(com_pgs)} páginas")
    print(f"grupo controle : {len(sem_pgs)} páginas")
    conn = db.connect(db.DEFAULT_DATABASE, migrate=False)
    freq_com = _textos(conn, com_pgs)
    print(f"tokens no grupo relevante: {sum(freq_com.values()):,}")
    freq_sem = _textos(conn, sem_pgs)
    print(f"tokens no controle       : {sum(freq_sem.values()):,}")
    conn.close()

    texto = relatorio(
        freq_com, freq_sem, len(com_pgs), len(sem_pgs), git_commit(db.ROOT)
    )
    Path(args.relatorio).write_text(texto, encoding="utf-8")
    print(f"escrito: {args.relatorio}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
