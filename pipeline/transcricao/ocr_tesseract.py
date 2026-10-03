"""Camada de texto por OCR próprio (Tesseract) sobre os scans da Hemeroteca.

A camada embutida nos PDFs da BN é gratuita e determinística, mas suja: entre
4,84% e 14,33% de ruído conforme a célula jornal-ano, e a sonda difusa mediu
que ela custou ao censo cerca de 20,8% das páginas que mencionam a Caixa de
Conversão (`docs/relatorio-sonda-difusa-2026-08-12.md`). A hipótese desta
camada é simples: reler a mesma imagem com um motor melhor entrega texto mais
inteligível por máquina, sem custo de API e sem nenhuma decisão de construto.

Três coisas governam o desenho.

**A camada da BN nunca é tocada.** O texto novo vai para
`C:/dados-caixa/texto_tesseract/`, ao lado, com o mesmo layout de pastas. Tudo
que já foi medido, o censo, o portão de 1906, a sonda, foi medido contra a
camada antiga, e apagá-la destruiria a única base de comparação que decide se
esta camada vale.

**A imagem não é persistida.** O JPEG vem do XObject do PDF, entra no Tesseract
por stdin, o texto sai por stdout, e a imagem morre na memória. Persistir seriam
dezenas de gigabytes para nada, já que o PDF original é a origem e continua no
acervo.

**Ausência é registrada.** Página que o motor não leu vira linha de manifesto
com status próprio e a mensagem de erro, nunca sumiço.

E a advertência que vale para toda segunda testemunha: **concordância entre dois
OCRs não é verdade.** Os dois leem a mesma imagem degradada e podem errar junto,
com erro correlacionado. Consenso é sinal de confiabilidade, nunca validação.

Uso:
  uv run python -m pipeline.transcricao.ocr_tesseract --amostra 60 --compara
  uv run python -m pipeline.transcricao.ocr_tesseract --corpus --executar
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - conveniência de execução direta
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

PROTOCOLO = "ocr-tesseract-scans-bn"
VERSAO = "1.0.0"

RAIZ = Path(__file__).resolve().parents[2]
DIR_PDF = Path("C:/dados-caixa/raw_pdf")
DIR_BN = Path("C:/dados-caixa/texto_embutido")
DIR_SAIDA = Path("C:/dados-caixa/texto_tesseract")
DIR_TESSDATA = Path("C:/dados-caixa/tessdata")
DIR_MANIFESTO = RAIZ / "dados" / "transcricao" / "ocr_tesseract"

#: Semente do sorteio da amostra de comparação. Fixa e registrada.
SEMENTE = 20260812

BIB2JORNAL = {
    "089842": "correio_manha",
    "090972": "correio_paulistano",
    "103730": "gazeta_noticias",
    "178691": "o_paiz",
}

TOKEN = re.compile(r"[^\W\d_]+", re.UNICODE)
# `y` entra como vogal: era vogal na ortografia da época (Nictheroy, Bahya), e
# tratá-la como ruído puniria justamente o texto mais antigo do corpus. Mesma
# convenção de `pipeline/analise/qualidade_ocr.py`, para os números serem
# comparáveis com a linha de base já publicada.
VOGAL = re.compile(r"[aeiouyàáâãäéêëíîïóôõöúûü]", re.IGNORECASE)


class PaginaIndisponivel(Exception):
    """O PDF não tem essa página, ou a página não tem imagem embutida."""


@dataclass(frozen=True, slots=True)
class Parametros:
    """Tudo que muda o texto de saída. Vai inteiro para o manifesto."""

    idioma: str
    psm: int
    oem: int
    variante: str
    escala: float = 1.0


#: `psm 3` é segmentação automática de página, que é o que respeita as seis a
#: oito colunas do jornal; `psm 6` trata a página como bloco único e mistura as
#: colunas. `oem 1` é o motor LSTM. A variante do `traineddata` fica explícita
#: porque `best` e `fast` produzem texto diferente com o mesmo comando.
PARAMETROS_PADRAO = Parametros(idioma="por", psm=3, oem=1, variante="best")


def prepara_imagem(imagem: bytes, escala: float) -> bytes:
    """Amplia antes do OCR, ou devolve o original intacto.

    O JPEG embutido tem cerca de 2016x2985, o que numa página de jornal dá perto
    de 135 DPI, metade do que o Tesseract espera. Ampliar é a correção padrão
    para esse regime. Com `escala` 1.0 os bytes voltam SEM reencodar: reencodar
    à toa introduziria perda de JPEG sem nenhum ganho.
    """
    if escala == 1.0:
        return imagem

    import io

    from PIL import Image

    original = Image.open(io.BytesIO(imagem))
    ampliada = original.resize(
        (int(original.width * escala), int(original.height * escala)),
        Image.LANCZOS,
    )
    buffer = io.BytesIO()
    ampliada.save(buffer, format="PNG")
    return buffer.getvalue()


def acha_binario() -> str | None:
    """Caminho do executável, incluindo a instalação padrão do Windows."""
    achado = shutil.which("tesseract")
    if achado:
        return achado
    padrao = Path("C:/Program Files/Tesseract-OCR/tesseract.exe")
    return str(padrao) if padrao.is_file() else None


def versao_do_motor(binario: str | None = None) -> dict:
    """Identidade exata do binário, para o manifesto. Sem isto não é citável."""
    binario = binario or acha_binario()
    saida = subprocess.run(
        [binario, "--version"], capture_output=True, text=True, check=False
    ).stdout
    primeira = saida.splitlines()[0] if saida else ""
    versao = primeira.replace("tesseract", "").strip().lstrip("v")
    leptonica = ""
    for linha in saida.splitlines():
        if "leptonica" in linha:
            leptonica = linha.strip().split()[-1]
    return {
        "engine": "tesseract",
        "version": versao,
        "leptonica": leptonica,
        "binario": binario,
    }


def comando(parametros: Parametros, binario: str | None = None) -> list[str]:
    """Argv da chamada. `-` `-` significa imagem por stdin, texto por stdout."""
    return [
        binario or acha_binario(),
        "-",
        "-",
        "-l",
        parametros.idioma,
        "--psm",
        str(parametros.psm),
        "--oem",
        str(parametros.oem),
    ]


def ambiente(parametros: Parametros) -> dict[str, str]:
    """Ambiente da chamada, com o `tessdata` da variante escolhida."""
    return {
        **os.environ,
        "TESSDATA_PREFIX": str(DIR_TESSDATA / parametros.variante),
    }


def roda_tesseract(
    imagem: bytes, parametros: Parametros, tempo_limite: int = 300
) -> str:
    """OCR de uma imagem em memória. A imagem não toca o disco."""
    resultado = subprocess.run(
        comando(parametros),
        input=imagem,
        capture_output=True,
        env=ambiente(parametros),
        timeout=tempo_limite,
        check=True,
    )
    return resultado.stdout.decode("utf-8", errors="replace")


def imagem_de_teste(texto: str) -> bytes:
    """PNG com o texto renderizado, para testar a invocação sem o acervo."""
    import io

    from PIL import Image, ImageDraw, ImageFont

    imagem = Image.new("L", (1200, 200), color=255)
    desenho = ImageDraw.Draw(imagem)
    try:
        fonte = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 72)
    except OSError:  # pragma: no cover - máquina sem a fonte
        fonte = ImageFont.load_default()
    desenho.text((30, 50), texto, fill=0, font=fonte)
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    return buffer.getvalue()


# --- acervo ----------------------------------------------------------------


def caminho_pdf(bib: str, source_identifier: str) -> Path:
    return DIR_PDF / bib / f"{source_identifier}.pdf"


def caminho_saida(
    bib: str, source_identifier: str, page_number: int, raiz: Path | None = None
) -> Path:
    """Destino do texto novo. `raiz` separa varredura de parâmetro da produção.

    Sem essa separação a retomada devolveria o texto de uma configuração
    anterior como se fosse a atual, e a comparação entre configurações mediria
    a si mesma.
    """
    return (raiz or DIR_SAIDA) / bib / source_identifier / f"p{page_number:03d}.txt"


def caminho_bn(bib: str, source_identifier: str, page_number: int) -> Path:
    return DIR_BN / bib / source_identifier / f"p{page_number:03d}.txt"


def extrai_imagem(bib: str, source_identifier: str, page_number: int) -> bytes:
    """JPEG embutido no PDF, direto do XObject, sem rasterizar.

    Os PDFs da BN trazem a página como um único JPEG de cerca de 2016x2985.
    Rasterizar seria redesenhar o que já está lá e perder qualidade.
    """
    from pypdf import PdfReader

    caminho = caminho_pdf(bib, source_identifier)
    if not caminho.is_file():
        raise PaginaIndisponivel(f"pdf ausente: {caminho.name}")
    leitor = PdfReader(str(caminho))
    if not 1 <= page_number <= len(leitor.pages):
        raise PaginaIndisponivel(
            f"pagina {page_number} fora do intervalo (1..{len(leitor.pages)})"
        )
    imagens = list(leitor.pages[page_number - 1].images)
    if not imagens:
        raise PaginaIndisponivel(f"pagina {page_number} sem imagem embutida")
    return imagens[0].data


def ja_processada(destino: Path) -> bool:
    """Retomada: só conta como feita a página com arquivo NÃO vazio.

    Arquivo de tamanho zero é rodada interrompida no meio da escrita, e tratá-lo
    como pronto deixaria buraco silencioso numa rodada de dezenas de horas.
    """
    try:
        return destino.stat().st_size > 0
    except OSError:
        return False


# --- métricas de comparação ------------------------------------------------


def metricas_de_texto(texto: str) -> dict:
    """Métricas cruas e auditáveis de qualidade, sem léxico externo.

    Léxico moderno rejeitaria a ortografia da época (hontem, cambio, actual) e
    mediria anacronismo em vez de ruído. Mesmas três métricas de
    `pipeline/analise/qualidade_ocr.py`, para comparar com a linha de base já
    publicada em `docs/relatorio-qualidade-ocr.md`.
    """
    tokens = TOKEN.findall(texto)
    if not tokens:
        return {
            "chars": len(texto),
            "tokens": 0,
            "taxa_sem_vogal": None,
            "taxa_hapax": None,
            "comprimento_medio": None,
        }
    contagem = Counter(token.lower() for token in tokens)
    return {
        "chars": len(texto),
        "tokens": len(tokens),
        "taxa_sem_vogal": sum(
            1 for token in tokens if not VOGAL.search(token)
        ) / len(tokens),
        "taxa_hapax": sum(1 for n in contagem.values() if n == 1) / len(contagem),
        "comprimento_medio": sum(len(t) for t in tokens) / len(tokens),
    }


def compara_camadas(texto_bn: str, texto_novo: str) -> dict:
    """As duas pontas e a diferença. Negativo em `delta_sem_vogal` é melhora."""
    bn = metricas_de_texto(texto_bn)
    novo = metricas_de_texto(texto_novo)
    delta = None
    if bn["taxa_sem_vogal"] is not None and novo["taxa_sem_vogal"] is not None:
        delta = novo["taxa_sem_vogal"] - bn["taxa_sem_vogal"]
    return {"bn": bn, "novo": novo, "delta_sem_vogal": delta}


# --- manifesto -------------------------------------------------------------


def sha256_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def registro_de_pagina(
    *,
    bib: str,
    ano: int,
    source_identifier: str,
    page_number: int,
    texto: str | None,
    parametros: Parametros,
    motor: dict,
    duracao_s: float,
    erro: str = "",
) -> dict:
    """Uma linha de manifesto por página tentada, com ou sem sucesso."""
    if texto is None:
        status, sha, chars = "falha", None, 0
    elif not texto.strip():
        status, sha, chars = "vazio", sha256_texto(texto), len(texto)
    else:
        status, sha, chars = "ok", sha256_texto(texto), len(texto)

    return {
        "bib": bib,
        "jornal": BIB2JORNAL.get(bib, bib),
        "ano": ano,
        "source_identifier": source_identifier,
        "page_number": page_number,
        "protocol_name": PROTOCOLO,
        "protocol_version": VERSAO,
        "engine": motor.get("engine", ""),
        "engine_version": motor.get("version", ""),
        "leptonica": motor.get("leptonica", ""),
        "idioma": parametros.idioma,
        "psm": parametros.psm,
        "oem": parametros.oem,
        "variante_tessdata": parametros.variante,
        "escala": parametros.escala,
        "status": status,
        "text_sha256": sha,
        "char_count": chars,
        "duracao_s": round(duracao_s, 2),
        "erro": erro,
    }


CAMPOS = [
    "bib", "jornal", "ano", "source_identifier", "page_number",
    "protocol_name", "protocol_version", "engine", "engine_version",
    "leptonica", "idioma", "psm", "oem", "variante_tessdata", "status",
    "escala", "text_sha256", "char_count", "duracao_s", "erro",
]


# --- execução --------------------------------------------------------------


def paginas_do_censo() -> list[dict]:
    """Todas as páginas do corpus, direto dos manifestos de triagem.

    O censo de triagem é o inventário completo das 117.705 páginas, e usá-lo
    como fonte da lista mantém esta camada alinhada com tudo que já foi medido.
    Ordem determinística.
    """
    import glob

    tarefas: list[dict] = []
    for caminho in sorted(glob.glob(str(RAIZ / "dados/triagem/triagem_nome_*.csv"))):
        bib, ano = Path(caminho).stem.split("_")[2:4]
        with open(caminho, encoding="utf-8", newline="") as arquivo:
            for linha in csv.DictReader(arquivo):
                tarefas.append(
                    {
                        "bib": bib,
                        "ano": int(ano),
                        "source_identifier": linha["source_identifier"],
                        "page_number": int(linha["page_number"]),
                        "hit_censo": 1 if linha["hit"] == "1" else 0,
                    }
                )
    tarefas.sort(
        key=lambda t: (t["bib"], t["ano"], t["source_identifier"], t["page_number"])
    )
    return tarefas


def filtra_braco(tarefas: list[dict], braco: str) -> list[dict]:
    """Recorta o censo por braço.

    `com_mencao` é o braço de sensibilidade: em página que sabidamente traz o
    nome, o motor novo acha o que a camada da BN achou? Sem essa medida, uma
    taxa de recall medida em página aleatória não tem como ser corrigida.
    """
    if braco == "com_mencao":
        return [t for t in tarefas if t["hit_censo"] == 1]
    if braco == "sem_mencao":
        return [t for t in tarefas if t["hit_censo"] == 0]
    return tarefas


def amostra_por_celula(tarefas: list[dict], por_celula: int, semente: int) -> list[dict]:
    """Amostra determinística estratificada nas células jornal-ano."""
    celulas: dict[tuple[str, int], list[dict]] = {}
    for tarefa in tarefas:
        celulas.setdefault((tarefa["bib"], tarefa["ano"]), []).append(tarefa)
    escolhidas: list[dict] = []
    for n, chave in enumerate(sorted(celulas)):
        populacao = celulas[chave]
        quantas = min(por_celula, len(populacao))
        indices = random.Random(semente + n).sample(range(len(populacao)), quantas)
        escolhidas += [populacao[i] for i in sorted(indices)]
    return escolhidas


_MOTOR: dict = {}
_PARAMETROS: Parametros = PARAMETROS_PADRAO
_DIR_SAIDA: Path = DIR_SAIDA


def _inicia_worker(
    parametros: Parametros, dir_saida: Path
) -> None:  # pragma: no cover - subprocesso
    global _MOTOR, _PARAMETROS, _DIR_SAIDA
    _PARAMETROS = parametros
    _DIR_SAIDA = dir_saida
    _MOTOR = versao_do_motor()


def processa_tarefa(tarefa: dict) -> dict:  # pragma: no cover - subprocesso
    """Extrai, OCRa, grava o texto e devolve a linha de manifesto."""
    destino = caminho_saida(
        tarefa["bib"], tarefa["source_identifier"], tarefa["page_number"], _DIR_SAIDA
    )
    inicio = time.time()
    if ja_processada(destino):
        texto = destino.read_text(encoding="utf-8", errors="replace")
        registro = registro_de_pagina(
            bib=tarefa["bib"], ano=tarefa["ano"],
            source_identifier=tarefa["source_identifier"],
            page_number=tarefa["page_number"], texto=texto,
            parametros=_PARAMETROS, motor=_MOTOR, duracao_s=0.0,
        )
        registro["status"] = "retomada"
        return registro

    try:
        imagem = extrai_imagem(
            tarefa["bib"], tarefa["source_identifier"], tarefa["page_number"]
        )
        texto = roda_tesseract(
            prepara_imagem(imagem, _PARAMETROS.escala), _PARAMETROS, tempo_limite=900
        )
        erro = ""
    except Exception as excecao:  # noqa: BLE001 - a falha vira linha, não parada
        texto, erro = None, f"{type(excecao).__name__}: {excecao}"[:300]

    if texto is not None:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8", newline="\n")

    return registro_de_pagina(
        bib=tarefa["bib"], ano=tarefa["ano"],
        source_identifier=tarefa["source_identifier"],
        page_number=tarefa["page_number"], texto=texto,
        parametros=_PARAMETROS, motor=_MOTOR,
        duracao_s=time.time() - inicio, erro=erro,
    )


def main(argv: list[str] | None = None) -> int:
    import multiprocessing as mp

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--amostra", type=int, default=0, help="páginas por célula")
    parser.add_argument("--corpus", action="store_true", help="o corpus inteiro")
    parser.add_argument(
        "--executar",
        action="store_true",
        help="obrigatório com --corpus: dezenas de horas de CPU",
    )
    parser.add_argument("--compara", action="store_true", help="cabeça a cabeça com a BN")
    parser.add_argument("--workers", type=int, default=14)
    parser.add_argument("--psm", type=int, default=PARAMETROS_PADRAO.psm)
    parser.add_argument("--oem", type=int, default=PARAMETROS_PADRAO.oem)
    parser.add_argument("--variante", default=PARAMETROS_PADRAO.variante)
    parser.add_argument("--escala", type=float, default=1.0)
    parser.add_argument("--idioma", default=PARAMETROS_PADRAO.idioma)
    parser.add_argument("--semente", type=int, default=SEMENTE)
    parser.add_argument("--rotulo", default="", help="sufixo do manifesto")
    parser.add_argument("--manifesto", type=Path, default=DIR_MANIFESTO)
    parser.add_argument("--saida", type=Path, default=DIR_SAIDA)
    parser.add_argument(
        "--braco", choices=("todos", "com_mencao", "sem_mencao"), default="todos"
    )
    args = parser.parse_args(argv)

    if acha_binario() is None:
        parser.error("tesseract não encontrado no PATH nem em Program Files")
    if args.corpus and not args.executar:
        parser.error(
            "o corpus inteiro são dezenas de horas de CPU. Repita com --executar."
        )
    if not args.corpus and not args.amostra:
        parser.error("escolha --amostra N ou --corpus --executar")

    parametros = Parametros(
        idioma=args.idioma, psm=args.psm, oem=args.oem, variante=args.variante,
        escala=args.escala,
    )
    if not (DIR_TESSDATA / parametros.variante / f"{parametros.idioma}.traineddata").is_file():
        parser.error(
            f"traineddata ausente: {DIR_TESSDATA / parametros.variante}/"
            f"{parametros.idioma}.traineddata"
        )

    tarefas = filtra_braco(paginas_do_censo(), args.braco)
    if not args.corpus:
        tarefas = amostra_por_celula(tarefas, args.amostra, args.semente)
    motor = versao_do_motor()
    print(
        f"{len(tarefas)} páginas | {motor['engine']} {motor['version']} | "
        f"psm {parametros.psm} oem {parametros.oem} {parametros.variante} "
        f"{parametros.idioma} | {args.workers} processos"
    )

    args.manifesto.mkdir(parents=True, exist_ok=True)
    rotulo = args.rotulo or (
        "corpus" if args.corpus
        else f"amostra{args.amostra}_psm{args.psm}_{args.variante}"
    )

    inicio = time.time()
    registros: list[dict] = []
    with mp.Pool(
        processes=args.workers,
        initializer=_inicia_worker,
        initargs=(parametros, args.saida),
    ) as pool:
        for n, registro in enumerate(
            pool.imap_unordered(processa_tarefa, tarefas, chunksize=4), 1
        ):
            registros.append(registro)
            if n % 200 == 0 or n == len(tarefas):
                decorrido = time.time() - inicio
                restante = (len(tarefas) - n) * decorrido / n
                print(
                    f"  {n}/{len(tarefas)} | {decorrido/60:.1f} min | "
                    f"{n/decorrido*3600:.0f} pág/h | faltam {restante/3600:.1f} h",
                    flush=True,
                )
    duracao = time.time() - inicio

    registros.sort(
        key=lambda r: (r["bib"], r["ano"], r["source_identifier"], r["page_number"])
    )
    destino_manifesto = args.manifesto / f"manifesto_{rotulo}.csv"
    with open(destino_manifesto, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(registros)

    resumo = {
        "protocol_name": PROTOCOLO,
        "protocol_version": VERSAO,
        "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "motor": motor,
        "parametros": asdict(parametros),
        "semente": args.semente,
        "workers": args.workers,
        "paginas": len(registros),
        "duracao_segundos": round(duracao, 1),
        "segundos_por_pagina_por_worker": (
            round(sum(r["duracao_s"] for r in registros) / max(1, len(registros)), 2)
        ),
        "status": dict(Counter(r["status"] for r in registros)),
        "advertencia": (
            "Concordância entre dois OCRs não é verdade: os dois leem a mesma "
            "imagem degradada e podem errar junto, com erro correlacionado. "
            "Consenso é sinal de confiabilidade, nunca validação."
        ),
    }

    resumo["dir_saida"] = str(args.saida)
    if args.compara:
        resumo["comparacao"] = compara_com_a_bn(registros, args.saida)

    (args.manifesto / f"relatorio_{rotulo}.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    print(f"texto em {args.saida}\nmanifesto em {destino_manifesto}")
    return 0


def compara_com_a_bn(registros: list[dict], raiz: Path | None = None) -> dict:
    """Cabeça a cabeça por célula, só nas páginas em que as duas camadas existem."""
    por_celula: dict[tuple[str, int], list[dict]] = {}
    for registro in registros:
        if registro["status"] not in {"ok", "retomada"}:
            continue
        bn = caminho_bn(
            registro["bib"], registro["source_identifier"], registro["page_number"]
        )
        novo = caminho_saida(
            registro["bib"], registro["source_identifier"], registro["page_number"],
            raiz,
        )
        if not (bn.is_file() and novo.is_file()):
            continue
        comparacao = compara_camadas(
            bn.read_text(encoding="utf-8", errors="replace"),
            novo.read_text(encoding="utf-8", errors="replace"),
        )
        por_celula.setdefault(
            (registro["jornal"], registro["ano"]), []
        ).append(comparacao)

    def media(valores: list[float | None]) -> float | None:
        limpos = [v for v in valores if v is not None]
        return round(sum(limpos) / len(limpos), 5) if limpos else None

    celulas = []
    for (jornal, ano), itens in sorted(por_celula.items()):
        celulas.append(
            {
                "jornal": jornal,
                "ano": ano,
                "paginas": len(itens),
                "sem_vogal_bn": media([i["bn"]["taxa_sem_vogal"] for i in itens]),
                "sem_vogal_novo": media([i["novo"]["taxa_sem_vogal"] for i in itens]),
                "hapax_bn": media([i["bn"]["taxa_hapax"] for i in itens]),
                "hapax_novo": media([i["novo"]["taxa_hapax"] for i in itens]),
                "compr_bn": media([i["bn"]["comprimento_medio"] for i in itens]),
                "compr_novo": media([i["novo"]["comprimento_medio"] for i in itens]),
                "tokens_bn": media([i["bn"]["tokens"] for i in itens]),
                "tokens_novo": media([i["novo"]["tokens"] for i in itens]),
                "celula_melhorou": None,
            }
        )
        celulas[-1]["celula_melhorou"] = (
            celulas[-1]["sem_vogal_novo"] < celulas[-1]["sem_vogal_bn"]
        )

    todos = [item for itens in por_celula.values() for item in itens]
    return {
        "paginas_comparadas": len(todos),
        "celulas": celulas,
        "celulas_em_que_o_novo_ganhou": sum(1 for c in celulas if c["celula_melhorou"]),
        "total_de_celulas": len(celulas),
        "agregado": {
            "sem_vogal_bn": media([i["bn"]["taxa_sem_vogal"] for i in todos]),
            "sem_vogal_novo": media([i["novo"]["taxa_sem_vogal"] for i in todos]),
            "hapax_bn": media([i["bn"]["taxa_hapax"] for i in todos]),
            "hapax_novo": media([i["novo"]["taxa_hapax"] for i in todos]),
            "compr_bn": media([i["bn"]["comprimento_medio"] for i in todos]),
            "compr_novo": media([i["novo"]["comprimento_medio"] for i in todos]),
        },
    }


if __name__ == "__main__":
    raise SystemExit(main())
