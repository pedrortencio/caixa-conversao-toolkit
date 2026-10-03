"""Testes do sorteio e da apuração da inspeção da sonda difusa.

A sonda conta quantas páginas descartadas pelo censo trazem forma parecida com
"Caixa de Conversão". Esse número só vira medida de falso negativo depois que
alguém LÊ uma amostra e diz quantos daqueles achados são menção de verdade. O
módulo existe para que esse passo seja reprodutível: semente fixa, amostra
estratificada por distância, e intervalo de Wilson em vez de proporção nua.

O teste que sustenta o resto é `test_mesma_semente_mesma_amostra`. Sem ele, a
precisão medida não é reconferível e o número final é opinião.
"""

from __future__ import annotations

import unittest

from pipeline.triagem import inspeciona_sonda as ins


def linhas(quantidade: int, distancia: int = 1) -> list[dict]:
    return [
        {
            "bib": "178691",
            "source_identifier": f"obj{i:04d}",
            "page_number": i,
            "offset": 0,
            "distancia": distancia,
        }
        for i in range(quantidade)
    ]


class AmostraTests(unittest.TestCase):
    def test_mesma_semente_mesma_amostra(self) -> None:
        primeira = ins.amostra_determinista(linhas(200), 20, semente=20260812)
        segunda = ins.amostra_determinista(linhas(200), 20, semente=20260812)
        self.assertEqual(primeira, segunda)

    def test_semente_diferente_muda_a_amostra(self) -> None:
        primeira = ins.amostra_determinista(linhas(200), 20, semente=1)
        segunda = ins.amostra_determinista(linhas(200), 20, semente=2)
        self.assertNotEqual(primeira, segunda)

    def test_respeita_o_tamanho_pedido(self) -> None:
        self.assertEqual(len(ins.amostra_determinista(linhas(200), 20, 7)), 20)

    def test_populacao_menor_que_a_amostra_sai_inteira(self) -> None:
        self.assertEqual(len(ins.amostra_determinista(linhas(5), 20, 7)), 5)

    def test_a_amostra_sai_ordenada_para_leitura(self) -> None:
        amostra = ins.amostra_determinista(linhas(200), 20, 7)
        chaves = [
            (a["distancia"], a["bib"], a["source_identifier"], a["page_number"])
            for a in amostra
        ]
        self.assertEqual(chaves, sorted(chaves))

    def test_nao_depende_da_ordem_de_entrada(self) -> None:
        """Amostra sorteada sobre a mesma população, embaralhada, é a mesma."""
        populacao = linhas(200)
        primeira = ins.amostra_determinista(populacao, 20, 7)
        segunda = ins.amostra_determinista(list(reversed(populacao)), 20, 7)
        self.assertEqual(primeira, segunda)


class AmostraEstratificadaTests(unittest.TestCase):
    def populacao(self) -> list[dict]:
        return linhas(50, 1) + linhas(50, 2) + linhas(50, 3)

    def test_pega_a_cota_de_cada_estrato(self) -> None:
        amostra = ins.amostra_estratificada(self.populacao(), 10, semente=7)
        contagem: dict[int, int] = {}
        for linha in amostra:
            contagem[linha["distancia"]] = contagem.get(linha["distancia"], 0) + 1
        self.assertEqual(contagem, {1: 10, 2: 10, 3: 10})

    def test_estrato_pequeno_entra_inteiro_sem_estourar(self) -> None:
        populacao = linhas(50, 1) + linhas(3, 2)
        amostra = ins.amostra_estratificada(populacao, 10, semente=7)
        self.assertEqual(sum(1 for a in amostra if a["distancia"] == 2), 3)

    def test_deterministica(self) -> None:
        self.assertEqual(
            ins.amostra_estratificada(self.populacao(), 10, 7),
            ins.amostra_estratificada(self.populacao(), 10, 7),
        )


class WilsonTests(unittest.TestCase):
    def test_sem_acerto_o_piso_e_zero(self) -> None:
        baixo, alto = ins.wilson(0, 10)
        self.assertEqual(baixo, 0.0)
        self.assertGreater(alto, 0.0)

    def test_acerto_total_o_teto_e_um(self) -> None:
        baixo, alto = ins.wilson(10, 10)
        self.assertEqual(alto, 1.0)
        self.assertLess(baixo, 1.0)

    def test_intervalo_contem_a_proporcao(self) -> None:
        baixo, alto = ins.wilson(5, 10)
        self.assertLess(baixo, 0.5)
        self.assertGreater(alto, 0.5)

    def test_amostra_maior_aperta_o_intervalo(self) -> None:
        estreito = ins.wilson(500, 1000)
        largo = ins.wilson(5, 10)
        self.assertLess(estreito[1] - estreito[0], largo[1] - largo[0])

    def test_amostra_vazia_nao_afirma_nada(self) -> None:
        self.assertEqual(ins.wilson(0, 0), (0.0, 1.0))


