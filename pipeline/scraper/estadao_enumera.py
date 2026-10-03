"""F1a-Estadão — enumera as páginas do acervo que casam com o termo de triagem.

Percorre `procura/busca.php` ano a ano dentro do recorte 1906-1914 e coleta os
nomes de arquivo distintos. Escreve um CSV de hits que a etapa de download come.

ESCOPO DELIBERADO: o padrão é UM termo, "caixa de conversão", que é menção pelo
nome. Isso é inventário, reversível, e não seleciona segundo o construto.
Ampliar a lista de termos (valorização, papel-moeda, convênio de Taubaté) JÁ É
seleção segundo o construto e passa pelo gate de
`docs/contexto-debate-metodologico-mensuracao.md` antes de rodar. O parâmetro
--termo existe para quando essa decisão tiver sido tomada e registrada, não para
ser usado à revelia dela.

Contagem, que tem duas armadilhas medidas em 12/08/2026 e custou uma leitura
errada antes de ser resolvida:

  1. A página traz "Foram encontrados N registros" e "Exibindo M ocorrências",
     com N sempre 23 acima de M, em todo ano e na busca sem filtro. Só M conta.
  2. Ocorrência não é página. Em 1908 o acervo serviu 156 ocorrências que são
     126 páginas distintas: uma página que menciona o termo duas vezes aparece
     duas vezes no resultado.

Comparar páginas distintas com qualquer um dos contadores fabrica uma taxa de
perda inexistente. A completude se afere por ocorrências SERVIDAS contra
ocorrências PROMETIDAS, e é isso que o resumo final reporta.

Uso:
  uv run python pipeline/scraper/estadao_enumera.py
  uv run python pipeline/scraper/estadao_enumera.py --anos 1906 --out /tmp/teste.csv
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys
import time

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import estadao as E  # noqa: E402

# A página traz DOIS contadores e só um serve.
#   "Foram encontrados N registros"  -> N é sempre 23 a mais que o outro, em todo
#      ano e também na busca sem filtro. É constante global, conta outra coisa.
#   "Exibindo N ocorrências"         -> o conjunto de resultados de fato servido.
# E ocorrência não é página: uma página que menciona o termo duas vezes aparece
# duas vezes no resultado. Medido em 1908 (12/08/2026): 156 ocorrências servidas
# para 126 páginas distintas. Comparar páginas distintas contra qualquer um dos
# dois contadores produz uma "taxa de perda" que não existe.
RE_OCORRENCIAS = re.compile(r"Exibindo\s+([0-9]+)\s+ocorr")
MAX_PAGINAS = 200  # trava de segurança: 10 hits/página, nenhum ano chega perto


def conta_cards(achados: list[str]) -> int:
    """Quantos RESULTADOS uma página de busca trouxe, a partir dos nomes brutos.

    Cada card repete o mesmo nome N vezes na marcação (N=5 na sessão com Referer,
    3 sem ela; por isso o fator é medido e não fixado). Contar `len(achados)` cru
    infla o número em 5x e faz qualquer aferição de completude passar por engano.
    """
    if not achados:
        return 0
    por_nome: dict[str, int] = {}
    for n in achados:
        por_nome[n] = por_nome.get(n, 0) + 1
    repeticao = min(por_nome.values())
    return len(achados) // repeticao if repeticao else 0


def pega_pagina(sessao: requests.Session, termo: str, ano: int, pagina: int,
                pausa: float, tentativas: int = 3) -> tuple[str, list[str]]:
    """Uma página de resultados, com retry. Retorna (html, nomes encontrados).

    O endpoint devolve HTTP 200 mesmo quando o backend de busca falha, então
    status 200 não basta como sinal de saúde.

    ATENÇÃO ao discriminador. A string "Servidor ocupado" aparece em TODA resposta
    boa, dentro de um handler JS de fallback do histograma de décadas
    (`$("#conteudo_decada").html("Servidor ocupado...")`). Procurar por ela marca
    toda página como falha. O sinal honesto de resposta útil é ter resultado ou
    ter o contador de registros; faltando os dois, a resposta não serve.
    """
    espera = pausa
    html = ""
    for tentativa in range(1, tentativas + 1):
        try:
            r = sessao.get(E.url_busca(termo, ano=ano, page=pagina), timeout=60)
            r.raise_for_status()
            html = r.text
            achados = E.RE_NOME.findall(html)
            if not achados and not RE_OCORRENCIAS.search(html):
                raise requests.RequestException("resposta sem resultados e sem contador")
            return html, achados
        except requests.RequestException:
            if tentativa == tentativas:
                return html, []
            time.sleep(espera)
            espera *= 2
    return html, []


def busca_ano(sessao: requests.Session, termo: str, ano: int, pausa: float,
              verbose: bool = True) -> tuple[list[str], int, int]:
    """Varre um ano inteiro.

    Retorna (páginas distintas, ocorrências servidas, ocorrências prometidas).
    A completude se afere por servidas == prometidas. Páginas distintas é menor
    por construção, porque a mesma página pode casar o termo mais de uma vez.
    """
    nomes: list[str] = []
    vistos: set[str] = set()
    prometidas = -1
    servidas = 0

    for pagina in range(1, MAX_PAGINAS + 1):
        html, achados = pega_pagina(sessao, termo, ano, pagina, pausa)

        if prometidas < 0:
            m = RE_OCORRENCIAS.search(html)
            prometidas = int(m.group(1)) if m else 0

        # Página vazia SÓ encerra depois de confirmada: uma falha transitória
        # ("Servidor ocupado") devolve zero resultados e truncaria o ano em
        # silêncio. Medido em 12/08/2026: uma primeira passada perdeu 3 páginas
        # de resultado em 1908 e 1 em 1914 exatamente por isso.
        if not achados:
            time.sleep(pausa * 2)
            html, achados = pega_pagina(sessao, termo, ano, pagina, pausa)
            if not achados:
                break
            print(f"    (página {pagina} de {ano} veio vazia na 1ª tentativa e "
                  f"trouxe {len(achados)} na 2ª; fim de paginação NÃO assumido)")

        servidas += conta_cards(achados)
        for n in achados:
            if n not in vistos:
                vistos.add(n)
                nomes.append(n)
        time.sleep(pausa)

    if verbose:
        completo = "completo" if servidas >= prometidas > 0 else "INCOMPLETO"
        print(f"  {ano}: {len(nomes):3d} páginas distintas de {servidas} ocorrências "
              f"servidas / {prometidas} prometidas  [{completo}]")
    return nomes, servidas, prometidas


def main() -> None:
    ap = argparse.ArgumentParser(description="F1a-Estadão: enumera páginas-hit do acervo")
    ap.add_argument("--termo", default="caixa de conversao",
                    help='termo de busca; ampliar a lista passa pelo gate metodológico')
    ap.add_argument("--anos", type=int, nargs="*",
                    help=f"anos a varrer (padrão {E.ANO_INICIAL}-{E.ANO_FINAL})")
    ap.add_argument("--out", type=pathlib.Path,
                    default=pathlib.Path("dados/scraping/estadao/hits_caixa_de_conversao.csv"))
    ap.add_argument("--pausa", type=float, default=3.0, help="segundos entre requisições")
    args = ap.parse_args()

    anos = args.anos or list(range(E.ANO_INICIAL, E.ANO_FINAL + 1))
    termo = f'"{args.termo}"'  # frase exata

    sessao = requests.Session()
    sessao.headers.update({"User-Agent": E.USER_AGENT, "Referer": f"{E.HOST}/procura/"})

    print(f"Termo: {termo}  |  anos: {anos[0]}-{anos[-1]}  |  pausa: {args.pausa}s")
    linhas: list[dict] = []
    incompletos: list[int] = []

    for ano in anos:
        try:
            nomes, servidas, prometidas = busca_ano(sessao, termo, ano, args.pausa)
        except requests.RequestException as e:
            print(f"  {ano}: ERRO de rede, ano pulado: {e}")
            incompletos.append(ano)
            continue
        if prometidas > 0 and servidas < prometidas:
            incompletos.append(ano)
        for nome in nomes:
            try:
                meta = E.parse_nome(nome)
            except ValueError:
                print(f"    (ignorado, nome fora do padrão) {nome}")
                continue
            meta["termo"] = args.termo
            meta["ocorrencias_servidas_no_ano"] = servidas
            meta["ocorrencias_prometidas_no_ano"] = prometidas
            linhas.append(meta)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    campos = ["nome_arquivo", "data", "ano", "edicao", "caderno", "pagina", "tipo",
              "termo", "ocorrencias_servidas_no_ano", "ocorrencias_prometidas_no_ano"]
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)

    edicoes = len({(x["data"], x["edicao"]) for x in linhas})
    print(f"\n{len(linhas)} páginas distintas em {edicoes} edições -> {args.out}")
    if incompletos:
        print(f"ATENÇÃO: anos com paginação incompleta: {incompletos}. "
              f"Rode de novo só esses anos antes de usar o CSV.")
    else:
        print("Completude: toda ocorrência prometida foi servida em todos os anos.")


if __name__ == "__main__":
    main()
