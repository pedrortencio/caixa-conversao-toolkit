"""Sondagem exploratoria: temas da agenda de Rui Pedro Esteves no corpus.

NAO e instrumento. Nao seleciona nem estrutura segundo o construto do objeto 2.
Apenas conta ocorrencia de padroes lexicais e guarda contexto, para saber o
que existe na base antes de afirmar qualquer coisa a um economista de divida
soberana.
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
    # divida externa e o funding
    "funding": r"funding\s*-?\s*loan|funding|fundingloan",
    "emprestimo_externo": r"emprestimo\s+(?:externo|de\s+conversao|federal)",
    "divida_externa": r"divida\s+externa",
    "servico_da_divida": r"servi[cç]o\s+d[ae]s?\s+divida",
    # titulos e cotacao
    "apolices_titulos": r"\bap[oó]lices\b|\bt[ií]tulos\s+brasileiros\b|fundos\s+brasileiros",
    "cotacao_londres": r"(?:pra[cç]a|bolsa|mercado)\s+de\s+londres|em\s+londres.{0,40}cota",
    "juro_taxa_emprestimo": r"juros?\s+de\s+\d",
    # agentes financeiros e casas
    "agentes_financeiros": r"agentes?\s+financeir[oa]s?",
    "rothschild": r"rothschild|rotschild|rothsch",
    "outras_casas": r"\bspeyer\b|\bbaring\b|schr[oö]der|cr[eé]dit\s+lyonnais|\bdisconto\b|p[eé]rier",
    # expertise metropolitana citada
    "rafalovich": r"rafalovich|rafalovitch|raffalovich",
    "ansiaux": r"ansiaux",
    "leroy_beaulieu": r"leroy[- ]?beaulieu",
    "the_economist": r"the\s+economist|\beconomist\b",
    "financial_news": r"financial\s+(?:news|times)|south\s+american\s+journal",
    # regime cambial / trilema
    "credito_externo": r"cr[eé]dito\s+(?:externo|do\s+paiz|do\s+pa[ií]s|internacional)",
    "confianca_capital_estrangeiro": r"capit(?:a[li]|aes)\s+estrangeir[oa]s?|capitalistas\s+europeus",
    "padrao_ouro": r"padr[aã]o\s+ouro|circula[cç][aã]o\s+metallica|circula[cç][aã]o\s+met[aá]lica",
    "fuga_de_ouro": r"sahida\s+d[eo]\s+ouro|saida\s+d[eo]\s+ouro|exporta[cç][aã]o\s+d[eo]\s+ouro",
    "fundo_de_garantia": r"fundo\s+de\s+garantia",
    "moratoria_default": r"morat[oó]ria|banca?rota|repudi(?:o|ar)\s+d[ae]\s+divida",
}
COMPILADO = {k: re.compile(v) for k, v in PADROES.items()}
CAIXA = re.compile(r"caixa\s+de\s+conv")


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


def main(limite_exemplos: int = 6):
    contagem = Counter()
    por_ano = defaultdict(Counter)
    por_jornal = defaultdict(Counter)
    coocorre_caixa = Counter()  # padrao a <=300 chars da mencao da Caixa
    exemplos = defaultdict(list)
    n_pag = 0

    for bib, ano, obj, pag, caminho in paginas_triadas():
        n_pag += 1
        bruto = normaliza(caminho.read_text(encoding="utf-8", errors="replace"))
        pos_caixa = [m.start() for m in CAIXA.finditer(bruto)]
        for nome, rx in COMPILADO.items():
            achados = list(rx.finditer(bruto))
            if not achados:
                continue
            contagem[nome] += 1
            por_ano[nome][ano] += 1
            por_jornal[nome][bib] += 1
            perto = any(
                any(abs(m.start() - c) <= 300 for c in pos_caixa) for m in achados
            )
            if perto:
                coocorre_caixa[nome] += 1
            if len(exemplos[nome]) < limite_exemplos:
                m = achados[0]
                exemplos[nome].append(
                    {
                        "bib": bib,
                        "ano": ano,
                        "objeto": obj,
                        "pagina": pag,
                        "perto_da_caixa": perto,
                        "contexto": bruto[max(0, m.start() - 220) : m.end() + 220],
                    }
                )
        if n_pag % 1000 == 0:
            print(f"  ... {n_pag} paginas", file=sys.stderr, flush=True)

    saida = {
        "paginas_lidas": n_pag,
        "paginas_com_padrao": dict(contagem.most_common()),
        "paginas_com_padrao_perto_da_caixa_300c": dict(coocorre_caixa.most_common()),
        "por_ano": {k: dict(sorted(v.items())) for k, v in por_ano.items()},
        "por_jornal": {k: dict(sorted(v.items())) for k, v in por_jornal.items()},
        "exemplos": {k: v for k, v in exemplos.items()},
    }
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("sonda_esteves.json")
    destino.write_text(
        json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: saida[k]
                for k in (
                    "paginas_lidas",
                    "paginas_com_padrao",
                    "paginas_com_padrao_perto_da_caixa_300c",
                )
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
