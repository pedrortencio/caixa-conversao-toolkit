"""Testes do estimador de Monroe, Colaresi e Quinn (2008).

O núcleo é função pura sobre contagens, sem banco: as propriedades abaixo são
as que justificaram escolher o método em 2026-07-23, então são elas que
precisam estar presas por teste, não a mecânica de leitura do corpus.

Especificação em `docs/todo-fightin-words.md`.
"""

from __future__ import annotations

import math
import unittest
from collections import Counter

from pipeline.analise import fightin_words as fw


def _corpus(**palavras: int) -> Counter:
    return Counter(palavras)


class NormalizaTests(unittest.TestCase):
    """Regime mínimo ratificado por Pedro em 2026-07-25."""

    def test_minusculas_e_sem_acento(self) -> None:
        self.assertEqual(fw.tokeniza("Café CONVERSÃO câmbio"),
                         ["cafe", "conversao", "cambio"])

    def test_ortografia_de_epoca_e_preservada(self) -> None:
        """A decisão foi NÃO aplicar regras de época: `actual` não vira
        `atual`, `hontem` não vira `ontem`."""
        self.assertEqual(fw.tokeniza("actual hontem"), ["actual", "hontem"])

    def test_numeros_ficam_fora_do_vocabulario(self) -> None:
        self.assertEqual(fw.tokeniza("cambio a 15 dinheiros"),
                         ["cambio", "a", "dinheiros"])


class EstatisticasTests(unittest.TestCase):
    def test_grupos_identicos_nao_tem_termo_distintivo(self) -> None:
        c = _corpus(caixa=50, conversao=40, cambio=30, ouro=20)
        for r in fw.estatisticas(c, Counter(c), piso=0):
            self.assertAlmostEqual(r["z"], 0.0, places=12)

    def test_troca_de_grupo_inverte_o_sinal(self) -> None:
        a = _corpus(caixa=80, cambio=20, ouro=50)
        b = _corpus(caixa=10, cambio=90, ouro=50)
        ida = {r["termo"]: r["z"] for r in fw.estatisticas(a, b, piso=0)}
        volta = {r["termo"]: r["z"] for r in fw.estatisticas(b, a, piso=0)}
        for termo, z in ida.items():
            self.assertAlmostEqual(z, -volta[termo], places=12)

    def test_termo_raro_e_encolhido_mais_que_termo_frequente(self) -> None:
        """A propriedade que motivou a escolha do método: com a MESMA razão
        entre grupos (10 para 1), o termo raro recebe z menor em módulo. É o
        que impede a lista de palavras distintivas de virar lista de erro de
        OCR, que é sempre raro."""
        enchimento = {f"w{i}": 100 for i in range(40)}
        a = _corpus(frequente=1000, rara=10, **enchimento)
        b = _corpus(frequente=100, rara=1, **enchimento)
        z = {r["termo"]: r["z"] for r in fw.estatisticas(a, b, piso=0)}
        self.assertGreater(z["frequente"], z["rara"])

    def test_termo_ausente_de_um_grupo_nao_estoura(self) -> None:
        """Sem o prior, o log iria a menos infinito."""
        a = _corpus(caixa=50, so_em_a=30)
        b = _corpus(caixa=50)
        z = {r["termo"]: r["z"] for r in fw.estatisticas(a, b, piso=0)}
        self.assertTrue(math.isfinite(z["so_em_a"]))
        self.assertGreater(z["so_em_a"], 0)

    def test_piso_de_frequencia_corta_o_termo_raro(self) -> None:
        a = _corpus(caixa=50, hapax=1)
        b = _corpus(caixa=50)
        termos = {r["termo"] for r in fw.estatisticas(a, b, piso=5)}
        self.assertEqual(termos, {"caixa"})

    def test_saida_vem_ordenada_do_grupo_i_para_o_grupo_j(self) -> None:
        a = _corpus(caixa=90, cambio=10, ouro=50)
        b = _corpus(caixa=10, cambio=90, ouro=50)
        zs = [r["z"] for r in fw.estatisticas(a, b, piso=0)]
        self.assertEqual(zs, sorted(zs, reverse=True))

    def test_alpha_zero_maior_encolhe_mais(self) -> None:
        """alpha_0 é o único parâmetro de ajuste, e o to-do exige reportar
        sensibilidade: aumentar o prior tem que aproximar os z de zero."""
        a = _corpus(caixa=80, cambio=20, ouro=50)
        b = _corpus(caixa=10, cambio=90, ouro=50)
        fraco = {r["termo"]: r["z"] for r in fw.estatisticas(a, b, alpha_0=1, piso=0)}
        forte = {r["termo"]: r["z"] for r in fw.estatisticas(a, b, alpha_0=5000, piso=0)}
        self.assertLess(abs(forte["caixa"]), abs(fraco["caixa"]))

    def test_contagens_dos_dois_grupos_saem_na_tabela(self) -> None:
        """Rastreabilidade: a especificação exige a contagem ao lado do z,
        para o termo ser auditável até a evidência."""
        a = _corpus(caixa=90, cambio=40, ouro=30)
        b = _corpus(caixa=10, cambio=40, ouro=30)
        r = next(r for r in fw.estatisticas(a, b, piso=0) if r["termo"] == "caixa")
        self.assertEqual((r["n_i"], r["n_j"], r["n_corpus"]), (90, 10, 100))


