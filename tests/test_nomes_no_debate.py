"""Testes da medida de proximidade nome-mencao.

O grosso destes testes fixa COLISAO: os casos em que a tolerancia a OCR
casaria palavra corrente com nome proprio. Cada um deles foi observado na base
real antes de virar teste.
"""
from __future__ import annotations

import pytest

from pipeline.analise import nomes_no_debate as mod


# ---------------------------------------------------------------------------
# Elenco e exclusoes versionados
# ---------------------------------------------------------------------------

def test_elenco_carrega_e_nao_tem_ator_repetido():
    elenco = mod.carrega_elenco()
    assert len(elenco) >= 40
    nomes = [a.nome for a in elenco]
    assert len(nomes) == len(set(nomes))
    campista = next(a for a in elenco if a.nome == "David Campista")
    assert campista.formas == (("campista",),)


def test_ator_com_duas_formas_guarda_as_duas():
    elenco = mod.carrega_elenco()
    ator = next(a for a in elenco if a.nome == "Rui/Ruy Barbosa")
    assert ("rui", "barbosa") in ator.formas
    assert ("ruy", "barbosa") in ator.formas
    assert ator.tokens == frozenset({"rui", "ruy", "barbosa"})


def test_exclusoes_tem_motivo_escrito():
    exclusoes = mod.carrega_exclusoes()
    assert exclusoes["cambista"]
    assert exclusoes["dinheiro"]
    assert all(motivo.strip() for motivo in exclusoes.values())


# ---------------------------------------------------------------------------
# Teto assimetrico
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "token, esperado",
    [("campista", 1), ("rothschild", 1), ("bulhoes", 1), ("costa", 0), ("ramos", 0)],
)
def test_teto_por_tamanho_do_token(token, esperado):
    assert mod.teto_de(token) == esperado


def test_distancia_corta_no_teto():
    assert mod.distancia("campista", "campisla", 1) == 1
    assert mod.distancia("campista", "camplsla", 1) == 2  # teto+1
    assert mod.distancia("costa", "conta", 0) == 1  # teto+1


# ---------------------------------------------------------------------------
# Pre-filtro por metades
# ---------------------------------------------------------------------------

def test_metade_sobrevive_a_uma_edicao():
    esquerda, direita = mod.metades("rothschild")
    for variante in ("rotschild", "rothschlld", "kothschild"):
        assert esquerda in variante or direita in variante


# ---------------------------------------------------------------------------
# Descoberta de variantes: as colisoes medidas na base
# ---------------------------------------------------------------------------

def test_recolhe_variante_de_ocr_do_nome():
    variantes = mod.descobre_variantes(
        ["campista", "campisla", "camplsta", "cambista"],
        ["campista"],
        mod.carrega_exclusoes(),
    )
    assert "campisla" in variantes["campista"]
    assert "cambista" not in variantes["campista"]


@pytest.mark.parametrize(
    "chave, colisao",
    [
        ("carvalhal", "carvalho"),
        ("campista", "cambista"),
        ("pinheiro", "dinheiro"),
        ("sarmento", "sargento"),
        ("murtinho", "martinho"),
        ("felisbello", "felisberto"),
        ("orlando", "orando"),
        ("bulhoes", "bilhoes"),
    ],
)
def test_colisao_medida_fica_de_fora(chave, colisao):
    variantes = mod.descobre_variantes(
        [chave, colisao], [chave], mod.carrega_exclusoes()
    )
    assert chave in variantes[chave]
    assert colisao not in variantes[chave]


@pytest.mark.parametrize(
    "chave, colisao",
    [
        ("campista", "cambista"),
        ("pinheiro", "dinheiro"),
        ("sarmento", "sargento"),
        ("murtinho", "martinho"),
        ("orlando", "orando"),
        ("bulhoes", "bilhoes"),
    ],
)
def test_e_a_lista_de_exclusao_que_segura_a_colisao(chave, colisao):
    """Sem a lista, estas casariam: a distancia de edicao entre elas e 1.

    Existe para que o teste anterior nao passe por acidente. As colisoes que
    a propria distancia ja recusa (carvalhal/carvalho, felisbello/felisberto,
    a 2 edicoes) nao entram aqui.
    """
    sem_lista = mod.descobre_variantes([chave, colisao], [chave], {})
    assert colisao in sem_lista[chave]


def test_token_curto_nao_aceita_variante():
    variantes = mod.descobre_variantes(
        ["costa", "conta", "consta", "custa"], ["costa"], {}
    )
    assert variantes["costa"] == {"costa"}


