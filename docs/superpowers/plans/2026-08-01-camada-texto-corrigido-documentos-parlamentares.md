# Camada de Texto Corrigido dos Documentos Parlamentares Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gerar uma camada derivada, conservadora e auditável para leitura e pesquisa dos dois volumes de *Caixa de Conversão*, preservando ortografia histórica, páginas físicas e vínculo byte a byte com o OCR bruto.

**Architecture:** Separar regras puras de correção, geração de artefatos e validação do corpus. A rotina faz duas passagens: primeiro aprende do próprio corpus os compostos que usam hífen lexical dentro da linha, depois corrige cada página sem cruzar fronteiras físicas e registra toda transformação.

**Tech Stack:** Python 3.11+, biblioteca padrão (`argparse`, `csv`, `dataclasses`, `hashlib`, `json`, `pathlib`, `re`), pytest 8+, JSONL e CSV UTF-8.

## Global Constraints

- O texto bruto em `dados/texto_embutido/fontes_parlamentares/caixa_conversao/` permanece imutável.
- Preservar exatamente 698 páginas do volume 1 e 454 páginas do volume 2.
- Preservar ortografia histórica, incluindo `ph`, `th`, `y`, consoantes dobradas e acentuação de época.
- Não usar correção livre por LLM no corpus integral.
- Não atravessar fronteiras de página durante reflow ou dehifenização.
- Casos duvidosos permanecem como no OCR bruto.
- Toda substituição lexical precisa existir em lista permitida versionada.
- Todo produto usa UTF-8 sem BOM e finais de linha `LF`.
- Nunca usar travessão em textos produzidos para Pedro.
- Citações acadêmicas continuam sendo conferidas no PDF original.

---

## File Map

- Create: `pipeline/base/correcao_texto_parlamentar.py`, regras puras e tipos de dados.
- Create: `pipeline/base/gera_texto_corrigido.py`, leitura dos JSONL, CLI, escrita e replay.
- Create: `pipeline/base/correcoes_lexicais_documentos_parlamentares.csv`, lista permitida versionada.
- Create: `tests/test_correcao_texto_parlamentar.py`, testes unitários das regras.
- Create: `tests/test_gera_texto_corrigido.py`, testes de integração com corpus mínimo.
- Create: `dados/texto_corrigido/fontes_parlamentares/caixa_conversao/`, artefatos derivados gerados.
- Modify: `dados/README.md`, semântica e localização da nova camada.

### Task 1: Núcleo puro de correção conservadora

**Files:**
- Create: `pipeline/base/correcao_texto_parlamentar.py`
- Create: `tests/test_correcao_texto_parlamentar.py`

**Interfaces:**
- Consumes: texto de uma página, `Mapping[str, str]` de correções lexicais e `AbstractSet[str]` de compostos com hífen lexical.
- Produces: `coleta_hifens_lexicais(textos: Iterable[str]) -> frozenset[str]`, `carrega_regras_lexicais(caminho: Path) -> dict[str, str]` e `corrige_pagina(texto: str, *, regras_lexicais: Mapping[str, str], hifens_lexicais: AbstractSet[str]) -> ResultadoCorrecao`.

- [ ] **Step 1: Write failing tests for classification, spaces and historical spelling**

```python
from pipeline.base.correcao_texto_parlamentar import (
    TipoLinha,
    classifica_linha,
    corrige_pagina,
)


def test_classifica_estrutura_sem_usar_sentido():
    assert classifica_linha("SESSÃO DE 25 DE SETEMBRO") is TipoLinha.TITULO
    assert classifica_linha("O SR. ARTHUR ORLANDO. - Sr. Presidente") is TipoLinha.FALA
    assert classifica_linha("1. Projecto da commissão") is TipoLinha.LISTA
    assert classifica_linha("Taxa     15 15/16") is TipoLinha.TABELA
    assert classifica_linha("A emissão será regulada pela lei.") is TipoLinha.PROSA


def test_limpa_espacos_sem_modernizar_ortografia():
    bruto = "O commercio  exterior , segundo a hypothese , cresce."
    resultado = corrige_pagina(
        bruto, regras_lexicais={}, hifens_lexicais=frozenset()
    )
    assert resultado.texto == "O commercio exterior, segundo a hypothese, cresce."
    assert "commercio" in resultado.texto
    assert "hypothese" in resultado.texto
```

