"""Testes do conferidor de citacoes curadas."""
from __future__ import annotations

import pytest

from pipeline.analise import verifica_citacoes as mod


def test_casa_apesar_de_espaco_e_acento():
    fonte = "as opiniões  do\nrei dos banqueiros londrinos"
    assert mod.confere("as opinioes do rei dos banqueiros londrinos", fonte)


def test_casa_apesar_de_hifenizacao_de_quebra_de_coluna():
    fonte = "os agentes finan-\nceiros do Brasil em Londres"
    assert mod.confere("os agentes financeiros do Brasil em Londres", fonte)


def test_nao_casa_quando_a_citacao_conserta_o_ocr():
    """O ponto do conferidor: limpar o OCR quebra a conferencia, e deve."""
    fonte = "o prestigio dos banqueiros da grande banca do jogo universal"
    assert not mod.confere("o prestígio dos banqueiros da grande banca mundial", fonte)


def test_nao_casa_frase_ausente():
    assert not mod.confere("os banqueiros de Paris recusaram", "texto sobre outra coisa")


def test_caminho_de_pagina(tmp_path):
    caminho = mod.caminho_da_fonte(
        "pagina", "103730", "per103730_1906_00282", "1", texto_embutido=tmp_path
    )
    assert caminho == tmp_path / "103730" / "per103730_1906_00282" / "p001.txt"


def test_caminho_de_retrospecto(tmp_path):
    caminho = mod.caminho_da_fonte(
        "retrospecto", "", "retrospecto_1907_caixa.txt", "0", raiz=tmp_path
    )
    assert caminho == tmp_path / "dados" / "retrospecto_jc" / "retrospecto_1907_caixa.txt"


def test_fonte_desconhecida_aborta():
    with pytest.raises(ValueError):
        mod.caminho_da_fonte("planilha", "x", "y", "1")


def test_linha_com_citacao_curta_e_recusada(tmp_path):
    origem = tmp_path / "103730" / "obj"
    origem.mkdir(parents=True)
    (origem / "p001.txt").write_text("texto qualquer", encoding="utf-8")
    linha = {
        "id": "t1", "fonte_tipo": "pagina", "bib": "103730", "objeto": "obj",
        "pagina": "1", "citacao_verbatim": "curta demais",
    }
    assert mod.verifica_linha(linha, texto_embutido=tmp_path).situacao == "curta"


def test_linha_que_nao_casa_e_reportada(tmp_path):
    origem = tmp_path / "103730" / "obj"
    origem.mkdir(parents=True)
    (origem / "p001.txt").write_text("a caixa de conversao recebeu ouro", encoding="utf-8")
    linha = {
        "id": "t2", "fonte_tipo": "pagina", "bib": "103730", "objeto": "obj",
        "pagina": "1", "citacao_verbatim": "os banqueiros ingleses recusaram o emprestimo",
    }
    assert mod.verifica_linha(linha, texto_embutido=tmp_path).situacao == "nao_casa"


def test_linha_valida_passa(tmp_path):
    origem = tmp_path / "103730" / "obj"
    origem.mkdir(parents=True)
    (origem / "p001.txt").write_text(
        "as opiniões do rei dos banqueiros londrinos pesaram", encoding="utf-8"
    )
    linha = {
        "id": "t3", "fonte_tipo": "pagina", "bib": "103730", "objeto": "obj",
        "pagina": "1", "citacao_verbatim": "as opiniões do rei dos banqueiros londrinos",
    }
    assert mod.verifica_linha(linha, texto_embutido=tmp_path).ok


def test_manifesto_do_repo_esta_integralmente_conferido():
    """Portao: nenhuma citacao do relatorio pode deixar de casar com a fonte."""
    if not mod.MANIFESTO_PADRAO.is_file():
        pytest.skip("manifesto ainda nao gerado")
    if not mod.TEXTO_EMBUTIDO.is_dir():
        pytest.skip("camada de texto embutido indisponivel nesta maquina")
    falhas = [r for r in mod.verifica_manifesto() if not r.ok]
    assert falhas == [], f"citacoes que nao casam: {falhas}"
