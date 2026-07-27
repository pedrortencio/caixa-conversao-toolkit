"""Calibracao: quais variantes de OCR o nome Rothschild realmente assume."""

import re, sys, collections, pathlib

root = pathlib.Path(sys.argv[1])

# Bem frouxo de proposito: token comecando em R/B (R vira B no OCR gotico)
# com miolo qualquer e terminando em ld/id/1d. Serve para DESCOBRIR variantes.
frouxo = re.compile(r"\b[RB][a-zA-Z0-9ºªàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ]{4,12}[li1][ld1]\b")

alvo = re.compile(r"(?i)r.{0,2}t.{0,2}s?c?h", re.S)

cont = collections.Counter()
paginas = 0
for f in sorted(root.rglob("*.txt")):
    try:
        txt = f.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    paginas += 1
    for m in frouxo.findall(txt):
        # so guarda o que plausivelmente e Rothschild-like
        low = m.lower()
        if low.startswith(("ro", "bo", "ra", "ba")) and (
            "h" in low or "c" in low or "s" in low
        ):
            cont[m] += 1

print(f"paginas lidas: {paginas}")
print(f"tokens distintos candidatos: {len(cont)}")
print()
print("=== TOP 60 candidatos ===")
for tok, n in cont.most_common(60):
    print(f"{n:6d}  {tok}")
