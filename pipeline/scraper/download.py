"""F1b — download das edições-hit do host estático da Hemeroteca.

Lê a lista de hits da F1a (CSV com colunas: jornal,bib,ano,edicao) e baixa cada
EDIÇÃO INTEIRA em PDF de:

    https://hemeroteca-pdf.bn.gov.br/{bib}/per{bib}_{ano}_{edicao:05d}.pdf

HTTP puro (o host estático não tem o Cloudflare do DocReader — verificado 14/07/2026).
Educado e retomável:
  - rate-limit entre requisições de rede (não conta os pulos por resume);
  - retry com backoff exponencial;
  - resume: pula PDF já baixado e válido;
  - 404 → registra em auditoria de recall (hit sem PDF no host), não aborta;
  - valida assinatura %PDF de cada download.

Uso:
  uv run python pipeline/scraper/download.py --hits dados/scraping/hits/opaiz_1906.csv
  uv run python pipeline/scraper/download.py --hits ... --limite 5           # amostra
  uv run python pipeline/scraper/download.py --hits ... --out dados/raw_pdf/_teste_f1b
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys
import time

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import hemeroteca as H  # noqa: E402


def le_hits(caminho: pathlib.Path) -> list[dict]:
    """Lê o CSV de hits. Colunas mínimas: bib, ano, edicao (jornal é opcional)."""
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.DictReader(f))
    faltando = {"bib", "ano", "edicao"} - set(linhas[0].keys() if linhas else [])
    if faltando:
        sys.exit(f"CSV de hits sem colunas obrigatórias: {faltando}")
    # dedup por (bib, ano, edicao): a edição inteira cobre vários hits da mesma edição
    vistos, unicos = set(), []
    for h in linhas:
        chave = (h["bib"].strip(), h["ano"].strip(), h["edicao"].strip())
        if chave not in vistos:
            vistos.add(chave)
            unicos.append(h)
    return unicos


def baixa_um(sessao: requests.Session, url: str, destino: pathlib.Path,
             tentativas: int = 4) -> tuple[str, str]:
    """Baixa uma edição. Retorna (status, detalhe). status ∈ {ok,404,erro}."""
    espera = 3.0
    for tentativa in range(1, tentativas + 1):
        try:
            r = sessao.get(url, timeout=60, stream=True)
            if r.status_code == 404:
                return "404", "não existe no host"
            r.raise_for_status()
            tmp = destino.with_suffix(".pdf.part")
            total = 0
            with open(tmp, "wb") as f:
                for bloco in r.iter_content(chunk_size=65536):
                    if bloco:
                        f.write(bloco)
                        total += len(bloco)
            tmp.replace(destino)
            if not H.eh_pdf_valido(destino):
                destino.unlink(missing_ok=True)
                return "erro", f"resposta não é PDF válido ({total} bytes)"
            return "ok", f"{total / 1024:.0f} KB"
        except requests.RequestException as e:
            if tentativa == tentativas:
                return "erro", f"falhou após {tentativas} tentativas: {e}"
            time.sleep(espera)
            espera *= 2
    return "erro", "inesperado"


def main() -> None:
    ap = argparse.ArgumentParser(description="F1b: baixa edições-hit do host estático da Hemeroteca")
    ap.add_argument("--hits", required=True, type=pathlib.Path, help="CSV de hits (jornal,bib,ano,edicao)")
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("dados/raw_pdf"),
                    help="raiz de saída (subpasta por jornal); padrão dados/raw_pdf")
    ap.add_argument("--limite", type=int, default=0, help="baixar no máximo N (0 = todos); útil p/ amostra")
    ap.add_argument("--pausa", type=float, default=2.5, help="segundos entre requisições de rede")
    args = ap.parse_args()

    if not args.hits.exists():
        sys.exit(f"lista de hits não encontrada: {args.hits}")
    hits = le_hits(args.hits)
    if args.limite:
        hits = hits[:args.limite]
    print(f"Hits (edições únicas) a processar: {len(hits)}  |  saída: {args.out}")

    sessao = requests.Session()
    sessao.headers.update({"User-Agent": H.USER_AGENT, "Accept": "application/pdf,*/*"})

    audit = args.out / "_auditoria_404.csv"
    audit.parent.mkdir(parents=True, exist_ok=True)
    faltantes = []
    n_ok = n_pulado = n_404 = n_erro = 0

    for i, h in enumerate(hits, 1):
        bib, ano, edicao = h["bib"].strip(), h["ano"].strip(), h["edicao"].strip()
        slug = (h.get("jornal") or "").strip() and H.JORNAIS.get(h["jornal"].strip(), {}).get("slug")
        slug = slug or H.slug_por_bib(bib)
        pasta = args.out / slug
        pasta.mkdir(parents=True, exist_ok=True)
        destino = pasta / H.nome_pdf(bib, ano, edicao)

        if H.eh_pdf_valido(destino):  # resume
            n_pulado += 1
            continue

        url = H.url_pdf(bib, ano, edicao)
        status, detalhe = baixa_um(sessao, url, destino)
        marca = {"ok": "[ok] ", "404": "[404]", "erro": "[ERRO]"}[status]
        print(f"  [{i}/{len(hits)}] {marca} {H.nome_pdf(bib, ano, edicao)}  {detalhe}")
        if status == "ok":
            n_ok += 1
        elif status == "404":
            n_404 += 1
            faltantes.append({"jornal": h.get("jornal", ""), "bib": bib, "ano": ano,
                              "edicao": edicao, "url": url})
        else:
            n_erro += 1
            faltantes.append({"jornal": h.get("jornal", ""), "bib": bib, "ano": ano,
                              "edicao": edicao, "url": url, "erro": detalhe})
        time.sleep(args.pausa)  # educação: só após bater na rede

    if faltantes:
        campos = ["jornal", "bib", "ano", "edicao", "url", "erro"]
        with open(audit, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            for row in faltantes:
                w.writerow({c: row.get(c, "") for c in campos})

    print(f"\nResumo: {n_ok} baixados · {n_pulado} já tinham (resume) · "
          f"{n_404} ausentes (404) · {n_erro} erros")
    if faltantes:
        print(f"Auditoria de faltantes: {audit}")


if __name__ == "__main__":
    main()
