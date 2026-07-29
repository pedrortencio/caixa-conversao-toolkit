"""Testes da amostra de leitura para caracterização das fases.

Protocolo em `docs/plano-leitura-fases.md`. O que precisa ser garantido: a
seleção é determinística (a semente entra no manifesto), nenhuma peça aparece
em duas camadas, e a fronteira negativa não vaza para as camadas substantivas.
"""

from __future__ import annotations

import unittest

import pandas as pd

from pipeline.triagem import amostra_leitura


def peca(item_id: str, **campos) -> dict:
    base = {
        "item_id": item_id,
        "jornal": "o_paiz",
        "source_year": 1906,
        "data": pd.Timestamp("1906-09-15"),
        "data_confiavel": 1,
        "source_identifier": f"per178691_1906_{item_id}",
        "page_number": 1,
        "forma": "noticia",
        "secao": "",
        "titulo": f"titulo {item_id}",
        "registro": "substantivo",
        "status": "keep",
    }
    base.update(campos)
    base["fase"] = amostra_leitura.fase(base["source_year"])
    return base


class FaseTests(unittest.TestCase):
    def test_fronteiras_das_fases(self) -> None:
        self.assertEqual(amostra_leitura.fase(1906), "F1")
        self.assertEqual(amostra_leitura.fase(1907), "F2")
        self.assertEqual(amostra_leitura.fase(1909), "F2")
        self.assertEqual(amostra_leitura.fase(1910), "F3")
        self.assertEqual(amostra_leitura.fase(1913), "F3")
        self.assertEqual(amostra_leitura.fase(1914), "F4")


class SelecionaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.d = pd.DataFrame(
            [
                peca("e1", forma="editorial"),
                peca("e2", forma="editorial", source_year=1914,
                     data=pd.Timestamp("1914-08-20")),
                peca("a1", forma="artigo"),
                # Notícia substantiva fora de qualquer janela de episódio.
                peca("n1", data=pd.Timestamp("1907-05-02"), source_year=1907),
                # Notícia substantiva dentro da janela da criação.
                peca("n2", data=pd.Timestamp("1906-11-10")),
                peca("r1", registro="operacional_rotina"),
                peca("i1", registro="incidental"),
                # Peça descartada na limpeza, não pode ser selecionada.
                peca("x1", forma="editorial", status="drop_disclaimer"),
            ]
        )
        self.d = self.d[self.d["status"] == "keep"].copy()

    def test_camada_0_pega_todo_editorial_e_artigo_substantivo(self) -> None:
        ficha = amostra_leitura.seleciona(self.d)
        c0 = set(ficha[ficha["camada"] == "0_censo_editorial_artigo"]["item_id"])
        self.assertEqual(c0, {"e1", "e2", "a1"})

    def test_nenhuma_peca_em_duas_camadas(self) -> None:
        ficha = amostra_leitura.seleciona(self.d)
        self.assertEqual(len(ficha), ficha["item_id"].nunique())

    def test_episodio_nao_reaproveita_peca_da_camada_0(self) -> None:
        ficha = amostra_leitura.seleciona(self.d)
        c1 = set(ficha[ficha["camada"] == "1_episodio"]["item_id"])
        self.assertIn("n2", c1)
        self.assertNotIn("e1", c1)

    def test_rotina_e_incidental_so_na_fronteira_negativa(self) -> None:
        ficha = amostra_leitura.seleciona(self.d)
        for item in ("r1", "i1"):
            camada = ficha[ficha["item_id"] == item]["camada"].item()
            self.assertEqual(camada, "3_fronteira_negativa")

    def test_selecao_e_deterministica(self) -> None:
        a = amostra_leitura.seleciona(self.d)
        b = amostra_leitura.seleciona(self.d)
        self.assertEqual(list(a["item_id"]), list(b["item_id"]))

    def test_campos_de_leitura_saem_vazios(self) -> None:
        ficha = amostra_leitura.seleciona(self.d)
        for campo in amostra_leitura.CAMPOS_LEITURA:
            self.assertTrue((ficha[campo] == "").all(), campo)


if __name__ == "__main__":
    unittest.main()
