"""Roda o piloto de catalogacao com um anotador e confere as citacoes.

Uma janela por chamada: isola a falha, permite retomar e mantem o parse
simples. A resposta crua e sempre gravada, mesmo quando o parse falha, para
que nenhum erro de anotador desapareca sem registro.

Uso:
  uv run python pipeline/catalogo/roda_piloto.py --anotador claude --limite 4
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.catalogo import verifica

PROMPT = Path("pipeline/prompts/catalogacao_debates.md")
JANELAS = Path("dados/catalogo/piloto_janelas.jsonl")
DIR_SAIDA = Path("dados/catalogo")

TIMEOUT_S = 600


def carrega_janelas(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8") as arquivo:
        return [json.loads(linha) for linha in arquivo if linha.strip()]


def monta_prompt(gabarito: str, janela: dict) -> str:
    return (
        gabarito.replace("{JANELA_ID}", janela["janela_id"])
        .replace("{JORNAL}", janela["jornal"])
        .replace("{ANO}", str(janela["ano"]))
        .replace("{TEXTO}", janela["texto"])
    )


def extrai_json(resposta: str) -> tuple[list[dict] | None, str]:
    """Array JSON da resposta, tolerando cerca de codigo e prosa em volta.

    Le o PRIMEIRO array que decodifica por completo, em vez de ir do primeiro
    colchete ao ultimo da resposta. O anotador as vezes acrescenta um
    comentario depois do array, e se esse comentario citar colchetes o corte
    pelo ultimo `]` invalida uma anotacao que estava correta. Aconteceu na
    retomada de 31/07 e custou uma janela.
    """
    texto = resposta.strip()
    if texto.startswith("```"):
        linhas = [l for l in texto.splitlines() if not l.strip().startswith("```")]
        texto = "\n".join(linhas).strip()

    decodificador = json.JSONDecoder()
    inicio, ultimo_erro = texto.find("["), None
    while inicio != -1:
        try:
            valor, _ = decodificador.raw_decode(texto[inicio:])
        except json.JSONDecodeError as erro:
            ultimo_erro = erro.msg
            inicio = texto.find("[", inicio + 1)
            continue
        if not isinstance(valor, list):
            return None, "json_nao_e_array"
        return [x for x in valor if isinstance(x, dict)], "ok"

    if ultimo_erro is not None:
        return None, f"json_invalido: {ultimo_erro}"
    return None, "sem_array_json"


WRAPPER = Path("scripts/invoca-codex.ps1")
DIR_MANIFESTOS = Path("colaboracao/manifestos")


def versao_cli(comando: list[str]) -> str:
    try:
        saida = subprocess.run(
            comando, capture_output=True, text=True, encoding="utf-8", timeout=60
        )
        return (saida.stdout or saida.stderr).strip().splitlines()[0][:120]
    except Exception:  # noqa: BLE001 - versao e metadado, nao pode derrubar a corrida
        return "desconhecida"


def chama_claude(prompt: str, _seq: int) -> tuple[str, dict]:
    concluido = subprocess.run(
        ["claude", "-p"],
        input=prompt,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=TIMEOUT_S,
    )
    if concluido.returncode != 0:
        raise RuntimeError(
            f"claude falhou ({concluido.returncode}): {concluido.stderr[:400]}"
        )
    return concluido.stdout, {"servico": "claude-code-cli"}


def chama_codex(prompt: str, seq: int) -> tuple[str, dict]:
    """Invoca o Codex SEMPRE pelo wrapper, no modo anotacao.

    O wrapper garante encoding, isolamento, `--ephemeral`,
    `--ignore-user-config` e o registro de proveniencia em
    colaboracao/registros/. Chamar `codex exec` direto aqui perderia tudo
    isso e violaria a regra da CLAUDE.md.
    """
    DIR_MANIFESTOS.mkdir(parents=True, exist_ok=True)
    task_id = f"catalogo-piloto-{seq:03d}"
    manifesto = DIR_MANIFESTOS / f"{task_id}.md"
    manifesto.write_text(prompt, encoding="utf-8", newline="\n")

    concluido = subprocess.run(
        [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(WRAPPER),
            "-Manifesto", str(manifesto),
            "-TaskId", task_id,
            "-Modo", "anotacao",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",  # PowerShell escreve no codepage do console, nao em UTF-8
        timeout=TIMEOUT_S,
    )
    if concluido.returncode != 0:
        raise RuntimeError(
            f"wrapper falhou ({concluido.returncode}): "
            f"{(concluido.stderr or concluido.stdout)[-900:]}"
        )

    # Os caminhos NAO sao lidos do stdout do PowerShell: o console escreve no
    # codepage local e o caminho do repo tem acento (Academico, Dissertacao),
    # entao a decodificacao corrompe a string e o arquivo nunca e encontrado.
    # O wrapper ja nomeia a saida por task_id, entao localizamos por padrao.
    def mais_recente(diretorio: Path, sufixo: str) -> Path | None:
        achados = sorted(
            diretorio.glob(f"{task_id}--*{sufixo}"),
            key=lambda p: p.stat().st_mtime,
        )
        return achados[-1] if achados else None

    saida = mais_recente(Path("colaboracao/anotacoes"), ".json")
    resposta = saida.read_text(encoding="utf-8") if saida else ""

    meta = {"servico": "codex-cli", "saida": str(saida).replace("\\", "/") if saida else None}
    registro = mais_recente(Path("colaboracao/registros"), ".json")
    if registro is not None and registro.is_file():
        dados = json.loads(registro.read_text(encoding="utf-8"))
        meta |= {
            "modelo": dados.get("modelo_reportado") or dados.get("modelo_solicitado"),
            "versao": dados.get("versao_cli"),
            "effort": dados.get("effort_solicitado"),
            "registro": str(registro).replace("\\", "/"),
            "token_usage": dados.get("token_usage"),
        }
    return resposta, meta


ANOTADORES = {"claude": chama_claude, "codex": chama_codex}
VERSAO_CMD = {"claude": ["claude", "--version"], "codex": ["codex.cmd", "--version"]}


def indexa_feitas(linhas: list[dict]) -> dict[str, dict]:
    """Ultima tentativa BEM SUCEDIDA de cada janela, por janela_id.

    Falha nao entra: janela que caiu continua pendente. A tentativa mais
    recente vence, porque o JSONL bruto e append-only e uma retomada
    posterior e, por definicao, a melhor informacao disponivel.
    """
    feitas: dict[str, dict] = {}
    for linha in linhas:
        if linha.get("status") == "ok" and linha.get("janela_id"):
            feitas[linha["janela_id"]] = linha
    return feitas


def le_jsonl(caminho: Path) -> list[dict]:
    if not caminho.exists():
        return []
    texto = caminho.read_text(encoding="utf-8")
    return [json.loads(linha) for linha in texto.splitlines() if linha.strip()]


def executa(
    *,
    janelas: list[dict],
    gabarito: str,
    prompt_sha: str,
    versao: str,
    anotador: str,
    chama,
    dir_saida: Path,
    retomar: bool = False,
) -> dict:
    """Roda o anotador nas janelas pendentes e reconfere TODAS as citacoes.

    Com `retomar`, as janelas que ja tem registro `ok` sao reaproveitadas e o
    JSONL bruto nao e truncado, porque ele guarda tambem as tentativas que
    falharam e essa historia e proveniencia, nao lixo.
    """
    dir_saida.mkdir(parents=True, exist_ok=True)
    caminho_bruto = dir_saida / f"anotacoes_{anotador}.jsonl"

    feitas = indexa_feitas(le_jsonl(caminho_bruto)) if retomar else {}
    if not retomar:
        caminho_bruto.write_text("", encoding="utf-8")

    registros: list[dict] = []
    for linha in feitas.values():
        for registro in linha.get("registros") or []:
            registro.setdefault("janela_id", linha["janela_id"])
            registros.append(registro)

    pendentes = [
        (n, janela)
        for n, janela in enumerate(janelas, 1)
        if janela["janela_id"] not in feitas
    ]
    falhas = 0
    for posicao, (n, janela) in enumerate(pendentes, 1):
        inicio = time.monotonic()
        try:
            resposta, meta = chama(monta_prompt(gabarito, janela), n)
            erro = None
        except Exception as excecao:  # noqa: BLE001 - registrar e seguir
            resposta, meta, erro = "", {}, str(excecao)[:400]
        decorrido = time.monotonic() - inicio

        parsed, motivo = (None, erro) if erro else extrai_json(resposta)
        linha = {
            "janela_id": janela["janela_id"],
            "anotador": anotador,
            "versao_cli": versao,
            "prompt": str(PROMPT).replace("\\", "/"),
            "prompt_sha": prompt_sha,
            "proveniencia": meta,
            "quando": datetime.now(timezone.utc).isoformat(),
            "segundos": round(decorrido, 1),
            "status": "ok" if parsed is not None else "falha",
            "motivo": motivo,
            "resposta_crua": resposta,
            "registros": parsed or [],
        }
        # O JSONL e reaberto a cada linha, em vez de ficar aberto na corrida
        # inteira, porque o wrapper do Codex calcula hash de TODO arquivo nao
        # rastreado do repo para o snapshot de proveniencia. Um arquivo aberto
        # para escrita aqui vira violacao de compartilhamento la.
        with open(caminho_bruto, "a", encoding="utf-8", newline="\n") as saida:
            saida.write(json.dumps(linha, ensure_ascii=False) + "\n")

        if parsed is None:
            falhas += 1
        else:
            for registro in parsed:
                registro.setdefault("janela_id", janela["janela_id"])
                registros.append(registro)
        print(
            f"[{posicao}/{len(pendentes)}] janela {n:03d} "
            f"{janela['janela_id'][:42]:42s} "
            f"{linha['status']:5s} {len(parsed or []):2d} reg  {decorrido:5.1f}s"
        )

    texto_por_id = {j["janela_id"]: j["texto"] for j in janelas}
    aceitos, rejeitados = verifica.confere_registros(registros, texto_por_id)

    (dir_saida / f"aceitos_{anotador}.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in aceitos),
        encoding="utf-8",
    )
    (dir_saida / f"rejeitados_{anotador}.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rejeitados),
        encoding="utf-8",
    )

    motivos: dict[str, int] = {}
    for r in rejeitados:
        motivos[r["motivo_rejeicao"]] = motivos.get(r["motivo_rejeicao"], 0) + 1

    return {
        "janelas": len(janelas),
        "reaproveitadas": len(feitas),
        "chamadas": len(pendentes),
        "falhas": falhas,
        "registros": len(registros),
        "aceitos": len(aceitos),
        "rejeitados": len(rejeitados),
        "taxa": verifica.taxa_rejeicao(aceitos, rejeitados),
        "motivos": motivos,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anotador", choices=sorted(ANOTADORES), required=True)
    parser.add_argument("--limite", type=int, default=0, help="0 = todas")
    parser.add_argument("--janelas", type=Path, default=JANELAS)
    parser.add_argument(
        "--retomar",
        action="store_true",
        help="pula janelas que ja tem anotacao ok e nao trunca o bruto",
    )
    args = parser.parse_args()

    gabarito = PROMPT.read_text(encoding="utf-8")
    prompt_sha = hashlib.sha256(gabarito.encode("utf-8")).hexdigest()[:16]
    janelas = carrega_janelas(args.janelas)
    if args.limite:
        janelas = janelas[: args.limite]

    versao = versao_cli(VERSAO_CMD[args.anotador])
    print(f"anotador {args.anotador} | cli {versao} | prompt {prompt_sha}")

    resumo = executa(
        janelas=janelas,
        gabarito=gabarito,
        prompt_sha=prompt_sha,
        versao=versao,
        anotador=args.anotador,
        chama=ANOTADORES[args.anotador],
        dir_saida=DIR_SAIDA,
        retomar=args.retomar,
    )

    print(f"\n== {args.anotador} | prompt {prompt_sha} ==")
    print(
        f"janelas: {resumo['janelas']} | reaproveitadas: {resumo['reaproveitadas']} "
        f"| chamadas: {resumo['chamadas']} | falha de chamada ou parse: {resumo['falhas']}"
    )
    print(f"registros devolvidos: {resumo['registros']}")
    print(
        f"aceitos: {resumo['aceitos']} | rejeitados: {resumo['rejeitados']} "
        f"| taxa {resumo['taxa']:.1%}"
    )
    for motivo, n in sorted(resumo["motivos"].items(), key=lambda x: -x[1]):
        print(f"  {motivo}: {n}")


if __name__ == "__main__":
    main()
