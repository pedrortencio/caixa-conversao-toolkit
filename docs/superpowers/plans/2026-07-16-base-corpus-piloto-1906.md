# Base do Corpus e Carga Piloto 1906 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar o contrato SQLite v2 da base do corpus e importar, com proveniência e verificações reproduzíveis, os 67 PDFs canônicos de O Paiz disponíveis no piloto de 1906.

**Architecture:** O contrato canônico fica em SQL consolidado e em uma migração inicial autocontida. Um módulo `sqlite3` concentra conexão, migração e operações idempotentes da camada de aquisição. O carregador descobre somente as três fontes autorizadas, cria registros históricos append-only, atualiza apenas ponteiros vigentes e valida o banco em uma transação.

**Tech Stack:** Python 3.12, biblioteca padrão (`sqlite3`, `hashlib`, `json`, `pathlib`, `re`, `unittest`), SQLite e `uv`.

## Global Constraints

- Executar Python somente por `uv run python`.
- Não adicionar dependências ao `pyproject.toml`.
- Não alterar nem versionar arquivos sob `dados/raw_pdf/`.
- O banco operacional é `dados/base/caixa_conversao.db` e deve permanecer fora do Git.
- Usar somente `dados/piloto_1906/data_processed`, `dados/raw_pdf/piloto_1906/data_tests` e `dados/piloto_1906/analises_json` na carga.
- Preservar resultados históricos; somente tabelas `current_*` podem ser atualizadas.
- Tratar Estadão como fora do escopo analítico, sem falhar caso seus artefatos sejam descobertos.
- Não realizar chamadas de rede nem chamadas pagas.
- Não usar travessões em textos destinados a Pedro.

---

### Task 1: Contrato SQL consolidado e migração inicial

**Files:**
- Create: `pipeline/base/__init__.py`
- Create: `pipeline/base/schema.sql`
- Create: `pipeline/base/migrations/001_init.sql`
- Create: `tests/test_base_schema.py`

**Interfaces:**
- Consumes: contrato de 44 tabelas e quatro views em `docs/superpowers/specs/2026-07-16-esquema-base-corpus-design-v2.md`.
- Produces: schema executável em banco vazio e migração autocontida com `PRAGMA user_version = 1`.

- [ ] **Step 1: Escrever o teste falho do contrato SQL**

```python
class SchemaTests(unittest.TestCase):
    def test_schema_cria_as_44_tabelas_e_views(self):
        conn = sqlite3.connect(":memory:")
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        tables = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'"
            )
        }
        views = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='view'"
            )
        }
        self.assertEqual(44, len(tables))
        self.assertEqual(
            {"v_digital_object_inventory", "v_current_page_assessments",
             "v_current_edition_dates", "v_current_edition_phases"},
            views,
        )
        self.assertEqual("ok", conn.execute("PRAGMA integrity_check").fetchone()[0])
        self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())
```

- [ ] **Step 2: Executar o teste e confirmar a falha por ausência do schema**

Run: `uv run python -m unittest tests.test_base_schema -v`

Expected: FAIL porque `pipeline/base/schema.sql` ainda não existe.

- [ ] **Step 3: Criar o schema completo em ordem segura**

