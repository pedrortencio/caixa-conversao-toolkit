# Fase A: Censo e Download do Acervo 1906-1914 - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enumerar por varredura o censo completo de objetos digitais dos 4 jornais (1906-1914) no host estático da BN, baixar os PDFs inteiros e materializar inventário, páginas e avaliações iniciais na base v2, com registro positivo de cada número sondado (existente ou ausente).

**Architecture:** Um motor de varredura (`pipeline/scraper/censo.py`) itera números candidatos por (bib, ano) com transporte HTTP injetável, detecção de regime de numeração (anual vs contínuo) e regra de parada por 404s consecutivos. Um persistidor (`pipeline/base/carrega_censo.py`) grava cada resultado: sucesso vira `digital_objects` + `object_fetches` + `physical_pages` + avaliação `not_assessed` na mesma transação; ausência vira linha no manifesto CSV versionado (`dados/censo/`). O resume lê o manifesto e pula números já sondados.

**Tech Stack:** Python 3.12, `requests` (já dependência), `pypdf` (nova, contagem real de páginas, achado D.2 do parecer), SQLite via `pipeline/base/db.py`, `unittest`.

## Global Constraints

- Rate limit: pausa configurável entre requisições de rede, padrão 4.0 s de dia (decisão de Pedro em 18/07, prevalece sobre o "lotes grandes de madrugada" do CLAUDE.md); 404 também conta como requisição.
- Retry com backoff exponencial (4 tentativas) só para erros de rede, nunca para 404.
- Regra de parada por (bib, ano): parar quando `n > ultimo_sucesso + 90`; se nenhum sucesso, parar em `inicio + 200`. Cap absoluto de 600 números por (bib, ano).
- Detecção de regime por (bib, ano): sondar n=1..6; qualquer 200 => regime anual (início 1); todos 404 => contínuo (início = fim do ano anterior + 1).
- Âncoras 1906 (menor número conhecido do piloto): O Paiz 7819, Correio da Manhã 1646, Correio Paulistano 15290, Gazeta 58. Para bibs contínuos em 1906, o início é descoberto por caminhada descendente a partir da âncora até 90 404s consecutivos.
- Raiz local dos PDFs: `C:\dados-caixa\raw_pdf` (fora do OneDrive; backup via robocopy para o Google Drive `G:\My Drive\caixa-conversao\raw_pdf`). `storage_path` no banco é ABSOLUTO.
- Buracos reais existem (Gazeta 1907: números 100 e 200 ausentes, 320 existe; verificado em 18/07). Ausência é registrada positivamente no manifesto, nunca inferida.
- Protocolos: `inventory/censo_host_estatico/1.0.0` (parâmetros = só método: host, anos, regra de parada, âncoras; NUNCA raw_root ou pausa, que variam por execução) e reuso de `identification/initial_not_assessed/1.0.0`.
- `response_sha256` = SHA-256 do corpo HTTP real (idêntico ao `pdf_sha256`; achado E.1 satisfeito com honestidade).
- Manifesto: `dados/censo/varredura_{bib}_{ano}.csv`, versionado em git, colunas `numero,status,http_status,pdf_sha256,byte_count,page_count,quando`. `status` em {`ok`,`ausente`,`erro`,`pdf_invalido`}.
- Calendário civil 1906-01-01 a 1914-12-31 materializado em `calendar_days` para os 4 jornais.
- Nada de Selenium; só o host estático.

## File Map

- Create `pipeline/scraper/censo.py`: motor de varredura (regime, início contínuo, iteração com parada, download validado com hash em streaming).
- Create `tests/test_censo.py`: transporte falso; regime, caminhada descendente, parada, buracos, download.
- Create `pipeline/base/carrega_censo.py`: persistência na base v2 + manifesto CSV + resume + CLI.
- Create `tests/test_carrega_censo.py`: persistência com banco temporário e resultados sintéticos; resume por manifesto.
- Modify `pyproject.toml`: `pypdf>=4.0` em dependencies; grupo dev com `pytest` (achado E.6).
- Create dir `dados/censo/` (manifesto versionado).

---

### Task 1: Motor de varredura com transporte injetável

**Files:**
- Create: `pipeline/scraper/censo.py`
- Test: `tests/test_censo.py`

**Interfaces:**
- Consumes: `hemeroteca.url_pdf(bib, ano, numero)`, `hemeroteca.USER_AGENT`.
- Produces: `Resultado(numero, status, http_status, pdf_sha256, byte_count, caminho)`, `Transporte` (Protocol com `obtem(url, destino) -> Resultado parcial`), `TransporteHttp(pausa)`, `detecta_regime(transporte, bib, ano) -> str`, `inicio_continuo_1906(transporte, bib, ancora) -> int`, `varre_ano(transporte, bib, ano, inicio, ja_sondados, cap=600, parada=90, sem_sucesso=200) -> Iterator[Resultado]`.

