"""Re-extração DIRIGIDA das FALHAs (Passo 1c).

As FALHAs são páginas onde a triagem por nome achou "Caixa de Conversão" no
OCR mas a recuperação de página inteira (recupera_amostra) devolveu 0 itens.
O diagnóstico de 2026-07-22 mostrou que a menção está lá, legível, mas é breve
e incidental (escala de guarda, nomeação) ou está numa coluna que a passada
de página inteira não priorizou, agulha num palheiro denso. A solução dirigida
dá ao modelo a PISTA do OCR (janela larga centrada no match real) e pede para
localizar e transcrever aquela menção específica.

Custo pequeno (~30 páginas). Saída: `falhas_recuperadas.csv`, mesma estrutura
de `amostra_recuperada.csv`, para substituir as linhas `sem_mencao_na_imagem`.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db
from pipeline.triagem import db_leitura, regra_nome
from pipeline.triagem.recupera_amostra import (
    Artigo, MODELO, PRECO_IN, PRECO_OUT, _storage_paths, imagem_b64,
)
from pipeline.triagem.roda_censo import DIR_MANIFESTO

PROTOCOLO = "recuperacao-falha-dirigida/claude-sonnet-5 0.1.0"
JANELA_HINT = 200
TETO_USD = 3.0
ENTRADA = DIR_MANIFESTO / "amostra_recuperada.csv"
SAIDA = DIR_MANIFESTO / "falhas_recuperadas.csv"

CABECALHO = [
    "item_id", "jornal", "source_identifier", "source_year", "page_number",
    "data", "data_fonte", "titulo", "secao", "forma", "continua",
    "trecho_caixa", "texto", "match_ids_pagina", "ocr_contexto", "modelo",
    "protocolo", "registro",
]

PROMPT_HINT = """Esta é uma página de jornal brasileiro de 1906-1914 (ortografia \
da época). O reconhecimento automático de texto (OCR) achou uma menção à \
"Caixa de Conversão" nesta página, neste trecho aproximado (com ruído de OCR):

"{hint}"

Sua tarefa: LOCALIZE na imagem o item que contém essa menção à Caixa de \
Conversão e transcreva-o. A menção pode ser BREVE e incidental, procure com \
atenção mesmo em listas densas e colunas inferiores. Exemplos de menção \
incidental: uma linha de escala de guarda ("na caixa de conversão, alferes \
Fulano"), um item de nomeação ("director da caixa de conversão, Fulano").

Devolva o item com: titulo (null se sem título); secao (cabeçalho impresso, \
senão null); forma (editorial/artigo/noticia/telegrama/tabela_boletim/lista/\
anuncio/outro); texto (transcrição VERBATIM do item, ortografia da época); \
continua (true se continua em outra página); trecho_caixa (a frase exata que \
nomeia a Caixa de Conversão).

NÃO confunda com "Caixa de Amortização" (instituição distinta). Se, mesmo \
procurando com atenção, o nome "Caixa de Conversão" realmente não estiver na \
imagem (o OCR pode ter errado), devolva itens vazio e diga isso em observacoes. \
NÃO julgue ortodoxo/expansionista; só transcreva e classifique a forma."""


def constroi_hint(conn: sqlite3.Connection, sid: str, page: int) -> str | None:
    """Janela larga do OCR centrada no match real do nome, garantindo que a
    pista contenha 'caixa de conversão'."""
    for p in db_leitura.itera_paginas(conn, source_identifiers=[sid]):
        if p.page_number != page:
            continue
        norm = regra_nome.normaliza(db_leitura.le_conteudo(p))
        spans = regra_nome.encontra(db_leitura.le_conteudo(p))
        if not spans:
            return None
        o = spans[0].offset
        return norm[max(0, o - JANELA_HINT): o + len(spans[0].texto) + JANELA_HINT]
    return None


def extrai_dirigido(
    client: anthropic.Anthropic, b64: str, hint: str
) -> tuple[Artigo, int, int]:
    resp = client.messages.parse(
        model=MODELO, max_tokens=8000, thinking={"type": "disabled"},
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {
                "type": "base64", "media_type": "image/jpeg", "data": b64}},
            {"type": "text", "text": PROMPT_HINT.format(hint=hint)}]}],
        output_format=Artigo,
    )
    return resp.parsed_output, resp.usage.input_tokens, resp.usage.output_tokens


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Re-extração dirigida das FALHAs")
    parser.add_argument("--entrada", default=str(ENTRADA))
    parser.add_argument("--saida", default=str(SAIDA))
    parser.add_argument("--teto-usd", type=float, default=TETO_USD)
    args = parser.parse_args(argv)

    load_dotenv(db.ROOT / ".env")
    client = anthropic.Anthropic()

    falhas = [r for r in csv.DictReader(open(args.entrada, encoding="utf-8"))
              if r["forma"] == "sem_mencao_na_imagem"]
    saida = Path(args.saida)
    feitas = set()
    if saida.exists():
        feitas = {r["source_identifier"] + ":" + r["page_number"]
                  for r in csv.DictReader(open(saida, encoding="utf-8"))}

    conn = db.connect(db.DEFAULT_DATABASE, migrate=False)
    caminhos = _storage_paths(conn)
    novo = not saida.exists()
    custo = 0.0
    recuperados = ainda_zero = 0
    with saida.open("a", encoding="utf-8", newline="") as fout:
        w = csv.writer(fout, lineterminator="\n")
        if novo:
            w.writerow(CABECALHO)
        for r in falhas:
            sid, page = r["source_identifier"], int(r["page_number"])
            if f"{sid}:{page}" in feitas:
                continue
            if custo >= args.teto_usd:
                print(f"[teto] parando em ${custo:.2f}", flush=True)
                break
            hint = constroi_hint(conn, sid, page)
            if not hint:
                continue
            try:
                b64 = imagem_b64(caminhos[sid], page)
                art, ti, to = extrai_dirigido(client, b64, hint)
            except Exception as exc:
                print(f"[{sid} p{page}] ERRO {type(exc).__name__}: {exc}", flush=True)
                continue
            custo += ti / 1e6 * PRECO_IN + to / 1e6 * PRECO_OUT
            base = [r["jornal"], sid, r["source_year"], page, r["data"],
                    r["data_fonte"]]
            if art.itens:
                recuperados += 1
                for i, item in enumerate(art.itens):
                    w.writerow([
                        f"{sid}:p{page:03d}:d{i}", *base, item.titulo or "",
                        item.secao or "", item.forma,
                        1 if item.continua else 0, item.trecho_caixa,
                        item.texto, r["match_ids_pagina"], r["ocr_contexto"],
                        MODELO, PROTOCOLO, "",
                    ])
            else:
                ainda_zero += 1
                w.writerow([
                    f"{sid}:p{page:03d}:d0", *base, "", "",
                    "sem_mencao_confirmada", 0, "", "",
                    r["match_ids_pagina"], r["ocr_contexto"], MODELO, PROTOCOLO, "",
                ])
            fout.flush()
            print(f"[{sid} p{page}] itens={len(art.itens)} custo=${custo:.3f}",
                  flush=True)
    conn.close()
    print(f"\nfeito: {recuperados} recuperadas, {ainda_zero} confirmadas sem "
          f"menção, custo ${custo:.3f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
