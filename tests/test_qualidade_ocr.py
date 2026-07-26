"""Testes da medida de qualidade do OCR por grupo.

Pré-requisito 4 de `docs/todo-fightin-words.md`: sem medir o ruído por célula
jornal-ano, a análise lexical distintiva devolve as palavras do pior scanner em
vez das palavras do jornal. As funções de métrica são puras sobre texto, para
que o número publicado seja conferível sem banco.
"""

from __future__ import annotations

import unittest

from pipeline.analise import qualidade_ocr


class MetricasTests(unittest.TestCase):
    def test_token_sem_vogal_e_ruido_de_ocr(self) -> None:
        m = qualidade_ocr.metricas("casa xhtq praça")
        self.assertAlmostEqual(m["taxa_sem_vogal"], 1 / 3)

    def test_ortografia_de_epoca_com_y_nao_conta_como_ruido(self) -> None:
        """`y` era vogal na ortografia da época (Nictheroy, Bahya). Contá-la
        como ruído puniria o texto mais antigo, que é justamente 1906."""
        m = qualidade_ocr.metricas("Nictheroy Bahya")
        self.assertEqual(m["taxa_sem_vogal"], 0.0)

    def test_numeros_e_pontuacao_ficam_fora_da_contagem(self) -> None:
        m = qualidade_ocr.metricas("o cambio de 15 3/4 dinheiros, hontem.")
        self.assertEqual(m["n_tokens"], 5)

    def test_hapax_e_proporcao_do_vocabulario_nao_dos_tokens(self) -> None:
        """Vocabulário {caixa, de, conversao}: só `conversao` aparece uma vez
        em 4 tokens, então 1/3 do vocabulário, não 1/4 dos tokens."""
        m = qualidade_ocr.metricas("caixa de caixa de conversao")
        self.assertAlmostEqual(m["taxa_hapax"], 1 / 3)

    def test_comprimento_medio_pesa_por_ocorrencia(self) -> None:
        m = qualidade_ocr.metricas("ab ab abcd")
        self.assertAlmostEqual(m["comprimento_medio"], (2 + 2 + 4) / 3)

    def test_texto_vazio_nao_divide_por_zero(self) -> None:
        m = qualidade_ocr.metricas("")
        self.assertEqual(m["n_tokens"], 0)
        self.assertEqual(m["taxa_sem_vogal"], 0.0)
        self.assertEqual(m["taxa_hapax"], 0.0)


class AgregaTests(unittest.TestCase):
    def test_agrega_soma_o_vocabulario_da_celula(self) -> None:
        """A célula é a unidade: hapax tem que ser medido no vocabulário
        somado, senão página curta infla a taxa."""
        m = qualidade_ocr.agrega(["caixa de conversao", "caixa de conversao"])
        self.assertEqual(m["taxa_hapax"], 0.0)
        self.assertEqual(m["n_tokens"], 6)
        self.assertEqual(m["n_paginas"], 2)


class AmostraTests(unittest.TestCase):
    def test_amostra_e_deterministica_por_celula(self) -> None:
        pop = [f"pagina{i}" for i in range(100)]
        a = qualidade_ocr.amostra(pop, 10, chave="178691-1906")
        b = qualidade_ocr.amostra(pop, 10, chave="178691-1906")
        c = qualidade_ocr.amostra(pop, 10, chave="178691-1909")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertEqual(len(a), 10)

    def test_amostra_menor_que_o_pedido_devolve_a_populacao(self) -> None:
        self.assertEqual(len(qualidade_ocr.amostra(["a", "b"], 10, chave="x")), 2)


if __name__ == "__main__":
    unittest.main()
