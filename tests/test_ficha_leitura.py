"""Testes do preenchimento assistido da ficha de leitura.

O que precisa de teste aqui nao e o prompt, e o contrato: o vocabulario que a
ficha aceita, a correspondencia um-para-um entre objeto e direcao, e a gravacao
que nao corrompe acento nem perde trabalho no meio da sessao.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from pipeline.leitura import campos as mod
from pipeline.leitura import ficha


def campo(nome: str) -> mod.Campo:
    return next(c for c in mod.CAMPOS if c.nome == nome)


# ---------------------------------------------------------------- vocabulario

def test_vazio_sempre_passa():
    for c in mod.CAMPOS:
        assert mod.valida(c, "  ") == ""


def test_voz_recusa_valor_fora_do_vocabulario():
    with pytest.raises(mod.ErroDeCampo, match="vocabulario"):
        mod.valida(campo("voz"), "editorial")


def test_voz_aceita_o_termo_exato_e_normaliza_caixa():
    assert mod.valida(campo("voz"), "  Editorial_Do_Jornal ") == "editorial_do_jornal"


def test_voz_recusa_dois_valores():
    with pytest.raises(mod.ErroDeCampo, match="um valor so"):
        mod.valida(campo("voz"), "assinado;indeterminado")


def test_objeto_aceita_varios_e_preserva_a_ordem():
    assert mod.valida(campo("objeto_politica"), "lastro; taxa") == "lastro;taxa"


def test_data_masthead_exige_formato_iso():
    with pytest.raises(mod.ErroDeCampo, match="AAAA-MM-DD"):
        mod.valida(campo("data_masthead"), "25/09/1906")
    assert mod.valida(campo("data_masthead"), "1906-09-25") == "1906-09-25"


def test_campo_livre_colapsa_espaco_mas_preserva_acento():
    valor = mod.valida(campo("posicao_declarada"), "defende  a  valorização")
    assert valor == "defende a valorização"


def test_vocabulario_epoca_preserva_verbatim_com_acento():
    valor = mod.valida(campo("vocabulario_epoca"), "agio; padrão ouro ;troco de notas")
    assert valor == "agio;padrão ouro;troco de notas"


# -------------------------------------------------- direcao casa com o objeto

def test_direcao_precisa_de_um_veredito_por_objeto():
    with pytest.raises(mod.ErroDeCampo, match="um para um"):
        mod.valida_direcao_casa_objeto("taxa;lastro", "ortodoxo")


def test_direcao_um_para_um_passa():
    mod.valida_direcao_casa_objeto("taxa;lastro", "ortodoxo;nao_aplica")


def test_sem_objeto_e_sem_direcao_passa():
    mod.valida_direcao_casa_objeto("", "")


def test_objeto_sem_direcao_e_recusado():
    """Deixar passar equivaleria a completar com nao_aplica por conta propria."""
    with pytest.raises(mod.ErroDeCampo):
        mod.valida_direcao_casa_objeto("taxa", "")


# ------------------------------------------------------------- estado da fila

def test_ficha_conta_como_lida_pela_voz():
    assert not mod.esta_preenchida({"voz": ""})
    assert mod.esta_preenchida({"voz": "assinado"})


def test_peca_de_rotina_sem_campos_nao_e_cobrada_pelo_estrito():
    assert mod.pendencias_do_estrito({"registro": "operacional_rotina"}) == []


def test_peca_substantiva_cobra_os_campos_que_o_codebook_consome():
    faltando = mod.pendencias_do_estrito({"registro": "substantivo", "voz": "assinado"})
    assert "vocabulario_epoca" in faltando
    assert "dificuldade" in faltando
    assert "voz" not in faltando


# ------------------------------------------------------------------- caminhos

def test_caminho_do_pdf_usa_o_bib_de_seis_digitos(tmp_path):
    linha = {"jornal": "o_paiz", "source_identifier": "per178691_1906_07832",
             "page_number": "1"}
    assert mod.caminho_pdf(linha, tmp_path) == (
        tmp_path / "raw_pdf" / "178691" / "per178691_1906_07832.pdf"
    )


def test_caminho_do_ocr_zera_a_pagina_em_tres_digitos(tmp_path):
    linha = {"jornal": "gazeta_noticias", "source_identifier": "per103730_1906_00239",
             "page_number": "5"}
    assert mod.caminho_texto_ocr(linha, tmp_path).name == "p005.txt"


def test_jornal_desconhecido_e_recusado(tmp_path):
    with pytest.raises(mod.ErroDeCampo, match="jornal desconhecido"):
        mod.caminho_pdf({"jornal": "estadao"}, tmp_path)


# ------------------------------------------------------- conferencia frouxa

def test_citacao_identica_ao_ocr_e_reconhecida(tmp_path):
    pagina = tmp_path / "p001.txt"
    pagina.write_text("a caixa de conversao foi creada em 1906", encoding="utf-8")
    assert "casa o OCR" in ficha.confere_citacao("A Caixa de Conversão foi creada", pagina)


def test_citacao_com_ruido_de_ocr_avisa_sem_bloquear(tmp_path):
    """O OCR e sujo e a transcricao vem da imagem: divergir e o caso normal."""
    pagina = tmp_path / "p001.txt"
    pagina.write_text("o indiffe-rente governo resolveu transferir o ouro para "
                      "londres com os agentes financeiros", encoding="utf-8")
    aviso = ficha.confere_citacao(
        "o indifferente governo resolveu transferir o ouro para Londres", pagina)
    assert "ATENCAO" not in aviso
    assert "palavras batem" in aviso


def test_citacao_de_outra_pagina_dispara_atencao(tmp_path):
    pagina = tmp_path / "p001.txt"
    pagina.write_text("cotacoes do mercado de assucar e algodao", encoding="utf-8")
    aviso = ficha.confere_citacao(
        "quebrar o padrao equivale a reduzir o valor devido aos credores", pagina)
    assert "ATENCAO" in aviso


def test_sem_ocr_no_acervo_a_conferencia_se_declara(tmp_path):
    assert "nao conferi" in ficha.confere_citacao("x y z", tmp_path / "nao_existe.txt")


# --------------------------------------------------------------- persistencia

def test_gravacao_e_atomica_e_preserva_utf8_sem_bom(tmp_path):
    caminho = tmp_path / "f.csv"
    caminho.write_text("item_id,voz\na,\n", encoding="utf-8")
    colunas, linhas = ficha.carrega(caminho)
    linhas[0]["voz"] = "editorial_do_jornal"
    linhas[0]["item_id"] = "peça com ç e ã"
    ficha.grava(caminho, colunas, linhas)

    assert not caminho.read_bytes().startswith(b"\xef\xbb\xbf")
    assert "peça com ç e ã" in caminho.read_text(encoding="utf-8")
    assert not (tmp_path / "f.csv.parcial").exists()


def test_a_ficha_real_tem_todas_as_colunas_que_o_modulo_escreve():
    """Regressao: renomear um campo aqui sem mexer no amostrador quebraria tudo."""
    caminho = Path(ficha.FICHA_PADRAO)
    if not caminho.is_file():  # pragma: no cover - so num checkout sem dados
        pytest.skip("ficha nao presente neste checkout")
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        colunas = csv.DictReader(arquivo).fieldnames or []
    for coluna in mod.COLUNAS_LEITURA:
        assert coluna in colunas, coluna
    for coluna in mod.COLUNAS_IDENTIFICACAO:
        assert coluna in colunas, coluna
