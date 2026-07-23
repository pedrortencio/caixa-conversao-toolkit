"""Diagnostico da amostra rotulavel: escala da truncagem + variante de nome.

EXPLORATORIO (2026-07-23). Backing dos numeros reportados em docs/decisoes.md.
So mede, nao altera nada. (1) Truncagem: quantas keep comecam no meio de frase
(minusculo), quantas nao terminam em pontuacao, quantas em ambos (o caso ruim),
quantas curtas. (2) Variante 'Caixa de Emissao e Conversao' (nome do Convenio
de Taubate): quantas keep a contem e, dessas, quantas NAO teriam sido pegas por
um match plano da regra atual (perda de recall real).
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if __package__ in {None, ""}:
    sys.path.insert(0, str(RAIZ))

from pipeline.triagem import regra_nome

CSV = RAIZ / "dados" / "triagem" / "amostra_para_rotular.csv"

VAR = re.compile(r"caixa d\w? emiss\w* e conver")
TERMINAL = tuple(".!?\"»)")


def main() -> int:
    with open(CSV, encoding="utf-8", newline="") as f:
        keep = [r for r in csv.DictReader(f) if r["status"] == "keep"]

    ini_min = sem_fim = ambos = curtos = 0
    var_hits = var_so_variante = 0
    for r in keep:
        t = (r["texto"] or "").strip()
        norm = regra_nome.normaliza(t)
        a = bool(t) and t[0].islower()
        b = bool(t) and not t.rstrip().endswith(TERMINAL)
        ini_min += a
        sem_fim += b
        ambos += a and b
        curtos += len(t) < 200
        if VAR.search(norm):
            var_hits += 1
            if not regra_nome.encontra(t):
                var_so_variante += 1

    n = len(keep)
    print(f"keep total: {n}")
    print(f"inicio minusculo (comeca no meio): {ini_min} ({ini_min * 100 // n}%)")
    print(f"sem pontuacao final:               {sem_fim} ({sem_fim * 100 // n}%)")
    print(f"AMBOS (truncado dos dois lados):   {ambos} ({ambos * 100 // n}%)")
    print(f"texto < 200 chars:                 {curtos} ({curtos * 100 // n}%)")
    print(f"variante 'emissao e conversao' em: {var_hits} keep; "
          f"sem match plano: {var_so_variante}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
