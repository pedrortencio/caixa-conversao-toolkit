"""Correção conservadora do OCR embutido da Hemeroteca.

O OCR da BN é determinístico e gratuito, mas sujo: ruído medido entre 4,84%
e 14,33% conforme a célula jornal-ano. Este protocolo torna esse texto legível
por humano e pesquisável por máquina sem virar reescrita.

A garantia que o torna defensável é uma só, e está travada por teste:

    a sequência de caracteres alfanuméricos do texto corrigido é IDÊNTICA
    à do texto bruto.

Toda operação ou remove caractere não alfanumérico (controle, espaço, hífen de
quebra de linha, pontuação espúria) ou junta pedaços que já estavam na página.
Nenhuma inventa, apaga ou reordena letra e dígito. Por isso o protocolo não
conserta `Convërtflo` para `Conversão`: isso seria adivinhar, e adivinhação de
máquina foi exatamente o que estragou a coluna `texto` de
`dados/triagem/amostra_para_rotular.csv` (ver `docs/exploracao-base-2026-07-28.md`).
Palavra destruída continua destruída, visível, e é problema para a leitura na
imagem, não para este protocolo.

O bruto nunca é sobrescrito. Cada página sai com sha256 das duas pontas no
manifesto, então qualquer afirmação feita sobre o texto corrigido é reconferível
contra a origem.

Uso:
  uv run python -m pipeline.transcricao.corrige_conservador --limite 50
  uv run python -m pipeline.transcricao.corrige_conservador --todas
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - conveniência de execução direta
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

PROTOCOLO = "correcao-conservadora-ocr-jornais"
VERSAO = "1.0.0"

RAIZ = Path(__file__).resolve().parents[2]
LEXICO_CSV = Path(__file__).resolve().parent / "correcoes_lexicais_permitidas.csv"

DIR_BRUTO = Path("C:/dados-caixa/texto_embutido")
DIR_CORRIGIDO = Path("C:/dados-caixa/texto_corrigido/jornais")
DIR_MANIFESTO = RAIZ / "dados" / "texto_corrigido" / "jornais"

NOMES_OPERACAO = (
    "remove_controle",
    "dehifenizacao",
    "refluxo_linha",
    "espaco_pontuacao",
    "correcao_lexical",
)

BIB2JORNAL = {
    "089842": "correio_manha",
    "090972": "correio_paulistano",
    "103730": "gazeta_noticias",
    "178691": "o_paiz",
}


@dataclass(frozen=True, slots=True)
class Resultado:
    """Texto corrigido e a contagem de cada operação aplicada."""

    texto: str
    operacoes: dict[str, int]


def so_alfanumerico(texto: str) -> str:
    """Só os caracteres alfanuméricos, na ordem. A base da invariante."""
    return "".join(c for c in texto if c.isalnum())


def sha256_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


# --- operações -------------------------------------------------------------

# Letra, sem dígito e sem sublinhado, para que intervalo de ano (1906-\n1914)
# não seja confundido com palavra partida pela quebra de coluna.
_LETRA = r"[^\W\d_]"
_HIFEN_QUEBRA = re.compile(rf"(?<={_LETRA})-[ \t]*\r?\n[ \t]*(?={_LETRA})")
_ESPACO_ANTES_PONT = re.compile(r"(?<=\w)[ \t]+([.,;:!?])")
_FALTA_ESPACO_DEPOIS = re.compile(rf"([,;:])(?={_LETRA})")
_ESPACO_REPETIDO = re.compile(r"[ \t]{2,}")


def remove_controle(texto: str) -> tuple[str, int]:
    """Tira caractere de controle, preservando quebra de linha e tabulação.

    São 0,36% dos caracteres nas páginas triadas e não são texto: o OCR os
    emite onde o scan degradou.
    """
    mantidos = []
    removidos = 0
    for caractere in texto:
        if caractere in "\n\r\t":
            mantidos.append(caractere)
        elif unicodedata.category(caractere) == "Cc":
            removidos += 1
        else:
            mantidos.append(caractere)
    return "".join(mantidos), removidos


def dehifeniza(texto: str) -> tuple[str, int]:
    """Junta a palavra partida pelo fim de linha, só entre letras."""
    return _sub_contando(_HIFEN_QUEBRA, "", texto)


def reflui_linhas(texto: str) -> tuple[str, int]:
    """Junta linha continuada, preservando parágrafo e início de período.

    Só junta quando a linha anterior termina em letra minúscula ou vírgula E a
    seguinte começa em letra minúscula. Linha em branco e maiúscula inicial são
    fronteiras: atravessá-las apagaria a estrutura da página.
    """
    linhas = texto.split("\n")
    if len(linhas) < 2:
        return texto, 0

    saida = [linhas[0]]
    juntadas = 0
    for linha in linhas[1:]:
        anterior = saida[-1].rstrip(" \t")
        proxima = linha.lstrip(" \t")
        continua = (
            anterior
            and proxima
            and (anterior[-1].islower() or anterior[-1] == ",")
            and proxima[0].islower()
        )
        if continua:
            saida[-1] = f"{anterior} {proxima}"
            juntadas += 1
        else:
            saida.append(linha)
    return "\n".join(saida), juntadas


def espaco_pontuacao(texto: str) -> tuple[str, int]:
    """Cola a pontuação na palavra, abre espaço depois dela e colapsa espaço.

    Nunca toca em `1.000$000` nem em `27 1/2`: a regra de abertura só vale
    quando a pontuação é seguida de LETRA, e a de fechamento exige palavra
    antes.
    """
    texto, n1 = _sub_contando(_ESPACO_ANTES_PONT, r"\1", texto)
    texto, n2 = _sub_contando(_FALTA_ESPACO_DEPOIS, r"\1 ", texto)
    texto, n3 = _sub_contando(_ESPACO_REPETIDO, " ", texto)
    return texto, n1 + n2 + n3


def aplica_lexico(texto: str, lexico: list[tuple[str, str]]) -> tuple[str, int]:
    """Aplica a lista FECHADA de correções lexicais, só em token inteiro.

    A fronteira importa: sem ela, `q.ue` casaria dentro de `q.uem` e o
    protocolo passaria a inventar palavra.
    """
    total = 0
    for bruta, corrigida in lexico:
        padrao = re.compile(rf"(?<!\w){re.escape(bruta)}(?!\w)")
        texto, n = _sub_contando(padrao, corrigida.replace("\\", "\\\\"), texto)
        total += n
    return texto, total


def _sub_contando(padrao: re.Pattern[str], troca: str, texto: str) -> tuple[str, int]:
    novo, n = padrao.subn(troca, texto)
    return novo, n


def corrige(texto: str, lexico: list[tuple[str, str]]) -> Resultado:
    """Aplica o protocolo inteiro, na ordem, e confere a invariante.

    A dehifenização vem antes do refluxo de propósito: invertido, a palavra
    partida receberia um espaço no meio e nunca mais se juntaria.
    """
    operacoes: dict[str, int] = {}
    saida, operacoes["remove_controle"] = remove_controle(texto)
    saida, operacoes["dehifenizacao"] = dehifeniza(saida)
    saida, operacoes["refluxo_linha"] = reflui_linhas(saida)
    saida, operacoes["espaco_pontuacao"] = espaco_pontuacao(saida)
    saida, operacoes["correcao_lexical"] = aplica_lexico(saida, lexico)

    if so_alfanumerico(saida) != so_alfanumerico(texto):
        raise RuntimeError(
            "protocolo alterou a sequência alfanumérica: isso é reescrita, "
            "não correção. Conferir a lista léxica."
        )
    return Resultado(texto=saida, operacoes=operacoes)


def carrega_lexico(caminho: Path = LEXICO_CSV) -> list[tuple[str, str]]:
    """Lê a lista fechada. Ordena da forma mais longa para a mais curta para
    que `qu.e` não seja consumida por uma entrada mais curta antes da hora."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        pares = [
            (linha["forma_bruta"], linha["forma_corrigida"])
            for linha in csv.DictReader(arquivo)
        ]
    return sorted(pares, key=lambda p: -len(p[0]))


