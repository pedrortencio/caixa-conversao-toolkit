"""Testes da sonda difusa de "Caixa de Conversão".

A sonda é um instrumento de MEDIÇÃO DE FALHA, não um casador de produção. Ela
existe para responder uma pergunta que o censo não responde sobre si mesmo:
quantas páginas o casador exato `regra_nome` deixou passar porque o OCR da BN
destruiu a expressão.

Dois testes carregam o resto:

`test_nao_altera_o_casador_exato` trava a separação entre os dois instrumentos.
A sonda importa `regra_nome` e nunca o modifica: se a sonda pudesse mexer no
casador, o censo passaria a medir contra si mesmo e o portão de 1906 mudaria de
lugar sem ninguém aprovar.

`test_determinismo` trava a reprodutibilidade: mesma página, mesma saída, mesma
ordem. Sem isso nenhum número da sonda é reconferível.

Os casos de quase-acerto (`QuaseAcertoTests`) são transcritos de páginas reais
do acervo, não inventados: cada um é uma menção que o casador exato perdeu.
"""

from __future__ import annotations

import unittest

from pipeline.triagem import regra_nome
from pipeline.triagem import sonda_difusa as sd


class VariantesTests(unittest.TestCase):
    def test_inclui_a_forma_exata(self) -> None:
        self.assertIn("caixa", sd.variantes_com_um_erro("caixa"))

    def test_inclui_substituicao_delecao_e_insercao(self) -> None:
        variantes = set(sd.variantes_com_um_erro("caixa"))
        self.assertIn("ca.xa", variantes)  # substituição: "calxa"
        self.assertIn("caxa", variantes)  # deleção: OCR comeu o "i"
        self.assertIn("cai.xa", variantes)  # inserção: "cai-xa", "cai xa"

    def test_deterministico_e_sem_repeticao(self) -> None:
        primeira = sd.variantes_com_um_erro("conver")
        segunda = sd.variantes_com_um_erro("conver")
        self.assertEqual(primeira, segunda)
        self.assertEqual(len(primeira), len(set(primeira)))


class DistanciaTests(unittest.TestCase):
    def test_zero_quando_o_padrao_e_subcadeia(self) -> None:
        self.assertEqual(sd.distancia_subcadeia("abc", "xxabcxx"), 0)

    def test_conta_uma_substituicao(self) -> None:
        self.assertEqual(sd.distancia_subcadeia("abc", "xxaXcxx"), 1)

    def test_conta_uma_delecao(self) -> None:
        self.assertEqual(sd.distancia_subcadeia("abc", "xxacxx"), 1)

    def test_janela_vazia_custa_o_padrao_inteiro(self) -> None:
        self.assertEqual(sd.distancia_subcadeia("abc", ""), 3)

    def test_inicio_e_fim_livres_no_lado_da_janela(self) -> None:
        # A janela pode sobrar dos dois lados sem custo; o padrão, não.
        self.assertEqual(
            sd.distancia_subcadeia(sd.CANONICA, "hontem na caixa de conversao 11.490"),
            0,
        )