class ConteudoTests(unittest.TestCase):
    """Separar tamanho de efeito de tamanho de amostra.

    Com dezenas de milhões de tokens, palavra funcional (`que`, `do`, `ao`)
    alcança z altíssimo com diferença proporcional mínima, porque z cresce com
    a amostra. O delta é o tamanho do efeito e não cresce assim, então é ele
    que separa termo de conteúdo de palavra gramatical.
    """

    def test_delta_pequeno_sai_mesmo_com_z_alto(self) -> None:
        linhas = [
            {"termo": "que", "delta": 0.24, "z": 130.0},
            {"termo": "conversao", "delta": 3.13, "z": 57.8},
        ]
        self.assertEqual(
            [r["termo"] for r in fw.filtra_conteudo(linhas, delta_minimo=1.0)],
            ["conversao"],
        )

    def test_corta_dos_dois_lados(self) -> None:
        linhas = [
            {"termo": "aluga", "delta": -2.77, "z": -88.8},
            {"termo": "rua", "delta": -0.89, "z": -212.3},
        ]
        self.assertEqual(
            [r["termo"] for r in fw.filtra_conteudo(linhas, delta_minimo=1.0)],
            ["aluga"],
        )

    def test_token_de_uma_letra_nao_e_palavra(self) -> None:
        """`i`, `n`, `l` são fragmento de OCR, e aparecem no topo do controle
        com z de centenas."""
        linhas = [
            {"termo": "i", "delta": -1.41, "z": -257.6},
            {"termo": "sk", "delta": -2.04, "z": -72.6},
        ]
        self.assertEqual(
            [r["termo"] for r in fw.filtra_conteudo(linhas, delta_minimo=1.0)],
            ["sk"],
        )

    def test_preserva_a_ordem_recebida(self) -> None:
        linhas = [
            {"termo": "conversao", "delta": 3.13, "z": 57.8},
            {"termo": "libras", "delta": 1.46, "z": 50.8},
        ]
        self.assertEqual(
            [r["termo"] for r in fw.filtra_conteudo(linhas, delta_minimo=1.0)],
            ["conversao", "libras"],
        )


class PiorRuidoTests(unittest.TestCase):
    """O piso de frequência é carga estrutural ou conveniência de leitura?

    Se o termo mais extremo ABAIXO do piso alcança z desprezível, então quem
    suprime o ruído é a padronização pelo erro padrão, e o piso só existe para
    a lista ser legível. Isso é o que se quer poder afirmar numa banca: o
    resultado não depende do corte do analista.
    """

    def test_devolve_o_termo_de_maior_z_abaixo_do_piso(self) -> None:
        enchimento = {f"w{i}": 500 for i in range(60)}
        a = _corpus(frequente=900, ruido=9, quieto=3, **enchimento)
        b = _corpus(frequente=100, ruido=1, quieto=3, **enchimento)
        pior = fw.pior_ruido_abaixo_do_piso(a, b, piso=20)
        self.assertEqual(pior["termo"], "ruido")
        self.assertEqual(pior["n_corpus"], 10)

    def test_ignora_termo_que_esta_acima_do_piso(self) -> None:
        enchimento = {f"w{i}": 500 for i in range(60)}
        a = _corpus(acima=900, abaixo=9, **enchimento)
        b = _corpus(acima=10, abaixo=1, **enchimento)
        self.assertEqual(
            fw.pior_ruido_abaixo_do_piso(a, b, piso=20)["termo"], "abaixo"
        )

    def test_sem_termo_abaixo_do_piso_devolve_none(self) -> None:
        a = _corpus(caixa=90, cambio=40)
        b = _corpus(caixa=10, cambio=40)
        self.assertIsNone(fw.pior_ruido_abaixo_do_piso(a, b, piso=1))


if __name__ == "__main__":
    unittest.main()
