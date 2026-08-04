"""Testes do documento de leitura do piloto de catalogacao.

O documento e para leitura humana, mas carrega duas garantias que nao podem
depender de conferencia visual:

- nenhuma citacao aparece no corpo sem ser substring literal da janela de
  origem, mesmo que um dia entre no gerador um arquivo de aceitos produzido
  por outra versao do conferidor;
- a concordancia entre anotadores e reportada como DETECCAO por janela, nunca
  como validacao. Um anotador que caiu no meio da corrida nao pode ser lido
  como anotador que nao encontrou nada, e por isso janela sem tentativa
  valida entra numa classe propria.
"""

from __future__ import annotations

import unittest

from pipeline.catalogo import relatorio_leitura as rel

JANELAS = [
    {
        "janela_id": "j1",
        "jornal": "o_paiz",
        "ano": 1906,
        "fase": "F1",
        "source_identifier": "per178691_1906_08005",
        "page_number": 4,
        "texto": "a Caixa de Conversao recebeu ouro em deposito legal do Tesouro",
    },
    {
        "janela_id": "j2",
        "jornal": "gazeta_noticias",
        "ano": 1914,
        "fase": "F4",
        "source_identifier": "per103730_1914_00140",
        "page_number": 6,
        "texto": "o troco das notas da Caixa foi suspenso por decreto do governo",
    },
]

ACEITOS = {
    "claude": [
        {
            "janela_id": "j1",
            "debate": "Deposito de ouro",
            "posicao_defendida": "O deposito garante a conversibilidade.",
            "voz": "editorial_do_jornal",
            "objeto_politica": ["lastro"],
            "direcao_por_objeto": [{"objeto": "lastro", "direcao": "valorizacao"}],
            "citacao_verbatim": "recebeu ouro em deposito legal",
        }
    ],
    "codex": [
        {
            "janela_id": "j2",
            "debate": "Suspensao do troco",
            "posicao_defendida": "O decreto suspende a conversibilidade.",
            "voz": "documento_oficial",
            "objeto_politica": ["conversibilidade"],
            "direcao_por_objeto": [
                {"objeto": "conversibilidade", "direcao": "nao_classificavel"}
            ],
            "citacao_verbatim": "troco das notas da Caixa foi suspenso",
        }
    ],
}

ANOTACOES = {
    "claude": [
        {"janela_id": "j1", "status": "ok", "registros": [{}], "segundos": 10.0},
        {"janela_id": "j2", "status": "falha", "registros": [], "segundos": 2.0},
    ],
    "codex": [
        {"janela_id": "j1", "status": "ok", "registros": [], "segundos": 20.0},
        {"janela_id": "j2", "status": "ok", "registros": [{}], "segundos": 30.0},
    ],
}


class CoberturaTests(unittest.TestCase):
    def test_conta_ok_e_falha_por_anotador(self) -> None:
        cob = rel.cobertura(ANOTACOES["claude"])
        self.assertEqual(cob["ok"], 1)
        self.assertEqual(cob["falha"], 1)

    def test_tentativa_ok_posterior_substitui_falha(self) -> None:
        linhas = [
            {"janela_id": "j1", "status": "falha", "registros": [], "segundos": 2.0},
            {"janela_id": "j1", "status": "ok", "registros": [{}], "segundos": 9.0},
        ]
        self.assertEqual(rel.cobertura(linhas), {"ok": 1, "falha": 0, "janelas": 1})


