# Amostra de caracterização de registro (Passo 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir o amostrador estratificado de contextos de match que produz o CSV rotulável do Passo 1 da medida de substância, para Pedro validar as três etiquetas de registro antes de qualquer detector.

**Architecture:** Um módulo novo `pipeline/triagem/amostra_registro.py` que reusa `db_leitura` (leitura da camada de texto) e `regra_nome` (spans do nome), enumera todos os matches do censo com uma janela de contexto ampla, sorteia uma amostra estratificada por jornal × ano com semente fixa, e escreve um CSV determinístico com uma coluna `registro` vazia para Pedro rotular. Sem detector de registro nesta fase.

**Tech Stack:** Python 3.12, uv, sqlite3, csv, random (stdlib), pytest/unittest. Reusa `pipeline.triagem.db_leitura` e `pipeline.triagem.regra_nome`, já implementados e testados.

## Global Constraints

- Rodar sempre via `uv run python ...`; nunca pip/venv manuais.
- `from __future__ import annotations` no topo; dataclasses `frozen=True, slots=True`; nomes em português; estilo dos módulos existentes de `pipeline/triagem/`.
- Testes em `unittest.TestCase` rodáveis sob pytest, no padrão de `tests/test_triagem.py` (banco real em tempdir, sem mock).
- Manifesto/amostra em CSV utf-8, `lineterminator="\n"`, determinístico (mesma entrada, bytes idênticos), entra no git (texto leve, domínio público).
- Piloto metodológico: nenhum texto é descartado; a amostra é uma vista rastreável. Proveniência: semente e `regra_nome.REGRA_VERSAO` registradas.
- Não abrir a API (custo zero de token); leitura do banco é somente-leitura na prática (nenhum INSERT).
- `match_id` estável e único: `{source_identifier}:p{page:03d}:o{offset}`.

---

### Task 1: Enumeração de matches com contexto amplo

**Files:**
- Create: `pipeline/triagem/amostra_registro.py`
- Test: `tests/test_amostra_registro.py`

**Interfaces:**
- Consumes: `db_leitura.itera_paginas(conn, bib=, ano=)`, `db_leitura.le_conteudo(pagina)`, `regra_nome.normaliza(texto)`, `regra_nome.encontra(texto) -> list[Span]` (Span tem `.offset`, `.texto`).
- Produces: `MatchContexto` (dataclass) e `enumera_matches(conn, *, bib=None, ano=None) -> Iterator[MatchContexto]`.

- [ ] **Step 1: Write the failing test**

Em `tests/test_amostra_registro.py`. Reusa o helper `_semeia` de `tests/test_triagem.py` copiando o setup mínimo (newspaper, protocolos, objeto+páginas+texto). Para evitar duplicação grande, este teste importa o setup por herança:

```python
from __future__ import annotations

import csv
import random
import unittest
from pathlib import Path

from pipeline.triagem import amostra_registro
from tests.test_triagem import TriagemTests  # reusa setUp e _semeia


class EnumeraMatchesTests(TriagemTests):
    def test_enumera_um_match_por_span_com_contexto(self) -> None:
        self._semeia(
            "178691", 1906, "00001",
            ["a creacao da caixa de conversao para fixar o cambio", None],
        )
        matches = list(amostra_registro.enumera_matches(self.conn, bib="178691"))
        self.assertEqual(1, len(matches))
        m = matches[0]
        self.assertEqual("per178691_1906_00001:p001:o13", m.match_id)
        self.assertEqual("178691", m.bib)
        self.assertEqual(1906, m.source_year)
        self.assertEqual(1, m.page_number)
        self.assertIn("caixa de conver", m.texto)
        self.assertIn("creacao da caixa de conversao para fixar", m.contexto)

    def test_pagina_sem_texto_nao_entra(self) -> None:
        self._semeia("178691", 1906, "00002", [None])
        matches = list(amostra_registro.enumera_matches(self.conn, bib="178691"))
        self.assertEqual([], matches)
```

Nota sobre o offset esperado (`o13`): em `"a creacao da caixa de conversao..."` normalizado, "caixa" começa no índice 13. Confirme com `regra_nome.normaliza` se ajustar o texto do teste.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m pytest tests/test_amostra_registro.py -q`
Expected: FAIL com `ModuleNotFoundError` ou `AttributeError: module 'pipeline.triagem.amostra_registro' has no attribute 'enumera_matches'`.

- [ ] **Step 3: Write minimal implementation**

Em `pipeline/triagem/amostra_registro.py`:

```python
"""Amostra estratificada de contextos de match (Passo 1 da medida de
substância). Enumera os matches do nome no censo com janela de contexto
ampla e sorteia uma amostra por jornal-ano, com semente fixa, para Pedro
rotular o registro (incidental/operacional_rotina/substantivo) antes de
qualquer detector. Contrato: docs/superpowers/specs/
2026-07-21-decomposicao-registro-substancia-design.md.
"""