- [ ] **Step 2: Run the focused tests and confirm red state**

Run: `uv run pytest tests/test_correcao_texto_parlamentar.py -v`

Expected: FAIL during import because `pipeline.base.correcao_texto_parlamentar` does not exist.

- [ ] **Step 3: Implement types, classification and horizontal cleanup**

```python
from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import AbstractSet, Iterable, Mapping

PROTOCOL_NAME = "correcao-conservadora-documentos-parlamentares"
PROTOCOL_VERSION = "1.0.0"


class TipoLinha(str, Enum):
    VAZIA = "vazia"
    TITULO = "titulo"
    FALA = "fala"
    LISTA = "lista"
    TABELA = "tabela"
    PROSA = "prosa"


@dataclass(frozen=True, slots=True)
class Mudanca:
    tipo: str
    antes: str
    depois: str
    quantidade: int


@dataclass(frozen=True, slots=True)
class ResultadoCorrecao:
    texto: str
    mudancas: tuple[Mudanca, ...]

    @property
    def contagens(self) -> dict[str, int]:
        totais: Counter[str] = Counter()
        for item in self.mudancas:
            totais[item.tipo] += item.quantidade
        return dict(sorted(totais.items()))


_FALA = re.compile(r"^(?:O|A)\s+SR(?:A)?\.", re.IGNORECASE)
_LISTA = re.compile(r"^(?:\d+[.)]|[IVXLCDM]+[.)]|[-*])\s+", re.IGNORECASE)
_PAGINA = re.compile(r"^-?\s*\d+\s*-$")


def classifica_linha(linha: str) -> TipoLinha:
    limpa = linha.strip()
    if not limpa:
        return TipoLinha.VAZIA
    if _FALA.match(limpa):
        return TipoLinha.FALA
    if _LISTA.match(limpa):
        return TipoLinha.LISTA
    if _PAGINA.match(limpa) or "...." in limpa:
        return TipoLinha.TABELA
    if re.search(r"\S\s{3,}\S", linha) and re.search(r"\d", linha):
        return TipoLinha.TABELA
    letras = [c for c in limpa if c.isalpha()]
    if 4 <= len(letras) and len(limpa) <= 120:
        proporcao = sum(c.isupper() for c in letras) / len(letras)
        if proporcao >= 0.8:
            return TipoLinha.TITULO
    return TipoLinha.PROSA
```

- [ ] **Step 4: Run the focused tests and confirm green state**

Run: `uv run pytest tests/test_correcao_texto_parlamentar.py -v`

Expected: PASS for classification and spacing tests.

- [ ] **Step 5: Write failing tests for corpus-derived lexical hyphens**

```python
from pipeline.base.correcao_texto_parlamentar import coleta_hifens_lexicais


def test_coleta_composto_impresso_na_mesma_linha():
    compostos = coleta_hifens_lexicais(
        ["O papel-moeda circula.", "O padrão-ouro foi mencionado."]
    )
    assert compostos == frozenset({"papel-moeda", "padrão-ouro"})


def test_dehifeniza_silaba_mas_preserva_composto_lexical():
    compostos = frozenset({"papel-moeda"})
    bruto = "A circu-\nlante emissão de papel-\nmoeda cresceu."
    resultado = corrige_pagina(
        bruto, regras_lexicais={}, hifens_lexicais=compostos
    )
    assert resultado.texto == "A circulante emissão de papel-moeda cresceu."
    assert resultado.contagens["dehifenizacao"] == 1
```