class QuaseAcertoTests(unittest.TestCase):
    """Trechos reais em que o casador exato falha e a sonda precisa acertar."""

    PERDIDOS = (
        "director da cai-xa de conversao.",  # hífen fora de quebra de linha
        "hontem da cai.xa de conversao constou apenas",  # ponto no meio
        "proveniente do thesoureiro da ca xa de conversao",  # espaço no meio
        "director, quand meme, da caixa.de conversao",  # ponto no conector
        "o deposito de ouro, hontem, na caixa,1c conversao",  # conector destruído
        "a caixa rie conversao vai remetter",  # conector "de" virou "rie"
        "guardas: na ca-ixa da conversao, o alferes",  # hífen dentro de caixa
    )

    def test_o_casador_exato_realmente_perde_esses_trechos(self) -> None:
        for trecho in self.PERDIDOS:
            with self.subTest(trecho=trecho):
                self.assertEqual(regra_nome.encontra(trecho), [])

    def test_a_sonda_recupera_esses_trechos(self) -> None:
        for trecho in self.PERDIDOS:
            with self.subTest(trecho=trecho):
                candidatos = sd.encontra_difuso(trecho)
                self.assertEqual(len(candidatos), 1, trecho)
                self.assertLessEqual(candidatos[0].distancia, 3)
                self.assertFalse(candidatos[0].sobrepoe_exato)

    def test_marca_sobreposicao_quando_o_casador_exato_ja_acha(self) -> None:
        candidatos = sd.encontra_difuso("a caixa de conversão recebeu ouro")
        self.assertEqual(len(candidatos), 1)
        self.assertEqual(candidatos[0].distancia, 0)
        self.assertTrue(candidatos[0].sobrepoe_exato)

    def test_nao_casa_os_falsos_amigos(self) -> None:
        for texto in (
            "a caixa de correio da esquina",
            "a caixa de amortização do thesouro",
            "a caixa de socorros dos operarios",
            "o convenio de Taubaté e o convite aos convidados",
            "conversão da divida externa",  # sem o nome "caixa" não é o objeto
        ):
            with self.subTest(texto=texto):
                self.assertEqual(sd.encontra_difuso(texto), [])

    def test_respeita_a_distancia_maxima(self) -> None:
        texto = "caixa de conver e mais nada"
        self.assertTrue(sd.encontra_difuso(texto, distancia_maxima=8))
        self.assertEqual(sd.encontra_difuso(texto, distancia_maxima=1), [])

    def test_offset_e_contexto_referem_o_texto_normalizado(self) -> None:
        texto = "PREFACIO. A Cai-xa de Conversão."
        normalizado = regra_nome.normaliza(texto)
        candidato = sd.encontra_difuso(texto)[0]
        self.assertEqual(
            normalizado[candidato.offset : candidato.fim], candidato.trecho
        )
        self.assertIn(candidato.trecho, candidato.contexto)


class SeparacaoDosInstrumentosTests(unittest.TestCase):
    def test_nao_altera_o_casador_exato(self) -> None:
        """A sonda lê `regra_nome`; mexer nele deslocaria o censo e o portão."""
        antes = regra_nome.encontra("a caixa de conversão")
        sd.encontra_difuso("cai-xa de conversao " * 5)
        depois = regra_nome.encontra("a caixa de conversão")
        self.assertEqual(antes, depois)
        self.assertEqual(regra_nome.REGRA_VERSAO, "triagem/nome-caixa-conversao 1.0.0")

    def test_determinismo(self) -> None:
        texto = "na cai-xa de conversao e depois na caixa de con-versao outra vez"
        self.assertEqual(sd.encontra_difuso(texto), sd.encontra_difuso(texto))

    def test_candidatos_saem_em_ordem_de_offset(self) -> None:
        texto = "caixa de conversao. muito texto no meio. cai-xa de conversao."
        offsets = [c.offset for c in sd.encontra_difuso(texto)]
        self.assertEqual(offsets, sorted(offsets))
        self.assertEqual(len(offsets), 2)


class RegistroDePaginaTests(unittest.TestCase):
    BASE = dict(
        bib="178691",
        ano=1906,
        source_identifier="per178691_1906_07890",
        page_number=3,
        hit_censo=0,
    )

    def test_pagina_com_quase_acerto(self) -> None:
        registro = sd.registro_de_pagina(
            **self.BASE, texto="o saldo da cai-xa de conversao era"
        )
        self.assertEqual(registro["status"], "ok")
        self.assertEqual(registro["n_candidatos"], 1)
        self.assertEqual(registro["melhor_distancia"], 1)
        self.assertEqual(registro["protocol_version"], sd.VERSAO)
        self.assertEqual(len(registro["candidatos"]), 1)

    def test_pagina_sem_candidato_registra_distancia_ausente(self) -> None:
        registro = sd.registro_de_pagina(**self.BASE, texto="noticias do porto")
        self.assertEqual(registro["status"], "ok")
        self.assertEqual(registro["n_candidatos"], 0)
        self.assertIsNone(registro["melhor_distancia"])

    def test_pagina_vazia_vira_linha_com_status_proprio(self) -> None:
        registro = sd.registro_de_pagina(**self.BASE, texto="  \n ")
        self.assertEqual(registro["status"], "empty")
        self.assertEqual(registro["n_candidatos"], 0)

    def test_pagina_ilegivel_vira_linha_com_status_proprio(self) -> None:
        """Ausência nunca é inferida do silêncio: falha é linha, não sumiço."""
        registro = sd.registro_de_pagina(**self.BASE, texto=None)
        self.assertEqual(registro["status"], "arquivo_ausente")
        self.assertEqual(registro["n_candidatos"], 0)
        self.assertIsNone(registro["texto_sha256"])

    def test_grava_hash_do_texto_lido(self) -> None:
        registro = sd.registro_de_pagina(**self.BASE, texto="qualquer coisa")
        self.assertEqual(len(registro["texto_sha256"]), 64)


