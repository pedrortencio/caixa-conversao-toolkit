"""Config e utilidades compartilhadas do scraper (F1a enumeração + F1b download).

Ponto único de verdade para: mapa de jornais/bibs/pastas, construção de URL e
nome de arquivo, e validação de PDF. Se a Hemeroteca mudar de layout, muda-se
aqui e não espalhado pelos scripts.
"""

from __future__ import annotations

import pathlib

# Host de arquivos ESTÁTICOS da Hemeroteca (aberto; sem o Cloudflare do DocReader).
# Serve a edição inteira: {HOST_PDF}/{bib}/per{bib}_{ano}_{edicao:05d}.pdf
HOST_PDF = "https://hemeroteca-pdf.bn.gov.br"

# UA de navegador: o host estático responde a curl/requests, mas usamos um UA
# realista por educação e robustez (comprovado com HTTP 200 em 14/07/2026).
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# Corpus. `pastas` mapeia a pasta do DocReader (usada na busca/F1a) ao intervalo
# de anos que ela cobre. O download (F1b) usa só o `bib` cru.
JORNAIS: dict[str, dict] = {
    "O Paiz": {
        "slug": "o_paiz",
        "bib": "178691",
        "pastas": {"178691_03": (1900, 1909), "178691_04": (1910, 1919)},
    },
    "Correio Paulistano": {
        "slug": "correio_paulistano",
        "bib": "090972",
        "pastas": {"090972_06": (1900, 1919)},
    },
    "Gazeta de Notícias": {
        "slug": "gazeta_noticias",
        "bib": "103730",
        "pastas": {"103730_04": (1900, 1919)},
    },
    "Correio da Manhã": {
        "slug": "correio_manha",
        "bib": "089842",
        "pastas": {"089842_01": (1901, 1909), "089842_02": (1910, 1919)},
    },
}

# Gabarito da regressão de 1906 (contagens do piloto). F1a deve reproduzir.
GABARITO_1906 = {
    "O Paiz": 79,
    "Correio Paulistano": 94,
    "Correio da Manhã": 110,
    "Gazeta de Notícias": 146,
}


def slug_por_bib(bib: str) -> str:
    for j in JORNAIS.values():
        if j["bib"] == str(bib):
            return j["slug"]
    return f"bib_{bib}"


def nome_pdf(bib: str, ano: int, edicao: int | str) -> str:
    """Nome canônico da edição: per{bib}_{ano}_{edicao:05d}.pdf (padrão do piloto)."""
    return f"per{bib}_{int(ano)}_{int(edicao):05d}.pdf"


def url_pdf(bib: str, ano: int, edicao: int | str) -> str:
    return f"{HOST_PDF}/{bib}/{nome_pdf(bib, ano, edicao)}"


def eh_pdf_valido(caminho: pathlib.Path, min_kb: int = 10) -> bool:
    """PDF de verdade: assinatura %PDF e tamanho plausível (uma edição tem ~MBs)."""
    try:
        if caminho.stat().st_size < min_kb * 1024:
            return False
        with open(caminho, "rb") as f:
            return f.read(5).startswith(b"%PDF")
    except OSError:
        return False
