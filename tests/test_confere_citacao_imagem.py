"""Testes da conferencia de citacao contra a imagem do scan.

O que precisa nao falhar: a guarda contra alucinacao. Uma transcricao que nao
seja reconhecivelmente a mesma passagem do OCR nao pode receber veredito `ok`,
porque `ok` e o que autoriza a leitura de imagem a ir para revisao.
"""
from __future__ import annotations

import pytest

from pipeline.analise import confere_citacao_imagem as mod


def trecho(**kwargs) -> mod.Trecho:
    base = dict(id="x", encontrado=True, transcricao="", legibilidade="legivel", nota=None)
    return mod.Trecho(**{**base, **kwargs})


# --- normalizacao e similaridade ---------------------------------------------


def test_normalizacao_ignora_espaco_que_o_ocr_comeu():
    """`agentesfinanceiros` e `agentes financeiros` sao a mesma leitura."""
    assert mod.normaliza_para_comparar("agentesfinanceiros") == mod.normaliza_para_comparar(
        "agentes financeiros"
    )


def test_normalizacao_ignora_diacritico_e_caixa():
    assert mod.normaliza_para_comparar("Opinião") == mod.normaliza_para_comparar("opiniao")


def test_similaridade_alta_no_pior_ocr_do_manifesto():
    """O caso que motivou o modulo tem de passar do limiar."""
    sim = mod.similaridade(
        "quando recebeu 111:1 lelcgraiimia de aos-sos banqueiros em Londres",
        "quando recebeu um telegramma de nossos banqueiros em Londres",
    )
    assert sim >= mod.LIMIAR_SIMILARIDADE


def test_similaridade_baixa_entre_passagens_diferentes():
    sim = mod.similaridade(
        "quando recebeu 111:1 lelcgraiimia de aos-sos banqueiros em Londres",
        "o ouro sera retirado hoje da Caixa de Conversao pelo Thesouro Federal",
    )
    assert sim < mod.LIMIAR_SIMILARIDADE


def test_similaridade_zero_com_transcricao_vazia():
    assert mod.similaridade("qualquer coisa", "") == 0.0


# --- veredito ----------------------------------------------------------------


def test_ok_quando_a_leitura_corrige_o_mesmo_trecho():
    t = trecho(transcricao="um telegramma de nossos banqueiros em Londres")
    situacao, sim = mod.julga(t, "recebeu 111:1 lelcgraiimia de aos-sos banqueiros em Londres")
    assert situacao == "ok"
    assert sim > 0.6


def test_divergente_quando_a_transcricao_e_outra_passagem():
    """A alucinacao que a ancoragem no OCR existe para barrar."""
    t = trecho(transcricao="os banqueiros de Paris recusaram o emprestimo")
    situacao, _ = mod.julga(t, "recebeu 111:1 lelcgraiimia de aos-sos banqueiros em Londres")
    assert situacao == "divergente"


def test_nao_encontrada_e_resultado_legitimo():
    situacao, sim = mod.julga(trecho(encontrado=False), "qualquer citacao")
    assert (situacao, sim) == ("nao_encontrada", 0.0)


def test_nao_encontrada_quando_a_transcricao_vem_vazia():
    situacao, _ = mod.julga(trecho(encontrado=True, transcricao="   "), "qualquer citacao")
    assert situacao == "nao_encontrada"


def test_devolver_o_proprio_ocr_de_volta_nao_e_correcao():
    """Similaridade 1.0 com o OCR e leitura que nao leu: fica em ok, mas a
    revisao humana precisa ver que nada mudou. O teste fixa o comportamento."""
    ocr = "111:1 lelcgraiimia de aos-sos banqueiros"
    situacao, sim = mod.julga(trecho(transcricao=ocr), ocr)
    assert situacao == "ok"
    assert sim == pytest.approx(1.0)


# --- reconciliacao entre as duas leituras ------------------------------------


