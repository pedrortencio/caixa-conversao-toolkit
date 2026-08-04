"""O contrato da ficha de leitura: quais campos existem e o que aceitam.

Nucleo puro, sem I/O e sem prompt, para que a regra que governa a ficha seja
testavel sem simular teclado. A casca interativa vive em `ficha.py`.

Duas regras deste modulo merecem explicacao, porque nao sao arbitrarias.

`direcao_por_objeto` casa um-para-um com `objeto_politica`. O plano de leitura
registra direcao POR OBJETO justamente para nao adotar o veredito holistico da
escala, que e o formato do D-Escala, o incumbente cujas fraquezas estao
medidas. Se as duas listas puderem ter tamanhos diferentes, a correspondencia
se perde e a ficha volta a ser um veredito unico disfarcado. Dai a validacao
recusar, em vez de completar com `nao_aplica`: completar por conta propria
inventaria codificacao que o leitor nao fez.

`vocabulario_epoca` e `dificuldade` sao os dois campos que o codebook consome
diretamente, e por isso sao os unicos que o modo estrito exige preenchidos numa
peca substantiva. Os demais sustentam o capitulo e podem ficar vazios sem
quebrar nada.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

PROTOCOL_NAME = "ficha-leitura"
PROTOCOL_VERSION = "0.1.0"

# As 12 colunas que o amostrador ja preencheu. A ficha nunca as escreve.
COLUNAS_IDENTIFICACAO = (
    "item_id", "camada", "estrato", "motivo_selecao", "fase", "jornal", "data",
    "data_confiavel", "source_identifier", "page_number", "forma", "secao",
    "titulo", "registro",
)

VOZES = (
    "editorial_do_jornal",
    "assinado",
    "reproduzido_terceiro",
    "telegrama_agencia",
    "discurso_parlamentar",
    "indeterminado",
)

OBJETOS = (
    "taxa",
    "conversibilidade",
    "lastro",
    "emissao",
    "valorizacao_cafe",
    "divida_externa",
    "outro",
)

DIRECOES = ("ortodoxo", "expansionista", "nao_aplica", "nao_classificavel")

BIBS = {
    "correio_manha": "089842",
    "correio_paulistano": "090972",
    "gazeta_noticias": "103730",
    "o_paiz": "178691",
}

DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ErroDeCampo(ValueError):
    """Valor recusado. A mensagem vai direto para o leitor."""


@dataclass(frozen=True, slots=True)
class Campo:
    nome: str
    pergunta: str
    ajuda: str
    vocabulario: tuple[str, ...] = ()
    multiplo: bool = False
    obrigatorio_no_estrito: bool = False
    exemplos: tuple[str, ...] = field(default=())


CAMPOS: tuple[Campo, ...] = (
    Campo(
        nome="data_masthead",
        pergunta="data no cabecalho da pagina",
        ajuda="AAAA-MM-DD, como esta impresso. Nao ha mapa edicao-data para "
              "1907-14; e a leitura que o constroi. Vazio se ilegivel.",
        exemplos=("1906-09-25",),
    ),
    Campo(
        nome="voz",
        pergunta="voz",
        ajuda="Quem fala. Hospedar voz nao e ter posicao: SECCAO LIVRE e espaco "
              "pago e relato de sessao e fala de terceiro.",
        vocabulario=VOZES,
        obrigatorio_no_estrito=True,
    ),
    Campo(
        nome="objeto_politica",
        pergunta="objeto(s) de politica",
        ajuda="O que concretamente esta em disputa na peca. Varios separados "
              "por ponto e virgula, na ordem em que voce for classificar a direcao.",
        vocabulario=OBJETOS,
        multiplo=True,
    ),
    Campo(
        nome="direcao_por_objeto",
        pergunta="direcao, um por objeto na mesma ordem",
        ajuda="Um veredito para cada objeto acima. Nao e escala: a escala e "
              "derivavel dos atributos, o caminho inverso nao existe.",
        vocabulario=DIRECOES,
        multiplo=True,
    ),
    Campo(
        nome="posicao_declarada",
        pergunta="o que a peca defende, em uma frase",
        ajuda="Insumo direto do bloco da fase.",
    ),
    Campo(
        nome="argumento",
        pergunta="a justificativa mobilizada",
        ajuda="Por que a peca defende o que defende.",
    ),
    Campo(
        nome="atores_nomeados",
        pergunta="atores nomeados",
        ajuda="Pessoas, bancos, estados, instituicoes. Ponto e virgula entre eles.",
        multiplo=True,
    ),
    Campo(
        nome="interesses_invocados",
        pergunta="interesses invocados",
        ajuda="A quem a peca atribui ganho ou perda. Ponto e virgula entre eles.",
        multiplo=True,
    ),
    Campo(
        nome="vocabulario_epoca",
        pergunta="vocabulario de epoca, VERBATIM",
        ajuda="Termos como estao na pagina, nao parafraseados. E o inventario "
              "lexical, atestado e nao inferido. O codebook consome este campo.",
        multiplo=True,
        obrigatorio_no_estrito=True,
        exemplos=("agio;padrao ouro;troco de notas",),
    ),
    Campo(
        nome="citacao_ancora",
        pergunta="citacao ancora, transcrita da pagina",
        ajuda="Trecho literal que sustenta a leitura. Transcreva da imagem, "
              "nunca da coluna `texto` de amostra_para_rotular.csv.",
    ),
    Campo(
        nome="localizacao",
        pergunta="localizacao na pagina",
        ajuda="Pagina e coluna, para rastrear a citacao.",
        exemplos=("p1 col3",),
    ),
    Campo(
        nome="confianca",
        pergunta="confianca (1 a 3)",
        ajuda="1 e baixa. Onde cair para 1, ha caso-limite, e o proximo campo "
              "e que o registra.",
        vocabulario=("1", "2", "3"),
    ),
    Campo(
        nome="dificuldade",
        pergunta="o que tornou a codificacao dificil",
        ajuda="Alimenta os casos-limite do codebook, que e o que distingue um "
              "codebook operacional de uma descricao. Vazio se foi trivial.",
        obrigatorio_no_estrito=True,
    ),
    Campo(
        nome="dialogo_historiografia",
        pergunta="com que leitura a peca conversa ou colide",
        ajuda="Cruzamento com a historiografia. Vazio se nada saltou.",
    ),
)

COLUNAS_LEITURA = tuple(c.nome for c in CAMPOS) + ("minutos",)


def normaliza_para_busca(texto: str) -> str:
    """Minusculo, sem acento, sem pontuacao, espaco colapsado.

    Serve so para a conferencia FROUXA da citacao contra o OCR. Nao e a
    normalizacao de `regra_nome`, que governa medida, e nao deve virar isso.
    """
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", " ", sem_acento).strip()


def valida(campo: Campo, bruto: str) -> str:
    """Devolve o valor canonico ou levanta ErroDeCampo. Vazio sempre passa."""
    valor = bruto.strip()
    if not valor:
        return ""

    if campo.nome == "data_masthead":
        if not DATA.match(valor):
            raise ErroDeCampo("data precisa ser AAAA-MM-DD, ex 1906-09-25")
        return valor

    if not campo.vocabulario:
        if campo.multiplo:
            partes = [p.strip() for p in valor.split(";") if p.strip()]
            return ";".join(partes)
        return " ".join(valor.split())

    partes = [p.strip().lower() for p in valor.split(";") if p.strip()]
    if not campo.multiplo and len(partes) > 1:
        raise ErroDeCampo(f"{campo.nome} aceita um valor so")
    for parte in partes:
        if parte not in campo.vocabulario:
            raise ErroDeCampo(
                f"{parte!r} nao esta no vocabulario. Aceitos: "
                + ", ".join(campo.vocabulario)
            )
    return ";".join(partes)


def valida_direcao_casa_objeto(objetos: str, direcoes: str) -> None:
    """Um veredito por objeto, na mesma ordem. Ver o cabecalho do modulo."""
    n_obj = len([p for p in objetos.split(";") if p])
    n_dir = len([p for p in direcoes.split(";") if p])
    if not n_obj and not n_dir:
        return
    if n_obj != n_dir:
        raise ErroDeCampo(
            f"{n_obj} objeto(s) e {n_dir} direcao(oes). Precisa ser um para um, "
            "na mesma ordem. Use nao_aplica onde a peca nao se pronuncia."
        )


def esta_preenchida(linha: dict[str, str]) -> bool:
    """Uma ficha conta como lida se tem voz, que e o campo minimo da leitura.

    Escolhi `voz` e nao "qualquer campo" porque uma peca pode legitimamente ter
    todos os outros vazios (uma tabela de boletim, por exemplo), e nesse caso
    varrer por "algum campo preenchido" a devolveria para a fila para sempre.
    """
    return bool((linha.get("voz") or "").strip())


def pendencias_do_estrito(linha: dict[str, str]) -> list[str]:
    """Campos que o modo estrito cobra numa peca substantiva."""
    if (linha.get("registro") or "").strip() != "substantivo":
        return []
    faltando = []
    for campo in CAMPOS:
        if campo.obrigatorio_no_estrito and not (linha.get(campo.nome) or "").strip():
            faltando.append(campo.nome)
    return faltando


def caminho_pdf(linha: dict[str, str], raiz_acervo) -> object:
    """O PDF da edicao inteira. A pagina vem de `page_number`."""
    bib = BIBS.get((linha.get("jornal") or "").strip())
    if bib is None:
        raise ErroDeCampo(f"jornal desconhecido: {linha.get('jornal')!r}")
    return raiz_acervo / "raw_pdf" / bib / f"{linha['source_identifier']}.pdf"


def caminho_texto_ocr(linha: dict[str, str], raiz_acervo) -> object:
    """O OCR determinístico da Hemeroteca para aquela pagina."""
    bib = BIBS.get((linha.get("jornal") or "").strip())
    if bib is None:
        raise ErroDeCampo(f"jornal desconhecido: {linha.get('jornal')!r}")
    pagina = int(linha["page_number"])
    return (
        raiz_acervo / "texto_embutido" / bib / linha["source_identifier"]
        / f"p{pagina:03d}.txt"
    )
