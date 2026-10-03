"""Testes do protocolo de correção conservadora do OCR embutido.

O teste que sustenta todo o resto é `test_preserva_sequencia_alfanumerica`.
Toda operação do protocolo ou remove caractere não alfanumérico (controle,
espaço, hífen de quebra, pontuação espúria) ou junta pedaços já presentes.
Nenhuma inventa, apaga ou reordena letra e dígito. Enquanto essa invariante
valer, o texto corrigido é uma leitura do mesmo objeto, não uma reescrita, e
a citação continua rastreável à página.

Se uma entrada nova do léxico quebrar esse teste, a entrada está errada, não
o teste: correção que troca letra é reescrita e sai do protocolo.
"""

from __future__ import annotations

import unittest

from pipeline.transcricao import corrige_conservador as cc

ALFANUM = cc.so_alfanumerico


class OperacoesTests(unittest.TestCase):
    def test_remove_controle_preserva_quebra_e_tabulacao(self) -> None:
        texto = "a\x00b\x7fc\nd\te"
        saida, n = cc.remove_controle(texto)
        self.assertEqual(saida, "abc\nd\te")
        self.assertEqual(n, 2)

    def test_dehifeniza_junta_palavra_partida(self) -> None:
        saida, n = cc.dehifeniza("conver-\nsão do paiz")
        self.assertEqual(saida, "conversão do paiz")
        self.assertEqual(n, 1)

    def test_dehifeniza_tolera_espaco_em_volta_da_quebra(self) -> None:
        saida, n = cc.dehifeniza("conver- \r\n  são")
        self.assertEqual(saida, "conversão")
        self.assertEqual(n, 1)

    def test_dehifeniza_nao_junta_quando_o_lado_nao_e_letra(self) -> None:
        # Intervalo de anos e travessão de fala não são palavra partida.
        for texto in ("1906-\n1914", "fala -\nEm 3 de maio", "-\nEm"):
            with self.subTest(texto=texto):
                saida, n = cc.dehifeniza(texto)
                self.assertEqual(saida, texto)
                self.assertEqual(n, 0)

    def test_reflui_linha_continuada(self) -> None:
        saida, n = cc.reflui_linhas("a caixa de\nconversão foi")
        self.assertEqual(saida, "a caixa de conversão foi")
        self.assertEqual(n, 1)

    def test_reflui_nao_atravessa_linha_em_branco(self) -> None:
        texto = "fim de trecho\n\ncomeco de outro"
        saida, n = cc.reflui_linhas(texto)
        self.assertEqual(saida, texto)
        self.assertEqual(n, 0)

    def test_reflui_nao_junta_quando_a_proxima_linha_comeca_maiuscula(self) -> None:
        # Início de período ou de nome próprio: juntar apagaria a estrutura.
        texto = "encerrou a sessao\nEm 3 de maio o Sr. Campista"
        saida, n = cc.reflui_linhas(texto)
        self.assertEqual(saida, texto)
        self.assertEqual(n, 0)

    def test_espaco_pontuacao_cola_pontuacao_na_palavra(self) -> None:
        saida, n = cc.espaco_pontuacao("Finanças . com votos ,em separado")
        self.assertEqual(saida, "Finanças. com votos, em separado")
        # Três operações: dois espaços fechados antes de pontuação e um aberto
        # depois da vírgula colada em `,em`.
        self.assertEqual(n, 3)

    def test_espaco_pontuacao_nao_estraga_numero(self) -> None:
        texto = "1.000$000 e 27 1/2"
        saida, _ = cc.espaco_pontuacao(texto)
        self.assertEqual(saida, texto)

    def test_espaco_pontuacao_colapsa_espaco_repetido(self) -> None:
        saida, n = cc.espaco_pontuacao("caixa    de     conversão")
        self.assertEqual(saida, "caixa de conversão")
        self.assertEqual(n, 2)

    def test_aplica_lexico_so_aceita_forma_da_lista(self) -> None:
        lexico = [("q.ue", "que"), ("C:aixa", "Caixa")]
        saida, n = cc.aplica_lexico("q.ue a C:aixa e q.uem", lexico)
        self.assertEqual(saida, "que a Caixa e q.uem")
        self.assertEqual(n, 2)


