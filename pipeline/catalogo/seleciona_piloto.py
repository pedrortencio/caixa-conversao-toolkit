"""Seleciona as janelas do piloto de catalogacao, de forma deterministica.

Estratifica por jornal e fase do codebook, sorteia com semente fixa e grava
as janelas em JSONL, com o texto CRU embutido. O arquivo gerado e o insumo
identico dos dois anotadores (Claude e Codex), para que a comparacao seja
sobre a anotacao e nao sobre o material.

Uso:
  uv run python pipeline/catalogo/seleciona_piloto.py --por-celula 3
"""

from __future__ import annotations

import argparse
import glob
import json
import random
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.catalogo import janela as mod_janela

SEMENTE = 20260728
DIR_TEXTO = Path("C:/dados-caixa/texto_embutido")
SAIDA = Path("dados/catalogo/piloto_janelas.jsonl")

BIB2JORNAL = {
    "089842": "correio_manha",
    "090972": "correio_paulistano",
    "103730": "gazeta_noticias",
    "178691": "o_paiz",
}


def fase(ano: int) -> str:
    if ano <= 1906:
        return "F1"
    if ano <= 1909:
        return "F2"
    if ano <= 1913:
        return "F3"
    return "F4"


def paginas_com_mencao() -> list[dict]:
    """Censo das paginas com match, direto dos manifestos versionados."""
    linhas: list[dict] = []
    for caminho in sorted(glob.glob("dados/triagem/triagem_nome_*.csv")):
        nome = Path(caminho).name
        bib, ano = nome.replace(".csv", "").split("_")[2:4]
        import csv

        with open(caminho, encoding="utf-8", newline="") as arquivo:
            for linha in csv.DictReader(arquivo):
                if linha["hit"] != "1":
                    continue
                linhas.append(
                    {
                        "bib": bib,
                        "jornal": BIB2JORNAL[bib],
                        "ano": int(ano),
                        "fase": fase(int(ano)),
                        "source_identifier": linha["source_identifier"],
                        "page_number": int(linha["page_number"]),
                        "n_matches": int(linha["n_matches"]),
                    }
                )
    return linhas


def caminho_texto(bib: str, source_identifier: str, page_number: int) -> Path:
    return DIR_TEXTO / bib / source_identifier / f"p{page_number:03d}.txt"


def seleciona(por_celula: int, largura: int) -> list[dict]:
    """Ate `por_celula` janelas por (jornal, fase), semente fixa.

    Prefere as paginas com mais mencoes dentro de cada celula: a janela com
    debate denso e a que testa o anotador, e a de rotina ja esta coberta
    pela rotulagem de registro.
    """
    rng = random.Random(SEMENTE)
    celulas: dict[tuple[str, str], list[dict]] = {}
    for pagina in paginas_com_mencao():
        celulas.setdefault((pagina["jornal"], pagina["fase"]), []).append(pagina)

    escolhidas: list[dict] = []
    for chave in sorted(celulas):
        populacao = sorted(
            celulas[chave],
            key=lambda p: (-p["n_matches"], p["source_identifier"], p["page_number"]),
        )
        candidatas = populacao[: max(por_celula * 5, 20)]
        for pagina in rng.sample(candidatas, min(por_celula, len(candidatas))):
            caminho = caminho_texto(
                pagina["bib"], pagina["source_identifier"], pagina["page_number"]
            )
            if not caminho.is_file():
                continue
            texto = caminho.read_text(encoding="utf-8", errors="replace")
            janelas = mod_janela.janelas(texto, largura=largura)
            if not janelas:
                continue
            maior = max(janelas, key=lambda j: (j.n_mencoes, len(j.texto)))
            escolhidas.append(
                {
                    "janela_id": mod_janela.janela_id(
                        pagina["source_identifier"], pagina["page_number"], maior
                    ),
                    "jornal": pagina["jornal"],
                    "ano": pagina["ano"],
                    "fase": pagina["fase"],
                    "source_identifier": pagina["source_identifier"],
                    "page_number": pagina["page_number"],
                    "inicio": maior.inicio,
                    "fim": maior.fim,
                    "n_mencoes": maior.n_mencoes,
                    "texto": maior.texto,
                }
            )
    return sorted(escolhidas, key=lambda j: j["janela_id"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--por-celula", type=int, default=3)
    parser.add_argument("--largura", type=int, default=mod_janela.LARGURA_PADRAO)
    parser.add_argument("--saida", type=Path, default=SAIDA)
    args = parser.parse_args()

    janelas = seleciona(args.por_celula, args.largura)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with open(args.saida, "w", encoding="utf-8", newline="\n") as arquivo:
        for registro in janelas:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

    chars = sum(len(j["texto"]) for j in janelas)
    print(f"semente {SEMENTE} | largura {args.largura}")
    print(f"janelas: {len(janelas)}")
    print(f"caracteres: {chars:,}  (~{chars / 4 / 1000:.1f}k tokens de entrada)")
    celulas: dict[tuple[str, str], int] = {}
    for j in janelas:
        chave = (j["jornal"], j["fase"])
        celulas[chave] = celulas.get(chave, 0) + 1
    print("\ncobertura jornal x fase:")
    for chave in sorted(celulas):
        print(f"  {chave[0]:20s} {chave[1]}  {celulas[chave]}")
    print(f"\nescrito em {args.saida}")


if __name__ == "__main__":
    main()
