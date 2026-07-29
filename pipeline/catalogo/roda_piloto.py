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
    """Array JSON da resposta, tolerando cerca de código em volta."""
    texto = resposta.strip()
    if texto.startswith("```"):
        linhas = [l for l in texto.splitlines() if not l.strip().startswith("```")]
        texto = "\n".join(linhas).strip()
    inicio, fim = texto.find("["), texto.rfind("]")
    if inicio == -1 or fim == -1 or fim < inicio:
        return None, "sem_array_json"
    try:
        valor = json.loads(texto[inicio : fim + 1])
    except json.JSONDecodeError as erro:
        return None, f"json_invalido: {erro.msg}"
    if not isinstance(valor, list):
        return None, "json_nao_e_array"
    return [x for x in valor if isinstance(x, dict)], "ok"


def chama_claude(prompt: str) -> str:
    concluido = subprocess.run(
        ["claude", "-p"],
        input=prompt,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=TIMEOUT_S,
    )
    if concluido.returncode != 0:
        raise RuntimeError(f"claude falhou ({concluido.returncode}): {concluido.stderr[:400]}")
    return concluido.stdout


def chama_codex(prompt: str) -> str:
    concluido = subprocess.run(
        ["codex.cmd", "exec", "--skip-git-repo-check", "-"],
        input=prompt,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=TIMEOUT_S,
    )
    if concluido.returncode != 0:
        raise RuntimeError(f"codex falhou ({concluido.returncode}): {concluido.stderr[:400]}")
    return concluido.stdout


ANOTADORES = {"claude": chama_claude, "codex": chama_codex}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anotador", choices=sorted(ANOTADORES), required=True)
    parser.add_argument("--limite", type=int, default=0, help="0 = todas")
    parser.add_argument("--janelas", type=Path, default=JANELAS)
    args = parser.parse_args()

    gabarito = PROMPT.read_text(encoding="utf-8")
    prompt_sha = hashlib.sha256(gabarito.encode("utf-8")).hexdigest()[:16]
    janelas = carrega_janelas(args.janelas)
    if args.limite:
        janelas = janelas[: args.limite]

    chama = ANOTADORES[args.anotador]
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    caminho_bruto = DIR_SAIDA / f"anotacoes_{args.anotador}.jsonl"

    registros: list[dict] = []
    falhas: list[dict] = []
    with open(caminho_bruto, "w", encoding="utf-8", newline="\n") as saida:
        for n, janela in enumerate(janelas, 1):
            inicio = time.monotonic()
            try:
                resposta = chama(monta_prompt(gabarito, janela))
                erro = None
            except Exception as excecao:  # noqa: BLE001 - registrar e seguir
                resposta, erro = "", str(excecao)[:400]
            decorrido = time.monotonic() - inicio

            parsed, motivo = (None, erro) if erro else extrai_json(resposta)
            linha = {
                "janela_id": janela["janela_id"],
                "anotador": args.anotador,
                "prompt_sha": prompt_sha,
                "quando": datetime.now(timezone.utc).isoformat(),
                "segundos": round(decorrido, 1),
                "status": "ok" if parsed is not None else "falha",
                "motivo": motivo,
                "resposta_crua": resposta,
                "registros": parsed or [],
            }
            saida.write(json.dumps(linha, ensure_ascii=False) + "\n")
            saida.flush()

            if parsed is None:
                falhas.append(linha)
            else:
                for registro in parsed:
                    registro.setdefault("janela_id", janela["janela_id"])
                    registros.append(registro)
            print(
                f"[{n}/{len(janelas)}] {janela['janela_id'][:42]:42s} "
                f"{linha['status']:5s} {len(parsed or []):2d} reg  {decorrido:5.1f}s"
            )

    texto_por_id = {j["janela_id"]: j["texto"] for j in janelas}
    aceitos, rejeitados = verifica.confere_registros(registros, texto_por_id)
    taxa = verifica.taxa_rejeicao(aceitos, rejeitados)

    (DIR_SAIDA / f"aceitos_{args.anotador}.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in aceitos),
        encoding="utf-8",
    )
    (DIR_SAIDA / f"rejeitados_{args.anotador}.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rejeitados),
        encoding="utf-8",
    )

    print(f"\n== {args.anotador} | prompt {prompt_sha} ==")
    print(f"janelas: {len(janelas)} | falha de chamada ou parse: {len(falhas)}")
    print(f"registros devolvidos: {len(registros)}")
    print(f"aceitos: {len(aceitos)} | rejeitados: {len(rejeitados)} | taxa {taxa:.1%}")
    motivos: dict[str, int] = {}
    for r in rejeitados:
        motivos[r["motivo_rejeicao"]] = motivos.get(r["motivo_rejeicao"], 0) + 1
    for motivo, n in sorted(motivos.items(), key=lambda x: -x[1]):
        print(f"  {motivo}: {n}")


if __name__ == "__main__":
    main()