O arquivo deve começar com:

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE newspapers (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    bn_bib TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    active_from TEXT,
    active_to TEXT,
    created_at TEXT NOT NULL
);
```

Materializar as 44 tabelas da seção 4 e da seção 5 da v2, acrescentar todas as FKs diferidas apenas por ordem de criação, os `CHECK` declarados e índices para colunas de FK e filtros de cobertura. Criar as quatro views ao final. `population_memberships.edition_day_id` deve referenciar `edition_days(id)` no schema novo.

- [ ] **Step 4: Criar a migração inicial autocontida**

`001_init.sql` deve repetir integralmente o DDL consolidado, sem comentários que referenciem outro arquivo, e terminar com:

```sql
PRAGMA user_version = 1;
```

- [ ] **Step 5: Testar igualdade estrutural entre schema e migração**

Adicionar teste que cria dois bancos em memória, aplica `schema.sql` no primeiro, `001_init.sql` no segundo e compara `sqlite_master` após remover a própria linha de definição de `sqlite_sequence`.

- [ ] **Step 6: Executar os testes do schema**

Run: `uv run python -m unittest tests.test_base_schema -v`

Expected: PASS, 44 tabelas, quatro views, integridade `ok` e nenhuma violação de FK.

### Task 2: Conexão, migrador e acesso idempotente à aquisição

**Files:**
- Create: `pipeline/base/db.py`
- Create: `tests/test_base_db.py`

**Interfaces:**
- Consumes: `pipeline/base/migrations/NNN_*.sql` e caminhos `pathlib.Path`.
- Produces: `connect`, `migrate`, `upsert_newspaper`, `upsert_protocol`, `upsert_calendar_day`, `upsert_digital_object`, `get_digital_object`, `mark_download_status`, `get_current_fetch`, `upsert_population_definition` e `upsert_population_membership`.

- [ ] **Step 1: Escrever testes falhos para conexão e migração**

```python
def test_connect_ativa_foreign_keys_e_wal(self):
    conn = db.connect(self.db_path)
    self.assertEqual(1, conn.execute("PRAGMA foreign_keys").fetchone()[0])
    self.assertEqual("wal", conn.execute("PRAGMA journal_mode").fetchone()[0])

def test_migrate_aplica_001_uma_unica_vez(self):
    conn = db.connect(self.db_path)
    self.assertEqual(1, db.migrate(conn))
    self.assertEqual(1, conn.execute("PRAGMA user_version").fetchone()[0])
    self.assertEqual(1, db.migrate(conn))
```

- [ ] **Step 2: Executar e confirmar a falha por ausência de `db.py`**

Run: `uv run python -m unittest tests.test_base_db -v`

Expected: FAIL na importação de `pipeline.base.db`.

- [ ] **Step 3: Implementar conexão e migrador transacional**

```python
def connect(path: Path = DEFAULT_DATABASE) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def migrate(conn: sqlite3.Connection, migrations_dir: Path = MIGRATIONS_DIR) -> int:
    current = int(conn.execute("PRAGMA user_version").fetchone()[0])
    for path in sorted(migrations_dir.glob("[0-9][0-9][0-9]_*.sql")):
        version = int(path.name[:3])
        if version <= current:
            continue
        if version != current + 1:
            raise MigrationError(f"migração esperada {current + 1:03d}, encontrada {version:03d}")
        sql = path.read_text(encoding="utf-8")
        conn.executescript("BEGIN IMMEDIATE;\n" + sql + "\nCOMMIT;")
        current = int(conn.execute("PRAGMA user_version").fetchone()[0])
        if current != version:
            raise MigrationError(f"{path.name} não definiu user_version={version}")
    return current
```

No ramo de exceção, executar `ROLLBACK` apenas quando `conn.in_transaction` for verdadeiro e relançar a exceção original.

- [ ] **Step 4: Escrever testes falhos das chaves naturais e histórico de downloads**

Os testes devem inserir o mesmo jornal, protocolo, dia e objeto duas vezes e exigir IDs iguais. Duas chamadas a `mark_download_status` devem criar duas linhas em `object_fetches` e apontar `current_object_fetches` somente para a segunda.

- [ ] **Step 5: Implementar as funções de acesso tipadas**

Usar `INSERT ... ON CONFLICT(natural_key) DO UPDATE` somente para entidades de cadastro e ponteiros vigentes. `object_fetches` deve usar apenas `INSERT`. Protocolos com `executor_type='model'` devem depender dos `CHECK` do banco para exigir identidade exata do modelo.

- [ ] **Step 6: Executar testes de banco e schema**

Run: `uv run python -m unittest tests.test_base_schema tests.test_base_db -v`

Expected: PASS sem warnings.

### Task 3: Descoberta do piloto, parser de páginas e datas

**Files:**
- Create: `pipeline/base/carrega_piloto.py`
- Create: `tests/test_carrega_piloto.py`

**Interfaces:**
- Consumes: PDFs `per{bib}_{ano}_{numero}.pdf`, TXT com marcadores `PAGE`, `PAGE_METADATA` e `ARTICLE`, JSON legados opcionais.
- Produces: `parse_artifact_name`, `count_pdf_pages`, `parse_transcription`, `parse_observed_date` e `discover_artifacts`.

- [ ] **Step 1: Escrever testes falhos para nomes, páginas e masthead**

```python
def test_parse_artifact_name(self):
    self.assertEqual(
        ("178691", 1906, "00001"),
        loader.parse_artifact_name("per178691_1906_00001"),
    )

