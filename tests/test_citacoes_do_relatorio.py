"""Toda citacao em bloco do relatorio do credor externo tem de ser rastreavel.

Este teste existe porque a regra falhou comigo. Ao escrever o relatorio eu
misturei, num mesmo bloco de citacao, palavras da primeira leitura de imagem com
palavras da segunda: `dos nos-sos banqueiros` de uma e `fora ante-hontem` da
outra. O resultado parece uma citacao e nao e nenhuma das duas leituras. Nenhuma
das conferencias anteriores pegaria isso, porque as duas olham o manifesto e
nenhuma olha o texto que vai para o capitulo.

A regra: cada bloco `>` do relatorio tem de casar com o OCR literal ou com uma
das duas leituras de imagem, inteiro, sem costura entre fontes.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from pipeline.analise.confere_citacao_imagem import normaliza_para_comparar

RAIZ = Path(__file__).resolve().parents[1]
RELATORIO = RAIZ / "docs" / "relatorio-credor-externo-no-debate.md"
CONFERIDAS = RAIZ / "dados" / "analise" / "citacoes_conferidas_imagem.csv"


def blocos_de_citacao(markdown: str) -> list[str]:
    blocos: list[str] = []
    atual: list[str] = []
    for linha in markdown.splitlines():
        if linha.startswith(">"):
            atual.append(linha.lstrip("> ").rstrip())
        elif atual:
            blocos.append(" ".join(atual))
            atual = []
    if atual:
        blocos.append(" ".join(atual))
    return blocos


def formas_aceitas() -> list[tuple[str, str, str]]:
    formas = []
    with CONFERIDAS.open(encoding="utf-8", newline="") as entrada:
        for linha in csv.DictReader(entrada):
            for campo in ("citacao_ocr", "leitura_1", "leitura_2"):
                if linha[campo].strip():
                    formas.append((linha["id"], campo, normaliza_para_comparar(linha[campo])))
    return formas


def test_blocos_de_citacao_existem():
    blocos = blocos_de_citacao(RELATORIO.read_text(encoding="utf-8"))
    assert len(blocos) >= 30, "o relatorio perdeu suas citacoes"


@pytest.mark.parametrize("bloco", blocos_de_citacao(RELATORIO.read_text(encoding="utf-8")))
def test_cada_citacao_casa_com_uma_fonte_inteira(bloco: str):
    alvo = normaliza_para_comparar(bloco)
    assert any(
        alvo in forma or forma in alvo for _, _, forma in formas_aceitas()
    ), f"citacao sem fonte unica (costura entre leituras?): {bloco[:120]!r}"


def test_travessao_so_aparece_dentro_de_citacao():
    """Regra de escrita do Pedro: travessao no corpo do texto, nunca."""
    fora_de_citacao = [
        linha
        for linha in RELATORIO.read_text(encoding="utf-8").splitlines()
        if "—" in linha and not linha.startswith(">")
    ]
    assert fora_de_citacao == []


def test_costura_entre_leituras_seria_reprovada():
    """Guarda do proprio teste: a frase misturada nao pode passar."""
    costura = normaliza_para_comparar(
        "recebeu telegramma dos nos-sos banqueiros em Londres, communicando que o "
        "emprestimo de libras 3.000.000, por antecipação de receita, fora ante-hontem "
        "lançado naquella praça com exito extraordinario"
    )
    assert not any(costura in forma or forma in costura for _, _, forma in formas_aceitas())
