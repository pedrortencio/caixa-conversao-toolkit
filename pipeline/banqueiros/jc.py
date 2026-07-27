"""Rothschild e banqueiros externos no Retrospecto Commercial do JC (bib 180688)."""

import pathlib, re, sys, collections

REPO = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(REPO))
from pipeline.triagem import regra_nome  # noqa: E402

PRE = re.compile(r"\b[rb][o0][a-z0-9]{2,8}[il1t][l1i][do0]\b")


def lev(a, b, teto=2):
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


OUTROS = {
    "baring": re.compile(r"\bbar[il1]ngs?\b"),
    "speyer": re.compile(r"\bspe[yi]er\b"),
    "schroder": re.compile(r"\bschr[oe][ed]er\b"),
    "london_brazilian": re.compile(
        r"london\s+(and|&|a)\s+braz[il1]|londrino\s+e\s+braz[il1]"
    ),
    "banqueiros": re.compile(r"banqueiros?"),
    "funding": re.compile(r"\bfund[il1]ng\b"),
    "praca_londres": re.compile(r"pra[cç]a\s+de\s+londres"),
    "emprestimo_externo": re.compile(r"empr[e3]st[il1]mo\s+(?:externo|estrange)"),
    "caja_argentina": re.compile(r"ca[ij]a\s+de\s+conversi[oó]n|argentin"),
}

d = REPO / "dados" / "retrospecto_jc"
tot = collections.Counter()
for f in sorted(d.glob("retrospecto_*_caixa.txt")):
    ano = f.stem.split("_")[1]
    norm = regra_nome.normaliza(f.read_text(encoding="utf-8", errors="replace"))
    roth = [
        (m.start(), m.group(0))
        for m in PRE.finditer(norm)
        if lev(m.group(0), "rothschild") <= 2
    ]
    cx = [
        s.offset
        for s in regra_nome.encontra(f.read_text(encoding="utf-8", errors="replace"))
    ]
    linha = {k: len(pat.findall(norm)) for k, pat in OUTROS.items()}
    tot["rothschild"] += len(roth)
    for k, v in linha.items():
        tot[k] += v
    print(f"--- {ano}  ({len(norm):,} chars, {len(cx)} mencoes a Caixa) ---")
    print(
        f"    rothschild={len(roth)}  "
        + "  ".join(f"{k}={v}" for k, v in linha.items() if v)
    )
    for pos, var in roth[:4]:
        ctx = norm[max(0, pos - 500) : pos + 500].replace("\n", " ")
        print(f"    [{var}] ...{ctx}...")
    print()

print("=== TOTAIS NO RETROSPECTO ===")
for k, v in tot.most_common():
    print(f"  {k}: {v}")