class AgregacaoTests(unittest.TestCase):
    def registros(self) -> list[dict]:
        base = dict(bib="178691", ano=1906, source_identifier="obj", hit_censo=0)
        return [
            sd.registro_de_pagina(**base, page_number=1, texto="cai-xa de conversao"),
            sd.registro_de_pagina(**base, page_number=2, texto="nada aqui"),
            sd.registro_de_pagina(**base, page_number=3, texto=None),
            sd.registro_de_pagina(**base, page_number=4, texto=" "),
        ]

    def test_contagens_da_celula_fecham_com_o_total(self) -> None:
        (celula,) = sd.agrega_celulas(self.registros())
        self.assertEqual(celula["bib"], "178691")
        self.assertEqual(celula["ano"], 1906)
        self.assertEqual(celula["jornal"], "o_paiz")
        self.assertEqual(celula["paginas"], 4)
        self.assertEqual(
            celula["paginas_ok"] + celula["paginas_vazias"] + celula["paginas_ausentes"],
            celula["paginas"],
        )

    def test_conta_paginas_por_limiar_de_forma_cumulativa(self) -> None:
        (celula,) = sd.agrega_celulas(self.registros())
        self.assertEqual(celula["paginas_d1"], 1)
        self.assertEqual(celula["paginas_d3"], 1)
        self.assertEqual(celula["paginas_d0"], 0)

    def test_separa_celulas_por_bib_ano_e_braco(self) -> None:
        base = dict(source_identifier="obj", page_number=1, texto="nada")
        registros = [
            sd.registro_de_pagina(bib="178691", ano=1906, hit_censo=0, **base),
            sd.registro_de_pagina(bib="178691", ano=1907, hit_censo=0, **base),
            sd.registro_de_pagina(bib="089842", ano=1906, hit_censo=0, **base),
            sd.registro_de_pagina(bib="178691", ano=1906, hit_censo=1, **base),
        ]
        celulas = sd.agrega_celulas(registros)
        self.assertEqual(len(celulas), 4)
        self.assertEqual(
            [(c["bib"], c["ano"], c["hit_censo"]) for c in celulas],
            sorted((c["bib"], c["ano"], c["hit_censo"]) for c in celulas),
        )


class TrechosParaInspecaoTests(unittest.TestCase):
    def linhas(self) -> list[dict]:
        return [
            {"distancia": d, "bib": "178691", "source_identifier": "o", "page_number": p, "offset": 0}
            for p, d in enumerate([0, 1, 2, 3, 4, 5, 6, 7, 8], start=1)
        ]

    def test_ordena_pela_proximidade_do_limiar(self) -> None:
        escolhidos = sd.trechos_para_inspecao(self.linhas(), limiar=3, quantidade=3)
        self.assertEqual([linha["distancia"] for linha in escolhidos], [3, 2, 4])

    def test_respeita_a_quantidade_pedida(self) -> None:
        self.assertEqual(len(sd.trechos_para_inspecao(self.linhas(), 3, 5)), 5)

    def test_deterministico(self) -> None:
        primeira = sd.trechos_para_inspecao(self.linhas(), 3, 9)
        segunda = sd.trechos_para_inspecao(self.linhas(), 3, 9)
        self.assertEqual(primeira, segunda)


if __name__ == "__main__":
    unittest.main()
