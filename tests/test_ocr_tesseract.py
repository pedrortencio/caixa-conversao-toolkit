"""Testes da camada de texto por OCR próprio (Tesseract) sobre os scans da BN.

Três invariantes sustentam o resto, e todas as três são sobre não destruir o
que já existe:

`test_nunca_escreve_na_camada_da_bn` trava a separação de camadas. A camada
embutida da BN é a origem de tudo que já foi medido, incluindo o censo e o
portão de 1906. Uma camada nova que sobrescreva a antiga apaga a possibilidade
de comparar as duas, que é justamente o que decide se valeu a pena.

`test_falha_vira_linha_de_manifesto` trava a regra de ausência: página que o
motor não conseguiu ler é linha gravada com status próprio, nunca sumiço.

`test_registro_grava_a_identidade_do_motor` trava a proveniência. Motor,
versão exata do binário, `traineddata` e todos os parâmetros vão no manifesto,
porque uma camada de texto sem isso não é reproduzível e não é citável.
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from pipeline.transcricao import ocr_tesseract as ocr

TEM_TESSERACT = ocr.acha_binario() is not None
TEM_ACERVO = ocr.DIR_PDF.is_dir()


class ComandoTests(unittest.TestCase):
    def test_monta_o_comando_com_stdin_e_stdout(self) -> None:
        """Imagem entra por stdin e texto sai por stdout: nada toca o disco."""
        comando = ocr.comando(ocr.PARAMETROS_PADRAO, binario="tesseract")
        self.assertEqual(comando[:3], ["tesseract", "-", "-"])
        self.assertIn("--psm", comando)
        self.assertIn("3", comando)
        self.assertIn("-l", comando)
        self.assertIn("por", comando)

    def test_parametros_diferentes_produzem_comandos_diferentes(self) -> None:
        outro = ocr.Parametros(idioma="por", psm=4, oem=1, variante="fast")
        self.assertNotEqual(
            ocr.comando(ocr.PARAMETROS_PADRAO, binario="t"),
            ocr.comando(outro, binario="t"),
        )

    def test_a_variante_escolhe_o_tessdata(self) -> None:
        ambiente = ocr.ambiente(ocr.Parametros(idioma="por", psm=3, oem=1, variante="best"))
        self.assertTrue(ambiente["TESSDATA_PREFIX"].endswith("best"))


class CaminhosTests(unittest.TestCase):
    def test_espelha_o_layout_da_camada_embutida(self) -> None:
        destino = ocr.caminho_saida("178691", "per178691_1906_07890", 3)
        self.assertEqual(destino.name, "p003.txt")
        self.assertEqual(destino.parent.name, "per178691_1906_07890")

    def test_nunca_escreve_na_camada_da_bn(self) -> None:
        destino = ocr.caminho_saida("178691", "per178691_1906_07890", 3)
        bn = Path("C:/dados-caixa/texto_embutido/178691/per178691_1906_07890/p003.txt")
        self.assertNotEqual(destino, bn)
        self.assertNotIn("texto_embutido", str(destino))
        self.assertIn("texto_tesseract", str(destino))

    def test_o_pdf_e_procurado_pelo_identificador_do_objeto(self) -> None:
        caminho = ocr.caminho_pdf("178691", "per178691_1906_07890")
        self.assertTrue(str(caminho).endswith("per178691_1906_07890.pdf"))
        self.assertIn("178691", str(caminho))


class ResumeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(ocr.RAIZ) / "tests" / "_tmp_ocr"
        self.tmp.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_pagina_ausente_nao_conta_como_feita(self) -> None:
        self.assertFalse(ocr.ja_processada(self.tmp / "nao_existe.txt"))

    def test_pagina_vazia_nao_conta_como_feita(self) -> None:
        """Arquivo de tamanho zero é rodada interrompida, não página em branco."""
        vazio = self.tmp / "vazio.txt"
        vazio.write_text("", encoding="utf-8")
        self.assertFalse(ocr.ja_processada(vazio))

    def test_pagina_com_texto_conta_como_feita(self) -> None:
        feito = self.tmp / "feito.txt"
        feito.write_text("texto qualquer", encoding="utf-8")
        self.assertTrue(ocr.ja_processada(feito))


class RegistroTests(unittest.TestCase):
    BASE = dict(
        bib="178691",
        ano=1906,
        source_identifier="per178691_1906_07890",
        page_number=3,
    )

    def test_registro_grava_a_identidade_do_motor(self) -> None:
        registro = ocr.registro_de_pagina(
            **self.BASE,
            texto="a caixa de conversão recebeu ouro",
            parametros=ocr.PARAMETROS_PADRAO,
            motor={"engine": "tesseract", "version": "5.4.0", "leptonica": "1.84.1"},
            duracao_s=1.5,
        )
        self.assertEqual(registro["status"], "ok")
        self.assertEqual(registro["engine"], "tesseract")
        self.assertEqual(registro["engine_version"], "5.4.0")
        self.assertEqual(registro["psm"], 3)
        self.assertEqual(registro["oem"], 1)
        self.assertEqual(registro["idioma"], "por")
        self.assertEqual(registro["variante_tessdata"], "best")
        self.assertEqual(len(registro["text_sha256"]), 64)

    def test_falha_vira_linha_de_manifesto(self) -> None:
        registro = ocr.registro_de_pagina(
            **self.BASE,
            texto=None,
            parametros=ocr.PARAMETROS_PADRAO,
            motor={"engine": "tesseract", "version": "5.4.0"},
            duracao_s=0.0,
            erro="pdf sem imagem na pagina",
        )
        self.assertEqual(registro["status"], "falha")
        self.assertEqual(registro["erro"], "pdf sem imagem na pagina")
        self.assertIsNone(registro["text_sha256"])
        self.assertEqual(registro["char_count"], 0)

    def test_pagina_sem_texto_reconhecido_tem_status_proprio(self) -> None:
        registro = ocr.registro_de_pagina(
            **self.BASE,
            texto="   \n  ",
            parametros=ocr.PARAMETROS_PADRAO,
            motor={"engine": "tesseract", "version": "5.4.0"},
            duracao_s=1.0,
        )
        self.assertEqual(registro["status"], "vazio")


class MetricasTests(unittest.TestCase):
    def test_conta_token_sem_vogal(self) -> None:
        m = ocr.metricas_de_texto("caixa xhtq conversao lll")
        self.assertEqual(m["tokens"], 4)
        self.assertAlmostEqual(m["taxa_sem_vogal"], 0.5)

    def test_y_conta_como_vogal(self) -> None:
        """Era vogal na ortografia da época: Nictheroy, Bahya."""
        self.assertEqual(ocr.metricas_de_texto("Bahya")["taxa_sem_vogal"], 0.0)

    def test_texto_vazio_nao_divide_por_zero(self) -> None:
        m = ocr.metricas_de_texto("")
        self.assertEqual(m["tokens"], 0)
        self.assertIsNone(m["taxa_sem_vogal"])

    def test_compara_camadas_devolve_as_duas_pontas_e_a_diferenca(self) -> None:
        comparacao = ocr.compara_camadas("caixa xhtq", "caixa conversao")
        self.assertAlmostEqual(comparacao["bn"]["taxa_sem_vogal"], 0.5)
        self.assertAlmostEqual(comparacao["novo"]["taxa_sem_vogal"], 0.0)
        self.assertAlmostEqual(comparacao["delta_sem_vogal"], -0.5)


@unittest.skipUnless(TEM_TESSERACT, "tesseract não instalado")
class MotorTests(unittest.TestCase):
    def test_le_a_versao_exata_do_binario(self) -> None:
        motor = ocr.versao_do_motor()
        self.assertEqual(motor["engine"], "tesseract")
        self.assertRegex(motor["version"], r"^\d+\.\d+")

    def test_reconhece_texto_renderizado(self) -> None:
        """Contrato de invocação de ponta a ponta, sem depender do acervo."""
        imagem = ocr.imagem_de_teste("caixa de conversao")
        texto = ocr.roda_tesseract(imagem, ocr.PARAMETROS_PADRAO)
        self.assertIn("caixa", texto.lower())


@unittest.skipUnless(TEM_ACERVO, "acervo C:/dados-caixa ausente")
class ExtracaoTests(unittest.TestCase):
    def test_extrai_o_jpeg_embutido_sem_rasterizar(self) -> None:
        imagem = ocr.extrai_imagem("178691", "per178691_1906_07890", 3)
        self.assertEqual(imagem[:2], b"\xff\xd8")  # SOI de JPEG

    def test_pagina_fora_do_intervalo_levanta_erro_nomeado(self) -> None:
        with self.assertRaises(ocr.PaginaIndisponivel):
            ocr.extrai_imagem("178691", "per178691_1906_07890", 999)


if __name__ == "__main__":
    unittest.main()


class BracoTests(unittest.TestCase):
    TAREFAS = [
        {"bib": "178691", "ano": 1906, "hit_censo": 1},
        {"bib": "178691", "ano": 1906, "hit_censo": 0},
        {"bib": "089842", "ano": 1907, "hit_censo": 1},
    ]

    def test_com_mencao_e_o_braco_de_sensibilidade(self) -> None:
        self.assertEqual(len(ocr.filtra_braco(self.TAREFAS, "com_mencao")), 2)

    def test_sem_mencao_e_o_braco_de_recall(self) -> None:
        self.assertEqual(len(ocr.filtra_braco(self.TAREFAS, "sem_mencao")), 1)

    def test_todos_nao_recorta(self) -> None:
        self.assertEqual(len(ocr.filtra_braco(self.TAREFAS, "todos")), 3)


class EscalaTests(unittest.TestCase):
    def test_escala_1_devolve_os_bytes_intactos(self) -> None:
        """Sem ampliação não se reencoda: seria perda de JPEG sem ganho."""
        original = b"\xff\xd8bytes quaisquer"
        self.assertIs(ocr.prepara_imagem(original, 1.0), original)

    def test_ampliacao_dobra_as_dimensoes(self) -> None:
        import io

        from PIL import Image

        pequena = ocr.imagem_de_teste("caixa")
        antes = Image.open(io.BytesIO(pequena)).size
        depois = Image.open(io.BytesIO(ocr.prepara_imagem(pequena, 2))).size
        self.assertEqual(depois, (antes[0] * 2, antes[1] * 2))

    def test_a_escala_vai_para_o_manifesto(self) -> None:
        registro = ocr.registro_de_pagina(
            bib="178691", ano=1906, source_identifier="obj", page_number=1,
            texto="texto", parametros=ocr.Parametros("por", 3, 1, "best", 2.0),
            motor={"engine": "tesseract", "version": "5.4.0"}, duracao_s=1.0,
        )
        self.assertEqual(registro["escala"], 2.0)
        self.assertIn("escala", ocr.CAMPOS)
