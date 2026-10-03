"""Sonda difusa: quantas menções à Caixa de Conversão o censo perdeu?

O censo por nome (`regra_nome`, protocolo `nome-caixa-conversao` 1.0.0) marcou
8.331 páginas com menção e 109.372 sem. O casador é tolerante a ruído de OCR,
mas é EXATO no radical: exige "caixa", conector curto começando por "d", e o
radical "conver". Onde o OCR da BN partiu "caixa" ao meio ("cai-xa", "ca xa"),
comeu o conector ("caixa,1c conversao") ou trocou letra dentro do radical, a
página caiu no lado errado e ninguém sabe quantas são.

Esta sonda é um SEGUNDO instrumento, paralelo e deliberadamente mais tolerante,
que existe só para medir essa falha. Ela não é um casador de produção, não
substitui `regra_nome` e não altera o censo: trocar o casador deslocaria o
portão de 1906, cujo gabarito de 426 números distintos é medido contra o censo
atual, e isso é decisão do Pedro, com entrada em `docs/decisoes.md`.

Como funciona, em duas etapas:

1. **Geração barata de candidatos.** Uma expressão regular casa "caixa" com até
   um erro (substituição, deleção ou inserção), um vão de até 6 caracteres, e
   "conver" com até um erro. Roda em C sobre o texto normalizado, a cerca de
   34 MB/s, o que torna o corpus inteiro viável sem OCR novo e sem token pago.
2. **Pontuação cara, só nos candidatos.** Para cada candidato, a distância de
   edição de Levenshtein entre a forma canônica "caixa de conversao" e a melhor
   subcadeia da janela (início e fim livres do lado da janela, padrão consumido
   inteiro). Distância 0 é o nome intacto; 1 a 3 é o nome com ruído; acima
   disso, a leitura humana decide.

O que a sonda NÃO acha, e por isso o número que ela devolve é **cota inferior**
e não estimativa: página em que OCR destruiu as DUAS âncoras ao mesmo tempo
("Cnixn" perto de "Convorsão"), e menção que não usa o nome (anáfora, "a Caixa",
"o troco"). O braço de OCR novo, que é a outra testemunha, é que fecha esse
flanco. E vale a advertência que governa as duas testemunhas: **concordância
entre dois leitores da mesma imagem degradada não é verdade**, os dois podem
errar junto, com erro correlacionado. Consenso é sinal de confiabilidade, nunca
validação.

Uso:
  uv run python -m pipeline.triagem.sonda_difusa --limite 2000
  uv run python -m pipeline.triagem.sonda_difusa --braco ambos
"""

from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import re
import sys
import time
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - conveniência de execução direta
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.triagem import regra_nome

PROTOCOLO = "sonda-difusa-caixa-conversao"
VERSAO = "1.0.0"
SONDA_VERSAO = f"triagem/{PROTOCOLO} {VERSAO}"

RAIZ = Path(__file__).resolve().parents[2]
DIR_BRUTO = Path("C:/dados-caixa/texto_embutido")
DIR_SAIDA = RAIZ / "dados" / "triagem" / "sonda_difusa"

BIB2JORNAL = {
    "089842": "correio_manha",
    "090972": "correio_paulistano",
    "103730": "gazeta_noticias",
    "178691": "o_paiz",
}

#: Forma canônica, já normalizada como `regra_nome.normaliza` normaliza.
CANONICA = "caixa de conversao"

#: Âncoras da regex de candidatos. "conver" é o mesmo radical mínimo do casador
#: exato: encurtá-lo para "conv" traria de graça a família convenio/convite.
ANCORA_ESQUERDA = "caixa"
ANCORA_DIREITA = "conver"

#: Vão máximo entre as âncoras. O conector real é "de" (4 caracteres com os
#: espaços); 6 cobre "d e ", ",1c ", " rie " e o espúrio que o OCR insere.
VAO_MAXIMO = 6

#: Folga da janela pontuada, à esquerda e à direita do casamento da regex. À
#: direita precisa caber o "sao" que a âncora não exige.
FOLGA_ESQUERDA = 2
FOLGA_DIREITA = 10

#: Acima disso o candidato nem entra no manifesto: é ruído de regex, não
#: quase-acerto. 8 de 18 caracteres já é 44% do nome errado.
DISTANCIA_MAXIMA_REGISTRADA = 8

#: Limiar de decisão da cota inferior, calibrado por leitura dos trechos.
LIMIAR_QUASE_ACERTO = 3

