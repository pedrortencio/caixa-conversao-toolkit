# Contexto do Debate Metodológico de Mensuração Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar e tornar descobrível o contexto canônico que condiciona a Fase B à comparação explícita entre desenhos de mensuração.

**Architecture:** Um memorando autocontido em `docs/` registra o estado da pesquisa, as escolhas provisórias, as famílias metodológicas concorrentes, os critérios de comparação e o gate humano. `AGENTS.md` e `CLAUDE.md` funcionam apenas como pontos de entrada e não duplicam o conteúdo substantivo.

**Tech Stack:** Markdown, Git, `rg`, `git diff --check`

## Global Constraints

- Texto em português, autocontido e legível sem acesso à conversa original.
- A escala `-2/+2`, *stance detection*, LLM, DSL e agregação são candidatos, não decisões finais.
- Não alterar codebook, prompts, schema, código do pipeline ou o registro histórico de decisões.
- Não usar travessões no texto.
- Nenhuma classificação substantiva em lote antes da comparação metodológica e da aprovação de Pedro.

---

### Task 1: Criar o contexto canônico

**Files:**
- Create: `docs/contexto-debate-metodologico-mensuracao.md`
- Reference: `docs/superpowers/specs/2026-07-18-contexto-debate-metodologico-mensuracao-design.md`
- Reference: `docs/handoff-2026-07-16-base-corpus.md`

**Interfaces:**
- Consumes: estado da Fase A e requisitos da especificação aprovada.
- Produces: documento canônico que as sessões futuras devem consultar antes de decisões sobre a Fase B.

- [ ] **Step 1: Criar o memorando com as seções obrigatórias**

O arquivo deve conter, nesta ordem:

```markdown
# Contexto para o debate científico-metodológico sobre mensuração

## Finalidade e estatuto
## Estado da pesquisa em 18 de julho de 2026
## A decisão central ainda está aberta
## Quatro níveis que não devem ser confundidos
## Estatuto das escolhas atuais
## Por que a decisão antecede parte da Fase B
## Famílias de desenhos a comparar
## Critérios predefinidos de comparação
## Protocolo da próxima rodada
## Gate de decisão e responsabilidade
## Instrução para novas sessões
```

O conteúdo deve registrar literalmente as seguintes regras substantivas:

```markdown
O objetivo imediato não é escolher o método mais sofisticado em abstrato. É identificar qual representação e qual instrumento produzem medidas cientificamente defensáveis para as quantidades históricas que Pedro decidir investigar.

A escala ordinal de -2 a +2, a unidade edição-dia, o enquadramento como stance detection, o uso de LLM, o DSL e as regras de agregação são hipóteses de trabalho. Nenhuma delas deve ser tratada como irreversível apenas porque aparece no piloto ou na documentação anterior.

Se uma etapa de processamento selecionar, descartar, resumir ou estruturar informação segundo uma definição substantiva, ela integra o desenho de mensuração e precisa ser discutida antes da execução em escala.
```

O documento deve distinguir atividades reversíveis, como preservação de PDFs, hashes, OCR ou transcrição com proveniência, das atividades condicionadas, como triagem seletiva, descarte de contexto, schema classificatório, rótulos de produção e agregação final.

- [ ] **Step 2: Verificar completude e linguagem provisória**

Run:

```powershell
rg -n "Finalidade|Estado da pesquisa|decisão central|Quatro níveis|escolhas atuais|Fase B|Famílias|Critérios|Protocolo|Gate|Instrução" docs/contexto-debate-metodologico-mensuracao.md
rg -n -i "\\b(TBD|TODO)\\b|<preencher>" docs/contexto-debate-metodologico-mensuracao.md
```

Expected: a primeira busca encontra todas as seções; a segunda não produz saída.

- [ ] **Step 3: Verificar que o documento não decide antecipadamente o método**

Run:

```powershell
rg -n -i "método definitivo|escala definitiva|DSL obrigatório|LLM obrigatório|validade superior" docs/contexto-debate-metodologico-mensuracao.md
```

Expected: nenhuma ocorrência afirmativa. Ocorrências em negações devem ser reescritas para evitar ambiguidade.

- [ ] **Step 4: Verificar formatação**

Run:

```powershell
git diff --check -- docs/contexto-debate-metodologico-mensuracao.md
```

Expected: exit code 0, sem whitespace errors.

### Task 2: Tornar o contexto obrigatório nos pontos de entrada

**Files:**
- Modify: `AGENTS.md:23-28`
- Modify: `CLAUDE.md:5-30`
- Test: buscas textuais nos três arquivos documentais

**Interfaces:**
- Consumes: `docs/contexto-debate-metodologico-mensuracao.md` da Task 1.
- Produces: referência canônica para o Codex e alerta operacional para o Claude.

- [ ] **Step 1: Adicionar o documento aos canônicos do Codex**

Adicionar em `AGENTS.md`, sob `## Documentos canônicos`:

```markdown
- `docs/contexto-debate-metodologico-mensuracao.md` (decisão crítica anterior à Fase B; leitura obrigatória para tarefas sobre processamento textual, codebook, instrumento, classificação ou agregação)
```

- [ ] **Step 2: Adicionar o gate metodológico ao contexto do Claude**

Adicionar depois de `## Pergunta e estimando` e do parágrafo atual:

```markdown
### Decisão metodológica pendente antes da Fase B

A formulação acima descreve o desenho herdado do piloto, não uma escolha definitiva. Antes de implementar triagem substantiva, schema classificatório ou classificação em lote, ler `docs/contexto-debate-metodologico-mensuracao.md`. A escala `-2/+2`, o enquadramento como *stance detection*, o uso de LLM, o DSL e as regras de agregação permanecem candidatos sujeitos a revisão comparativa e aprovação de Pedro. Processamento que selecione, descarte ou estruture informação segundo o construto não deve ser tratado como neutro.
```

- [ ] **Step 3: Testar a descoberta pelos pontos de entrada**

Run:

```powershell
rg -n --fixed-strings "docs/contexto-debate-metodologico-mensuracao.md" AGENTS.md CLAUDE.md
rg -n --fixed-strings "não uma escolha definitiva" CLAUDE.md
```

Expected: um vínculo em `AGENTS.md`, um vínculo em `CLAUDE.md` e o alerta operacional em `CLAUDE.md`.

- [ ] **Step 4: Verificar o escopo do diff**

Run:

```powershell
git diff --name-only
git diff --check
```

Expected: apenas `AGENTS.md`, `CLAUDE.md` e `docs/contexto-debate-metodologico-mensuracao.md`; nenhuma falha de formatação.

- [ ] **Step 5: Fazer revisão de coerência**

Conferir que:

```text
1. o documento não declara um método vencedor;
2. o inventário e a preservação do corpus continuam válidos;
3. a fronteira entre processamento reversível e mensuração seletiva está explícita;
4. Pedro mantém a decisão substantiva final;
5. não há alteração de código, dados, prompts ou codebook.
```

- [ ] **Step 6: Commit**

```powershell
git add -- AGENTS.md CLAUDE.md docs/contexto-debate-metodologico-mensuracao.md docs/superpowers/plans/2026-07-18-contexto-debate-metodologico-mensuracao.md
git commit -m "docs: contextualiza debate metodologico de mensuracao"
```

Expected: commit criado com quatro arquivos e working tree limpo.
