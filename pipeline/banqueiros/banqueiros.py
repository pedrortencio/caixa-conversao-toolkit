"""Levantamento exploratorio: Rothschild e banqueiros externos no corpus.

NAO e instrumento de medida. E sondagem para o Pedro decidir se ha filao.
Reusa a regra de nome ratificada (pipeline/triagem/regra_nome) para a
intersecao com a Caixa de Conversao, em vez de inventar segundo construto.
"""

import csv
import collections
import pathlib
import re
import sqlite3
import sys
import unicodedata

REPO = pathlib.Path(sys.argv[1])
RAIZ = pathlib.Path(sys.argv[2])
SAIDA = pathlib.Path(sys.argv[3])

sys.path.insert(0, str(REPO))
from pipeline.triagem import regra_nome  # noqa: E402


def deacento(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


# --- Rothschild: pre-filtro barato, depois distancia de edicao ---
PRE_ROTH = re.compile(r"\b[rb][o0][a-z0-9]{2,8}[il1t][l1i][do0]\b")


def lev(a: str, b: str, teto: int = 3) -> int:
    if abs(len(a) - len(b)) > teto:
        return teto + 1
    ant = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(ant[j] + 1, cur[j - 1] + 1, ant[j - 1] + (ca != cb)))
        if min(cur) > teto:
            return teto + 1
        ant = cur
    return ant[-1]


# --- Outros banqueiros / casas externas ---
# Toleram ruido leve de OCR; propositalmente conservadores.
BANQUEIROS = {
    "baring": re.compile(r"\bbar[il1]ngs?\b"),
    "speyer": re.compile(r"\bspe[yi]er\b"),
    "schroder": re.compile(r"\bschr[oe][ed]er\b"),
    "london_brazilian": re.compile(
        r"london\s+(and|&|a)\s+braz[il1]|londrino\s+e\s+braz[il1]"
    ),
    "banco_ingles": re.compile(r"banco[s]?\s+(ingle[sz]|britan[il1]co)"),
    "banque_paris": re.compile(r"ban[qg]ue\s+de\s+par[il1]s|paris\s+et\s+des\s+pays"),
    "credit_lyonnais": re.compile(r"cr[e3]d[il1]t\s+l[yi]onna[il1]s"),
    "deutsche_bank": re.compile(
        r"deutsche\s+bank|banco\s+allem[ãa]o|alem[ãa]o\s+transatlant"
    ),
    "dresdner": re.compile(r"dresdner"),
    "funding": re.compile(r"\bfund[il1]ng\b"),
    "banqueiros_generico": re.compile(
        r"banqueiros?\s+(?:de\s+)?(?:ingle[sz]|londr|europ|estrange|extern|nova\s*york|par[il1]s)"
    ),
    "praca_londres": re.compile(r"pra[cç]a\s+de\s+londres"),
    "emprestimo_externo": re.compile(r"empr[e3]st[il1]mo\s+(?:externo|estrange)"),
}

bib2jornal = {}
con = sqlite3.connect(REPO / "dados" / "base" / "caixa_conversao.db")
for bib, titulo in con.execute("select bn_bib, title from newspapers"):
    bib2jornal[str(bib)] = titulo
con.close()

celula = collections.defaultdict(lambda: collections.Counter())
tokens_roth = collections.Counter()
achados = []

arquivos = sorted(RAIZ.rglob("*.txt"))
total = len(arquivos)
print(f"paginas a varrer: {total}", flush=True)

for k, f in enumerate(arquivos, 1):
    if k % 10000 == 0:
        print(f"  ... {k}/{total}", flush=True)
    try:
        bruto = f.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue

    obj = f.parent.name  # per178691_1906_07755
    bib = f.parent.parent.name
    partes = obj.split("_")
    ano = partes[1] if len(partes) > 2 else "?"
    jornal = bib2jornal.get(bib, bib)
    chave = (jornal, ano)

    celula[chave]["paginas"] += 1

    norm = regra_nome.normaliza(bruto)  # minusculas, sem acento, hifen de quebra
    tem_caixa = bool(regra_nome.encontra(bruto))
    if tem_caixa:
        celula[chave]["paginas_caixa"] += 1

    # Rothschild
    roth = []
    for cand in PRE_ROTH.findall(norm):
        if lev(cand, "rothschild", 2) <= 2:
            roth.append(cand)
    if roth:
        celula[chave]["paginas_roth"] += 1
        for t in roth:
            tokens_roth[t] += 1
        if tem_caixa:
            celula[chave]["paginas_roth_e_caixa"] += 1
        pos = norm.find(roth[0])
        ctx = norm[max(0, pos - 120) : pos + 160].replace("\n", " ")
        achados.append(
            {
                "jornal": jornal,
                "ano": ano,
                "objeto": obj,
                "pagina": f.stem,
                "termo": "rothschild",
                "variante": roth[0],
                "n_na_pagina": len(roth),
                "tem_caixa": int(tem_caixa),
                "contexto": ctx,
                "caminho": str(f),
            }
        )

    # demais casas
    for nome, pat in BANQUEIROS.items():
        m = pat.search(norm)
        if m:
            celula[chave][f"pg_{nome}"] += 1
            if tem_caixa:
                celula[chave][f"pg_{nome}_e_caixa"] += 1
                pos = m.start()
                ctx = norm[max(0, pos - 120) : pos + 160].replace("\n", " ")
                achados.append(
                    {
                        "jornal": jornal,
                        "ano": ano,
                        "objeto": obj,
                        "pagina": f.stem,
                        "termo": nome,
                        "variante": m.group(0),
                        "n_na_pagina": 1,
                        "tem_caixa": 1,
                        "contexto": ctx,
                        "caminho": str(f),
                    }
                )

SAIDA.mkdir(parents=True, exist_ok=True)

with (SAIDA / "celulas.csv").open("w", newline="", encoding="utf-8") as fh:
    campos = sorted({k for c in celula.values() for k in c})
    w = csv.writer(fh)
    w.writerow(["jornal", "ano"] + campos)
    for (j, a), c in sorted(celula.items()):
        w.writerow([j, a] + [c.get(k, 0) for k in campos])

with (SAIDA / "achados.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(
        fh,
        fieldnames=[
            "jornal",
            "ano",
            "objeto",
            "pagina",
            "termo",
            "variante",
            "n_na_pagina",
            "tem_caixa",
            "contexto",
            "caminho",
        ],
    )
    w.writeheader()
    w.writerows(achados)

with (SAIDA / "variantes_rothschild.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["variante", "ocorrencias"])
    for t, n in tokens_roth.most_common():
        w.writerow([t, n])

print()
print("=== TOTAIS ===")
tot = collections.Counter()
for c in celula.values():
    tot.update(c)
for k in sorted(tot):
    print(f"  {k}: {tot[k]}")
print()
print(f"variantes distintas de Rothschild: {len(tokens_roth)}")
print(f"ocorrencias brutas de Rothschild: {sum(tokens_roth.values())}")
print(f"linhas em achados.csv: {len(achados)}")