LEXICO_PADRAO = carrega_lexico()


# --- manifesto e leitura humana -------------------------------------------


def registro_de_pagina(
    *, bib: str, source_identifier: str, page_number: int, bruto: str
) -> dict:
    """Uma linha de manifesto, com hash das duas pontas.

    Página sem texto recebe status próprio em vez de sumir: ausência é
    registrada positivamente, nunca inferida do silêncio.
    """
    if not bruto.strip():
        return {
            "bib": bib,
            "source_identifier": source_identifier,
            "page_number": page_number,
            "protocol_name": PROTOCOLO,
            "protocol_version": VERSAO,
            "raw_text_sha256": sha256_texto(bruto),
            "corrected_text_sha256": sha256_texto(bruto),
            "status": "empty",
            "raw_char_count": len(bruto),
            "corrected_char_count": len(bruto),
            "operation_counts": {nome: 0 for nome in NOMES_OPERACAO},
            "corrected_text": bruto,
        }

    resultado = corrige(bruto, LEXICO_PADRAO)
    return {
        "bib": bib,
        "source_identifier": source_identifier,
        "page_number": page_number,
        "protocol_name": PROTOCOLO,
        "protocol_version": VERSAO,
        "raw_text_sha256": sha256_texto(bruto),
        "corrected_text_sha256": sha256_texto(resultado.texto),
        "status": "ok",
        "raw_char_count": len(bruto),
        "corrected_char_count": len(resultado.texto),
        "operation_counts": resultado.operacoes,
        "corrected_text": resultado.texto,
    }


