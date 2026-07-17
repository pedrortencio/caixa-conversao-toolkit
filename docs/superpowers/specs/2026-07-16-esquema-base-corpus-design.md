# Esquema da base do corpus (caixa_conversao.db): design

Data: 2026-07-16. Status: design validado contra dados reais do piloto, aguardando olhos frescos (painel + parecer do Codex) antes do plano de implementacao.

## 1. Objetivo e principio

Estruturar a base de dados que torna o corpus da Hemeroteca (1906-1914) inteligivel por maquina: o que existe, o PDF de cada edicao, o texto transcrito e a proveniencia de cada etapa. A base e a **fonte da verdade operacional** do pipeline de extracao e processamento; cada etapa le e escreve o estado nela, e o resume e guiado por ela.

Principio de projeto: **a base do corpus e agnostica a medicao**. Baixar e transcrever e caro e unico; classificar e barato e refazivel. A base blinda o caro contra mudancas no barato. Por isso as tabelas de medicao (classificacao de postura, codigos humanos) ficam deliberadamente fora deste design; elas serao redesenhadas na rodada metodologica com o Codex e entrarao depois, referenciando este corpus sem altera-lo.

## 2. Consumidores do contrato

O esquema abaixo e um contrato. Seus consumidores a jusante:

1. As proprias etapas do pipeline (enumeracao, download, identificacao, transcricao), que leem status para o resume e escrevem resultados.
2. A camada de medicao futura (le `paginas.texto`, `edicoes.data`, `edicoes.fase`, `edicoes.is_hit`; materializa `artigos` e classificacoes).
3. A analise final (le agregados por jornal, fase, mes).
4. O passo de export (le transcricoes para gravar o arquivo versionado em git).

Mudanca de coluna, tipo, nulabilidade ou semantica e breaking por padrao e exige migracao versionada com nota.

## 3. Achados de validacao contra dados reais (2026-07-16)

O design foi corrigido apos medir o material real do piloto, nao a partir de premissas:

- **Edicao = 8 a 12 paginas fisicas** (PDF de 7 a 10 MB), medido em 67 PDFs de edicao reais. O piloto transcreveu cerca de 1 pagina por edicao (a front page). Transcrever a edicao inteira custa cerca de 10x o piloto; a extracao cirurgica por pagina relevante e justificada pelos dados.
- **A data esta na fonte.** 90 das 110 transcricoes do CorreioM tem a data legivel no masthead, ainda que o consolidado do piloto as tenha marcado como "data nao encontrada". Os "169 sem data" sao falha de parsing downstream, nao ausencia. Os formatos reais tem ruido de OCR que quebra parser ingenuo: "SABBA[D]O 13 DE JANEIRO DE 1906", "ANNU VI N. 1.701", "RIO DE JANEIRO ~ QUARTA-FEIRA". A data e o numero da edicao aparecem juntos no masthead.
- **A transcricao do piloto ja e segmentada** com marcadores: `PAGE_METADATA` (masthead), `HEADLINE`, `SECTION_HEADER`, `ARTICLE`, `COLUMN`. Uma pagina do O Paiz trazia 13 artigos marcados. O grao de artigo existe no formato do piloto; nao precisa ser inventado, e derivavel do texto marcado.
- **Ancora de proveniencia:** as contagens de transcricao do piloto batem exatamente com o gabarito de regressao 1906 (CorreioM 110, CorreioP 94, Gazeta 146, O Paiz 79).
- **Casos degenerados existem:** ha JSON de analise vazio (`[]`, do Estadao, fora de escopo). O contrato tolera vazios.

## 4. Grao de extracao

A extracao cirurgica opera na **pagina**: identificar e transcrever apenas as paginas relevantes (com conteudo da Caixa) de cada edicao-hit, nao as 8 a 12 paginas inteiras. A economia mora ai. A estrutura de artigo vem de brinde nos marcadores que a transcricao produz. Como para saber qual artigo de uma pagina e sobre a Caixa e preciso ler a pagina, o artigo isolado nao e unidade de extracao pratica; e derivavel. `artigos` fica como tabela da camada de medicao.

## 5. O contrato (esquema)

Banco SQLite em `dados/base/caixa_conversao.db`. `PRAGMA foreign_keys = ON`.

### 5.1 `edicoes`, uma linha por edicao (1 PDF de 8 a 12 paginas). Populacao = censo.

