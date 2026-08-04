"""Os mesmos padroes de perifrase, aplicados aos Documentos Parlamentares.

Motivo de existir, medido em 03/08: nos dois volumes, 1.152 paginas,
Rothschild, Speyer, Baring, Schroder e Credit Lyonnais somam ZERO mencao pelo
nome. Na imprensa, porem, 418 das 8.331 paginas designam o credor sem nomear,
contra 132 que nomeiam sem designar. A perifrase derrota a busca por nome por
uma margem grande, entao o silencio parlamentar so vale como achado depois de
rodar sobre esses volumes a mesma varredura que a imprensa recebeu. Sem isso,
o zero pode ser artefato do instrumento e nao propriedade da fonte.

Diferenca de desenho em relacao a `perifrase_banqueiro`: la a pagina de jornal
mistura debate, boletim, turfe e anuncio, e por isso cada achado carrega a
distancia ate a mencao mais proxima da Caixa. Aqui o volume inteiro E o debate,
como ja registrado em `nomes_parlamentares`, entao nao ha filtro de distancia e
nenhum achado e descartado por estar longe.

ESTATUTO: varredura de CANDIDATOS A LEITURA, o mesmo da varredura na imprensa.
Nao e instrumento e nao mede nada sozinha, porque `nossos credores` pode ser
credor nacional, `capitalistas estrangeiros` e classe e nao pessoa, e `casa
bancaria` designa tanto Rothschild quanto um banco da rua da Alfandega. So a
leitura da pagina resolve o referente.

Insumo: a camada corrigida, que hoje e produto sem instrumento (a rotina que a
gerou nao esta no repo, ver docs/auditoria-da-base-2026-08-03.md, secao 2.1).
Nenhum numero daqui entra em texto antes de a rotina existir e o replay passar.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from pipeline.analise.nomes_parlamentares import carrega_volume
from pipeline.analise.perifrase_banqueiro import Padrao, carrega_padroes, encontra

PROTOCOL_NAME = "perifrase-parlamentar"
PROTOCOL_VERSION = "0.1.0"

RAIZ = Path(__file__).resolve().parents[2]

# Volume 1 e o debate de 1906 (criacao), volume 2 o de 1910 (taxa de 16
# dinheiros). Sao dois cortes no tempo, nao uma serie.
VOLUMES = {1: "1906_criacao", 2: "1910_taxa_16d"}


def varre_volume(
    paginas: list[tuple[int, str]], volume: int, padroes: tuple[Padrao, ...]
) -> list[dict]:
    """Uma linha por ocorrencia, com contexto de 480 chars em torno do casamento.

    A janela e a mesma da varredura na imprensa, para que os dois manifestos
    possam ser lidos lado a lado sem correcao de escala.
    """
    registros: list[dict] = []
    for numero, texto in paginas:
        for padrao, posicao, trecho in encontra(texto, padroes):
            ini = max(0, posicao - 220)
            fim = min(len(texto), posicao + 260)
            registros.append(
                {
                    "volume": volume,
                    "corte": VOLUMES[volume],
                    "pdf_page": numero,
                    "familia": padrao.familia,
                    "padrao": padrao.expressao,
                    "confianca": padrao.confianca,
                    "trecho_casado": trecho,
                    "posicao": posicao,
                    "contexto": texto[ini:fim],
                }
            )
    return registros


def main() -> None:  # pragma: no cover - orquestracao com I/O
    padroes = carrega_padroes()
    print(f"padroes: {len(padroes)} em {len({p.familia for p in padroes})} familias")

    registros: list[dict] = []
    total_paginas = 0
    for volume in VOLUMES:
        paginas = carrega_volume(volume)
        total_paginas += len(paginas)
        achados = varre_volume(paginas, volume, padroes)
        registros.extend(achados)
        distintas = len({r["pdf_page"] for r in achados})
        print(
            f"volume {volume} ({VOLUMES[volume]}): {len(paginas)} paginas, "
            f"{len(achados)} ocorrencias em {distintas} paginas distintas"
        )

    destino = RAIZ / "dados" / "analise" / "perifrase_parlamentar.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="") as arquivo:
        campos = [
            "volume", "corte", "pdf_page", "familia", "padrao", "confianca",
            "trecho_casado", "posicao", "contexto",
        ]
        escritor = csv.DictWriter(arquivo, fieldnames=campos, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(registros)

    print(f"\ntotal: {total_paginas} paginas varridas, {len(registros)} ocorrencias em "
          f"{len({(r['volume'], r['pdf_page']) for r in registros})} paginas distintas")

    print("\npor familia (ocorrencias | paginas | v1 1906 | v2 1910):")
    for familia in sorted({r["familia"] for r in registros}):
        alvo = [r for r in registros if r["familia"] == familia]
        v1 = sum(1 for r in alvo if r["volume"] == 1)
        print(f"  {familia:24s} {len(alvo):5d} | "
              f"{len({(r['volume'], r['pdf_page']) for r in alvo}):5d} | "
              f"{v1:5d} | {len(alvo) - v1:5d}")

    print("\npor confianca do padrao:")
    for confianca in ("alta", "media", "baixa"):
        alvo = [r for r in registros if r["confianca"] == confianca]
        print(f"  {confianca:6s} {len(alvo):5d} ocorrencias em "
              f"{len({(r['volume'], r['pdf_page']) for r in alvo}):4d} paginas")

    print("\ntrechos casados mais frequentes:")
    for trecho, n in Counter(r["trecho_casado"] for r in registros).most_common(25):
        print(f"  {n:5d}  {trecho}")

    resumo = {
        "protocolo": PROTOCOL_NAME,
        "versao": PROTOCOL_VERSION,
        "paginas_varridas": total_paginas,
        "ocorrencias": len(registros),
        "paginas_com_perifrase": len({(r["volume"], r["pdf_page"]) for r in registros}),
        "por_familia": {
            f: sum(1 for r in registros if r["familia"] == f)
            for f in sorted({r["familia"] for r in registros})
        },
        "por_volume": {
            str(v): sum(1 for r in registros if r["volume"] == v) for v in VOLUMES
        },
    }
    resumo_destino = RAIZ / "dados" / "analise" / "perifrase_parlamentar_resumo.json"
    resumo_destino.write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nmanifesto: {destino}\nresumo: {resumo_destino}")


if __name__ == "__main__":  # pragma: no cover
    main()
