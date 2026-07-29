"""Amostra de leitura para caracterizacao das fases do codebook.

Protocolo: docs/plano-leitura-fases.md. Custo zero de API: combina dois
artefatos deterministicos ja versionados.

  - `dados/triagem/amostra_para_rotular.csv`: pecas extraidas, com data,
    forma, secao, titulo e status de limpeza;
  - `dados/triagem/rotulagem_registro.xlsx`: rotulo de registro atribuido
    por Pedro (substantivo, operacional_rotina, incidental).

Produz a ficha de leitura com a identificacao pre-preenchida e o manifesto
da selecao. Nao decide construto e nao atribui posicao.

Saidas:
  - `dados/leitura/fichas_leitura.csv` (uma linha por peca)
  - `dados/leitura/auditoria_recall_edicoes.csv` (uma linha por edicao sem mencao)

Uso: uv run python pipeline/triagem/amostra_leitura.py
"""

import glob
from pathlib import Path

import pandas as pd

SEMENTE = 20260728
MIN_CELULA = 6  # pecas substantivas por fase x jornal, somando camadas 0 a 2
COTA_ROTINA = 3  # pecas operacional_rotina por fase
COTA_INCIDENTAL = 2  # pecas incidental por fase
COTA_SEM_MENCAO = 4  # edicoes sem mencao por fase x jornal (auditoria de recall)

CSV_AMOSTRA = "dados/triagem/amostra_para_rotular.csv"
XLSX_ROTULAGEM = "dados/triagem/rotulagem_registro.xlsx"
DIR_SAIDA = Path("dados/leitura")

BIB2JORNAL = {
    "089842": "correio_manha",
    "090972": "correio_paulistano",
    "103730": "gazeta_noticias",
    "178691": "o_paiz",
}

# Janelas da secao 19 de docs/contexto-bibliografia-caixa-conversao.md que caem
# no recorte. A janela de 1908 fica no ano inteiro: a data do emprestimo de
# Paris ainda nao foi conferida na historiografia (fila de leitura, item 6).
EPISODIOS = {
    "criacao": ("1906-08-01", "1906-12-31"),
    "paris_1908": ("1908-01-01", "1908-12-31"),
    "taxa_16d": ("1910-10-01", "1911-03-31"),
    "suspensao": ("1914-07-01", "1914-12-31"),
}

# `direcao_por_objeto` no lugar de um veredito holistico na escala: a escala e
# derivavel dos atributos, o caminho inverso nao existe, e o benchmark do
# artefato 6 ainda nao escolheu entre D-Escala, D-Atributos e D-Extracao.
# `minutos` mede a taxa que decide a viabilidade do D-Humano por censo.
CAMPOS_LEITURA = [
    "data_masthead",
    "voz",
    "objeto_politica",
    "direcao_por_objeto",
    "posicao_declarada",
    "argumento",
    "atores_nomeados",
    "interesses_invocados",
    "vocabulario_epoca",
    "citacao_ancora",
    "localizacao",
    "confianca",
    "dificuldade",
    "dialogo_historiografia",
    "minutos",
]


def fase(ano: int) -> str:
    """Fases do codebook (docs/codebook-fases.md)."""
    if ano <= 1906:
        return "F1"
    if ano <= 1909:
        return "F2"
    if ano <= 1913:
        return "F3"
    return "F4"


def carrega_pecas() -> pd.DataFrame:
    """Pecas `keep` com o rotulo de registro ja atribuido."""
    pecas = pd.read_csv(CSV_AMOSTRA, engine="python")
    rotulos = pd.read_excel(XLSX_ROTULAGEM, usecols=["item_id", "registro"])
    d = pecas.merge(rotulos, on="item_id", how="left", suffixes=("", "_rot"))
    if "registro_rot" in d.columns:
        d["registro"] = d["registro_rot"].combine_first(d["registro"])
        d = d.drop(columns=["registro_rot"])
    d = d[d["status"] == "keep"].copy()
    d["fase"] = d["source_year"].map(fase)
    d["data"] = pd.to_datetime(d["data"], errors="coerce")
    return d


def carrega_edicoes_sem_mencao() -> pd.DataFrame:
    """Edicoes em que a triagem por nome nao achou nenhuma ocorrencia.

    Registro positivo do nao-achado: cada edicao aqui foi varrida pagina a
    pagina e nao produziu match. Base da auditoria de recall.
    """
    frames = []
    for caminho in sorted(glob.glob("dados/triagem/triagem_nome_*.csv")):
        nome = Path(caminho).name
        bib, ano = nome.replace(".csv", "").split("_")[2:4]
        pag = pd.read_csv(
            caminho, engine="python", usecols=["source_identifier", "hit"]
        )
        ed = pag.groupby("source_identifier", as_index=False)["hit"].max()
        ed["jornal"] = BIB2JORNAL[bib]
        ed["source_year"] = int(ano)
        frames.append(ed)
    todas = pd.concat(frames, ignore_index=True)
    sem = todas[todas["hit"] == 0].copy()
    sem["fase"] = sem["source_year"].map(fase)
    return sem.drop(columns=["hit"])


