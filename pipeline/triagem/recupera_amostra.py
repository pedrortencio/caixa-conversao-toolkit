"""Recuperação por visão dos artigos da amostra de registro (Passo 1b).

Para cada página amostrada em `dados/triagem/amostra_registro.csv`, extrai a
imagem legível do scan (JPEG embutido no PDF), pede ao Claude (visão) a
transcrição estruturada dos artigos que mencionam a Caixa de Conversão, e
monta o dataset rotulável que Pedro classifica por registro. A forma
observável (`forma`) vem de graça e serve de sinal de registro.

Estatuto: recuperação/transcrição com proveniência (atividade "pode avançar"
do contexto de mensuração), NÃO é o instrumento de stance. O julgamento de
registro é humano. Saída não-determinística (LLM); registra-se modelo, versão
e o OCR original ao lado do texto recuperado, para auditoria.

Contrato: docs/superpowers/specs/2026-07-21-decomposicao-registro-substancia-
design.md (camada de recuperação da amostra).
"""

from __future__ import annotations

import argparse
import base64
import csv
import io
import re
import sqlite3
import sys
import time
import unicodedata
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel
from pypdf import PdfReader

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db
from pipeline.triagem import db_leitura
from pipeline.triagem.roda_censo import DIR_MANIFESTO

MODELO = "claude-sonnet-5"
PROTOCOLO = "recuperacao-artigo-visao/claude-sonnet-5 0.1.0"
MAX_EDGE = 2576
MAX_TOKENS = 12000
# Sonnet 5 preço introdutório por 1M tokens (até 2026-08-31): input, output.
PRECO_IN, PRECO_OUT = 2.0, 10.0
TETO_USD = 18.0  # guarda: para antes de encostar nos $20

DIR_AMOSTRA = DIR_MANIFESTO / "amostra_registro.csv"
DIR_SAIDA = DIR_MANIFESTO / "amostra_recuperada.csv"

CABECALHO = [
    "item_id",
    "jornal",
    "source_identifier",
    "source_year",
    "page_number",
    "data",
    "data_fonte",
    "titulo",
    "secao",
    "forma",
    "continua",
    "trecho_caixa",
    "texto",
    "match_ids_pagina",
    "ocr_contexto",
    "modelo",
    "protocolo",
    "registro",
]

MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5,
    "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "septembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}
_DATA = re.compile(r"(\d{1,2})\s+de\s+([a-z]+)\s+de\s+(\d{4})")

PROMPT = """Esta é uma página de jornal brasileiro de 1906-1914 (ortografia \
da época). Localize CADA artigo ou item que menciona pelo nome a "Caixa de \
Conversão" (a instituição monetária). O OCR pode ter corrompido o nome, mas \
na imagem ele estará legível. NÃO inclua matérias vizinhas que não mencionem \
a Caixa de Conversão. Para cada item que a menciona, extraia:
- titulo: título/manchete do item (null se for tabela ou nota sem título)
- secao: cabeçalho de seção impresso acima dele, se houver (senão null)
- forma: a forma OBSERVÁVEL, uma de: editorial, artigo, noticia, telegrama, \
tabela_boletim, lista, anuncio, outro
- texto: transcrição VERBATIM e completa do item, ortografia da época \
preservada; se continuar além desta página, transcreva o que há aqui e marque \
continua=true; trechos ilegíveis viram [ilegível]. Não resuma.
- continua: true se o item continua em outra página/coluna
- trecho_caixa: a frase exata que menciona a Caixa, para localização

Também, se visíveis nesta página:
- data: a data completa do cabeçalho/masthead (verbatim), senão null
- pagina_impressa: número da página impressa, senão null
- observacoes: notas de legibilidade do scan, senão null

NÃO julgue se o conteúdo é ortodoxo ou expansionista, nem se é relevante: só \
transcreva e classifique a forma observável. Menção de rotina (escala de \
guarda, movimento de ouro) também entra, com a forma apropriada."""


