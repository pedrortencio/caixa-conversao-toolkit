"""Testes da retomada do piloto de catalogacao.

A corrida de 29/07 provou a necessidade: o anotador `claude` morreu na janela
25 de 48 e as 24 restantes falharam em sequencia. Sem retomada, a unica saida
seria rodar tudo de novo, o que descartaria 24 anotacoes boas e pagaria duas
vezes pelo mesmo trabalho.

Regras que estes testes fixam:

- so conta como feita a janela que tem registro com status `ok`; falha nao
  vira `pendente resolvido` por descuido;
- retomar NUNCA trunca o JSONL bruto, que e append-only e guarda tambem as
  tentativas fracassadas;
- os aceitos sao recomputados sobre o estado final de TODAS as janelas, as
  reaproveitadas e as novas, nunca so sobre as da rodada corrente;
- o numero de sequencia da janela e estavel, porque ele nomeia o manifesto e
  o registro de proveniencia do Codex.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pipeline.catalogo import roda_piloto

GABARITO = "catalogue {JANELA_ID} do {JORNAL} em {ANO}:\n{TEXTO}"

JANELAS = [
    {
        "janela_id": "j1",
        "jornal": "o_paiz",
        "ano": 1906,
        "texto": "a Caixa de Conversao recebeu ouro em deposito legal",
    },
    {
        "janela_id": "j2",
        "jornal": "gazeta_noticias",
        "ano": 1910,
        "texto": "o troco das notas da Caixa foi suspenso pelo governo",
    },
    {
        "janela_id": "j3",
        "jornal": "correio_manha",
        "ano": 1914,
        "texto": "a taxa de dezesseis dinheiros foi fixada em lei",
    },
]


def resposta_com(citacao: str) -> str:
    return json.dumps([{"citacao_verbatim": citacao, "debate": "d"}], ensure_ascii=False)


class AnotadorFalso:
    """Anotador injetavel: devolve resposta pronta ou levanta erro."""

    def __init__(self, por_janela: dict[str, str], quebra: set[str] | None = None):
        self.por_janela = por_janela
        self.quebra = quebra or set()
        self.chamadas: list[tuple[int, str]] = []

    def __call__(self, prompt: str, seq: int) -> tuple[str, dict]:
        alvo = next(j["janela_id"] for j in JANELAS if j["janela_id"] in prompt)
        self.chamadas.append((seq, alvo))
        if alvo in self.quebra:
            raise RuntimeError("anotador caiu")
        return self.por_janela[alvo], {"servico": "falso"}


class RetomadaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir_saida = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.respostas = {
            "j1": resposta_com("recebeu ouro em deposito legal"),
            "j2": resposta_com("troco das notas da Caixa foi suspenso"),
            "j3": resposta_com("taxa de dezesseis dinheiros foi fixada"),
        }

    def executa(self, chama, *, retomar: bool, janelas=None) -> dict:
        return roda_piloto.executa(
            janelas=janelas or JANELAS,
            gabarito=GABARITO,
            prompt_sha="sha",
            versao="cli-teste",
            anotador="teste",
            chama=chama,
            dir_saida=self.dir_saida,
            retomar=retomar,
        )

    def linhas(self, nome: str) -> list[dict]:
        caminho = self.dir_saida / nome
        if not caminho.exists():
            return []
        texto = caminho.read_text(encoding="utf-8")
        return [json.loads(l) for l in texto.splitlines() if l.strip()]

    def test_corrida_completa_chama_todas_as_janelas(self) -> None:
        anotador = AnotadorFalso(self.respostas)
        resumo = self.executa(anotador, retomar=False)
        self.assertEqual(len(anotador.chamadas), 3)
        self.assertEqual(resumo["aceitos"], 3)
        self.assertEqual(len(self.linhas("anotacoes_teste.jsonl")), 3)

    def test_retomar_pula_janela_ja_ok(self) -> None:
        self.executa(AnotadorFalso(self.respostas, quebra={"j2", "j3"}), retomar=False)
        segundo = AnotadorFalso(self.respostas)
        resumo = self.executa(segundo, retomar=True)
        self.assertEqual([alvo for _, alvo in segundo.chamadas], ["j2", "j3"])
        self.assertEqual(resumo["reaproveitadas"], 1)
        self.assertEqual(resumo["chamadas"], 2)

    def test_retomar_nao_trunca_o_bruto(self) -> None:
        self.executa(AnotadorFalso(self.respostas, quebra={"j3"}), retomar=False)
        self.executa(AnotadorFalso(self.respostas), retomar=True)
        linhas = self.linhas("anotacoes_teste.jsonl")
        self.assertEqual(len(linhas), 4)  # 3 da primeira corrida + 1 da retomada
        self.assertEqual([l["status"] for l in linhas], ["ok", "ok", "falha", "ok"])

    def test_aceitos_somam_reaproveitadas_e_novas(self) -> None:
        self.executa(AnotadorFalso(self.respostas, quebra={"j2", "j3"}), retomar=False)
        resumo = self.executa(AnotadorFalso(self.respostas), retomar=True)
        self.assertEqual(resumo["aceitos"], 3)
        aceitos = self.linhas("aceitos_teste.jsonl")
        self.assertEqual({a["janela_id"] for a in aceitos}, {"j1", "j2", "j3"})

    def test_sequencia_da_janela_e_estavel_na_retomada(self) -> None:
        self.executa(AnotadorFalso(self.respostas, quebra={"j3"}), retomar=False)
        segundo = AnotadorFalso(self.respostas)
        self.executa(segundo, retomar=True)
        self.assertEqual(segundo.chamadas, [(3, "j3")])

    def test_falha_de_uma_janela_nao_derruba_a_corrida(self) -> None:
        anotador = AnotadorFalso(self.respostas, quebra={"j2"})
        resumo = self.executa(anotador, retomar=False)
        self.assertEqual(resumo["falhas"], 1)
        self.assertEqual(resumo["aceitos"], 2)
        falha = [l for l in self.linhas("anotacoes_teste.jsonl") if l["status"] == "falha"]
        self.assertEqual(len(falha), 1)
        self.assertIn("anotador caiu", falha[0]["motivo"])

    def test_retomar_sem_arquivo_anterior_roda_tudo(self) -> None:
        anotador = AnotadorFalso(self.respostas)
        resumo = self.executa(anotador, retomar=True)
        self.assertEqual(resumo["chamadas"], 3)
        self.assertEqual(resumo["reaproveitadas"], 0)

    def test_citacao_ausente_da_janela_continua_rejeitada_na_retomada(self) -> None:
        self.executa(AnotadorFalso(self.respostas, quebra={"j2"}), retomar=False)
        inventada = dict(self.respostas)
        inventada["j2"] = resposta_com("a Caixa seria um desastre para o paiz")
        resumo = self.executa(AnotadorFalso(inventada), retomar=True)
        self.assertEqual(resumo["rejeitados"], 1)
        rejeitados = self.linhas("rejeitados_teste.jsonl")
        self.assertEqual(rejeitados[0]["motivo_rejeicao"], "citacao_ausente_da_janela")


class ExtraiJsonTests(unittest.TestCase):
    """O anotador as vezes comenta depois de responder.

    Caso real da retomada de 31/07 (janela 046, `per178691_1914_10818`): o
    array veio inteiro e correto, seguido de um paragrafo de prosa que citava
    `[]`. O extrator ia do primeiro colchete ao ULTIMO da resposta, engolia a
    prosa e derrubava a janela por `Extra data`. A anotacao estava certa e foi
    descartada por causa do parser.
    """

    REGISTRO = '[{"janela_id": "j1", "citacao_verbatim": "abc"}]'

    def test_array_puro(self) -> None:
        valor, motivo = roda_piloto.extrai_json(self.REGISTRO)
        self.assertEqual(motivo, "ok")
        self.assertEqual(len(valor), 1)

    def test_cerca_de_codigo(self) -> None:
        valor, motivo = roda_piloto.extrai_json(f"```json\n{self.REGISTRO}\n```")
        self.assertEqual(motivo, "ok")
        self.assertEqual(len(valor), 1)

    def test_prosa_depois_do_array_e_ignorada(self) -> None:
        resposta = (
            f"{self.REGISTRO}\n\n**Nota fora do JSON:** devolver `[]` aqui "
            "esconderia um falso positivo previsivel."
        )
        valor, motivo = roda_piloto.extrai_json(resposta)
        self.assertEqual(motivo, "ok")
        self.assertEqual(len(valor), 1)

    def test_preambulo_antes_do_array_e_ignorado(self) -> None:
        valor, motivo = roda_piloto.extrai_json(f"Segue a catalogacao:\n{self.REGISTRO}")
        self.assertEqual(motivo, "ok")
        self.assertEqual(len(valor), 1)

    def test_lista_vazia_e_resposta_valida(self) -> None:
        valor, motivo = roda_piloto.extrai_json("[]")
        self.assertEqual(motivo, "ok")
        self.assertEqual(valor, [])

    def test_resposta_sem_array(self) -> None:
        valor, motivo = roda_piloto.extrai_json("nao encontrei nada nesta janela")
        self.assertIsNone(valor)
        self.assertEqual(motivo, "sem_array_json")

    def test_json_realmente_quebrado_continua_falhando(self) -> None:
        valor, motivo = roda_piloto.extrai_json('[{"janela_id": "j1",]')
        self.assertIsNone(valor)
        self.assertTrue(motivo.startswith("json_invalido"))


class FeitasTests(unittest.TestCase):
    def test_so_conta_como_feita_a_janela_com_status_ok(self) -> None:
        linhas = [
            {"janela_id": "j1", "status": "ok", "registros": [{"a": 1}]},
            {"janela_id": "j2", "status": "falha", "registros": []},
        ]
        feitas = roda_piloto.indexa_feitas(linhas)
        self.assertEqual(set(feitas), {"j1"})

    def test_tentativa_mais_recente_vence(self) -> None:
        linhas = [
            {"janela_id": "j1", "status": "ok", "registros": [{"v": "antiga"}]},
            {"janela_id": "j1", "status": "ok", "registros": [{"v": "nova"}]},
        ]
        feitas = roda_piloto.indexa_feitas(linhas)
        self.assertEqual(feitas["j1"]["registros"], [{"v": "nova"}])


if __name__ == "__main__":
    unittest.main()
