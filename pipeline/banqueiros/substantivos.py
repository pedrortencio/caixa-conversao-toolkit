"""Ranqueia candidatos SUBSTANTIVOS (na tipologia de registro de 23/07)
entre as paginas onde banqueiro externo e Caixa de Conversao co-ocorrem.

Nao decide nada: ordena para leitura humana.
"""

import csv, pathlib, re, sys, collections

REPO = pathlib.Path(sys.argv[1])
S = pathlib.Path(sys.argv[2])
JORNAL = sys.argv[3] if len(sys.argv) > 3 else None
TOPN = int(sys.argv[4]) if len(sys.argv) > 4 else 6
sys.path.insert(0, str(REPO))
from pipeline.triagem import regra_nome  # noqa: E402

PRE = re.compile(r"\b[rb][o0][a-z0-9]{2,8}[il1t][l1i][do0]\b")
BANQ = re.compile(
    r"\bbar[il1]ngs?\b|\bspe[yi]er\b|\bschr[oe][ed]er\b|banqueiros?|"
    r"london\s+(?:and|&|a)\s+braz[il1]|\bfund[il1]ng\b|pra[cç]a\s+de\s+londres"
)


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


SUB = re.compile(
    r"opini[ao]|acham|considera|julga|entende|sustenta|affirma|declar|protesta|"
    r"censur|critic|combat|defend|condemn|estranha|lament|applaud|"
    r"questao|debate|discussao|camara|senado|sessao|discurso|parlamentar|"
    r"imprensa|folha|jornal|artigo|editorial|entrevista|carta|telegramma|"
    r"garantia|lastro|conversibilidade|estabilis|estabiliz|valoris|valoriz|"
    r"tutela|soberania|credito|ortodox|padrao|convenio|taxa de|pence|"
    r"desfavoravel|favoravel|contrario|recusa|apoio|transferir|deposito"
)
NOISE = re.compile(
    r"entraram hoje|sahiram|existencia em cofre|notas dilaceradas|"
    r"kilos|jockey|prado|handicap|potro|corrida|pur.?sang|"
    r"passageiros|embarcaram|de familia|e senhora|"
    r"fallecimento|enterro|missa|"
    r"foi nomeado|exonerado|rendimento da alfandega|renda arrecadada"
)

ach = [
    a
    for a in csv.DictReader((S / "achados.csv").open(encoding="utf-8"))
    if a["tem_caixa"] == "1"
]

# dedupe por pagina, guardando o termo
porpag = {}
for a in ach:
    porpag.setdefault((a["jornal"], a["ano"], a["objeto"], a["pagina"]), a)

cands = collections.defaultdict(list)
for (j, ano, obj, pg), a in porpag.items():
    if JORNAL and j != JORNAL:
        continue
    p = pathlib.Path(a["caminho"])
    if not p.exists():
        continue
    bruto = p.read_text(encoding="utf-8", errors="replace")
    norm = regra_nome.normaliza(bruto)
    marcas = [
        m.start() for m in PRE.finditer(norm) if lev(m.group(0), "rothschild") <= 2
    ]
    marcas += [m.start() for m in BANQ.finditer(norm)]
    cx = [s.offset for s in regra_nome.encontra(bruto)]
    if not marcas or not cx:
        continue
    d, mb, mc = min(((abs(x - c), x, c) for x in marcas for c in cx))
    if d > 4000:
        continue
    ini, fim = min(mb, mc) - 350, max(mb, mc) + 350
    jan = norm[max(0, ini) : fim]
    nsub, nnoise = len(SUB.findall(jan)), len(NOISE.findall(jan))
    score = nsub - 2 * nnoise
    cands[j].append((score, nsub, nnoise, d, ano, obj, pg, jan, a["variante"]))

for j in sorted(cands):
    lst = sorted(cands[j], key=lambda t: -t[0])[:TOPN]
    print("#" * 78)
    print(f"# {j}   ({len(cands[j])} candidatos com distancia <= 4000)")
    print("#" * 78)
    for score, nsub, nnoise, d, ano, obj, pg, jan, var in lst:
        print(
            f"\n>>> {j} {ano} | {obj} {pg} | dist={d} | sub={nsub} ruido={nnoise} score={score} | var={var}"
        )
        print(jan[:1500].replace("\n", " "))
        print()