def test_estavel_quando_as_duas_leituras_coincidem():
    veredito, acordo = mod.reconcilia(
        "um telegramma de nossos banqueiros em Londres",
        "um telegramma de nossos banqueiros em Londres",
        "recebeu 111:1 lelcgraiimia de aos-sos banqueiros em Londres",
    )
    assert veredito == "estavel"
    assert acordo == pytest.approx(1.0)


def test_estavel_ignora_diferenca_so_de_acento_e_espaco():
    veredito, _ = mod.reconcilia(
        "opposição acerba movida por elle",
        "opposicao  acerba movida por elle",
        "op|)Osicão ncerba movi-«Ia nor clle",
    )
    assert veredito == "estavel"


def test_instavel_quando_as_leituras_discordam_de_uma_palavra():
    """O caso `cm1913-murtinho`: `acerba` numa leitura, `occulta` na outra."""
    veredito, acordo = mod.reconcilia(
        "da opposição acerba movida por elle Rodrigues Alves",
        "da opposição occulta movida por elle Rodrigues Alves",
        "da op|)Osicão ncerba movi-«Ia nor clle Rodrigues Alves",
    )
    assert veredito == "instavel"
    assert acordo < 1.0


def test_divergente_do_ocr_quando_uma_leitura_foge_da_passagem():
    veredito, _ = mod.reconcilia(
        "os banqueiros de Paris recusaram tudo",
        "os banqueiros de Paris recusaram tudo",
        "recebeu 111:1 lelcgraiimia de aos-sos banqueiros em Londres",
    )
    assert veredito == "divergente_do_ocr"


def test_leitura_ausente_quando_um_dos_passes_nao_leu():
    assert mod.reconcilia("", "alguma leitura", "ocr") == ("leitura_ausente", 0.0)
    assert mod.reconcilia("alguma leitura", "", "ocr") == ("leitura_ausente", 0.0)


def test_junta_passes_casa_por_id_e_preserva_o_ocr():
    p1 = [
        {"id": "a", "citacao_imagem": "leitura estavel", "citacao_ocr": "leilura estavcl",
         "similaridade": "0.900", "legibilidade": "legivel", "pdf": "x.pdf", "pagina_pdf": "1"},
    ]
    p2 = [{"id": "a", "citacao_imagem": "leitura estavel"}]
    junto = mod.junta_passes(p1, p2)
    assert junto[0]["veredito"] == "estavel"
    assert junto[0]["citacao_ocr"] == "leilura estavcl"
    assert junto[0]["leitura_2"] == "leitura estavel"


def test_junta_passes_marca_ausencia_quando_o_segundo_passe_nao_tem_a_linha():
    p1 = [{"id": "a", "citacao_imagem": "leitura", "citacao_ocr": "leilura"}]
    assert mod.junta_passes(p1, [])[0]["veredito"] == "leitura_ausente"


# --- omissoes: a guarda que as duas leituras nao dao -------------------------


def test_omissao_pega_a_palavra_que_as_duas_leituras_engoliram():
    """`gn1906-282-rei`: o OCR tem `reidos`, a imagem devolveu so `dos`."""
    perdidas = mod.omissoes(
        "ás opiniões do reidos banqueiros londrinos",
        "ás opiniões dos banqueiros londrinos",
    )
    assert any("rei" in p for p in perdidas)


def test_omissao_pega_trecho_longo_alisado():
    """`op1908-ouro-onde`: `palacio dourado da avenida` virou `cofre`."""
    perdidas = mod.omissoes(
        "ter o ouro aqui no palaciodourado da avenida, ou tel-o em londres",
        "ter o ouro aqui no cofre, ou tel-o em Londres",
    )
    assert any("dourado" in p for p in perdidas)


def test_sem_omissao_quando_a_leitura_so_desfaz_ruido_de_ocr():
    assert mod.omissoes(
        "aos nossos agentes financeiros- emLondres",
        "aos nossos agentes financeiros em Londres",
    ) == []


def test_omissao_ignora_diferenca_de_uma_ou_duas_letras():
    assert mod.omissoes("o emprostimo de libras", "o emprestimo de libras") == []


# --- adicoes: a guarda que as omissoes nao dao -------------------------------