def test_forma_exata_entra_mesmo_estando_na_lista_de_exclusao():
    variantes = mod.descobre_variantes(["pena"], ["pena"], {"pena": "palavra corrente"})
    assert variantes["pena"] == {"pena"}


# ---------------------------------------------------------------------------
# Localizacao do nome no texto
# ---------------------------------------------------------------------------

def _indice(vocabulario, tokens_chave):
    return mod.indice_de_formas(
        mod.descobre_variantes(vocabulario, tokens_chave, mod.carrega_exclusoes())
    )


def test_nome_composto_exige_adjacencia():
    texto = "o sr. barbosa disse que o sr. lima votou contra"
    ator = mod.Ator("Barbosa Lima", "parlamentar", (("barbosa", "lima"),), "teste")
    indice = _indice(mod.TOKEN.findall(texto), ["barbosa", "lima"])
    assert mod.posicoes(texto, ator, indice) == []

    texto2 = "o sr. barbosa lima votou contra"
    indice2 = _indice(mod.TOKEN.findall(texto2), ["barbosa", "lima"])
    assert mod.posicoes(texto2, ator, indice2) == [texto2.index("barbosa")]


def test_variante_de_ocr_e_localizada():
    texto = "discurso do sr. campisla sobre a caixa"
    ator = mod.Ator("David Campista", "parlamentar", (("campista",),), "teste")
    indice = _indice(mod.TOKEN.findall(texto), ["campista"])
    assert mod.posicoes(texto, ator, indice) == [texto.index("campisla")]


def test_sobrenome_do_alferes_da_guarda_nao_vira_o_deputado():
    """Colisao medida na amostra de conferencia de 2026-08-03.

    A escala da guarda do quartel lista "na caixa de conversao, tenente
    peixoto". Com a chave `peixoto` sozinha isso virava Carlos Peixoto a 28
    caracteres da mencao, e o deputado subia ao terceiro lugar do ranking por
    causa da escala militar. A chave passou a exigir o nome composto.
    """
    texto = "guardas: na caixa de conversao, tenente peixoto, ambos do 1 regimento"
    elenco = mod.carrega_elenco()
    ator = next(a for a in elenco if a.nome == "Carlos Peixoto")
    indice = _indice(mod.TOKEN.findall(texto), ator.tokens)
    assert mod.posicoes(texto, ator, indice) == []

    texto2 = "o sr. carlos peixoto deu parecer favoravel ao projecto da caixa de conversao"
    indice2 = _indice(mod.TOKEN.findall(texto2), ator.tokens)
    assert mod.posicoes(texto2, ator, indice2) == [texto2.index("carlos")]


def test_ator_com_duas_formas_localiza_qualquer_uma():
    texto = "o sr. ruy barbosa e depois o sr. rui barbosa"
    ator = mod.Ator("Rui/Ruy Barbosa", "parlamentar",
                    (("rui", "barbosa"), ("ruy", "barbosa")), "teste")
    indice = _indice(mod.TOKEN.findall(texto), ["rui", "ruy", "barbosa"])
    assert len(mod.posicoes(texto, ator, indice)) == 2


# ---------------------------------------------------------------------------
# Distancia ate a mencao
# ---------------------------------------------------------------------------

def test_distancia_minima_toma_o_par_mais_proximo():
    assert mod.distancia_minima([10, 900], [1000]) == 100
    assert mod.distancia_minima([1000], [10, 900]) == 100


def test_distancia_minima_recusa_lado_vazio():
    with pytest.raises(ValueError):
        mod.distancia_minima([], [10])


def test_mencoes_usam_a_regra_de_nome_ratificada():
    texto = "a caixa de conversao e a caixa de amortizacao"
    assert len(mod.mencoes_em(texto)) == 1


def test_medida_ponta_a_ponta_numa_pagina_sintetica():
    texto = (
        "o sr. campista defendeu o projecto da caixa de conversao "
        + "x" * 5000
        + " o sr. rothschild em londres"
    )
    indice = _indice(mod.TOKEN.findall(texto), ["campista", "rothschild"])
    mencoes = mod.mencoes_em(texto)
    campista = mod.Ator("David Campista", "parlamentar", (("campista",),), "teste")
    roth = mod.Ator("Rothschild", "banqueiro_externo", (("rothschild",),), "teste")
    perto = mod.distancia_minima(mod.posicoes(texto, campista, indice), mencoes)
    longe = mod.distancia_minima(mod.posicoes(texto, roth, indice), mencoes)
    assert perto < 100
    assert longe > 4000
