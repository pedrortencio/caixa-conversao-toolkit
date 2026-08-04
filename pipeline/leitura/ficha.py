"""Preenchimento assistido de `dados/leitura/fichas_leitura.csv`.

Motivo de existir: sao 185 pecas por 15 campos, e uma planilha e onde esse tipo
de ficha morre. Tres coisas concretas que o Excel faz de errado com este
arquivo e que aqui nao acontecem:

  - o CSV e UTF-8 SEM BOM, e o Excel em portugues abre como ANSI, transforma
    CONVERSAO em CONVERSAO e grava o lixo de volta;
  - o vocabulario de `voz`, `objeto_politica` e `direcao_por_objeto` nao e
    validado em lugar nenhum, e um typo vira categoria nova em silencio;
  - `direcao_por_objeto` tem de casar um-para-um com `objeto_politica`, e
    planilha nenhuma cobra isso.

O que o modulo NAO faz, de proposito: nao le a peca por voce, nao sugere valor,
nao preenche campo nenhum sozinho. A leitura e o instrumento aqui, e um default
oferecido pela maquina contaminaria a codificacao humana que existe justamente
para nao vir de modelo.

Uso:

    uv run python -m pipeline.leitura.ficha                 # camada 0, fase F1
    uv run python -m pipeline.leitura.ficha --camada 1_episodio
    uv run python -m pipeline.leitura.ficha --fase F2 --jornal o_paiz
    uv run python -m pipeline.leitura.ficha --item per178691_1906_07832:p001:i0
    uv run python -m pipeline.leitura.ficha --resumo

Grava a linha inteira no disco a cada peca terminada, por arquivo temporario e
troca atomica, para que uma queda no meio da sessao nao leve o trabalho junto.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
import webbrowser
from pathlib import Path

from pipeline.leitura.campos import (
    CAMPOS,
    COLUNAS_LEITURA,
    ErroDeCampo,
    caminho_pdf,
    caminho_texto_ocr,
    esta_preenchida,
    normaliza_para_busca,
    pendencias_do_estrito,
    valida,
    valida_direcao_casa_objeto,
)

RAIZ = Path(__file__).resolve().parents[2]
FICHA_PADRAO = RAIZ / "dados" / "leitura" / "fichas_leitura.csv"
ACERVO_PADRAO = Path("C:/dados-caixa")

SAIR = {"sair", "fim", "quit", ":q"}
PULAR = {"pular", "skip", ">"}
VOLTAR = {"voltar", "<"}
AJUDA = {"?", "ajuda", "help"}


def carrega(caminho: Path) -> tuple[list[str], list[dict[str, str]]]:
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        return list(leitor.fieldnames or []), list(leitor)


def grava(caminho: Path, colunas: list[str], linhas: list[dict[str, str]]) -> None:
    """Troca atomica: escreve ao lado e substitui, nunca trunca o original."""
    temporario = caminho.with_suffix(caminho.suffix + ".parcial")
    with open(temporario, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)
    os.replace(temporario, caminho)


def abre_pdf(caminho: Path, pagina: int, modo: str) -> str:
    if modo == "nenhum":
        return "visualizador desligado"
    if not caminho.is_file():
        return f"PDF NAO ENCONTRADO em {caminho}"
    if modo == "navegador":
        # Edge e Chrome respeitam a ancora #page=N; leitor nativo geralmente nao.
        webbrowser.open(caminho.as_uri() + f"#page={pagina}")
        return f"aberto no navegador na pagina {pagina}"
    try:
        os.startfile(caminho)  # type: ignore[attr-defined]
        return f"aberto no visualizador padrao, va para a pagina {pagina}"
    except OSError as erro:
        return f"nao consegui abrir ({erro}); o caminho esta acima"


def confere_citacao(citacao: str, caminho_ocr: Path) -> str:
    """Conferencia FROUXA contra o OCR, que avisa e nunca bloqueia.

    O OCR da Hemeroteca e sujo e a transcricao vem da imagem, entao divergencia
    e o caso normal, nao o erro. O que esta checagem pega de verdade e
    localizador errado: se nenhum pedaco da citacao aparece na pagina, provavel
    que a pagina nao seja essa. Bloquear seria empurrar o leitor a higienizar a
    transcricao para agradar a maquina, que e exatamente o defeito que a
    conferencia mecanica existe para impedir.
    """
    if not citacao.strip():
        return ""
    if not caminho_ocr.is_file():
        return "  (sem OCR desta pagina no acervo, nao conferi)"
    texto = normaliza_para_busca(caminho_ocr.read_text(encoding="utf-8", errors="replace"))
    alvo = normaliza_para_busca(citacao)
    if alvo and alvo in texto:
        return "  citacao casa o OCR literalmente"
    palavras = [p for p in alvo.split() if len(p) >= 4]
    if not palavras:
        return "  (citacao curta demais para conferir)"
    achadas = sum(1 for p in palavras if p in texto)
    proporcao = achadas / len(palavras)
    if proporcao >= 0.6:
        return (f"  {achadas}/{len(palavras)} palavras batem com o OCR; "
                "divergencia esperada, o OCR e sujo")
    return (f"  ATENCAO: so {achadas}/{len(palavras)} palavras aparecem no OCR "
            "desta pagina. Confira se a pagina e mesmo esta.")


def cabecalho(linha: dict[str, str], indice: int, total: int) -> None:
    print("\n" + "=" * 78)
    print(f"[{indice}/{total}]  {linha['item_id']}")
    print("=" * 78)
    jornal = linha["jornal"].replace("_", " ")
    data = linha["data"] or "SEM DATA"
    if linha.get("data_confiavel") == "0":
        data += "  (data NAO confiavel, confira o cabecalho)"
    print(f"  {jornal}, {data}, pagina {linha['page_number']}")
    print(f"  camada {linha['camada']}  |  fase {linha['fase']}  |  "
          f"registro {linha['registro']}  |  forma {linha['forma']}")
    if linha.get("secao"):
        print(f"  secao:  {linha['secao']}")
    if linha.get("titulo"):
        print(f"  titulo: {linha['titulo']}")
    print(f"  motivo da selecao: {linha['motivo_selecao']}")
    if linha["forma"] in ("editorial", "artigo"):
        print("  NOTA: `forma` veio do claude-sonnet-5, nao de voce. Se a peca "
              "nao for isso,\n        registre em `dificuldade`: o rotulo e "
              "suspeito de subdeteccao.")


def pergunta_campo(campo, linha: dict[str, str]) -> str | None:
    """Devolve o valor validado, ou None se o leitor pediu para voltar."""
    print()
    if campo.vocabulario:
        largura = max(len(v) for v in campo.vocabulario) + 2
        opcoes = [f"{i + 1}) {v:{largura}}" for i, v in enumerate(campo.vocabulario)]
        for i in range(0, len(opcoes), 3):
            print("    " + "".join(opcoes[i:i + 3]))
    if campo.exemplos:
        print(f"    ex: {campo.exemplos[0]}")
    sufixo = "  (varios com ;)" if campo.multiplo else ""
    while True:
        try:
            bruto = input(f"  {campo.pergunta}{sufixo}\n  > ")
        except EOFError:
            return ""
        corte = bruto.strip().lower()
        if corte in AJUDA:
            print(f"    {campo.ajuda}")
            continue
        if corte in VOLTAR:
            return None
        if campo.vocabulario and corte:
            # Atalho por numero: "2" ou "1;3" viram os nomes do vocabulario.
            partes = [p.strip() for p in corte.split(";") if p.strip()]
            if all(p.isdigit() and 1 <= int(p) <= len(campo.vocabulario) for p in partes):
                if campo.nome == "confianca":
                    bruto = corte
                else:
                    bruto = ";".join(campo.vocabulario[int(p) - 1] for p in partes)
        try:
            return valida(campo, bruto)
        except ErroDeCampo as erro:
            print(f"    {erro}")


def le_uma(linha: dict[str, str], acervo: Path, modo_pdf: str) -> bool:
    """Preenche uma ficha. Devolve False se o leitor pediu para sair."""
    try:
        pdf = caminho_pdf(linha, acervo)
        ocr = caminho_texto_ocr(linha, acervo)
    except ErroDeCampo as erro:
        print(f"  {erro}")
        return True
    print(f"\n  PDF: {pdf}")
    print(f"  {abre_pdf(pdf, int(linha['page_number']), modo_pdf)}")
    print("\n  `?` explica o campo, `<` volta um campo, `pular` pula a peca, "
          "`sair` encerra.")

    inicio = time.monotonic()
    valores: dict[str, str] = {}
    i = 0
    while i < len(CAMPOS):
        campo = CAMPOS[i]
        resposta = pergunta_campo(campo, linha)
        if resposta is None:
            i = max(0, i - 1)
            continue
        if resposta.strip().lower() in SAIR:
            return False
        if resposta.strip().lower() in PULAR:
            print("  peca pulada, nada gravado")
            return True
        if campo.nome == "direcao_por_objeto":
            try:
                valida_direcao_casa_objeto(valores.get("objeto_politica", ""), resposta)
            except ErroDeCampo as erro:
                print(f"    {erro}")
                continue
        valores[campo.nome] = resposta
        if campo.nome == "citacao_ancora":
            aviso = confere_citacao(resposta, ocr)
            if aviso:
                print(aviso)
        i += 1

    medidos = (time.monotonic() - inicio) / 60
    print(f"\n  cronometro: {medidos:.1f} min")
    bruto = input("  minutos (Enter aceita o cronometro) > ").strip()
    valores["minutos"] = bruto if bruto else f"{medidos:.1f}"

    linha.update(valores)
    faltando = pendencias_do_estrito(linha)
    if faltando:
        print(f"  nota: peca substantiva sem {', '.join(faltando)}. "
              "Sao os campos que o codebook consome.")
    return True


def resumo(linhas: list[dict[str, str]]) -> None:
    feitas = [l for l in linhas if esta_preenchida(l)]
    print(f"\n{len(feitas)} de {len(linhas)} fichas preenchidas\n")
    print(f"{'camada':32s} {'feitas':>7s} {'total':>7s}")
    for camada in sorted({l["camada"] for l in linhas}):
        alvo = [l for l in linhas if l["camada"] == camada]
        print(f"{camada:32s} {sum(1 for l in alvo if esta_preenchida(l)):>7d} "
              f"{len(alvo):>7d}")
    print(f"\n{'fase':32s} {'feitas':>7s} {'total':>7s}")
    for fase in sorted({l["fase"] for l in linhas}):
        alvo = [l for l in linhas if l["fase"] == fase]
        print(f"{fase:32s} {sum(1 for l in alvo if esta_preenchida(l)):>7d} "
              f"{len(alvo):>7d}")
    minutos = [float(l["minutos"]) for l in feitas if (l.get("minutos") or "").strip()]
    if minutos:
        media = sum(minutos) / len(minutos)
        print(f"\ntaxa medida: {media:.1f} min por peca em {len(minutos)} pecas")
        print(f"projecao para as 185: {media * 185 / 60:.1f} horas")
        print("Essa taxa e o que estreita a projecao do D-Humano por censo. "
              "Ver docs/plano-leitura-fases.md, secao 9.")


def main() -> int:  # pragma: no cover - orquestracao com I/O
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ficha", type=Path, default=FICHA_PADRAO)
    parser.add_argument("--acervo", type=Path, default=ACERVO_PADRAO)
    parser.add_argument("--camada", default="0_censo_editorial_artigo")
    parser.add_argument("--fase", default=None)
    parser.add_argument("--jornal", default=None)
    parser.add_argument("--item", default=None, help="um item_id especifico")
    parser.add_argument("--todas", action="store_true", help="ignora o filtro de camada")
    parser.add_argument("--refazer", action="store_true",
                        help="inclui fichas ja preenchidas")
    parser.add_argument("--pdf", choices=("padrao", "navegador", "nenhum"),
                        default="navegador",
                        help="navegador abre na pagina certa pela ancora #page")
    parser.add_argument("--resumo", action="store_true")
    args = parser.parse_args()

    for fluxo in (sys.stdout, sys.stdin):
        try:
            fluxo.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, OSError):
            pass

    colunas, linhas = carrega(args.ficha)
    faltando = [c for c in COLUNAS_LEITURA if c not in colunas]
    if faltando:
        print(f"ficha sem as colunas {faltando}; e a ficha certa?")
        return 1

    if args.resumo:
        resumo(linhas)
        return 0

    fila = list(linhas)
    if args.item:
        fila = [l for l in fila if l["item_id"] == args.item]
    else:
        if not args.todas:
            fila = [l for l in fila if l["camada"] == args.camada]
        if args.fase:
            fila = [l for l in fila if l["fase"] == args.fase]
        if args.jornal:
            fila = [l for l in fila if l["jornal"] == args.jornal]
        if not args.refazer:
            fila = [l for l in fila if not esta_preenchida(l)]

    if not fila:
        print("nada na fila com esses filtros. `--resumo` mostra o estado.")
        return 0

    print(f"{len(fila)} peca(s) na fila. Ordem: fase, depois jornal, depois data.")
    fila.sort(key=lambda l: (l["fase"], l["jornal"], l["data"] or "9999"))

    feitas = 0
    for i, linha in enumerate(fila, 1):
        cabecalho(linha, i, len(fila))
        try:
            seguir = le_uma(linha, args.acervo, args.pdf)
        except KeyboardInterrupt:
            print("\n  interrompido; a peca corrente nao foi gravada")
            break
        if not seguir:
            break
        if esta_preenchida(linha):
            grava(args.ficha, colunas, linhas)
            feitas += 1
            print(f"  gravado em {args.ficha.name}")

    print(f"\n{feitas} ficha(s) gravada(s) nesta sessao.")
    resumo(linhas)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
