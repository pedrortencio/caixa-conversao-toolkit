"""A co-ocorrencia na PAGINA e relacao topica ou vizinhanca de coluna?

Mede a distancia minima em caracteres entre a mencao a Rothschild e a mencao
a Caixa de Conversao, nas 170 paginas onde as duas aparecem. Numa pagina de
jornal-lencol com 30-40 mil caracteres, "mesma pagina" pode nao significar nada.
"""

import csv, pathlib, re, statistics, sys, collections

REPO = pathlib.Path(sys.argv[1])
S = pathlib.Path(sys.argv[2])
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


# marcadores baratos de secao ruidosa
RUIDO = {
    "turfe": re.compile(
        r"\b(kilos|jockey|corrida|prado|handicap|pur[- ]?sang|potro|[0-9] a\.,)\b"
    ),
    "passageiros": re.compile(
        r"\b(passageiros|paquete .{0,40}chegou|embarcaram|de familia|e senhora)\b"
    ),
    "obituario": re.compile(r"\b(fallecimento|fallecido|enterro|missa)\b"),
    "financeiro": re.compile(
        r"\b(emprestimo|thesouro|libras|cambio|banqueiros?|resgate|apolices|funding|remessa)\b"
    ),
}

ach = [
    a
    for a in csv.DictReader((S / "achados.csv").open(encoding="utf-8"))
    if a["termo"] == "rothschild" and a["tem_caixa"] == "1"
]

dists, linhas = [], []
marc = collections.Counter()
for a in ach:
    p = pathlib.Path(a["caminho"])
    if not p.exists():
        continue
    norm = regra_nome.normaliza(p.read_text(encoding="utf-8", errors="replace"))
    roth = [m.start() for m in PRE.finditer(norm) if lev(m.group(0), "rothschild") <= 2]
    caixa = [
        s.offset
        for s in regra_nome.encontra(p.read_text(encoding="utf-8", errors="replace"))
    ]
    if not roth or not caixa:
        continue
    d = min(abs(r - c) for r in roth for c in caixa)
    dists.append(d)
    ctx = norm[max(0, min(roth) - 400) : min(roth) + 400]
    tags = [k for k, pat in RUIDO.items() if pat.search(ctx)]
    for t in tags:
        marc[t] += 1
    if not tags:
        marc["sem_marcador"] += 1
    linhas.append(
        (d, a["jornal"], a["ano"], a["objeto"], a["pagina"], ",".join(tags), len(norm))
    )

print(f"paginas medidas: {len(dists)}")
print(
    f"tamanho medio da pagina: {statistics.mean(l[6] for l in linhas):,.0f} caracteres"
)
print()
print("=== DISTANCIA MINIMA Rothschild <-> Caixa de Conversao (caracteres) ===")
print(f"  mediana: {statistics.median(dists):,.0f}")
print(f"  media:   {statistics.mean(dists):,.0f}")
faixas = [(0, 200), (200, 1000), (1000, 5000), (5000, 15000), (15000, 10**9)]
for lo, hi in faixas:
    n = sum(1 for d in dists if lo <= d < hi)
    rot = "#" * int(40 * n / len(dists))
    et = f"{lo:,}-{hi:,}" if hi < 10**9 else f">{lo:,}"
    print(f"  {et:>15s}  {n:4d}  {100 * n / len(dists):5.1f}%  {rot}")

print()
print("=== MARCADOR DE SECAO NO ENTORNO DA MENCAO (800 chars) ===")
for k, n in marc.most_common():
    print(f"  {k:14s} {n:4d}  {100 * n / len(dists):5.1f}%")

print()
print("=== AS 15 PAGINAS MAIS PROXIMAS (candidatas a relacao real) ===")
linhas.sort()
for d, j, a, o, pg, tags, _ in linhas[:15]:
    print(f"  {d:6,d} ch  {j:20s} {a}  {o} {pg}  [{tags}]")

with (S / "proximidade.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(
        [
            "distancia_chars",
            "jornal",
            "ano",
            "objeto",
            "pagina",
            "marcadores",
            "chars_pagina",
        ]
    )
    w.writerows(linhas)
