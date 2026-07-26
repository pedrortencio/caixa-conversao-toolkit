"""Testes da limpeza determinística da amostra (`pipeline/triagem/limpa_amostra.py`).

Cobrem os dois bugs achados na revisão da rotulagem de registro
(`docs/relatorio-rotulagem-registro.md`, 2026-07-23):

  - bug 1: meta-comentário da visão ("não há menção à Caixa de Conversão neste
    item") passava como `keep`, porque o próprio disclaimer nomeia a Caixa e a
    regra de nome casava com ele;
  - bug 2: `data` guardava ora data ISO, ora o ano nu, então contagem que
    parseia a coluna perde linha em silêncio.

Os trechos de disclaimer são citações literais da amostra real
(`dados/triagem/amostra_para_rotular.csv`).
"""

from __future__ import annotations

import unittest

from pipeline.triagem import limpa_amostra

# Variantes de redação do disclaimer, literais da amostra. Todas nomeiam a
# Caixa dentro da própria negação, que é o motivo do vazamento.
DISCLAIMERS = [
    "não menciona Caixa de Conversão - descartado",
    "não menciona a Caixa de Conversão diretamente - ignorar",
    "(não menciona diretamente — verificado sem menção explícita a Caixa de "
    "Conversão nesta nota)",
    "(sem menção direta à Caixa de Conversão nesta nota, incluída apenas por "
    "proximidade)",
    "(tabela sem menção direta explícita à Caixa de Conversão nesta parte "
    "transcrita, incluída por contiguidade com item vizinho já marcado)",
    "não aplicável - este item não menciona a Caixa de Conversão diretamente, "
    "mas foi incluído por proximidade; deve ser desconsiderado",
    "não há menção explícita à Caixa de Conversão neste trecho",
    "não há menção à Caixa de Conversão neste artigo",
    "não há Caixa de Conversão mencionada neste item",
]


def _linha(trecho: str, texto: str = "", **campos) -> dict:
    """Linha da amostra com os campos que `classifica` lê."""
    base = {
        "forma": "noticia",
        "trecho_caixa": trecho,
        "texto": texto or ("A Caixa de Conversão recebeu ontem o movimento "
                           "de câmbio da praça, conforme o boletim. " * 6),
        "continua": "0",
    }
    base.update(campos)
    return base


class DisclaimerTests(unittest.TestCase):
    """Bug 1: o meta-comentário da visão não é peça, é ausência de peça."""

    def test_variantes_de_disclaimer_sao_descartadas(self) -> None:
        for trecho in DISCLAIMERS:
            with self.subTest(trecho=trecho[:40]):
                self.assertEqual(
                    limpa_amostra.classifica(_linha(trecho)),
                    "drop_disclaimer",
                )

    def test_negacao_do_jornal_nao_e_disclaimer(self) -> None:
        """A peça de época nega o argumento, não a existência da menção.

        Descartar aqui seria cortar justamente o trecho polêmico, que é o
        material de maior valor para a medida de posição.
        """
        genuinos = [
            "Não há dúvida de que a Caixa de Conversão beneficia a lavoura.",
            "Sem menção ao interesse dos importadores, o governo não existe "
            "para a praça; a Caixa de Conversão o comprova.",
            "Não consta dos anais que a Caixa de Conversão tenha falhado.",
        ]
        for trecho in genuinos:
            with self.subTest(trecho=trecho[:40]):
                self.assertEqual(limpa_amostra.classifica(_linha(trecho)), "keep")

    def test_negacao_sem_nome_em_lugar_nenhum_nao_sobrevive_por_continuacao(
        self,
    ) -> None:
        """Peça que continua, sem o nome no texto, e cuja visão diz não ter
        achado a menção: não sobra evidência positiva nenhuma.

        A regra de continuação existe para não perder peça partida em coluna,
        e pressupõe que o nome esteja do outro lado. Aqui a visão declara a
        ausência e a regra de nome não acha nada em 3.800 caracteres, então a
        continuação não é motivo para manter (caso real
        `per178691_1910_09522:p002:i1`).
        """
        linha = _linha(
            "(sem menção diretamente aqui — verificado dentro do texto do "
            "editorial republicano)",
            texto="Ao marechal Hermes da Fonseca, futuro presidente da "
                  "Republica, confiaram os republicanos brazileiros os "
                  "destinos da Patria. " * 8,
            forma="editorial",
            continua="1",
        )
        self.assertEqual(limpa_amostra.classifica(linha), "drop_disclaimer")

    def test_continuacao_sem_marca_de_negacao_segue_keep(self) -> None:
        """Guarda da regra de continuação: sem marca de ausência, a peça
        partida em coluna continua valendo, mesmo sem o nome neste pedaço."""
        linha = _linha(
            "o movimento de ontem na praça, segue na coluna ao lado",
            texto="O movimento de ontem na praça foi de 12 mil contos. " * 8,
            continua="1",
        )
        self.assertEqual(limpa_amostra.classifica(linha), "keep")


class ResolveDataTests(unittest.TestCase):
    """Bug 2: `source_year` é a chave de ano; `data` só vale onde é data.

    A coluna guardava ora data ISO completa, ora o ano nu, e quem parseava a
    coluna como data perdia 25 linhas em silêncio, 18 delas em 1910, que é o
    ano mais atípico da série. O ano nunca se perde: está em `source_year`.
    """

    def _linha_data(self, data: str = "", ano: str = "1910") -> dict:
        return {
            "source_identifier": f"per178691_{ano}_09522",
            "source_year": ano,
            "data": data,
            "data_fonte": "visao",
        }

    def test_sem_data_resolvida_a_coluna_fica_vazia(self) -> None:
        linha = self._linha_data(data="quinta-feira, sem data legivel")
        limpa_amostra.resolve_data(linha, masthead={})
        self.assertEqual(linha["data"], "")
        self.assertEqual(linha["data_fonte"], "ano_apenas")
        self.assertEqual(linha["data_confiavel"], 0)

    def test_masthead_resolve_a_data_e_marca_confiavel(self) -> None:
        linha = self._linha_data(data="ilegivel")
        limpa_amostra.resolve_data(
            linha, masthead={"per178691_1910_09522": "1910-03-14"}
        )
        self.assertEqual(linha["data"], "1910-03-14")
        self.assertEqual(linha["data_fonte"], "masthead_pag1_ano")
        self.assertEqual(linha["data_confiavel"], 1)

    def test_data_da_visao_consistente_com_o_ano_e_mantida(self) -> None:
        linha = self._linha_data(data="14 de março de 1910")
        limpa_amostra.resolve_data(linha, masthead={})
        self.assertEqual(linha["data"], "1910-03-14")
        self.assertEqual(linha["data_confiavel"], 1)


class DivergenciaDeAnoTests(unittest.TestCase):
    """Bug 2, segunda metade: a divergência entre a data resolvida e o
    `source_year` é registro positivo, não silêncio.

    A tolerância de um ano em `resolve_data` existe porque edição de virada de
    ano cai na pasta errada do acervo. Ela é defensável, mas move o item de
    balde na contagem por ano, então precisa ser contada e publicada.
    """

    def test_conta_divergencia_entre_data_confiavel_e_source_year(self) -> None:
        linhas = [
            {"source_year": "1912", "data": "1913-01-18", "data_confiavel": 1},
            {"source_year": "1912", "data": "1912-05-03", "data_confiavel": 1},
            {"source_year": "1910", "data": "", "data_confiavel": 0},
        ]
        self.assertEqual(limpa_amostra.conta_ano_divergente(linhas), 1)


if __name__ == "__main__":
    unittest.main()
