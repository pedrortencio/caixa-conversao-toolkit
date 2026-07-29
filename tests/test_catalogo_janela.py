"""Testes da janela de leitura e da conferência de citação.

O teste que sustenta todo o resto é `test_normalizacao_nao_diverge`: os
offsets de `regra_nome.encontra` são coordenadas do texto normalizado, e a
janela só aponta para o lugar certo do texto cru enquanto as duas
normalizações produzirem exatamente a mesma string.
"""

from __future__ import annotations

import glob
import unittest
from pathlib import Path

from pipeline.catalogo import janela as mod_janela
from pipeline.catalogo import verifica
from pipeline.triagem import regra_nome

REPO_ROOT = Path(__file__).resolve().parents[1]
TEXTO_EMBUTIDO = Path("C:/dados-caixa/texto_embutido")


class NormalizaComIndiceTests(unittest.TestCase):
    def test_normalizacao_nao_diverge(self) -> None:
        casos = [
            "A Caixa de Conversão",
            "caixa   de\n\n conver-\nsão do paiz",
            "  ESPAÇO nas bordas  ",
            "acentuação: ç, ã, é, ô, ü",
            "hífen-simples não some",
            "",
            "\n\n\t  \n",
        ]
        for texto in casos:
            with self.subTest(texto=texto[:30]):
                normalizado, indices = mod_janela.normaliza_com_indice(texto)
                self.assertEqual(normalizado, regra_nome.normaliza(texto))
                self.assertEqual(len(normalizado), len(indices))

    def test_indice_aponta_para_o_caractere_de_origem(self) -> None:
        texto = "xx Caixa de Conversão"
        normalizado, indices = mod_janela.normaliza_com_indice(texto)
        pos = normalizado.index("caixa")
        self.assertEqual(texto[indices[pos]], "C")

    def test_indice_sobrevive_a_hifenizacao_de_quebra(self) -> None:
        texto = "a caixa de conver-\n   sao seguiu"
        normalizado, indices = mod_janela.normaliza_com_indice(texto)
        pos = normalizado.index("caixa")
        self.assertEqual(texto[indices[pos]], "c")


class JanelasTests(unittest.TestCase):
    def test_pagina_sem_mencao_nao_gera_janela(self) -> None:
        self.assertEqual(mod_janela.janelas("nada aqui sobre bancos"), [])

    def test_janela_contem_a_mencao(self) -> None:
        texto = "x" * 500 + " a Caixa de Conversão emitiu " + "y" * 500
        (j,) = mod_janela.janelas(texto, largura=200)
        self.assertIn("Caixa de Conversão", j.texto)
        self.assertEqual(j.n_mencoes, 1)

    def test_janela_nao_estoura_os_limites_da_pagina(self) -> None:
        texto = "Caixa de Conversão no começo"
        (j,) = mod_janela.janelas(texto, largura=10_000)
        self.assertEqual(j.inicio, 0)
        self.assertEqual(j.fim, len(texto))

    def test_mencoes_proximas_sao_fundidas_numa_janela(self) -> None:
        texto = "Caixa de Conversão " + "z" * 50 + " caixa de conversao"
        janelas = mod_janela.janelas(texto, largura=400)
        self.assertEqual(len(janelas), 1)
        self.assertEqual(janelas[0].n_mencoes, 2)

    def test_mencoes_distantes_ficam_em_janelas_separadas(self) -> None:
        texto = "Caixa de Conversão " + "z" * 4000 + " caixa de conversao"
        janelas = mod_janela.janelas(texto, largura=200)
        self.assertEqual(len(janelas), 2)

    def test_texto_da_janela_e_recorte_cru_e_preserva_acento(self) -> None:
        texto = "prefixo. A Caixa de Conversão RECEBEU ouro."
        (j,) = mod_janela.janelas(texto, largura=1000)
        self.assertEqual(j.texto, texto[j.inicio:j.fim])
        self.assertIn("RECEBEU", j.texto)

    def test_id_da_janela_carrega_o_intervalo(self) -> None:
        texto = "Caixa de Conversão"
        (j,) = mod_janela.janelas(texto)
        self.assertEqual(
            mod_janela.janela_id("per178691_1906_07890", 3, j),
            f"per178691_1906_07890:p003:c{j.inicio}-{j.fim}",
        )


