from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pipeline.scraper import indice_bndigital


HTML_EXEMPLO = """
<html><body>
<a href="https://hemeroteca-pdf.bn.gov.br/178691/per178691_1906_07755.pdf">7755</a>
<a href="https://hemeroteca-pdf.bn.gov.br/178691/per178691_1906_07756.pdf">7756</a>
<a href="https://hemeroteca-pdf.bn.gov.br/178691/per178691_1906_07756.pdf">7756 repetido</a>
<a href="https://hemeroteca-pdf.bn.gov.br/178691/per178691_1905_07700.pdf">fora do recorte</a>
<a href="https://hemeroteca-pdf.bn.gov.br/178691/per178691_1915_11100.pdf">fora do recorte</a>
<a href="https://hemeroteca-pdf.bn.gov.br/089842/per089842_1906_01635.pdf">outro bib</a>
<a href="/acervo-digital/paiz/178691">link sem pdf</a>
</body></html>
"""


class ExtraiEdicoesTests(unittest.TestCase):
    def test_extrai_dedupe_e_filtra_bib_e_recorte(self) -> None:
        edicoes = indice_bndigital.extrai_edicoes(HTML_EXEMPLO, "178691")
        self.assertEqual({(1906, 7755), (1906, 7756)}, edicoes)

    def test_recorte_de_anos_e_parametrizavel(self) -> None:
        edicoes = indice_bndigital.extrai_edicoes(
            HTML_EXEMPLO, "178691", ano_min=1905, ano_max=1915
        )
        self.assertIn((1905, 7700), edicoes)
        self.assertIn((1915, 11100), edicoes)

    def test_html_sem_links_do_bib_retorna_vazio(self) -> None:
        self.assertEqual(
            set(), indice_bndigital.extrai_edicoes(HTML_EXEMPLO, "999999")
        )


class ManifestoCsvTests(unittest.TestCase):
    def test_le_manifesto_com_cabecalho_ano_numero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "indice_bndigital_178691.csv"
            caminho.write_text(
                "ano,numero\n1906,7755\n1906,7756\n1907,8125\n",
                encoding="utf-8",
            )
            self.assertEqual(
                {(1906, 7755), (1906, 7756), (1907, 8125)},
                indice_bndigital.le_manifesto_csv(caminho),
            )


class ComparaTests(unittest.TestCase):
    def test_conjuntos_iguais_nao_divergem(self) -> None:
        a = {(1906, 7755), (1907, 8125)}
        so_snapshot, so_manifesto = indice_bndigital.compara(a, set(a))
        self.assertEqual([], so_snapshot)
        self.assertEqual([], so_manifesto)

    def test_divergencias_saem_ordenadas(self) -> None:
        snapshot = {(1907, 8125), (1906, 7755)}
        manifesto = {(1906, 7755), (1914, 11042), (1906, 7000)}
        so_snapshot, so_manifesto = indice_bndigital.compara(snapshot, manifesto)
        self.assertEqual([(1907, 8125)], so_snapshot)
        self.assertEqual([(1906, 7000), (1914, 11042)], so_manifesto)


class VerificaTests(unittest.TestCase):
    def test_verifica_por_bib_com_snapshot_e_manifesto_em_disco(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "snapshot_bndigital_178691_teste.html").write_text(
                HTML_EXEMPLO, encoding="utf-8"
            )
            (raiz / "indice_bndigital_178691.csv").write_text(
                "ano,numero\n1906,7755\n1906,7757\n", encoding="utf-8"
            )
            resultado = indice_bndigital.verifica_bib(
                bib="178691",
                snapshot=raiz / "snapshot_bndigital_178691_teste.html",
                manifesto=raiz / "indice_bndigital_178691.csv",
            )
            self.assertEqual(2, resultado.total_snapshot)
            self.assertEqual(2, resultado.total_manifesto)
            self.assertEqual([(1906, 7756)], resultado.so_snapshot)
            self.assertEqual([(1906, 7757)], resultado.so_manifesto)
            self.assertFalse(resultado.identicos)


if __name__ == "__main__":
    unittest.main()
