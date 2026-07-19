from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from pipeline.base import db, extrai_texto


def _pdf_minimo(paginas: list[str | None]) -> bytes:
    """PDF válido mínimo; cada item vira uma página (None = sem texto)."""
    n_pag = len(paginas)
    font_num = 3 + 2 * n_pag
    kids = " ".join(f"{3 + 2 * i} 0 R" for i in range(n_pag))
    objetos: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {n_pag} >>".encode(),
    ]
    for i, texto in enumerate(paginas):
        content_num = 4 + 2 * i
        objetos.append(
            (
                "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 {font_num} 0 R >> >> "
                f"/Contents {content_num} 0 R >>"
            ).encode()
        )
        stream = (
            b""
            if texto is None
            else f"BT /F1 12 Tf 72 720 Td ({texto}) Tj ET".encode()
        )
        objetos.append(
            b"<< /Length "
            + str(len(stream)).encode()
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
    objetos.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    saida = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for num, corpo in enumerate(objetos, start=1):
        offsets.append(len(saida))
        saida += f"{num} 0 obj\n".encode() + corpo + b"\nendobj\n"
    inicio_xref = len(saida)
    total = len(objetos) + 1
    saida += f"xref\n0 {total}\n".encode()
    saida += b"0000000000 65535 f \n"
    for offset in offsets:
        saida += f"{offset:010d} 00000 n \n".encode()
    saida += (
        f"trailer\n<< /Size {total} /Root 1 0 R >>\n"
        f"startxref\n{inicio_xref}\n%%EOF\n"
    ).encode()
    return bytes(saida)


class ExtraiTextoTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.raiz_texto = self.tmp / "texto_embutido"
        self.pdf_dir = self.tmp / "raw_pdf"
        self.pdf_dir.mkdir()
        self.conn = db.connect(self.tmp / "base.db")
        self.addCleanup(self.conn.close)
        self.newspaper_id = db.upsert_newspaper(
            self.conn,
            slug="o_paiz",
            title="O Paiz",
            bn_bib="178691",
            city="Rio de Janeiro",
        )
        self.inventory_protocol = db.upsert_protocol(
            self.conn,
            stage="inventory",
            name="teste",
            version="1",
            executor_type="deterministic",
            code_commit="abc",
            parameters={},
        )
        self.conn.commit()

    def _cria_objeto(
        self, numero: str, pdf_bytes: bytes, paginas: int
    ) -> int:
        source_identifier = f"per178691_1906_{numero}"
        pdf_path = self.pdf_dir / f"{source_identifier}.pdf"
        pdf_path.write_bytes(pdf_bytes)
        object_id = db.upsert_digital_object(
            self.conn,
            newspaper_id=self.newspaper_id,
            source_identifier=source_identifier,
            source_url=f"https://example.test/{source_identifier}.pdf",
            source_year=1906,
            bn_file_key=f"178691/{source_identifier}.pdf",
            bn_file_number_literal=numero,
            discovered_by_protocol_id=self.inventory_protocol,
        )
        timestamp = db.utc_now()
        db.mark_download_status(
            self.conn,
            object_id=object_id,
            result="ok",
            attempted_at=timestamp,
            completed_at=timestamp,
            http_status=200,
            storage_path=str(pdf_path),
            pdf_sha256=hashlib.sha256(pdf_bytes).hexdigest(),
            byte_count=len(pdf_bytes),
            page_count=paginas,
        )
        for page_number in range(1, paginas + 1):
            self.conn.execute(
                """
                INSERT INTO physical_pages(
                    object_id, page_number, created_at
                ) VALUES (?, ?, ?)
                """,
                (object_id, page_number, timestamp),
            )
        self.conn.commit()
        return object_id

    def _vigentes(self) -> list[sqlite3.Row]:
        return db.rows(
            self.conn,
            """
            SELECT * FROM v_current_page_texts
            ORDER BY object_id, page_number
            """,
        )

    def test_extrai_celula_grava_arquivos_registros_e_vigencia(self) -> None:
        self._cria_objeto(
            "00001", _pdf_minimo(["CAIXA DE CONVERSAO", None]), 2
        )

        stats = extrai_texto.extrai_celula(
            self.conn, bib="178691", ano=1906, raiz_texto=self.raiz_texto
        )

        self.assertEqual(2, stats.pages_submitted)
        self.assertEqual(1, stats.ok)
        self.assertEqual(1, stats.empty)
        self.assertEqual(0, stats.error)

        vigentes = self._vigentes()
        self.assertEqual(2, len(vigentes))
        pagina1, pagina2 = vigentes

        self.assertEqual("ok", pagina1["result_status"])
        self.assertGreater(pagina1["char_count"], 0)
        arquivo = Path(pagina1["text_path"])
        self.assertTrue(arquivo.is_file())
        self.assertEqual(
            hashlib.sha256(arquivo.read_bytes()).hexdigest(),
            pagina1["text_sha256"],
        )
        self.assertIn("CAIXA DE CONVERSAO", arquivo.read_text("utf-8"))
        self.assertEqual(
            self.raiz_texto
            / "178691"
            / "per178691_1906_00001"
            / "p001.txt",
            arquivo,
        )

        self.assertEqual("empty", pagina2["result_status"])
        self.assertEqual(0, pagina2["char_count"])
        self.assertIsNone(pagina2["text_path"])

        run = db.rows(self.conn, "SELECT * FROM text_extraction_runs")[0]
        self.assertEqual("ok", run["run_status"])
        self.assertEqual(2, run["pages_submitted"])
        self.assertEqual(2, run["pages_completed"])

        protocolo = db.rows(
            self.conn,
            "SELECT * FROM protocols WHERE stage = 'text_extraction'",
        )[0]
        self.assertEqual("deterministic", protocolo["executor_type"])
        self.assertIn("pypdf", protocolo["parameters_json"])

    def test_reexecucao_e_deterministica_e_nao_duplica(self) -> None:
        self._cria_objeto(
            "00001", _pdf_minimo(["CAIXA DE CONVERSAO", None]), 2
        )
        extrai_texto.extrai_celula(
            self.conn, bib="178691", ano=1906, raiz_texto=self.raiz_texto
        )
        sha_antes = self._vigentes()[0]["text_sha256"]

        stats = extrai_texto.extrai_celula(
            self.conn, bib="178691", ano=1906, raiz_texto=self.raiz_texto
        )

        self.assertEqual(0, stats.pages_submitted)
        self.assertEqual(
            2,
            db.rows(
                self.conn, "SELECT COUNT(*) AS n FROM page_text_extractions"
            )[0]["n"],
        )
        self.assertEqual(
            1,
            db.rows(
                self.conn, "SELECT COUNT(*) AS n FROM text_extraction_runs"
            )[0]["n"],
        )
        self.assertEqual(sha_antes, self._vigentes()[0]["text_sha256"])

    def test_pdf_corrompido_e_pagina_faltante_geram_erro_positivo(
        self,
    ) -> None:
        self._cria_objeto("00001", b"isto nao e um pdf", 2)
        self._cria_objeto(
            "00002", _pdf_minimo(["GAZETA DE NOTICIAS"]), 3
        )

        stats = extrai_texto.extrai_celula(
            self.conn, bib="178691", ano=1906, raiz_texto=self.raiz_texto
        )

        self.assertEqual(5, stats.pages_submitted)
        self.assertEqual(1, stats.ok)
        self.assertEqual(0, stats.empty)
        self.assertEqual(4, stats.error)

        vigentes = self._vigentes()
        corrompidas = [r for r in vigentes if r["object_id"] == 1]
        self.assertEqual(2, len(corrompidas))
        for registro in corrompidas:
            self.assertEqual("error", registro["result_status"])

        erros = db.rows(
            self.conn,
            """
            SELECT error_class FROM page_text_extractions
            WHERE result_status = 'error'
            """,
        )
        self.assertEqual(4, len(erros))
        for erro in erros:
            self.assertTrue(erro["error_class"])

        fora_do_pdf = [
            r
            for r in vigentes
            if r["object_id"] == 2 and r["page_number"] == 3
        ]
        self.assertEqual("error", fora_do_pdf[0]["result_status"])

    def test_nova_obtencao_com_hash_diferente_reextrai(self) -> None:
        object_id = self._cria_objeto(
            "00001", _pdf_minimo(["PRIMEIRA VERSAO"]), 1
        )
        extrai_texto.extrai_celula(
            self.conn, bib="178691", ano=1906, raiz_texto=self.raiz_texto
        )

        novo_pdf = _pdf_minimo(["SEGUNDA VERSAO"])
        pdf_path = self.pdf_dir / "per178691_1906_00001.pdf"
        pdf_path.write_bytes(novo_pdf)
        timestamp = db.utc_now()
        db.mark_download_status(
            self.conn,
            object_id=object_id,
            result="ok",
            attempted_at=timestamp,
            completed_at=timestamp,
            http_status=200,
            storage_path=str(pdf_path),
            pdf_sha256=hashlib.sha256(novo_pdf).hexdigest(),
            byte_count=len(novo_pdf),
            page_count=1,
        )
        self.conn.commit()

        stats = extrai_texto.extrai_celula(
            self.conn, bib="178691", ano=1906, raiz_texto=self.raiz_texto
        )

        self.assertEqual(1, stats.pages_submitted)
        self.assertEqual(
            2,
            db.rows(
                self.conn, "SELECT COUNT(*) AS n FROM page_text_extractions"
            )[0]["n"],
        )
        vigente = self._vigentes()[0]
        self.assertEqual(
            hashlib.sha256(novo_pdf).hexdigest(),
            vigente["source_pdf_sha256"],
        )
        self.assertIn(
            "SEGUNDA VERSAO",
            Path(vigente["text_path"]).read_text("utf-8"),
        )

    def test_manifesto_e_deterministico(self) -> None:
        self._cria_objeto(
            "00001", _pdf_minimo(["CAIXA DE CONVERSAO", None]), 2
        )
        extrai_texto.extrai_celula(
            self.conn, bib="178691", ano=1906, raiz_texto=self.raiz_texto
        )

        manifesto = self.tmp / "extracao_178691_1906.csv"
        extrai_texto.exporta_manifesto(
            self.conn,
            bib="178691",
            ano=1906,
            caminho=manifesto,
            raiz_texto=self.raiz_texto,
        )
        primeira = manifesto.read_bytes()
        extrai_texto.exporta_manifesto(
            self.conn,
            bib="178691",
            ano=1906,
            caminho=manifesto,
            raiz_texto=self.raiz_texto,
        )
        self.assertEqual(primeira, manifesto.read_bytes())

        linhas = primeira.decode("utf-8").splitlines()
        self.assertEqual(
            "source_identifier,page_number,result_status,char_count,"
            "text_sha256,source_pdf_sha256,text_relpath",
            linhas[0],
        )
        self.assertEqual(3, len(linhas))
        self.assertIn("per178691_1906_00001,1,ok", linhas[1])
        self.assertIn(
            "178691/per178691_1906_00001/p001.txt", linhas[1]
        )
        self.assertIn("per178691_1906_00001,2,empty", linhas[2])

    def test_verificacao_detecta_arquivo_adulterado(self) -> None:
        self._cria_objeto("00001", _pdf_minimo(["CAIXA DE CONVERSAO"]), 1)
        extrai_texto.extrai_celula(
            self.conn, bib="178691", ano=1906, raiz_texto=self.raiz_texto
        )

        self.assertEqual(
            [],
            extrai_texto.verifica_celula(
                self.conn, bib="178691", ano=1906
            ),
        )

        arquivo = Path(self._vigentes()[0]["text_path"])
        arquivo.write_text("texto adulterado", encoding="utf-8")
        divergencias = extrai_texto.verifica_celula(
            self.conn, bib="178691", ano=1906
        )
        self.assertEqual(1, len(divergencias))
        self.assertIn("per178691_1906_00001", divergencias[0])


if __name__ == "__main__":
    unittest.main()
