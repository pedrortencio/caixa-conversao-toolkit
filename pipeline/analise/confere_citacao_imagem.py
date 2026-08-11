"""Confere cada citacao curada contra a IMAGEM do scan, nao contra o OCR.

`verifica_citacoes` responde uma pergunta: a linha existe no OCR da fonte, com
aquela grafia? Ela nao responde a pergunta que a dissertacao faz: o que esta
impresso na pagina? Quando o OCR entrega `111:1 lelcgraiimia de aos-sos
banqueiros`, a conferencia mecanica aprova e a citacao continua inutilizavel.

Este modulo produz a segunda camada. Para cada citacao do manifesto, extrai o
JPEG embutido no PDF da BN (o mesmo scan em que o piloto validou), pede a
Claude (visao) a transcricao VERBATIM do mesmo trecho lido na imagem, e guarda
as duas leituras lado a lado. O OCR nunca e sobrescrito: `citacao_verbatim`
permanece no manifesto de origem, e a leitura de imagem entra como coluna nova,
com modelo, versao e prompt registrados.

Duas guardas contra alucinacao, que e o risco especifico de deixar um modelo
"consertar" citacao:

1. ancoragem no OCR. A transcricao so passa se for reconhecivelmente a mesma
   passagem do OCR que ela diz corrigir. Isso barra a leitura que devolve outro
   trecho da pagina.
2. duas leituras. A pagina e lida duas vezes, em chamadas separadas, e a
   passagem so entra como `estavel` se as duas leituras coincidirem letra a
   letra. Onde discordam, a passagem e `instavel` e vai para o olho de Pedro.

Medido na rodada de 2026-08-03, e a razao de a primeira versao deste modulo ter
sido refeita: pedir "contexto em volta" junto da transcricao produziu
confabulacao franca. O modelo devolveu como contexto paragrafos inteiros
plausiveis e ausentes da pagina, enquanto as transcricoes pedidas trecho a
trecho seguiam o OCR de perto. Campo aberto convida invencao; campo ancorado num
trecho que ja existe, nao. Por isso o schema nao tem mais campo de contexto.

Nenhum veredito daqui dispensa Pedro de olhar a pagina, e duas leituras do mesmo
modelo nao sao dois anotadores: erro correlacionado passa pelas duas. O que o
modulo entrega e uma triagem, trocar "conferir 33 citacoes na imagem" por
"conferir as instaveis primeiro".

Estatuto: recuperacao/transcricao com proveniencia, do objeto 1. Nao seleciona,
nao descarta e nao estrutura informacao segundo o construto.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import re
import sys
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.triagem.recupera_amostra import imagem_b64

RAIZ = Path(__file__).resolve().parents[2]
RAW_PDF = Path("C:/dados-caixa/raw_pdf")
MANIFESTO_PADRAO = RAIZ / "dados" / "analise" / "mencoes_credor_externo.csv"
SAIDA_PADRAO = RAIZ / "dados" / "analise" / "citacoes_conferidas_imagem.csv"
PAGINAS_RETROSPECTO = RAIZ / "dados" / "retrospecto_jc" / "retrospecto_caixa_paginas.csv"

MODELO = "claude-sonnet-5"
# 1.1.0 muda apenas a reconciliacao, nao a leitura: acrescenta `adicoes_vs_ocr`
# e o veredito `estendida`. O prompt, o modelo e a chamada de API sao os mesmos
# de 1.0.0, entao passes gravados sob 1.0.0 continuam entrada valida e nao
# precisam ser relidos.
PROTOCOLO = "conferencia-citacao-imagem/claude-sonnet-5 1.1.0"
MAX_TOKENS = 8000
PRECO_IN, PRECO_OUT = 2.0, 10.0  # Sonnet 5, preco introdutorio por 1M tokens
TETO_USD = 3.0

# Abaixo deste limiar a "correcao" deixou de ser leitura do mesmo trecho.
# Calibrado contra o pior OCR do manifesto: `111:1 lelcgraiimia de aos-sos
# banqueiros em Londres` contra `um telegramma de nossos banqueiros em Londres`
# fica em torno de 0.70; ruido pior que isso merece olho humano de qualquer jeito.
LIMIAR_SIMILARIDADE = 0.60

# Crescimento liquido, em letras, a partir do qual um trecho deixa de ser
# recomposicao do que o OCR comeu e passa a ser extensao da passagem. Calibrado
# no piloto de 11/08 contra os dois extremos observados: `Kepit-Mica` virando
# `Republica` cresce zero e e o trabalho esperado da camada; `desconhe-` virando
# `desconhecidas aventuras.` cresce 14 e e texto que nao existe na pagina.
LIMIAR_ADICAO = 8

CABECALHO = [
    "id",
    "passe",
    "situacao",
    "similaridade",
    "citacao_ocr",
    "citacao_imagem",
    "legibilidade",
    "nota_visao",
    "pdf",
    "pagina_pdf",
    "modelo",
    "protocolo",
]

CABECALHO_RECONCILIADO = [
    "id",
    "veredito",
    "acordo_entre_leituras",
    "sim_ocr_leitura_1",
    "citacao_ocr",
    "leitura_1",
    "leitura_2",
    "omissoes_vs_ocr",
    "adicoes_vs_ocr",
    "legibilidade",
    "pdf",
    "pagina_pdf",
    "modelo",
    "protocolo",
]

PROMPT = """Esta imagem e a pagina de um impresso brasileiro de 1906-1914 \
(jornal diario ou anuario comercial), digitalizada pela Biblioteca Nacional. A \
camada de OCR desta pagina esta corrompida.

