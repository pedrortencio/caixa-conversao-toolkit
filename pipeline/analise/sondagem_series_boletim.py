"""Terceira sondagem: densidade das SERIES numericas diarias no corpus triado.

Mede quantas paginas trazem (a) o boletim de movimento da Caixa, (b) o balanco
de deposito com equivalente em libras, (c) a tabela de cambio oficial sobre
Londres. Nao extrai numero, so conta e guarda contexto.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(
    r"C:/Users/pedro/OneDrive/Documentos/Acadêmico/Dissertação Mestrado/Dados/caixa-conversao-toolkit"
)
TEXTO = Path("C:/dados-caixa/texto_embutido")
TRIAGEM = RAIZ / "dados" / "triagem"

PADROES = {
    "boletim_movimento": r"movimento d[ae] caixa d[ec] convers[aã]o|caixa de convers[aã]o (?:recebeu|receb[ei]|entraram)",
    "entrada_saida_moedas": r"entraram\s+[\d.]+\s*(?:libras|francos|dollars|marcos)|sa(?:h|)indo\s+[\d.]+",
    "balanco_deposito": r"(?:balan[cç]o|balancete)\s+(?:semanal|da semana)|em dep[oó]sito\s+r[eé]is|dep[oó]sito de\s+[\d.:]+\$",
    "equivalente_libras": r"equivalent[e]?s?\s+a\s+[\d.]+\.[\d]{3}[\s\-]*libras|libras\s+esterlinas?\s+[\d.]+",
    "tabela_cambio": r"cambio\s+off?ic[il]a[el]|pra[cç]a\s+90\s*d/v|90\s*d\|v|sobre\s+londres\s*[.,\s]*\d{2}",
    "cotacao_praticas": r"\b1[3-9]\s*\d{1,2}/\d{1,2}\b",  # 15 13/16, 16 1/8 etc
    "renda_alfandega": r"renda\s+d[ae]\s+alfandega",
    "premio_ouro": r"premio\s+d[eo]\s+ouro|agio\s+d[eo]\s+ouro",
    "titulos_londres_preco": r"(?:funding|emprestimo\s+de\s+18\d\d|apolices).{0,40}\b\d{2,3}\s*(?:1/[248]|3/4|5/8|7/8)\b",
}
COMPILADO = {k: re.compile(v) for k, v in PADROES.items()}


def normaliza(t: str) -> str:
    p = (
        unicodedata.normalize("NFKD", t or "")
        .encode("ascii", "ignore")
        .decode()
        .lower()
    )
    return re.sub(r"\s+", " ", p)


def paginas_triadas():
    for manifesto in sorted(TRIAGEM.glob("triagem_nome_*.csv")):
        bib, ano = manifesto.stem.split("_")[-2:]
        with open(manifesto, encoding="utf-8", newline="") as f:
            for reg in csv.DictReader(f):
                if reg["hit"] != "1":
                    continue
                p = (
                    TEXTO
                    / bib
                    / reg["source_identifier"]
                    / f"p{int(reg['page_number']):03d}.txt"
                )
                if p.is_file():
                    yield bib, ano, reg["source_identifier"], reg["page_number"], p


def main():
    contagem = Counter()
    por_ano_jornal = defaultdict(Counter)
    objetos_boletim = defaultdict(set)
    exemplos = defaultdict(list)
    n = 0
    for bib, ano, obj, pag, caminho in paginas_triadas():
        n += 1
        bruto = normaliza(caminho.read_text(encoding="utf-8", errors="replace"))
        for nome, rx in COMPILADO.items():
            m = rx.search(bruto)
            if not m:
                continue
            contagem[nome] += 1
            por_ano_jornal[nome][f"{bib}|{ano}"] += 1
            if nome == "boletim_movimento":
                objetos_boletim[f"{bib}|{ano}"].add(obj)
            if len(exemplos[nome]) < 4:
                exemplos[nome].append(
                    {
                        "bib": bib,
                        "ano": ano,
                        "objeto": obj,
                        "pagina": pag,
                        "contexto": bruto[max(0, m.start() - 200) : m.end() + 500],
                    }
                )
        if n % 2000 == 0:
            print(f"  ... {n}", file=sys.stderr, flush=True)

    # edicoes distintas com boletim, por jornal-ano
    edicoes = {k: len(v) for k, v in sorted(objetos_boletim.items())}
    saida = {
        "paginas_lidas": n,
        "paginas_com_padrao": dict(contagem.most_common()),
        "edicoes_distintas_com_boletim": edicoes,
        "por_ano_jornal": {
            k: dict(sorted(v.items())) for k, v in por_ano_jornal.items()
        },
        "exemplos": dict(exemplos),
    }
    Path(sys.argv[1]).write_text(
        json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: saida[k]
                for k in (
                    "paginas_lidas",
                    "paginas_com_padrao",
                    "edicoes_distintas_com_boletim",
                )
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
