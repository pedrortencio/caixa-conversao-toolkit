"""F1b-Estadão — baixa as páginas-hit em alta resolução e escreve o manifesto.

Para cada nome de arquivo do CSV da F1a:
  1. resolve a URL da imagem em alta via `montaPagina.php` (o salt no nome não é
     derivável, então esse passo é obrigatório e custa uma requisição por página);
  2. baixa o JPEG;
  3. valida assinatura, tamanho e dimensões contra o que o endpoint prometeu;
  4. grava uma linha de proveniência no manifesto.

Educado e retomável: rate-limit só após bater na rede, retry com backoff, resume
por arquivo já válido, e o manifesto é reescrito a cada N páginas para que uma
interrupção não perca o registro do que já veio.

As imagens vão para C:\\dados-caixa (fora do git e do OneDrive); o manifesto, que
é texto leve, vai versionado em dados/scraping/estadao/.

Uso:
  uv run python pipeline/scraper/estadao_download.py --hits dados/scraping/estadao/hits_caixa_de_conversao.csv
  uv run python pipeline/scraper/estadao_download.py --hits ... --limite 5   # amostra
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import pathlib
import re
import sys
import time

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import estadao as E  # noqa: E402

RE_IMG_ALTA = re.compile(r"https://acervo\.estadao\.com\.br/[^\"']*?/g/[^\"']+\.jpg")

CAMPOS_MANIFESTO = [
    "nome_arquivo", "data", "ano", "edicao", "caderno", "pagina", "tipo",
    "url_origem", "largura", "altura", "bytes", "sha256", "arquivo_local",
    "colhido_em", "status",
]


def resolve_url(sessao: requests.Session, nome: str) -> tuple[str | None, int, int]:
    """Consulta montaPagina.php. Retorna (url_alta, largura_prometida, altura_prometida)."""
    r = sessao.get(E.url_monta_pagina(nome), timeout=60)
    r.raise_for_status()
    texto = r.content.decode("utf-8-sig", errors="replace").strip()
    try:
        d = json.loads(texto)
        url = d.get("imagem_reader") or d.get("pagina_impressao") or ""
        larg = int(d.get("imagem_reader_width") or 0)
        alt = int(d.get("imagem_reader_height") or 0)
        if url:
            return url, larg, alt
    except (json.JSONDecodeError, ValueError):
        pass  # cai no regex: o endpoint às vezes devolve JSON malformado
    m = RE_IMG_ALTA.search(texto)
    return (m.group(0) if m else None), 0, 0


def baixa_um(sessao: requests.Session, url: str, destino: pathlib.Path,
             tentativas: int = 4) -> tuple[str, str]:
    """Baixa uma página. Retorna (status, detalhe). status ∈ {ok,404,erro}."""
    espera = 3.0
    for tentativa in range(1, tentativas + 1):
        try:
            r = sessao.get(url, timeout=90, stream=True)
            if r.status_code == 404:
                return "404", "não existe no acervo"
            r.raise_for_status()
            destino.parent.mkdir(parents=True, exist_ok=True)
            tmp = destino.with_suffix(".jpg.part")
            total = 0
            with open(tmp, "wb") as f:
                for bloco in r.iter_content(chunk_size=1 << 16):
                    if bloco:
                        f.write(bloco)
                        total += len(bloco)
            tmp.replace(destino)
            if not E.eh_jpeg_valido(destino):
                destino.unlink(missing_ok=True)
                return "erro", f"resposta não é JPEG em alta ({total} bytes)"
            return "ok", f"{total / 1024:.0f} KB"
        except requests.RequestException as e:
            if tentativa == tentativas:
                return "erro", f"falhou após {tentativas} tentativas: {e}"
            time.sleep(espera)
            espera *= 2
    return "erro", "inesperado"


def grava_manifesto(caminho: pathlib.Path, linhas: list[dict]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_MANIFESTO)
        w.writeheader()
        for linha in linhas:
            w.writerow({c: linha.get(c, "") for c in CAMPOS_MANIFESTO})


def main() -> None:
    ap = argparse.ArgumentParser(description="F1b-Estadão: baixa páginas-hit em alta resolução")
    ap.add_argument("--hits", required=True, type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, default=E.RAIZ_IMAGENS,
                    help=f"raiz das imagens (padrão {E.RAIZ_IMAGENS})")
    ap.add_argument("--manifesto", type=pathlib.Path,
                    default=pathlib.Path("dados/scraping/estadao/manifesto.csv"))
    ap.add_argument("--limite", type=int, default=0, help="baixar no máximo N (0 = todos)")
    ap.add_argument("--pausa", type=float, default=3.0, help="segundos entre requisições")
    args = ap.parse_args()

    if not args.hits.exists():
        sys.exit(f"CSV de hits não encontrado: {args.hits}")
    with open(args.hits, encoding="utf-8-sig", newline="") as f:
        hits = list(csv.DictReader(f))
    if args.limite:
        hits = hits[:args.limite]
    print(f"Páginas a processar: {len(hits)}  |  imagens: {args.out}  |  pausa: {args.pausa}s")

    sessao = requests.Session()
    sessao.headers.update({
        "User-Agent": E.USER_AGENT,
        "Referer": f"{E.HOST}/pagina/",
        "Accept": "image/jpeg,image/*,*/*",
    })

    manifesto: list[dict] = []
    n_ok = n_pulado = n_erro = 0

    for i, h in enumerate(hits, 1):
        nome = h["nome_arquivo"].strip()
        destino = E.caminho_local(nome, args.out)
        base = {k: h.get(k, "") for k in
                ("nome_arquivo", "data", "ano", "edicao", "caderno", "pagina", "tipo")}

        if E.eh_jpeg_valido(destino):  # resume
            larg, alt = E.dimensoes_jpeg(destino) or (0, 0)
            manifesto.append({**base, "url_origem": "", "largura": larg, "altura": alt,
                              "bytes": destino.stat().st_size, "sha256": E.sha256(destino),
                              "arquivo_local": str(destino), "colhido_em": "",
                              "status": "ja_tinha"})
            n_pulado += 1
            continue

        try:
            url, larg_prom, alt_prom = resolve_url(sessao, nome)
        except requests.RequestException as e:
            print(f"  [{i}/{len(hits)}] [ERRO] {nome}  resolução falhou: {e}")
            manifesto.append({**base, "status": f"erro_resolucao: {e}"})
            n_erro += 1
            time.sleep(args.pausa)
            continue
        time.sleep(args.pausa)

        if not url:
            print(f"  [{i}/{len(hits)}] [ERRO] {nome}  sem URL de alta resolução")
            manifesto.append({**base, "status": "sem_url_alta"})
            n_erro += 1
            continue

        status, detalhe = baixa_um(sessao, url, destino)
        marca = {"ok": "[ok] ", "404": "[404]", "erro": "[ERRO]"}[status]
        print(f"  [{i}/{len(hits)}] {marca} {nome}  {detalhe}")

        if status == "ok":
            larg, alt = E.dimensoes_jpeg(destino) or (0, 0)
            aviso = ""
            if larg_prom and (larg, alt) != (larg_prom, alt_prom):
                # divergência entre o prometido e o entregue: não corrige, registra
                aviso = f" (endpoint prometeu {larg_prom}x{alt_prom})"
                print(f"        aviso: dimensões divergem{aviso}")
            manifesto.append({**base, "url_origem": url, "largura": larg, "altura": alt,
                              "bytes": destino.stat().st_size, "sha256": E.sha256(destino),
                              "arquivo_local": str(destino),
                              "colhido_em": dt.datetime.now().isoformat(timespec="seconds"),
                              "status": "ok" + aviso})
            n_ok += 1
        else:
            manifesto.append({**base, "url_origem": url, "status": f"{status}: {detalhe}"})
            n_erro += 1

        time.sleep(args.pausa)
        if i % 25 == 0:  # checkpoint: interrupção não perde o registro
            grava_manifesto(args.manifesto, manifesto)

    grava_manifesto(args.manifesto, manifesto)
    gb = sum(int(m.get("bytes") or 0) for m in manifesto) / (1 << 30)
    print(f"\nResumo: {n_ok} baixadas · {n_pulado} já tinham (resume) · {n_erro} erros")
    print(f"Volume no manifesto: {gb:.2f} GB  |  manifesto: {args.manifesto}")


if __name__ == "__main__":
    main()