def test_adicao_pega_texto_que_a_leitura_inventou():
    """`cm1906-aventura`: as duas leituras acrescentaram `cidas aventuras.`,
    ausente de toda a pagina. O erro e correlacionado e passa pelas duas."""
    postas = mod.adicoes(
        "que não estAdisposto a embarcar em novas e desconhe-",
        "que não está disposto a embarcar em novas e desconhecidas aventuras.",
    )
    assert any("aventuras" in p for p in postas)


def test_sem_adicao_quando_a_leitura_so_desfaz_ruido_de_ocr():
    assert mod.adicoes(
        "aos nossos agentes financeiros- emLondres",
        "aos nossos agentes financeiros em Londres",
    ) == []


def test_adicao_ignora_diferenca_de_uma_ou_duas_letras():
    assert mod.adicoes("o emprostimo de libras", "o emprestimo de libras") == []


def test_adicao_e_a_omissao_com_os_papeis_trocados():
    ocr, leitura = "o ouro em londres", "o ouro guardado em londres"
    assert mod.adicoes(ocr, leitura) == mod.omissoes(leitura, ocr)


def test_estendida_quando_as_duas_leituras_concordam_mas_alongam_a_passagem():
    """Duas leituras identicas nao se absolvem: concordam porque o erro e
    correlacionado. `estendida` nomeia essa falha, que `instavel` nao pega."""
    leitura = "que não está disposto a embarcar em novas e desconhecidas aventuras."
    veredito, acordo = mod.reconcilia(
        leitura, leitura, "que não estAdisposto a embarcar em novas e desconhe-"
    )
    assert veredito == "estendida"
    assert acordo == pytest.approx(1.0)


def test_estavel_sobrevive_a_adicao_curta():
    """Recompor palavra que o OCR comeu e o trabalho da camada, nao defeito."""
    veredito, _ = mod.reconcilia(
        "um telegramma de nossos banqueiros em Londres",
        "um telegramma de nossos banqueiros em Londres",
        "recebeu 111:1 lelcgraiimia de aos-sos banqueiros em Londres",
    )
    assert veredito == "estavel"


def test_ancoragem_no_ocr_vem_antes_da_deteccao_de_adicao():
    veredito, _ = mod.reconcilia(
        "os banqueiros de Paris recusaram tudo e mais alguma coisa inventada",
        "os banqueiros de Paris recusaram tudo e mais alguma coisa inventada",
        "recebeu 111:1 lelcgraiimia de aos-sos banqueiros em Londres",
    )
    assert veredito == "divergente_do_ocr"


def test_junta_passes_publica_as_adicoes():
    p1 = [
        {"id": "a", "citacao_ocr": "novas e desconhe-",
         "citacao_imagem": "novas e desconhecidas aventuras."},
    ]
    p2 = [{"id": "a", "citacao_imagem": "novas e desconhecidas aventuras."}]
    junto = mod.junta_passes(p1, p2)
    assert "aventuras" in junto[0]["adicoes_vs_ocr"]
    assert junto[0]["veredito"] == "estendida"


# --- a pagina decide se a adicao e recuperacao ou invencao -------------------


PAGINA = (
    "movimento do porto e cotacoes do dia. Que diriam de tal acto? Pois a "
    "quebrado padrao, s:in tirar nem por, e a mesmacoisa. seguem os anuncios."
)


def test_adicao_que_esta_impressa_na_pagina_casa_alto():
    """`op1912-quebra`: a leitura acrescentou `Que diriam de tal acto?`, e a
    frase ESTA na pagina. A ancora curada e que era curta demais."""
    assert mod.casamento_na_pagina("Que diriam de tal acto?", PAGINA) > 0.95


def test_adicao_ausente_da_pagina_nao_casa():
    """`cm1906-aventura`: `desconhecidas aventuras.` nao aparece em lugar nenhum
    da pagina. Esta e a invencao que a guarda existe para pegar."""
    assert mod.casamento_na_pagina("desconhecidas aventuras.", PAGINA) < 0.6


