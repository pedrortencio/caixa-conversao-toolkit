"""Segunda sondagem: divida soberana, subsoberana e recepcao da imprensa credora."""

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
    # dilucao / divida subsoberana
    "emprestimo_estadual": r"emprestimos?\s+(?:extern[oa]s?\s+)?d[oe]s?\s+estados|emprestimos?\s+estadua",
    "estado_lanca_emprestimo": r"(?:estado|governo)\s+d[eo]\s+s\.?\s*paulo.{0,60}emprestimo|emprestimo\s+paulista",
    "autorizacao_federal": r"sem\s+autoriza[cç][aã]o\s+(?:do\s+congresso|federal)",
    # recepcao da imprensa credora
    "brasil_no_exterior": r"o\s+brasil\s+no\s+exterior",
    "imprensa_credora": r"financial\s+(?:news|times)|the\s+economist|morning\s+post|south\s+american\s+journal|statist\b",
    # operacoes concretas
    "conversao_1910": r"convers[aã]o\s+da\s+divida|emprestimo\s+de\s+convers[aã]o",
    "typo_emissao": r"\btypo\s+de\s+\d|ao\s+typo\s+de",
    "emprestimo_libras": r"emprestimo.{0,60}(?:milh[oõ]es|milhao)\s+(?:de\s+)?(?:libras|esterlinos)",
    # deposito do ouro da Caixa nos Rothschild
    "deposito_ouro_banqueiros": r"deposito.{0,80}(?:rothschild|banqueiros|londres)|ouro\s+da\s+caixa.{0,60}(?:londres|banqueiros)",
    "juro_dois_e_meio": r"2\s*1\|2\s*%|juro\s+de\s+2",
    # cotacao / spread
    "titulos_baixa_alta": r"titulos\s+brasileiros|fundos\s+brasileiros|apolices\s+(?:federaes|da\s+divida)",
    "cotacao_praca_londres": r"(?:pra[cç]a|bolsa|mercado)\s+de\s+londres",
    # instituicoes de credores
    "portadores_organizados": r"portadores?\s+de\s+titulos|council\s+of\s+foreign|conselho\s+dos\s+portadores|bondholders",
    "arbitragem_ouro": r"arbitragem|premio\s+do\s+ouro|agio\s+d[eo]\s+ouro",
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
    por_ano = defaultdict(Counter)
    exemplos = defaultdict(list)
    n = 0
    for bib, ano, obj, pag, caminho in paginas_triadas():
        n += 1
        bruto = normaliza(caminho.read_text(encoding="utf-8", errors="replace"))
        for nome, rx in COMPILADO.items():
            ms = list(rx.finditer(bruto))
            if not ms:
                continue
            contagem[nome] += 1
            por_ano[nome][ano] += 1
            if len(exemplos[nome]) < 10:
                m = ms[0]
                exemplos[nome].append(
                    {
                        "bib": bib,
                        "ano": ano,
                        "objeto": obj,
                        "pagina": pag,
                        "contexto": bruto[max(0, m.start() - 300) : m.end() + 300],
                    }
                )
        if n % 2000 == 0:
            print(f"  ... {n}", file=sys.stderr, flush=True)

    saida = {
        "paginas_lidas": n,
        "paginas_com_padrao": dict(contagem.most_common()),
        "por_ano": {k: dict(sorted(v.items())) for k, v in por_ano.items()},
        "exemplos": dict(exemplos),
    }
    Path(sys.argv[1]).write_text(
        json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "paginas_lidas": n,
                "paginas_com_padrao": saida["paginas_com_padrao"],
                "por_ano": saida["por_ano"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