- [ ] **Step 6: Run the dehyphenation tests and confirm red state**

Run: `uv run pytest tests/test_correcao_texto_parlamentar.py -k hifen -v`

Expected: FAIL because corpus-derived hyphen collection and dehyphenation are not implemented.

- [ ] **Step 7: Implement lexical-hyphen collection and page-local dehyphenation**

```python
_PALAVRA_HIFEN = re.compile(
    r"(?iu)\b([a-zà-öø-ÿ]{2,})-([a-zà-öø-ÿ]{2,})\b"
)
_QUEBRA_HIFEN = re.compile(
    r"(?iu)([a-zà-öø-ÿ]{2,})-[ \t]*\n[ \t]*([a-zà-öø-ÿ]{2,})"
)


def coleta_hifens_lexicais(textos: Iterable[str]) -> frozenset[str]:
    formas = {
        f"{esquerda}-{direita}".casefold()
        for texto in textos
        for esquerda, direita in _PALAVRA_HIFEN.findall(texto)
    }
    return frozenset(formas)


def _dehifeniza(texto: str, hifens_lexicais: AbstractSet[str]):
    mudancas: list[Mudanca] = []

    def troca(match: re.Match[str]) -> str:
        esquerda, direita = match.groups()
        composto = f"{esquerda}-{direita}"
        if composto.casefold() in hifens_lexicais:
            depois = composto
        else:
            depois = esquerda + direita
            mudancas.append(Mudanca("dehifenizacao", match.group(0), depois, 1))
        return depois

    return _QUEBRA_HIFEN.sub(troca, texto), mudancas
```

The final `corrige_pagina` must call `_dehifeniza` only within the supplied page string, so a boundary between JSONL records can never be crossed.

- [ ] **Step 8: Write failing tests for reflow and protected lines**

```python
def test_reflui_prosa_e_preserva_titulo_fala_lista_e_tabela():
    bruto = (
        "SESSÃO DE 25 DE SETEMBRO\n"
        "O SR. ARTHUR ORLANDO. - O projecto\n"
        "não altera a orthographia.\n\n"
        "1. Primeira emenda\n"
        "Taxa     15 15/16\n"
    )
    resultado = corrige_pagina(
        bruto, regras_lexicais={}, hifens_lexicais=frozenset()
    )
    assert resultado.texto == (
        "SESSÃO DE 25 DE SETEMBRO\n"
        "O SR. ARTHUR ORLANDO. - O projecto não altera a orthographia.\n\n"
        "1. Primeira emenda\n"
        "Taxa     15 15/16"
    )
```

- [ ] **Step 9: Implement stateful paragraph reflow**

Implement `_reflui_linhas(texto: str) -> tuple[str, list[Mudanca]]` with these exact transitions:

1. blank line flushes the current paragraph and emits one blank line;
2. `TITULO`, `LISTA` and `TABELA` flush the paragraph and remain on their own line;
3. `FALA` flushes the prior paragraph, starts a new paragraph and accepts following `PROSA` lines;
4. consecutive `PROSA` lines join with one space;
5. an indented `PROSA` line starts a new paragraph only when the previous paragraph ends in `.`, `?`, `!` or `:`;
6. leading and trailing blank lines are removed, internal single blank lines are preserved.

Record one `Mudanca("refluxo_linha", "\n", " ", quantidade)` for the number of joined line boundaries.

- [ ] **Step 10: Write failing tests for allowed lexical rules**

```python
def test_aplica_apenas_substituicao_listada_em_limite_de_token():
    resultado = corrige_pagina(
        "q.ue q.ueiro projecto d'e",
        regras_lexicais={"q.ue": "que"},
        hifens_lexicais=frozenset(),
    )
    assert resultado.texto == "que q.ueiro projecto d'e"
    assert resultado.contagens["correcao_lexical"] == 1
```

- [ ] **Step 11: Implement lexical rules with exact token boundaries**

