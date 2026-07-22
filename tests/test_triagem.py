"""Testes da triagem por nome com banco real (db_leitura, roda_censo,
calibra_1906). Semeia objetos/páginas/textos direto no schema, sem pypdf,
para controlar o conteúdo do OCR."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from pipeline.base import db
from pipeline.triagem import (
    calibra_1906,
    db_leitura,
    regra_nome,
    relatorio_triagem,
    roda_censo,
)

_BIB_JORNAL = {
    "178691": ("o_paiz", "O Paiz", "Rio de Janeiro"),
    "090972": ("correio_paulistano", "Correio Paulistano", "São Paulo"),
}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


class FixtureBancoTriagem(unittest.TestCase):
    """Base sem testes: banco em tempdir com o helper `_semeia`. Reusada por
    TriagemTests e pelos testes da amostra de registro, sem rerodar testes."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.raiz_texto = self.tmp / "texto"
        self.conn = db.connect(self.tmp / "base.db")
        self.addCleanup(self.conn.close)
        self.newspaper_ids: dict[str, int] = {}
        for bib, (slug, title, city) in _BIB_JORNAL.items():
            self.newspaper_ids[bib] = db.upsert_newspaper(
                self.conn, slug=slug, title=title, bn_bib=bib, city=city
            )
        self.inv_protocol = db.upsert_protocol(
            self.conn, stage="inventory", name="t", version="1",
            executor_type="deterministic", code_commit="abc", parameters={},
        )
        self.txt_protocol = db.upsert_protocol(
            self.conn, stage="text_extraction", name="t", version="1",
            executor_type="deterministic", code_commit="abc", parameters={},
        )
        self.conn.commit()

    def _semeia(
        self, bib: str, ano: int, numero: str, textos: list[str | None]
    ) -> int:
        """Cria objeto + páginas + camada de texto vigente. None = página
        sem texto (empty)."""
        source_identifier = f"per{bib}_{ano}_{numero}"
        object_id = db.upsert_digital_object(
            self.conn,
            newspaper_id=self.newspaper_ids[bib],
            source_identifier=source_identifier,
            source_url=f"https://x.test/{source_identifier}.pdf",
            source_year=ano,
            bn_file_key=f"{bib}/{source_identifier}.pdf",
            bn_file_number_literal=numero,
            discovered_by_protocol_id=self.inv_protocol,
        )
        ts = db.utc_now()
        cur = self.conn.execute(
            """
            INSERT INTO text_extraction_runs(
                protocol_id, started_at, completed_at, run_status,
                scope_manifest_sha256, pages_submitted, pages_completed
            ) VALUES (?, ?, ?, 'ok', ?, ?, ?)
            """,
            (self.txt_protocol, ts, ts, "0" * 64, len(textos), len(textos)),
        )
        run_id = int(cur.lastrowid)
        pdf_sha = _sha(source_identifier)
        for page_number, texto in enumerate(textos, start=1):
            cur = self.conn.execute(
                "INSERT INTO physical_pages(object_id, page_number, created_at)"
                " VALUES (?, ?, ?)",
                (object_id, page_number, ts),
            )
            page_id = int(cur.lastrowid)
            if texto is None:
                cur = self.conn.execute(
                    """
                    INSERT INTO page_text_extractions(
                        page_id, extraction_run_id, source_pdf_sha256,
                        result_status, char_count, created_at
                    ) VALUES (?, ?, ?, 'empty', 0, ?)
                    """,
                    (page_id, run_id, pdf_sha, ts),
                )
            else:
                destino = (
                    self.raiz_texto / bib / source_identifier
                    / f"p{page_number:03d}.txt"
                )
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(texto.encode("utf-8"))
                cur = self.conn.execute(
                    """
                    INSERT INTO page_text_extractions(
                        page_id, extraction_run_id, source_pdf_sha256,
                        result_status, text_path, text_sha256, char_count,
                        created_at
                    ) VALUES (?, ?, ?, 'ok', ?, ?, ?, ?)
                    """,
                    (
                        page_id, run_id, pdf_sha, str(destino),
                        _sha(texto), len(texto), ts,
                    ),
                )
            extraction_id = int(cur.lastrowid)
            self.conn.execute(
                """
                INSERT INTO current_page_text_extractions(
                    page_id, extraction_id, selected_at
                ) VALUES (?, ?, ?)
                """,
                (page_id, extraction_id, ts),
            )
        self.conn.commit()
        return object_id


