"""Quem o texto nomeia perto da menção, sem elenco definido de antemão.

Para que existe: `nomes_no_debate.py` responde "com que frequência cada um
destes 52 nomes aparece perto da menção", e o elenco veio de fontes que já
saíram do próprio corpus. Isso põe um teto de recall que não é medido: nome
que nenhuma dessas fontes registrou não pode aparecer no ranking, por mais
frequente que seja. Este módulo tira o teto.

Como: a imprensa da época nomeia por tratamento. "o sr. Campista", "o
conselheiro Affonso Penna", "o deputado Barbosa Lima". Colhendo o token que
vem depois do tratamento dentro de uma janela em torno da menção, sai um
ranking aberto, que não depende de eu saber quem procurar.

O que ele NÃO resolve: perífrase sem tratamento ("o rei dos banqueiros
londrinos"), designação por cargo sem nome ("o ministro da Fazenda"), e
sobrenome usado sozinho. O ranking aberto é piso de descoberta, não censo de
atores.

Agrupamento de variantes: formas a distância de edição 1 entre si são fundidas
na mais frequente, o que junta `campista` e `campisla` sem lista escrita à mão.
O agrupamento é reportado junto, para conferência.
"""
from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

from pipeline.analise.nomes_no_debate import distancia, mencoes_em, paginas_com_mencao
from pipeline.triagem import regra_nome

RAIZ = Path(__file__).resolve().parents[2]

TRATAMENTOS = (
    "sr", "srs", "sr.", "dr", "exm sr", "conselheiro", "deputado", "senador",
    "ministro", "visconde", "barao", "marechal", "general", "coronel",
)

# tratamento + ate dois tokens de nome, no texto ja normalizado
TRATAMENTO = re.compile(
    r"\b(?:sr|srs|dr|exm|conselheiro|deputado|senador|ministro|visconde|barao|"
    r"marechal|general|coronel)s?\.?\s+([a-z]{3,}(?:\s+[a-z]{3,})?)"
)

# Palavras que seguem tratamento sem serem nome proprio. Cada uma foi vista na
# saida bruta antes de entrar aqui.
NAO_E_NOME = {
    "da", "de", "do", "dos", "das", "e", "que", "presidente", "ministro",
    "senador", "deputado", "governador", "director", "doutor", "general",
    "coronel", "commandante", "chefe", "secretario", "consul", "juiz",
    "delegado", "prefeito", "vice", "seu", "sua", "meu", "nosso", "este",
    "esse", "aquelle", "mesmo", "proprio", "illustre", "nobre", "digno",
    "eminente", "ex", "exm", "exmo", "sr", "srs", "dr", "drs", "conselheiro",
    "barao", "visconde", "marechal", "commissario", "engenheiro", "capitao",
    "major", "tenente", "advogado", "medico", "padre", "frei", "dom",
}

LARGURA_PADRAO = 2000


def candidatos(texto: str, mencoes: list[int], largura: int = LARGURA_PADRAO) -> list[str]:
    """Nomes precedidos de tratamento dentro de `largura` em torno de uma menção."""
    metade = largura // 2
    achados: list[str] = []
    for encontrado in TRATAMENTO.finditer(texto):
        if not any(abs(encontrado.start() - m) <= metade for m in mencoes):
            continue
        tokens = [t for t in encontrado.group(1).split() if t not in NAO_E_NOME]
        if not tokens:
            continue
        achados.append(" ".join(tokens))
    return achados


def agrupa_variantes(contagem: Counter, minimo: int = 5) -> dict[str, str]:
    """forma -> forma canônica, fundindo o que está a uma edição de distância.

    A canônica é a mais frequente do grupo. Só formas com pelo menos `minimo`
    ocorrências puxam grupo, para o ruído de OCR não virar cabeça de cluster.
    """
    formas = [f for f, n in contagem.most_common() if n >= minimo]
    canonica: dict[str, str] = {}
    for forma in formas:
        for outra in canonica:
            if len(forma) != len(outra) and abs(len(forma) - len(outra)) > 1:
                continue
            if distancia(outra, forma, 1) <= 1:
                canonica[forma] = canonica[outra]
                break
        else:
            canonica[forma] = forma
    return canonica


def main() -> None:  # pragma: no cover - orquestracao com I/O
    import time

    inicio = time.time()
    contagem: Counter[str] = Counter()
    paginas: Counter[str] = Counter()
    por_ano: dict[str, Counter] = {}
    n = 0
    for bib, ano, objeto, pagina, caminho in paginas_com_mencao():
        texto = regra_nome.normaliza(caminho.read_text(encoding="utf-8", errors="replace"))
        marcas = mencoes_em(texto)
        if not marcas:
            continue
        achados = candidatos(texto, marcas)
        contagem.update(achados)
        for forma in set(achados):
            paginas[forma] += 1
            por_ano.setdefault(forma, Counter())[ano] += 1
        n += 1
    print(f"{n} paginas, {len(contagem)} formas, {sum(contagem.values())} ocorrencias, "
          f"{time.time() - inicio:.0f}s")

    canonica = agrupa_variantes(contagem)
    agrupado: Counter[str] = Counter()
    agrupado_pag: Counter[str] = Counter()
    membros: dict[str, list[str]] = {}
    for forma, alvo in canonica.items():
        agrupado[alvo] += contagem[forma]
        agrupado_pag[alvo] += paginas[forma]
        membros.setdefault(alvo, []).append(forma)

    anos = sorted({a for c in por_ano.values() for a in c})
    print("\n" + "=" * 104)
    print("RANKING ABERTO: nome precedido de tratamento, a menos de 1.000 caracteres da mencao")
    print("=" * 104)
    print(f"{'forma canonica':28s} {'ocorr':>6s} {'paginas':>8s}  " +
          " ".join(f"{a % 100:>4d}" for a in anos) + "   variantes fundidas")
    linhas_saida = []
    for forma, total in agrupado.most_common(45):
        contagens_ano = Counter()
        for membro in membros[forma]:
            contagens_ano.update(por_ano.get(membro, {}))
        serie = " ".join(f"{contagens_ano.get(a, 0):>4d}" for a in anos)
        outras = [m for m in sorted(membros[forma], key=lambda x: -contagem[x]) if m != forma]
        print(f"{forma:28s} {total:>6d} {agrupado_pag[forma]:>8d}  {serie}   "
              f"{', '.join(outras[:4])}")
        linhas_saida.append({
            "forma_canonica": forma,
            "ocorrencias": total,
            "paginas": agrupado_pag[forma],
            "variantes_fundidas": "|".join(sorted(membros[forma])),
            **{f"ano_{a}": contagens_ano.get(a, 0) for a in anos},
        })

    destino = RAIZ / "dados" / "analise" / "nomes_abertos.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=list(linhas_saida[0]), lineterminator="\n"
        )
        escritor.writeheader()
        escritor.writerows(linhas_saida)
    print(f"\nmanifesto: {destino}")


if __name__ == "__main__":  # pragma: no cover
    main()