Compile every allowed raw form with `(?<!\w)` and `(?!\w)`, apply rules in descending raw-form length and record `Mudanca("correcao_lexical", bruto, corrigido, quantidade)` only when at least one replacement occurs. Reject duplicate raw forms, empty fields and identity mappings in `carrega_regras_lexicais`.

- [ ] **Step 12: Run all core tests**

Run: `uv run pytest tests/test_correcao_texto_parlamentar.py -v`

Expected: PASS.

- [ ] **Step 13: Commit the core correction engine**

```bash
git add -- pipeline/base/correcao_texto_parlamentar.py tests/test_correcao_texto_parlamentar.py
git commit -m "feat: adiciona correcao conservadora de OCR parlamentar"
```

### Task 2: Gerador reproduzível de TXT, JSONL e manifestos

**Files:**
- Create: `pipeline/base/gera_texto_corrigido.py`
- Create: `tests/test_gera_texto_corrigido.py`

**Interfaces:**
- Consumes: os dois JSONL brutos, a lista permitida CSV e as funções da Task 1.
- Produces: `gera_corpus(entrada: Path, saida: Path, regras_path: Path) -> dict[str, object]`, `verifica_corpus(entrada: Path, saida: Path, regras_path: Path) -> list[str]` e CLI `python -m pipeline.base.gera_texto_corrigido`.

- [ ] **Step 1: Write failing integration test with two physical pages**

```python
import hashlib
import json

from pipeline.base.gera_texto_corrigido import gera_corpus


def test_gera_jsonl_txt_manifesto_e_relatorio(tmp_path):
    entrada = tmp_path / "bruto"
    saida = tmp_path / "corrigido"
    entrada.mkdir()
    bruto = "A circu-\nlante emissão."
    registros = [
        {
            "source_pdf": "caixa_conversao_v1.pdf",
            "source_pdf_sha256": "a" * 64,
            "volume": 1,
            "pdf_page": 1,
            "result_status": "ok",
            "text_sha256": hashlib.sha256(bruto.encode()).hexdigest(),
            "text": bruto,
        },
        {
            "source_pdf": "caixa_conversao_v1.pdf",
            "source_pdf_sha256": "a" * 64,
            "volume": 1,
            "pdf_page": 2,
            "result_status": "empty",
            "text_sha256": hashlib.sha256(b"").hexdigest(),
            "text": "",
        },
    ]
    caminho = entrada / "caixa_conversao_v1_paginas.jsonl"
    caminho.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in registros),
        encoding="utf-8",
    )
    regras = tmp_path / "regras.csv"
    regras.write_text(
        "forma_bruta,forma_corrigida,justificativa,escopo\n",
        encoding="utf-8",
    )

    resumo = gera_corpus(entrada, saida, regras)

    assert resumo["pages"] == 2
    assert resumo["errors"] == 0
    linhas = (saida / "caixa_conversao_v1_paginas_corrigidas.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()
    assert len(linhas) == 2
    assert json.loads(linhas[0])["corrected_text"] == "A circulante emissão."
    assert json.loads(linhas[1])["status"] == "empty"
```

- [ ] **Step 2: Run the integration test and confirm red state**

Run: `uv run pytest tests/test_gera_texto_corrigido.py -v`

Expected: FAIL during import because the generator does not exist.

- [ ] **Step 3: Implement strict input validation**

For every raw JSONL record, require these fields and invariants:

```python
REQUIRED = {
    "source_pdf",
    "source_pdf_sha256",
    "volume",
    "pdf_page",
    "result_status",
    "text_sha256",
    "text",
}


def valida_registro(registro: dict[str, object]) -> None:
    faltantes = REQUIRED - registro.keys()
    if faltantes:
        raise ValueError(f"campos ausentes: {sorted(faltantes)}")
    texto = registro["text"]
    if not isinstance(texto, str):
        raise TypeError("text deve ser str")
    calculado = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    if calculado != registro["text_sha256"]:
        raise ValueError("text_sha256 não confere")
```