from __future__ import annotations

import argparse
import csv
import random
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.base import db
from pipeline.triagem import db_leitura, regra_nome
from pipeline.triagem.roda_censo import DIR_MANIFESTO

CONTEXTO_AMPLO = 120
SEMENTE_PADRAO = 20260721
POR_CELULA_PADRAO = 12


@dataclass(frozen=True, slots=True)
class MatchContexto:
    match_id: str
    bib: str
    newspaper: str
    source_year: int
    source_identifier: str
    page_number: int
    offset: int
    texto: str
    contexto: str


def enumera_matches(
    conn: sqlite3.Connection,
    *,
    bib: str | None = None,
    ano: int | None = None,
) -> Iterator[MatchContexto]:
    """Um MatchContexto por span do nome nas páginas com texto vigente ok."""
    for pagina in db_leitura.itera_paginas(conn, bib=bib, ano=ano):
        if pagina.result_status != "ok":
            continue
        texto = db_leitura.le_conteudo(pagina)
        normalizado = regra_nome.normaliza(texto)
        for span in regra_nome.encontra(texto):
            ini = max(0, span.offset - CONTEXTO_AMPLO)
            fim = min(len(normalizado), span.offset + len(span.texto) + CONTEXTO_AMPLO)
            yield MatchContexto(
                match_id=(
                    f"{pagina.source_identifier}"
                    f":p{pagina.page_number:03d}:o{span.offset}"
                ),
                bib=pagina.bib,
                newspaper=pagina.newspaper,
                source_year=pagina.source_year,
                source_identifier=pagina.source_identifier,
                page_number=pagina.page_number,
                offset=span.offset,
                texto=span.texto,
                contexto=normalizado[ini:fim],
            )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run python -m pytest tests/test_amostra_registro.py -q`
Expected: PASS (2 passed). Se o offset esperado divergir, ajuste o texto do teste ou o valor `o13` conforme `regra_nome.normaliza`.

- [ ] **Step 5: Commit**

```bash
git add pipeline/triagem/amostra_registro.py tests/test_amostra_registro.py
git commit -m "feat: enumeracao de matches com contexto amplo (amostra passo 1)"
```

---

### Task 2: Amostra estratificada determinística

**Files:**
- Modify: `pipeline/triagem/amostra_registro.py`
- Test: `tests/test_amostra_registro.py`

**Interfaces:**
- Consumes: `enumera_matches` (Task 1).
- Produces: `amostra_estratificada(conn, *, por_celula=POR_CELULA_PADRAO, semente=SEMENTE_PADRAO) -> list[MatchContexto]`.

- [ ] **Step 1: Write the failing test**

Adicione em `tests/test_amostra_registro.py`:

```python
class AmostraEstratificadaTests(TriagemTests):
    def _semeia_celula(self, bib: str, ano: int, n: int) -> None:
        for i in range(n):
            self._semeia(
                bib, ano, f"{i:05d}",
                [f"item {i} sobre a caixa de conversao e o cambio"],
            )

    def test_amostra_por_celula_e_determinista(self) -> None:
        self._semeia_celula("178691", 1906, 20)
        self._semeia_celula("090972", 1906, 5)  # célula menor que por_celula
        a = amostra_registro.amostra_estratificada(
            self.conn, por_celula=3, semente=7
        )
        # 3 de O Paiz + todos os 5 do Correio Paulistano (menor que 3? não: 5>=3 -> 3)
        celulas = {}
        for m in a:
            celulas.setdefault((m.bib, m.source_year), 0)
            celulas[(m.bib, m.source_year)] += 1
        self.assertEqual(3, celulas[("178691", 1906)])
        self.assertEqual(3, celulas[("090972", 1906)])
        # determinismo: mesma semente, mesma amostra
        b = amostra_registro.amostra_estratificada(
            self.conn, por_celula=3, semente=7
        )
        self.assertEqual([m.match_id for m in a], [m.match_id for m in b])

    def test_celula_menor_que_cota_leva_tudo(self) -> None:
        self._semeia_celula("178691", 1906, 2)
        a = amostra_registro.amostra_estratificada(
            self.conn, por_celula=5, semente=1
        )
        self.assertEqual(2, len(a))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m pytest tests/test_amostra_registro.py::AmostraEstratificadaTests -q`
Expected: FAIL com `AttributeError: ... has no attribute 'amostra_estratificada'`.

- [ ] **Step 3: Write minimal implementation**

Adicione em `pipeline/triagem/amostra_registro.py`:

```python
def amostra_estratificada(
    conn: sqlite3.Connection,
    *,
    por_celula: int = POR_CELULA_PADRAO,
    semente: int = SEMENTE_PADRAO,
) -> list[MatchContexto]:
    """Amostra até `por_celula` matches por (bib, ano), semente fixa.

    População de cada célula ordenada por match_id antes do sorteio, para o
    resultado ser byte-idêntico entre execuções."""
    rng = random.Random(semente)
    por_celula_matches: dict[tuple[str, int], list[MatchContexto]] = {}
    for m in enumera_matches(conn):
        por_celula_matches.setdefault((m.bib, m.source_year), []).append(m)
    escolhidos: list[MatchContexto] = []
    for chave in sorted(por_celula_matches):
        populacao = sorted(
            por_celula_matches[chave], key=lambda m: m.match_id
        )
        cota = min(por_celula, len(populacao))
        escolhidos.extend(rng.sample(populacao, cota))
    return sorted(escolhidos, key=lambda m: m.match_id)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run python -m pytest tests/test_amostra_registro.py::AmostraEstratificadaTests -q`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add pipeline/triagem/amostra_registro.py tests/test_amostra_registro.py
git commit -m "feat: amostra estratificada determinista por jornal-ano"
```