CONTEXTO_JANELA = 60


@dataclass(frozen=True, slots=True)
class Candidato:
    """Quase-acerto pontuado, com offsets no texto NORMALIZADO da página."""

    offset: int
    fim: int
    trecho: str
    contexto: str
    distancia: int
    distancia_normalizada: float
    sobrepoe_exato: bool


def variantes_com_um_erro(palavra: str) -> list[str]:
    """Formas da palavra a até um erro, como pedaços de regex.

    Substituição e inserção viram `.` (qualquer caractere, que é como o OCR
    erra: troca letra, mete hífen, abre espaço no meio); deleção some com o
    caractere. Ordenadas da mais longa para a mais curta e sem repetição, para
    que a alternância da regex seja determinística e prefira o casamento mais
    específico.
    """
    formas = {palavra}
    for i in range(len(palavra)):
        formas.add(palavra[:i] + "." + palavra[i + 1 :])  # substituição
        formas.add(palavra[:i] + palavra[i + 1 :])  # deleção
    for i in range(len(palavra) + 1):
        formas.add(palavra[:i] + "." + palavra[i:])  # inserção
    return sorted(formas, key=lambda forma: (-len(forma), forma))


def _ancora(palavra: str) -> str:
    return "(?:" + "|".join(variantes_com_um_erro(palavra)) + ")"


PADRAO_CANDIDATO = re.compile(
    _ancora(ANCORA_ESQUERDA) + rf".{{0,{VAO_MAXIMO}}}?" + _ancora(ANCORA_DIREITA),
    re.DOTALL,
)


def distancia_subcadeia(padrao: str, janela: str) -> int:
    """Menor distância de edição entre `padrao` e alguma subcadeia de `janela`.

    Levenshtein com início e fim livres **do lado da janela**: a janela pode
    sobrar dos dois lados sem custo, o padrão tem de ser consumido inteiro.
    É a medida certa aqui porque a janela é um recorte arbitrário do texto e
    o que se quer saber é o custo de ler ali a forma canônica.
    """
    anterior = [0] * (len(janela) + 1)
    for i, caractere_padrao in enumerate(padrao, 1):
        atual = [i] + [0] * len(janela)
        for j, caractere_janela in enumerate(janela, 1):
            atual[j] = min(
                anterior[j] + 1,
                atual[j - 1] + 1,
                anterior[j - 1] + (caractere_padrao != caractere_janela),
            )
        anterior = atual
    return min(anterior)


def encontra_difuso(
    texto: str, *, distancia_maxima: int = DISTANCIA_MAXIMA_REGISTRADA
) -> list[Candidato]:
    """Candidatos a menção corrompida no texto (cru) de uma página.

    Normaliza pela MESMA função do casador exato, para que os offsets das duas
    medidas sejam comparáveis, e marca quais candidatos o casador exato já
    tinha achado. Determinístico: mesmo texto, mesma saída, mesma ordem.
    """
    normalizado = regra_nome.normaliza(texto)
    exatos = [
        (span.offset, span.offset + len(span.texto))
        for span in regra_nome.encontra(texto)
    ]

    candidatos: list[Candidato] = []
    for casado in PADRAO_CANDIDATO.finditer(normalizado):
        inicio, fim = casado.span()
        janela = normalizado[
            max(0, inicio - FOLGA_ESQUERDA) : fim + FOLGA_DIREITA
        ]
        distancia = distancia_subcadeia(CANONICA, janela)
        if distancia > distancia_maxima:
            continue
        candidatos.append(
            Candidato(
                offset=inicio,
                fim=fim,
                trecho=casado.group(0),
                contexto=normalizado[
                    max(0, inicio - CONTEXTO_JANELA) : fim + CONTEXTO_JANELA
                ],
                distancia=distancia,
                distancia_normalizada=round(distancia / len(CANONICA), 4),
                sobrepoe_exato=any(
                    inicio < fim_exato and inicio_exato < fim
                    for inicio_exato, fim_exato in exatos
                ),
            )
        )
    return candidatos


def sha256_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def sem_controle(texto: str) -> str:
    """Troca caractere de controle por espaço, só para o CSV ser legível.

    Não é limpeza de dado: o offset gravado devolve o trecho exato no texto
    normalizado da página, então nada aqui é irreversível.
    """
    return "".join(
        " " if unicodedata.category(c) == "Cc" else c for c in texto
    )