Also require unique, strictly increasing `pdf_page` per volume and a constant source PDF hash inside each volume.

- [ ] **Step 4: Implement the two-pass corpus generator**

Pass 1 loads all raw page strings and calls `coleta_hifens_lexicais`. Pass 2 calls `corrige_pagina` page by page and writes:

```python
{
    "source_pdf": registro["source_pdf"],
    "source_pdf_sha256": registro["source_pdf_sha256"],
    "volume": registro["volume"],
    "pdf_page": registro["pdf_page"],
    "protocol_name": PROTOCOL_NAME,
    "protocol_version": PROTOCOL_VERSION,
    "raw_text_sha256": registro["text_sha256"],
    "corrected_text_sha256": sha256(corrigido.encode("utf-8")).hexdigest(),
    "status": status,
    "raw_char_count": len(bruto),
    "corrected_char_count": len(corrigido),
    "operation_counts": resultado.contagens,
    "corrected_text": corrigido,
}
```

Use `empty` when the raw record is empty, `unchanged` when raw and corrected strings are identical, `ok` when they differ, and `error` only for a caught page-local exception. A structural or provenance failure aborts the run without replacing prior outputs.

- [ ] **Step 5: Write outputs atomically and with stable ordering**

Write every file to a sibling `*.part`, close it, calculate its SHA-256, then replace the final path with `Path.replace`. Sort manifest rows by `(volume, pdf_page)`. Use `json.dumps(..., ensure_ascii=False, separators=(",", ":"))` for JSONL and `lineterminator="\n"` for CSV.

The integral TXT must use these exact markers:

```text
===== PAGINA_PDF 0001 =====
[corrected page text]
===== FIM_PAGINA_PDF 0001 =====
```

- [ ] **Step 6: Implement replay verification**

`verifica_corpus` reruns both passes without writing and compares corrected page hashes, statuses, operation counts, page order and output file hashes. It returns a list of human-readable divergences and never mutates output.

- [ ] **Step 7: Implement CLI**

```text
python -m pipeline.base.gera_texto_corrigido \
  --entrada dados/texto_embutido/fontes_parlamentares/caixa_conversao \
  --saida dados/texto_corrigido/fontes_parlamentares/caixa_conversao \
  --regras pipeline/base/correcoes_lexicais_documentos_parlamentares.csv

python -m pipeline.base.gera_texto_corrigido \
  --entrada dados/texto_embutido/fontes_parlamentares/caixa_conversao \
  --saida dados/texto_corrigido/fontes_parlamentares/caixa_conversao \
  --regras pipeline/base/correcoes_lexicais_documentos_parlamentares.csv \
  --verificar
```

The first command exits 0 only with zero page errors. The second exits 0 only with an empty divergence list.

- [ ] **Step 8: Add failure tests**

Add exact tests for hash mismatch, duplicate page, missing page, unknown status, atomic cleanup after a forced exception and replay detection after a corrected JSONL is adulterated.

- [ ] **Step 9: Run generator tests and the core regression tests**

Run: `uv run pytest tests/test_gera_texto_corrigido.py tests/test_correcao_texto_parlamentar.py -v`

Expected: PASS.

- [ ] **Step 10: Commit the generator**

```bash
git add -- pipeline/base/gera_texto_corrigido.py tests/test_gera_texto_corrigido.py
git commit -m "feat: gera camada auditavel de texto corrigido"
```

### Task 3: Lista permitida e calibração conservadora

**Files:**
- Create: `pipeline/base/correcoes_lexicais_documentos_parlamentares.csv`
- Modify: `tests/test_correcao_texto_parlamentar.py`

**Interfaces:**
- Consumes: padrões recorrentes observados nos dois JSONL brutos.
- Produces: CSV versionado com `forma_bruta,forma_corrigida,justificativa,escopo`.