def test_parse_transcription_accepts_dois_formatos_de_page(self):
    text = (
        "--- PAGE 1 ---\n--- PAGE_METADATA START ---\n"
        "RIO DE JANEIRO, 13 DE JANEIRO DE 1906\n"
        "--- PAGE_METADATA END ---\n--- ARTICLE START ---\nA\n"
        "--- ARTICLE END ---\n--- PAGE per178691_1906_1.pdf-PAGE2 ---\nB"
    )
    pages = loader.parse_transcription(text)
    self.assertEqual([1, 2], sorted(pages))
    self.assertEqual(1, pages[1].article_count)

def test_parse_observed_date_preserva_literal(self):
    observed = loader.parse_observed_date(
        "RIO DE JANEIRO-SEGUNDA-FEIRA, 8 DE OUTUBRO DE 1906", 1
    )
    self.assertEqual("1906-10-08", observed.normalized)
    self.assertIn("8 DE OUTUBRO DE 1906", observed.literal)
    self.assertEqual(1, observed.page_number)
```

- [ ] **Step 2: Executar e confirmar a falha por ausência do carregador**

Run: `uv run python -m unittest tests.test_carrega_piloto -v`

Expected: FAIL na importação ou ausência das funções.

- [ ] **Step 3: Implementar parsing determinístico e tolerante ao legado**

Aceitar `--- PAGE 1 ---` e `--- PAGE arquivo.pdf-PAGE1 ---`, preservar o texto completo por página, extrair o bloco de masthead e contar artigos. Normalizar os meses portugueses após `unicodedata.normalize`, incluindo as formas com mojibake observadas no piloto. Recusar datas fora de 1906 nesta carga.

- [ ] **Step 4: Testar descoberta contra as fontes reais**

```python
def test_discover_artifacts_encontra_o_recorte_canonico(self):
    artifacts = loader.discover_artifacts(REPO_ROOT)
    self.assertEqual(67, len(artifacts))
    self.assertEqual({"178691"}, {item.bib for item in artifacts})
    self.assertTrue(all(item.txt_path is not None for item in artifacts))
```

- [ ] **Step 5: Implementar descoberta pela interseção PDF e TXT**

Cada artefato deve carregar caminho relativo, SHA-256 e bytes do PDF, número de páginas, TXT correspondente e JSONs legados associados quando identificáveis. A ausência de PDF exclui o TXT da materialização física e entra no relatório como fonte sem PDF canônico.

- [ ] **Step 6: Executar os testes do parser**

Run: `uv run python -m unittest tests.test_carrega_piloto -v`

Expected: PASS com 67 artefatos, todos de `per178691`.

### Task 4: Carga transacional, contratos e relatório de cobertura

**Files:**
- Modify: `pipeline/base/carrega_piloto.py`
- Modify: `tests/test_carrega_piloto.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: funções públicas de `pipeline.base.db` e artefatos da Task 3.
- Produces: `load(db_path, repo_root) -> CoverageReport`, `contract_checks(conn)` e CLI com `--db` e `--repo-root`.

- [ ] **Step 1: Escrever teste falho de carga mínima em diretório temporário**

O teste deve copiar um PDF real e seu TXT para a estrutura canônica temporária, executar `load`, exigir um objeto, todas as páginas físicas, avaliação vigente `not_assessed`, transcrição vigente para páginas existentes no TXT e data observada quando o masthead for resolvido.

- [ ] **Step 2: Executar e confirmar a falha por ausência de `load`**