def registro_de_pagina(
    *,
    bib: str,
    ano: int,
    source_identifier: str,
    page_number: int,
    hit_censo: int,
    texto: str | None,
    distancia_maxima: int = DISTANCIA_MAXIMA_REGISTRADA,
) -> dict:
    """Uma linha de manifesto por página examinada, sempre.

    Página que não pôde ser lida ou que não tem texto vira linha com status
    próprio, nunca sumiço: ausência é registrada positivamente, não inferida
    do silêncio.
    """
    comum = {
        "bib": bib,
        "jornal": BIB2JORNAL.get(bib, bib),
        "ano": ano,
        "source_identifier": source_identifier,
        "page_number": page_number,
        "hit_censo": hit_censo,
        "protocol_name": PROTOCOLO,
        "protocol_version": VERSAO,
    }
    if texto is None:
        return {
            **comum,
            "status": "arquivo_ausente",
            "texto_sha256": None,
            "n_candidatos": 0,
            "melhor_distancia": None,
            "candidatos": [],
        }
    if not texto.strip():
        return {
            **comum,
            "status": "empty",
            "texto_sha256": sha256_texto(texto),
            "n_candidatos": 0,
            "melhor_distancia": None,
            "candidatos": [],
        }

    candidatos = encontra_difuso(texto, distancia_maxima=distancia_maxima)
    return {
        **comum,
        "status": "ok",
        "texto_sha256": sha256_texto(texto),
        "n_candidatos": len(candidatos),
        "melhor_distancia": (
            min(c.distancia for c in candidatos) if candidatos else None
        ),
        "candidatos": candidatos,
    }


def agrega_celulas(registros: list[dict]) -> list[dict]:
    """Contagens por célula jornal-ano-braço, com as parcelas fechando o total.

    O braço é `hit_censo`: 1 são as 8.331 páginas que o censo marcou (braço de
    calibração), 0 são as 109.372 que ele descartou (braço de recall). Manter
    os dois separados é o que permite comparar a taxa de candidatos difusos
    entre páginas que sabidamente falam do assunto e páginas que o censo diz
    que não falam.
    """
    celulas: dict[tuple[str, int, int], dict] = {}
    for registro in registros:
        chave = (registro["bib"], registro["ano"], registro["hit_censo"])
        celula = celulas.get(chave)
        if celula is None:
            celula = {
                "bib": registro["bib"],
                "jornal": registro["jornal"],
                "ano": registro["ano"],
                "hit_censo": registro["hit_censo"],
                "paginas": 0,
                "paginas_ok": 0,
                "paginas_vazias": 0,
                "paginas_ausentes": 0,
                "candidatos": 0,
                **{
                    f"paginas_d{n}": 0
                    for n in range(DISTANCIA_MAXIMA_REGISTRADA + 1)
                },
            }
            celulas[chave] = celula

        celula["paginas"] += 1
        celula["candidatos"] += registro["n_candidatos"]
        if registro["status"] == "ok":
            celula["paginas_ok"] += 1
        elif registro["status"] == "empty":
            celula["paginas_vazias"] += 1
        else:
            celula["paginas_ausentes"] += 1

        melhor = registro["melhor_distancia"]
        if melhor is not None:
            for n in range(melhor, DISTANCIA_MAXIMA_REGISTRADA + 1):
                celula[f"paginas_d{n}"] += 1

    return [celulas[chave] for chave in sorted(celulas)]


def trechos_para_inspecao(
    linhas: list[dict], limiar: int, quantidade: int = 200
) -> list[dict]:
    """Os `quantidade` candidatos mais próximos do limiar de decisão.

    São os casos em que a máquina está menos segura, dos dois lados do corte, e
    por isso os que a leitura humana precisa ver para dizer se o limiar está no
    lugar. Ordem determinística, com desempate por identificador.
    """
    return sorted(
        linhas,
        key=lambda linha: (
            abs(linha["distancia"] - limiar),
            linha["distancia"],
            linha["bib"],
            linha["source_identifier"],
            linha["page_number"],
            linha["offset"],
        ),
    )[:quantidade]


# --- leitura do censo e execução -------------------------------------------