- [ ] **Step 1: Create the initial high-confidence allowlist**

```csv
forma_bruta,forma_corrigida,justificativa,escopo
q.ue,que,pontuação espúria dentro de palavra,ambos
qu.e,que,pontuação espúria dentro de palavra,ambos
q,ue,que,pontuação espúria dentro de palavra,ambos
q:ue,que,pontuação espúria dentro de palavra,ambos
par.a,para,pontuação espúria dentro de palavra,ambos
pa.ra,para,pontuação espúria dentro de palavra,ambos
ma.is,mais,pontuação espúria dentro de palavra,ambos
n'ão,não,apóstrofo espúrio dentro de palavra,ambos
C:aixa,Caixa,pontuação espúria dentro de nome,ambos
```

Do not add `d'e`, `d'o`, `d'a`, `papel-moeda`, ordinals, decimal forms or monetary figures because they can be historically valid.

- [ ] **Step 2: Add allowlist safety tests**

```python
def test_lista_inicial_preserva_formas_historicas(tmp_path):
    regras = carrega_regras_lexicais(
        Path("pipeline/base/correcoes_lexicais_documentos_parlamentares.csv")
    )
    resultado = corrige_pagina(
        "q.ue ma.is d'e papel-moeda projecto",
        regras_lexicais=regras,
        hifens_lexicais=frozenset({"papel-moeda"}),
    )
    assert resultado.texto == "que mais d'e papel-moeda projecto"
```

- [ ] **Step 3: Measure every allowlisted raw form before generation**

