"""Tabelas de leitura sobre `dados/analise/nomes_distancia.csv`.

Le so o manifesto, nunca o corpus, para que o relatorio seja barato de
regerar e para que qualquer numero publicado tenha uma linha de manifesto
atras dele.

Uso:
    uv run python -m pipeline.analise.relatorio_nomes
    uv run python -m pipeline.analise.relatorio_nomes --limiar 200
"""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FONTE = RAIZ / "dados" / "analise" / "nomes_distancia.csv"
LIMIARES = (200, 1000, 3000)


def carrega(caminho: Path = FONTE) -> list[dict]:
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    for linha in linhas:
        linha["ano"] = int(linha["ano"])
        linha["distancia_minima"] = int(linha["distancia_minima"])
        linha["ocorrencias_na_pagina"] = int(linha["ocorrencias_na_pagina"])
    return linhas


def denominador(raiz: Path = RAIZ) -> tuple[Counter, Counter]:
    """Paginas com mencao por ano e por jornal, lidas do manifesto de triagem."""
    por_ano: Counter = Counter()
    por_bib: Counter = Counter()
    for manifesto in sorted((raiz / "dados" / "triagem").glob("triagem_nome_*.csv")):
        bib, ano = manifesto.stem.split("_")[-2:]
        with open(manifesto, encoding="utf-8", newline="") as arquivo:
            for registro in csv.DictReader(arquivo):
                if registro["hit"] == "1":
                    por_ano[int(ano)] += 1
                    por_bib[bib] += 1
    return por_ano, por_bib


def main() -> None:  # pragma: no cover - saida de leitura
    parser = argparse.ArgumentParser()
    parser.add_argument("--limiar", type=int, default=1000)
    parser.add_argument("--topo", type=int, default=18)
    args = parser.parse_args()

    linhas = carrega()
    pag_ano, pag_bib = denominador()
    anos = sorted(pag_ano)
    total = sum(pag_ano.values())

    por_nome: dict[str, list[dict]] = defaultdict(list)
    for linha in linhas:
        por_nome[linha["nome"]].append(linha)

    print(f"paginas com mencao da Caixa: {total}")
    print(f"pares (pagina, ator) encontrados: {len(linhas)}")
    print(f"paginas por ano: {dict((a, pag_ano[a]) for a in anos)}")

    print("\n" + "=" * 108)
    print("A. RANKING. paginas em que o nome aparece a X caracteres da mencao")
    print("=" * 108)
    print(f"{'nome':22s} {'<=200':>6s} {'<=1000':>7s} {'<=3000':>7s} {'pagina':>7s} "
          f"{'mediana':>8s} {'% na pag':>9s}")
    ordem = sorted(
        por_nome,
        key=lambda n: -sum(1 for r in por_nome[n] if r["distancia_minima"] <= args.limiar),
    )
    for nome in ordem:
        regs = por_nome[nome]
        contas = {t: sum(1 for r in regs if r["distancia_minima"] <= t) for t in LIMIARES}
        mediana = statistics.median(r["distancia_minima"] for r in regs)
        print(f"{nome:22s} {contas[200]:>6d} {contas[1000]:>7d} {contas[3000]:>7d} "
              f"{len(regs):>7d} {mediana:>8.0f} {100 * contas[200] / len(regs):>8.0f}%")
    print("\nultima coluna: dos casos em que o nome esta na mesma pagina de uma mencao,")
    print("que fracao esta a 200 caracteres dela. E o teste que separa vizinhanca de")
    print("coluna de vizinhanca argumentativa.")

    print("\n" + "=" * 108)
    print(f"B. SERIE TEMPORAL, limiar <={args.limiar} (numero de paginas)")
    print("=" * 108)
    print(f"{'nome':22s} " + " ".join(f"{a % 100:>5d}" for a in anos))
    for nome in ordem[: args.topo]:
        c = Counter(r["ano"] for r in por_nome[nome] if r["distancia_minima"] <= args.limiar)
        print(f"{nome:22s} " + " ".join(f"{c.get(a, 0):>5d}" for a in anos))
    print(f"{'paginas com mencao':22s} " + " ".join(f"{pag_ano[a]:>5d}" for a in anos))

    print("\n" + "=" * 108)
    print("C. MESMA SERIE POR 100 PAGINAS COM MENCAO DO ANO")
    print("=" * 108)
    print(f"{'nome':22s} " + " ".join(f"{a % 100:>5d}" for a in anos))
    for nome in ordem[: args.topo]:
        c = Counter(r["ano"] for r in por_nome[nome] if r["distancia_minima"] <= args.limiar)
        print(f"{nome:22s} " + " ".join(
            f"{100 * c.get(a, 0) / pag_ano[a]:>5.1f}" for a in anos))

    print("\n" + "=" * 108)
    print(f"D. POR JORNAL, limiar <={args.limiar}")
    print("=" * 108)
    jornais = sorted({r["jornal"] for r in linhas})
    print(f"{'nome':22s} " + " ".join(f"{j[:18]:>19s}" for j in jornais))
    for nome in ordem[: args.topo]:
        c = Counter(r["jornal"] for r in por_nome[nome] if r["distancia_minima"] <= args.limiar)
        print(f"{nome:22s} " + " ".join(f"{c.get(j, 0):>19d}" for j in jornais))

    print("\n" + "=" * 108)
    print("E. DISTRIBUICAO DA DISTANCIA, todos os pares")
    print("=" * 108)
    todas = sorted(r["distancia_minima"] for r in linhas)
    for q in (10, 25, 50, 75, 90):
        print(f"  p{q:<3d}: {todas[min(len(todas) - 1, int(len(todas) * q / 100))]:>7d}")
    faixas = [(0, 200), (200, 1000), (1000, 3000), (3000, 10000), (10000, None)]
    for inicio, fim in faixas:
        n = sum(1 for d in todas if d >= inicio and (fim is None or d < fim))
        rotulo = f"[{inicio}, {fim})" if fim else f"[{inicio}, +)"
        print(f"  {rotulo:>16s}: {n:>6d} ({100 * n / len(todas):>4.1f}%)")


if __name__ == "__main__":  # pragma: no cover
    main()