class ApuracaoTests(unittest.TestCase):
    def julgadas(self) -> list[dict]:
        return [
            {"distancia": 1, "genuina": "1"},
            {"distancia": 1, "genuina": "1"},
            {"distancia": 1, "genuina": "0"},
            {"distancia": 3, "genuina": "1"},
            {"distancia": 3, "genuina": ""},  # não lida ainda
        ]

    def test_apura_por_estrato_e_ignora_o_nao_lido(self) -> None:
        apuracao = ins.apura(self.julgadas())
        self.assertEqual(apuracao["por_distancia"]["1"]["lidas"], 3)
        self.assertEqual(apuracao["por_distancia"]["1"]["genuinas"], 2)
        self.assertEqual(apuracao["por_distancia"]["3"]["lidas"], 1)
        self.assertEqual(apuracao["nao_lidas"], 1)

    def test_precisao_agregada_traz_intervalo(self) -> None:
        apuracao = ins.apura(self.julgadas())
        self.assertEqual(apuracao["total"]["lidas"], 4)
        self.assertEqual(apuracao["total"]["genuinas"], 3)
        baixo, alto = apuracao["total"]["ic95"]
        self.assertLess(baixo, 0.75)
        self.assertGreater(alto, 0.75)

    def test_rejeita_julgamento_fora_do_vocabulario(self) -> None:
        with self.assertRaises(ValueError):
            ins.apura([{"distancia": 1, "genuina": "talvez"}])


class BucketsTests(unittest.TestCase):
    def celula(self) -> dict:
        # cumulativo: d<=1 vale 10, d<=2 vale 25, d<=3 vale 30, e daí não sobe
        return {
            "bib": "178691",
            "jornal": "o_paiz",
            "ano": 1906,
            "hit_censo": 0,
            "paginas": 4000,
            "paginas_d0": 0,
            "paginas_d1": 10,
            "paginas_d2": 25,
            "paginas_d3": 30,
            "paginas_d4": 30,
        }

    def test_diferencia_o_cumulativo(self) -> None:
        self.assertEqual(
            ins.buckets_por_distancia(self.celula()), {0: 0, 1: 10, 2: 15, 3: 5, 4: 0}
        )

    def test_a_soma_dos_buckets_e_o_cumulativo_do_topo(self) -> None:
        buckets = ins.buckets_por_distancia(self.celula())
        self.assertEqual(sum(buckets.values()), self.celula()["paginas_d4"])


class EstimativaTests(unittest.TestCase):
    APURACAO = {
        "por_distancia": {
            "1": {"precisao": 1.0, "ic95": [0.9, 1.0]},
            "2": {"precisao": 0.5, "ic95": [0.3, 0.7]},
        }
    }

    def celulas(self) -> list[dict]:
        return [
            {
                "bib": "178691", "jornal": "o_paiz", "ano": 1906, "hit_censo": 0,
                "paginas": 1000, "paginas_d0": 0, "paginas_d1": 100,
                "paginas_d2": 300,
            }
        ]

    def test_pondera_cada_faixa_pela_sua_precisao(self) -> None:
        estimativa = ins.estima_falsos_negativos(self.celulas(), self.APURACAO, limiar=2)
        (celula,) = estimativa["celulas"]
        self.assertEqual(celula["paginas_sinalizadas"], 300)
        self.assertAlmostEqual(celula["paginas_estimadas"], 100 * 1.0 + 200 * 0.5)

    def test_o_limiar_corta_as_faixas_acima(self) -> None:
        estimativa = ins.estima_falsos_negativos(self.celulas(), self.APURACAO, limiar=1)
        (celula,) = estimativa["celulas"]
        self.assertEqual(celula["paginas_sinalizadas"], 100)
        self.assertAlmostEqual(celula["paginas_estimadas"], 100.0)

    def test_o_intervalo_vem_dos_limites_de_wilson_de_cada_faixa(self) -> None:
        estimativa = ins.estima_falsos_negativos(self.celulas(), self.APURACAO, limiar=2)
        (celula,) = estimativa["celulas"]
        self.assertAlmostEqual(celula["estimadas_ic95"][0], 100 * 0.9 + 200 * 0.3)
        self.assertAlmostEqual(celula["estimadas_ic95"][1], 100 * 1.0 + 200 * 0.7)

    def test_faixa_sem_precisao_lida_nao_e_chutada(self) -> None:
        """Faixa não inspecionada entra como desconhecida, não como zero nem um."""
        celulas = self.celulas()
        celulas[0]["paginas_d3"] = 350
        estimativa = ins.estima_falsos_negativos(celulas, self.APURACAO, limiar=3)
        self.assertEqual(estimativa["total"]["paginas_sem_precisao_medida"], 50)

    def test_ignora_o_braco_com_mencao(self) -> None:
        celulas = self.celulas() + [dict(self.celulas()[0], hit_censo=1)]
        estimativa = ins.estima_falsos_negativos(celulas, self.APURACAO, limiar=2)
        self.assertEqual(len(estimativa["celulas"]), 1)
        self.assertEqual(estimativa["total"]["paginas_sinalizadas"], 300)


if __name__ == "__main__":
    unittest.main()