class TriagemTests(FixtureBancoTriagem):
    # --- db_leitura ---
    def test_itera_paginas_ordem_e_filtro(self) -> None:
        self._semeia("178691", 1906, "00002", ["b", "a"])
        self._semeia("178691", 1906, "00001", ["x"])
        paginas = list(db_leitura.itera_paginas(self.conn, bib="178691"))
        # ordenado por source_identifier, page_number
        self.assertEqual(
            [(p.source_identifier, p.page_number) for p in paginas],
            [
                ("per178691_1906_00001", 1),
                ("per178691_1906_00002", 1),
                ("per178691_1906_00002", 2),
            ],
        )
        so_um = list(
            db_leitura.itera_paginas(
                self.conn, source_identifiers=["per178691_1906_00001"]
            )
        )
        self.assertEqual(1, len(so_um))
        self.assertEqual("178691", so_um[0].bib)

    def test_le_conteudo_ok_e_empty(self) -> None:
        self._semeia("178691", 1906, "00001", ["Caixa de Conversão", None])
        paginas = list(db_leitura.itera_paginas(self.conn, bib="178691"))
        self.assertEqual("Caixa de Conversão", db_leitura.le_conteudo(paginas[0]))
        self.assertEqual("", db_leitura.le_conteudo(paginas[1]))

    # --- roda_censo ---
    def test_avalia_objetos_relevancia_e_triado_completo(self) -> None:
        # objeto com hit numa página e uma página sem texto
        self._semeia(
            "178691", 1906, "00001",
            ["nada aqui", "a caixa de conversao e o cambio", None],
        )
        # objeto sem menção nenhuma, totalmente triado
        self._semeia("178691", 1906, "00002", ["bom dia", "boa noite"])
        objetos = {
            o.source_identifier: o
            for o in roda_censo.avalia_objetos(self.conn, bib="178691")
        }
        o1 = objetos["per178691_1906_00001"]
        self.assertTrue(o1.relevante)
        self.assertEqual(1, o1.paginas_hit)
        self.assertEqual(1, o1.paginas_sem_texto)
        self.assertFalse(o1.triado_completo)  # tem página empty
        o2 = objetos["per178691_1906_00002"]
        self.assertFalse(o2.relevante)
        self.assertTrue(o2.triado_completo)

    def test_conta_matches_agregados_no_objeto(self) -> None:
        self._semeia(
            "178691", 1906, "00001",
            ["caixa de conversao aqui", "e caixa de conversao de novo"],
        )
        o = roda_censo.avalia_objetos(self.conn, bib="178691")[0]
        self.assertEqual(2, o.n_matches)

    def test_manifesto_deterministico_e_conteudo(self) -> None:
        self._semeia(
            "178691", 1906, "00001", ["a caixa de conversao", None]
        )
        decisoes = list(roda_censo.avalia_paginas(self.conn, bib="178691"))
        caminho = self.tmp / "manifesto.csv"
        roda_censo.escreve_manifesto(decisoes, caminho)
        primeira = caminho.read_bytes()
        roda_censo.escreve_manifesto(decisoes, caminho)
        self.assertEqual(primeira, caminho.read_bytes())
        linhas = primeira.decode("utf-8").splitlines()
        self.assertEqual(linhas[0], ",".join(roda_censo.CABECALHO_MANIFESTO))
        self.assertIn("per178691_1906_00001,1,1,1", linhas[1])  # hit
        self.assertIn(roda_censo.regra_nome.REGRA_VERSAO, linhas[1])
        self.assertIn("per178691_1906_00001,2,0,0", linhas[2])  # empty, no hit
        self.assertTrue(linhas[2].endswith(",empty"))

    # --- calibra_1906 ---
    def _escreve_gold(
        self, bib: str, numero: str, label: str | None, invalido: bool = False
    ) -> None:
        pasta = self.tmp / "piloto" / calibra_1906.GABARITO_DIRS[bib]
        pasta.mkdir(parents=True, exist_ok=True)
        if invalido:
            (pasta / f"per{bib}_1906_{numero}_raw_invalid_json.txt").write_text(
                "lixo", encoding="utf-8"
            )
        else:
            (
                pasta / f"per{bib}_1906_{numero}_classificacao_holistica.json"
            ).write_text(
                json.dumps({"overall_classification": label}), encoding="utf-8"
            )

    def test_calibra_recall_e_sonda_em_conjuntos_distintos(self) -> None:
        # positivo recuperado
        self._semeia("178691", 1906, "00001", ["a caixa de conversao e o ouro"])
        self._escreve_gold("178691", "00001", "Clearly Orthodox")
        # positivo perdido (gabarito diz posição, mas OCR não tem o nome)
        self._semeia("178691", 1906, "00002", ["texto sem o termo algum"])
        self._escreve_gold("178691", "00002", "Leaning Expansionist")
        # NRM que a regra flaga (subcontagem do método antigo)
        self._semeia("178691", 1906, "00003", ["afinal a caixa de conversao"])
        self._escreve_gold("178691", "00003", "No Relevant Mentions Found")
        # NRM que a regra NÃO flaga
        self._semeia("178691", 1906, "00004", ["nada de interesse"])
        self._escreve_gold("178691", "00004", "No Relevant Mentions Found")
        # inválido: fora das duas métricas
        self._semeia("178691", 1906, "00005", ["a caixa de conversao"])
        self._escreve_gold("178691", "00005", None, invalido=True)

        c = calibra_1906.calibra(
            self.conn, bib="178691", dir_piloto=self.tmp / "piloto"
        )
        self.assertEqual(2, c.positivos)
        self.assertEqual(1, c.positivos_recuperados)
        self.assertAlmostEqual(0.5, c.recall)
        self.assertEqual(["per178691_1906_00002"], c.positivos_perdidos)
        self.assertEqual(2, c.nao_relevantes)
        self.assertEqual(1, c.nao_relevantes_com_hit)
        self.assertEqual(["per178691_1906_00003"], c.nao_relevantes_flagados)
        self.assertEqual(1, c.invalidos)

    def test_calibra_coalesce_edicoes_ab(self) -> None:
        # um único objeto no censo; duas manifestações A/B no gabarito,
        # uma positiva e uma não-relevante -> objeto-dia é positivo
        self._semeia("178691", 1906, "01646", ["a caixa de conversao discute"])
        self._escreve_gold("178691", "A1646", "No Relevant Mentions Found")
        self._escreve_gold("178691", "B1646", "Clearly Expansionist")
        gab = calibra_1906.carrega_gabarito(self.tmp / "piloto", "178691")
        self.assertEqual(1, len(gab))
        item = gab["per178691_1906_01646"]
        self.assertEqual("Clearly Expansionist", item.label)


