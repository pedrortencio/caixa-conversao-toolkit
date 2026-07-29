"""Conferencia mecanica das citacoes devolvidas por um anotador.

Regra unica e nao negociavel do desenho de catalogacao: toda citacao tem de
ser substring literal da janela que a originou. Linha que nao casa e
REJEITADA, nunca corrigida. Corrigir citacao de modelo transformaria uma
falha visivel numa falha invisivel.

A comparacao roda sobre os dois lados normalizados por
`regra_nome.normaliza` (caixa baixa, sem diacritico, espaco colapsado,
hifenizacao de quebra rejuntada). Isso perdoa o que e ruido de transcricao
do OCR e da copia, e nao perdoa o que e invencao: texto que o anotador
escreveu e nao estava na pagina continua nao casando.

A taxa de rejeicao por anotador e a metrica de qualidade do lote.
"""

from __future__ import annotations

from dataclasses import dataclass

from pipeline.triagem import regra_nome

MOTIVO_OK = "ok"
MOTIVO_VAZIA = "citacao_vazia"
MOTIVO_CURTA = "citacao_curta"
MOTIVO_AUSENTE = "citacao_ausente_da_janela"

MINIMO_CARACTERES = 20


@dataclass(frozen=True, slots=True)
class Veredito:
    aceita: bool
    motivo: str


def confere_citacao(
    citacao: str | None,
    janela: str,
    *,
    minimo: int = MINIMO_CARACTERES,
) -> Veredito:
    """Aceita a citacao apenas se ela existir literalmente na janela.

    `minimo` existe porque citacao curta demais casa por acaso e nao
    sustenta afirmacao nenhuma numa dissertacao.
    """
    if citacao is None:
        return Veredito(False, MOTIVO_VAZIA)
    limpa = regra_nome.normaliza(citacao)
    if not limpa:
        return Veredito(False, MOTIVO_VAZIA)
    if len(limpa) < minimo:
        return Veredito(False, MOTIVO_CURTA)
    if limpa not in regra_nome.normaliza(janela):
        return Veredito(False, MOTIVO_AUSENTE)
    return Veredito(True, MOTIVO_OK)


def confere_registros(
    registros: list[dict],
    janela_por_id: dict[str, str],
    *,
    campo_citacao: str = "citacao_verbatim",
    campo_janela: str = "janela_id",
    minimo: int = MINIMO_CARACTERES,
) -> tuple[list[dict], list[dict]]:
    """Separa os registros de um anotador em aceitos e rejeitados.

    Registro que aponta para janela desconhecida e rejeitado: sem a janela
    de origem nao ha como conferir, e o beneficio da duvida aqui seria
    exatamente o buraco por onde passa a citacao inventada.
    """
    aceitos: list[dict] = []
    rejeitados: list[dict] = []
    for registro in registros:
        janela = janela_por_id.get(registro.get(campo_janela, ""))
        if janela is None:
            rejeitados.append({**registro, "motivo_rejeicao": "janela_desconhecida"})
            continue
        veredito = confere_citacao(
            registro.get(campo_citacao), janela, minimo=minimo
        )
        if veredito.aceita:
            aceitos.append(registro)
            continue
        rejeitados.append({**registro, "motivo_rejeicao": veredito.motivo})
    return aceitos, rejeitados


def taxa_rejeicao(aceitos: list[dict], rejeitados: list[dict]) -> float:
    """Proporcao rejeitada. Zero registros devolve 0.0, nao divisao por zero."""
    total = len(aceitos) + len(rejeitados)
    if total == 0:
        return 0.0
    return len(rejeitados) / total
