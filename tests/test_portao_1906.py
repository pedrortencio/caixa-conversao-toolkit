"""Portão de 1906 conforme o pré-registro de 2026-07-18 (docs/decisoes.md, item 3).

O critério antigo (gabarito como subconjunto simples do censo) foi SUBSTITUÍDO.
O critério vigente: todo item do gabarito é atribuído a exatamente uma classe
(unidade canônica reproduzida, manifestação coalescida, exceção terminal
documentada), nenhum item fica inexplicado, e a lista de exceções exige
aprovação expressa de Pedro.
"""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from pipeline.base import portao_1906, relatorio_censo
from pipeline.base.carrega_censo import CAMPOS_MANIFESTO


def escreve_manifesto(caminho: Path, linhas: list[dict[str, object]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as saida:
        escritor = csv.DictWriter(saida, fieldnames=CAMPOS_MANIFESTO)
        escritor.writeheader()
        for item in linhas:
            base = {campo: "" for campo in CAMPOS_MANIFESTO}
            base.update(item)
            escritor.writerow(base)


def linha_ok(numero: int) -> dict[str, object]:
    return {
        "numero": numero,
        "status": "ok",
        "http_status": 200,
        "byte_count": 1,
        "page_count": 1,
    }


class PortaoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.raiz = Path(self.temporary.name)
        self.censo = self.raiz / "censo"
        self.censo.mkdir()
        self.excecoes = self.raiz / "excecoes.json"

    def grava_excecoes(
        self, itens: list[dict[str, object]], aprovado_por: str | None
    ) -> None:
        self.excecoes.write_text(
            json.dumps(
                {
                    "protocolo": "portao-1906",
                    "versao": "1.0.0",
                    "aprovado_por": aprovado_por,
                    "aprovado_em": "2026-07-27" if aprovado_por else None,
                    "excecoes": itens,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def gabarito(self, **por_bib: set[int]) -> dict[str, relatorio_censo.Gabarito]:
        return {
            bib: relatorio_censo.Gabarito(
                arquivos=len(numeros), numeros=frozenset(numeros)
            )
            for bib, numeros in por_bib.items()
        }

    def test_gabarito_integralmente_reproduzido_aprova_sem_excecoes(self) -> None:
        escreve_manifesto(
            self.censo / "varredura_178691_1906.csv",
            [linha_ok(7819), linha_ok(7820)],
        )

        resultado = portao_1906.avalia(
            self.gabarito(**{"178691": {7819, 7820}}), self.censo, self.excecoes
        )

        self.assertTrue(resultado.aprovado)
        self.assertEqual(resultado.reproduzidos, 2)
        self.assertEqual(resultado.inexplicados, ())

    def test_faltante_sem_excecao_fica_inexplicado(self) -> None:
        escreve_manifesto(self.censo / "varredura_178691_1906.csv", [linha_ok(7819)])

        resultado = portao_1906.avalia(
            self.gabarito(**{"178691": {7819, 7820}}), self.censo, self.excecoes
        )

        self.assertFalse(resultado.aprovado)
        self.assertEqual(resultado.inexplicados, (("178691", 7820),))

    def test_excecao_nao_ratificada_por_pedro_nao_explica(self) -> None:
        """A regra que dá sentido ao portão: lista sem aprovação não vale."""
        escreve_manifesto(self.censo / "varredura_089842_1906.csv", [linha_ok(1868)])
        self.grava_excecoes(
            [
                {
                    "bib": "089842",
                    "numero": 1869,
                    "classe": "excecao_terminal",
                    "fonte": "404 terminal, 2 observações (docs/relatorio-cobertura-censo.md)",
                }
            ],
            aprovado_por=None,
        )

        resultado = portao_1906.avalia(
            self.gabarito(**{"089842": {1868, 1869}}), self.censo, self.excecoes
        )

        self.assertFalse(resultado.aprovado)
        self.assertFalse(resultado.lista_aprovada)
        self.assertEqual(resultado.inexplicados, (("089842", 1869),))

    def test_excecao_ratificada_explica_o_faltante(self) -> None:
        escreve_manifesto(self.censo / "varredura_089842_1906.csv", [linha_ok(1868)])
        self.grava_excecoes(
            [
                {
                    "bib": "089842",
                    "numero": 1869,
                    "classe": "excecao_terminal",
                    "fonte": "404 terminal, 2 observações",
                }
            ],
            aprovado_por="Pedro Ortencio",
        )

        resultado = portao_1906.avalia(
            self.gabarito(**{"089842": {1868, 1869}}), self.censo, self.excecoes
        )

        self.assertTrue(resultado.aprovado)
        self.assertTrue(resultado.lista_aprovada)
        self.assertEqual(resultado.excecoes_aceitas, (("089842", 1869),))
        self.assertEqual(resultado.inexplicados, ())

    def test_classe_fora_do_pre_registro_nao_explica(self) -> None:
        escreve_manifesto(self.censo / "varredura_089842_1906.csv", [linha_ok(1868)])
        self.grava_excecoes(
            [
                {
                    "bib": "089842",
                    "numero": 1869,
                    "classe": "sumiu_mesmo",
                    "fonte": "nenhuma",
                }
            ],
            aprovado_por="Pedro Ortencio",
        )

        resultado = portao_1906.avalia(
            self.gabarito(**{"089842": {1868, 1869}}), self.censo, self.excecoes
        )

        self.assertFalse(resultado.aprovado)
        self.assertEqual(resultado.inexplicados, (("089842", 1869),))

    def test_excecao_sem_fonte_nao_explica(self) -> None:
        """'Exceção terminal DOCUMENTADA com fonte' é o texto do pré-registro."""
        escreve_manifesto(self.censo / "varredura_089842_1906.csv", [linha_ok(1868)])
        self.grava_excecoes(
            [{"bib": "089842", "numero": 1869, "classe": "excecao_terminal", "fonte": ""}],
            aprovado_por="Pedro Ortencio",
        )

        resultado = portao_1906.avalia(
            self.gabarito(**{"089842": {1868, 1869}}), self.censo, self.excecoes
        )

        self.assertFalse(resultado.aprovado)
        self.assertEqual(resultado.inexplicados, (("089842", 1869),))

    def test_manifesto_ausente_nao_quebra(self) -> None:
        escreve_manifesto(self.censo / "varredura_178691_1906.csv", [linha_ok(7819)])

        resultado = portao_1906.avalia(
            self.gabarito(**{"178691": {7819, 7820}}),
            self.censo,
            self.raiz / "nao_existe.json",
        )

        self.assertFalse(resultado.aprovado)
        self.assertFalse(resultado.lista_aprovada)
        self.assertEqual(resultado.inexplicados, (("178691", 7820),))

    def test_excecao_para_item_presente_nao_vira_excecao_aceita(self) -> None:
        escreve_manifesto(
            self.censo / "varredura_178691_1906.csv",
            [linha_ok(7819), linha_ok(7820)],
        )
        self.grava_excecoes(
            [
                {
                    "bib": "178691",
                    "numero": 7820,
                    "classe": "excecao_terminal",
                    "fonte": "obsoleta, a edição foi recuperada depois",
                }
            ],
            aprovado_por="Pedro Ortencio",
        )

        resultado = portao_1906.avalia(
            self.gabarito(**{"178691": {7819, 7820}}), self.censo, self.excecoes
        )

        self.assertTrue(resultado.aprovado)
        self.assertEqual(resultado.reproduzidos, 2)
        self.assertEqual(resultado.excecoes_aceitas, ())

    def test_recuperacao_conta_como_reproduzido(self) -> None:
        escreve_manifesto(
            self.censo / "varredura_178691_1906.csv",
            [{"numero": 7819, "status": "ausente", "http_status": 404}],
        )
        escreve_manifesto(self.censo / "recuperacao_178691_1906.csv", [linha_ok(7819)])

        resultado = portao_1906.avalia(
            self.gabarito(**{"178691": {7819}}), self.censo, self.excecoes
        )

        self.assertTrue(resultado.aprovado)
        self.assertEqual(resultado.reproduzidos, 1)


if __name__ == "__main__":
    unittest.main()
