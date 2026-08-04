"""O mesmo elenco, contado nos Documentos Parlamentares da Caixa de Conversao.

Aqui nao ha o problema que obriga a medir distancia no jornal: o volume
inteiro E o debate, entao contar nome na pagina ja e contar nome no debate.
Duas medidas por ator:

  - `mencoes`, quantas vezes o nome aparece no texto corrigido;
  - `turnos_de_fala`, quantas vezes o nome encabeca um turno de palavra, pelo
    marcador "O SR. NOME". Essa segunda separa quem fala de quem e citado, que
    e a distincao que o jornal nao deixa fazer sem leitura.

Volume 1 e o debate de 1906 (criacao), volume 2 o de 1910 (taxa de 16
dinheiros). Sao dois cortes no tempo, nao uma serie.

Insumo: `dados/texto_corrigido/fontes_parlamentares/caixa_conversao/`, camada
derivada de leitura. Citacao academica continua exigindo conferencia no PDF.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from pipeline.analise.nomes_no_debate import (
    TOKEN,
    carrega_elenco,
    carrega_exclusoes,
    descobre_variantes,
    indexa_pagina,
    indice_de_formas,
    mencoes_em,
    posicoes_na_pagina,
)
from pipeline.triagem import regra_nome

RAIZ = Path(__file__).resolve().parents[2]
BASE = RAIZ / "dados" / "texto_corrigido" / "fontes_parlamentares" / "caixa_conversao"

# "O SR. NOME." no texto ja normalizado (minusculo, sem acento).
MARCADOR_FALA = re.compile(r"\bo\s+sr\.?\s+([a-z][a-z' ]{3,40}?)\s*[\.\-:]")


def carrega_volume(volume: int, base: Path = BASE) -> list[tuple[int, str]]:
    caminho = base / f"caixa_conversao_v{volume}_paginas_corrigidas.jsonl"
    paginas: list[tuple[int, str]] = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        registro = json.loads(linha)
        paginas.append(
            (registro["pdf_page"], regra_nome.normaliza(registro.get("corrected_text") or ""))
        )
    return paginas


def inicios_de_fala(texto: str) -> set[int]:
    return {m.start(1) for m in MARCADOR_FALA.finditer(texto)}


def main() -> None:  # pragma: no cover - orquestracao com I/O
    elenco = carrega_elenco()
    exclusoes = carrega_exclusoes()
    volumes = {v: carrega_volume(v) for v in (1, 2)}

    for volume, paginas in volumes.items():
        chars = sum(len(t) for _, t in paginas)
        mencoes = sum(len(mencoes_em(t)) for _, t in paginas)
        com = sum(1 for _, t in paginas if mencoes_em(t))
        print(f"volume {volume}: {len(paginas)} paginas, {chars:,} chars normalizados, "
              f"{mencoes} mencoes do nome em {com} paginas")

    vocabulario: Counter[str] = Counter()
    for paginas in volumes.values():
        for _, texto in paginas:
            vocabulario.update(TOKEN.findall(texto))
    tokens_chave = {t for ator in elenco for t in ator.tokens}
    indice = indice_de_formas(descobre_variantes(vocabulario, tokens_chave, exclusoes))

    mencoes: dict[str, Counter] = {a.nome: Counter() for a in elenco}
    paginas_com: dict[str, dict[int, set]] = {a.nome: {1: set(), 2: set()} for a in elenco}
    falas: dict[str, Counter] = {a.nome: Counter() for a in elenco}

    for volume, paginas in volumes.items():
        for numero, texto in paginas:
            aberturas = inicios_de_fala(texto)
            indexada = indexa_pagina(texto, indice)
            for ator in elenco:
                achados = posicoes_na_pagina(indexada, ator)
                if not achados:
                    continue
                mencoes[ator.nome][volume] += len(achados)
                paginas_com[ator.nome][volume].add(numero)
                falas[ator.nome][volume] += sum(1 for p in achados if p in aberturas)

    ordem = sorted(elenco, key=lambda a: -(mencoes[a.nome][1] + mencoes[a.nome][2]))
    print("\n" + "=" * 92)
    print("DOCUMENTOS PARLAMENTARES: mencoes e turnos de fala por volume")
    print("=" * 92)
    print(f"{'nome':22s} {'total':>6s} {'v1 1906':>8s} {'v2 1910':>8s} "
          f"{'pag v1':>7s} {'pag v2':>7s} {'turnos':>7s}")
    saida = []
    for ator in ordem:
        v1, v2 = mencoes[ator.nome][1], mencoes[ator.nome][2]
        if not (v1 + v2):
            continue
        turnos = falas[ator.nome][1] + falas[ator.nome][2]
        print(f"{ator.nome:22s} {v1 + v2:>6d} {v1:>8d} {v2:>8d} "
              f"{len(paginas_com[ator.nome][1]):>7d} {len(paginas_com[ator.nome][2]):>7d} "
              f"{turnos:>7d}")
        saida.append({
            "nome": ator.nome, "classe": ator.classe, "total": v1 + v2,
            "v1_1906": v1, "v2_1910": v2,
            "paginas_v1": len(paginas_com[ator.nome][1]),
            "paginas_v2": len(paginas_com[ator.nome][2]),
            "turnos_de_fala": turnos,
        })

    ausentes = [a.nome for a in elenco if not (mencoes[a.nome][1] + mencoes[a.nome][2])]
    print(f"\nsem nenhuma mencao nos dois volumes ({len(ausentes)}): {', '.join(ausentes)}")

    destino = RAIZ / "dados" / "analise" / "nomes_documentos_parlamentares.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps({"atores": saida, "sem_mencao": ausentes}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"manifesto: {destino}")


if __name__ == "__main__":  # pragma: no cover
    main()
