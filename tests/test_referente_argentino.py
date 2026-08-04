"""Testes do marcador de referente argentino.

Cada caso abaixo saiu de uma pagina real do corpus, lida na investigacao de
31/07/2026. Os tres primeiros sao falsos positivos que a primeira versao do
marcador produziu, e por isso viraram teste: marcador que mede a si mesmo e
o modo mais silencioso de errar uma medida.
"""

from __future__ import annotations

import unittest

from pipeline.analise import referente_argentino as ref


class FalsosPositivosMedidosTests(unittest.TestCase):
    def test_escola_nacional_nao_e_la_nacion(self) -> None:
        # per178691_1908_08607 p4 e per103730_1907_00127 p2.
        texto = "o director da Escola Nacional de Bellas-Artes e o porteiro da caixa de conversão"
        self.assertEqual(ref.classifica(texto), "nenhuma")

    def test_lista_de_moedas_do_boletim_nao_e_materia_argentina(self) -> None:
        # per178691_1911_09732 p2, boletim diario da Caixa brasileira.
        texto = (
            "Foi este o movimento de hontem da Caixa de Conversão: Entradas: libras 2.288, "
            "francos 10, liras 40 e pesos argentinos 10, correspondentes a 34:379$472."
        )
        self.assertEqual(ref.classifica(texto), "moeda")

    def test_grafia_do_ocr_para_a_moeda_tambem_conta_como_moeda(self) -> None:
        self.assertEqual(ref.classifica("5 peso argentiuo e 100 marcos"), "moeda")

    def test_dateline_de_buenos_aires_e_materia_argentina(self) -> None:
        # per178691_1914_11013 p4.
        texto = "ARGENTINA BUENOS AIRES, 1. Pela ultima estatistica os depositos na Caixa de Conversão sobem a 221.676,533 pesos ouro."
        self.assertEqual(ref.classifica(texto), "estrita")

    def test_imprensa_portenha_comentando_a_reforma_brasileira(self) -> None:
        # per178691_1910_09337 p5.
        texto = (
            "El Diario não acredita que o projecto de reforma da lei básica da Caixa de "
            "Conversão brazileira, com a elevação da taxa para 16 d., tenha approvação"
        )
        self.assertEqual(ref.classifica(texto), "estrita")

    def test_precedencia_estrita_sobre_moeda(self) -> None:
        texto = "BUENOS AIRES, 20. entradas de 10 pesos argentinos na Caixa"
        self.assertEqual(ref.classifica(texto), "estrita")

    def test_pagina_brasileira_comum_nao_marca(self) -> None:
        texto = "O Sr. presidente da Republica enviou mensagem pedindo alteração do pessoal da caixa de conversão"
        self.assertEqual(ref.classifica(texto), "nenhuma")


class NormalizacaoTests(unittest.TestCase):
    def test_acento_e_caixa_nao_atrapalham(self) -> None:
        self.assertEqual(ref.classifica("a REPÚBLICA ARGENTINA e sua lei"), "estrita")

    def test_quebra_de_linha_nao_esconde_a_marca(self) -> None:
        self.assertEqual(ref.classifica("noticias de BUENOS\n   AIRES, 3."), "estrita")


if __name__ == "__main__":
    unittest.main()
