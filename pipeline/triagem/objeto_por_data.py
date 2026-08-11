"""Resolve "que objeto e a edicao de tal dia" sem depender do masthead do dia.

O problema, medido no piloto de 11/08/2026. A base nao mapeia data para objeto:
`edition_days` tem 67 linhas para 11.960 objetos. E o caminho obvio, ler a data
no masthead da pagina 1, e moeda ao ar:

| jornal              | objetos | data no OCR | e o ano confere |
|---------------------|---------|-------------|-----------------|
| Correio da Manha    |   3.238 |       64,4% |           51,5% |
| O Paiz              |   3.086 |       62,9% |           50,4% |
| Correio Paulistano  |   3.128 |       43,2% |           31,3% |
| Gazeta de Noticias  |   2.505 |       33,3% |           21,8% |

Duas observacoes sustentam este modulo.

A primeira: o ano impresso e a parte MENOS confiavel do masthead, e nao e
preciso. `per103730_1912_00017` traz `dé 1913`, e `per103730_1912_00016` traz
`de i91S`. O ano ja esta no nome do objeto. Por isso o parser daqui le dia e
mes, e ignora o ano impresso, ao contrario de `parse_observed_date` em
`pipeline/base/carrega_piloto.py`, que exige o ano e esta fixado em 1906.

A segunda: o numero do objeto e o numero da edicao, e edicoes sao contiguas no
tempo. Entao uma ancora legivel de cada lado do alvo resolve por aritmetica,
mesmo que a pagina do alvo esteja ilegivel. Foi assim que a data do editorial da
Gazeta sobre as retiradas se fixou em 17 de janeiro de 1912, contra os 15 que o
rascunho da dissertacao registrava: `00016` traz terca-feira 16, `00018` traz
18, e o calendario confirma que 17 caiu numa quarta.

A guarda: a aritmetica so vale se o intervalo de NUMEROS bater com o intervalo
de DIAS entre as duas ancoras. Quando nao bate houve dia sem edicao no meio, a
contagem deixa de ser exata, e a resolucao sai como `incerto` em vez de sair
errada com cara de certa. `incerto` traz o candidato mais provavel e diz por que
duvida, e nunca deve ser gravado como se fosse `masthead`.

Estatuto: recuperacao com proveniencia, do objeto 1. Nao seleciona, nao descarta
e nao estrutura informacao segundo o construto.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

TEXTO = Path("C:/dados-caixa/texto_embutido")

BIBS = {
    "o-paiz": "178691",
    "correio-da-manha": "089842",
    "correio-paulistano": "090972",
    "gazeta-de-noticias": "103730",
}

MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

# O dia tem de vir colado ao mes, com no maximo um `de` de permeio. Sem essa
# ancora o padrao casa qualquer numero solto da pagina com qualquer mes citado
# numa materia, e o masthead de um diario de 1906 tem numero solto de sobra.
_DATA = re.compile(
    rf"\b(?P<dia>[0-3]?\d)\s+(?:de\s+)?(?P<mes>{'|'.join(MESES)})\b",
    re.IGNORECASE,
)

_LINHAS_DE_MASTHEAD = 12


def normaliza(texto: str) -> str:
    """Tira acento e caixa, que o OCR perde de forma arbitraria."""
    nfkd = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def parse_dia_mes(texto: str) -> tuple[int, int] | None:
    """Dia e mes do masthead. O ano NAO sai daqui, de proposito.

    Devolve `None` quando nao ha data legivel, o que e frequente e esperado: em
    dois dos quatro jornais isso acontece na maioria das paginas.
    """
    achado = _DATA.search(normaliza(texto))
    if not achado:
        return None
    dia, mes = int(achado.group("dia")), MESES[achado.group("mes")]
    if not 1 <= dia <= 31:
        return None
    return dia, mes


def numero_do_objeto(objeto: str) -> int:
    """`per103730_1912_00017` vale 17. E o numero da edicao no ano."""
    return int(objeto.rsplit("_", 1)[1])


def ano_do_objeto(objeto: str) -> int:
    return int(objeto.rsplit("_", 2)[1])


@dataclass(frozen=True, slots=True)
class Resolucao:
    objeto: str | None
    metodo: str
    evidencia: str


def _data_valida(ano: int, mes: int, dia: int) -> date | None:
    try:
        return date(ano, mes, dia)
    except ValueError:
        return None


def indexa(bib: str, anos: range | list[int], raiz: Path = TEXTO) -> dict[str, date]:
    """Le a pagina 1 de cada objeto e devolve so as datas que o OCR entregou.

    Ausencia nao e inferida: objeto sem data legivel simplesmente nao entra no
    indice, e e do indice esburacado que a resolucao por vizinhos parte.
    """
    indice: dict[str, date] = {}
    pasta = raiz / bib
    if not pasta.is_dir():
        return indice
    for objeto in sorted(p.name for p in pasta.iterdir() if p.is_dir()):
        ano = ano_do_objeto(objeto)
        if ano not in anos:
            continue
        pagina = pasta / objeto / "p001.txt"
        if not pagina.is_file():
            continue
        cabeca = "\n".join(
            pagina.read_text(encoding="utf-8", errors="replace").splitlines()[:_LINHAS_DE_MASTHEAD]
        )
        lido = parse_dia_mes(cabeca)
        if lido is None:
            continue
        quando = _data_valida(ano, lido[1], lido[0])
        if quando is not None:
            indice[objeto] = quando
    return indice


def espinha(indice: dict[str, date]) -> dict[str, date]:
    """A maior cadeia de objetos em que numero e data crescem juntos.

    Leitura isolada de masthead nao merece confianca. Medido em 1910: 16,4% das
    datas lidas em O Paiz sao falsas, 19,5% na Gazeta e 31,3% no Correio
    Paulistano, porque o padrao de data casa com uma data citada dentro de uma
    materia que caiu nas primeiras linhas da pagina. `per178691_1910_09223` saiu
    como 30 de dezembro entre vizinhos de 5 e 7 de janeiro.

    O acervo, porem, e ordenado: o numero do objeto e o numero da edicao. Entao
    a data verdadeira pertence a uma cadeia crescente e a falsa nao cabe nela.
    Guardar a maior cadeia crescente descarta o ruido por construcao, sem limiar
    arbitrario e sem decidir caso a caso. Empate escolhe a cadeia encontrada
    primeiro, que e deterministica dada a ordenacao por numero.
    """
    import bisect

    itens = sorted(indice.items(), key=lambda kv: numero_do_objeto(kv[0]))
    if not itens:
        return {}
    # Patience sorting: `pontas[k]` guarda o indice do ultimo item da melhor
    # cadeia de comprimento k+1 conhecida ate agora.
    pontas: list[int] = []
    datas_das_pontas: list[date] = []
    anterior: list[int | None] = [None] * len(itens)
    for i, (_, quando) in enumerate(itens):
        k = bisect.bisect_left(datas_das_pontas, quando)
        anterior[i] = pontas[k - 1] if k else None
        if k == len(pontas):
            pontas.append(i)
            datas_das_pontas.append(quando)
        else:
            pontas[k] = i
            datas_das_pontas[k] = quando
    cadeia: list[int] = []
    atual: int | None = pontas[-1]
    while atual is not None:
        cadeia.append(atual)
        atual = anterior[atual]
    return {itens[i][0]: itens[i][1] for i in reversed(cadeia)}


def resolve(alvo: date, indice: dict[str, date]) -> Resolucao:
    """Qual objeto e a edicao de `alvo`, e com que grau de certeza."""
    do_ano = espinha({o: d for o, d in indice.items() if d.year == alvo.year})
    if not do_ano:
        return Resolucao(None, "sem_ancora", "nenhuma data legivel neste ano")

    for objeto, quando in do_ano.items():
        if quando == alvo:
            return Resolucao(objeto, "masthead", f"data legivel no masthead de {objeto}")

    # Ordenar por DATA, e nao por numero do objeto. Em O Paiz o numero nao cresce
    # com a data, e fatiar uma lista ordenada por numero devolve a ultima ancora
    # em ordem de numero em vez da mais proxima em data: medido em 1910, com 141
    # datas legiveis no ano, isso escolhia 5 de fevereiro e 30 de dezembro para
    # cercar 14 de maio.
    por_data = sorted(do_ano.items(), key=lambda kv: kv[1])
    antes = [(o, d) for o, d in por_data if d < alvo]
    depois = [(o, d) for o, d in por_data if d > alvo]
    if not antes or not depois:
        lado = "so ha ancora depois do alvo" if depois else "so ha ancora antes do alvo"
        candidato = depois[0] if depois else antes[-1]
        return Resolucao(_extrapola(alvo, candidato), "incerto", lado)

    obj_a, data_a = antes[-1]
    obj_b, data_b = depois[0]
    passo_numero = numero_do_objeto(obj_b) - numero_do_objeto(obj_a)
    passo_dias = (data_b - data_a).days
    evidencia = (
        f"{obj_a} traz {data_a.isoformat()} e {obj_b} traz {data_b.isoformat()}; "
        f"{passo_numero} edicoes para {passo_dias} dias"
    )
    numero = numero_do_objeto(obj_a) + (alvo - data_a).days
    candidato = _reescreve(obj_a, numero)
    if passo_numero != passo_dias:
        return Resolucao(
            candidato,
            "incerto",
            evidencia + ", houve dia sem edicao entre as ancoras e a contagem nao e exata",
        )
    return Resolucao(candidato, "vizinhos", evidencia)


def _reescreve(modelo: str, numero: int) -> str:
    prefixo, _ = modelo.rsplit("_", 1)
    return f"{prefixo}_{numero:05d}"


def _extrapola(alvo: date, ancora: tuple[str, date]) -> str:
    objeto, quando = ancora
    return _reescreve(objeto, numero_do_objeto(objeto) + (alvo - quando).days)


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - linha de comando
    parser = argparse.ArgumentParser(description="Resolve o objeto digital de uma data")
    parser.add_argument("jornal", choices=sorted(BIBS), help="slug do periodico")
    parser.add_argument("data", help="data alvo, AAAA-MM-DD")
    parser.add_argument("--raiz", default=str(TEXTO))
    args = parser.parse_args(argv)

    alvo = date.fromisoformat(args.data)
    bib = BIBS[args.jornal]
    indice = indexa(bib, [alvo.year], Path(args.raiz))
    print(f"{len(indice)} datas legiveis em {args.jornal} {alvo.year}")
    r = resolve(alvo, indice)
    print(f"objeto   : {r.objeto}")
    print(f"metodo   : {r.metodo}")
    print(f"evidencia: {r.evidencia}")
    if r.metodo == "incerto":
        print("\nNAO grave como data confirmada. Confira o masthead na imagem.")
    return 0 if r.objeto else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
