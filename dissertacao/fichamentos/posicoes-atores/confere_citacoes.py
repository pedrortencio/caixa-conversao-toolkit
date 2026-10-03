"""Conferencia mecanica das citacoes diretas do fichamento de fontes primarias.

Extrai, na ordem em que o LaTeX as compoe, cada \\tr[FONTE]{texto} e cada
\\cit[FONTE]{texto}{referencia} de introducao.tex, fichas/*.tex e sintese.tex
(na ordem dos \\input de main.tex) e confronta o texto, normalizado, com a fonte:

  P:vol:pdf         camada corrigida dos Documentos Parlamentares, pagina do PDF
                    (procura tambem nas 3 paginas vizinhas de cada lado)
  I:edicao:pagina   texto embutido da Hemeroteca (OCR-BN), pagina indicada

Normalizacao: minusculas, sem acento, so letras e algarismos. Elipses "[...]" e
interpolacoes entre colchetes dividem a citacao em segmentos, conferidos um a um;
vale o pior segmento.

Vereditos, na regra do projeto (citacao que nao casa e rejeitada, nunca corrigida):

  literal       substring literal da fonte normalizada
  aproximada    melhor janela com similaridade >= 0,85 (ruido de OCR, quebra de
                coluna). Nao e aprovacao plena: pede conferencia na imagem
  rejeitada     o resto

Saidas: relatorio-conferencia-citacoes.md e conferencia-status.tex (marca com
adaga, no PDF, as citacoes aproximadas). Sai com 1 se houver rejeitada.

Uso: uv run python dissertacao/fichamentos/posicoes-atores/confere_citacoes.py
"""

from __future__ import annotations

import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[2]
PARL = REPO / "dados" / "texto_corrigido" / "fontes_parlamentares" / "caixa_conversao"
OCR = Path("C:/dados-caixa/texto_embutido")
LIMIAR = 0.85
VIZINHAS = 3


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s)


def le_grupo(t: str, i: int, abre: str, fecha: str) -> tuple[str, int]:
    """Le um grupo balanceado que comeca em t[i] == abre. Devolve conteudo e posicao seguinte."""
    assert t[i] == abre, (t[i - 20 : i + 20], abre)
    prof, j = 0, i
    while True:
        c = t[j]
        if c == "\\":
            j += 2
            continue
        if c == abre:
            prof += 1
        elif c == fecha:
            prof -= 1
            if prof == 0:
                return t[i + 1 : j], j + 1
        j += 1


def extrai(arq: Path) -> list[dict]:
    t = arq.read_text(encoding="utf-8")
    t = re.sub(r"(?<!\\)%.*", "", t)  # tira comentarios
    achados = []
    for m in re.finditer(r"\\(tr|cit)\[", t):
        fonte, j = le_grupo(t, m.end() - 1, "[", "]")
        texto, j = le_grupo(t, j, "{", "}")
        linha = t.count("\n", 0, m.start()) + 1
        achados.append({"arq": arq.name, "linha": linha, "macro": m.group(1), "fonte": fonte.strip(), "texto": texto})
    return achados


def limpa_latex(s: str) -> str:
    s = re.sub(r"\\([$%&_#])", r"\1", s)
    s = s.replace("~", " ").replace("``", '"').replace("''", '"')
    return s


_cache: dict[str, dict[int, str]] = {}


def paginas(fonte: str) -> dict[int, str]:
    tipo, a, b = fonte.split(":")
    if tipo == "P":
        chave = f"P{a}"
        if chave not in _cache:
            arq = PARL / f"caixa_conversao_v{a}_paginas_corrigidas.jsonl"
            _cache[chave] = {
                d["pdf_page"]: norm(d["corrected_text"])
                for d in map(json.loads, arq.read_text(encoding="utf-8").splitlines())
            }
        p = int(b)
        return {q: _cache[chave].get(q, "") for q in range(p - VIZINHAS, p + VIZINHAS + 1)}
    if tipo == "I":
        arq = OCR / a[3:9] / a / f"p{int(b):03d}.txt"
        return {int(b): norm(arq.read_text(encoding="utf-8", errors="replace"))}
    raise ValueError(fonte)