---

### Task 3: Escrita do CSV rotulável

**Files:**
- Modify: `pipeline/triagem/amostra_registro.py`
- Test: `tests/test_amostra_registro.py`

**Interfaces:**
- Consumes: `MatchContexto` (Task 1).
- Produces: `CABECALHO_AMOSTRA` (list[str]) e `escreve_amostra(matches: list[MatchContexto], caminho: Path) -> int`.

- [ ] **Step 1: Write the failing test**

Adicione em `tests/test_amostra_registro.py`:

```python
class EscreveAmostraTests(TriagemTests):
    def test_csv_deterministico_com_coluna_registro_vazia(self) -> None:
        self._semeia("178691", 1906, "00001", ["a caixa de conversao aqui"])
        matches = list(amostra_registro.enumera_matches(self.conn, bib="178691"))
        caminho = self.tmp / "amostra.csv"
        n = amostra_registro.escreve_amostra(matches, caminho)
        self.assertEqual(1, n)
        primeira = caminho.read_bytes()
        amostra_registro.escreve_amostra(matches, caminho)
        self.assertEqual(primeira, caminho.read_bytes())  # determinístico
        linhas = primeira.decode("utf-8").splitlines()
        self.assertEqual(
            ",".join(amostra_registro.CABECALHO_AMOSTRA), linhas[0]
        )
        self.assertTrue(linhas[0].endswith(",registro"))
        self.assertTrue(linhas[1].endswith(","))  # coluna registro vazia
        self.assertIn("per178691_1906_00001:p001:o", linhas[1])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m pytest tests/test_amostra_registro.py::EscreveAmostraTests -q`
Expected: FAIL com `AttributeError: ... has no attribute 'CABECALHO_AMOSTRA'`.

- [ ] **Step 3: Write minimal implementation**

Adicione em `pipeline/triagem/amostra_registro.py`:

```python
CABECALHO_AMOSTRA = [
    "match_id",
    "bib",
    "newspaper",
    "source_year",
    "source_identifier",
    "page_number",
    "offset",
    "texto",
    "contexto",
    "registro",
]


def escreve_amostra(matches: list[MatchContexto], caminho: Path) -> int:
    """CSV determinístico com a coluna `registro` vazia para Pedro rotular."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    ordenados = sorted(matches, key=lambda m: m.match_id)
    with caminho.open("w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida, lineterminator="\n")
        escritor.writerow(CABECALHO_AMOSTRA)
        for m in ordenados:
            escritor.writerow(
                [
                    m.match_id,
                    m.bib,
                    m.newspaper,
                    m.source_year,
                    m.source_identifier,
                    m.page_number,
                    m.offset,
                    m.texto,
                    m.contexto,
                    "",
                ]
            )
    return len(ordenados)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run python -m pytest tests/test_amostra_registro.py::EscreveAmostraTests -q`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add pipeline/triagem/amostra_registro.py tests/test_amostra_registro.py
