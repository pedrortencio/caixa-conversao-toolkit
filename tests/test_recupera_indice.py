from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfWriter

from pipeline.base import db as base_db
from pipeline.base import recupera_indice
from pipeline.scraper import censo


NOW = "2026-07-18T15:00:00+00:00"


def pdf_valido() -> bytes:
    escritor = PdfWriter()
    escritor.add_blank_page(width=612, height=792)
    import io

    saida = io.BytesIO()
    escritor.write(saida)
    corpo = saida.getvalue()
    if len(corpo) < 11 * 1024:
        corpo += b"\n%" + b"x" * (11 * 1024 - len(corpo))
    return corpo


def escreve_manifesto(caminho: Path, linhas: list[dict]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as saida:
        escritor = csv.DictWriter(
            saida, fieldnames=recupera_indice.CAMPOS_MANIFESTO
        )
        escritor.writeheader()
        for linha in linhas:
            escritor.writerow(linha)


def linha(numero: int, status: str) -> dict:
    return {
        "numero": numero,
        "status": status,
        "http_status": 200 if status in {"ok", "pdf_invalido"} else 404,
        "pdf_sha256": "",
        "byte_count": "",
        "page_count": "",
        "quando": NOW,
    }


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


class ContagensTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.raiz = Path(self.temporary.name)

    def test_conta_ausencias_soma_entre_manifestos(self) -> None:
        a = self.raiz / "varredura_178691_1907.csv"
        b = self.raiz / "recuperacao_178691_1907.csv"
        escreve_manifesto(a, [linha(5254, "ausente"), linha(8125, "ok")])
        escreve_manifesto(b, [linha(5254, "ausente"), linha(8200, "ausente")])
        self.assertEqual(
            {5254: 2, 8200: 1}, recupera_indice.conta_ausencias(a, b)
        )

    def test_conta_ausencias_ignora_manifesto_inexistente(self) -> None:
        a = self.raiz / "varredura_178691_1907.csv"
        escreve_manifesto(a, [linha(5254, "ausente")])
        self.assertEqual(
            {5254: 1},
            recupera_indice.conta_ausencias(
                a, self.raiz / "recuperacao_178691_1907.csv"
            ),
        )

    def test_numeros_ok_une_manifestos(self) -> None:
        a = self.raiz / "varredura_178691_1907.csv"
        b = self.raiz / "recuperacao_178691_1907.csv"
        escreve_manifesto(
            a, [linha(8125, "ok"), linha(8126, "pdf_invalido")]
        )
        escreve_manifesto(b, [linha(8127, "ok")])
        self.assertEqual({8125, 8127}, recupera_indice.numeros_ok(a, b))


class AlvosTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.dir_censo = Path(self.temporary.name)

    def test_alvos_excluem_ok_e_404_terminal_e_incluem_o_resto(self) -> None:
        escreve_manifesto(
            self.dir_censo / "varredura_178691_1907.csv",
            [
                linha(8125, "ok"),          # baixado: fora
                linha(5254, "ausente"),     # 1 observação: dentro
                linha(8300, "ausente"),     # 1ª de 2 observações
                linha(8301, "erro"),        # transitório: dentro
            ],
        )
        escreve_manifesto(
            self.dir_censo / "recuperacao_178691_1907.csv",
            [linha(8300, "ausente")],       # 2ª observação: terminal, fora
        )
        escreve_manifesto(
            self.dir_censo / "varredura_178691_1913.csv",
            [linha(10408, "pdf_invalido")],  # não é ok: dentro
        )
        indice = {
            (1907, 8125),
            (1907, 5254),
            (1907, 8300),
            (1907, 8301),
            (1907, 9999),  # nunca sondado: dentro
            (1913, 10408),
        }
        self.assertEqual(
            [(1907, 5254), (1907, 8301), (1907, 9999), (1913, 10408)],
            recupera_indice.alvos_bib(indice, "178691", self.dir_censo),
        )


class ExecutaRecuperacaoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.raiz = Path(self.temporary.name)
        self.dir_censo = self.raiz / "censo"
        self.raw_root = self.raiz / "raw_pdf"
        self.db = self.raiz / "base.db"
        self.dir_censo.mkdir(parents=True)
        with open(
            self.dir_censo / "indice_bndigital_178691.csv",
            "w", encoding="utf-8", newline="",
        ) as saida:
            saida.write(
                "ano,numero\n1907,5254\n1913,10408\n1913,10999\n"
            )
        escreve_manifesto(
            self.dir_censo / "varredura_178691_1907.csv",
            [linha(5254, "ausente")],
        )
        escreve_manifesto(
            self.dir_censo / "varredura_178691_1913.csv",
            [linha(10408, "pdf_invalido")],
        )

    def executa(self, transporte: FakeTransporte) -> None:
        recupera_indice.executa_recuperacao(
            db=self.db,
            raw_root=self.raw_root,
            dir_censo=self.dir_censo,
            bibs=("178691",),
            transporte=transporte,
        )

    def test_rodada_baixa_alvos_e_fecha_404_com_duas_observacoes(self) -> None:
        transporte = FakeTransporte({(1913, 10408): pdf_valido()})
        self.executa(transporte)

        # 5254 já tinha 1 observação da varredura: 1 sonda fecha o terminal.
        self.assertEqual(1, transporte.chamadas.count((1907, 5254)))
        # 10999 nunca fora sondado: 404 no passe 1 + re-sonda no passe 2.
        self.assertEqual(2, transporte.chamadas.count((1913, 10999)))
        # 10408 baixado com sucesso no passe 1.
        self.assertEqual(1, transporte.chamadas.count((1913, 10408)))

        conn = base_db.connect(self.db)
        self.addCleanup(conn.close)
        fetch = conn.execute(
            """
            SELECT f.result FROM current_object_fetches c
            JOIN object_fetches f ON f.id = c.fetch_id
            JOIN digital_objects o ON o.id = c.object_id
            WHERE o.source_identifier = 'per178691_1913_10408'
            """
        ).fetchone()
        self.assertEqual("ok", fetch["result"])
        protocolo = conn.execute(
            "SELECT stage, name, version FROM protocols "
            "WHERE name='indice_bndigital'"
        ).fetchone()
        self.assertEqual("inventory", protocolo["stage"])
        self.assertEqual("1.0.0", protocolo["version"])

    def test_rodada_repetida_nao_gera_sondagem_nova(self) -> None:
        transporte = FakeTransporte({(1913, 10408): pdf_valido()})
        self.executa(transporte)
        repeticao = FakeTransporte({})
        self.executa(repeticao)
        self.assertEqual([], repeticao.chamadas)


if __name__ == "__main__":
    unittest.main()
