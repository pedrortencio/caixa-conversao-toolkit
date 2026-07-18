from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from pipeline.base import relatorio_censo
from pipeline.base.carrega_censo import CAMPOS_MANIFESTO


def escreve_manifesto(caminho: Path, linhas: list[dict[str, object]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as saida:
        escritor = csv.DictWriter(saida, fieldnames=CAMPOS_MANIFESTO)
        escritor.writeheader()
        for linha in linhas:
            base = {campo: "" for campo in CAMPOS_MANIFESTO}
            base.update(linha)
            escritor.writerow(base)


def linha(numero: int, status: str, **extras: object) -> dict[str, object]:
    return {"numero": numero, "status": status, **extras}


class GabaritoPilotoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.piloto = Path(self.temporary.name)

    def toca(self, relativo: str) -> None:
        caminho = self.piloto / relativo
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text("{}", encoding="utf-8")

    def test_extrai_numeros_por_bib_com_prefixo_e_dedupe(self) -> None:
        self.toca("jsonA_1906/per178691_1906_07819_classificacao_holistica.json")
        self.toca("jsonA_1906/per178691_1906_07820_classificacao_holistica.json")
        self.toca("jsonB_1906/per090972_1906_A15343_classificacao_holistica.json")
        self.toca("jsonB_1906/per090972_1906_15343_classificacao_holistica.json")
        self.toca("jsonB_1906/per999999_1906_00001_classificacao_holistica.json")
        self.toca("jsonB_1906/notas_soltas.json")
        self.toca("Tests/jsonC_1906/per178691_1906_09999_teste.json")
        # Falha de classificação também é hit do piloto: conta no gabarito.
        self.toca("jsonA_1906/per178691_1906_08091_raw_invalid_json.txt")

        gabarito = relatorio_censo.gabarito_piloto(self.piloto)

        self.assertEqual(set(gabarito), {"178691", "090972"})
        self.assertEqual(gabarito["178691"].arquivos, 3)
        self.assertEqual(gabarito["178691"].numeros, {7819, 7820, 8091})
        self.assertEqual(gabarito["090972"].arquivos, 2)
        self.assertEqual(gabarito["090972"].numeros, {15343})


class ResumeAnoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.censo = Path(self.temporary.name) / "censo"
        self.raw = Path(self.temporary.name) / "raw"

    def escreve_ano_misto(self) -> None:
        linhas = [linha(n, "ausente", http_status=404) for n in range(1, 7)]
        linhas += [
            linha(100, "ok", http_status=200, byte_count=1000, page_count=8),
            linha(101, "ausente", http_status=404),
            linha(102, "erro", http_status=""),
            linha(103, "ok", http_status=200, byte_count=500, page_count=4),
            linha(104, "pdf_invalido", http_status=200, byte_count=99),
            linha(105, "ausente", http_status=404),
            linha(106, "ausente", http_status=404),
            linha(107, "ausente", http_status=404),
        ]
        escreve_manifesto(
            self.censo / "varredura_178691_1906.csv", linhas
        )

    def test_contagens_intervalo_buracos_e_fronteira(self) -> None:
        self.escreve_ano_misto()

        resumo = relatorio_censo.resume_ano(
            "178691", 1906, dir_censo=self.censo, raw_root=None
        )

        self.assertEqual(
            resumo.contagens,
            {"ok": 2, "ausente": 10, "erro": 1, "pdf_invalido": 1},
        )
        self.assertEqual(resumo.ok_min, 100)
        self.assertEqual(resumo.ok_max, 103)
        self.assertEqual(resumo.buracos, (101,))
        self.assertEqual(resumo.erros, (102,))
        self.assertEqual(resumo.ausentes_fronteira, 9)
        self.assertEqual(resumo.paginas, 12)
        self.assertEqual(resumo.bytes_ok, 1500)
        self.assertFalse(resumo.concluido)

    def test_marcador_de_conclusao(self) -> None:
        self.escreve_ano_misto()
        (self.censo / "concluido_178691_1906.txt").write_text(
            "2026-07-18", encoding="utf-8"
        )

        resumo = relatorio_censo.resume_ano(
            "178691", 1906, dir_censo=self.censo, raw_root=None
        )

        self.assertTrue(resumo.concluido)

    def test_pdfs_sumidos_do_disco(self) -> None:
        self.escreve_ano_misto()
        pdf = self.raw / "178691" / "per178691_1906_00100.pdf"
        pdf.parent.mkdir(parents=True, exist_ok=True)
        pdf.write_bytes(b"%PDF-1.4 conteudo")

        resumo = relatorio_censo.resume_ano(
            "178691", 1906, dir_censo=self.censo, raw_root=self.raw
        )

        self.assertEqual(resumo.pdfs_sumidos, (103,))


class RecuperacaoNoResumoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.censo = Path(self.temporary.name)

    def test_resume_ano_unifica_varredura_e_recuperacao(self) -> None:
        escreve_manifesto(
            self.censo / "varredura_178691_1907.csv",
            [
                linha(5254, "ausente", http_status=404),
                linha(8125, "ok", http_status=200, byte_count=1000, page_count=8),
            ],
        )
        escreve_manifesto(
            self.censo / "recuperacao_178691_1907.csv",
            [linha(5254, "ok", http_status=200, byte_count=500, page_count=4)],
        )

        resumo = relatorio_censo.resume_ano(
            "178691", 1907, dir_censo=self.censo, raw_root=None
        )

        # Estado final por número: a recuperação prevalece sobre a varredura.
        self.assertEqual(resumo.contagens, {"ok": 2})
        self.assertEqual(resumo.paginas, 12)
        self.assertEqual(resumo.bytes_ok, 1500)

    def test_regressao_1906_conta_ok_da_recuperacao(self) -> None:
        escreve_manifesto(
            self.censo / "varredura_178691_1906.csv",
            [linha(7819, "ausente", http_status=404)],
        )
        escreve_manifesto(
            self.censo / "recuperacao_178691_1906.csv",
            [linha(7819, "ok", http_status=200, byte_count=1, page_count=1)],
        )
        gabarito = {
            "178691": relatorio_censo.Gabarito(
                arquivos=1, numeros=frozenset({7819})
            )
        }

        regressao = relatorio_censo.regressao_1906(gabarito, self.censo)

        self.assertTrue(regressao["178691"].aprovada)


class CoberturaIndiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        raiz = Path(self.temporary.name)
        self.censo = raiz / "censo"
        self.piloto = raiz / "piloto"
        self.piloto.mkdir(parents=True)
        self.censo.mkdir(parents=True)
        with open(
            self.censo / "indice_bndigital_178691.csv",
            "w", encoding="utf-8", newline="",
        ) as saida:
            saida.write("ano,numero\n1907,5254\n1907,7777\n1907,8125\n1907,9999\n")
        escreve_manifesto(
            self.censo / "varredura_178691_1907.csv",
            [
                linha(7777, "ausente", http_status=404),
                linha(8125, "ok", http_status=200, byte_count=1000, page_count=8),
            ],
        )
        escreve_manifesto(
            self.censo / "recuperacao_178691_1907.csv",
            [
                linha(5254, "ok", http_status=200, byte_count=500, page_count=4),
                linha(7777, "ausente", http_status=404),
            ],
        )

    def test_secao_do_indice_conta_ok_terminal_e_pendentes(self) -> None:
        texto = relatorio_censo.gera_relatorio(
            dir_censo=self.censo, dir_piloto=self.piloto, raw_root=None
        )

        self.assertIn("Cobertura contra o índice bndigital", texto)
        # 1907: índice 4, ok 2 (8125 varredura + 5254 recuperação),
        # terminal 1 (7777 com duas observações), pendente 1 (9999).
        self.assertIn("| 1907 | 4 | 2 | 1 | 1 |", texto)
        self.assertIn("pendentes do índice", texto)

    def test_ano_so_com_recuperacao_entra_na_cobertura(self) -> None:
        escreve_manifesto(
            self.censo / "recuperacao_178691_1914.csv",
            [linha(11000, "ok", http_status=200, byte_count=700, page_count=6)],
        )

        texto = relatorio_censo.gera_relatorio(
            dir_censo=self.censo, dir_piloto=self.piloto, raw_root=None
        )

        self.assertIn("| 1914 ", texto)
        self.assertNotIn("o_paiz (178691) 1914", texto)


class RegressaoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.censo = Path(self.temporary.name)

    def test_subconjunto_e_faltantes(self) -> None:
        escreve_manifesto(
            self.censo / "varredura_178691_1906.csv",
            [
                linha(7818, "ausente", http_status=404),
                linha(7819, "ok", http_status=200, byte_count=1, page_count=1),
            ],
        )
        gabarito = {
            "178691": relatorio_censo.Gabarito(
                arquivos=2, numeros=frozenset({7819, 7820})
            )
        }

        regressao = relatorio_censo.regressao_1906(gabarito, self.censo)

        self.assertEqual(regressao["178691"].esperados, 2)
        self.assertEqual(regressao["178691"].presentes, 1)
        self.assertEqual(regressao["178691"].faltantes, (7820,))

    def test_aprovacao_total(self) -> None:
        escreve_manifesto(
            self.censo / "varredura_178691_1906.csv",
            [
                linha(7819, "ok", http_status=200, byte_count=1, page_count=1),
                linha(7820, "ok", http_status=200, byte_count=1, page_count=1),
            ],
        )
        gabarito = {
            "178691": relatorio_censo.Gabarito(
                arquivos=2, numeros=frozenset({7819, 7820})
            )
        }

        regressao = relatorio_censo.regressao_1906(gabarito, self.censo)

        self.assertEqual(regressao["178691"].faltantes, ())
        self.assertTrue(regressao["178691"].aprovada)


class RelatorioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        raiz = Path(self.temporary.name)
        self.censo = raiz / "censo"
        self.piloto = raiz / "piloto"
        escreve_manifesto(
            self.censo / "varredura_178691_1906.csv",
            [
                linha(7819, "ok", http_status=200, byte_count=1000, page_count=8),
                linha(7820, "ausente", http_status=404),
            ],
        )
        (self.censo / "concluido_178691_1906.txt").write_text(
            "2026-07-18", encoding="utf-8"
        )
        json_dir = self.piloto / "jsonO_Paiz_1906"
        json_dir.mkdir(parents=True)
        (json_dir / "per178691_1906_07819_classificacao_holistica.json").write_text(
            "{}", encoding="utf-8"
        )
        (json_dir / "per178691_1906_07820_classificacao_holistica.json").write_text(
            "{}", encoding="utf-8"
        )

    def test_markdown_traz_cobertura_e_regressao(self) -> None:
        texto = relatorio_censo.gera_relatorio(
            dir_censo=self.censo, dir_piloto=self.piloto, raw_root=None
        )

        self.assertIn("178691", texto)
        self.assertIn("1906", texto)
        self.assertIn("REPROVADA", texto)
        self.assertIn("7820", texto)
        # 2 arquivos parseados divergem do gabarito documentado (79): alerta.
        self.assertIn("79", texto)


if __name__ == "__main__":
    unittest.main()