Run a read-only counter over both raw JSONL files and assert the initial frequencies observed during planning: `q.ue=24`, `qu.e=24`, `q,ue=17`, `q:ue=12`, `par.a=21`, `pa.ra=11`, `ma.is=10`, `n'ão=10`, `C:aixa=17`. If any count differs, stop and inspect the input hashes before proceeding.

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_correcao_texto_parlamentar.py -v`

Expected: PASS.

- [ ] **Step 5: Commit the allowlist**

```bash
git add -- pipeline/base/correcoes_lexicais_documentos_parlamentares.csv tests/test_correcao_texto_parlamentar.py
git commit -m "data: registra correcoes lexicais conservadoras"
```

### Task 4: Geração integral e validação do corpus

**Files:**
- Create: `dados/texto_corrigido/fontes_parlamentares/caixa_conversao/caixa_conversao_v1_texto_leitura.txt`
- Create: `dados/texto_corrigido/fontes_parlamentares/caixa_conversao/caixa_conversao_v2_texto_leitura.txt`
- Create: `dados/texto_corrigido/fontes_parlamentares/caixa_conversao/caixa_conversao_v1_paginas_corrigidas.jsonl`
- Create: `dados/texto_corrigido/fontes_parlamentares/caixa_conversao/caixa_conversao_v2_paginas_corrigidas.jsonl`
- Create: `dados/texto_corrigido/fontes_parlamentares/caixa_conversao/manifesto_correcao_paginas.csv`
- Create: `dados/texto_corrigido/fontes_parlamentares/caixa_conversao/correcoes_lexicais_permitidas.csv`
- Create: `dados/texto_corrigido/fontes_parlamentares/caixa_conversao/relatorio_qualidade_correcao.json`

**Interfaces:**
- Consumes: generator, allowlist and raw JSONL from Tasks 1 to 3.
- Produces: the complete corrected corpus and an auditable quality report.

- [ ] **Step 1: Record raw input hashes before generation**

Run: `Get-FileHash -Algorithm SHA256 dados/texto_embutido/fontes_parlamentares/caixa_conversao/*`

Save the six raw input hashes in the generated quality report under `raw_inputs`.

- [ ] **Step 2: Generate the complete corrected corpus**

Run the non-verification CLI from Task 2 with the canonical input, output and allowlist paths.

Expected: 1,152 output records, 698 for volume 1 and 454 for volume 2, with zero `error` statuses.

- [ ] **Step 3: Run deterministic replay**

Run the verification CLI from Task 2.

Expected: exit 0 and zero divergences.

- [ ] **Step 4: Verify raw inputs were not modified**

Run the same `Get-FileHash` command as Step 1 and compare every hash with `raw_inputs` in the report.

Expected: six exact matches.

- [ ] **Step 5: Verify page coverage and output integrity**

Run a Python audit that asserts:

```python
assert total_records == 1152
assert pages_by_volume == {1: 698, 2: 454}
assert duplicate_pages == []
assert missing_pages == []
assert error_pages == []
assert raw_hash_mismatches == []
assert corrected_hash_mismatches == []
assert marker_counts == {1: 698, 2: 454}
```

- [ ] **Step 6: Compare search behavior before and after correction**

Count case-insensitive matches for `Arthur Orlando`, `Caixa de Conversão`, `David Campista`, `papel-moeda`, `câmbio`, `projecto` and `emissão` in raw and corrected text. Record both counts in `relatorio_qualidade_correcao.json`. A lower count after correction is a blocking regression unless the report identifies the exact changed form and demonstrates equivalence.

- [ ] **Step 7: Review every Arthur Orlando page**

Inspect PDF pages 13, 351, 442, 525, 527 and 694 of volume 1 against their corrected records. Confirm page 13 contains two mentions and the remaining listed pages one each. Record one report row per page with `visual_review="pass"` or a concrete correction failure.

- [ ] **Step 8: Perform stratified visual review**

Render and inspect at least these pages: volume 1 pages 5, 20, 350, 442, 525 and 553; volume 2 pages 5, 20, 77 and 228. The set covers front matter, ordinary prose, parliamentary speech, a sparse page and a table. Record whether reflow, headings, tables, spelling and page boundaries remain correct.

- [ ] **Step 9: Run the full relevant suite**

Run: `uv run pytest tests/test_correcao_texto_parlamentar.py tests/test_gera_texto_corrigido.py tests/test_regra_nome.py -v`

Expected: PASS with zero failures.

- [ ] **Step 10: Keep generated data separate from implementation commits**

Do not stage the generated directory in the implementation commits. Report its size and Git status to Pedro so he can decide separately whether the derived corpus belongs in repository history.

### Task 5: Documentation and final gate

**Files:**
- Modify: `dados/README.md`
- Verify: `docs/superpowers/specs/2026-08-01-camada-texto-corrigido-documentos-parlamentares-design.md`

**Interfaces:**
- Consumes: verified outputs from Task 4.
- Produces: user-facing location, semantics, limitations and reproducible commands.

- [ ] **Step 1: Document the new data layer**

Add a `texto_corrigido/` entry to `dados/README.md` stating that it is a derived reading layer, preserves historical spelling, records page-level provenance and does not replace PDF verification for citation.

- [ ] **Step 2: Run documentation and repository checks**

Run:

```bash
git diff --check
rg -n "FIXME" dados/README.md pipeline/base/correcao_texto_parlamentar.py pipeline/base/gera_texto_corrigido.py tests/test_correcao_texto_parlamentar.py tests/test_gera_texto_corrigido.py
```

Expected: `git diff --check` exits 0 and `rg` returns no matches.

- [ ] **Step 3: Run the final verification command**

Run the full relevant pytest command from Task 4, then the replay CLI and the page-coverage audit. Read every output and require zero test failures, zero replay divergences and zero coverage errors.

- [ ] **Step 4: Commit documentation only after the final gate passes**

```bash
git add -- dados/README.md
git commit -m "docs: documenta camada de texto corrigido"
```

- [ ] **Step 5: Deliver the artifacts**

Report the corrected TXT, page JSONL, manifest, allowlist and quality report with absolute paths. State the counts of corrected, unchanged, empty and error pages, the number of transformations by type, the visual sample result and the fact that academic quotation still requires checking the PDF.
