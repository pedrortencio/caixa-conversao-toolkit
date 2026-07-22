"""Calibração da regra por nome contra o gabarito humano do piloto 1906.

Duas métricas distintas, nunca somadas (docs/superpowers/specs/
2026-07-20-triagem-nome-pivo-design.md):

- RECALL sobre os positivos do gabarito: das edições que o piloto codificou
  com menção/posição (`overall_classification` != "No Relevant Mentions
  Found"), quantas a regra por nome sinaliza como relevantes. Perda aqui mede
  quanto uma futura camada 2 (lista de termos) recuperaria.
- SONDA DE PRECISÃO sobre os "No Relevant Mentions Found": se a regra achar
  menção real nessas edições, é evidência de que o método antigo (busca de
  hits da BN) subcontou. Os negativos do gabarito vêm de busca, não de leitura
  de toda página, então não são verdade limpa: reportamos a lista para
  inspeção humana, não como denominador de precisão.

Escopo: piloto 1906. Agrega por OBJETO digital (proxy 1:1 da edição-dia,
verificado no piloto: 67 objetos = 67 edições-dia). 1906 é uma única fase
(criação), então não há recorte por fase a fazer aqui; `phase_definitions`
está vazia no banco e a resolução de fase do censo inteiro é projeto à parte.
Estadão não entra: está no gabarito do piloto mas não no acervo digital da BN.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db
from pipeline.base.carrega_piloto import now
from pipeline.triagem import roda_censo

DIR_PILOTO = db.ROOT / "dados" / "piloto_1906"
LABEL_NAO_RELEVANTE = "No Relevant Mentions Found"

# bib -> pasta de gabarito. Estadão de fora (fora do acervo BN).
GABARITO_DIRS = {
    "178691": "jsonO_Paiz_1906",
    "089842": "jsonCorreioM_1906",
    "090972": "jsonCorreioP_1906",
    "103730": "jsonGazeta_1906",
}
_PADRAO_ARQUIVO = re.compile(
    r"^per(\d+)_1906_[A-Za-z]?(\d+)_(classificacao_holistica|raw_invalid_json)$"
)


@dataclass(frozen=True, slots=True)
class ItemGabarito:
    source_identifier: str
    label: str | None  # None = saída inválida (não codificável)


@dataclass(slots=True)
class CalibracaoJornal:
    bib: str
    positivos: int = 0
    positivos_recuperados: int = 0
    nao_relevantes: int = 0
    nao_relevantes_com_hit: int = 0
    invalidos: int = 0
    faltantes_no_censo: list[str] = field(default_factory=list)
    positivos_perdidos: list[str] = field(default_factory=list)
    nao_relevantes_flagados: list[str] = field(default_factory=list)

    @property
    def recall(self) -> float | None:
        if self.positivos == 0:
            return None
        return self.positivos_recuperados / self.positivos


def carrega_gabarito(
    dir_piloto: Path, bib: str
) -> dict[str, ItemGabarito]:
    """Mapa source_identifier -> item do gabarito, para um bib.

    Colisões (edições A/B com o mesmo número BN) coalescem em um objeto: se
    qualquer manifestação é positiva, o objeto-dia é positivo (o dia discutiu
    a Caixa); saída inválida só vale se não houver rótulo real no mesmo id.
    """
    pasta = dir_piloto / GABARITO_DIRS[bib]
    itens: dict[str, ItemGabarito] = {}
    for caminho in sorted(pasta.glob("*")):
        if not caminho.is_file():
            continue
        encontrado = _PADRAO_ARQUIVO.match(caminho.stem)
        if encontrado is None or encontrado.group(1) != bib:
            continue
        numero = int(encontrado.group(2))
        source_identifier = f"per{bib}_1906_{numero:05d}"
        if encontrado.group(3) == "raw_invalid_json":
            label: str | None = None
        else:
            try:
                dados = json.loads(caminho.read_text("utf-8"))
                label = dados.get("overall_classification")
            except Exception:
                label = None
        atual = itens.get(source_identifier)
        itens[source_identifier] = _coalesce(atual, source_identifier, label)
    return itens


def _relevancia(label: str | None) -> int:
    """1 positivo, -1 não-relevante, 0 desconhecido (inválido)."""
    if label is None:
        return 0
    return -1 if label == LABEL_NAO_RELEVANTE else 1


def _coalesce(
    atual: ItemGabarito | None, source_identifier: str, label: str | None
) -> ItemGabarito:
    if atual is None:
        return ItemGabarito(source_identifier, label)
    # positivo domina não-relevante, que domina inválido.
    if _relevancia(label) > _relevancia(atual.label):
        return ItemGabarito(source_identifier, label)
    return atual


def calibra(
    conn: sqlite3.Connection,
    *,
    bib: str,
    dir_piloto: Path = DIR_PILOTO,
) -> CalibracaoJornal:
    gabarito = carrega_gabarito(dir_piloto, bib)
    decisoes = {
        d.source_identifier: d
        for d in roda_censo.avalia_objetos(
            conn,
            bib=bib,
            ano=1906,
            source_identifiers=list(gabarito),
        )
    }
    resultado = CalibracaoJornal(bib=bib)
    for source_identifier, item in sorted(gabarito.items()):
        decisao = decisoes.get(source_identifier)
        if decisao is None:
            resultado.faltantes_no_censo.append(source_identifier)
            continue
        if item.label is None:
            resultado.invalidos += 1
            continue
        if item.label == LABEL_NAO_RELEVANTE:
            resultado.nao_relevantes += 1
            if decisao.relevante:
                resultado.nao_relevantes_com_hit += 1
                resultado.nao_relevantes_flagados.append(source_identifier)
        else:
            resultado.positivos += 1
            if decisao.relevante:
                resultado.positivos_recuperados += 1
            else:
                resultado.positivos_perdidos.append(source_identifier)
    return resultado


def _lista_curta(ids: list[str], limite: int = 15) -> str:
    if not ids:
        return "nenhum"
    exibidos = ", ".join(ids[:limite])
    resto = len(ids) - limite
    return exibidos + (f" (+{resto})" if resto > 0 else "")


def gera_relatorio(
    conn: sqlite3.Connection, *, dir_piloto: Path = DIR_PILOTO
) -> str:
    partes = [
        "# Calibração da triagem por nome contra o gabarito 1906",
        "",
        f"Gerado em {now()}. Regra: `{roda_censo.regra_nome.REGRA_VERSAO}`. "
        "Escopo: piloto 1906, agregado por objeto digital (proxy 1:1 da "
        "edição-dia). Estadão fora (não está no acervo digital da BN).",
        "",
        "## Recall sobre os positivos do gabarito",
        "",
        "Critério: das edições que o piloto codificou com menção/posição, "
        "quantas a regra por nome sinaliza como relevantes. Recall baixo = "
        "OCR garbled demais para o nome; mede o que a camada 2 (termos) "
        "recuperaria.",
        "",
        "| Jornal | bib | positivos | recuperados | recall | perdidos |",
        "|---|---|---|---|---|---|",
    ]
    calibracoes = [
        calibra(conn, bib=bib, dir_piloto=dir_piloto)
        for bib in GABARITO_DIRS
    ]
    tot_pos = tot_rec = 0
    for c in calibracoes:
        recall = "—" if c.recall is None else f"{c.recall:.3f}"
        partes.append(
            f"| {H(c.bib)} | {c.bib} | {c.positivos} "
            f"| {c.positivos_recuperados} | {recall} "
            f"| {_lista_curta(c.positivos_perdidos)} |"
        )
        tot_pos += c.positivos
        tot_rec += c.positivos_recuperados
    recall_total = f"{tot_rec / tot_pos:.3f}" if tot_pos else "—"
    partes.append(
        f"| **Total** | | **{tot_pos}** | **{tot_rec}** "
        f"| **{recall_total}** | |"
    )

    partes += [
        "",
        "## Sonda de precisão sobre os \"No Relevant Mentions Found\"",
        "",
        "Não é precisão medida: os negativos do gabarito vêm de busca da BN, "
        "não de leitura de toda página. Um hit da regra aqui é candidato a "
        "menção que o método antigo perdeu, para inspeção humana.",
        "",
        "| Jornal | bib | não-relevantes | com hit da regra | flagados |",
        "|---|---|---|---|---|",
    ]
    for c in calibracoes:
        partes.append(
            f"| {H(c.bib)} | {c.bib} | {c.nao_relevantes} "
            f"| {c.nao_relevantes_com_hit} "
            f"| {_lista_curta(c.nao_relevantes_flagados)} |"
        )

    avisos: list[str] = []
    for c in calibracoes:
        if c.invalidos:
            avisos.append(
                f"{c.bib}: {c.invalidos} saída(s) inválida(s) do piloto "
                "(não codificável), fora das duas métricas."
            )
        if c.faltantes_no_censo:
            avisos.append(
                f"{c.bib}: {len(c.faltantes_no_censo)} id(s) do gabarito sem "
                f"objeto no censo: {_lista_curta(c.faltantes_no_censo)}."
            )
    partes += ["", "## Avisos", ""]
    partes += [f"- {a}" for a in avisos] if avisos else ["- Nenhum."]
    return "\n".join(partes) + "\n"


def H(bib: str) -> str:
    from pipeline.scraper import hemeroteca

    return hemeroteca.slug_por_bib(bib)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Calibra a triagem por nome contra o gabarito 1906"
    )
    parser.add_argument("--base", default=str(db.DEFAULT_DATABASE))
    parser.add_argument("--piloto", default=str(DIR_PILOTO))
    parser.add_argument("--saida", default=None)
    args = parser.parse_args(argv)

    conn = db.connect(args.base, migrate=False)
    try:
        texto = gera_relatorio(conn, dir_piloto=Path(args.piloto))
    finally:
        conn.close()
    if args.saida is None:
        print(texto)
    else:
        Path(args.saida).write_text(texto, encoding="utf-8")
        print(f"Relatório escrito em {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
