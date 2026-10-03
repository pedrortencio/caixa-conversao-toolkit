"""Inspeção da sonda difusa: da contagem de máquina para a taxa de falha lida.

A sonda difusa devolve uma contagem: quantas páginas que o censo descartou
trazem forma parecida com "Caixa de Conversão". Contagem de máquina não é taxa
de falso negativo, porque a sonda também acerta ruído: `caixa de convenio`,
`caixas de conserva`, um `conver` de outra palavra a dois caracteres de um
`caixa` que fala de outra coisa. Precisão se mede lendo, não presumindo.

Este módulo faz os dois passos do meio:

1. **Sorteio.** Amostra determinística, com semente registrada, estratificada
   por distância de edição, para que a precisão saia por faixa e o limiar possa
   ser escolhido com número, não com impressão.
2. **Apuração.** Proporção de achados genuínos por faixa, com intervalo de
   Wilson. Wilson e não a normal porque a proporção esperada encosta em 1 e a
   aproximação normal produz teto acima de 1 e piso negativo, que é exatamente
   a região onde a leitura vai cair.

O julgamento em si é humano e vai na coluna `genuina` do CSV sorteado: 1 quando
o trecho é menção à Caixa de Conversão apesar do OCR, 0 quando não é, vazio
enquanto não foi lido. Linha não lida é contada à parte, nunca tratada como 0:
ausência não é inferida do silêncio.

Uso:
  uv run python -m pipeline.triagem.inspeciona_sonda --sorteia --por-estrato 40
  uv run python -m pipeline.triagem.inspeciona_sonda --apura
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - conveniência de execução direta
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

PROTOCOLO = "inspecao-sonda-difusa"
VERSAO = "1.0.0"

RAIZ = Path(__file__).resolve().parents[2]
DIR_SONDA = RAIZ / "dados" / "triagem" / "sonda_difusa"

#: Semente do sorteio. Fixa e registrada: trocar a semente é trocar a amostra,
#: e amostra trocada depois de ver o resultado é seleção, não medição.
SEMENTE = 20260812

Z95 = 1.959963984540054

CHAVE_ORDEM = ("distancia", "bib", "source_identifier", "page_number", "offset")


def _chave(linha: dict) -> tuple:
    return tuple(linha[campo] for campo in CHAVE_ORDEM if campo in linha)


def amostra_determinista(
    linhas: list[dict], tamanho: int, semente: int = SEMENTE
) -> list[dict]:
    """Amostra sem reposição, reprodutível e independente da ordem de entrada.

    A população é ordenada pela chave de identificação antes do sorteio: assim
    a amostra depende só da semente e do conteúdo, e não de como o CSV veio
    do disco.
    """
    populacao = sorted(linhas, key=_chave)
    if tamanho >= len(populacao):
        return populacao
    indices = random.Random(semente).sample(range(len(populacao)), tamanho)
    return [populacao[i] for i in sorted(indices)]


def amostra_estratificada(
    linhas: list[dict], por_estrato: int, semente: int = SEMENTE
) -> list[dict]:
    """Cota igual por faixa de distância, para medir precisão faixa a faixa.

    Proporcional seria pior aqui: a faixa de distância 0 e 1 domina a contagem,
    e é justamente a faixa de que menos se duvida. O que decide o limiar é a
    precisão nas faixas raras, que uma amostra proporcional quase não veria.
    """
    estratos: dict[int, list[dict]] = {}
    for linha in linhas:
        estratos.setdefault(int(linha["distancia"]), []).append(linha)
    amostra: list[dict] = []
    for distancia in sorted(estratos):
        amostra += amostra_determinista(
            estratos[distancia], por_estrato, semente + distancia
        )
    return sorted(amostra, key=_chave)


def wilson(acertos: int, total: int, z: float = Z95) -> tuple[float, float]:
    """Intervalo de Wilson para uma proporção. `(0.0, 1.0)` para total zero."""
    if total <= 0:
        return (0.0, 1.0)
    proporcao = acertos / total
    denominador = 1 + z * z / total
    centro = (proporcao + z * z / (2 * total)) / denominador
    meia = (
        z
        * math.sqrt(proporcao * (1 - proporcao) / total + z * z / (4 * total * total))
        / denominador
    )
    return (round(max(0.0, centro - meia), 4), round(min(1.0, centro + meia), 4))


def apura(julgadas: list[dict]) -> dict:
    """Precisão por faixa de distância e agregada, a partir do que foi lido."""
    por_distancia: dict[str, dict] = {}
    nao_lidas = 0
    lidas_total = 0
    genuinas_total = 0

    for linha in julgadas:
        veredito = str(linha.get("genuina", "")).strip()
        if veredito == "":
            nao_lidas += 1
            continue
        if veredito not in {"0", "1"}:
            raise ValueError(
                f"julgamento fora do vocabulário: {veredito!r}. Use 1, 0 ou vazio."
            )
        chave = str(linha["distancia"])
        faixa = por_distancia.setdefault(chave, {"lidas": 0, "genuinas": 0})
        faixa["lidas"] += 1
        faixa["genuinas"] += veredito == "1"
        lidas_total += 1
        genuinas_total += veredito == "1"

    for faixa in por_distancia.values():
        faixa["precisao"] = round(faixa["genuinas"] / faixa["lidas"], 4)
        faixa["ic95"] = wilson(faixa["genuinas"], faixa["lidas"])

    return {
        "protocol_name": PROTOCOLO,
        "protocol_version": VERSAO,
        "semente": SEMENTE,
        "por_distancia": {
            chave: por_distancia[chave] for chave in sorted(por_distancia, key=int)
        },
        "total": {
            "lidas": lidas_total,
            "genuinas": genuinas_total,
            "precisao": (
                round(genuinas_total / lidas_total, 4) if lidas_total else None
            ),
            "ic95": wilson(genuinas_total, lidas_total),
        },
        "nao_lidas": nao_lidas,
    }


def buckets_por_distancia(celula: dict) -> dict[int, int]:
    """Desfaz o cumulativo `paginas_dN` em contagem exata por melhor distância.

    A célula guarda o cumulativo porque é o que se lê direto; a estimativa
    precisa da faixa exata, porque cada faixa tem precisão própria.
    """
    cumulativo = {
        int(chave.removeprefix("paginas_d")): int(valor)
        for chave, valor in celula.items()
        if chave.startswith("paginas_d")
    }
    buckets: dict[int, int] = {}
    anterior = 0
    for distancia in sorted(cumulativo):
        buckets[distancia] = cumulativo[distancia] - anterior
        anterior = cumulativo[distancia]
    return buckets


def estima_falsos_negativos(
    celulas: list[dict], apuracao: dict, limiar: int
) -> dict:
    """Páginas sinalizadas pela sonda, corrigidas pela precisão lida em cada faixa.

    A correção é necessária porque a sonda também acerta ruído, e o ruído não
    se distribui igual entre as faixas: `caixas de conservas` cai quase toda em
    distância 4 e 6, enquanto distância 1 e 2 é praticamente só menção de
    verdade. Aplicar uma precisão média a todas as faixas trocaria uma medida
    por uma impressão.

    A página é atribuída à faixa da sua MELHOR distância, e recebe a precisão
    daquela faixa. É um estimador conservador: ignora que uma página cujo
    melhor candidato é ruído possa ter um segundo candidato genuíno.

    Faixa que ninguém leu não entra na conta nem como zero nem como um: sai
    contada à parte em `paginas_sem_precisao_medida`, porque inventar a
    precisão de uma faixa não inspecionada é exatamente o tipo de silêncio que
    o projeto trata como ausência registrada.

    Só o braço `hit_censo == 0` entra: falso negativo é, por definição, o que
    o censo descartou.
    """
    precisoes = apuracao["por_distancia"]
    saida_celulas: list[dict] = []
    sem_precisao_total = 0

    for celula in celulas:
        if int(celula["hit_censo"]) != 0:
            continue
        buckets = buckets_por_distancia(celula)
        sinalizadas = 0
        estimadas = 0.0
        baixo = 0.0
        alto = 0.0
        sem_precisao = 0
        for distancia, paginas in sorted(buckets.items()):
            if distancia > limiar or paginas == 0:
                continue
            sinalizadas += paginas
            faixa = precisoes.get(str(distancia))
            if faixa is None:
                sem_precisao += paginas
                continue
            estimadas += paginas * faixa["precisao"]
            baixo += paginas * faixa["ic95"][0]
            alto += paginas * faixa["ic95"][1]
        sem_precisao_total += sem_precisao
        saida_celulas.append(
            {
                "bib": celula["bib"],
                "jornal": celula["jornal"],
                "ano": int(celula["ano"]),
                "paginas_examinadas": int(celula["paginas"]),
                "paginas_sinalizadas": sinalizadas,
                "paginas_estimadas": round(estimadas, 1),
                "estimadas_ic95": (round(baixo, 1), round(alto, 1)),
                "paginas_sem_precisao_medida": sem_precisao,
                "taxa_estimada": (
                    round(estimadas / int(celula["paginas"]), 5)
                    if int(celula["paginas"])
                    else None
                ),
            }
        )

    examinadas = sum(c["paginas_examinadas"] for c in saida_celulas)
    estimadas = sum(c["paginas_estimadas"] for c in saida_celulas)
    return {
        "limiar": limiar,
        "celulas": sorted(
            saida_celulas, key=lambda c: (c["bib"], c["ano"])
        ),
        "total": {
            "paginas_examinadas": examinadas,
            "paginas_sinalizadas": sum(
                c["paginas_sinalizadas"] for c in saida_celulas
            ),
            "paginas_estimadas": round(estimadas, 1),
            "estimadas_ic95": (
                round(sum(c["estimadas_ic95"][0] for c in saida_celulas), 1),
                round(sum(c["estimadas_ic95"][1] for c in saida_celulas), 1),
            ),
            "paginas_sem_precisao_medida": sem_precisao_total,
            "taxa_estimada": (
                round(estimadas / examinadas, 5) if examinadas else None
            ),
        },
    }


# --- execução --------------------------------------------------------------

CAMPOS_AMOSTRA = [
    "genuina", "distancia", "bib", "jornal", "ano", "source_identifier",
    "page_number", "offset", "trecho", "contexto",
]


def carrega_candidatos(caminho: Path, limiar: int) -> list[dict]:
    """Candidatos das páginas SEM menção no censo, até o limiar."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return [
            linha
            for linha in csv.DictReader(arquivo)
            if linha["hit_censo"] == "0" and int(linha["distancia"]) <= limiar
        ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sorteia", action="store_true")
    parser.add_argument("--apura", action="store_true")
    parser.add_argument("--por-estrato", type=int, default=40)
    parser.add_argument("--limiar", type=int, default=8)
    parser.add_argument("--semente", type=int, default=SEMENTE)
    parser.add_argument("--dir", type=Path, default=DIR_SONDA)
    args = parser.parse_args(argv)

    amostra_csv = args.dir / "amostra_inspecao.csv"

    if args.sorteia:
        candidatos = carrega_candidatos(args.dir / "candidatos.csv", args.limiar)
        amostra = amostra_estratificada(candidatos, args.por_estrato, args.semente)
        with open(amostra_csv, "w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.DictWriter(
                arquivo, fieldnames=CAMPOS_AMOSTRA, extrasaction="ignore"
            )
            escritor.writeheader()
            for linha in amostra:
                escritor.writerow({**linha, "genuina": ""})
        print(f"{len(amostra)} linhas sorteadas em {amostra_csv} (semente {args.semente})")

    if args.apura:
        with open(amostra_csv, encoding="utf-8", newline="") as arquivo:
            julgadas = list(csv.DictReader(arquivo))
        apuracao = apura(julgadas)
        apuracao["semente"] = args.semente
        with open(args.dir / "celulas.csv", encoding="utf-8", newline="") as arquivo:
            celulas = list(csv.DictReader(arquivo))
        apuracao["estimativa_de_falsos_negativos"] = {
            str(corte): estima_falsos_negativos(celulas, apuracao, corte)
            for corte in (2, 3, 5)
        }
        apuracao["advertencia"] = (
            "Precisão medida por leitura de uma amostra, por um modelo de "
            "linguagem, não pelo Pedro. É conferível no CSV sorteado e não "
            "substitui julgamento humano. Concordância entre dois leitores da "
            "mesma imagem degradada não é verdade."
        )
        destino = args.dir / "apuracao_inspecao.json"
        destino.write_text(
            json.dumps(apuracao, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(apuracao, ensure_ascii=False, indent=2))
        print(f"apuração em {destino}")

    if not (args.sorteia or args.apura):
        parser.error("escolha --sorteia ou --apura")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
