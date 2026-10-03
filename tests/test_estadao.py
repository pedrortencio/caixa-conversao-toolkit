"""Testes das utilidades do scraper do acervo do Estadao.

O teste que sustenta o resto e `test_rejeita_miniatura`. O acervo serve a mesma
pagina em dois caminhos, `/p/` (miniatura, dezenas de KB) e `/g/` (alta, ~1,5 MB),
e os dois devolvem HTTP 200 com JPEG valido. Baixar a miniatura por engano nao
levanta erro em lugar nenhum: produz um corpus silenciosamente ilegivel, que so
apareceria na transcricao, muito depois. O piso de tamanho existe para isso.

`test_parse_nome_*` protege a proveniencia: data, edicao e pagina saem do nome do
arquivo, e sao eles que ligam a imagem a citacao no manifesto.
"""

from __future__ import annotations

import pathlib
import struct
import tempfile
import unittest

from pipeline.scraper import estadao as E


def jpeg_falso(largura: int, altura: int, recheio: int = 0) -> bytes:
    """JPEG minimo com SOF0 legivel, para exercitar a validacao sem baixar nada."""
    sof = b"\xff\xc0" + struct.pack(">H", 17) + b"\x08" + struct.pack(">HH", altura, largura)
    return b"\xff\xd8" + sof + b"\x00" * 8 + b"\x00" * recheio + b"\xff\xd9"


class ParseNomeTests(unittest.TestCase):
    def test_parse_nome_comum(self) -> None:
        m = E.parse_nome("19061207-10228-nac-0001-999-1-not")
        self.assertEqual(m["data"], "1906-12-07")
        self.assertEqual(m["ano"], 1906)
        self.assertEqual(m["edicao"], "10228")
        self.assertEqual(m["caderno"], "nac")
        self.assertEqual(m["pagina"], 1)
        self.assertEqual(m["tipo"], "not")

    def test_parse_nome_classificados(self) -> None:
        m = E.parse_nome("19061207-10228-nac-0006-999-6-clas")
        self.assertEqual(m["pagina"], 6)
        self.assertEqual(m["tipo"], "clas")

    def test_parse_nome_campos_alfanumericos(self) -> None:
        """Pagina censurada e edicao com ordinal alfanumerico nao quebram o parse."""
        m = E.parse_nome("19931025-36531-nac-0027-eco-b3-not")
        self.assertEqual(m["data"], "1993-10-25")
        self.assertEqual(m["pagina"], 27)
        self.assertEqual(m["caderno"], "nac")

    def test_parse_nome_fora_do_padrao_levanta(self) -> None:
        with self.assertRaises(ValueError):
            E.parse_nome("19061207-10228-nac")

    def test_regex_casa_os_quatro_formatos_vistos(self) -> None:
        html = (
            "lixo #!/19060815-10114-nac-0004-999-4-not/busca/x lixo "
            "#!/19760313-30972-nac-0067-cen-5-not lixo "
            "#!/19931025-36531-nac-0027-eco-b3-not lixo "
            "#!/19061207-10228-nac-0006-999-6-clas"
        )
        achados = E.RE_NOME.findall(html)
        self.assertEqual(len(achados), 4)
        self.assertIn("19060815-10114-nac-0004-999-4-not", achados)
        self.assertIn("19931025-36531-nac-0027-eco-b3-not", achados)


class ValidacaoJpegTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _grava(self, nome: str, dados: bytes) -> pathlib.Path:
        p = self.dir / nome
        p.write_bytes(dados)
        return p

    def test_le_dimensoes_do_sof(self) -> None:
        p = self._grava("a.jpg", jpeg_falso(2506, 3362))
        self.assertEqual(E.dimensoes_jpeg(p), (2506, 3362))

    def test_rejeita_miniatura(self) -> None:
        """O caso que motiva o piso: /p/ e JPEG valido, mas nao e a pagina."""
        mini = self._grava("mini.jpg", jpeg_falso(160, 220, recheio=40 * 1024))
        self.assertIsNotNone(E.dimensoes_jpeg(mini))  # e JPEG de verdade
        self.assertFalse(E.eh_jpeg_valido(mini))      # e mesmo assim e recusado

    def test_aceita_pagina_em_alta(self) -> None:
        alta = self._grava("alta.jpg", jpeg_falso(2506, 3362, recheio=1_500 * 1024))
        self.assertTrue(E.eh_jpeg_valido(alta))

    def test_rejeita_html_com_extensao_jpg(self) -> None:
        """Pagina de erro salva como .jpg: sem assinatura, nao passa."""
        erro = self._grava("erro.jpg", b"<html>Servidor ocupado</html>" + b" " * (200 * 1024))
        self.assertIsNone(E.dimensoes_jpeg(erro))
        self.assertFalse(E.eh_jpeg_valido(erro))

    def test_rejeita_arquivo_truncado(self) -> None:
        truncado = self._grava("t.jpg", b"\xff\xd8" + b"\x00" * (200 * 1024))
        self.assertFalse(E.eh_jpeg_valido(truncado))

    def test_rejeita_inexistente(self) -> None:
        self.assertFalse(E.eh_jpeg_valido(self.dir / "nao_existe.jpg"))


class CaminhoEUrlTests(unittest.TestCase):
    def test_caminho_particiona_por_ano(self) -> None:
        raiz = pathlib.Path("/raiz")
        p = E.caminho_local("19061207-10228-nac-0001-999-1-not", raiz)
        self.assertEqual(p.parent.name, "1906")
        self.assertEqual(p.name, "19061207-10228-nac-0001-999-1-not.jpg")

    def test_url_busca_escapa_frase_e_omite_page_1(self) -> None:
        u = E.url_busca('"caixa de conversao"', ano=1906, page=1)
        self.assertIn("year=1906", u)
        self.assertNotIn("page=", u)
        self.assertNotIn(" ", u)

    def test_url_busca_pagina_n(self) -> None:
        self.assertIn("page=7", E.url_busca("x", ano=1910, page=7))

    def test_url_timeline_zero_pad(self) -> None:
        u = E.url_timeline(7, 12, 1906)
        self.assertIn("dia=07", u)
        self.assertIn("mes=12", u)
        self.assertIn("ano=1906", u)


class ContadoresDaBuscaTests(unittest.TestCase):
    """Regressao das duas armadilhas de contagem que ja produziram leitura errada.

    Na primeira passada eu li "Foram encontrados N registros" como se fosse o
    tamanho do conjunto de resultados e comparei com paginas distintas. Os dois
    erros se somaram e fabricaram uma taxa de perda de 15,6% que nao existe.
    """

    HTML = (
        '<p>Foram encontrados 179 registros para</p>'
        '<h2>RESULTADO DE BUSCA PARA <span>"caixa de conversao" (156)</span></h2>'
        '<h3>Exibindo 156 ocorr&ecirc;ncias<span></span></h3>'
        '<script>$("#conteudo_decada").html("Servidor ocupado.<br>Aguarde.");</script>'
        '<a href="#!/19080306-10680-nac-0001-999-1-not">x</a>'
        '<a href="#!/19080306-10680-nac-0001-999-1-not">x</a>'
        '<a href="#!/19080331-10705-nac-0001-999-1-not">y</a>'
    )

    def test_le_ocorrencias_e_nao_registros(self) -> None:
        from pipeline.scraper.estadao_enumera import RE_OCORRENCIAS

        m = RE_OCORRENCIAS.search(self.HTML)
        self.assertIsNotNone(m)
        self.assertEqual(int(m.group(1)), 156)  # nao 179

    def test_ocorrencia_nao_e_pagina(self) -> None:
        """A mesma pagina casa o termo duas vezes e aparece duas vezes."""
        achados = E.RE_NOME.findall(self.HTML)
        self.assertEqual(len(achados), 3)          # ocorrencias servidas
        self.assertEqual(len(set(achados)), 2)     # paginas distintas

    def test_conta_cards_desconta_a_repeticao_de_marcacao(self) -> None:
        """Cada card repete o nome N vezes; contar cru infla o total em Nx."""
        from pipeline.scraper.estadao_enumera import conta_cards

        a, b = "19080306-10680-nac-0001-999-1-not", "19080331-10705-nac-0001-999-1-not"
        self.assertEqual(conta_cards([a] * 5 + [b] * 5), 2)   # 10 brutos, 2 resultados
        self.assertEqual(conta_cards([a] * 3 + [b] * 3), 2)   # fator 3 do template sem sessao
        self.assertEqual(conta_cards([]), 0)

    def test_conta_cards_com_pagina_repetida_no_resultado(self) -> None:
        """Pagina que casa duas vezes ocupa dois cards e conta dois."""
        from pipeline.scraper.estadao_enumera import conta_cards

        a, b = "19080306-10680-nac-0001-999-1-not", "19080331-10705-nac-0001-999-1-not"
        achados = [a] * 10 + [b] * 5  # 'a' em dois cards, 'b' em um
        self.assertEqual(conta_cards(achados), 3)
        self.assertEqual(len(set(achados)), 2)  # e sao 2 paginas distintas

    def test_servidor_ocupado_no_js_nao_marca_falha(self) -> None:
        """A string aparece em TODA resposta boa, num handler JS de fallback.

        Tratar a presenca dela como erro derrubava toda pagina no retry e
        devolvia zero resultados para o ano inteiro.
        """
        self.assertIn("Servidor ocupado", self.HTML)
        self.assertTrue(E.RE_NOME.findall(self.HTML))  # e ainda assim tem resultado


