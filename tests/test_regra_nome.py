"""Testes da regra de casamento por nome (função pura, sem I/O).

Corner cases do design (docs/superpowers/specs/2026-07-20-triagem-nome-pivo-
design.md) e formas reais observadas no OCR dos positivos do gabarito 1906
(scratchpad/scan_ruido.py): conector corrompido/mesclado (deconversao, dc,
do), truncamento por quebra de coluna (conver-) e falsos amigos frequentes
(caixa de correio, caixa de amortização).
"""

from __future__ import annotations

import unittest

from pipeline.triagem import regra_nome


class NormalizaTests(unittest.TestCase):
    def test_remove_acento_cedilha_e_caixa_alta(self) -> None:
        self.assertEqual(
            "caixa de conversao",
            regra_nome.normaliza("Caixa de Conversão"),
        )

    def test_colapsa_espaco_multiplo_e_tab(self) -> None:
        self.assertEqual(
            "caixa de conversao",
            regra_nome.normaliza("Caixa  de\tConversão"),
        )

    def test_rejunta_hifenizacao_de_quebra(self) -> None:
        self.assertEqual(
            "caixa de conversao",
            regra_nome.normaliza("caixa de conver-\nsão"),
        )

    def test_idempotente(self) -> None:
        uma = regra_nome.normaliza("Caixa  de Conver-\nsão")
        self.assertEqual(uma, regra_nome.normaliza(uma))


class EncontraTests(unittest.TestCase):
    def _casou(self, texto: str) -> bool:
        return len(regra_nome.encontra(texto)) > 0

    # --- deve casar ---
    def test_casamento_direto(self) -> None:
        self.assertTrue(self._casou("Sobre a Caixa de Conversão hoje."))

    def test_caixa_alta_e_baixa(self) -> None:
        self.assertTrue(self._casou("CAIXA DE CONVERSÃO"))
        self.assertTrue(self._casou("caixa de conversao"))

    def test_acento_e_cedilha_caidos(self) -> None:
        self.assertTrue(self._casou("a caixa de conversao do governo"))

    def test_conector_mesclado_sem_espaco(self) -> None:
        # forma real dominante: "caixa deconversao"
        self.assertTrue(self._casou("hoje 15 d. na caixa deconversao, recebe"))

    def test_conector_corrompido_dc(self) -> None:
        self.assertTrue(self._casou("allluido para a caixa dc conversao, que"))

    def test_conector_corrompido_do(self) -> None:
        self.assertTrue(self._casou("a caixa do conversao desempenha a mesma"))

    def test_truncado_por_quebra_de_coluna(self) -> None:
        # "conver" truncado no fim da coluna ainda é sinal do nome
        self.assertTrue(self._casou("a creacao da caixa de conver"))

    def test_hifenizacao_entre_conver_e_sao(self) -> None:
        self.assertTrue(self._casou("da caixa de conver-\nsão para fixar"))

    def test_espaco_e_quebra_entre_tokens(self) -> None:
        self.assertTrue(self._casou("Caixa de\n   Conversão"))

    def test_artigo_colado_antes_de_caixa(self) -> None:
        # "acaixa dc conversao" (artigo mesclado): 'caixa' aparece como
        # subsequência e deve casar mesmo assim
        self.assertTrue(self._casou("para acaixa dc conversao que a esta hora"))

    # --- NÃO deve casar (falsos amigos) ---
    def test_rejeita_amortizacao(self) -> None:
        self.assertFalse(self._casou("a Caixa de Amortização resgatou títulos"))

    def test_rejeita_caixa_de_correio(self) -> None:
        # falso amigo empírico mais frequente
        self.assertFalse(self._casou("deixou na caixa de correio a carta"))

    def test_rejeita_caixa_de_socorros(self) -> None:
        self.assertFalse(self._casou("a caixa de socorros dos operarios"))

    def test_rejeita_conversao_isolada(self) -> None:
        # 'conversão' sem 'caixa' adjacente não é o nome da instituição
        self.assertFalse(self._casou("a conversao da divida externa em ouro"))

    def test_rejeita_caixa_isolada(self) -> None:
        self.assertFalse(self._casou("guardou o dinheiro na caixa do escritorio"))

    def test_rejeita_caixa_economica(self) -> None:
        self.assertFalse(self._casou("depositou na Caixa Econômica Federal"))

    def test_rejeita_familia_conv_nao_conver(self) -> None:
        # convenio/convite/convidados/convem começam conv+[ei], nunca conver
        self.assertFalse(self._casou("a caixa de convites para a festa"))

    # --- contagem e spans ---
    def test_conta_multiplos_matches(self) -> None:
        texto = "A Caixa de Conversão e, depois, a caixa de conversao de novo."
        spans = regra_nome.encontra(texto)
        self.assertEqual(2, len(spans))

    def test_span_traz_offset_texto_e_contexto(self) -> None:
        spans = regra_nome.encontra("prefixo. Caixa de Conversão sufixo.")
        self.assertEqual(1, len(spans))
        span = spans[0]
        self.assertIsInstance(span.offset, int)
        self.assertIn("caixa de conver", span.texto)
        self.assertIn("caixa de conver", span.contexto)

    def test_texto_vazio_nao_casa(self) -> None:
        self.assertEqual([], regra_nome.encontra(""))


class ProtocoloTests(unittest.TestCase):
    def test_regra_versao_pinada(self) -> None:
        self.assertEqual("nome-caixa-conversao", regra_nome.PROTOCOL_NAME)
        self.assertEqual("1.0.0", regra_nome.PROTOCOL_VERSION)
        self.assertEqual(
            "triagem/nome-caixa-conversao 1.0.0", regra_nome.REGRA_VERSAO
        )


if __name__ == "__main__":
    unittest.main()
