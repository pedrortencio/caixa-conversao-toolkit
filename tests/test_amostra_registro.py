"""Testes do amostrador estratificado de contextos (Passo 1 da medida de
substância). Reusa o fixture de banco de test_triagem, sem rerodar testes."""

from __future__ import annotations

import unittest
from pathlib import Path

from pipeline.triagem import amostra_registro
from tests.test_triagem import FixtureBancoTriagem


class EnumeraMatchesTests(FixtureBancoTriagem):
    def test_enumera_um_match_por_span_com_contexto(self) -> None:
        self._semeia(
            "178691", 1906, "00001",
            ["a creacao da caixa de conversao para fixar o cambio", None],
        )
        matches = list(amostra_registro.enumera_matches(self.conn, bib="178691"))
        self.assertEqual(1, len(matches))
        m = matches[0]
        self.assertEqual("per178691_1906_00001:p001:o13", m.match_id)
        self.assertEqual("178691", m.bib)
        self.assertEqual(1906, m.source_year)
        self.assertEqual(1, m.page_number)
        self.assertIn("caixa de conver", m.texto)
        self.assertIn("creacao da caixa de conversao para fixar", m.contexto)

    def test_pagina_sem_texto_nao_entra(self) -> None:
        self._semeia("178691", 1906, "00002", [None])
        matches = list(amostra_registro.enumera_matches(self.conn, bib="178691"))
        self.assertEqual([], matches)


class AmostraEstratificadaTests(FixtureBancoTriagem):
    def _semeia_celula(self, bib: str, ano: int, n: int) -> None:
        for i in range(n):
            self._semeia(
                bib, ano, f"{i:05d}",
                [f"item {i} sobre a caixa de conversao e o cambio"],
            )

    def test_amostra_por_celula_e_determinista(self) -> None:
        self._semeia_celula("178691", 1906, 20)
        self._semeia_celula("090972", 1906, 5)
        a = amostra_registro.amostra_estratificada(
            self.conn, por_celula=3, semente=7
        )
        celulas: dict[tuple[str, int], int] = {}
        for m in a:
            chave = (m.bib, m.source_year)
            celulas[chave] = celulas.get(chave, 0) + 1
        self.assertEqual(3, celulas[("178691", 1906)])
        self.assertEqual(3, celulas[("090972", 1906)])
        b = amostra_registro.amostra_estratificada(
            self.conn, por_celula=3, semente=7
        )
        self.assertEqual([m.match_id for m in a], [m.match_id for m in b])

    def test_celula_menor_que_cota_leva_tudo(self) -> None:
        self._semeia_celula("178691", 1906, 2)
        a = amostra_registro.amostra_estratificada(
            self.conn, por_celula=5, semente=1
        )
        self.assertEqual(2, len(a))


class EscreveAmostraTests(FixtureBancoTriagem):
    def test_csv_deterministico_com_coluna_registro_vazia(self) -> None:
        self._semeia("178691", 1906, "00001", ["a caixa de conversao aqui"])
        matches = list(
            amostra_registro.enumera_matches(self.conn, bib="178691")
        )
        caminho = self.tmp / "amostra.csv"
        n = amostra_registro.escreve_amostra(matches, caminho)
        self.assertEqual(1, n)
        primeira = caminho.read_bytes()
        amostra_registro.escreve_amostra(matches, caminho)
        self.assertEqual(primeira, caminho.read_bytes())
        linhas = primeira.decode("utf-8").splitlines()
        self.assertEqual(
            ",".join(amostra_registro.CABECALHO_AMOSTRA), linhas[0]
        )
        self.assertTrue(linhas[0].endswith(",registro"))
        self.assertTrue(linhas[1].endswith(","))
        self.assertIn("per178691_1906_00001:p001:o", linhas[1])


class ParseDataMastheadTests(unittest.TestCase):
    def test_data_por_extenso_normaliza(self) -> None:
        from pipeline.triagem.recupera_amostra import parse_data_masthead
        self.assertEqual(
            "1906-05-11",
            parse_data_masthead(
                "RIO DE JANEIRO, Sexta-feira 11 de Maio de 1906"
            ),
        )
        self.assertEqual(
            "1906-01-13",
            parse_data_masthead("SABBADO 13 DE JANEIRO DE 1906"),
        )

    def test_sem_data_devolve_none(self) -> None:
        from pipeline.triagem.recupera_amostra import parse_data_masthead
        self.assertIsNone(parse_data_masthead("texto qualquer sem data"))
        self.assertIsNone(parse_data_masthead("13 de mesinho de 1906"))


if __name__ == "__main__":
    unittest.main()