git commit -m "feat: escrita do CSV rotulavel da amostra de registro"
```

---

### Task 4: CLI, execução real e commit da amostra

**Files:**
- Modify: `pipeline/triagem/amostra_registro.py`
- Output: `dados/triagem/amostra_registro.csv`

**Interfaces:**
- Consumes: `amostra_estratificada`, `escreve_amostra`.
- Produces: `main(argv=None) -> int` e o CSV `dados/triagem/amostra_registro.csv`.

- [ ] **Step 1: Adicionar `main` (sem teste dedicado; é orquestração fina)**

Adicione ao fim de `pipeline/triagem/amostra_registro.py`:

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Amostra estratificada de contextos de match (Passo 1)"
    )
    parser.add_argument("--base", default=str(db.DEFAULT_DATABASE))
    parser.add_argument(
        "--saida", default=str(DIR_MANIFESTO / "amostra_registro.csv")
    )
    parser.add_argument("--por-celula", type=int, default=POR_CELULA_PADRAO)
    parser.add_argument("--semente", type=int, default=SEMENTE_PADRAO)
    args = parser.parse_args(argv)

    conn = db.connect(args.base, migrate=False)
    try:
        matches = amostra_estratificada(
            conn, por_celula=args.por_celula, semente=args.semente
        )
    finally:
        conn.close()
    n = escreve_amostra(matches, Path(args.saida))
    celulas = len({(m.bib, m.source_year) for m in matches})
    print(
        f"amostra: {n} contextos, {celulas} celulas, "
        f"semente={args.semente}, por_celula={args.por_celula} -> {args.saida}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Rodar a suíte inteira para garantir que nada regrediu**

Run: `uv run python -m pytest tests/ -q`
Expected: PASS (todos; deve subir de 128 para ~135 com os testes novos).

- [ ] **Step 3: Gerar a amostra real contra o censo**

Run: `uv run python -m pipeline.triagem.amostra_registro`
Expected: imprime algo como `amostra: ~400 contextos, ~35 celulas, semente=20260721, por_celula=12 -> .../amostra_registro.csv`. (Leitura de ~117k páginas leva alguns minutos.)

- [ ] **Step 4: Conferir o CSV a olho antes de commitar**

Run: `uv run python -c "import csv; r=list(csv.DictReader(open(r'dados/triagem/amostra_registro.csv',encoding='utf-8'))); print(len(r), 'linhas'); [print(x['match_id'], '|', x['contexto'][:80]) for x in r[:8]]"`
Expected: ~400 linhas, contextos legíveis, coluna `registro` vazia. Confirmar que a distribuição por jornal-ano parece razoável.

- [ ] **Step 5: Commit da amostra**

```bash
git add pipeline/triagem/amostra_registro.py dados/triagem/amostra_registro.csv
git commit -m "feat: gera amostra de caracterizacao de registro (~400 contextos)"
```

---

## Depois do plano (fora deste escopo)

Pedro preenche a coluna `registro` do CSV (incidental/operacional_rotina/substantivo) por leitura, definindo se as três etiquetas são exaustivas e suficientes. Esse CSV rotulado vira o conjunto de referência do segundo plano (classificador de registro, integração ao manifesto, `relatorio_registro.py`, calibração), cujos detectores serão fixados e medidos contra ele, com a margem de 5% por edição e a cláusula de calibração já registradas na spec.

## Self-Review

- **Cobertura da spec (Passo 1):** o componente `amostra_registro.py` da spec está coberto pelas Tasks 1-4 (enumeração, amostra estratificada, CSV rotulável, execução). Os demais componentes da spec (classificador, relatório, calibração) são explicitamente fora deste plano, por dependerem dos rótulos de Pedro.
- **Placeholders:** nenhum "TBD/TODO"; todo passo traz código completo e comando com saída esperada. O único valor a confirmar em execução é o offset `o13` no teste da Task 1, com instrução de como verificar.
- **Consistência de tipos:** `MatchContexto` (Task 1) é consumido por `amostra_estratificada` (Task 2), `escreve_amostra` (Task 3) e `main` (Task 4) com os mesmos campos; `CABECALHO_AMOSTRA` (Task 3) usado só na escrita; `enumera_matches`/`amostra_estratificada`/`escreve_amostra` com assinaturas idênticas entre definição e uso.