```sql
CREATE TABLE edicoes (
    id                   INTEGER PRIMARY KEY,
    bib                  TEXT    NOT NULL,   -- per178691, per090972, per103730, per089842
    jornal               TEXT    NOT NULL,   -- slug denormalizado (opaiz, correiop, gazeta, correiom)
    ano                  INTEGER NOT NULL,
    edicao               INTEGER NOT NULL,   -- o "N." do masthead, ordinal da folha
    data                 TEXT,               -- ISO-8601 (YYYY-MM-DD), resolvida do masthead; NULL se irresoluvel
    data_fonte           TEXT,               -- masthead | manual | vizinhanca
    data_confianca       TEXT,               -- alta | media | baixa
    fase                 INTEGER,            -- 1..4, derivada da data
    is_hit               INTEGER NOT NULL DEFAULT 0,  -- casou com a busca por Caixa de Conversao
    pdf_path             TEXT,               -- relativo a dados/raw_pdf; fora do git
    pdf_sha256           TEXT,
    n_paginas            INTEGER,            -- paginas fisicas do PDF
    status_download      TEXT NOT NULL DEFAULT 'pendente',      -- pendente | ok | ausente_404 | erro
    status_identificacao TEXT NOT NULL DEFAULT 'pendente',      -- pendente | ok | erro
    status_transcricao   TEXT NOT NULL DEFAULT 'pendente',      -- pendente | parcial | ok | erro
    criado_em            TEXT NOT NULL,
    atualizado_em        TEXT NOT NULL,
    UNIQUE (bib, ano, edicao),
    CHECK (data_fonte IS NULL OR data_fonte IN ('masthead','manual','vizinhanca')),
    CHECK (data_confianca IS NULL OR data_confianca IN ('alta','media','baixa')),
    CHECK (fase IS NULL OR fase BETWEEN 1 AND 4),
    CHECK (is_hit IN (0,1)),
    CHECK (status_download IN ('pendente','ok','ausente_404','erro')),
    CHECK (status_identificacao IN ('pendente','ok','erro')),
    CHECK (status_transcricao IN ('pendente','parcial','ok','erro'))
);
```

Auditoria de recall (hit enumerada sem PDF no host) fica visivel como `status_download = 'ausente_404'`.

### 5.2 `paginas`, uma linha por pagina materializada da edicao (unidade da extracao cirurgica).

Semantica de existencia da linha (para nao inflar a tabela com paginas vazias): so recebem linha em `paginas` a pagina do masthead (sempre transcrita, e a fonte da data) e as paginas identificadas como relevantes (`relevante=1`, a transcrever). Com `edicoes.status_identificacao='ok'`, a ausencia de linha para um numero de pagina significa "avaliada e nao relevante"; antes disso, significa "ainda nao avaliada". O `edicoes.n_paginas` guarda a contagem fisica total.

```sql
CREATE TABLE paginas (
    id                  INTEGER PRIMARY KEY,
    edicao_id           INTEGER NOT NULL REFERENCES edicoes(id) ON DELETE CASCADE,
    num_pagina          INTEGER NOT NULL,   -- 1..n_paginas
    tem_masthead        INTEGER NOT NULL DEFAULT 0,   -- 0/1: a front page traz os metadados
    relevante           INTEGER,            -- 0/1/NULL: identificada com conteudo da Caixa
    ident_metodo        TEXT,               -- busca | ocr_bn | agente | manual
    ident_modelo        TEXT,               -- proveniencia, se por modelo
    ident_versao        TEXT,
    texto               TEXT,               -- transcricao com marcadores (PAGE_METADATA, ARTICLE, ...); so paginas relevantes
    modelo_transcricao  TEXT,               -- ex. gemini-2.5-flash (pinado)
    versao_modelo       TEXT,               -- versao exata (guardrail CLAUDE.md)
    status              TEXT NOT NULL DEFAULT 'pendente',   -- pendente | ok | erro
    transcrito_em       TEXT,
    UNIQUE (edicao_id, num_pagina),
    CHECK (tem_masthead IN (0,1)),
    CHECK (relevante IS NULL OR relevante IN (0,1)),
    CHECK (status IN ('pendente','ok','erro'))
);
```

Regra de nulos: `texto` e preenchido na pagina do masthead (para a data) e nas paginas `relevante = 1` (cirurgico). `ident_metodo` fica sem `CHECK` de propria intencao: o metodo de identificacao ainda esta em aberto (secao 10) e sera fixado no plano de extracao.

### 5.3 `buscas`, proveniencia da enumeracao por termo.

```sql
CREATE TABLE buscas (
    id          INTEGER PRIMARY KEY,
    jornal      TEXT,
    bib         TEXT NOT NULL,
    termo       TEXT NOT NULL,
    ano         INTEGER NOT NULL,
    data_busca  TEXT NOT NULL,   -- ISO-8601, quando a passada rodou
    n_hits      INTEGER
);
```