class Item(BaseModel):
    titulo: str | None
    secao: str | None
    forma: str
    texto: str
    continua: bool
    trecho_caixa: str


class Artigo(BaseModel):
    data: str | None
    pagina_impressa: str | None
    itens: list[Item]
    observacoes: str | None


def _norm(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto.casefold())
    sem = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem)


def parse_data_masthead(texto_pag1: str) -> str | None:
    """Data normalizada (YYYY-MM-DD) do masthead, via OCR da página 1."""
    encontrado = _DATA.search(_norm(texto_pag1))
    if not encontrado:
        return None
    dia, mes_nome, ano = encontrado.groups()
    mes = MESES.get(mes_nome)
    if mes is None:
        return None
    return f"{int(ano):04d}-{mes:02d}-{int(dia):02d}"


def _storage_paths(conn: sqlite3.Connection) -> dict[str, str]:
    return {
        row["source_identifier"]: row["storage_path"]
        for row in db.rows(
            conn,
            """
            SELECT o.source_identifier, f.storage_path
            FROM digital_objects o
            JOIN current_object_fetches cf ON cf.object_id = o.id
            JOIN object_fetches f ON f.id = cf.fetch_id AND f.result = 'ok'
            """,
        )
    }


def imagem_b64(storage_path: str, page_number: int) -> str:
    reader = PdfReader(storage_path)
    imgs = reader.pages[page_number - 1].images
    if not imgs:
        raise ValueError(f"sem imagem embutida em {storage_path} p{page_number}")
    img = max((i.image for i in imgs), key=lambda im: im.size[0] * im.size[1])
    img = img.convert("L")
    w, h = img.size
    escala = MAX_EDGE / max(w, h)
    if escala < 1:
        img = img.resize((int(w * escala), int(h * escala)))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


def extrai_pagina(
    client: anthropic.Anthropic, b64: str, max_tokens: int = MAX_TOKENS
) -> tuple[Artigo, int, int]:
    resp = client.messages.parse(
        model=MODELO,
        max_tokens=max_tokens,
        thinking={"type": "disabled"},
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {
                    "type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": PROMPT},
            ],
        }],
        output_format=Artigo,
    )
    return (
        resp.parsed_output,
        resp.usage.input_tokens,
        resp.usage.output_tokens,
    )