def datas_conhecidas() -> dict[str, str]:
    """Mapa objeto digital -> data civil, só do que foi OBSERVADO no banco.

    Data imputada não entra: o projeto registra ausência, não a preenche. Hoje
    são poucas dezenas de objetos, e resolver o resto é trabalho de
    `pipeline/triagem/objeto_por_data.py`, não deste protocolo.
    """
    from pipeline.base import db

    conn = db.connect(db.DEFAULT_DATABASE, migrate=False)
    try:
        linhas = conn.execute(
            """SELECT o.source_identifier, dr.normalized_date
               FROM digital_objects o
               JOIN edition_object_links l ON l.object_id = o.id
               JOIN current_edition_dates ced ON ced.edition_day_id = l.edition_day_id
               JOIN date_records dr ON dr.id = ced.date_record_id
               WHERE dr.status = 'observed' AND dr.normalized_date IS NOT NULL"""
        ).fetchall()
    finally:
        conn.close()
    return {linha[0]: linha[1] for linha in linhas}


def markdown_da_edicao(
    *,
    jornal: str,
    source_identifier: str,
    data: str,
    paginas: list[tuple[int, str]],
    ano: str = "",
) -> str:
    """Edição-dia inteira em Markdown, com proveniência no cabeçalho.

    O cabeçalho diz o que o arquivo é e o que ele não é, porque este .md vai
    circular fora do repo e sem essa frase alguém vai citá-lo como se fosse a
    página.
    """
    partes = [
        f"# {jornal} · {data or 'data não resolvida'}",
        "",
        f"- **Objeto digital:** `{source_identifier}`",
        f"- **Jornal:** {jornal}",
        f"- **Data:** {data or 'não resolvida no censo'}",
        f"- **Origem:** camada de texto embutida no PDF da Hemeroteca Digital "
        f"da Biblioteca Nacional (OCR determinístico, não reprocessado)",
        f"- **Protocolo:** `{PROTOCOLO}` v{VERSAO}",
        f"- **Páginas:** {len(paginas)}",
        "",
        "> Este texto é **OCR corrigido de forma conservadora**, não uma "
        "transcrição diplomática. A correção só remove ruído e junta palavra "
        "partida pela quebra de coluna: a sequência de letras e dígitos é "
        "idêntica à do OCR de origem. Palavra que o OCR destruiu continua "
        "destruída aqui. **Não substitui a imagem da página**, e citação "
        "verbatim para publicação deve ser conferida no fac-símile.",
        "",
        "---",
        "",
    ]
    for numero, texto in paginas:
        partes += [f"## Página {numero}", "", texto.strip(), "", "---", ""]
    return "\n".join(partes)


# --- execução --------------------------------------------------------------


