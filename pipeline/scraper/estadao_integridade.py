"""Auditoria de integridade do indice do acervo do Estadao.

O acervo tem defeito medido no seu proprio indice (12/08/2026). Nenhuma imagem
esta errada: o que corrompe e o METADADO. Duas classes distintas, e confundi-las
leva a correcao errada:

  A. NUMERO DE EDICAO CORROMPIDO, data correta.
     09/05/1910 = ed 11470, 10/05/1910 = ed 11174, 11/05/1910 = ed 11472.
     11174 e 11471 com digitos trocados, e o proprio `montaPagina.php` confirma
     que o arquivo e "EDICAO DE 10 DE Maio DE 1910". Corrigir a DATA aqui seria
     estragar um registro bom.

  B. DATA FANTASMA, edicao correta.
     A edicao 12658 (15/08/1913) aparece TAMBEM como 15/07/1913, com o mesmo
     salt no nome e bytes identicos. Sao 8 pares assim, todos em julho de 1913.
     Aqui o registro de julho e que nao existe.

Por que isso importa para a pesquisa: se a unidade de analise for edicao-dia, A
quebra a chave e B fabrica dias de publicacao que nao houve. Ambas inflam ou
deslocam contagem por periodo. O `CLAUDE.md` ja registra armadilha analoga entre
jornais (a mesma peca circulando); esta e dentro do mesmo jornal.

Duas checagens, ambas determinsticas e sem rede:

  1. sha256 repetido  -> classe B (mesmo scan sob nomes distintos)
  2. monotonia data x edicao -> classe A e B (o Estadao publicava diariamente e o
     numero anda +1 por dia publicado, entao ordenado por data ele nao decresce)

Uso:
  uv run python pipeline/scraper/estadao_integridade.py
  uv run python pipeline/scraper/estadao_integridade.py --manifesto ... --out ...
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import pathlib
import sys

CAMPOS = ["classe", "nome_arquivo", "data", "edicao", "evidencia", "acao_sugerida"]


def le_manifesto(caminho: pathlib.Path) -> list[dict]:
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def duplicatas_por_sha(man: list[dict]) -> list[dict]:
    """Classe B: bytes identicos sob nomes diferentes."""
    por_sha: dict[str, list[dict]] = {}
    for m in man:
        if m.get("sha256"):
            por_sha.setdefault(m["sha256"], []).append(m)

    achados = []
    for sha, grupo in por_sha.items():
        if len(grupo) < 2:
            continue
        # o registro legitimo e o de edicao coerente com a data; na duvida, o
        # mais recente, porque o fantasma observado sempre antecedeu o bom.
        legitimo = max(grupo, key=lambda g: g["data"])
        for g in grupo:
            if g is legitimo:
                continue
            achados.append({
                "classe": "B_data_fantasma",
                "nome_arquivo": g["nome_arquivo"],
                "data": g["data"],
                "edicao": g["edicao"],
                "evidencia": f"sha256 {sha[:12]} identico a {legitimo['nome_arquivo']}",
                "acao_sugerida": f"descartar; o registro bom e {legitimo['data']}",
            })
    return achados


def inversoes_data_edicao(man: list[dict], ignorar: set[str] | None = None) -> list[dict]:
    """Classe A: ordenado por data, o numero de edicao nao pode cair.

    ORDEM IMPORTA: rode depois de `duplicatas_por_sha` e passe os fantasmas em
    `ignorar`. Um registro de classe B senta na serie com a edicao de outro mes e
    produz uma inversao no dia seguinte que NAO e defeito proprio. Medido: o
    fantasma 15/07/1913 ed 12658 fazia 16/07 ed 12628 parecer corrompida, quando
    12628 e exatamente a edicao correta do dia 16 (15/07 e a 12627).
    """
    ignorar = ignorar or set()
    man = [m for m in man if m["nome_arquivo"] not in ignorar]
    pares = sorted({(m["data"], int(m["edicao"])) for m in man})
    por_chave: dict[tuple[str, str], dict] = {}
    for m in man:
        por_chave.setdefault((m["data"], m["edicao"]), m)

    achados = []
    for (d1, e1), (d2, e2) in zip(pares, pares[1:]):
        if e2 >= e1:
            continue
        m = por_chave[(d2, str(e2))]
        dias = (dt.date.fromisoformat(d2) - dt.date.fromisoformat(d1)).days
        achados.append({
            "classe": "A_edicao_corrompida",
            "nome_arquivo": m["nome_arquivo"],
            "data": d2,
            "edicao": str(e2),
            "evidencia": f"{d1} tem ed {e1}; {dias} dia(s) depois a edicao cai para {e2}",
            "acao_sugerida": f"conferir na pagina; edicao esperada ~{e1 + dias}",
        })
    return achados


def main() -> None:
    ap = argparse.ArgumentParser(description="Auditoria de integridade do indice do Estadao")
    ap.add_argument("--manifesto", type=pathlib.Path,
                    default=pathlib.Path("dados/scraping/estadao/manifesto.csv"))
    ap.add_argument("--out", type=pathlib.Path,
                    default=pathlib.Path("dados/scraping/estadao/auditoria_integridade.csv"))
    args = ap.parse_args()

    if not args.manifesto.exists():
        sys.exit(f"manifesto nao encontrado: {args.manifesto}")
    man = le_manifesto(args.manifesto)

    b = duplicatas_por_sha(man)
    a = inversoes_data_edicao(man, ignorar={x["nome_arquivo"] for x in b})
    achados = a + b

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(achados)

    distintos_sha = len({m["sha256"] for m in man if m.get("sha256")})
    print(f"paginas no manifesto:        {len(man)}")
    print(f"imagens distintas por sha:   {distintos_sha}")
    print(f"classe A (edicao corrompida): {len(a)}")
    print(f"classe B (data fantasma):     {len(b)}")
    print(f"\nauditoria -> {args.out}")
    for x in achados:
        print(f"  [{x['classe']}] {x['nome_arquivo']}  {x['evidencia']}")

    if achados:
        print(f"\nATENCAO: {len(achados)} registros suspeitos. Nenhuma imagem foi "
              f"alterada; a correcao e de metadado e e decisao de curadoria.")


if __name__ == "__main__":
    main()
