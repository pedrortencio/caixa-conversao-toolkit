"""Testes da varredura de perifrase do credor externo.

O caso que fundou a varredura entra como teste: a Gazeta de Noticias de 1906
chama Rothschild de "o rei dos banqueiros londrinos". Se a lista de padroes
deixar de casar isso, o motivo de existir do modulo se perdeu em silencio.
"""
from __future__ import annotations

import pytest

from pipeline.analise import perifrase_banqueiro as mod
from pipeline.triagem import regra_nome


@pytest.fixture(scope="module")
def padroes():
    return mod.carrega_padroes()


def test_lista_versionada_carrega_com_familia_e_confianca(padroes):
    assert len(padroes) >= 15
    assert {p.confianca for p in padroes} <= mod.CONFIANCAS
    assert all(p.justificativa for p in padroes)
    assert "realeza_bancaria" in {p.familia for p in padroes}


def test_o_caso_que_fundou_a_varredura(padroes):
    texto = regra_nome.normaliza(
        "e o rei dos banqueiros londrinos quem decide a sorte do nosso cambio"
    )
    familias = {p.familia for p, _, _ in mod.encontra(texto, padroes)}
    assert "realeza_bancaria" in familias
    assert "banqueiro_estrangeiro" in familias


def test_perifrase_com_palavra_colada_pelo_ocr(padroes):
    """A forma REAL na pagina, nao a forma limpa.

    A Gazeta traz "opinioes do rei" no fim de uma linha e "dos banqueiros
    londrinos" no comeco da seguinte, e o OCR entrega "reidos banqueiros". A
    primeira versao do padrao exigia espaco e nao casou o unico caso que
    justificava a varredura.
    """
    texto = regra_nome.normaliza(
        "indifferentes aos avisos e as opinioes do reidos banqueiros londrinos"
    )
    familias = {p.familia for p, _, _ in mod.encontra(texto, padroes)}
    assert "realeza_bancaria" in familias


def test_padrao_de_mercado_nao_casa_mercado_de_cafe(padroes):
    """Regressao: o padrao `mercado de` casou 2.312 vezes na primeira rodada."""
    texto = regra_nome.normaliza("o mercado de cafe e o mercado de cambio de santos")
    assert [p.familia for p, _, _ in mod.encontra(texto, padroes)] == []
    ingles = regra_nome.normaliza("o mercado ingles reagiu mal")
    assert any(p.familia == "praca" for p, _, _ in mod.encontra(ingles, padroes))


def test_designacao_por_cargo_e_apanhada(padroes):
    texto = regra_nome.normaliza(
        "o thesouro remetteu a somma aos nossos agentes financeiros em Londres"
    )
    achados = mod.encontra(texto, padroes)
    assert any(p.familia == "agente_financeiro" for p, _, _ in achados)


def test_ocorrencia_sem_perifrase_devolve_lista_vazia(padroes):
    texto = regra_nome.normaliza(
        "entraram hoje na caixa de conversao 25.000 libras esterlinas"
    )
    assert mod.encontra(texto, padroes) == []


def test_um_trecho_pode_casar_duas_familias_e_as_duas_ficam(padroes):
    texto = regra_nome.normaliza("o rei dos banqueiros ingleses esteve aqui")
    familias = [p.familia for p, _, _ in mod.encontra(texto, padroes)]
    assert familias.count("realeza_bancaria") == 1
    assert familias.count("banqueiro_estrangeiro") == 1


def test_achados_saem_ordenados_por_posicao(padroes):
    texto = regra_nome.normaliza(
        "os nossos credores externos e, mais adiante, os agentes financeiros"
    )
    posicoes = [pos for _, pos, _ in mod.encontra(texto, padroes)]
    assert posicoes == sorted(posicoes)


def test_padrao_tolera_ortografia_de_epoca(padroes):
    """A epoca escreve syndicato com y e ingleses com z."""
    texto = regra_nome.normaliza("o syndicato bancario e os banqueiros inglezes")
    familias = {p.familia for p, _, _ in mod.encontra(texto, padroes)}
    assert "syndicato" in familias
    assert "banqueiro_estrangeiro" in familias


def test_distancia_usa_a_mencao_mais_proxima():
    assert mod.distancia_ate_mencao(500, [100, 480, 5000]) == 20


def test_distancia_recusa_pagina_sem_mencao():
    with pytest.raises(ValueError):
        mod.distancia_ate_mencao(10, [])


def test_carga_recusa_confianca_invalida(tmp_path):
    caminho = tmp_path / "p.csv"
    caminho.write_text(
        "familia,padrao,confianca,justificativa\nx,abc,altissima,porque sim\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="confianca invalida"):
        mod.carrega_padroes(caminho)


def test_carga_recusa_padrao_sem_justificativa(tmp_path):
    caminho = tmp_path / "p.csv"
    caminho.write_text(
        "familia,padrao,confianca,justificativa\nx,abc,alta,\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="sem justificativa"):
        mod.carrega_padroes(caminho)


def test_carga_recusa_padrao_repetido(tmp_path):
    caminho = tmp_path / "p.csv"
    caminho.write_text(
        "familia,padrao,confianca,justificativa\n"
        "x,abc,alta,um\ny,abc,alta,outro\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="padrao repetido"):
        mod.carrega_padroes(caminho)