Trilha para reproduzir `is_hit` e auditar recall. A ligacao hit para edicao e resolvida na importacao (marca `edicoes.is_hit`).

## 6. Resolucao de data

Passo de parsing sobre o `paginas.texto` da pagina com masthead: extrair a linha da cidade e data, normalizar ruido de OCR conhecido (por exemplo `DE`/`DE` com acento espurio, `~` por virgula, `U`/`N` trocados), mapear mes por extenso, gravar `edicoes.data` (ISO), `data_fonte='masthead'` e `data_confianca` conforme a limpeza do casamento. Fallback para os casos degradados: inferir da vizinhanca (edicoes adjacentes por numero) com `data_fonte='vizinhanca'` e confianca baixa, ou marcar para revisao manual. `fase` deriva da data. Isso ataca diretamente o P0 dos "169 sem data".

## 7. Fluxo do pipeline (a base guia o resume)

- **Enumeracao (F1a):** `INSERT edicoes` (censo) e `INSERT buscas`; marca `is_hit` nas que casaram.
- **Download (F1b):** por edicao com `status_download='pendente'`, baixa o PDF inteiro, grava `pdf_path`, `pdf_sha256`, `n_paginas`, `status_download`.
- **Identificacao:** nas edicoes `is_hit`, decide quais paginas sao relevantes, faz `UPSERT paginas(relevante, ident_*, tem_masthead)`, atualiza `status_identificacao`.
- **Transcricao (F3):** paginas `relevante=1 status='pendente'`, grava `texto`, `modelo_transcricao`, `versao_modelo`, `status`; faz o parse do masthead e preenche `edicoes.data/data_fonte/data_confianca/fase`; atualiza `edicoes.status_transcricao`.
- **Export:** grava as transcricoes em texto versionado (`dados/transcricoes/{jornal}/...`) para o backup em git.
- **Medicao (depois):** le `paginas.texto`, materializa `artigos` e classificacoes.

## 8. Tecnologia, versionamento e layout

- **Acesso:** `sqlite3` da stdlib, sem ORM. Modulo fino de acesso com funcoes tipadas.
- **Contrato imposto no banco:** `CHECK` nos enums, `NOT NULL`, `UNIQUE`, `FOREIGN KEY` com `PRAGMA foreign_keys=ON`. Escrita que viola o contrato falha na hora.
- **Versionamento:** migracoes numeradas em `pipeline/base/migrations/00N_*.sql`, aplicadas por um migrador que le `PRAGMA user_version`, roda as pendentes e incrementa a versao. Sem rename ou drop silencioso; mudanca breaking e migracao com nota.
- **Layout:**
  - `pipeline/base/`: `db.py` (conexao e acesso), `schema.sql` (contrato canonico), `migrations/`.
  - `dados/base/caixa_conversao.db`: banco vivo, gitignored como o `raw_pdf`, duravel via backup do OneDrive.
  - `dados/transcricoes/{jornal}/`: export de texto versionado (guardrail "transcricoes sempre entram no git"). O banco e a verdade operacional; o export e o arquivo duravel; se o banco se perder, reconstroi dos PDFs ou do export.

## 9. Portoes de verificacao (antes de "pronto")

- **Contract check:** schema, enums, FKs e taxa de nulos batem com o contrato declarado.
- **Real data:** carregar o piloto 1906 real neste esquema como teste com dado de producao; toda restricao declarada sobrevive ao contato. Isso ja entrega o substrato para a auditoria P0.
- **Idempotencia:** re-rodar uma etapa faz upsert por chave natural e produz o mesmo resultado; nada de `now()` ou aleatorio na chave.

## 10. Fronteira deferida e questoes em aberto

Fora deste design, para a rodada metodologica com o Codex:

- `artigos` (parse dos marcadores `ARTICLE` em unidades coerentes, podendo cruzar paginas), `classificacoes` (rotulos do modelo, com modelo e versao pinados e fase), `codigos_humanos`. Referenciam `edicoes(id)` ou `paginas(id)`.
- **Metodo de identificacao de pagina relevante** sem transcrever tudo (OCR da BN, passada de visao barata, ou o proprio hit): decisao de extracao a fechar no plano.
- **Enumeracao do censo** (listar todas as edicoes por jornal e ano, nao so as hits): mecanica de scraper a fechar.
- **Denominador da saliencia** (total de edicoes vs so as hits): decisao metodologica; o esquema ja suporta via `is_hit` sobre populacao de censo.