def paginas_do_censo(braco: str = "ambos") -> list[dict]:
    """Páginas a examinar, direto dos manifestos versionados da triagem.

    `braco`: "sem_mencao" (hit=0, o braço de recall), "com_mencao" (hit=1, o
    braço de calibração) ou "ambos". Ordem determinística.
    """
    tarefas: list[dict] = []
    for caminho in sorted(glob.glob(str(RAIZ / "dados/triagem/triagem_nome_*.csv"))):
        bib, ano = Path(caminho).stem.split("_")[2:4]
        with open(caminho, encoding="utf-8", newline="") as arquivo:
            for linha in csv.DictReader(arquivo):
                hit = 1 if linha["hit"] == "1" else 0
                if braco == "sem_mencao" and hit:
                    continue
                if braco == "com_mencao" and not hit:
                    continue
                tarefas.append(
                    {
                        "bib": bib,
                        "ano": int(ano),
                        "source_identifier": linha["source_identifier"],
                        "page_number": int(linha["page_number"]),
                        "hit_censo": hit,
                    }
                )
    tarefas.sort(
        key=lambda t: (t["bib"], t["ano"], t["source_identifier"], t["page_number"])
    )
    return tarefas


def caminho_bruto(bib: str, source_identifier: str, page_number: int) -> Path:
    return DIR_BRUTO / bib / source_identifier / f"p{page_number:03d}.txt"


def processa_tarefa(tarefa: dict) -> dict:
    """Lê a página do acervo e devolve o registro. Roda em processo separado."""
    origem = caminho_bruto(
        tarefa["bib"], tarefa["source_identifier"], tarefa["page_number"]
    )
    try:
        texto = origem.read_text(encoding="utf-8")
    except OSError:
        texto = None
    registro = registro_de_pagina(
        bib=tarefa["bib"],
        ano=tarefa["ano"],
        source_identifier=tarefa["source_identifier"],
        page_number=tarefa["page_number"],
        hit_censo=tarefa["hit_censo"],
        texto=texto,
    )
    registro["candidatos"] = [asdict(c) for c in registro["candidatos"]]
    return registro