class IntegridadeTests(unittest.TestCase):
    """O indice do acervo tem defeito medido, em duas classes que pedem acoes opostas."""

    def _linha(self, nome: str, data: str, edicao: str, sha: str = "") -> dict:
        return {"nome_arquivo": nome, "data": data, "edicao": edicao, "sha256": sha}

    def test_detecta_data_fantasma_por_sha(self) -> None:
        from pipeline.scraper.estadao_integridade import duplicatas_por_sha

        man = [
            self._linha("19130715-12658-nac-0003-999-3-not", "1913-07-15", "12658", "abc"),
            self._linha("19130815-12658-nac-0003-999-3-not", "1913-08-15", "12658", "abc"),
            self._linha("19130816-12659-nac-0001-999-1-not", "1913-08-16", "12659", "def"),
        ]
        achados = duplicatas_por_sha(man)
        self.assertEqual(len(achados), 1)
        # o descartado e o de julho, nao o de agosto
        self.assertEqual(achados[0]["data"], "1913-07-15")
        self.assertEqual(achados[0]["classe"], "B_data_fantasma")

    def test_detecta_edicao_corrompida_por_inversao(self) -> None:
        from pipeline.scraper.estadao_integridade import inversoes_data_edicao

        man = [
            self._linha("a", "1910-05-09", "11470"),
            self._linha("b", "1910-05-10", "11174"),  # deveria ser 11471
            self._linha("c", "1910-05-11", "11472"),
        ]
        achados = inversoes_data_edicao(man)
        self.assertEqual(len(achados), 1)
        self.assertEqual(achados[0]["data"], "1910-05-10")
        self.assertIn("11471", achados[0]["acao_sugerida"])

    def test_fantasma_nao_gera_falso_positivo_de_edicao(self) -> None:
        """A ordem importa: sem ignorar o fantasma, o dia seguinte parece corrompido."""
        from pipeline.scraper.estadao_integridade import inversoes_data_edicao

        man = [
            self._linha("real14", "1913-07-14", "12626"),
            self._linha("fantasma", "1913-07-15", "12658"),  # edicao de agosto
            self._linha("real16", "1913-07-16", "12628"),    # correta, mas parece queda
        ]
        self.assertEqual(len(inversoes_data_edicao(man)), 1)          # falso positivo
        self.assertEqual(len(inversoes_data_edicao(man, {"fantasma"})), 0)  # limpo

    def test_serie_sadia_nao_acusa_nada(self) -> None:
        from pipeline.scraper.estadao_integridade import (
            duplicatas_por_sha,
            inversoes_data_edicao,
        )

        man = [self._linha(f"n{i}", f"1906-03-{10 + i:02d}", str(9950 + i), f"sha{i}")
               for i in range(6)]
        self.assertEqual(duplicatas_por_sha(man), [])
        self.assertEqual(inversoes_data_edicao(man), [])


if __name__ == "__main__":
    unittest.main()
