"""Limpeza determinística da amostra recuperada por visão (sem API/LLM).

Marca cada peça com um `status` (keep ou motivo de descarte) e um flag de
data confiável, sem apagar nada (registro positivo). A avaliação de 2026-07-22
mostrou ~40% de ruído de sobreinclusão na recuperacao (itens vizinhos, Caixa
de Amortizacao, marcadores de incerteza) e falha de recall da visao (~7%)
concentrada em 1911-12; por isso a contabilidade de perdas sai por ano, para
a comparacao temporal nao ser enviesada por descarte silencioso.

Saída: `amostra_para_rotular.csv` (todas as linhas + status + data_confiavel +
registro vazio; Pedro rotula onde status==keep) e um relatorio por ano.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db
from pipeline.triagem import db_leitura, regra_nome
from pipeline.triagem.roda_censo import DIR_MANIFESTO

ENTRADA = DIR_MANIFESTO / "amostra_recuperada.csv"
FALHAS = DIR_MANIFESTO / "falhas_recuperadas.csv"
SAIDA = DIR_MANIFESTO / "amostra_para_rotular.csv"
RELATORIO = db.ROOT / "docs" / "relatorio-limpeza-amostra.md"

_DISCLAIMER = re.compile(
    r"\[|nao (e|est|h)|nenhum|aproximad|refer[eê]ncia|indireta|passagem", re.I
)
# Meta-comentário da visão sobre a AUSÊNCIA de menção. Casado sobre o trecho
# normalizado (o padrão acima roda sobre o texto cru e não vê "não" acentuado).
# Vaza pela regra de nome porque a própria negação nomeia a Caixa.
#
# A negação precisa ser SOBRE A MENÇÃO À CAIXA, não uma negação qualquer: o
# jornal de época nega o argumento ("não há dúvida de que a Caixa beneficia a
# lavoura") e descartar isso cortaria justamente o trecho polêmico. Daí a
# vizinhança exigida entre a negação, o verbo de menção e o nome, e o corte da
# janela em ponto e ponto-e-vírgula, que separam orações.
_NEGA_MENCAO = r"nao aplic|nao menciona|sem mencao|nao (ha|existe|consta) mencao"
_DISCLAIMER_VISAO = re.compile(
    rf"nao aplic|({_NEGA_MENCAO})[^.;]{{0,40}}caixa"
    r"|nao (ha|existe|consta)[^.;]{0,40}caixa[^.;]{0,20}mencionad"
)
# Forma solta da negação, usada só depois que a regra de nome já falhou no
# trecho E no texto: sem nome em lugar nenhum, a vizinhança com "caixa" deixa
# de ser exigível e a marca de ausência basta.
_NEGA_MENCAO_SOLTA = re.compile(_NEGA_MENCAO)
_DATA = re.compile(r"(\d{1,2})\s+de\s+([a-z]+)\s+de\s+(\d{4})")
_MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5,
    "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "septembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}


def classifica(row: dict) -> str:
    """status: keep ou motivo de descarte. Ordem importa (mais forte primeiro)."""
    if row["forma"] in ("sem_mencao_na_imagem", "erro", "sem_mencao_confirmada"):
        return "falha"
    trecho = row["trecho_caixa"]
    if not trecho.strip():
        return "drop_trecho_vazio"
    if "amortiza" in regra_nome.normaliza(trecho):
        return "drop_amortizacao"
    if _DISCLAIMER.search(trecho) or _DISCLAIMER_VISAO.search(
        regra_nome.normaliza(trecho)
    ):
        return "drop_disclaimer"
    texto_norm = regra_nome.normaliza(row["texto"])
    if len(row["texto"].strip()) < 150 and (
        row["texto"].strip().startswith("[")
        or "incluido acima" in texto_norm
        or "cobre tambem" in texto_norm
    ):
        return "drop_referencia"
    if regra_nome.encontra(row["texto"]) or regra_nome.encontra(trecho):
        return "keep"
    # Sem nome no trecho nem no texto: a regra de continuação supõe que o nome
    # esteja do outro lado da coluna, o que a declaração de ausência da visão
    # desmente. Sem ela, a peça partida continua valendo.
    if _NEGA_MENCAO_SOLTA.search(regra_nome.normaliza(trecho)):
        return "drop_disclaimer"
    return "keep" if row["continua"] == "1" else "drop_sem_nome"


def _iso_valida(ano: int, mes: int, dia: int) -> str | None:
    """'YYYY-MM-DD' se for data de calendário possível, senão None (rejeita
    dia impossível de erro de OCR, ex. 30 de fevereiro, 39 de abril)."""
    try:
        return datetime.date(ano, mes, dia).isoformat()
    except ValueError:
        return None


def _para_iso(texto: str) -> str | None:
    """Data 'YYYY-MM-DD' válida a partir de 'YYYY-MM-DD' ou de data por
    extenso; None se não parsear ou for dia/mês impossível."""
    achado_iso = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", texto)
    if achado_iso:
        a, m, d = (int(g) for g in achado_iso.groups())
        return _iso_valida(a, m, d)
    achado = _DATA.search(regra_nome.normaliza(texto))
    if not achado:
        return None
    dia, mes_nome, ano = achado.groups()
    mes = _MESES.get(mes_nome)
    return _iso_valida(int(ano), mes, int(dia)) if mes else None


def masthead_por_ano(
    conn, sids_anos: dict[str, str]
) -> dict[str, str]:
    """Para cada objeto, a data do masthead da página 1 cujo ANO casa com
    source_year (rejeita datas de decreto reproduzido, ex. 1887 numa edição
    de 1910). É o consertador determinístico das datas suspeitas."""
    resolvido: dict[str, str] = {}
    for sid, ano in sids_anos.items():
        texto = None
        for p in db_leitura.itera_paginas(conn, source_identifiers=[sid]):
            if p.page_number == 1:
                texto = db_leitura.le_conteudo(p)
                break
        if not texto:
            continue
        for achado in _DATA.finditer(regra_nome.normaliza(texto)):
            dia, mes_nome, a = achado.groups()
            mes = _MESES.get(mes_nome)
            iso = _iso_valida(int(a), mes, int(dia)) if mes else None
            if iso and int(a) == int(ano):
                resolvido[sid] = iso
                break
    return resolvido


def resolve_data(row: dict, masthead: dict[str, str]) -> None:
    """Fixa data/data_fonte/data_confiavel por prioridade: masthead da pág. 1
    com ano casado (confiável) > data da visão consistente com o ano
    (confiável) > nenhuma data (`ano_apenas`, não confiável).

    Quando não há data, a coluna fica VAZIA em vez de receber o ano nu: a
    coluna é de data, e guardar duas espécies de valor nela fazia consumidor
    que parseia perder linha em silêncio. O ano não se perde, está em
    `source_year`, que é a chave de ano de qualquer contagem."""
    sid, ano = row["source_identifier"], row["source_year"]
    if sid in masthead:
        row["data"], row["data_fonte"], row["data_confiavel"] = (
            masthead[sid], "masthead_pag1_ano", 1
        )
        return
    iso = _para_iso(row["data"]) if row["data"] else None
    if iso and abs(int(iso[:4]) - int(ano)) <= 1:
        row["data"], row["data_confiavel"] = iso, 1
        return
    row["data"], row["data_fonte"], row["data_confiavel"] = "", "ano_apenas", 0


def conta_ano_divergente(linhas: list[dict]) -> int:
    """Quantas datas confiáveis caem em ano diferente do `source_year`.

    São as edições de virada de ano que a tolerância de um ano aceita: a data
    do masthead manda sobre o rótulo de ano da pasta do acervo, mas o item
    muda de balde numa contagem por data. Publicado no relatório para a
    escolha da chave de ano ficar visível, não implícita."""
    return sum(
        1
        for r in linhas
        if int(r["data_confiavel"]) == 1
        and r["data"][:4] != str(r["source_year"])
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Limpa a amostra recuperada")
    parser.add_argument("--entrada", default=str(ENTRADA))
    parser.add_argument("--falhas", default=str(FALHAS))
    parser.add_argument("--saida", default=str(SAIDA))
    parser.add_argument("--relatorio", default=str(RELATORIO))
    args = parser.parse_args(argv)

    linhas = list(csv.DictReader(open(args.entrada, encoding="utf-8")))
    campos = list(linhas[0].keys()) + ["status", "data_confiavel"]

    # Mescla as FALHAs re-extraídas de forma dirigida: remove as linhas
    # `sem_mencao_na_imagem` das páginas re-extraídas e usa os itens recuperados.
    falhas_path = Path(args.falhas)
    if falhas_path.exists():
        rec = list(csv.DictReader(open(falhas_path, encoding="utf-8")))
        pgs = {(r["source_identifier"], r["page_number"]) for r in rec}
        linhas = [
            r for r in linhas
            if not (r["forma"] == "sem_mencao_na_imagem"
                    and (r["source_identifier"], r["page_number"]) in pgs)
        ]
        linhas += rec

    conn = db.connect(db.DEFAULT_DATABASE, migrate=False)
    sids_anos = {r["source_identifier"]: r["source_year"] for r in linhas}
    masthead = masthead_por_ano(conn, sids_anos)
    conn.close()

    por_ano: dict[str, Counter] = defaultdict(Counter)
    for r in linhas:
        r["status"] = classifica(r)
        resolve_data(r, masthead)
        por_ano[r["source_year"]][r["status"]] += 1

    with open(args.saida, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)

    motivos = ["keep", "drop_disclaimer", "drop_trecho_vazio",
               "drop_amortizacao", "drop_sem_nome", "falha"]
    anos = sorted(por_ano)
    partes = [
        "# Relatório de limpeza da amostra recuperada",
        "",
        "Limpeza determinística (`pipeline/triagem/limpa_amostra.py`, sem "
        "API/LLM). `keep` = peça válida para rotular; `falha` = visão não "
        "capturou o trecho que o OCR indica (registro não determinado); os "
        "`drop_*` são ruído de sobreinclusão da recuperação. Perdas por ano "
        "para a comparação temporal não ser enviesada por descarte silencioso.",
        "",
        "| ano | total | " + " | ".join(motivos) + " | keep% | falha% |",
        "|" + "---|" * (len(motivos) + 4),
    ]
    tot = Counter()
    for a in anos:
        c = por_ano[a]
        n = sum(c.values())
        tot.update(c)
        partes.append(
            f"| {a} | {n} | "
            + " | ".join(str(c.get(m, 0)) for m in motivos)
            + f" | {100*c.get('keep',0)/n:.0f}% | {100*c.get('falha',0)/n:.0f}% |"
        )
    ntot = sum(tot.values())
    partes.append(
        f"| **tot** | **{ntot}** | "
        + " | ".join(f"**{tot.get(m,0)}**" for m in motivos)
        + f" | **{100*tot.get('keep',0)/ntot:.0f}%** "
        f"| **{100*tot.get('falha',0)/ntot:.0f}%** |"
    )
    n_suspeita = sum(1 for r in linhas if r["data_confiavel"] == 0)
    n_diverge = conta_ano_divergente(linhas)
    partes += [
        "",
        f"Sem data resolvida (`data_confiavel=0`, coluna `data` vazia): "
        f"{n_suspeita} de {ntot}. O ano segue conhecido por `source_year`, "
        "que é a chave de ano de toda contagem; `data` só entra onde "
        "`data_confiavel=1`, e apenas para série mensal.",
        "",
        f"Datas confiáveis em ano diferente do `source_year`: {n_diverge}. "
        "São edições de virada de ano, em que o masthead manda sobre o rótulo "
        "de ano da pasta do acervo; contadas aqui porque mudam de balde numa "
        "contagem por data.",
    ]
    Path(args.relatorio).write_text("\n".join(partes) + "\n", encoding="utf-8")
    print("\n".join(partes))
    print(f"\nescrito: {args.saida} ({ntot} linhas), {args.relatorio}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
