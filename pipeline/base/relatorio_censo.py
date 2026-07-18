"""Relatório de cobertura do censo 1906-1914 e regressão do gabarito do piloto.

Lê os manifestos versionados de `dados/censo/` (registro positivo de cada
número sondado) e os nomes de arquivo do piloto de 1906 e produz o relatório
de cobertura da Fase A: contagens por (bib, ano), intervalo de sucessos,
buracos internos versus 404 de fronteira, presença dos PDFs em disco e o
portão da Fase A, a regressão "hits do piloto são subconjunto do censo".
Não abre o banco: enquanto a varredura roda, o manifesto é a fonte segura.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base.carrega_censo import (
    BIBS_CENSO,
    DIR_CENSO,
    RAW_ROOT_PADRAO,
)
from pipeline.base.carrega_piloto import now
from pipeline.base import recupera_indice
from pipeline.scraper import censo
from pipeline.scraper import hemeroteca as H
from pipeline.scraper.indice_bndigital import le_manifesto_csv

RAIZ_REPO = Path(__file__).resolve().parents[2]
DIR_PILOTO = RAIZ_REPO / "dados" / "piloto_1906"
GABARITO_ESPERADO = {"178691": 79, "090972": 94, "089842": 110, "103730": 146}
MAX_NUMEROS_LISTADOS = 20
_PADRAO_PILOTO = re.compile(r"^per(\d+)_1906_[A-Za-z]?(\d+)")
_PADRAO_MANIFESTO = re.compile(r"^(?:varredura|recuperacao)_(\d+)_(\d{4})\.csv$")


@dataclass(frozen=True, slots=True)
class Gabarito:
    arquivos: int
    numeros: frozenset[int]


@dataclass(frozen=True, slots=True)
class ResumoAno:
    bib: str
    ano: int
    contagens: dict[str, int]
    ok_min: int | None
    ok_max: int | None
    buracos: tuple[int, ...]
    erros: tuple[int, ...]
    ausentes_fronteira: int
    paginas: int
    bytes_ok: int
    concluido: bool
    pdfs_sumidos: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Regressao:
    esperados: int
    presentes: int
    faltantes: tuple[int, ...]

    @property
    def aprovada(self) -> bool:
        return not self.faltantes


def gabarito_piloto(dir_piloto: Path = DIR_PILOTO) -> dict[str, Gabarito]:
    """Extrai (bib, número de edição) dos nomes de arquivo do piloto.

    Prefixos A/B (duas edições com o mesmo número BN no dia) contam como o
    mesmo número no host estático; números repetidos são deduplicados.
    Saídas de classificação inválida (`*_raw_invalid_json.txt`) também são
    hits do piloto e contam no gabarito.
    """
    arquivos: dict[str, int] = {}
    numeros: dict[str, set[int]] = {}
    for caminho in sorted(dir_piloto.glob("json*_1906/*")):
        if not caminho.is_file():
            continue
        encontrado = _PADRAO_PILOTO.match(caminho.stem)
        if encontrado is None:
            continue
        bib = encontrado.group(1)
        if bib not in BIBS_CENSO:
            continue
        arquivos[bib] = arquivos.get(bib, 0) + 1
        numeros.setdefault(bib, set()).add(int(encontrado.group(2)))
    return {
        bib: Gabarito(arquivos=arquivos[bib], numeros=frozenset(numeros[bib]))
        for bib in arquivos
    }


def _estado_final_por_numero(caminho: Path) -> dict[int, dict[str, str]]:
    """Última linha de cada número: o resume pode sondar de novo um erro."""
    if not caminho.exists():
        return {}
    with open(caminho, encoding="utf-8", newline="") as entrada:
        return {
            int(linha["numero"]): linha for linha in csv.DictReader(entrada)
        }


def _estados_unificados(
    dir_censo: Path, bib: str, ano: int
) -> dict[int, dict[str, str]]:
    """Estado final por número: a recuperação é observação posterior à
    varredura, então prevalece quando as duas sondaram o mesmo número."""
    estados = _estado_final_por_numero(
        dir_censo / f"varredura_{bib}_{ano}.csv"
    )
    estados.update(
        _estado_final_por_numero(dir_censo / f"recuperacao_{bib}_{ano}.csv")
    )
    return estados


def _numeros_ok(dir_censo: Path, bib: str, ano: int) -> frozenset[int]:
    estados = _estados_unificados(dir_censo, bib, ano)
    return frozenset(
        numero for numero, linha in estados.items() if linha["status"] == "ok"
    )


def resume_ano(
    bib: str,
    ano: int,
    *,
    dir_censo: Path = DIR_CENSO,
    raw_root: Path | None,
) -> ResumoAno:
    estados = _estados_unificados(dir_censo, bib, ano)
    contagens: dict[str, int] = {}
    for linha in estados.values():
        contagens[linha["status"]] = contagens.get(linha["status"], 0) + 1

    oks = sorted(
        numero for numero, linha in estados.items() if linha["status"] == "ok"
    )
    ok_min = oks[0] if oks else None
    ok_max = oks[-1] if oks else None
    buracos = tuple(
        numero
        for numero, linha in sorted(estados.items())
        if linha["status"] == "ausente"
        and ok_min is not None
        and ok_min < numero < ok_max
    )
    erros = tuple(
        numero
        for numero, linha in sorted(estados.items())
        if linha["status"] == "erro"
    )
    paginas = sum(
        int(linha["page_count"] or 0)
        for linha in estados.values()
        if linha["status"] == "ok"
    )
    bytes_ok = sum(
        int(linha["byte_count"] or 0)
        for linha in estados.values()
        if linha["status"] == "ok"
    )
    pdfs_sumidos: tuple[int, ...] = ()
    if raw_root is not None:
        pdfs_sumidos = tuple(
            numero
            for numero in oks
            if not (raw_root / bib / H.nome_pdf(bib, ano, numero)).exists()
        )
    return ResumoAno(
        bib=bib,
        ano=ano,
        contagens=contagens,
        ok_min=ok_min,
        ok_max=ok_max,
        buracos=buracos,
        erros=erros,
        ausentes_fronteira=contagens.get("ausente", 0) - len(buracos),
        paginas=paginas,
        bytes_ok=bytes_ok,
        concluido=(dir_censo / f"concluido_{bib}_{ano}.txt").exists(),
        pdfs_sumidos=pdfs_sumidos,
    )


def regressao_1906(
    gabarito: dict[str, Gabarito],
    dir_censo: Path = DIR_CENSO,
) -> dict[str, Regressao]:
    resultado: dict[str, Regressao] = {}
    for bib, itens in sorted(gabarito.items()):
        oks = _numeros_ok(dir_censo, bib, 1906)
        resultado[bib] = Regressao(
            esperados=len(itens.numeros),
            presentes=len(itens.numeros & oks),
            faltantes=tuple(sorted(itens.numeros - oks)),
        )
    return resultado


def _anos_varridos(dir_censo: Path, bib: str) -> list[int]:
    """Anos com manifesto de varredura OU de recuperação."""
    anos = set()
    for caminho in dir_censo.glob(f"*_{bib}_*.csv"):
        encontrado = _PADRAO_MANIFESTO.match(caminho.name)
        if encontrado is not None:
            anos.add(int(encontrado.group(2)))
    return sorted(anos)


def _lista_curta(numeros: tuple[int, ...]) -> str:
    if not numeros:
        return ""
    exibidos = ", ".join(str(n) for n in numeros[:MAX_NUMEROS_LISTADOS])
    resto = len(numeros) - MAX_NUMEROS_LISTADOS
    return exibidos + (f" (+{resto})" if resto > 0 else "")


def gera_relatorio(
    *,
    dir_censo: Path = DIR_CENSO,
    dir_piloto: Path = DIR_PILOTO,
    raw_root: Path | None,
) -> str:
    partes = [
        "# Relatório de cobertura do censo 1906-1914",
        "",
        f"Gerado em {now()} a partir dos manifestos de `dados/censo/` "
        "(estado final de cada número sondado).",
        "",
        "## Cobertura por jornal e ano",
        "",
        "| Jornal | bib | Ano | ok | ausente | erro | pdf inválido "
        "| intervalo ok | buracos | 404 fronteira | páginas | MB "
        "| concluído | PDFs sumidos |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    alertas: list[str] = []
    nao_varridos: list[str] = []
    for bib in BIBS_CENSO:
        anos = _anos_varridos(dir_censo, bib)
        for ano in censo.ANOS_CENSO:
            if ano not in anos:
                nao_varridos.append(f"{H.slug_por_bib(bib)} ({bib}) {ano}")
        for ano in anos:
            resumo = resume_ano(
                bib, ano, dir_censo=dir_censo, raw_root=raw_root
            )
            intervalo = (
                f"{resumo.ok_min}-{resumo.ok_max}"
                if resumo.ok_min is not None
                else "sem sucesso"
            )
            partes.append(
                f"| {H.slug_por_bib(bib)} | {bib} | {ano} "
                f"| {resumo.contagens.get('ok', 0)} "
                f"| {resumo.contagens.get('ausente', 0)} "
                f"| {resumo.contagens.get('erro', 0)} "
                f"| {resumo.contagens.get('pdf_invalido', 0)} "
                f"| {intervalo} | {len(resumo.buracos)} "
                f"| {resumo.ausentes_fronteira} | {resumo.paginas} "
                f"| {resumo.bytes_ok / 1_000_000:.0f} "
                f"| {'sim' if resumo.concluido else 'NÃO'} "
                f"| {len(resumo.pdfs_sumidos)} |"
            )
            varreu = (dir_censo / f"varredura_{bib}_{ano}.csv").exists()
            if not resumo.concluido and varreu:
                alertas.append(
                    f"{bib} {ano}: varredura sem marcador de conclusão."
                )
            if resumo.erros:
                alertas.append(
                    f"{bib} {ano}: números com erro de rede não resolvido: "
                    f"{_lista_curta(resumo.erros)}."
                )
            if resumo.pdfs_sumidos:
                alertas.append(
                    f"{bib} {ano}: {len(resumo.pdfs_sumidos)} PDFs ok no "
                    f"manifesto ausentes do disco: "
                    f"{_lista_curta(resumo.pdfs_sumidos)}."
                )
    if nao_varridos:
        partes += ["", "## Anos sem varredura", ""]
        partes += [f"- {item}" for item in nao_varridos]

    secao_indice: list[str] = []
    for bib in BIBS_CENSO:
        caminho_indice = dir_censo / f"indice_bndigital_{bib}.csv"
        if not caminho_indice.exists():
            continue
        indice = le_manifesto_csv(caminho_indice)
        for ano in sorted({ano for ano, _ in indice}):
            numeros_indice = {n for a, n in indice if a == ano}
            manifestos = (
                recupera_indice.caminho_varredura(bib, ano, dir_censo),
                recupera_indice.caminho_recuperacao(bib, ano, dir_censo),
            )
            oks = recupera_indice.numeros_ok(*manifestos) & numeros_indice
            ausencias = recupera_indice.conta_ausencias(*manifestos)
            terminais = {
                n
                for n in numeros_indice - oks
                if ausencias.get(n, 0) >= recupera_indice.TERMINAL_404
            }
            pendentes = numeros_indice - oks - terminais
            secao_indice.append(
                f"| {H.slug_por_bib(bib)} | {bib} | {ano} "
                f"| {len(numeros_indice)} | {len(oks)} | {len(terminais)} "
                f"| {len(pendentes)} |"
            )
            if pendentes:
                alertas.append(
                    f"{bib} {ano}: {len(pendentes)} pendentes do índice "
                    f"bndigital: {_lista_curta(tuple(sorted(pendentes)))}."
                )
    if secao_indice:
        partes += [
            "",
            "## Cobertura contra o índice bndigital",
            "",
            "Critério: todo item do índice oficial deve estar materializado "
            "(ok) ou com ausência terminal (duas observações de 404); o resto "
            "são pendentes do índice.",
            "",
            "| Jornal | bib | Ano | índice | ok | 404 terminal | pendentes |",
            "|---|---|---|---|---|---|---|",
        ]
        partes += secao_indice

    partes += [
        "",
        "## Regressão do gabarito 1906 (portão da Fase A)",
        "",
        "Critério: toda edição com hit no piloto de 1906 deve estar no censo "
        "com download ok.",
        "",
        "| Jornal | bib | arquivos do piloto | esperado | edições únicas "
        "| presentes | faltantes | veredito |",
        "|---|---|---|---|---|---|---|---|",
    ]
    gabarito = gabarito_piloto(dir_piloto)
    for bib, itens in sorted(gabarito.items()):
        regressao = regressao_1906({bib: gabarito[bib]}, dir_censo)[bib]
        esperado = GABARITO_ESPERADO.get(bib)
        veredito = "APROVADA" if regressao.aprovada else "REPROVADA"
        partes.append(
            f"| {H.slug_por_bib(bib)} | {bib} | {itens.arquivos} "
            f"| {esperado} | {regressao.esperados} | {regressao.presentes} "
            f"| {_lista_curta(regressao.faltantes)} | {veredito} |"
        )
        if esperado is not None and itens.arquivos != esperado:
            alertas.append(
                f"{bib}: piloto com {itens.arquivos} arquivos, esperado "
                f"{esperado} (CLAUDE.md); conferir sincronização do OneDrive."
            )
        if not regressao.aprovada:
            alertas.append(
                f"{bib}: regressão 1906 REPROVADA, "
                f"{len(regressao.faltantes)} edições do piloto fora do censo."
            )
    for bib in BIBS_CENSO:
        if bib not in gabarito:
            alertas.append(f"{bib}: nenhum arquivo do piloto encontrado.")

    partes += ["", "## Alertas", ""]
    partes += (
        [f"- {alerta}" for alerta in alertas] if alertas else ["- Nenhum."]
    )
    return "\n".join(partes) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Relatório de cobertura do censo + regressão 1906"
    )
    parser.add_argument("--dir-censo", type=Path, default=DIR_CENSO)
    parser.add_argument("--piloto", type=Path, default=DIR_PILOTO)
    parser.add_argument("--raw-root", type=Path, default=RAW_ROOT_PADRAO)
    parser.add_argument(
        "--sem-disco", action="store_true",
        help="não conferir presença dos PDFs em disco",
    )
    parser.add_argument(
        "--saida", type=Path, default=None,
        help="arquivo de saída (padrão: stdout)",
    )
    argumentos = parser.parse_args()
    texto = gera_relatorio(
        dir_censo=argumentos.dir_censo,
        dir_piloto=argumentos.piloto,
        raw_root=None if argumentos.sem_disco else argumentos.raw_root,
    )
    if argumentos.saida is None:
        print(texto)
    else:
        argumentos.saida.write_text(texto, encoding="utf-8")
        print(f"Relatório escrito em {argumentos.saida}")


if __name__ == "__main__":
    main()
