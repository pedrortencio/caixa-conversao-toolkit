"""Referente da mencao: a Caixa brasileira ou a homonima argentina.

A Caixa de Conversao argentina, criada pela lei de 1899, e citada o tempo
todo pela imprensa brasileira. Presumir que essa citacao e ruido seria erro:
em boa parte dos casos ela e o ARGUMENTO, mobilizada a favor ou contra a
Caixa brasileira. Este modulo nao decide isso, ele apenas mede o tamanho do
problema e separa o que e artefato de marcador do que e material argentino
de fato.

Tres classes, e a fronteira entre elas nao e deterministica:

- `moeda`: a expressao "pesos argentinos" aparece na LISTA DE MOEDAS do
  boletim diario de movimento da Caixa brasileira. E rotina operacional
  brasileira, nao materia argentina. Foi o falso positivo que derrubou a
  primeira medida desta investigacao, 9,9% viraram 3,9% ao separa-lo;
- `estrita`: ha marca de materia argentina perto da mencao (dateline de
  Buenos Aires, imprensa portenha, lei argentina);
- `nenhuma`.

O que este modulo NAO faz, e nao deve fazer: dizer se a peca mobiliza o caso
argentino no debate brasileiro. Isso depende de enquadramento que o OCR
corrompe. Na janela do Correio da Manha de 23/05/1906, o vinculo com o
debate nacional esta na expressao "paladinos do Cou-veniode T abate", que
nenhuma regra de nome casa com "Convenio de Taubate". Classificar referente
por regra determinística produziria falso negativo justamente nas pecas mais
argumentativas.
"""

from __future__ import annotations

import re
import unicodedata

# Marcas de materia argentina. Fronteira de palavra e obrigatoria: sem ela,
# "la nacion" casa dentro de "Escola Nacional" e o marcador mede a si mesmo.
ESTRITAS = [
    r"buenos a[iy]res",  # a Hemeroteca traz "Aires" e "Ayres"
    r"la prensa",
    r"la nacion\b",
    r"el diario",
    r"republica argentina",
    r"governo argentino",
    r"convers[ãa]o argentina",
    r"lei argentina",
    r"piastras?\b",
]

# A moeda no boletim de movimento da Caixa brasileira.
MOEDA = r"pesos? argenti[nu]os?"

MARCA_ESTRITA = re.compile("|".join(ESTRITAS))
MARCA_MOEDA = re.compile(MOEDA)


def normaliza(texto: str) -> str:
    plano = unicodedata.normalize("NFKD", texto or "")
    plano = plano.encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", plano)


def classifica(texto: str) -> str:
    """`estrita`, `moeda` ou `nenhuma`, nessa ordem de precedencia."""
    plano = normaliza(texto)
    if MARCA_ESTRITA.search(plano):
        return "estrita"
    if MARCA_MOEDA.search(plano):
        return "moeda"
    return "nenhuma"


def marcas_encontradas(texto: str) -> list[str]:
    return MARCA_ESTRITA.findall(normaliza(texto)) or []


# --------------------------------------------------------------------------
# Varredura do corpus triado, para dimensionar a questao. Le so a camada de
# texto e os manifestos da triagem, nao toca no banco.
# --------------------------------------------------------------------------

def varre(largura: int = 1200) -> list[dict]:
    """Uma linha por janela de mencao do corpus triado, com a classe."""
    import csv
    from pathlib import Path

    from pipeline.catalogo import janela as mod_janela

    raiz = Path(__file__).resolve().parents[2]
    triagem = raiz / "dados" / "triagem"
    texto_embutido = Path("C:/dados-caixa/texto_embutido")

    linhas: list[dict] = []
    for manifesto in sorted(triagem.glob("triagem_nome_*.csv")):
        bib, ano = manifesto.stem.split("_")[-2:]
        with open(manifesto, encoding="utf-8", newline="") as arquivo:
            for registro in csv.DictReader(arquivo):
                if registro["hit"] != "1":
                    continue
                pagina = (
                    texto_embutido
                    / bib
                    / registro["source_identifier"]
                    / f"p{int(registro['page_number']):03d}.txt"
                )
                if not pagina.is_file():
                    continue
                bruto = pagina.read_text(encoding="utf-8", errors="replace")
                for j in mod_janela.janelas(bruto, largura=largura):
                    linhas.append(
                        {
                            "bib": bib,
                            "ano": ano,
                            "source_identifier": registro["source_identifier"],
                            "page_number": registro["page_number"],
                            "inicio": j.inicio,
                            "fim": j.fim,
                            "classe": classifica(j.texto),
                            "marcas": "|".join(sorted(set(marcas_encontradas(j.texto)))),
                        }
                    )
    return linhas


def main() -> None:
    import csv
    from collections import Counter
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[2]
    saida = raiz / "dados" / "analise" / "referente_argentino.csv"
    saida.parent.mkdir(parents=True, exist_ok=True)

    linhas = varre()
    with open(saida, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)

    classes = Counter(l["classe"] for l in linhas)
    total = len(linhas)
    print(f"janelas de mencao: {total}")
    for classe in ("estrita", "moeda", "nenhuma"):
        n = classes.get(classe, 0)
        print(f"  {classe}: {n} ({100 * n / total:.1f}%)")
    print("\npor ano (janelas | estritas | %):")
    por_ano: Counter[str] = Counter()
    estritas_ano: Counter[str] = Counter()
    for l in linhas:
        por_ano[l["ano"]] += 1
        if l["classe"] == "estrita":
            estritas_ano[l["ano"]] += 1
    for ano in sorted(por_ano):
        h, a = por_ano[ano], estritas_ano[ano]
        print(f"  {ano}: {h:6d} | {a:4d} | {100 * a / h:5.1f}%")
    print(f"\nmanifesto: {saida}")


if __name__ == "__main__":
    import sys
    from pathlib import Path as _Path

    sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))
    main()
