"""Testes da rodada 1 do Fightin' Words: relevante contra não relevante.

O que precisa estar preso por teste é a CONSTRUÇÃO DOS GRUPOS. A rodada compara
páginas que nomeiam a Caixa com páginas que não a nomeiam, e a medida de
qualidade do OCR de 2026-07-25 mostrou que o ruído varia por célula jornal-ano
(O Paiz vai de 4,84% a 14,33%). Se o controle não espelhar a composição por
célula do tratamento, a lista de termos distintivos mistura debate com scanner.
"""

from __future__ import annotations

import unittest
from collections import Counter

from pipeline.analise import fw_relevancia as fwr


def _pagina(bib: str, ano: int, ed: str, pag: int, hit: int) -> dict:
    return {
        "bib": bib,
        "ano": ano,
        "source_identifier": f"per{bib}_{ano}_{ed}",
        "page_number": pag,
        "hit": hit,
        "result_status": "ok",
    }


def _populacao() -> list[dict]:
    """Duas células. Em 178691-1906 há 2 hits e 20 não hits; em 089842-1910
    há 1 hit e 20 não hits. Um controle sorteado sem estratificar tenderia a
    repartir o controle meio a meio entre as células, e não 2 para 1."""
    linhas = []
    for i in range(20):
        linhas.append(_pagina("178691", 1906, "00001", i + 1, 0))
        linhas.append(_pagina("089842", 1910, "00002", i + 1, 0))
    linhas.append(_pagina("178691", 1906, "00003", 1, 1))
    linhas.append(_pagina("178691", 1906, "00003", 2, 1))
    linhas.append(_pagina("089842", 1910, "00004", 1, 1))
    return linhas


class SelecionaTests(unittest.TestCase):
    def test_controle_tem_o_tamanho_do_tratamento(self) -> None:
        com, sem = fwr.seleciona(_populacao())
        self.assertEqual(len(com), 3)
        self.assertEqual(len(sem), 3)

    def test_controle_espelha_a_composicao_por_celula(self) -> None:
        com, sem = fwr.seleciona(_populacao())
        composicao = Counter((p["bib"], p["ano"]) for p in sem)
        self.assertEqual(composicao[("178691", 1906)], 2)
        self.assertEqual(composicao[("089842", 1910)], 1)

    def test_controle_e_disjunto_do_tratamento(self) -> None:
        com, sem = fwr.seleciona(_populacao())
        chaves = {(p["source_identifier"], p["page_number"]) for p in com}
        for p in sem:
            self.assertNotIn((p["source_identifier"], p["page_number"]), chaves)

    def test_selecao_e_deterministica(self) -> None:
        a = fwr.seleciona(_populacao())[1]
        b = fwr.seleciona(_populacao())[1]
        self.assertEqual([p["source_identifier"] for p in a],
                         [p["source_identifier"] for p in b])

    def test_pagina_sem_camada_de_texto_fica_fora_dos_dois_grupos(self) -> None:
        """Página `empty`/`error` não é evidência de ausência de menção, é
        ausência de medida. Entrar no controle seria contar silêncio de OCR
        como silêncio do jornal."""
        pop = _populacao()
        pop.append({**_pagina("178691", 1906, "00005", 1, 0),
                    "result_status": "empty"})
        com, sem = fwr.seleciona(pop)
        self.assertNotIn("per178691_1906_00005",
                         [p["source_identifier"] for p in sem])

    def test_celula_sem_controle_suficiente_nao_inventa_pagina(self) -> None:
        pop = [_pagina("178691", 1906, "00003", i, 1) for i in range(1, 6)]
        pop.append(_pagina("178691", 1906, "00001", 1, 0))
        com, sem = fwr.seleciona(pop)
        self.assertEqual(len(com), 5)
        self.assertEqual(len(sem), 1)


if __name__ == "__main__":
    unittest.main()