def _ja_feitas(caminho: Path) -> set[tuple[str, int]]:
    if not caminho.exists():
        return set()
    with caminho.open(encoding="utf-8", newline="") as entrada:
        return {
            (r["source_identifier"], int(r["page_number"]))
            for r in csv.DictReader(entrada)
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Recupera artigos da amostra por visão (Claude)"
    )
    parser.add_argument("--base", default=str(db.DEFAULT_DATABASE))
    parser.add_argument("--amostra", default=str(DIR_AMOSTRA))
    parser.add_argument("--saida", default=str(DIR_SAIDA))
    parser.add_argument("--teto-usd", type=float, default=TETO_USD)
    parser.add_argument("--limite", type=int, default=None,
                        help="nº máximo de páginas nesta execução")
    parser.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    args = parser.parse_args(argv)

    load_dotenv(db.ROOT / ".env")
    client = anthropic.Anthropic()

    linhas = list(csv.DictReader(open(args.amostra, encoding="utf-8")))
    # agrega matches por (source_identifier, page): uma chamada por página
    paginas: dict[tuple[str, int], list[dict]] = {}
    for r in linhas:
        paginas.setdefault(
            (r["source_identifier"], int(r["page_number"])), []
        ).append(r)

    conn = db.connect(args.base, migrate=False)
    caminhos = _storage_paths(conn)
    saida = Path(args.saida)
    feitas = _ja_feitas(saida)
    novo = not saida.exists()
    saida.parent.mkdir(parents=True, exist_ok=True)

    custo = 0.0
    n_pag = n_item = 0
    with saida.open("a", encoding="utf-8", newline="") as fout:
        escritor = csv.writer(fout, lineterminator="\n")
        if novo:
            escritor.writerow(CABECALHO)
        for (sid, page), matches in sorted(paginas.items()):
            if (sid, page) in feitas:
                continue
            if custo >= args.teto_usd:
                print(f"[teto] parando: custo ${custo:.2f} >= ${args.teto_usd}",
                      flush=True)
                break
            if args.limite is not None and n_pag >= args.limite:
                break
            ref = matches[0]
            try:
                b64 = imagem_b64(caminhos[sid], page)
                art, ti, to = _com_retry(client, b64, max_tokens=args.max_tokens)
            except Exception as exc:  # registro positivo do erro, segue
                escritor.writerow([
                    f"{sid}:p{page:03d}:ERRO", ref["newspaper"], sid,
                    ref["source_year"], page, "", "erro", "", "", "erro",
                    "", str(exc)[:200], "", ";".join(m["match_id"] for m in matches),
                    ref["contexto"], MODELO, PROTOCOLO, "",
                ])
                fout.flush()
                print(f"[{sid} p{page}] ERRO: {type(exc).__name__}: {exc}",
                      flush=True)
                continue
            custo += ti / 1e6 * PRECO_IN + to / 1e6 * PRECO_OUT
            n_pag += 1

            if art.data:
                data = parse_data_masthead(_norm(art.data)) or art.data
                data_fonte = "masthead_llm"
            else:
                pag1 = _texto_pag1(conn, sid)
                dn = parse_data_masthead(pag1) if pag1 else None
                data, data_fonte = (
                    (dn, "masthead_ocr") if dn else ("", "nao_resolvida")
                )

            mids = ";".join(m["match_id"] for m in matches)
            octx = ref["contexto"]
            for i, item in enumerate(art.itens):
                escritor.writerow([
                    f"{sid}:p{page:03d}:i{i}", ref["newspaper"], sid,
                    ref["source_year"], page, data or "", data_fonte,
                    item.titulo or "", item.secao or "", item.forma,
                    1 if item.continua else 0, item.trecho_caixa,
                    item.texto, mids, octx, MODELO, PROTOCOLO, "",
                ])
                n_item += 1
            if not art.itens:
                # registro positivo: o nome bateu no OCR mas a visão não achou
                # menção na imagem (candidato a falso positivo da triagem).
                escritor.writerow([
                    f"{sid}:p{page:03d}:i0", ref["newspaper"], sid,
                    ref["source_year"], page, data or "", data_fonte,
                    "", "", "sem_mencao_na_imagem", 0, "", "",
                    mids, octx, MODELO, PROTOCOLO, "",
                ])
            fout.flush()
            print(f"[{sid} p{page}] itens={len(art.itens)} "
                  f"data={data!r}({data_fonte}) custo=${custo:.2f}",
                  flush=True)

    conn.close()
    print(f"\nfeito: {n_pag} páginas novas, {n_item} itens, custo ${custo:.2f}",
          flush=True)
    return 0


def _com_retry(
    client: anthropic.Anthropic, b64: str, *,
    max_tokens: int = MAX_TOKENS, tentativas: int = 3
) -> tuple[Artigo, int, int]:
    ultimo: Exception | None = None
    for k in range(tentativas):
        try:
            return extrai_pagina(client, b64, max_tokens=max_tokens)
        except (anthropic.RateLimitError, anthropic.APIStatusError,
                anthropic.APIConnectionError) as exc:
            ultimo = exc
            time.sleep(2 ** k)
    assert ultimo is not None
    raise ultimo


def _texto_pag1(conn: sqlite3.Connection, sid: str) -> str | None:
    for p in db_leitura.itera_paginas(conn, source_identifiers=[sid]):
        if p.page_number == 1:
            return db_leitura.le_conteudo(p)
    return None


if __name__ == "__main__":
    raise SystemExit(main())
