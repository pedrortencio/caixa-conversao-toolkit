"""Testes da estimativa do subcorpus substantivo (a medida pivô).

Dívida registrada em `docs/estado-2026-07-23-pos-rotulagem.md`, item 6: o
número que decide o desenho de mensuração (entre 3.000 e 3.750 edições) saía de
script sem teste. Fixtures pequenas, com aritmética conferível à mão.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from pipeline.triagem import estima_subcorpus


class CarregaRotulagemTests(unittest.TestCase):
    """O denominador da proporção substantiva é a amostra `keep`, não tudo o
    que foi parar na planilha."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.xlsx = self.tmp / "rotulagem.xlsx"
        self.csv = self.tmp / "amostra.csv"

    def _escreve(self, itens: list[tuple[str, str, str, str, int]]) -> None:
        """itens: (item_id, jornal, registro, status, source_year)."""
        pd.DataFrame(
            [{"item_id": i, "jornal": j, "registro": r} for i, j, r, _, _ in itens]
        ).to_excel(self.xlsx, index=False)
        pd.DataFrame(
            [
                {"item_id": i, "source_year": a, "status": s}
                for i, _, _, s, a in itens
            ]
        ).to_csv(self.csv, index=False)

    def test_exclui_item_descartado_pela_limpeza(self) -> None:
        """Item rotulado antes da correção do disclaimer segue na planilha,
        mas não é mais peça: a limpeza o marcou `drop_disclaimer`."""
        self._escreve([
            ("a:i1", "o_paiz", "substantivo", "keep", 1910),
            ("a:i2", "o_paiz", "operacional_rotina", "keep", 1910),
            ("a:i3", "o_paiz", "substantivo", "drop_disclaimer", 1910),
        ])
        rot = estima_subcorpus.carrega_rotulagem(self.xlsx, self.csv)
        self.assertEqual(list(rot["item_id"]), ["a:i1", "a:i2"])
        self.assertEqual(rot["subst"].mean(), 0.5)

    def test_celula_em_branco_e_indeterminado_e_sai_do_denominador(self) -> None:
        self._escreve([
            ("a:i1", "o_paiz", "substantivo", "keep", 1910),
            ("a:i2", "o_paiz", None, "keep", 1910),
        ])
        rot = estima_subcorpus.carrega_rotulagem(self.xlsx, self.csv)
        self.assertEqual(list(rot["item_id"]), ["a:i1"])


class ProjetaTests(unittest.TestCase):
    """Piso e teto, com a aritmética conferível à mão.

    Testes de caracterização: fixam a fórmula que já produzia o número
    publicado, para que uma mudança futura não a altere em silêncio.
    """

    def _rot(self, ano: int, subst: list[int]) -> pd.DataFrame:
        return pd.DataFrame({"source_year": ano, "subst": subst})

    def test_piso_e_teto_de_um_ano(self) -> None:
        # p = 0,5. Duas edições, uma com 1 match e outra com 2.
        # piso = 0,5 * 2 = 1,0 (registros perfeitamente correlacionados)
        # teto = (1 - 0,5^1) + (1 - 0,5^2) = 0,5 + 0,75 = 1,25 (independentes)
        rot = self._rot(1910, [1, 1, 0, 0])
        ed = pd.DataFrame({"ano": [1910, 1910], "n_matches": [1, 2]})
        self.assertEqual(estima_subcorpus.projeta(rot, ed), (1.0, 1.25))

    def test_piso_e_teto_coincidem_quando_toda_edicao_tem_um_match(self) -> None:
        """É por isso que a faixa publicada é estreita: a mediana de matches
        por edição é 1."""
        rot = self._rot(1906, [1, 1, 1, 1])
        ed = pd.DataFrame({"ano": [1906] * 3, "n_matches": [1, 1, 1]})
        self.assertEqual(estima_subcorpus.projeta(rot, ed), (3.0, 3.0))

    def test_ano_sem_amostra_rotulada_nao_entra_na_projecao(self) -> None:
        """Ano do censo sem nenhuma peça rotulada não tem `p`, e entrar com
        zero seria afirmar ausência de substantivo em vez de ausência de
        medida."""
        rot = self._rot(1910, [1, 0])
        ed = pd.DataFrame({"ano": [1910, 1913], "n_matches": [1, 1]})
        piso, teto = estima_subcorpus.projeta(rot, ed)
        self.assertEqual((piso, teto), (0.5, 0.5))


if __name__ == "__main__":
    unittest.main()
