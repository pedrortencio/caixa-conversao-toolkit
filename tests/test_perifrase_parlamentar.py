"""Testes da varredura de perifrase nos Documentos Parlamentares.

A diferenca de desenho em relacao a varredura na imprensa e o que precisa de
teste: la o achado carrega distancia ate a mencao da Caixa, porque a pagina de
jornal mistura debate e boletim; aqui o volume inteiro E o debate e nenhum
achado pode ser descartado por estar longe. Um filtro de distancia que voltasse
por copia do outro modulo silenciaria justamente o material que a varredura
existe para achar.
"""
from __future__ import annotations

import pytest

from pipeline.analise import perifrase_banqueiro as banqueiro
from pipeline.analise import perifrase_parlamentar as mod
from pipeline.triagem import regra_nome


@pytest.fixture(scope="module")
def padroes():
    return banqueiro.carrega_padroes()


def norm(texto: str) -> str:
    return regra_nome.normaliza(texto)


def test_varre_devolve_uma_linha_por_ocorrencia_com_pagina(padroes):
    paginas = [
        (7, norm("o sr. bulhoes disse que os nossos agentes financeiros em londres")),
        (8, norm("nada aqui sobre o assunto")),
    ]
    registros = mod.varre_volume(paginas, 1, padroes)
    assert [r["pdf_page"] for r in registros] == [7]
    assert registros[0]["familia"] == "agente_financeiro"
    assert registros[0]["volume"] == 1
    assert registros[0]["corte"] == "1906_criacao"


def test_achado_longe_de_qualquer_mencao_da_caixa_e_mantido(padroes):
    """O ponto do modulo.

    Este texto nao contem "caixa de conversao" em lugar nenhum. Na varredura da
    imprensa a pagina nem entraria, porque o iterador so visita paginas com
    mencao. Aqui tem de entrar, porque o volume inteiro e o debate.
    """
    paginas = [(3, norm("responderam os nossos credores externos com uma recusa"))]
    registros = mod.varre_volume(paginas, 2, padroes)
    assert registros, "achado sem mencao da Caixa na pagina foi descartado"
    assert {r["familia"] for r in registros} == {"credor"}
    assert all("distancia_minima" not in r for r in registros)


def test_contexto_cerca_o_casamento_e_nao_a_pagina(padroes):
    recheio = "x" * 900
    paginas = [(1, norm(recheio + " banqueiros de londres " + recheio))]
    registro = mod.varre_volume(paginas, 1, padroes)[0]
    assert registro["trecho_casado"] in registro["contexto"]
    assert len(registro["contexto"]) <= 480


def test_volume_dois_recebe_o_corte_de_1910(padroes):
    paginas = [(1, norm("a grande banca do jogo universal"))]
    registro = mod.varre_volume(paginas, 2, padroes)[0]
    assert registro["corte"] == "1910_taxa_16d"


def test_pagina_sem_perifrase_nao_gera_linha(padroes):
    paginas = [(1, norm("o projecto foi approvado por 115 votos contra 25"))]
    assert mod.varre_volume(paginas, 1, padroes) == []


def test_os_dois_volumes_estao_declarados():
    assert set(mod.VOLUMES) == {1, 2}
