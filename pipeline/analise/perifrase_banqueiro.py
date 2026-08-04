"""O credor externo quando o texto NAO o nomeia.

Motivo de existir, medido: a Gazeta de Noticias de 1906 (ed. 282) chama
Rothschild de "o rei dos banqueiros londrinos", sem nomea-lo. Nenhuma regra de
nome proprio casa isso. Como o casamento por nome ja perde metade das
ocorrencias so por ruido de OCR, e depois perde de novo tudo o que a lingua
diz por perifrase e por cargo, uma medida que so conte nome subestima o credor
externo por duas vias somadas.

ESTATUTO: varredura de CANDIDATOS A LEITURA, no mesmo patamar da sondagem de
banqueiros de 26/07. Nao e instrumento e nao mede nada sozinha. A razao e
estrutural, nao de calibracao: "nossos credores" pode ser credor nacional,
"capitalistas estrangeiros" e classe e nao pessoa, e "casa bancaria" designa
tanto Rothschild quanto um banco da rua da Alfandega. So a leitura da pagina
resolve o referente, e por isso cada padrao carrega um campo `confianca`
declarado antes de olhar resultado.

Os padroes vivem em `padroes_perifrase_banqueiro.csv`, versionados, um por
linha com familia, expressao, confianca e justificativa. Acrescentar padrao e
mudanca de instrumento de busca e exige registro em docs/decisoes.md.

Recall e desconhecido e nao ha como estima-lo por dentro: nao existe lista
fechada das formas que a lingua de 1906 usava para dizer credor. O que a
varredura garante e piso, nunca censo.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from pipeline.analise.nomes_no_debate import BIBS, mencoes_em, paginas_com_mencao
from pipeline.triagem import regra_nome

PROTOCOL_NAME = "perifrase-banqueiro-externo"
PROTOCOL_VERSION = "0.1.0"

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
PADROES_PADRAO = AQUI / "padroes_perifrase_banqueiro.csv"

CONFIANCAS = frozenset({"alta", "media", "baixa"})


@dataclass(frozen=True, slots=True)
class Padrao:
    familia: str
    expressao: str
    confianca: str
    justificativa: str
    regex: re.Pattern[str]


def carrega_padroes(caminho: Path = PADROES_PADRAO) -> tuple[Padrao, ...]:
    padroes: list[Padrao] = []
    vistos: set[str] = set()
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            expressao = linha["padrao"].strip()
            if not expressao:
                continue
            if expressao in vistos:
                raise ValueError(f"padrao repetido: {expressao}")
            vistos.add(expressao)
            confianca = linha["confianca"].strip()
            if confianca not in CONFIANCAS:
                raise ValueError(f"confianca invalida em {expressao!r}: {confianca!r}")
            if not linha["justificativa"].strip():
                raise ValueError(f"padrao sem justificativa: {expressao}")
            padroes.append(
                Padrao(
                    familia=linha["familia"].strip(),
                    expressao=expressao,
                    confianca=confianca,
                    justificativa=linha["justificativa"].strip(),
                    regex=re.compile(expressao),
                )
            )
    if not padroes:
        raise ValueError("lista de padroes vazia")
    return tuple(padroes)


def encontra(texto: str, padroes: Sequence[Padrao]) -> list[tuple[Padrao, int, str]]:
    """Ocorrencias no texto JA normalizado, em ordem de posicao.

    Um mesmo trecho pode casar mais de um padrao ("rei dos banqueiros
    londrinos" casa realeza_bancaria e banqueiro_estrangeiro). As duas ficam,
    porque suprimir uma esconderia qual familia achou o caso.
    """
    achados: list[tuple[Padrao, int, str]] = []
    for padrao in padroes:
        for casado in padrao.regex.finditer(texto):
            achados.append((padrao, casado.start(), casado.group(0)))
    achados.sort(key=lambda item: (item[1], item[0].familia))
    return achados


def distancia_ate_mencao(posicao: int, mencoes: Iterable[int]) -> int:
    lista = list(mencoes)
    if not lista:
        raise ValueError("pagina sem mencao da Caixa")
    return min(abs(posicao - m) for m in lista)


def main() -> None:  # pragma: no cover - orquestracao com I/O
    import time
    from collections import Counter

    inicio = time.time()
    padroes = carrega_padroes()
    print(f"padroes: {len(padroes)} em {len({p.familia for p in padroes})} familias")

    registros: list[dict] = []
    paginas = 0
    for bib, ano, objeto, pagina, caminho in paginas_com_mencao():
        bruto = caminho.read_text(encoding="utf-8", errors="replace")
        texto = regra_nome.normaliza(bruto)
        mencoes = mencoes_em(texto)
        if not mencoes:
            continue
        paginas += 1
        for padrao, posicao, trecho in encontra(texto, padroes):
            distancia = distancia_ate_mencao(posicao, mencoes)
            ini = max(0, posicao - 220)
            fim = min(len(texto), posicao + 260)
            registros.append(
                {
                    "bib": bib,
                    "jornal": BIBS.get(bib, bib),
                    "ano": ano,
                    "objeto": objeto,
                    "pagina": pagina,
                    "familia": padrao.familia,
                    "padrao": padrao.expressao,
                    "confianca": padrao.confianca,
                    "trecho_casado": trecho,
                    "distancia_minima": distancia,
                    "contexto": texto[ini:fim],
                }
            )

    destino = RAIZ / "dados" / "analise" / "perifrase_banqueiro.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=list(registros[0]), lineterminator="\n"
        )
        escritor.writeheader()
        escritor.writerows(registros)

    print(f"{paginas} paginas varridas, {len(registros)} ocorrencias, "
          f"{time.time() - inicio:.0f}s")
    print(f"paginas distintas com alguma perifrase: "
          f"{len({(r['objeto'], r['pagina']) for r in registros})}")

    print("\npor familia (ocorrencias | paginas | a <=200 chars da mencao):")
    for familia in sorted({r["familia"] for r in registros}):
        alvo = [r for r in registros if r["familia"] == familia]
        perto = [r for r in alvo if r["distancia_minima"] <= 200]
        print(f"  {familia:24s} {len(alvo):6d} | "
              f"{len({(r['objeto'], r['pagina']) for r in alvo}):5d} | {len(perto):5d}")

    print("\npor confianca do padrao:")
    for confianca in ("alta", "media", "baixa"):
        alvo = [r for r in registros if r["confianca"] == confianca]
        perto = [r for r in alvo if r["distancia_minima"] <= 200]
        print(f"  {confianca:6s} {len(alvo):6d} ocorrencias, {len(perto):5d} a <=200")

    print("\npor ano (ocorrencias a <=1000 chars):")
    perto = Counter(r["ano"] for r in registros if r["distancia_minima"] <= 1000)
    for ano in sorted(perto):
        print(f"  {ano}: {perto[ano]}")

    print("\ntrechos casados mais frequentes:")
    for trecho, n in Counter(r["trecho_casado"] for r in registros).most_common(25):
        print(f"  {n:5d}  {trecho}")

    print(f"\nmanifesto: {destino}")


if __name__ == "__main__":  # pragma: no cover
    main()