def seleciona(d: pd.DataFrame) -> pd.DataFrame:
    """Camadas 0 a 3 do protocolo, em ordem, sem repetir peca."""
    subst = d[d["registro"] == "substantivo"]
    partes = []

    # Camada 0: censo de editorial e artigo substantivos.
    c0 = subst[subst["forma"].isin(["editorial", "artigo"])].copy()
    c0["camada"] = "0_censo_editorial_artigo"
    c0["estrato"] = "substantivo_" + c0["forma"]
    c0["motivo_selecao"] = "censo do material mais proximo do construto"
    partes.append(c0)
    usados = set(c0["item_id"])

    # Camada 1: episodios comparados entre os quatro jornais.
    for episodio, (ini, fim) in EPISODIOS.items():
        janela = subst[
            subst["data"].between(pd.Timestamp(ini), pd.Timestamp(fim))
            & ~subst["item_id"].isin(usados)
        ].copy()
        if janela.empty:
            continue
        janela["camada"] = "1_episodio"
        janela["estrato"] = f"episodio_{episodio}"
        janela["motivo_selecao"] = f"janela {ini} a {fim}, comparacao entre jornais"
        partes.append(janela)
        usados |= set(janela["item_id"])

    # Camada 2: sorteio para completar as celulas fase x jornal.
    ja = pd.concat(partes, ignore_index=True)
    contagem = ja.groupby(["fase", "jornal"]).size()
    sorteios = []
    for (f, j), g in subst[~subst["item_id"].isin(usados)].groupby(["fase", "jornal"]):
        falta = MIN_CELULA - int(contagem.get((f, j), 0))
        if falta <= 0:
            continue
        sorteios.append(g.sample(min(falta, len(g)), random_state=SEMENTE))
    if sorteios:
        c2 = pd.concat(sorteios, ignore_index=True)
        c2["camada"] = "2_sorteio_estratificado"
        c2["estrato"] = "substantivo_sorteado"
        c2["motivo_selecao"] = f"completar celula ate {MIN_CELULA} pecas"
        partes.append(c2)
        usados |= set(c2["item_id"])

    # Camada 3: fronteira negativa, o que nao conta como debate.
    for registro, cota in (
        ("operacional_rotina", COTA_ROTINA),
        ("incidental", COTA_INCIDENTAL),
    ):
        pool = d[(d["registro"] == registro) & ~d["item_id"].isin(usados)]
        if pool.empty:
            continue
        c3 = pd.concat(
            [g.sample(min(cota, len(g)), random_state=SEMENTE)
             for _, g in pool.groupby("fase")],
            ignore_index=True,
        )
        c3["camada"] = "3_fronteira_negativa"
        c3["estrato"] = registro
        c3["motivo_selecao"] = "fixar por escrito o que nao conta como debate"
        partes.append(c3)
        usados |= set(c3["item_id"])

    ficha = pd.concat(partes, ignore_index=True)
    ficha = ficha.sort_values(["camada", "fase", "jornal", "data"]).reset_index(drop=True)
    for campo in CAMPOS_LEITURA:
        ficha[campo] = ""
    colunas = [
        "item_id", "camada", "estrato", "motivo_selecao", "fase", "jornal",
        "data", "data_confiavel", "source_identifier", "page_number", "forma",
        "secao", "titulo", "registro", *CAMPOS_LEITURA,
    ]
    return ficha[colunas]


def main() -> None:
    d = carrega_pecas()
    ficha = seleciona(d)

    sem_mencao = carrega_edicoes_sem_mencao()
    recall = pd.concat(
        [g.sample(min(COTA_SEM_MENCAO, len(g)), random_state=SEMENTE)
         for _, g in sem_mencao.groupby(["fase", "jornal"])],
        ignore_index=True,
    )
    recall = recall.sort_values(["fase", "jornal", "source_identifier"])
    recall = recall.assign(achou_mencao_na_leitura="", observacao="")

    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    ficha.to_csv(DIR_SAIDA / "fichas_leitura.csv", index=False, encoding="utf-8")
    recall.to_csv(
        DIR_SAIDA / "auditoria_recall_edicoes.csv", index=False, encoding="utf-8"
    )

    print(f"semente {SEMENTE}")
    print(f"\n== ficha de leitura: {len(ficha)} pecas ==")
    print(ficha.groupby(["camada", "estrato"]).size().to_string())
    print("\n== cobertura fase x jornal ==")
    print(pd.crosstab(ficha["fase"], ficha["jornal"], margins=True).to_string())
    print("\n== por forma ==")
    print(ficha["forma"].value_counts().to_string())
    print(f"\n== auditoria de recall: {len(recall)} edicoes sem mencao ==")
    print(f"moldura: {len(sem_mencao)} edicoes sem nenhum match no censo")
    print(f"\nescrito em {DIR_SAIDA}/")


if __name__ == "__main__":
    main()
