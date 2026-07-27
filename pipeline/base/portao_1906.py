r"""Portão de 1906: o critério vigente, do pré-registro de 2026-07-18.

Pré-registro em `docs/decisoes.md`, entrada de 2026-07-18, item 3. Ele
SUBSTITUI o critério antigo (gabarito do piloto como subconjunto simples do
censo), que reprovava sem dar estado formal aos 4 faltantes confirmados fora
das duas rotas verificadas. `relatorio_censo.regressao_1906` continua sendo a
contagem crua, e é insumo deste módulo, não mais o veredito.

Critério: todo item do gabarito do piloto recebe exatamente uma classe.

  - `unidade_canonica`        reproduzida pelo censo (varredura ou recuperação)
  - `manifestacao_coalescida` coalescida em uma edição-dia canônica
  - `excecao_terminal`        ausência documentada com fonte

Nenhum item pode ficar inexplicado, e a lista de exceções **exige aprovação
expressa de Pedro**. Lista sem aprovação não explica nada: é o que impede que
uma ausência inconveniente vire exceção no meio de uma sessão apressada.

Guardrail que este módulo serve (CLAUDE.md): nunca rodar lote pago de API sem
antes passar o portão de 1906.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from pipeline.base.relatorio_censo import (
    DIR_CENSO,
    Gabarito,
    _numeros_ok,  # fonte única do que conta como "ok" no censo
    gabarito_piloto,
)

CLASSES_VALIDAS = frozenset(
    {"unidade_canonica", "manifestacao_coalescida", "excecao_terminal"}
)

RAIZ_REPO = Path(__file__).resolve().parents[2]
MANIFESTO_PADRAO = (
    RAIZ_REPO / "pipeline" / "base" / "manifests" / "excecoes_portao_1906.json"
)


@dataclass(frozen=True, slots=True)
class ListaExcecoes:
    aprovado_por: str | None
    aprovado_em: str | None
    itens: dict[tuple[str, int], str]

    @property
    def aprovada(self) -> bool:
        return bool(self.aprovado_por)


@dataclass(frozen=True, slots=True)
class ResultadoPortao:
    reproduzidos: int
    excecoes_aceitas: tuple[tuple[str, int], ...]
    inexplicados: tuple[tuple[str, int], ...]
    lista_aprovada: bool
    aprovado_por: str | None

    @property
    def aprovado(self) -> bool:
        return not self.inexplicados


def carrega_excecoes(caminho: Path = MANIFESTO_PADRAO) -> ListaExcecoes:
    """Lê o manifesto de exceções. Ausência de arquivo é lista vazia, não erro."""
    if not caminho.exists():
        return ListaExcecoes(aprovado_por=None, aprovado_em=None, itens={})
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    itens: dict[tuple[str, int], str] = {}
    for item in dados.get("excecoes", []):
        classe = str(item.get("classe", ""))
        fonte = str(item.get("fonte", "")).strip()
        # "Exceção terminal documentada com fonte": sem classe válida ou sem
        # fonte, o item não explica nada e volta a contar como inexplicado.
        if classe not in CLASSES_VALIDAS or not fonte:
            continue
        itens[(str(item["bib"]), int(item["numero"]))] = classe
    return ListaExcecoes(
        aprovado_por=dados.get("aprovado_por"),
        aprovado_em=dados.get("aprovado_em"),
        itens=itens,
    )


def avalia(
    gabarito: dict[str, Gabarito],
    dir_censo: Path = DIR_CENSO,
    caminho_excecoes: Path = MANIFESTO_PADRAO,
) -> ResultadoPortao:
    lista = carrega_excecoes(caminho_excecoes)
    reproduzidos = 0
    aceitas: list[tuple[str, int]] = []
    inexplicados: list[tuple[str, int]] = []

    for bib, itens in sorted(gabarito.items()):
        oks = _numeros_ok(dir_censo, bib, 1906)
        for numero in sorted(itens.numeros):
            if numero in oks:
                reproduzidos += 1
            elif lista.aprovada and (bib, numero) in lista.itens:
                aceitas.append((bib, numero))
            else:
                inexplicados.append((bib, numero))

    return ResultadoPortao(
        reproduzidos=reproduzidos,
        excecoes_aceitas=tuple(aceitas),
        inexplicados=tuple(inexplicados),
        lista_aprovada=lista.aprovada,
        aprovado_por=lista.aprovado_por,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Portão de 1906 (pré-registro de 2026-07-18, item 3)"
    )
    parser.add_argument("--censo", type=Path, default=DIR_CENSO)
    parser.add_argument("--excecoes", type=Path, default=MANIFESTO_PADRAO)
    args = parser.parse_args()

    resultado = avalia(gabarito_piloto(), args.censo, args.excecoes)
    total = (
        resultado.reproduzidos
        + len(resultado.excecoes_aceitas)
        + len(resultado.inexplicados)
    )

    print("PORTÃO DE 1906 (docs/decisoes.md, 2026-07-18, item 3)")
    print(f"  itens do gabarito      : {total}")
    print(f"  reproduzidos no censo  : {resultado.reproduzidos}")
    print(f"  exceções aceitas       : {len(resultado.excecoes_aceitas)}")
    print(f"  inexplicados           : {len(resultado.inexplicados)}")
    print(
        "  lista de exceções      : "
        + (
            f"ratificada por {resultado.aprovado_por}"
            if resultado.lista_aprovada
            else "NÃO RATIFICADA"
        )
    )

    if resultado.inexplicados:
        print("\n  Itens sem classe atribuída:")
        for bib, numero in resultado.inexplicados:
            print(f"    bib {bib}  edição {numero}")

    print()
    if resultado.aprovado:
        print("VEREDITO: APROVADO. Lote pago liberado pelo portão de 1906.")
        return 0
    print("VEREDITO: REPROVADO. Nenhum lote pago de API deve rodar.")
    if not resultado.lista_aprovada and resultado.inexplicados:
        print(
            "Causa provável: a lista de exceções existe mas não tem aprovação\n"
            "expressa de Pedro. O pré-registro exige ratificação explícita."
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