class NormalizaContraCorpusRealTests(unittest.TestCase):
    """A garantia só vale se sobreviver ao OCR sujo de verdade."""

    def test_paginas_reais_nao_divergem(self) -> None:
        if not TEXTO_EMBUTIDO.is_dir():
            self.skipTest("camada de texto indisponivel neste ambiente")
        caminhos = sorted(
            glob.glob(str(TEXTO_EMBUTIDO / "*" / "*" / "p001.txt"))
        )[:25]
        if not caminhos:
            self.skipTest("nenhuma pagina encontrada")
        for caminho in caminhos:
            texto = Path(caminho).read_text(encoding="utf-8", errors="replace")
            with self.subTest(pagina=Path(caminho).parent.name):
                normalizado, indices = mod_janela.normaliza_com_indice(texto)
                self.assertEqual(normalizado, regra_nome.normaliza(texto))
                self.assertEqual(len(normalizado), len(indices))


class ConfereCitacaoTests(unittest.TestCase):
    JANELA = "O Sr. David Campista declarou que jamais lhe tinha passado pela cabeça."

    def test_citacao_literal_e_aceita(self) -> None:
        v = verifica.confere_citacao("jamais lhe tinha passado pela cabeça", self.JANELA)
        self.assertTrue(v.aceita)

    def test_diferenca_de_acento_e_caixa_e_perdoada(self) -> None:
        v = verifica.confere_citacao("JAMAIS LHE TINHA PASSADO PELA CABECA", self.JANELA)
        self.assertTrue(v.aceita)

    def test_citacao_inventada_e_rejeitada(self) -> None:
        v = verifica.confere_citacao(
            "declarou que a Caixa seria um desastre para o paiz", self.JANELA
        )
        self.assertFalse(v.aceita)
        self.assertEqual(v.motivo, verifica.MOTIVO_AUSENTE)

    def test_citacao_curta_demais_e_rejeitada(self) -> None:
        v = verifica.confere_citacao("Campista", self.JANELA)
        self.assertFalse(v.aceita)
        self.assertEqual(v.motivo, verifica.MOTIVO_CURTA)

    def test_citacao_vazia_ou_nula_e_rejeitada(self) -> None:
        for valor in (None, "", "   "):
            with self.subTest(valor=valor):
                self.assertFalse(verifica.confere_citacao(valor, self.JANELA).aceita)


class ConfereRegistrosTests(unittest.TestCase):
    def setUp(self) -> None:
        self.janelas = {"j1": "a Caixa de Conversão recebeu ouro em deposito legal"}

    def test_separa_aceitos_de_rejeitados(self) -> None:
        registros = [
            {"janela_id": "j1", "citacao_verbatim": "recebeu ouro em deposito legal"},
            {"janela_id": "j1", "citacao_verbatim": "vendeu ouro ao Banco do Brasil"},
        ]
        aceitos, rejeitados = verifica.confere_registros(registros, self.janelas)
        self.assertEqual(len(aceitos), 1)
        self.assertEqual(len(rejeitados), 1)
        self.assertEqual(rejeitados[0]["motivo_rejeicao"], verifica.MOTIVO_AUSENTE)

    def test_janela_desconhecida_e_rejeitada(self) -> None:
        registros = [{"janela_id": "inexistente", "citacao_verbatim": "qualquer coisa"}]
        aceitos, rejeitados = verifica.confere_registros(registros, self.janelas)
        self.assertEqual(aceitos, [])
        self.assertEqual(rejeitados[0]["motivo_rejeicao"], "janela_desconhecida")

    def test_taxa_de_rejeicao(self) -> None:
        self.assertEqual(verifica.taxa_rejeicao([], []), 0.0)
        self.assertEqual(verifica.taxa_rejeicao([{}], [{}]), 0.5)


if __name__ == "__main__":
    unittest.main()
