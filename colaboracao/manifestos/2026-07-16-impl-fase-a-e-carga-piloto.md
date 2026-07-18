# Manifesto: implementar a base (schema + acesso + migrador) e carregar o piloto 1906

- task_id: 2026-07-16-impl-fase-a-e-carga-piloto
- solicitante: Pedro (decisao final dele)
- papel_solicitado: implementador designado (produzir codigo; sua saida final e o codigo em blocos delimitados, voce nao edita arquivos no disco)
- nivel: critico (corpus); a revisao independente do codigo sera do Claude
- gate: autorizado por Pedro em 16/07/2026 para implementar com o orcamento do Codex
- orcamento: uma rodada; leia os arquivos listados
- ferramentas: sandbox read-only; voce NAO roda o codigo (o Claude roda); escreva codigo correto e testavel
- workdir: repo principal (branch main)

## Objetivo

A partir da v2 do spec que voce mesmo redigiu, produzir a implementacao inicial da base e um carregador que traz o piloto 1906 real para dentro do esquema e valida o contrato. Carregar o piloto real e o portao de dado de producao da disciplina de engenharia de dados: se o contrato declarado nao sobrevive ao contato com o piloto, o desenho precisa mudar.

## Entregar (todos os arquivos, cada um em um bloco delimitado, veja formato)

1. **pipeline/base/schema.sql**: o DDL completo e consolidado da v2 (todas as tabelas, CHECKs, FKs, indices), com `PRAGMA foreign_keys=ON`. Deve criar um banco vazio valido de uma so vez.
2. **pipeline/base/migrations/001_init.sql**: a migracao inicial que aplica o schema e seta `PRAGMA user_version = 1`.
3. **pipeline/base/db.py**: modulo de acesso com stdlib `sqlite3`. Conexao (com foreign_keys on), o migrador (le user_version, aplica migracoes pendentes de migrations/ em ordem, incrementa a versao), e funcoes de acesso tipadas ao menos para a camada de aquisicao (inventario de objeto digital, jornais/protocolos, calendario/populacao elegivel): inserir e consultar objetos, marcar status de download, upsert idempotente por chave natural.
4. **pipeline/base/carrega_piloto.py**: script `uv run` que carrega o piloto 1906 REAL para dentro do esquema e roda os contract checks. Fontes reais no repo (leia para escrever o loader correto):
   - transcricoes por edicao: `dados/piloto_1906/data_processed/Caixa_de_Conversao_*_1906/per*_1906_*.txt` (marcadores PAGE_METADATA, ARTICLE, etc.);
   - PDFs de edicao: `dados/raw_pdf/piloto_1906/data_tests/per*_1906_*.pdf` (8 a 12 paginas cada);
   - analises: `dados/piloto_1906/analises_json/*.json` (algumas vazias, `[]`).
   O loader deve popular pelo menos: inventario de objeto digital (dos PDFs, com hash e n_paginas), edicoes logicas, paginas com avaliacao, e as transcricoes versionadas (a partir dos txt). Extrair a data do masthead (PAGE_METADATA) como `data_literal` + normalizada + status observada. Ao fim, rodar contract checks: schema aplicado, FKs intactas, enums validos, e imprimir um relatorio de cobertura (quantas edicoes, paginas, datas resolvidas vs nao).

## Calibracao das 44 tabelas (importante)

Ao escrever o loader, para CADA tabela do schema que voce NAO conseguir popular a partir dos dados reais disponiveis do piloto, registre-a numa lista de "tabelas sem dado real no piloto" no final da sua resposta (fora dos blocos de arquivo), com uma linha dizendo por que. Isso e sinal de calibracao: tabela que ninguem popula pode estar super-normalizada ou pode ser legitimamente futura. Nao remova tabelas; so sinalize.

## Arquivos de contexto (leia, relativos ao workdir)

1. docs/superpowers/specs/2026-07-16-esquema-base-corpus-design-v2.md (a v2 que voce redigiu; a fonte do schema)
2. CLAUDE.md (guardrails: uv, `google-genai`, modelos pinados, nunca travessoes em texto para o Pedro, dados/raw_pdf fora do git)
3. pipeline/scraper/download.py (o downloader existente, para o db.py de aquisicao ser compativel)

## Evidencia potencialmente relevante nao fornecida

- O piloto tem tambem pastas jsonX_1906 e Tests que nao listei; use apenas data_processed, raw_pdf/data_tests e analises_json, que sao as canonicas.
- Estadao esta fora de escopo; se aparecer no piloto, carregue mas marque como fora de escopo, nao deixe quebrar o loader.

## Criterios de aceite

Codigo Python 3.12 que roda com `uv run`, sem dependencias novas alem do que ja existe (stdlib sqlite3; pypdf so se necessario para contar paginas, e ja foi usado no projeto). O schema cria banco valido; o loader popula o piloto e os contract checks passam ou apontam com precisao onde o contrato nao bate. Sem placeholders.

## Formato esperado da saida

Cada arquivo entre delimitadores EXATOS, para eu separar por script sem ambiguidade:

===ARQUIVO: pipeline/base/schema.sql===
<conteudo integral>
===FIM===

===ARQUIVO: pipeline/base/migrations/001_init.sql===
<conteudo>
===FIM===

(e assim por diante para db.py e carrega_piloto.py)

Depois dos blocos, fora deles, a lista de "tabelas sem dado real no piloto" e qualquer aviso. Portugues, sem travessoes.
