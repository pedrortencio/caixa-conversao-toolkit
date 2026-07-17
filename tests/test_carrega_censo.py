from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfWriter

from pipeline.base import carrega_censo
from pipeline.base import db as base_db
from pipeline.scraper import censo


NOW = "2026-07-18T14:00:00+00:00"


def escreve_pdf(caminho: Path, paginas: int) -> tuple[str, int]:
    escritor = PdfWriter()
    for _ in range(paginas):
        escritor.add_blank_page(width=612, height=792)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "wb") as saida:
        escritor.write(saida)
    corpo = caminho.read_bytes()
    if len(corpo) < 11 * 1024:
        corpo += b"\n%" + b"x" * (11 * 1024 - len(corpo))
        caminho.write_bytes(corpo)
    return hashlib.sha256(corpo).hexdigest(), len(corpo)


class CargaCensoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.raiz = Path(self.temporary.name)
        self.conn = base_db.connect(self.raiz / "censo.db")
        self.addCleanup(self.conn.close)
        self.protocolos = carrega_censo.garante_protocolos(
            self.conn, commit="a" * 40, timestamp=NOW
        )
        self.newspaper_ids = carrega_censo.garante_cadastro(
            self.conn, timestamp=NOW
        )

    def resultado_ok(self, caminho: Path, sha: str, tamanho: int) -> censo.Resultado:
        return censo.Resultado(
            bib="178691", ano=1907, numero=8125, status="ok",
            http_status=200, pdf_sha256=sha, byte_count=tamanho,
            caminho=caminho,
        )

    def test_persiste_sucesso_materializa_tudo_em_uma_transacao(self) -> None:
        caminho = self.raiz / "178691" / "per178691_1907_08125.pdf"
        sha, tamanho = escreve_pdf(caminho, paginas=2)
        resultado = self.resultado_ok(caminho, sha, tamanho)

        carrega_censo.persiste_sucesso(
            self.conn,
            resultado=resultado,
            newspaper_id=self.newspaper_ids["178691"],
            protocolos=self.protocolos,
            timestamp=NOW,
        )
        carrega_censo.persiste_sucesso(
            self.conn,
            resultado=resultado,
            newspaper_id=self.newspaper_ids["178691"],
            protocolos=self.protocolos,
            timestamp=NOW,
        )

        contagens = {
            tabela: self.conn.execute(
                f"SELECT count(*) FROM {tabela}"
            ).fetchone()[0]
            for tabela in (
                "digital_objects",
                "object_fetches",
                "physical_pages",
                "identification_runs",
            )
        }
        self.assertEqual(
            {
                "digital_objects": 1,
                "object_fetches": 1,
                "physical_pages": 2,
                "identification_runs": 1,
            },
            contagens,
        )
        fetch = self.conn.execute(
            "SELECT result, http_status, page_count, response_sha256 "
            "FROM object_fetches"
        ).fetchone()
        self.assertEqual("ok", fetch["result"])
        self.assertEqual(200, fetch["http_status"])
        self.assertEqual(2, fetch["page_count"])
        self.assertEqual(sha, fetch["response_sha256"])
        self.assertEqual(
            2,
            self.conn.execute(
                """
                SELECT count(*) FROM current_page_assessments c
                JOIN page_assessments a ON a.id = c.assessment_id
                WHERE c.assessment_level='screening'
                  AND a.result='not_assessed'
                """
            ).fetchone()[0],
        )

    def test_pdf_ilegivel_registra_invalid_pdf_sem_paginas(self) -> None:
        caminho = self.raiz / "178691" / "per178691_1907_08126.pdf"
        caminho.parent.mkdir(parents=True, exist_ok=True)
        corpo = b"%PDF-1.4 lixo que o pypdf nao le" + b"x" * (12 * 1024)
        caminho.write_bytes(corpo)
        resultado = censo.Resultado(
            bib="178691", ano=1907, numero=8126, status="ok",
            http_status=200,
            pdf_sha256=hashlib.sha256(corpo).hexdigest(),
            byte_count=len(corpo), caminho=caminho,
        )

        carrega_censo.persiste_sucesso(
            self.conn,
            resultado=resultado,
            newspaper_id=self.newspaper_ids["178691"],
            protocolos=self.protocolos,
            timestamp=NOW,
        )

        fetch = self.conn.execute(
            "SELECT result, error_class FROM object_fetches"
        ).fetchone()
        self.assertEqual("invalid_pdf", fetch["result"])
        self.assertEqual("pypdf", fetch["error_class"])
        self.assertEqual(
            0,
            self.conn.execute(
                "SELECT count(*) FROM physical_pages"
            ).fetchone()[0],
        )

    def test_manifesto_acumula_e_devolve_sondados(self) -> None:
        manifesto = self.raiz / "varredura_178691_1907.csv"
        caminho = self.raiz / "178691" / "per178691_1907_08125.pdf"
        sha, tamanho = escreve_pdf(caminho, paginas=1)
        carrega_censo.registra_manifesto(
            manifesto, self.resultado_ok(caminho, sha, tamanho), page_count=1
        )
        carrega_censo.registra_manifesto(
            manifesto,
            censo.Resultado(
                bib="178691", ano=1907, numero=8200, status="ausente",
                http_status=404, pdf_sha256=None, byte_count=None,
                caminho=None,
            ),
            page_count=None,
        )

        sondados = carrega_censo.numeros_sondados(manifesto)
        self.assertEqual({8125: "ok", 8200: "ausente"}, sondados)

    def test_calendario_civil_completo_e_idempotente(self) -> None:
        primeiro = carrega_censo.garante_calendario(
            self.conn, self.newspaper_ids, timestamp=NOW
        )
        segundo = carrega_censo.garante_calendario(
            self.conn, self.newspaper_ids, timestamp=NOW
        )
        self.assertEqual(primeiro, segundo)
        self.assertEqual(
            3287,
            self.conn.execute(
                "SELECT count(*) FROM calendar_days WHERE newspaper_id=?",
                (self.newspaper_ids["178691"],),
            ).fetchone()[0],
        )

    def test_transporte_com_cache_nao_bate_na_rede_para_pdf_valido(self) -> None:
        caminho = self.raiz / "178691" / "per178691_1907_08125.pdf"
        sha, tamanho = escreve_pdf(caminho, paginas=1)

        class Explode:
            def obtem(self, bib, ano, numero, destino):
                raise AssertionError("não deveria tocar a rede")

        transporte = carrega_censo.TransporteComCache(Explode())
        resultado = transporte.obtem("178691", 1907, 8125, caminho)
        self.assertEqual("ok", resultado.status)
        self.assertEqual(sha, resultado.pdf_sha256)
        self.assertEqual(tamanho, resultado.byte_count)


if __name__ == "__main__":
    unittest.main()