Abaixo estao trechos como o OCR os devolveu. Cada um corresponde a uma \
passagem REAL desta pagina. Sua tarefa e localizar cada passagem na IMAGEM e \
transcrever o que esta impresso.

{trechos}

Para cada trecho, devolva:
- id: o identificador dado acima
- encontrado: true se voce localizou a passagem na imagem
- transcricao: o MESMO trecho, na mesma extensao, transcrito VERBATIM da \
imagem. Preserve a ortografia da epoca (ph, th, y, consoante dobrada, \
acentuacao de 1906) exatamente como impressa. Junte palavra que a coluna \
partiu com hifen no fim da linha: transcreva `telegramma`, nao `tele-gramma`. \
NAO modernize, NAO corrija a gramatica do autor, NAO complete palavra que voce \
nao consegue ler. Palavra ilegivel vira [ilegivel].
- legibilidade: legivel, parcial ou ilegivel
- nota: o que atrapalhou a leitura, se algo atrapalhou (mancha, borrao, \
sangria da coluna vizinha, texto cortado na margem); senao null

Se voce NAO localizar a passagem na imagem, marque encontrado=false e deixe \
transcricao vazia. Nao invente, nao reconstrua por plausibilidade e nao \
devolva a propria string do OCR de volta: um trecho nao encontrado e um \
resultado legitimo e util."""


class Trecho(BaseModel):
    id: str
    encontrado: bool
    transcricao: str
    legibilidade: str
    nota: str | None


class Pagina(BaseModel):
    trechos: list[Trecho]


@dataclass(frozen=True, slots=True)
class Alvo:
    """Uma citacao do manifesto, resolvida ate a pagina fisica do PDF."""

    id: str
    citacao_ocr: str
    pdf: Path
    pagina_pdf: int


_SO_LETRAS = re.compile(r"[^a-z0-9]+")


def normaliza_para_comparar(texto: str) -> str:
    """Reduz as duas leituras ao que elas tem de comparavel: as letras.

    O OCR cola palavra na quebra de linha (`agentesfinanceiros`) e a leitura de
    imagem separa. Comparar com espaco puniria a leitura correta. Diacritico
    tambem sai, porque o OCR o perde de forma arbitraria.
    """
    nfkd = unicodedata.normalize("NFKD", texto.casefold())
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return _SO_LETRAS.sub("", sem_acento)


def similaridade(ocr: str, imagem: str) -> float:
    """Quanto a leitura de imagem se parece com o OCR que ela diz corrigir."""
    a, b = normaliza_para_comparar(ocr), normaliza_para_comparar(imagem)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def julga(trecho: Trecho, citacao_ocr: str, limiar: float = LIMIAR_SIMILARIDADE) -> tuple[str, float]:
    """Veredito de uma leitura isolada, contra o OCR que ela diz corrigir.

    `ok` aqui nao quer dizer citacao boa nem citacao conferida: quer dizer que a
    leitura e reconhecivelmente a mesma passagem, e nao outro trecho da pagina.
    O veredito que conta e o da reconciliacao entre as duas leituras.
    """
    if not trecho.encontrado or not trecho.transcricao.strip():
        return "nao_encontrada", 0.0
    sim = similaridade(citacao_ocr, trecho.transcricao)
    if sim < limiar:
        return "divergente", sim
    return "ok", sim


def reconcilia(leitura_1: str, leitura_2: str, citacao_ocr: str) -> tuple[str, float]:
    """Confronta duas leituras independentes da mesma passagem na mesma imagem.

    Duas leituras do mesmo modelo nao sao anotadores independentes e isto NAO e
    validacao: erro correlacionado sobrevive as duas. O que a segunda leitura
    pega e a leitura instavel, aquela em que o modelo esta preenchendo lacuna do
    scan por plausibilidade em vez de ler tinta. `cm1913-murtinho` e o caso: o
    OCR traz `ncerba`, uma leitura devolveu `occulta`. Passagem instavel nao vai
    para o texto sem que Pedro leia a pagina.
    """
    if not leitura_1.strip() or not leitura_2.strip():
        return "leitura_ausente", 0.0
    acordo = similaridade(leitura_1, leitura_2)
    # A ancoragem no OCR vem ANTES da comparacao entre as duas leituras: duas
    # leituras identicas e ambas erradas concordam perfeitamente, e concordancia
    # entre elas nao pode absolver o par de ter saido da passagem.
    if (
        similaridade(citacao_ocr, leitura_1) < LIMIAR_SIMILARIDADE
        or similaridade(citacao_ocr, leitura_2) < LIMIAR_SIMILARIDADE
    ):
        return "divergente_do_ocr", acordo
    # Antes de comparar as duas leituras entre si, pergunte se alguma delas
    # alongou a passagem. Concordancia nao absolve extensao pela mesma razao que
    # nao absolve fuga: o erro e correlacionado e sobrevive as duas leituras.
    if estendeu(citacao_ocr, leitura_1) or estendeu(citacao_ocr, leitura_2):
        return "estendida", acordo
    if normaliza_para_comparar(leitura_1) == normaliza_para_comparar(leitura_2):
        return "estavel", acordo
    return "instavel", acordo


def omissoes(citacao_ocr: str, leitura: str, minimo: int = 3) -> list[str]:
    """Sequencias de letras que o OCR tem e a leitura de imagem nao tem.

    A guarda que as duas leituras NAO dao. O modelo alisa: onde o scan esta
    sujo, ele entrega uma frase limpa e plausivel, mais curta que a impressa, e
    entrega a mesma nas duas passagens, porque o erro e correlacionado. Foi o que
    aconteceu com `gn1906-282-rei`: o OCR traz `reidos banqueiros londrinos`, que
    so pode ser `rei dos banqueiros londrinos`, e as duas leituras devolveram
    `dos banqueiros londrinos`, sem o `rei`. Justamente a metafora que motivou a
    varredura de perifrase.

    Ruido de OCR tambem aparece aqui, e isso e esperado: a lista e material de
    triagem para o olho humano, nao veredito.
    """
    palavras, dono = _letras_com_dono(citacao_ocr)
    a = "".join(letra for letra, _ in dono)
    b = normaliza_para_comparar(leitura)
    atingidas: list[int] = []
    for tag, i1, i2, _, _ in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag in {"delete", "replace"} and i2 - i1 >= minimo:
            atingidas.extend(indice for _, indice in dono[i1:i2])
    vistas: dict[int, None] = {}
    for indice in atingidas:
        vistas.setdefault(indice, None)
    return [palavras[i] for i in sorted(vistas)]


def adicoes(citacao_ocr: str, leitura: str, minimo: int = 3) -> list[str]:
    """Sequencias de letras que a leitura de imagem tem e o OCR nao tem.

    A guarda simetrica de `omissoes`, e a que faltava. `omissoes` pega o que o
    modelo alisou; nada pegava o que ele acrescentou, e acrescentar e o risco
    vivo. Medido em `cm1906-aventura`, no piloto de 11/08: o OCR termina em
    `novas e desconhe-`, na quebra da coluna, e as DUAS leituras devolveram
    `novas e desconhecidas aventuras.`. Os vinte caracteres finais nao existem
    em nenhum lugar da pagina. O veredito saiu `estavel`, porque as duas
    leituras concordam, e elas concordam porque o erro e correlacionado: e a
    completacao obvia da frase, e o mesmo modelo a completa duas vezes igual.

    Pode ate ser leitura legitima de tinta que o OCR perdeu. O ponto e que o
    protocolo nao distingue isso de confabulacao, e por isso a adicao vai para
    o olho humano em vez de para o texto.

    E `omissoes` com os papeis trocados: o que a leitura tem e o OCR nao tem.
    """
    return omissoes(leitura, citacao_ocr, minimo)


def casamento_na_pagina(agulha: str, pagina: str) -> float:
    """Quanto do trecho acrescentado existe no OCR da PAGINA INTEIRA.

    `estendida` diz que a leitura foi alem da ancora. Nao diz por que, e as duas
    causas pedem acoes opostas. Medido nas cinco `estendida` conhecidas em
    11/08/2026:

    - ancora curta, tres casos. `op1912-quebra` acrescentou `Que diriam de tal
      acto?` e a frase casa a 1,00 com o OCR da pagina; `cm1914-posse`
      acrescentou `Barroso`, casa a 1,00; `op1910-concordata` acrescentou
      `tantos abalos,` e a pagina traz `utantosabalo`, casa a 0,92. Nesses a
      leitura esta certa e quem estava curto era o `citacao_verbatim` curado. A
      acao e estender a ancora, nao descartar a leitura.
    - invencao, um caso. `cm1906-aventura` acrescentou `desconhecidas
      aventuras.` e nao ha ocorrencia de `aventur` nem de `cidas` nos 42.510
      caracteres da pagina. A acao e descartar.

    Compara pelo maior bloco contiguo em comum, e nao pela razao global, porque
    a agulha tem dezenas de caracteres e o palheiro tem dezenas de milhares.
    `autojunk` fica desligado: com ele o difflib trata como lixo o caractere
    frequente numa sequencia longa, que numa pagina de jornal e toda vogal.

    Nao decide sozinho. Casamento alto num trecho curto e comum, `de`, `que`,
    pode ser coincidencia, e a ultima palavra continua sendo a da imagem.
    """
    a = normaliza_para_comparar(agulha)
    b = normaliza_para_comparar(pagina)
    if not a or not b:
        return 0.0
    bloco = difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(
        0, len(a), 0, len(b)
    )
    return bloco.size / len(a)


def _crescimento_maximo(citacao_ocr: str, leitura: str) -> int:
    """Maior crescimento liquido, em letras, de um unico trecho da leitura.

    Nao basta medir o tamanho do trecho inserido. `Kepit-Mica` virando
    `Republica` e uma substituicao de nove letras por nove letras, e e
    exatamente o que se quer da camada de visao. O que denuncia extensao da
    passagem e o SALDO: quanto a leitura cresceu alem do que o OCR ancora
    naquele mesmo ponto. Por isso `replace` conta apenas o excedente, e so
    `insert` conta integralmente.
    """
    a = normaliza_para_comparar(citacao_ocr)
    b = normaliza_para_comparar(leitura)
    maior = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag == "insert":
            maior = max(maior, j2 - j1)
        elif tag == "replace":
            maior = max(maior, (j2 - j1) - (i2 - i1))
    return maior


def estendeu(citacao_ocr: str, leitura: str, limiar: int | None = None) -> bool:
    """A leitura alongou a passagem alem do que o OCR ancora.

    O limiar e lido em tempo de chamada, e nao amarrado como default, para que
    a calibracao possa varrer valores sem editar o modulo.
    """
    if limiar is None:
        limiar = LIMIAR_ADICAO
    return _crescimento_maximo(citacao_ocr, leitura) >= limiar


def _letras_com_dono(texto: str) -> tuple[list[str], list[tuple[str, int]]]:
    """Letras normalizadas, cada uma sabendo de que palavra do OCR ela veio.

    A comparacao tem de correr sobre letras, porque o OCR cola palavra na quebra
    de linha; o relato tem de sair em palavras, porque quem le e uma pessoa.
    """
    palavras: list[str] = []
    dono: list[tuple[str, int]] = []
    for bruta in texto.split():
        limpa = normaliza_para_comparar(bruta)
        if not limpa:
            continue
        indice = len(palavras)
        palavras.append(bruta)
        dono.extend((letra, indice) for letra in limpa)
    return palavras, dono


def caminho_do_pdf(bib: str, objeto: str, raw_pdf: Path = RAW_PDF) -> Path:
    return raw_pdf / bib / f"{objeto}.pdf"


def caminho_do_retrospecto(ano: str, raw_pdf: Path = RAW_PDF) -> Path:
    return raw_pdf / "jc_retrospecto" / f"per180688_{int(ano)}_00001.pdf"


def pagina_do_retrospecto(ano: str, citacao: str, linhas: list[dict]) -> int:
    """Pagina fisica do volume anual que contem a citacao.

    O Retrospecto nao tem uma pagina por arquivo: o ano inteiro e um PDF so. A
    pagina sai do censo de paginas ja extraido, por casamento literal do texto,
    e nao de estimativa.
    """
    alvo = normaliza_para_comparar(citacao)
    achados = [
        int(linha["page_number"])
        for linha in linhas
        if linha["ano"] == str(int(ano)) and alvo in normaliza_para_comparar(linha["texto"])
    ]
    if not achados:
        raise ValueError(f"citacao nao localizada no censo de paginas do retrospecto {ano}")
    return achados[0]


def resolve_alvos(
    linhas_manifesto: list[dict],
    linhas_retrospecto: list[dict],
    raw_pdf: Path = RAW_PDF,
) -> list[Alvo]:
    alvos = []
    for linha in linhas_manifesto:
        citacao = (linha.get("citacao_verbatim") or "").strip()
        if linha["fonte_tipo"] == "pagina":
            pdf = caminho_do_pdf(linha["bib"], linha["objeto"], raw_pdf)
            pagina = int(linha["pagina"])
        elif linha["fonte_tipo"] == "retrospecto":
            pdf = caminho_do_retrospecto(linha["ano"], raw_pdf)
            pagina = pagina_do_retrospecto(linha["ano"], citacao, linhas_retrospecto)
        else:
            raise ValueError(f"fonte_tipo desconhecido: {linha['fonte_tipo']!r}")
        alvos.append(Alvo(linha["id"], citacao, pdf, pagina))
    return alvos


def agrupa_por_pagina(alvos: list[Alvo]) -> dict[tuple[Path, int], list[Alvo]]:
    """Uma chamada por pagina: quatro citacoes da mesma pagina custam uma."""
    grupos: dict[tuple[Path, int], list[Alvo]] = {}
    for alvo in alvos:
        grupos.setdefault((alvo.pdf, alvo.pagina_pdf), []).append(alvo)
    return grupos


def monta_prompt(alvos: list[Alvo]) -> str:
    trechos = "\n\n".join(f"[{a.id}]\n{a.citacao_ocr}" for a in alvos)
    return PROMPT.format(trechos=trechos)


def le_pagina(
    client: anthropic.Anthropic, b64: str, alvos: list[Alvo], max_tokens: int = MAX_TOKENS
) -> tuple[Pagina, int, int]:
    resposta = client.messages.parse(
        model=MODELO,
        max_tokens=max_tokens,
        thinking={"type": "disabled"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
                    },
                    {"type": "text", "text": monta_prompt(alvos)},
                ],
            }
        ],
        output_format=Pagina,
    )
    return resposta.parsed_output, resposta.usage.input_tokens, resposta.usage.output_tokens


def _com_retry(
    client: anthropic.Anthropic,
    b64: str,
    alvos: list[Alvo],
    *,
    max_tokens: int = MAX_TOKENS,
    tentativas: int = 3,
) -> tuple[Pagina, int, int]:
    ultimo: Exception | None = None
    for k in range(tentativas):
        try:
            return le_pagina(client, b64, alvos, max_tokens=max_tokens)
        except (
            anthropic.RateLimitError,
            anthropic.APIStatusError,
            anthropic.APIConnectionError,
        ) as erro:
            ultimo = erro
            time.sleep(2**k)
    assert ultimo is not None
    raise ultimo


def _ja_feitos(caminho: Path) -> set[str]:
    if not caminho.exists():
        return set()
    with caminho.open(encoding="utf-8", newline="") as entrada:
        return {linha["id"] for linha in csv.DictReader(entrada)}


def _le_csv(caminho: Path) -> list[dict]:
    csv.field_size_limit(10**9)  # a coluna texto do retrospecto tem pagina inteira
    with caminho.open(encoding="utf-8", newline="") as entrada:
        return list(csv.DictReader(entrada))


def caminho_do_passe(passe: int, saida_base: Path = SAIDA_PADRAO) -> Path:
    return saida_base.with_name(f"leitura_imagem_passe{passe}.csv")


def junta_passes(
    linhas_1: list[dict], linhas_2: list[dict], modelo: str = MODELO, protocolo: str = PROTOCOLO
) -> list[dict]:
    """Reconcilia as duas leituras e devolve o manifesto final, por citacao."""
    por_id_2 = {linha["id"]: linha for linha in linhas_2}
    reconciliado = []
    for linha_1 in linhas_1:
        linha_2 = por_id_2.get(linha_1["id"], {})
        leitura_1 = linha_1.get("citacao_imagem", "")
        leitura_2 = linha_2.get("citacao_imagem", "")
        ocr = linha_1["citacao_ocr"]
        veredito, acordo = reconcilia(leitura_1, leitura_2, ocr)
        reconciliado.append(
            {
                "id": linha_1["id"],
                "veredito": veredito,
                "acordo_entre_leituras": f"{acordo:.3f}",
                "sim_ocr_leitura_1": linha_1.get("similaridade", ""),
                "citacao_ocr": ocr,
                "leitura_1": leitura_1,
                "leitura_2": leitura_2,
                "omissoes_vs_ocr": " | ".join(omissoes(ocr, leitura_1)),
                "adicoes_vs_ocr": " | ".join(adicoes(ocr, leitura_1)),
                "legibilidade": linha_1.get("legibilidade", ""),
                "pdf": linha_1.get("pdf", ""),
                "pagina_pdf": linha_1.get("pagina_pdf", ""),
                "modelo": modelo,
                "protocolo": protocolo,
            }
        )
    return reconciliado


def _reconcilia_arquivos(saida_base: Path) -> int:  # pragma: no cover - linha de comando
    linhas_1 = _le_csv(caminho_do_passe(1, saida_base))
    linhas_2 = _le_csv(caminho_do_passe(2, saida_base))
    reconciliado = junta_passes(linhas_1, linhas_2)
    with saida_base.open("w", encoding="utf-8", newline="") as fout:
        escritor = csv.DictWriter(fout, CABECALHO_RECONCILIADO, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(reconciliado)
    contagem: dict[str, int] = {}
    for linha in reconciliado:
        contagem[linha["veredito"]] = contagem.get(linha["veredito"], 0) + 1
    for veredito, n in sorted(contagem.items(), key=lambda kv: -kv[1]):
        print(f"  {veredito:20s} {n}")
    print(f"\n{len(reconciliado)} citacoes reconciliadas em {saida_base}")
    return 0


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - linha de comando
    parser = argparse.ArgumentParser(
        description="Confere as citacoes curadas contra a imagem do scan"
    )
    parser.add_argument("--manifesto", default=str(MANIFESTO_PADRAO))
    parser.add_argument("--saida", default=str(SAIDA_PADRAO))
    parser.add_argument("--passe", type=int, default=1, choices=(1, 2),
                        help="qual das duas leituras independentes rodar")
    parser.add_argument("--reconciliar", action="store_true",
                        help="nao chama a API: junta os dois passes ja gravados")
    parser.add_argument("--teto-usd", type=float, default=TETO_USD)
    parser.add_argument("--limite", type=int, default=None, help="max de paginas nesta rodada")
    parser.add_argument("--so-estimar", action="store_true", help="nao chama a API")
    args = parser.parse_args(argv)

    if args.reconciliar:
        return _reconcilia_arquivos(Path(args.saida))

    alvos = resolve_alvos(_le_csv(Path(args.manifesto)), _le_csv(PAGINAS_RETROSPECTO))
    grupos = agrupa_por_pagina(alvos)
    saida = caminho_do_passe(args.passe, Path(args.saida))
    feitos = _ja_feitos(saida)
    pendentes = {
        chave: lista
        for chave, lista in grupos.items()
        if any(a.id not in feitos for a in lista)
    }

    print(f"{len(alvos)} citacoes em {len(grupos)} paginas; {len(pendentes)} paginas pendentes")
    faltando = [chave for chave in pendentes if not chave[0].is_file()]
    for pdf, pagina in faltando:
        print(f"  PDF AUSENTE {pdf} p{pagina}")
    # ~4.8k tokens de imagem + prompt, saida curta: ~$0.025 por pagina medidos
    # na recuperacao de 2026-07-22.
    print(f"custo estimado: ~${0.025 * len(pendentes):.2f} (teto ${args.teto_usd:.2f})")
    if args.so_estimar:
        return 0

    load_dotenv(RAIZ / ".env")
    client = anthropic.Anthropic()
    novo = not saida.exists()
    saida.parent.mkdir(parents=True, exist_ok=True)

    custo = 0.0
    n_pag = 0
    with saida.open("a", encoding="utf-8", newline="") as fout:
        escritor = csv.writer(fout, lineterminator="\n")
        if novo:
            escritor.writerow(CABECALHO)
        for (pdf, pagina), lista in sorted(pendentes.items(), key=lambda kv: str(kv[0])):
            if custo >= args.teto_usd:
                print(f"[teto] parando: ${custo:.2f} >= ${args.teto_usd:.2f}", flush=True)
                break
            if args.limite is not None and n_pag >= args.limite:
                break
            faltantes = [a for a in lista if a.id not in feitos]
            try:
                b64 = imagem_b64(str(pdf), pagina)
                lido, ti, to = _com_retry(client, b64, faltantes)
            except Exception as erro:  # registro positivo do erro, segue
                for alvo in faltantes:
                    escritor.writerow(
                        [alvo.id, args.passe, "erro", "", alvo.citacao_ocr, "", "",
                         str(erro)[:200], pdf.name, pagina, MODELO, PROTOCOLO]
                    )
                fout.flush()
                print(f"[{pdf.name} p{pagina}] ERRO {type(erro).__name__}: {erro}", flush=True)
                continue
            custo += ti / 1e6 * PRECO_IN + to / 1e6 * PRECO_OUT
            n_pag += 1

            por_id = {t.id: t for t in lido.trechos}
            for alvo in faltantes:
                trecho = por_id.get(alvo.id)
                if trecho is None:
                    escritor.writerow(
                        [alvo.id, args.passe, "sem_resposta", "", alvo.citacao_ocr, "", "", "",
                         pdf.name, pagina, MODELO, PROTOCOLO]
                    )
                    continue
                situacao, sim = julga(trecho, alvo.citacao_ocr)
                escritor.writerow(
                    [alvo.id, args.passe, situacao, f"{sim:.3f}", alvo.citacao_ocr,
                     trecho.transcricao, trecho.legibilidade, trecho.nota or "",
                     pdf.name, pagina, MODELO, PROTOCOLO]
                )
                print(f"  {situacao:15s} {sim:.3f}  {alvo.id}", flush=True)
            fout.flush()

    print(f"\nfeito: {n_pag} paginas, custo ${custo:.2f}", flush=True)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