def paginas_triadas() -> list[dict]:
    """Páginas com menção ao nome, direto dos manifestos versionados."""
    import glob

    linhas: list[dict] = []
    for caminho in sorted(glob.glob(str(RAIZ / "dados/triagem/triagem_nome_*.csv"))):
        nome = Path(caminho).name
        bib, ano = nome.replace(".csv", "").split("_")[2:4]
        with open(caminho, encoding="utf-8", newline="") as arquivo:
            for linha in csv.DictReader(arquivo):
                if linha["hit"] != "1":
                    continue
                linhas.append(
                    {
                        "bib": bib,
                        "jornal": BIB2JORNAL[bib],
                        "ano": int(ano),
                        "source_identifier": linha["source_identifier"],
                        "page_number": int(linha["page_number"]),
                    }
                )
    return linhas


def caminho_bruto(bib: str, source_identifier: str, page_number: int) -> Path:
    return DIR_BRUTO / bib / source_identifier / f"p{page_number:03d}.txt"


def caminho_corrigido(bib: str, source_identifier: str, page_number: int) -> Path:
    return DIR_CORRIGIDO / bib / source_identifier / f"p{page_number:03d}.txt"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limite", type=int, default=0, help="0 = todas as triadas")
    parser.add_argument("--todas", action="store_true", help="sem limite")
    parser.add_argument("--saida", type=Path, default=DIR_CORRIGIDO)
    parser.add_argument("--manifesto", type=Path, default=DIR_MANIFESTO)
    parser.add_argument("--sem-md", action="store_true", help="só os .txt")
    args = parser.parse_args(argv)

    paginas = paginas_triadas()
    if args.limite and not args.todas:
        paginas = paginas[: args.limite]

    args.manifesto.mkdir(parents=True, exist_ok=True)
    por_edicao: dict[tuple[str, str], list[tuple[int, str]]] = {}
    registros: list[dict] = []
    totais = {nome: 0 for nome in NOMES_OPERACAO}
    falhas = 0

    for n, pagina in enumerate(paginas, 1):
        origem = caminho_bruto(
            pagina["bib"], pagina["source_identifier"], pagina["page_number"]
        )
        if not origem.is_file():
            falhas += 1
            continue
        bruto = origem.read_text(encoding="utf-8", errors="replace")
        registro = registro_de_pagina(
            bib=pagina["bib"],
            source_identifier=pagina["source_identifier"],
            page_number=pagina["page_number"],
            bruto=bruto,
        )
        texto = registro.pop("corrected_text")
        for nome, valor in registro["operation_counts"].items():
            totais[nome] += valor

        destino = caminho_corrigido(
            pagina["bib"], pagina["source_identifier"], pagina["page_number"]
        )
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8", newline="\n")

        registro["jornal"] = pagina["jornal"]
        registro["ano"] = pagina["ano"]
        registros.append(registro)
        por_edicao.setdefault(
            (pagina["jornal"], pagina["source_identifier"]), []
        ).append((pagina["page_number"], texto))

        if n % 500 == 0:
            print(f"  {n}/{len(paginas)} páginas")

    if not args.sem_md:
        dir_md = args.saida / "_md"
        for (jornal, objeto), paginas_da_edicao in por_edicao.items():
            md = markdown_da_edicao(
                jornal=jornal,
                source_identifier=objeto,
                data="",
                paginas=sorted(paginas_da_edicao),
            )
            alvo = dir_md / jornal / f"{objeto}.md"
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(md, encoding="utf-8", newline="\n")

    campos = [
        "bib", "jornal", "ano", "source_identifier", "page_number",
        "protocol_name", "protocol_version", "raw_text_sha256",
        "corrected_text_sha256", "status", "raw_char_count",
        "corrected_char_count", "operation_counts",
    ]
    with open(
        args.manifesto / "manifesto_correcao_paginas.csv",
        "w", encoding="utf-8", newline="",
    ) as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        for registro in registros:
            linha = dict(registro)
            linha["operation_counts"] = json.dumps(
                linha["operation_counts"], sort_keys=True
            )
            escritor.writerow(linha)

    resumo = {
        "protocol_name": PROTOCOLO,
        "protocol_version": VERSAO,
        "pages": len(registros),
        "missing_source": falhas,
        "status_counts": {
            estado: sum(1 for r in registros if r["status"] == estado)
            for estado in ("ok", "empty")
        },
        "operation_counts": totais,
        "editions": len(por_edicao),
    }
    (args.manifesto / "relatorio_qualidade_correcao.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    print(f"texto corrigido em {args.saida}")
    print(f"manifesto em {args.manifesto}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