class DeteccaoTests(unittest.TestCase):
    def test_classifica_janela_por_quem_catalogou(self) -> None:
        classes = rel.deteccao(JANELAS, ACEITOS, ANOTACOES)
        self.assertEqual(classes["j1"], "so_claude")
        self.assertEqual(classes["j2"], "so_codex")

    def test_janela_sem_tentativa_valida_nao_vira_ausencia(self) -> None:
        anotacoes = {
            "claude": [{"janela_id": "j1", "status": "falha", "registros": []}],
            "codex": [{"janela_id": "j1", "status": "ok", "registros": []}],
        }
        classes = rel.deteccao(JANELAS[:1], {"claude": [], "codex": []}, anotacoes)
        self.assertEqual(classes["j1"], "sem_par")

    def test_nenhum_dos_dois_encontrou_e_classe_propria(self) -> None:
        anotacoes = {
            "claude": [{"janela_id": "j1", "status": "ok", "registros": []}],
            "codex": [{"janela_id": "j1", "status": "ok", "registros": []}],
        }
        classes = rel.deteccao(JANELAS[:1], {"claude": [], "codex": []}, anotacoes)
        self.assertEqual(classes["j1"], "nenhum")

    def test_ambos_catalogaram(self) -> None:
        aceitos = {
            "claude": ACEITOS["claude"],
            "codex": [{**ACEITOS["claude"][0], "debate": "outro corte"}],
        }
        classes = rel.deteccao(JANELAS[:1], aceitos, ANOTACOES)
        self.assertEqual(classes["j1"], "ambos")


class RenderizaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.texto = rel.renderiza(
            janelas=JANELAS,
            aceitos=ACEITOS,
            rejeitados={"claude": [], "codex": []},
            anotacoes=ANOTACOES,
            meta={"prompt_sha": "sha", "prompt": "p.md", "quando": "2026-07-31"},
        )

    def test_traz_as_duas_janelas_e_as_duas_citacoes(self) -> None:
        self.assertIn("recebeu ouro em deposito legal", self.texto)
        self.assertIn("troco das notas da Caixa foi suspenso", self.texto)

    def test_nao_usa_travessao(self) -> None:
        self.assertNotIn("—", self.texto)
        self.assertNotIn("–", self.texto)

    def test_virgula_decimal_nao_contamina_a_versao_da_cli(self) -> None:
        anotacoes = {
            "claude": [
                {
                    "janela_id": "j1",
                    "status": "ok",
                    "registros": [{}],
                    "versao_cli": "2.1.220 (Claude Code)",
                }
            ],
            "codex": [],
        }
        texto = rel.renderiza(
            janelas=JANELAS,
            aceitos=ACEITOS,
            rejeitados={"claude": [], "codex": []},
            anotacoes=anotacoes,
            meta={"prompt_sha": "sha", "prompt": "p.md", "quando": "2026-07-31"},
        )
        self.assertIn("2.1.220 (Claude Code)", texto)
        self.assertNotIn("2,1,220", texto)

    def test_taxa_de_rejeicao_sai_com_virgula_decimal(self) -> None:
        texto = rel.renderiza(
            janelas=JANELAS,
            aceitos={"claude": ACEITOS["claude"], "codex": []},
            rejeitados={"claude": [{"janela_id": "j1", "motivo_rejeicao": "citacao_vazia"}], "codex": []},
            anotacoes=ANOTACOES,
            meta={"prompt_sha": "sha", "prompt": "p.md", "quando": "2026-07-31"},
        )
        self.assertIn("50,0%", texto)

    def test_registra_a_queda_do_anotador_como_queda(self) -> None:
        self.assertIn("falha", self.texto.lower())

    def test_toda_citacao_do_corpo_existe_na_janela(self) -> None:
        divergentes = rel.confere_citacoes_do_corpo(JANELAS, ACEITOS)
        self.assertEqual(divergentes, [])

    def test_citacao_que_nao_casa_e_denunciada_e_nao_renderizada(self) -> None:
        aceitos = {
            "claude": [
                {**ACEITOS["claude"][0], "citacao_verbatim": "frase que nunca existiu na pagina"}
            ],
            "codex": [],
        }
        self.assertEqual(len(rel.confere_citacoes_do_corpo(JANELAS, aceitos)), 1)
        texto = rel.renderiza(
            janelas=JANELAS,
            aceitos=aceitos,
            rejeitados={"claude": [], "codex": []},
            anotacoes=ANOTACOES,
            meta={"prompt_sha": "sha", "prompt": "p.md", "quando": "2026-07-31"},
        )
        self.assertNotIn("frase que nunca existiu na pagina", texto)


if __name__ == "__main__":
    unittest.main()
