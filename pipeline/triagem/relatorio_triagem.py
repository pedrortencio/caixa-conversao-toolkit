"""Relatório da triagem por nome: R/S por jornal-ANO no censo inteiro.

Lê os manifestos versionados de `dados/triagem/` (registro positivo por
página) e agrega a objeto digital (proxy 1:1 da edição-dia): S = objetos
completamente triados (todas as páginas com texto ok), R = objetos
relevantes (alguma página com o nome). Não abre o banco: o manifesto é a
fonte. A calibração contra o gabarito 1906 sai por `calibra_1906.py`.

ATENÇÃO METODOLÓGICA (verificada por amostragem nesta rodada): R conta
PRESENÇA DO NOME, não discussão substantiva. Em 1906 (debate de criação,
Caixa ainda não operava) presença ≈ discussão. Nos anos de operação
(1907-1914) o nome aparece em boletins diários de movimento de ouro, escalas
militares de guarda ao prédio e datas de telegrama, então R superconta a
discussão editorial e a subida de saliência é em parte artefato de gênero
textual. Distinguir menção de substância é decisão de desenho pendente
(camada de gênero/substância), não desta passada.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db
from pipeline.base.carrega_piloto import now
from pipeline.scraper import hemeroteca
from pipeline.triagem import regra_nome
from pipeline.triagem.roda_censo import DIR_MANIFESTO

# Faixa ilustrativa de esforço para LER e codificar a posição de uma
# edição-dia inteira (múltiplas páginas). Não é medição; serve só para
# situar R contra as horas de codificação de Pedro.
MIN_POR_EDICAO = (10, 25)


@dataclass(frozen=True, slots=True)
class ResumoCelula:
    bib: str
    ano: int
    objetos: int
    triados_completos: int  # S
    relevantes: int  # R
    paginas: int
    paginas_ok: int
    paginas_hit: int

    @property
    def saliencia(self) -> float | None:
        if self.triados_completos == 0:
            return None
        return self.relevantes / self.triados_completos


def resume_manifesto(caminho: Path) -> ResumoCelula:
    bib, ano = _bib_ano_de(caminho)
    hit_por_objeto: dict[str, bool] = {}
    completo_por_objeto: dict[str, bool] = {}
    paginas = paginas_ok = paginas_hit = 0
    with caminho.open(encoding="utf-8", newline="") as entrada:
        for linha in csv.DictReader(entrada):
            sid = linha["source_identifier"]
            hit = linha["hit"] == "1"
            ok = linha["result_status"] == "ok"
            paginas += 1
            paginas_ok += 1 if ok else 0
            paginas_hit += 1 if hit else 0
            hit_por_objeto[sid] = hit_por_objeto.get(sid, False) or hit
            completo_por_objeto[sid] = completo_por_objeto.get(sid, True) and ok
    return ResumoCelula(
        bib=bib,
        ano=ano,
        objetos=len(hit_por_objeto),
        triados_completos=sum(1 for v in completo_por_objeto.values() if v),
        relevantes=sum(1 for v in hit_por_objeto.values() if v),
        paginas=paginas,
        paginas_ok=paginas_ok,
        paginas_hit=paginas_hit,
    )


def _bib_ano_de(caminho: Path) -> tuple[str, int]:
    partes = caminho.stem.split("_")  # triagem_nome_{bib}_{ano}
    return partes[2], int(partes[3])


def gera_relatorio(dir_manifesto: Path = DIR_MANIFESTO) -> str:
    resumos = [
        resume_manifesto(caminho)
        for caminho in sorted(dir_manifesto.glob("triagem_nome_*.csv"))
    ]
    partes = [
        "# Relatório da triagem por nome (medida pivô)",
        "",
        f"Gerado em {now()}. Regra: `{regra_nome.REGRA_VERSAO}`. Fonte: "
        "manifestos de `dados/triagem/` sobre o texto embutido (OCR da BN), "
        "custo zero de token. Agregação por objeto digital (proxy 1:1 da "
        "edição-dia, validado no piloto 1906).",
        "",
        "**R conta presença do nome, não discussão substantiva.** Ver a nota "
        "metodológica no cabeçalho do módulo e a seção de interpretação ao "
        "fim: nos anos de operação (1907-1914) o nome aparece em boletins de "
        "movimento de ouro, escalas de guarda e telegramas, então R e a "
        "saliência estão inflados por gênero textual. 1906 (criação) é limpo.",
        "",
        "## Cobertura e saliência por jornal e ano",
        "",
        "S = objetos completamente triados (todas as páginas com texto ok). "
        "R = objetos relevantes (alguma página com o nome). Saliência = R/S.",
        "",
        "| Jornal | bib | Ano | objetos | S | R | saliência R/S "
        "| páginas | páginas ok | páginas com hit |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    tot_r = tot_s = tot_obj = 0
    for r in resumos:
        sal = "—" if r.saliencia is None else f"{r.saliencia:.2f}"
        partes.append(
            f"| {hemeroteca.slug_por_bib(r.bib)} | {r.bib} | {r.ano} "
            f"| {r.objetos} | {r.triados_completos} | {r.relevantes} "
            f"| {sal} | {r.paginas} | {r.paginas_ok} | {r.paginas_hit} |"
        )
        tot_r += r.relevantes
        tot_s += r.triados_completos
        tot_obj += r.objetos
    sal_total = f"{tot_r / tot_s:.2f}" if tot_s else "—"
    partes.append(
        f"| **Total** | | | **{tot_obj}** | **{tot_s}** | **{tot_r}** "
        f"| **{sal_total}** | | | |"
    )

    partes += _secao_por_jornal(resumos)
    partes += _secao_horas(tot_r)
    partes += _secao_interpretacao()
    return "\n".join(partes) + "\n"


def _secao_por_jornal(resumos: list[ResumoCelula]) -> list[str]:
    linhas = ["", "## R por jornal (soma 1906-1914)", "", "| Jornal | bib | R |",
              "|---|---|---|"]
    por_bib: dict[str, int] = {}
    for r in resumos:
        por_bib[r.bib] = por_bib.get(r.bib, 0) + r.relevantes
    for bib in sorted(por_bib):
        linhas.append(
            f"| {hemeroteca.slug_por_bib(bib)} | {bib} | {por_bib[bib]} |"
        )
    return linhas


def _secao_horas(tot_r: int) -> list[str]:
    lo, hi = MIN_POR_EDICAO
    horas_lo = tot_r * lo / 60
    horas_hi = tot_r * hi / 60
    return [
        "",
        "## Projeção de horas de codificação humana (sobre R bruto)",
        "",
        f"R = {tot_r} edições-dia nomeando a Caixa. A {lo}-{hi} min por "
        f"edição-dia inteira (ler + codificar posição), seriam "
        f"~{horas_lo:.0f} a ~{horas_hi:.0f} horas. A ~15-20 h/semana, isso é "
        "muito além do orçamento de tempo de Pedro (~2 meses).",
        "",
        "Consequência: codificar à mão o R BRUTO inteiro é inviável. As saídas "
        "reais são (a) filtrar R para discussão substantiva (camada de "
        "gênero/substância) antes de contar, encolhendo o denominador; e/ou "
        "(b) amostra estratificada humana forte (padrão-ouro) mais cobertura "
        "por classificador validado. A escolha é decisão de Pedro.",
    ]


def _secao_interpretacao() -> list[str]:
    return [
        "",
        "## Interpretação: presença do nome vs discussão substantiva",
        "",
        "Amostragem de contextos casados (scratchpad desta rodada) mostra que, "
        "nos anos de operação, boa parte dos matches é presença de nome sem "
        "engajamento editorial:",
        "",
        "- **boletim diário de movimento**: \"o movimento de hontem da caixa "
        "de conversão foi… entraram 50.238 libras\" (ticker financeiro);",
        "- **escala de guarda militar**: \"na caixa de conversão, alferes "
        "Servulo\" (qual oficial guarda o prédio);",
        "- **telegrama/dateline** e nota administrativa (nomeação de diretor, "
        "obra, até aniversário de ex-diretor).",
        "",
        "Em 1906 (Caixa ainda não operava) o nome aparece no debate de "
        "criação, então presença ≈ discussão. A subida de saliência de 1907 "
        "em diante é, em parte relevante, artefato de gênero textual: a Caixa "
        "virou dado de rotina. Isto confirma, na prática e de graça, o risco "
        "pré-registrado (decisoes.md 2026-07-19) de que diferenças aparentes "
        "decorram de gênero, evento ou voz reproduzida, não de alinhamento "
        "editorial. A camada de gênero/substância que separa isso é a próxima "
        "decisão de desenho, não parte desta medida pivô.",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Relatório da triagem por nome (R/S por jornal-ano)"
    )
    parser.add_argument("--manifesto-dir", default=str(DIR_MANIFESTO))
    parser.add_argument("--saida", default=None)
    args = parser.parse_args(argv)
    texto = gera_relatorio(Path(args.manifesto_dir))
    if args.saida is None:
        print(texto)
    else:
        Path(args.saida).write_text(texto, encoding="utf-8")
        print(f"Relatório escrito em {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
