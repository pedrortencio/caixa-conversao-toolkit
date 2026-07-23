"""Limpeza determinística da amostra recuperada por visão (sem API/LLM).

Marca cada peça com um `status` (keep ou motivo de descarte) e um flag de
data confiável, sem apagar nada (registro positivo). A avaliação de 2026-07-22
mostrou ~40% de ruído de sobreinclusão na recuperacao (itens vizinhos, Caixa
de Amortizacao, marcadores de incerteza) e falha de recall da visao (~7%)
concentrada em 1911-12; por isso a contabilidade de perdas sai por ano, para
a comparacao temporal nao ser enviesada por descarte silencioso.

Saída: `amostra_para_rotular.csv` (todas as linhas + status + data_confiavel +
registro vazio; Pedro rotula onde status==keep) e um relatorio por ano.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db
from pipeline.triagem import regra_nome
from pipeline.triagem.roda_censo import DIR_MANIFESTO

ENTRADA = DIR_MANIFESTO / "amostra_recuperada.csv"
FALHAS = DIR_MANIFESTO / "falhas_recuperadas.csv"
SAIDA = DIR_MANIFESTO / "amostra_para_rotular.csv"
RELATORIO = db.ROOT / "docs" / "relatorio-limpeza-amostra.md"

_DISCLAIMER = re.compile(
    r"\[|nao (e|est|h)|nenhum|aproximad|refer[eê]ncia|indireta|passagem", re.I
)


def classifica(row: dict) -> str:
    """status: keep ou motivo de descarte. Ordem importa (mais forte primeiro)."""
    if row["forma"] in ("sem_mencao_na_imagem", "erro", "sem_mencao_confirmada"):
        return "falha"
    trecho = row["trecho_caixa"]
    if not trecho.strip():
        return "drop_trecho_vazio"
    if "amortiza" in regra_nome.normaliza(trecho):
        return "drop_amortizacao"
    if _DISCLAIMER.search(trecho):
        return "drop_disclaimer"
    if regra_nome.encontra(row["texto"]) or regra_nome.encontra(trecho):
        return "keep"
    return "keep" if row["continua"] == "1" else "drop_sem_nome"


def data_confiavel(row: dict) -> int:
    """1 se a data veio da visão e o ano casa com source_year (tolerância de
    1 ano nas viradas de ano); 0 caso contrário (parser de OCR ou divergência),
    para inspeção humana."""
    data, ano = row["data"], row["source_year"]
    if row["data_fonte"] != "masthead_llm" or len(data) < 4 or not data[:4].isdigit():
        return 0
    return 1 if abs(int(data[:4]) - int(ano)) <= 1 else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Limpa a amostra recuperada")
    parser.add_argument("--entrada", default=str(ENTRADA))
    parser.add_argument("--falhas", default=str(FALHAS))
    parser.add_argument("--saida", default=str(SAIDA))
    parser.add_argument("--relatorio", default=str(RELATORIO))
    args = parser.parse_args(argv)

    linhas = list(csv.DictReader(open(args.entrada, encoding="utf-8")))
    campos = list(linhas[0].keys()) + ["status", "data_confiavel"]

    # Mescla as FALHAs re-extraídas de forma dirigida: remove as linhas
    # `sem_mencao_na_imagem` das páginas re-extraídas e usa os itens recuperados.
    falhas_path = Path(args.falhas)
    if falhas_path.exists():
        rec = list(csv.DictReader(open(falhas_path, encoding="utf-8")))
        pgs = {(r["source_identifier"], r["page_number"]) for r in rec}
        linhas = [
            r for r in linhas
            if not (r["forma"] == "sem_mencao_na_imagem"
                    and (r["source_identifier"], r["page_number"]) in pgs)
        ]
        linhas += rec

    por_ano: dict[str, Counter] = defaultdict(Counter)
    for r in linhas:
        r["status"] = classifica(r)
        r["data_confiavel"] = data_confiavel(r)
        por_ano[r["source_year"]][r["status"]] += 1

    with open(args.saida, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)

    motivos = ["keep", "drop_disclaimer", "drop_trecho_vazio",
               "drop_amortizacao", "drop_sem_nome", "falha"]
    anos = sorted(por_ano)
    partes = [
        "# Relatório de limpeza da amostra recuperada",
        "",
        "Limpeza determinística (`pipeline/triagem/limpa_amostra.py`, sem "
        "API/LLM). `keep` = peça válida para rotular; `falha` = visão não "
        "capturou o trecho que o OCR indica (registro não determinado); os "
        "`drop_*` são ruído de sobreinclusão da recuperação. Perdas por ano "
        "para a comparação temporal não ser enviesada por descarte silencioso.",
        "",
        "| ano | total | " + " | ".join(motivos) + " | keep% | falha% |",
        "|" + "---|" * (len(motivos) + 4),
    ]
    tot = Counter()
    for a in anos:
        c = por_ano[a]
        n = sum(c.values())
        tot.update(c)
        partes.append(
            f"| {a} | {n} | "
            + " | ".join(str(c.get(m, 0)) for m in motivos)
            + f" | {100*c.get('keep',0)/n:.0f}% | {100*c.get('falha',0)/n:.0f}% |"
        )
    ntot = sum(tot.values())
    partes.append(
        f"| **tot** | **{ntot}** | "
        + " | ".join(f"**{tot.get(m,0)}**" for m in motivos)
        + f" | **{100*tot.get('keep',0)/ntot:.0f}%** "
        f"| **{100*tot.get('falha',0)/ntot:.0f}%** |"
    )
    n_suspeita = sum(1 for r in linhas if r["data_confiavel"] == 0)
    partes += [
        "",
        f"Datas a conferir (`data_confiavel=0`): {n_suspeita} de {ntot} "
        "(parser de OCR ou ano divergente do source_year).",
    ]
    Path(args.relatorio).write_text("\n".join(partes) + "\n", encoding="utf-8")
    print("\n".join(partes))
    print(f"\nescrito: {args.saida} ({ntot} linhas), {args.relatorio}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
