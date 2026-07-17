"""Motor de varredura do censo 1906-1914 no host estático da Hemeroteca.

A existência de uma edição não é um intervalo contíguo de números (a Gazeta
de 1907 tem buracos reais no meio do ano), então o censo é uma varredura
número a número por (bib, ano), com regra de parada por ausências
consecutivas e registro positivo de cada sondagem. O transporte HTTP é
injetável para os testes não tocarem a rede.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator, Mapping, Protocol

import requests

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.scraper import hemeroteca as H

ANOS_CENSO = tuple(range(1906, 1915))

# Menor número de edição conhecido em 1906 (stems do piloto); ponto de
# partida da caminhada descendente que descobre o início do ano.
ANCORAS_1906 = {
    "178691": 7819,
    "089842": 1646,
    "090972": 15290,
    "103730": 58,
}


@dataclass(frozen=True, slots=True)
class Resultado:
    bib: str
    ano: int
    numero: int
    status: str  # ok | ausente | erro | pdf_invalido
    http_status: int | None
    pdf_sha256: str | None
    byte_count: int | None
    caminho: Path | None
    detalhe: str = ""


class Transporte(Protocol):
    def obtem(
        self, bib: str, ano: int, numero: int, destino: Path
    ) -> Resultado: ...


class TransporteHttp:
    """GET com stream, hash durante o download, retry só para erro de rede."""

    def __init__(self, pausa: float | Callable[[], float] = 4.0) -> None:
        self._pausa = pausa
        self.sessao = requests.Session()
        self.sessao.headers.update(
            {"User-Agent": H.USER_AGENT, "Accept": "application/pdf,*/*"}
        )

    def _dorme(self) -> None:
        pausa = self._pausa() if callable(self._pausa) else self._pausa
        time.sleep(pausa)

    def obtem(
        self, bib: str, ano: int, numero: int, destino: Path
    ) -> Resultado:
        url = H.url_pdf(bib, ano, numero)
        espera = 3.0
        for tentativa in range(1, 5):
            try:
                resposta = self.sessao.get(url, timeout=90, stream=True)
                if resposta.status_code == 404:
                    resposta.close()
                    self._dorme()
                    return Resultado(
                        bib=bib, ano=ano, numero=numero, status="ausente",
                        http_status=404, pdf_sha256=None, byte_count=None,
                        caminho=None,
                    )
                resposta.raise_for_status()
                digest = hashlib.sha256()
                total = 0
                destino.parent.mkdir(parents=True, exist_ok=True)
                temporario = destino.with_suffix(destino.suffix + ".part")
                with open(temporario, "wb") as saida:
                    for bloco in resposta.iter_content(chunk_size=65536):
                        if bloco:
                            saida.write(bloco)
                            digest.update(bloco)
                            total += len(bloco)
                temporario.replace(destino)
                self._dorme()
                if not H.eh_pdf_valido(destino):
                    return Resultado(
                        bib=bib, ano=ano, numero=numero,
                        status="pdf_invalido",
                        http_status=resposta.status_code,
                        pdf_sha256=digest.hexdigest(), byte_count=total,
                        caminho=destino,
                        detalhe="sem assinatura %PDF ou menor que 10 KB",
                    )
                return Resultado(
                    bib=bib, ano=ano, numero=numero, status="ok",
                    http_status=resposta.status_code,
                    pdf_sha256=digest.hexdigest(), byte_count=total,
                    caminho=destino,
                )
            except requests.RequestException as erro:
                if tentativa == 4:
                    self._dorme()
                    return Resultado(
                        bib=bib, ano=ano, numero=numero, status="erro",
                        http_status=None, pdf_sha256=None, byte_count=None,
                        caminho=None, detalhe=str(erro),
                    )
                time.sleep(espera)
                espera *= 2
        raise AssertionError("inalcançável")


def _destino(destino_dir: Path, bib: str, ano: int, numero: int) -> Path:
    return destino_dir / H.nome_pdf(bib, ano, numero)


def detecta_regime(
    transporte: Transporte,
    bib: str,
    ano: int,
    destino_dir: Path,
) -> tuple[str, list[Resultado]]:
    """Sonda n=1..6; qualquer sucesso indica numeração anual (início em 1)."""
    resultados = [
        transporte.obtem(bib, ano, n, _destino(destino_dir, bib, ano, n))
        for n in range(1, 7)
    ]
    regime = (
        "anual"
        if any(r.status == "ok" for r in resultados)
        else "continuo"
    )
    return regime, resultados


def inicio_continuo_1906(
    transporte: Transporte,
    bib: str,
    *,
    ancora: int,
    destino_dir: Path,
    parada: int = 90,
) -> tuple[int, list[Resultado]]:
    """Desce da âncora até `parada` ausências consecutivas; devolve o início."""
    resultados: list[Resultado] = []
    menor_sucesso = ancora
    ausencias = 0
    numero = ancora - 1
    while ausencias < parada and numero >= 1:
        resultado = transporte.obtem(
            bib, 1906, numero, _destino(destino_dir, bib, 1906, numero)
        )
        resultados.append(resultado)
        if resultado.status == "ok":
            menor_sucesso = numero
            ausencias = 0
        else:
            ausencias += 1
        numero -= 1
    return menor_sucesso, resultados


def varre_ano(
    transporte: Transporte,
    bib: str,
    ano: int,
    *,
    inicio: int,
    ja_sondados: Mapping[int, str],
    destino_dir: Path,
    cap: int = 600,
    parada: int = 90,
    sem_sucesso: int = 200,
) -> Iterator[Resultado]:
    """Varre números a partir de `inicio`, atravessando buracos menores que
    `parada`. Números em `ja_sondados` alimentam a regra de parada sem gerar
    requisição nem resultado novo."""
    ultimo_sucesso: int | None = None
    numero = inicio
    while True:
        if numero >= inicio + cap:
            return
        if ultimo_sucesso is not None and numero > ultimo_sucesso + parada:
            return
        if ultimo_sucesso is None and numero >= inicio + sem_sucesso:
            return
        status_previo = ja_sondados.get(numero)
        if status_previo is not None:
            if status_previo == "ok":
                ultimo_sucesso = numero
            numero += 1
            continue
        resultado = transporte.obtem(
            bib, ano, numero, _destino(destino_dir, bib, ano, numero)
        )
        yield resultado
        if resultado.status == "ok":
            ultimo_sucesso = numero
        numero += 1
