"""Recuperação por união de fontes: alvos do índice bndigital fora do censo.

O índice oficial (`dados/censo/indice_bndigital_{bib}.csv`, extraído duas
vezes com resultado idêntico em 18/07/2026) lista edições que a varredura da
Fase A não materializou, porque a regra de parada não atravessou saltos de
numeração (CM 2099→2255) ou porque o ano nunca teve âncora (Gazeta 1914).
Este módulo baixa exatamente esses alvos, com registro positivo por item em
`dados/censo/recuperacao_{bib}_{ano}.csv`.

Regras do parecer duplo de 18/07/2026:
- alvo = índice menos (ok da varredura + ok da recuperação + 404 terminal);
- 404 só é terminal com DUAS observações (varredura e recuperação contam);
  a rodada re-sonda no passe 2 o que só tem uma;
- 403/429/5xx e falha de rede são transitórios (status `erro`, re-tentado
  em rodada futura, nunca virando ausência);
- pdf_invalido não é ok, então o Paiz 1913_10408 volta a ser alvo.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db as base_db
from pipeline.base.carrega_censo import (
    CAMPOS_MANIFESTO,
    DIR_CENSO,
    RAIZ_REPO,
    RAW_ROOT_PADRAO,
    BIBS_CENSO,
    Protocolos,
    TransporteComCache,
    garante_cadastro,
    garante_calendario,
    pausa_automatica,
    persiste_sucesso,
    registra_manifesto,
)
from pipeline.base.carrega_piloto import git_commit, now
from pipeline.scraper import censo
from pipeline.scraper import hemeroteca as H
from pipeline.scraper.indice_bndigital import le_manifesto_csv

TERMINAL_404 = 2


def caminho_recuperacao(bib: str, ano: int, dir_censo: Path) -> Path:
    return dir_censo / f"recuperacao_{bib}_{ano}.csv"


def caminho_varredura(bib: str, ano: int, dir_censo: Path) -> Path:
    return dir_censo / f"varredura_{bib}_{ano}.csv"


def _linhas(manifesto: Path) -> list[dict]:
    if not manifesto.exists():
        return []
    with open(manifesto, encoding="utf-8", newline="") as entrada:
        return list(csv.DictReader(entrada))


def conta_ausencias(*manifestos: Path) -> dict[int, int]:
    """Observações de ausência (404) por número, somadas entre manifestos."""
    contagem: Counter[int] = Counter()
    for manifesto in manifestos:
        for linha in _linhas(manifesto):
            if linha["status"] == "ausente":
                contagem[int(linha["numero"])] += 1
    return dict(contagem)


def numeros_ok(*manifestos: Path) -> set[int]:
    """Números com download bem-sucedido em qualquer manifesto."""
    return {
        int(linha["numero"])
        for manifesto in manifestos
        for linha in _linhas(manifesto)
        if linha["status"] == "ok"
    }


def alvos_bib(
    indice: set[tuple[int, int]],
    bib: str,
    dir_censo: Path,
    *,
    terminal: int = TERMINAL_404,
) -> list[tuple[int, int]]:
    """Alvos (ano, numero) pendentes: nem baixados, nem 404 terminal."""
    alvos: list[tuple[int, int]] = []
    for ano in sorted({ano for ano, _ in indice}):
        manifestos = (
            caminho_varredura(bib, ano, dir_censo),
            caminho_recuperacao(bib, ano, dir_censo),
        )
        baixados = numeros_ok(*manifestos)
        ausencias = conta_ausencias(*manifestos)
        for _, numero in sorted(n for n in indice if n[0] == ano):
            if numero in baixados:
                continue
            if ausencias.get(numero, 0) >= terminal:
                continue
            alvos.append((ano, numero))
    return alvos


def garante_protocolos_recuperacao(
    conn, *, commit: str, timestamp: str
) -> Protocolos:
    """Protocolo de descoberta = índice bndigital (campo `censo` do par)."""
    with base_db.transaction(conn):
        protocolo_indice = base_db.upsert_protocol(
            conn,
            stage="inventory",
            name="indice_bndigital",
            version="1.0.0",
            executor_type="deterministic",
            code_commit=commit,
            parameters={
                "fonte": "bndigital.bn.gov.br/acervo-digital (paginas publicas)",
                "manifestos": "dados/censo/indice_bndigital_{bib}.csv",
                "verificacao": (
                    "duas extracoes independentes identicas em 18/07/2026; "
                    "snapshots com sha256 em dados/censo/snapshots_bndigital/"
                ),
                "alvo": "indice menos ok(varredura+recuperacao) menos 404 terminal",
                "regra_404_terminal": TERMINAL_404,
                "erros_transitorios": "403/429/5xx e falha de rede (status erro)",
                "recorte": "1906-1914",
            },
            created_at=timestamp,
        )
        protocolo_inicial = base_db.upsert_protocol(
            conn,
            stage="identification",
            name="initial_not_assessed",
            version="1.0.0",
            executor_type="deterministic",
            code_commit=commit,
            parameters={"result": "not_assessed"},
            created_at=timestamp,
        )
    return Protocolos(censo=protocolo_indice, inicial=protocolo_inicial)


def executa_recuperacao(
    *,
    db: Path,
    raw_root: Path,
    dir_censo: Path = DIR_CENSO,
    bibs: tuple[str, ...] = BIBS_CENSO,
    pausa: float | None = None,
    limite: int = 0,
    transporte: censo.Transporte | None = None,
) -> None:
    if transporte is None:
        transporte = TransporteComCache(
            censo.TransporteHttp(pausa if pausa is not None else pausa_automatica)
        )
    conn = base_db.connect(db)
    try:
        commit = git_commit(RAIZ_REPO)
        protocolos = garante_protocolos_recuperacao(
            conn, commit=commit, timestamp=now()
        )
        newspaper_ids = garante_cadastro(conn, timestamp=now())
        garante_calendario(conn, newspaper_ids, timestamp=now())

        sucessos = 0
        for passe in (1, 2):
            pendentes = 0
            for bib in bibs:
                indice = le_manifesto_csv(
                    dir_censo / f"indice_bndigital_{bib}.csv"
                )
                alvos = alvos_bib(indice, bib, dir_censo)
                if not alvos:
                    continue
                pendentes += len(alvos)
                print(
                    f"== passe {passe}: {H.slug_por_bib(bib)} "
                    f"({len(alvos)} alvos) ==",
                    flush=True,
                )
                for ano, numero in alvos:
                    destino = raw_root / bib / H.nome_pdf(bib, ano, numero)
                    resultado = transporte.obtem(bib, ano, numero, destino)
                    page_count = None
                    if resultado.status in {"ok", "pdf_invalido"}:
                        page_count = persiste_sucesso(
                            conn,
                            resultado=resultado,
                            newspaper_id=newspaper_ids[bib],
                            protocolos=protocolos,
                            timestamp=now(),
                        )
                    registra_manifesto(
                        caminho_recuperacao(bib, ano, dir_censo),
                        resultado,
                        page_count=page_count,
                    )
                    rotulo = {
                        "ok": "[ok]  ",
                        "ausente": "[404] ",
                        "erro": "[ERRO]",
                        "pdf_invalido": "[PDF?]",
                    }[resultado.status]
                    print(
                        f"  {rotulo} {H.nome_pdf(bib, ano, numero)}"
                        f"  {resultado.detalhe or (f'{page_count} páginas' if page_count else '')}",
                        flush=True,
                    )
                    if resultado.status == "ok" and page_count is not None:
                        sucessos += 1
                        if limite and sucessos >= limite:
                            print(
                                f"Limite de {limite} sucessos atingido.",
                                flush=True,
                            )
                            return
            if pendentes == 0:
                break
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recuperação dos alvos do índice bndigital fora do censo"
    )
    parser.add_argument("--db", type=Path, default=base_db.DEFAULT_DATABASE)
    parser.add_argument("--raw-root", type=Path, default=RAW_ROOT_PADRAO)
    parser.add_argument(
        "--bib", action="append", choices=BIBS_CENSO, default=None,
        help="restringe a um bib (repetível); padrão todos",
    )
    parser.add_argument(
        "--pausa", type=float, default=None,
        help="segundos entre requisições; padrão automático (4.0 dia, 2.5 madrugada)",
    )
    parser.add_argument(
        "--limite", type=int, default=0,
        help="parar após N downloads bem-sucedidos (0 = sem limite)",
    )
    argumentos = parser.parse_args()
    executa_recuperacao(
        db=argumentos.db.resolve(),
        raw_root=argumentos.raw_root,
        bibs=tuple(argumentos.bib or BIBS_CENSO),
        pausa=argumentos.pausa,
        limite=argumentos.limite,
    )


if __name__ == "__main__":
    main()
