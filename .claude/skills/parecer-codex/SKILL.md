---
name: parecer-codex
description: Use when Claude needs to consult, review with, or dispatch work to Codex, including methodological opinions, academic audits, cross-review, designated implementation, "parecer do Codex", or "pergunta pro GPT" requests.
---

# Despacho de tarefas ao Codex

Spec: `docs/superpowers/specs/2026-07-15-integracao-codex-design.md`. Protocolo: `docs/protocolo-colaboracao-claude-codex.md`.

## Princípio

Pedro aprova cada gasto. O wrapper preserva proveniência. Quem implementa um artefato não atua como auditor independente dele.

## Fluxo obrigatório

1. **Classificar o nível.** É crítico quando envolve estimando, corpus, codebook, instrumento de mensuração ou conclusão histórica. Os demais casos são ordinários.
2. **Montar o manifesto** com `colaboracao/templates/manifesto.md`, salvando em `colaboracao/manifestos/<task_id>.md`, onde `task_id` é `YYYY-MM-DD-<slug>`. Incluir fatos, caminhos e critérios, sem conclusões próprias. Preencher obrigatoriamente **Evidência potencialmente relevante não fornecida**.
3. **Obter o gate de Pedro.** No ordinário, apresentar objetivo e custo. No crítico, apresentar o manifesto completo. NUNCA invocar sem o ok.
4. **No nível crítico**, escrever o parecer do Claude ANTES em `colaboracao/pareceres/<task_id>-claude.md`, congelar seu hash em registro, montar pacote neutro em `%TEMP%` sem caminhos do repo e invocar com `-Workdir <pacote> -PacoteIsolado -SufixoParecer '-codex'`.
5. **Invocar somente pelo wrapper:** `powershell -File scripts\invoca-codex.ps1 -Manifesto colaboracao\manifestos\<task_id>.md`. Nunca usar `codex exec` direto nem `resume` para pareceres.
6. **Em falha ou cota esgotada**, informar Pedro e esperar. Nunca trocar modelo silenciosamente.
7. **Apresentar o parecer bruto** a Pedro antes ou junto da síntese.
8. **Sintetizar com rastreabilidade.** Citar divergências por referência verificável e não editar arquivos de parecer do Codex.
9. **Como implementador designado**, usar worktree fora do OneDrive, commit-base e arquivos autorizados no manifesto. Entregar diff e relatório para revisão do Claude. Nunca usar escrita na árvore principal.

## Verificação rápida

- Manifesto versionado e gate registrado.
- Wrapper usado com modelo e effort pinados.
- Parecer bruto e registro apresentados.
- No crítico, parecer do Claude congelado antes do despacho e pacote isolado.
- Nenhum implementador auditou o próprio artefato.
