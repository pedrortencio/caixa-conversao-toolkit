"""Estimativa do subcorpus substantivo: a medida pivo do desenho de mensuracao.

Script exploratorio (sem testes ainda, ver docs/estado-2026-07-23-pos-rotulagem.md).
Custo zero: combina dois artefatos deterministicos ja existentes.

  - manifestos da triagem por nome (`dados/triagem/triagem_nome_*.csv`):
    censo completo de matches por edicao;
  - rotulagem de registro (`dados/triagem/rotulagem_registro.xlsx`):
    amostra estratificada com a proporcao de matches substantivos.

Pergunta que responde (docs/desenhos-concorrentes.md, secao Dependencias):
quantas edicoes-dia discutem a Caixa de forma substantiva? O numero decide se
D-Humano cobre a posicao por censo ou apenas por amostra.

Uso: uv run python pipeline/triagem/estima_subcorpus.py
"""

import glob
from pathlib import Path

import numpy as np
import pandas as pd

BIB2JORNAL = {
    "089842": "correio_manha",
    "090972": "correio_paulistano",
    "103730": "gazeta_noticias",
    "178691": "o_paiz",
}
# Gabarito do piloto de 1906 (CLAUDE.md), usado como calibracao externa.
GABARITO_1906 = {
    "o_paiz": 79,
    "correio_paulistano": 94,
    "gazeta_noticias": 146,
    "correio_manha": 110,
}
SEMENTE = 20260723
B = 2000


def carrega_censo_matches() -> pd.DataFrame:
    """Matches por edicao, do censo completo da triagem por nome."""
    frames = []
    for caminho in glob.glob("dados/triagem/triagem_nome_*.csv"):
        nome = caminho.replace("\\", "/").split("/")[-1]
        bib, ano = nome.replace(".csv", "").split("_")[2:4]
        d = pd.read_csv(caminho, engine="python", usecols=["source_identifier", "n_matches"])
        d["jornal"] = BIB2JORNAL[bib]
        d["ano"] = int(ano)
        frames.append(d)
    pag = pd.concat(frames, ignore_index=True)
    ed = pag.groupby(["jornal", "ano", "source_identifier"], as_index=False)["n_matches"].sum()
    return ed[ed["n_matches"] > 0].copy()


XLSX_ROTULAGEM = "dados/triagem/rotulagem_registro.xlsx"
CSV_AMOSTRA = "dados/triagem/amostra_para_rotular.csv"


def carrega_rotulagem(
    caminho_xlsx: str | Path = XLSX_ROTULAGEM,
    caminho_amostra: str | Path = CSV_AMOSTRA,
) -> pd.DataFrame:
    """Amostra rotulada, so as celulas decididas (branco = indeterminado) de
    pecas que sobreviveram a limpeza (`status == keep`).

    O filtro por status importa: a correcao do vazamento de disclaimer
    (2026-07-25) descartou 19 itens que ja estavam na planilha, 3 deles
    rotulados. Sem o filtro, eles seguiriam no denominador substantivo.
    """
    rot = pd.read_excel(caminho_xlsx)
    src = pd.read_csv(caminho_amostra, engine="python")
    rot = rot.merge(
        src[["item_id", "source_year", "status"]], on="item_id", how="left"
    )
    rot = rot[(rot["registro"].notna()) & (rot["status"] == "keep")].copy()
    rot["subst"] = (rot["registro"] == "substantivo").astype(int)
    return rot


def projeta(rot: pd.DataFrame, ed_hit: pd.DataFrame) -> tuple[float, float]:
    """Piso e teto de edicoes substantivas.

    Piso: registros perfeitamente correlacionados dentro da edicao (p * N).
    Teto: registros independentes dentro da edicao (1 - (1-p)^k somado).
    A verdade fica entre os dois; a mediana de matches por edicao e 1, entao
    a faixa e estreita.
    """
    p = rot.groupby("source_year")["subst"].mean()
    piso = teto = 0.0
    for ano, g in ed_hit.groupby("ano"):
        pa = p.get(ano, np.nan)
        if np.isnan(pa):
            continue
        piso += pa * len(g)
        teto += (1 - (1 - pa) ** g["n_matches"].values).sum()
    return piso, teto


def main() -> None:
    ed_hit = carrega_censo_matches()
    rot = carrega_rotulagem()

    print("== censo de matches ==")
    print(f"edicoes com ao menos um match: {len(ed_hit)}")
    print(f"matches totais: {int(ed_hit['n_matches'].sum())}")
    print(f"matches por edicao: mediana {ed_hit['n_matches'].median():.0f}, "
          f"media {ed_hit['n_matches'].mean():.2f}")

    print("\n== calibracao contra o gabarito de 1906 ==")
    e06 = ed_hit[ed_hit["ano"] == 1906]
    for jornal, g in e06.groupby("jornal"):
        p = rot[(rot["source_year"] == 1906) & (rot["jornal"] == jornal)]["subst"].mean()
        print(f"  {jornal:20s} previsto {round(p * len(g)):4d}   gabarito {GABARITO_1906[jornal]:4d}")
    p06 = rot[rot["source_year"] == 1906]["subst"].mean()
    print(f"  {'TOTAL':20s} previsto {round(p06 * len(e06)):4d}   "
          f"gabarito {sum(GABARITO_1906.values()):4d}")

    piso, teto = projeta(rot, ed_hit)
    rng = np.random.default_rng(SEMENTE)
    boot = []
    for _ in range(B):
        partes = [
            g.sample(len(g), replace=True, random_state=int(rng.integers(1 << 31)))
            for _, g in rot.groupby("source_year")
        ]
        boot.append(projeta(pd.concat(partes, ignore_index=True), ed_hit))
    boot = np.array(boot)

    print("\n== projecao por ano ==")
    p = rot.groupby("source_year")["subst"].mean()
    linhas = [
        {
            "ano": ano,
            "edicoes_com_match": len(g),
            "p_subst": round(p.loc[ano], 3),
            "n_rotulado": int((rot["source_year"] == ano).sum()),
            "piso": round(p.loc[ano] * len(g)),
            "teto": round((1 - (1 - p.loc[ano]) ** g["n_matches"].values).sum()),
        }
        for ano, g in ed_hit.groupby("ano")
    ]
    print(pd.DataFrame(linhas).to_string(index=False))

    print("\n== subcorpus substantivo (bootstrap por ano, 2000 reamostragens) ==")
    print(f"piso: {piso:.0f}  IC95 [{np.percentile(boot[:, 0], 2.5):.0f}, "
          f"{np.percentile(boot[:, 0], 97.5):.0f}]")
    print(f"teto: {teto:.0f}  IC95 [{np.percentile(boot[:, 1], 2.5):.0f}, "
          f"{np.percentile(boot[:, 1], 97.5):.0f}]")
    print("\n== horas de leitura implicadas ==")
    for nome, n in (("piso", piso), ("teto", teto)):
        faixas = ", ".join(f"{m} min/ed = {n * m / 60:.0f} h" for m in (2, 4, 6))
        print(f"  {nome} ({n:.0f} edicoes): {faixas}")


if __name__ == "__main__":
    main()