class InvarianteTests(unittest.TestCase):
    """A garantia que torna o protocolo defensável na dissertação."""

    CASOS = [
        "",
        "\n\n\t  \n",
        "Caixa de Conver-\nsão , com votos . em separado",
        "a\x00b\x7fc de\nconversão   e  1.000$000",
        "1906-\n1914 e fala -\nEm 3",
        "q.ue a C:aixa n'ão par.a ma.is",
        "AHNO XXIISm muM111\nM0FI.1EDADB DE OI A SOCIEDADE",
        "Caixa do Convërtflo ¦ con-jciiieiuiiu directa",
        "linha final sem quebra",
    ]

    def test_preserva_sequencia_alfanumerica(self) -> None:
        for texto in self.CASOS:
            with self.subTest(texto=texto[:32]):
                resultado = cc.corrige(texto, cc.LEXICO_PADRAO)
                self.assertEqual(ALFANUM(resultado.texto), ALFANUM(texto))

    def test_lexico_padrao_so_remove_caractere_nao_alfanumerico(self) -> None:
        for bruta, corrigida in cc.LEXICO_PADRAO:
            with self.subTest(entrada=bruta):
                self.assertEqual(
                    ALFANUM(corrigida),
                    ALFANUM(bruta),
                    "entrada de léxico que troca letra é reescrita, não correção",
                )

    def test_corrige_e_idempotente(self) -> None:
        for texto in self.CASOS:
            with self.subTest(texto=texto[:32]):
                uma = cc.corrige(texto, cc.LEXICO_PADRAO).texto
                duas = cc.corrige(uma, cc.LEXICO_PADRAO).texto
                self.assertEqual(uma, duas)

    def test_corrige_e_deterministico(self) -> None:
        texto = self.CASOS[2]
        primeira = cc.corrige(texto, cc.LEXICO_PADRAO)
        segunda = cc.corrige(texto, cc.LEXICO_PADRAO)
        self.assertEqual(primeira.texto, segunda.texto)
        self.assertEqual(primeira.operacoes, segunda.operacoes)

    def test_texto_vazio_nao_quebra(self) -> None:
        resultado = cc.corrige("", cc.LEXICO_PADRAO)
        self.assertEqual(resultado.texto, "")
        self.assertEqual(sum(resultado.operacoes.values()), 0)


class ContabilidadeTests(unittest.TestCase):
    def test_operacoes_sao_contadas_por_nome(self) -> None:
        texto = "a\x00b de\nconver-\nsão  ,ok"
        resultado = cc.corrige(texto, cc.LEXICO_PADRAO)
        self.assertEqual(set(resultado.operacoes), set(cc.NOMES_OPERACAO))
        self.assertGreaterEqual(resultado.operacoes["remove_controle"], 1)
        self.assertGreaterEqual(resultado.operacoes["dehifenizacao"], 1)


class ManifestoTests(unittest.TestCase):
    def test_registro_carrega_hash_das_duas_pontas(self) -> None:
        registro = cc.registro_de_pagina(
            bib="178691",
            source_identifier="per178691_1906_07890",
            page_number=1,
            bruto="Caixa de Conver-\nsão",
        )
        self.assertEqual(registro["status"], "ok")
        self.assertEqual(registro["protocol_version"], cc.VERSAO)
        self.assertNotEqual(
            registro["raw_text_sha256"], registro["corrected_text_sha256"]
        )
        self.assertEqual(len(registro["raw_text_sha256"]), 64)

    def test_pagina_vazia_recebe_status_proprio(self) -> None:
        registro = cc.registro_de_pagina(
            bib="178691",
            source_identifier="per178691_1906_07890",
            page_number=2,
            bruto="   \n\n ",
        )
        self.assertEqual(registro["status"], "empty")

    def test_hash_do_bruto_bate_com_o_arquivo_de_origem(self) -> None:
        bruto = "Caixa de Conversão"
        registro = cc.registro_de_pagina(
            bib="178691",
            source_identifier="per178691_1906_07890",
            page_number=1,
            bruto=bruto,
        )
        self.assertEqual(registro["raw_text_sha256"], cc.sha256_texto(bruto))


class LeituraHumanaTests(unittest.TestCase):
    def test_md_da_edicao_traz_cabecalho_de_proveniencia(self) -> None:
        md = cc.markdown_da_edicao(
            jornal="o_paiz",
            source_identifier="per178691_1906_07890",
            data="1906-05-11",
            paginas=[(1, "primeira pagina"), (2, "segunda pagina")],
        )
        self.assertIn("per178691_1906_07890", md)
        self.assertIn("1906-05-11", md)
        self.assertIn(cc.PROTOCOLO, md)
        self.assertIn(cc.VERSAO, md)
        self.assertIn("## Página 1", md)
        self.assertIn("## Página 2", md)
        self.assertIn("primeira pagina", md)

    def test_md_declara_que_o_texto_e_ocr_corrigido_e_nao_a_pagina(self) -> None:
        md = cc.markdown_da_edicao(
            jornal="o_paiz",
            source_identifier="per178691_1906_07890",
            data="1906-05-11",
            paginas=[(1, "texto")],
        )
        self.assertIn("OCR", md)
        self.assertIn("substitui a imagem da página", md)


if __name__ == "__main__":
    unittest.main()