class RelatorioTriagemTests(unittest.TestCase):
    def test_resume_manifesto_agrega_r_e_s(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        caminho = Path(tmp.name) / "triagem_nome_178691_1908.csv"
        # obj A: 2 páginas ok, uma com hit -> relevante e triado completo
        # obj B: 1 página ok sem hit + 1 empty -> não relevante, NÃO triado
        # obj C: 1 página ok sem hit -> não relevante, triado completo
        linhas = [
            roda_censo.CABECALHO_MANIFESTO,
            ["178691", "per178691_1908_1", 1, 1, 1, "caixa de conver", 3,
             regra_nome.REGRA_VERSAO, 7, "ok"],
            ["178691", "per178691_1908_1", 2, 0, 0, "", "", regra_nome.REGRA_VERSAO, 7, "ok"],
            ["178691", "per178691_1908_2", 1, 0, 0, "", "", regra_nome.REGRA_VERSAO, 7, "ok"],
            ["178691", "per178691_1908_2", 2, 0, 0, "", "", regra_nome.REGRA_VERSAO, 7, "empty"],
            ["178691", "per178691_1908_3", 1, 0, 0, "", "", regra_nome.REGRA_VERSAO, 7, "ok"],
        ]
        with caminho.open("w", encoding="utf-8", newline="") as saida:
            csv.writer(saida, lineterminator="\n").writerows(linhas)

        r = relatorio_triagem.resume_manifesto(caminho)
        self.assertEqual("178691", r.bib)
        self.assertEqual(1908, r.ano)
        self.assertEqual(3, r.objetos)
        self.assertEqual(1, r.relevantes)  # só o obj A
        self.assertEqual(2, r.triados_completos)  # A e C; B tem empty
        self.assertEqual(5, r.paginas)
        self.assertEqual(4, r.paginas_ok)
        self.assertEqual(1, r.paginas_hit)
        self.assertAlmostEqual(0.5, r.saliencia)  # 1/2


if __name__ == "__main__":
    unittest.main()