- [ ] **Step 1: Testes falhos do motor** (transporte falso com dicionário `(ano, numero) -> bytes | None`; casos: regime anual detectado com 200 em n<=6; regime contínuo com 6 404s; caminhada descendente acha início; varredura atravessa buraco de 30 404s e para após 90; `ja_sondados` é pulado sem requisição; download grava arquivo com sha e valida `%PDF`).
- [ ] **Step 2: Rodar e ver falhar** (`uv run python -m unittest tests.test_censo -v`).
- [ ] **Step 3: Implementar `censo.py`** (sem rede nos testes; `TransporteHttp` usa `requests.Session` com UA, stream para `.part`, sha256 durante o stream, rename atômico, backoff 3s/6s/12s para `RequestException`, pausa após cada requisição de rede).
- [ ] **Step 4: Rodar e ver passar; suíte completa.**
- [ ] **Step 5: Commit** `feat: motor de varredura do censo com transporte injetável`.

### Task 2: Persistência, manifesto, resume e CLI

**Files:**
- Create: `pipeline/base/carrega_censo.py`
- Test: `tests/test_carrega_censo.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Consumes: `censo.varre_ano`, `censo.Resultado`, `base_db.upsert_*`, `base_db.mark_download_status`, `carrega_piloto.NEWSPAPERS` (fonte única de cadastro).
- Produces: `garante_protocolos(conn, commit) -> Protocolos`, `garante_calendario(conn, newspaper_ids) -> int`, `persiste_sucesso(conn, ...) -> None` (objeto + fetch ok com http_status=200 + páginas via pypdf + not_assessed, uma transação), `registra_manifesto(caminho_csv, resultado) -> None`, `numeros_sondados(caminho_csv) -> set[int]`, CLI `--raw-root --pausa --limite --bib --ano --ate-horario`.

- [ ] **Step 1: Testes falhos** (banco temporário; sucesso sintético com PDF mínimo de 2 páginas gerado por pypdf => objeto+fetch+2 páginas+2 not_assessed e contract checks passam; pdf ilegível => fetch `invalid_pdf`, sem páginas; manifesto acumula e `numeros_sondados` devolve o conjunto; segunda persistência do mesmo sucesso é idempotente).
- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar + `pypdf` no pyproject + grupo dev com pytest + `uv sync`.**
- [ ] **Step 4: Rodar e ver passar; suíte completa; compileall.**
- [ ] **Step 5: Commit** `feat: carga do censo na base v2 com manifesto auditável`.

### Task 3: Smoke real mínimo

- [ ] **Step 1:** `uv run python pipeline/base/carrega_censo.py --bib 178691 --ano 1907 --limite 3 --raw-root C:\dados-caixa\raw_pdf` (espera: 3 PDFs baixados a partir de 08125, 3 objetos no banco, manifesto com 3 linhas ok).
- [ ] **Step 2:** conferir no banco: objetos com fetch `ok`, `http_status=200`, páginas materializadas = contagem pypdf, avaliações `not_assessed`; conferir resume (rodar de novo com `--limite 3` => pula os 3, baixa os próximos 0 por já estar no limite... usar `--limite 6` e ver 3 pulados + 3 novos).
- [ ] **Step 3: Commit** `test: valida censo com amostra real do host` (manifesto entra no git).

### Task 4: Varredura completa e backup

- [ ] **Step 1:** disparo destacado (sobrevive ao fim da sessão): `Start-Process` do CLI sem filtros com log em `dados/censo/log_varredura.txt`; pausa 4.0 de dia.
- [ ] **Step 2:** monitoramento por comando de status (contagens do manifesto + tail do log).
- [ ] **Step 3:** backup incremental: `robocopy C:\dados-caixa\raw_pdf "G:\My Drive\caixa-conversao\raw_pdf" /E /XO` ao fim de cada dia de varredura.
- [ ] **Step 4:** ao concluir 1906-1914: relatório de cobertura do censo (contagens por bib/ano, buracos, cascata de estados de ausência) + commit dos manifestos + atualização do handoff.

## Verificação final (portão da Fase A)

1. Todos os (bib, ano) com varredura concluída (parada por regra, não por interrupção).
2. `object_fetches` ok == arquivos válidos em disco == linhas `ok` no manifesto.
3. `physical_pages` por objeto == `page_count` do pypdf; toda página com `not_assessed` vigente.
4. Regressão do gabarito 1906: os hits do piloto (79/94/146/110 edições) são subconjunto do censo de 1906.
5. `PRAGMA integrity_check` ok; contract checks do piloto continuam passando.
