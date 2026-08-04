"""Confere mecanicamente cada citacao do relatorio contra a fonte.

A regra do repo vale para qualquer citacao, venha de anotador ou de mim:
normalizada, ela tem de ser substring literal do texto de origem. Linha que
nao casa e rejeitada, nunca corrigida. Este modulo aplica a regra a um
manifesto de citacoes curadas.

Duas fontes:

  `pagina`      camada de texto embutido, `{bib}/{objeto}/p{pagina:03d}.txt`;
  `retrospecto` secoes anuais do Retrospecto Commercial do Jornal do Commercio
                em `dados/retrospecto_jc/`, que nao esta no censo.

O que a conferencia garante e o que ela NAO garante: garante que a linha
existe no OCR da fonte, com aquela grafia. Nao garante que o OCR corresponda
a pagina impressa. Citacao de dissertacao continua exigindo conferencia na
imagem, e por isso o manifesto tem coluna `conferido_na_imagem`.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from pipeline.triagem import regra_nome

RAIZ = Path(__file__).resolve().parents[2]
TEXTO_EMBUTIDO = Path("C:/dados-caixa/texto_embutido")
MANIFESTO_PADRAO = RAIZ / "dados" / "analise" / "mencoes_credor_externo.csv"

MINIMO_CARACTERES = 20


@dataclass(frozen=True, slots=True)
class Resultado:
    id: str
    situacao: str
    detalhe: str = ""

    @property
    def ok(self) -> bool:
        return self.situacao == "ok"


def caminho_da_fonte(
    fonte_tipo: str,
    bib: str,
    objeto: str,
    pagina: str,
    raiz: Path = RAIZ,
    texto_embutido: Path = TEXTO_EMBUTIDO,
) -> Path:
    if fonte_tipo == "pagina":
        return texto_embutido / bib / objeto / f"p{int(pagina):03d}.txt"
    if fonte_tipo == "retrospecto":
        return raiz / "dados" / "retrospecto_jc" / objeto
    raise ValueError(f"fonte_tipo desconhecido: {fonte_tipo!r}")


def confere(citacao: str, texto_fonte: str) -> bool:
    """Substring literal apos a normalizacao ratificada da triagem."""
    return regra_nome.normaliza(citacao) in regra_nome.normaliza(texto_fonte)


def verifica_linha(linha: dict, **caminhos) -> Resultado:
    identificador = linha.get("id", "?")
    citacao = (linha.get("citacao_verbatim") or "").strip()
    if len(citacao) < MINIMO_CARACTERES:
        return Resultado(identificador, "curta", f"{len(citacao)} caracteres")
    caminho = caminho_da_fonte(
        linha["fonte_tipo"], linha.get("bib", ""), linha["objeto"],
        linha.get("pagina", "0"), **caminhos
    )
    if not caminho.is_file():
        return Resultado(identificador, "fonte_ausente", str(caminho))
    texto = caminho.read_text(encoding="utf-8", errors="replace")
    if not confere(citacao, texto):
        return Resultado(identificador, "nao_casa", str(caminho))
    return Resultado(identificador, "ok")


def verifica_manifesto(caminho: Path = MANIFESTO_PADRAO, **caminhos) -> list[Resultado]:
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return [verifica_linha(linha, **caminhos) for linha in csv.DictReader(arquivo)]


def main() -> int:  # pragma: no cover - saida de linha de comando
    resultados = verifica_manifesto()
    falhas = [r for r in resultados if not r.ok]
    for r in resultados:
        marca = "ok  " if r.ok else "FALHA"
        print(f"  {marca} {r.id:24s} {r.situacao:14s} {r.detalhe}")
    print(f"\n{len(resultados) - len(falhas)} de {len(resultados)} citacoes conferidas")
    if falhas:
        print("Citacao que nao casa e rejeitada, nunca corrigida.")
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