def sha256_arquivo(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


CAMPOS_CANDIDATO = [
    "bib", "jornal", "ano", "source_identifier", "page_number", "hit_censo",
    "offset", "fim", "distancia", "distancia_normalizada", "sobrepoe_exato",
    "trecho", "contexto",
]
CAMPOS_FALHA = [
    "bib", "jornal", "ano", "source_identifier", "page_number", "hit_censo",
    "status",
]


def _linhas_de_candidato(registro: dict) -> list[dict]:
    cabeca = {
        campo: registro[campo]
        for campo in ("bib", "jornal", "ano", "source_identifier", "page_number", "hit_censo")
    }
    linhas = []
    for candidato in registro["candidatos"]:
        linha = dict(cabeca)
        linha.update(
            {
                "offset": candidato["offset"],
                "fim": candidato["fim"],
                "distancia": candidato["distancia"],
                "distancia_normalizada": candidato["distancia_normalizada"],
                "sobrepoe_exato": int(candidato["sobrepoe_exato"]),
                "trecho": sem_controle(candidato["trecho"]),
                "contexto": sem_controle(candidato["contexto"]),
            }
        )
        linhas.append(linha)
    return linhas


def main(argv: list[str] | None = None) -> int:
    import multiprocessing as mp

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--braco", choices=("sem_mencao", "com_mencao", "ambos"), default="ambos"
    )
    parser.add_argument("--limite", type=int, default=0, help="0 = todas as páginas")
    parser.add_argument("--workers", type=int, default=14)
    parser.add_argument("--limiar", type=int, default=LIMIAR_QUASE_ACERTO)
    parser.add_argument("--saida", type=Path, default=DIR_SAIDA)
    args = parser.parse_args(argv)

    tarefas = paginas_do_censo(args.braco)
    if args.limite:
        tarefas = tarefas[: args.limite]
    print(f"{len(tarefas)} páginas a examinar (braço {args.braco})")

    inicio = time.time()
    registros: list[dict] = []
    with mp.Pool(processes=args.workers) as pool:
        for n, registro in enumerate(
            pool.imap_unordered(processa_tarefa, tarefas, chunksize=64), 1
        ):
            registros.append(registro)
            if n % 10000 == 0:
                decorrido = time.time() - inicio
                print(
                    f"  {n}/{len(tarefas)} páginas, {decorrido:.0f}s, "
                    f"{n / decorrido:.0f} pág/s"
                )
    duracao = time.time() - inicio

    registros.sort(
        key=lambda r: (r["bib"], r["ano"], r["source_identifier"], r["page_number"])
    )
    args.saida.mkdir(parents=True, exist_ok=True)

    linhas_candidato = [
        linha for registro in registros for linha in _linhas_de_candidato(registro)
    ]
    with open(args.saida / "candidatos.csv", "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS_CANDIDATO)
        escritor.writeheader()
        escritor.writerows(linhas_candidato)

    celulas = agrega_celulas(registros)
    with open(args.saida / "celulas.csv", "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(celulas[0]) if celulas else ["bib"])
        escritor.writeheader()
        escritor.writerows(celulas)

    falhas = [
        {campo: registro[campo] for campo in CAMPOS_FALHA}
        for registro in registros
        if registro["status"] != "ok"
    ]
    with open(args.saida / "falhas.csv", "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS_FALHA)
        escritor.writeheader()
        escritor.writerows(falhas)

    inspecao = trechos_para_inspecao(
        [linha for linha in linhas_candidato if not linha["sobrepoe_exato"]],
        limiar=args.limiar,
    )
    with open(
        args.saida / "trechos_para_inspecao.csv", "w", encoding="utf-8", newline=""
    ) as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS_CANDIDATO)
        escritor.writeheader()
        escritor.writerows(inspecao)

    sem_mencao = [r for r in registros if r["hit_censo"] == 0]
    com_mencao = [r for r in registros if r["hit_censo"] == 1]

    def perfil(grupo: list[dict], so_fora_do_exato: bool) -> dict:
        por_limiar = {}
        for n in range(DISTANCIA_MAXIMA_REGISTRADA + 1):
            paginas = 0
            mencoes = 0
            for registro in grupo:
                candidatos = [
                    c
                    for c in registro["candidatos"]
                    if c["distancia"] <= n
                    and (not so_fora_do_exato or not c["sobrepoe_exato"])
                ]
                if candidatos:
                    paginas += 1
                    mencoes += len(candidatos)
            por_limiar[str(n)] = {"paginas": paginas, "candidatos": mencoes}
        return por_limiar

    relatorio = {
        "protocol_name": PROTOCOLO,
        "protocol_version": VERSAO,
        "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "duracao_segundos": round(duracao, 1),
        "braco": args.braco,
        "parametros": {
            "canonica": CANONICA,
            "ancora_esquerda": ANCORA_ESQUERDA,
            "ancora_direita": ANCORA_DIREITA,
            "vao_maximo": VAO_MAXIMO,
            "folga_janela": [FOLGA_ESQUERDA, FOLGA_DIREITA],
            "distancia_maxima_registrada": DISTANCIA_MAXIMA_REGISTRADA,
            "limiar_quase_acerto": args.limiar,
            "contexto_janela": CONTEXTO_JANELA,
            "regra_versao_do_casador_exato": regra_nome.REGRA_VERSAO,
        },
        "hashes_do_instrumento": {
            "sonda_difusa.py": sha256_arquivo(Path(__file__)),
            "regra_nome.py": sha256_arquivo(Path(regra_nome.__file__)),
        },
        "paginas": {
            "examinadas": len(registros),
            "sem_mencao_no_censo": len(sem_mencao),
            "com_mencao_no_censo": len(com_mencao),
            "status": {
                estado: sum(1 for r in registros if r["status"] == estado)
                for estado in ("ok", "empty", "arquivo_ausente")
            },
        },
        "perfil_por_limiar": {
            "sem_mencao_no_censo": perfil(sem_mencao, so_fora_do_exato=False),
            "com_mencao_no_censo_fora_do_span_exato": perfil(
                com_mencao, so_fora_do_exato=True
            ),
        },
        "cota_inferior_de_falsos_negativos": {
            "limiar": args.limiar,
            "paginas": sum(
                1
                for r in sem_mencao
                if r["melhor_distancia"] is not None
                and r["melhor_distancia"] <= args.limiar
            ),
            "base": len(sem_mencao),
            "leia_se": (
                "páginas que o censo marcou como sem menção e onde a sonda achou "
                "forma a distância <= limiar da forma canônica. É cota INFERIOR: "
                "a sonda não acha página com as duas âncoras destruídas nem menção "
                "sem o nome. Precisão do limiar é conferida por leitura em "
                "trechos_para_inspecao.csv, não presumida."
            ),
        },
        "advertencia": (
            "Concordância entre dois leitores da mesma imagem degradada não é "
            "verdade: os dois podem errar junto, com erro correlacionado. "
            "Consenso é sinal de confiabilidade, nunca validação."
        ),
    }
    (args.saida / "relatorio.json").write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    print(f"saída em {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
