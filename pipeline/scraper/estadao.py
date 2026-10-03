"""Config e utilidades do scraper do acervo de O Estado de S. Paulo.

Ponto único de verdade para host, construção de URL, parse do nome de arquivo e
validação de JPEG. Espelha o papel de `hemeroteca.py` para a BN.

O acervo (acervo.estadao.com.br) roda um Internet Archive BookReader sobre uma
base PHP antiga. Três endpoints abertos (medidos em 12/08/2026):

  servicos/timeLinePaginas.php?dia=&mes=&ano=   lista as páginas da edição da data
  servicos/montaPagina.php?nome_arquivo=        resolve a URL da imagem em alta
  procura/busca.php?busca=&year=&page=          busca de texto completo, 10/página

Diferenças que importam contra a BN:
  - a unidade servida é a PÁGINA em JPEG, não a edição em PDF;
  - a imagem em alta tem sufixo de salt no nome (`-xawggqa`), estável por arquivo
    mas não derivável, então `montaPagina.php` é obrigatório antes de cada baixa;
  - a resolução (~2506x3362) é maior que a dos scans da BN (~2069x3000), o que
    torna a digitalização uma variável confundida entre fontes. Ver o aviso em
    CLAUDE.md sobre ruído de OCR por célula jornal-ano antes de comparar.
"""

from __future__ import annotations

import hashlib
import pathlib
import re
import struct

HOST = "https://acervo.estadao.com.br"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# O acervo é próprio do Estadão e fica fora da BN. O recorte do projeto é o
# período da Caixa de Conversão.
ANO_INICIAL, ANO_FINAL = 1906, 1914

# Raiz do acervo pesado: fora do git e fora do OneDrive (política do projeto).
RAIZ_IMAGENS = pathlib.Path(r"C:\dados-caixa\estadao")

# nome_arquivo: 19061207-10228-nac-0001-999-1-not
#               data     edicao cad  pag  ?   ord tipo
# O 5º campo é 999 no caso comum e vira sigla em página censurada/editoria
# ("cen", "eco"); o 6º é ordinal e pode ser alfanumérico ("b3").
RE_NOME = re.compile(r"\d{8}-\d+-[a-z]+-\d+-[0-9a-z]+-[0-9a-z]+-[a-z]+")


def url_timeline(dia: int | str, mes: int | str, ano: int | str) -> str:
    return f"{HOST}/servicos/timeLinePaginas.php?dia={int(dia):02d}&mes={int(mes):02d}&ano={int(ano)}"


def url_monta_pagina(nome_arquivo: str) -> str:
    return f"{HOST}/servicos/montaPagina.php?nome_arquivo={nome_arquivo}"


def url_busca(termo: str, ano: int | None = None, page: int = 1) -> str:
    from urllib.parse import quote_plus

    u = f"{HOST}/procura/busca.php?busca={quote_plus(termo)}"
    if ano is not None:
        u += f"&year={int(ano)}"
    if page > 1:
        u += f"&page={int(page)}"
    return u


def parse_nome(nome_arquivo: str) -> dict:
    """Decompõe o nome canônico em campos de proveniência."""
    p = nome_arquivo.split("-")
    if len(p) < 7:
        raise ValueError(f"nome_arquivo fora do padrão: {nome_arquivo}")
    data = p[0]
    return {
        "nome_arquivo": nome_arquivo,
        "data": f"{data[:4]}-{data[4:6]}-{data[6:8]}",
        "ano": int(data[:4]),
        "edicao": p[1],
        "caderno": p[2],
        "pagina": int(p[3]),
        "tipo": p[6],
    }


def caminho_local(nome_arquivo: str, raiz: pathlib.Path | None = None) -> pathlib.Path:
    """Imagens particionadas por ano: {raiz}/{ano}/{nome_arquivo}.jpg"""
    meta = parse_nome(nome_arquivo)
    return (raiz or RAIZ_IMAGENS) / str(meta["ano"]) / f"{nome_arquivo}.jpg"


def dimensoes_jpeg(caminho: pathlib.Path) -> tuple[int, int] | None:
    """(largura, altura) lendo o marcador SOF, sem depender de Pillow."""
    try:
        with open(caminho, "rb") as f:
            dados = f.read()
    except OSError:
        return None
    if not dados.startswith(b"\xff\xd8"):
        return None
    i = 2
    while i + 9 < len(dados):
        if dados[i] != 0xFF:
            return None
        marcador = dados[i + 1]
        tamanho = struct.unpack(">H", dados[i + 2:i + 4])[0]
        if marcador in (0xC0, 0xC1, 0xC2, 0xC3):
            altura, largura = struct.unpack(">HH", dados[i + 5:i + 9])
            return largura, altura
        i += 2 + tamanho
    return None


def eh_jpeg_valido(caminho: pathlib.Path, min_kb: int = 100) -> bool:
    """JPEG de verdade: assinatura, tamanho plausível e SOF legível.

    O piso de 100 KB separa a página em alta (~1,5 MB medido) da miniatura
    servida em /p/ (dezenas de KB), que é o erro silencioso mais provável aqui.
    """
    try:
        if caminho.stat().st_size < min_kb * 1024:
            return False
    except OSError:
        return False
    return dimensoes_jpeg(caminho) is not None


def sha256(caminho: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()
