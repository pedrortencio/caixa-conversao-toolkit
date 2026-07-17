from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from pipeline.scraper import censo


PDF = b"%PDF-1.4 conteudo sintetico do acervo" + b"x" * 64


class FakeTransporte:
    """Acervo em memória: (ano, numero) -> bytes; ausente = 404."""

    def __init__(self, acervo: dict[tuple[int, int], bytes]) -> None:
        self.acervo = acervo
        self.chamadas: list[tuple[int, int]] = []

    def obtem(
        self, bib: str, ano: int, numero: int, destino: Path
    ) -> censo.Resultado:
        self.chamadas.append((ano, numero))
        corpo = self.acervo.get((ano, numero))
        if corpo is None:
            return censo.Resultado(
                bib=bib, ano=ano, numero=numero, status="ausente",
                http_status=404, pdf_sha256=None, byte_count=None,
                caminho=None,
            )
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(corpo)
        return censo.Resultado(
            bib=bib, ano=ano, numero=numero, status="ok", http_status=200,
            pdf_sha256=hashlib.sha256(corpo).hexdigest(),
            byte_count=len(corpo), caminho=destino,
        )


class CensoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.destino = Path(self.temporary.name)

    def test_detecta_regime_anual_com_sucesso_em_numero_baixo(self) -> None:
        transporte = FakeTransporte({(1907, 3): PDF})
        regime, resultados = censo.detecta_regime(
            transporte, "103730", 1907, self.destino
        )
        self.assertEqual("anual", regime)
        self.assertEqual(6, len(resultados))
        self.assertEqual(
            {"ok"}, {r.status for r in resultados if r.numero == 3}
        )
        self.assertLessEqual(len(transporte.chamadas), 6)

    def test_detecta_regime_continuo_sem_sucesso_em_numeros_baixos(self) -> None:
        transporte = FakeTransporte({})
        regime, resultados = censo.detecta_regime(
            transporte, "178691", 1907, self.destino
        )
        self.assertEqual("continuo", regime)
        self.assertEqual(6, len(resultados))
        self.assertEqual({"ausente"}, {r.status for r in resultados})

    def test_inicio_continuo_desce_da_ancora_ate_a_parada(self) -> None:
        acervo = {(1906, n): PDF for n in (7815, 7816, 7817, 7818)}
        transporte = FakeTransporte(acervo)
        inicio, resultados = censo.inicio_continuo_1906(
            transporte, "178691", ancora=7819, destino_dir=self.destino,
            parada=5,
        )
        self.assertEqual(7815, inicio)
        numeros_ok = {r.numero for r in resultados if r.status == "ok"}
        self.assertEqual({7815, 7816, 7817, 7818}, numeros_ok)
        self.assertEqual((1906, 7810), transporte.chamadas[-1])

    def test_varre_ano_atravessa_buraco_e_para_apos_o_limite(self) -> None:
        acervo = {(1907, n): PDF for n in (1, 2, 3, 4, 5, 20, 21, 22)}
        transporte = FakeTransporte(acervo)
        resultados = list(
            censo.varre_ano(
                transporte, "103730", 1907, inicio=1, ja_sondados={},
                destino_dir=self.destino, cap=100, parada=20,
                sem_sucesso=50,
            )
        )
        numeros_ok = [r.numero for r in resultados if r.status == "ok"]
        self.assertEqual([1, 2, 3, 4, 5, 20, 21, 22], numeros_ok)
        self.assertEqual((1907, 42), transporte.chamadas[-1])

    def test_varre_ano_para_sem_nenhum_sucesso(self) -> None:
        transporte = FakeTransporte({})
        resultados = list(
            censo.varre_ano(
                transporte, "178691", 1908, inicio=100, ja_sondados={},
                destino_dir=self.destino, cap=600, parada=90,
                sem_sucesso=30,
            )
        )
        self.assertEqual(30, len(resultados))
        self.assertEqual({"ausente"}, {r.status for r in resultados})

    def test_varre_ano_pula_numeros_ja_sondados_sem_rede(self) -> None:
        acervo = {(1907, n): PDF for n in (3, 4)}
        transporte = FakeTransporte(acervo)
        resultados = list(
            censo.varre_ano(
                transporte, "103730", 1907, inicio=1,
                ja_sondados={1: "ok", 2: "ausente"},
                destino_dir=self.destino, cap=100, parada=10,
                sem_sucesso=50,
            )
        )
        numeros_chamados = [n for _, n in transporte.chamadas]
        self.assertNotIn(1, numeros_chamados)
        self.assertNotIn(2, numeros_chamados)
        self.assertEqual([3, 4], [r.numero for r in resultados if r.status == "ok"])
        self.assertEqual((1907, 14), transporte.chamadas[-1])

    def test_varre_ano_respeita_o_cap_absoluto(self) -> None:
        acervo = {(1909, n): PDF for n in range(1, 200)}
        transporte = FakeTransporte(acervo)
        resultados = list(
            censo.varre_ano(
                transporte, "103730", 1909, inicio=1, ja_sondados={},
                destino_dir=self.destino, cap=50, parada=90,
                sem_sucesso=200,
            )
        )
        self.assertEqual(50, len(resultados))
        self.assertEqual((1909, 50), transporte.chamadas[-1])

    def test_resultado_ok_grava_arquivo_com_nome_canonico(self) -> None:
        transporte = FakeTransporte({(1907, 8125): PDF})
        resultados = list(
            censo.varre_ano(
                transporte, "178691", 1907, inicio=8125, ja_sondados={},
                destino_dir=self.destino, cap=5, parada=2, sem_sucesso=5,
            )
        )
        sucesso = [r for r in resultados if r.status == "ok"][0]
        self.assertEqual(
            self.destino / "per178691_1907_08125.pdf", sucesso.caminho
        )
        self.assertTrue(sucesso.caminho.exists())
        self.assertEqual(
            hashlib.sha256(PDF).hexdigest(), sucesso.pdf_sha256
        )


if __name__ == "__main__":
    unittest.main()
