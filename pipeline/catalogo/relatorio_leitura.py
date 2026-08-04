"""Documento de leitura do piloto de catalogacao.

Transforma os JSONL do piloto num markdown que o Pedro le de ponta a ponta:
os debates catalogados, janela a janela, com a citacao verbatim ao lado e a
divergencia entre anotadores visivel.

Duas garantias sao reconferidas aqui, e nao herdadas da corrida:

1. **Citacao.** Toda citacao renderizada e conferida de novo contra a janela
   de origem. Registro que nao casa nao entra no corpo e sai listado no
   apendice. Um documento de leitura que exibisse citacao nao conferida
   viraria, por uso, uma fonte de citacao para a dissertacao.
2. **Ausencia.** Dizer que um anotador nao encontrou nada exige que ele tenha
   olhado. Janela em que algum anotador caiu, e onde ninguem catalogou nada,
   fica na classe `sem_par` em vez de virar `nenhum`.

Uso:
  uv run python pipeline/catalogo/relatorio_leitura.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.catalogo import verifica

DIR_DADOS = Path("dados/catalogo")
JANELAS = DIR_DADOS / "piloto_janelas.jsonl"
SAIDA = Path("docs/relatorio-piloto-catalogacao.md")
ANOTADORES = ("claude", "codex")

JORNAIS = {
    "o_paiz": "O Paiz",
    "correio_manha": "Correio da Manhã",
    "correio_paulistano": "Correio Paulistano",
    "gazeta_noticias": "Gazeta de Notícias",
}

FASES = {
    "F1": "F1, 1906, criação da Caixa",
    "F2": "F2, 1907 a 1909, operação, lastro e alfândega",
    "F3": "F3, 1910 a 1913, taxa de 16 dinheiros e ampliação do limite",
    "F4": "F4, 1914, suspensão do troco",
}

CLASSES = {
    "ambos": "os dois catalogaram",
    "so_claude": "só o Claude catalogou",
    "so_codex": "só o Codex catalogou",
    "nenhum": "os dois olharam e não catalogaram nada",
    "sem_par": "sem par comparável (algum anotador não concluiu)",
}


def le_jsonl(caminho: Path) -> list[dict]:
    if not caminho.exists():
        return []
    texto = caminho.read_text(encoding="utf-8")
    return [json.loads(linha) for linha in texto.splitlines() if linha.strip()]


def cobertura(anotacoes: list[dict]) -> dict[str, int]:
    """Estado final por janela: a tentativa mais recente vence."""
    ultima: dict[str, str] = {}
    for linha in anotacoes:
        ultima[linha["janela_id"]] = linha.get("status", "falha")
    return {
        "ok": sum(1 for s in ultima.values() if s == "ok"),
        "falha": sum(1 for s in ultima.values() if s != "ok"),
        "janelas": len(ultima),
    }


def _com_tentativa_valida(anotacoes: list[dict]) -> set[str]:
    ultima: dict[str, str] = {}
    for linha in anotacoes:
        ultima[linha["janela_id"]] = linha.get("status", "falha")
    return {j for j, status in ultima.items() if status == "ok"}


def por_janela(registros: list[dict]) -> dict[str, list[dict]]:
    indice: dict[str, list[dict]] = {}
    for registro in registros:
        indice.setdefault(registro.get("janela_id", ""), []).append(registro)
    return indice


def deteccao(
    janelas: list[dict],
    aceitos: dict[str, list[dict]],
    anotacoes: dict[str, list[dict]],
) -> dict[str, str]:
    """Classifica cada janela por quem catalogou algo nela.

    Afirmacao de presenca precisa so de quem achou. Afirmacao de ausencia
    precisa de todos: se ninguem catalogou mas algum anotador nao concluiu a
    janela, a classe e `sem_par`, porque `nenhum` seria mentira sobre quem
    nem chegou a olhar.
    """
    indices = {a: por_janela(aceitos.get(a, [])) for a in ANOTADORES}
    validas = {a: _com_tentativa_valida(anotacoes.get(a, [])) for a in ANOTADORES}
    classes: dict[str, str] = {}
    for janela in janelas:
        jid = janela["janela_id"]
        achou = [a for a in ANOTADORES if indices[a].get(jid)]
        if len(achou) == len(ANOTADORES):
            classes[jid] = "ambos"
        elif achou:
            classes[jid] = f"so_{achou[0]}"
        elif all(jid in validas[a] for a in ANOTADORES):
            classes[jid] = "nenhum"
        else:
            classes[jid] = "sem_par"
    return classes


def confere_citacoes_do_corpo(
    janelas: list[dict], aceitos: dict[str, list[dict]]
) -> list[dict]:
    """Registros cuja citacao nao casa com a janela, reconferidos agora."""
    texto_por_id = {j["janela_id"]: j["texto"] for j in janelas}
    divergentes: list[dict] = []
    for anotador in ANOTADORES:
        for registro in aceitos.get(anotador, []):
            janela = texto_por_id.get(registro.get("janela_id", ""))
            if janela is None:
                divergentes.append({**registro, "anotador": anotador, "falha": "janela_desconhecida"})
                continue
            veredito = verifica.confere_citacao(registro.get("citacao_verbatim"), janela)
            if not veredito.aceita:
                divergentes.append({**registro, "anotador": anotador, "falha": veredito.motivo})
    return divergentes


def _direcoes(registro: dict) -> str:
    pares = registro.get("direcao_por_objeto") or []
    if not pares:
        return ", ".join(registro.get("objeto_politica") or []) or "não informado"
    return ", ".join(f"{p.get('objeto')} ({p.get('direcao')})" for p in pares)


def _lista_nomes(registro: dict, campo: str) -> str:
    itens = registro.get(campo) or []
    nomes = [i.get("nome", "") for i in itens if isinstance(i, dict) and i.get("nome")]
    return ", ".join(nomes)


def _marcos(registro: dict) -> str:
    itens = registro.get("marcos") or []
    partes = [
        f"{i.get('data', 's/d')} ({i.get('descricao', '')})"
        for i in itens
        if isinstance(i, dict)
    ]
    return "; ".join(partes)


def _bloco_registro(registro: dict) -> list[str]:
    linhas = [
        f"- **{registro.get('debate', 'sem título')}**",
        f"  - voz: `{registro.get('voz', 'indeterminado')}`",
        f"  - objetos e direção: {_direcoes(registro)}",
    ]
    if registro.get("posicao_defendida"):
        linhas.append(f"  - posição: {registro['posicao_defendida']}")
    if registro.get("argumento"):
        linhas.append(f"  - argumento: {registro['argumento']}")
    agentes = _lista_nomes(registro, "agentes")
    if agentes:
        linhas.append(f"  - agentes: {agentes}")
    marcos = _marcos(registro)
    if marcos:
        linhas.append(f"  - marcos: {marcos}")
    linhas.append(f"  - citação conferida: > {registro.get('citacao_verbatim', '')}")
    if registro.get("observacao"):
        linhas.append(f"  - observação do anotador: {registro['observacao']}")
    return linhas


def renderiza(
    *,
    janelas: list[dict],
    aceitos: dict[str, list[dict]],
    rejeitados: dict[str, list[dict]],
    anotacoes: dict[str, list[dict]],
    meta: dict,
) -> str:
    divergentes = confere_citacoes_do_corpo(janelas, aceitos)
    ids_divergentes = {
        (d["anotador"], d.get("janela_id"), d.get("citacao_verbatim")) for d in divergentes
    }
    indices = {a: por_janela(aceitos.get(a, [])) for a in ANOTADORES}
    validas = {a: _com_tentativa_valida(anotacoes.get(a, [])) for a in ANOTADORES}
    classes = deteccao(janelas, aceitos, anotacoes)

    p: list[str] = []
    p.append("# Piloto de catalogação por LLM, documento de leitura")
    p.append("")
    p.append(f"**Gerado em:** {meta.get('quando')}. ")
    p.append(
        f"**Prompt:** `{meta.get('prompt')}`, sha `{meta.get('prompt_sha')}`, "
        "o mesmo para os dois anotadores."
    )
    p.append("")
    p.append(
        "Este documento é o **objeto 1**, mapeamento descritivo. Não é atribuição "
        "de posição editorial ao jornal, não é escala, não é estimativa. O campo "
        "`voz` existe justamente para impedir que hospedar um discurso seja lido "
        "como defendê-lo."
    )
    p.append("")
    p.append(
        "A concordância entre os dois anotadores aparece aqui como análise de "
        "sensibilidade descritiva. Não é validação humana e não é validade de "
        "construto."
    )
    p.append("")

    p.append("## 1. Cobertura e qualidade do lote")
    p.append("")
    p.append("| anotador | CLI | janelas concluídas | falhas | registros aceitos | rejeitados | taxa de rejeição |")
    p.append("|---|---|---|---|---|---|---|")
    for a in ANOTADORES:
        cob = cobertura(anotacoes.get(a, []))
        acc, rej = len(aceitos.get(a, [])), len(rejeitados.get(a, []))
        taxa = rej / (acc + rej) if (acc + rej) else 0.0
        cli = next(
            (l.get("versao_cli") for l in anotacoes.get(a, []) if l.get("versao_cli")),
            "não registrada",
        )
        # A virgula decimal vale para a taxa, nao para a linha: aplicada ao
        # texto inteiro ela transforma "2.1.220 (Claude Code)" em "2,1,220".
        taxa_pt = f"{taxa:.1%}".replace(".", ",")
        p.append(
            f"| {a} | {cli} | {cob['ok']} de {len(janelas)} | {cob['falha']} | "
            f"{acc} | {rej} | {taxa_pt} |"
        )
    p.append("")
    p.append(
        "A taxa de rejeição é a métrica de qualidade do lote. Citação que não casa "
        "com a janela é descartada, nunca corrigida."
    )
    p.append("")

    p.append("## 2. Onde os dois anotadores se encontram")
    p.append("")
    contagem: dict[str, int] = {}
    for classe in classes.values():
        contagem[classe] = contagem.get(classe, 0) + 1
    p.append("| classe | janelas |")
    p.append("|---|---|")
    for chave, rotulo in CLASSES.items():
        if contagem.get(chave):
            p.append(f"| {rotulo} | {contagem[chave]} |")
    p.append("")
    p.append(
        "Detecção quer dizer catalogar ao menos um debate na janela. Não mede "
        "acordo sobre o conteúdo do que foi catalogado, que é leitura sua."
    )
    p.append("")

    p.append("## 3. Os debates catalogados")
    p.append("")
    ordem_fase = ["F1", "F2", "F3", "F4"]
    for fase in ordem_fase:
        da_fase = [j for j in janelas if j.get("fase") == fase]
        if not da_fase:
            continue
        p.append(f"### {FASES.get(fase, fase)}")
        p.append("")
        for janela in sorted(
            da_fase, key=lambda j: (j.get("jornal", ""), j.get("source_identifier", ""))
        ):
            jid = janela["janela_id"]
            jornal = JORNAIS.get(janela.get("jornal", ""), janela.get("jornal", ""))
            p.append(
                f"#### {jornal}, {janela.get('ano')}, edição "
                f"{janela.get('source_identifier', '')}, página {janela.get('page_number')}"
            )
            p.append("")
            p.append(f"`{jid}`, classe: {CLASSES[classes[jid]]}.")
            p.append("")
            for a in ANOTADORES:
                registros = [
                    r
                    for r in indices[a].get(jid, [])
                    if (a, r.get("janela_id"), r.get("citacao_verbatim")) not in ids_divergentes
                ]
                if registros:
                    p.append(f"**{a}**, {len(registros)} registro(s):")
                    p.append("")
                    for registro in registros:
                        p.extend(_bloco_registro(registro))
                    p.append("")
                elif jid not in validas[a]:
                    p.append(f"**{a}**: não concluiu esta janela (falha de chamada).")
                    p.append("")
                else:
                    p.append(f"**{a}**: olhou e não catalogou nada.")
                    p.append("")

    p.append("## 4. Apêndice, registros rejeitados na conferência de citação")
    p.append("")
    total_rejeitados = sum(len(rejeitados.get(a, [])) for a in ANOTADORES)
    if not total_rejeitados and not divergentes:
        p.append("Nenhum registro rejeitado.")
        p.append("")
    for a in ANOTADORES:
        for registro in rejeitados.get(a, []):
            p.append(
                f"- **{a}**, `{registro.get('janela_id')}`, motivo "
                f"`{registro.get('motivo_rejeicao')}`: {registro.get('debate', '')}"
            )
            citacao = (registro.get("citacao_verbatim") or "").strip()
            if citacao:
                p.append(f"  - citação recusada: {citacao}")
    if divergentes:
        p.append("")
        p.append(
            "Registros que passaram na corrida e não passaram nesta reconferência "
            "(sinal de arquivo desatualizado ou de conferidor alterado):"
        )
        for d in divergentes:
            p.append(f"- **{d['anotador']}**, `{d.get('janela_id')}`, falha `{d['falha']}`")
    p.append("")
    return "\n".join(p)


def main() -> None:
    janelas = le_jsonl(JANELAS)
    aceitos = {a: le_jsonl(DIR_DADOS / f"aceitos_{a}.jsonl") for a in ANOTADORES}
    rejeitados = {a: le_jsonl(DIR_DADOS / f"rejeitados_{a}.jsonl") for a in ANOTADORES}
    anotacoes = {a: le_jsonl(DIR_DADOS / f"anotacoes_{a}.jsonl") for a in ANOTADORES}
    primeira = next(
        (l for l in anotacoes["claude"] + anotacoes["codex"] if l.get("prompt_sha")), {}
    )
    texto = renderiza(
        janelas=janelas,
        aceitos=aceitos,
        rejeitados=rejeitados,
        anotacoes=anotacoes,
        meta={
            "prompt": primeira.get("prompt", "pipeline/prompts/catalogacao_debates.md"),
            "prompt_sha": primeira.get("prompt_sha", ""),
            "quando": date.today().isoformat(),
        },
    )
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(texto, encoding="utf-8", newline="\n")
    print(f"escrito: {SAIDA} ({len(texto):,} caracteres)".replace(",", "."))
    for a in ANOTADORES:
        cob = cobertura(anotacoes[a])
        print(f"  {a}: {cob['ok']} ok, {cob['falha']} falha, {len(aceitos[a])} aceitos")


if __name__ == "__main__":
    main()