Run: `uv run python -m unittest tests.test_carrega_piloto.PilotLoadTests -v`

Expected: FAIL porque a carga ainda não está implementada.

- [ ] **Step 3: Implementar a carga em uma transação**

Criar protocolos determinísticos para inventário, avaliação inicial, importação da transcrição legada, parsing de data e população disponível, além de um protocolo `external_service` para importar as análises JSON legadas sem fingir conhecer a versão exata do modelo. Para cada PDF, inserir objeto, obtenção, edição lógica, vínculo, páginas, avaliações iniciais e ponteiros. Para cada página do TXT, inserir transcrição histórica com hashes de entrada, texto, resposta bruta e export. Quando um JSON puder ser associado sem ambiguidade a uma página, inserir uma avaliação substantiva histórica e seu ponteiro; JSON vazio ou associação ambígua deve permanecer explicitamente reportado, não convertido em negativo. Para a data observada, inserir `date_records`, atualizar `current_edition_dates`, criar `calendar_days` e filiação elegível.

- [ ] **Step 4: Implementar contract checks explícitos**

Verificar `user_version=1`, 44 tabelas, `foreign_keys=1`, `integrity_check='ok'`, `foreign_key_check` vazio, igualdade entre `page_count` e páginas materializadas, existência de avaliação `screening` vigente para toda página, hashes com 64 caracteres, enums válidos e datas observadas com literal, página e região.

- [ ] **Step 5: Testar idempotência da carga**

Executar `load` duas vezes sobre o mesmo banco temporário. Cadastros e objetos não podem duplicar. Resultados históricos só podem ser reutilizados quando a identidade completa de protocolo, entrada e hash for idêntica; ponteiros vigentes devem permanecer consistentes.

- [ ] **Step 6: Ignorar o banco operacional**

Acrescentar a `.gitignore`:

```gitignore
# Banco operacional local, preservado pelo OneDrive
dados/base/*.db
```

- [ ] **Step 7: Executar toda a suíte**

Run: `uv run python -m unittest discover -s tests -v`

Expected: PASS sem acessar rede.

### Task 5: Portão de dado real e calibração do esquema

**Files:**
- Modify: `docs/handoff-2026-07-16-base-corpus.md`
- Create: `docs/relatorio-carga-piloto-1906.md`

**Interfaces:**
- Consumes: carregador validado e as três fontes canônicas no repositório principal.
- Produces: banco operacional local, relatório terminal reproduzível e registro versionado da cobertura e das tabelas sem dado real.

- [ ] **Step 1: Executar a carga completa em banco temporário**

Run: `uv run python pipeline/base/carrega_piloto.py --db dados/base/caixa_conversao_piloto_verificacao.db`

Expected: exit code 0, 67 objetos, nenhuma violação de contrato e relatório de datas observadas versus não resolvidas.

- [ ] **Step 2: Inspecionar o banco de verificação**

Run: `uv run python -m unittest discover -s tests -v`

Run: `uv run python -c "import sqlite3; c=sqlite3.connect('dados/base/caixa_conversao_piloto_verificacao.db'); print(c.execute('pragma integrity_check').fetchone()[0]); print(c.execute('pragma foreign_key_check').fetchall())"`

Expected: `ok` e `[]`.

- [ ] **Step 3: Executar a carga operacional**

Run: `uv run python pipeline/base/carrega_piloto.py --db dados/base/caixa_conversao.db`

Expected: o mesmo relatório de cobertura do banco temporário.

- [ ] **Step 4: Registrar calibração e limitações**

O relatório deve registrar os números efetivamente produzidos, a limitação de 67 PDFs somente de O Paiz, os 474 TXT sem PDF canônico no recorte e uma linha de justificativa para cada tabela sem dado real no piloto.

- [ ] **Step 5: Executar verificação final e revisar o diff**

Run: `uv run python -m unittest discover -s tests -v`

Run: `git diff --check`

Run: `git status --short`

Expected: testes sem falhas, `git diff --check` sem saída e nenhum PDF ou banco listado pelo Git.
