r"""PreToolUse: barra etapa paga de API enquanto o portão de 1906 não passar.

Converte o guardrail número um do CLAUDE.md ("nunca rodar lote completo de API
sem antes passar a regressão de 1906") de prosa em barreira executável.

Casa apenas as etapas que gastam token: `pipeline/anotadores`,
`pipeline/transcricao` e `pipeline/classificacao`. Qualquer outro comando passa
sem tocar no portão, para o hook não virar pedágio no trabalho do dia a dia.

Protocolo: exit 0 libera, exit 2 bloqueia e devolve a mensagem do stderr ao
modelo. Não existe variável de escape: liberar é ratificar o manifesto de
exceções ou reproduzir as edições faltantes, que é exatamente o que o
pré-registro de 2026-07-18 pede.

Falha fecha, não abre. Se o evento não for JSON legível (o PowerShell prefixa
BOM ao encanar para executável nativo, por exemplo), o payload cru ainda é
varrido pelo padrão em vez de passar livre; e portão inexecutável bloqueia.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

ETAPAS_PAGAS = re.compile(
    r"pipeline[./\\](anotadores|transcricao|classificacao)\b", re.IGNORECASE
)


def main() -> int:
    # utf-8-sig porque o PowerShell prefixa BOM ao encanar para nativo.
    texto = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace")
    try:
        evento = json.loads(texto)
        alvo = str((evento.get("tool_input") or {}).get("command", ""))
    except Exception:
        # Sem estrutura legível, varre o payload cru: um evento ilegível não
        # pode virar passe livre para etapa paga.
        alvo = texto

    if not ETAPAS_PAGAS.search(alvo):
        return 0

    try:
        proc = subprocess.run(
            ["uv", "run", "python", "-m", "pipeline.base.portao_1906"],
            cwd=RAIZ,
            capture_output=True,
            text=True,
            encoding="utf-8",  # senão o Windows decodifica em cp1252 e sai mojibake
            errors="replace",
            timeout=180,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
    except Exception as erro:  # portão inexecutável é motivo para barrar, não liberar
        print(
            f"BLOQUEADO: o portão de 1906 não pôde ser executado ({erro}).\n"
            "Um lote pago não roda sem veredito do portão.",
            file=sys.stderr,
        )
        return 2

    if proc.returncode == 0:
        return 0

    print(
        "BLOQUEADO pelo portão de 1906 (guardrail não negociável do CLAUDE.md).\n\n"
        f"{proc.stdout.strip()}\n\n"
        "Para liberar, uma das duas:\n"
        "  1. Pedro ratifica pipeline/base/manifests/excecoes_portao_1906.json\n"
        "     (preencher aprovado_por e aprovado_em), conferindo antes a classe\n"
        "     de cada item; ou\n"
        "  2. as edições faltantes são reproduzidas no censo.\n\n"
        "Não edite o manifesto por conta própria: a ratificação é decisão de\n"
        "Pedro pelo protocolo de nível crítico.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