def test_casamento_tolera_ruido_de_ocr_na_pagina():
    """`op1910-concordata`: a pagina traz `utantosabalo`, colado e sem o s."""
    assert mod.casamento_na_pagina("tantos abalos", "texto utantosabalo mais texto") > 0.85


def test_casamento_vazio_nao_casa_com_nada():
    assert mod.casamento_na_pagina("", PAGINA) == 0.0
    assert mod.casamento_na_pagina("qualquer coisa", "") == 0.0


def test_caminho_do_passe_separa_os_dois_arquivos(tmp_path):
    base = tmp_path / "citacoes_conferidas_imagem.csv"
    assert mod.caminho_do_passe(1, base).name == "leitura_imagem_passe1.csv"
    assert mod.caminho_do_passe(2, base).name == "leitura_imagem_passe2.csv"


# --- resolucao de fonte ------------------------------------------------------


def test_caminho_de_pagina_de_jornal(tmp_path):
    caminho = mod.caminho_do_pdf("103730", "per103730_1906_00282", raw_pdf=tmp_path)
    assert caminho == tmp_path / "103730" / "per103730_1906_00282.pdf"


def test_caminho_do_retrospecto_e_o_volume_do_ano(tmp_path):
    caminho = mod.caminho_do_retrospecto("1907", raw_pdf=tmp_path)
    assert caminho == tmp_path / "jc_retrospecto" / "per180688_1907_00001.pdf"


def test_pagina_do_retrospecto_sai_do_censo_de_paginas():
    linhas = [
        {"ano": "1907", "page_number": "7", "texto": "embora conhecida a opiniao desfavoravel"},
        {"ano": "1907", "page_number": "8", "texto": "os quaes sempre negaram apoio"},
        {"ano": "1906", "page_number": "7", "texto": "os quaes sempre negaram apoio"},
    ]
    assert mod.pagina_do_retrospecto("1907", "os quaes sempre negaram apoio", linhas) == 8


def test_pagina_do_retrospecto_falha_alto_quando_nao_acha():
    with pytest.raises(ValueError):
        mod.pagina_do_retrospecto("1907", "frase que nao esta la", [])


def test_resolve_alvos_das_duas_fontes(tmp_path):
    manifesto = [
        {
            "id": "gn1906",
            "fonte_tipo": "pagina",
            "bib": "103730",
            "objeto": "per103730_1906_00282",
            "pagina": "1",
            "ano": "1906",
            "citacao_verbatim": "as opinioes do reidos banqueiros",
        },
        {
            "id": "jc1907",
            "fonte_tipo": "retrospecto",
            "bib": "",
            "objeto": "retrospecto_1907_caixa.txt",
            "pagina": "0",
            "ano": "1907",
            "citacao_verbatim": "negaram apoio",
        },
    ]
    retro = [{"ano": "1907", "page_number": "8", "texto": "os quaes sempre negaram apoio"}]
    alvos = mod.resolve_alvos(manifesto, retro, raw_pdf=tmp_path)
    assert alvos[0].pagina_pdf == 1
    assert alvos[0].pdf.name == "per103730_1906_00282.pdf"
    assert alvos[1].pagina_pdf == 8
    assert alvos[1].pdf.name == "per180688_1907_00001.pdf"


def test_agrupa_por_pagina_para_uma_chamada_por_pagina(tmp_path):
    pdf = tmp_path / "a.pdf"
    alvos = [
        mod.Alvo("a", "x", pdf, 1),
        mod.Alvo("b", "y", pdf, 1),
        mod.Alvo("c", "z", pdf, 2),
    ]
    grupos = mod.agrupa_por_pagina(alvos)
    assert len(grupos) == 2
    assert [a.id for a in grupos[(pdf, 1)]] == ["a", "b"]


def test_prompt_carrega_todos_os_ids_da_pagina(tmp_path):
    pdf = tmp_path / "a.pdf"
    prompt = mod.monta_prompt([mod.Alvo("a", "trecho um", pdf, 1), mod.Alvo("b", "trecho dois", pdf, 1)])
    assert "[a]" in prompt and "[b]" in prompt
    assert "trecho um" in prompt and "trecho dois" in prompt