def melhor(q: str, alvo: dict[int, str]) -> float:
    best = 0.0
    for txt in alvo.values():
        if q in txt:
            return 1.0
        n = len(q)
        passo = max(1, n // 6)
        sm = difflib.SequenceMatcher(autojunk=False)
        sm.set_seq2(q)
        for i in range(0, max(1, len(txt) - n + 1), passo):
            sm.set_seq1(txt[i : i + n])
            if sm.real_quick_ratio() <= best or sm.quick_ratio() <= best:
                continue
            best = max(best, sm.ratio())
    return best


def confere(c: dict) -> tuple[str, float]:
    alvo = paginas(c["fonte"])
    segs = [norm(s) for s in re.split(r"\[[^\]]*\]", limpa_latex(c["texto"]))]
    segs = [s for s in segs if len(s) >= 8]
    if not segs:
        return "rejeitada", 0.0
    pior = min(melhor(s, alvo) for s in segs)
    if pior == 1.0:
        return "literal", 1.0
    return ("aproximada" if pior >= LIMIAR else "rejeitada"), pior


def main() -> int:
    ordem = re.findall(r"\\input\{([^}]+)\}", (AQUI / "main.tex").read_text(encoding="utf-8"))
    arqs = [AQUI / f"{o}.tex" for o in ordem if not o.startswith("..")]
    cits = [c for a in arqs if a.exists() for c in extrai(a)]
    linhas, status, cont = [], [], {"literal": 0, "aproximada": 0, "rejeitada": 0}
    for n, c in enumerate(cits, 1):
        try:
            v, s = confere(c)
        except (FileNotFoundError, ValueError) as e:
            v, s = "rejeitada", 0.0
            c["erro"] = repr(e)
        cont[v] += 1
        trecho = re.sub(r"\s+", " ", limpa_latex(c["texto"])).replace("|", "/")
        trecho = trecho if len(trecho) <= 90 else trecho[:87] + "..."
        linhas.append(f"| {n} | {c['arq']}:{c['linha']} | `{c['fonte']}` | {v} | {s:.2f} | {trecho} |")
        if v == "aproximada":
            status.append(f"\\expandafter\\def\\csname stcit@{n}\\endcsname{{\\textsuperscript{{\\dag}}}}")
        elif v == "rejeitada":
            status.append(f"\\expandafter\\def\\csname stcit@{n}\\endcsname{{\\textsuperscript{{\\ddag}}}}")
    total = len(cits)
    rel = [
        "# Conferência mecânica das citações do fichamento de fontes primárias",
        "",
        "**Instrumento:** `confere_citacoes.py`. **Custo de API: zero.**",
        "",
        f"Sobre {total} citações diretas: **{cont['literal']} literais, {cont['aproximada']} aproximadas, "
        f"{cont['rejeitada']} rejeitadas**.",
        "",
        "`aproximada` não é aprovação plena: é citação lida sobre OCR ruidoso ou cortada por quebra de coluna,",
        "com similaridade de pelo menos 0,85, e pede conferência na imagem antes de ir para a dissertação.",
        "",
        "| n | arquivo:linha | fonte | veredito | sim. | trecho |",
        "|---|---|---|---|---|---|",
        *linhas,
        "",
    ]
    (AQUI / "relatorio-conferencia-citacoes.md").write_text("\n".join(rel), encoding="utf-8")
    (AQUI / "conferencia-status.tex").write_text(
        "% Gerado por confere_citacoes.py. Nao editar.\n\\makeatletter\n" + "\n".join(status) + "\n\\makeatother\n",
        encoding="utf-8",
    )
    print(f"{total} citacoes: {cont}")
    for l in linhas:
        if "| literal |" not in l:
            print(l)
    return 1 if cont["rejeitada"] else 0


if __name__ == "__main__":
    sys.exit(main())
