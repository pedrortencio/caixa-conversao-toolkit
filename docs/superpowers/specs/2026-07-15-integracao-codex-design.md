# Design: integração do Codex no fluxo de trabalho via ponto de entrada único

**Data:** 15 de julho de 2026

**Status:** aprovado por Pedro (estrutura, rebalanceamento e gates decididos em 15/07/2026)

**Origem:** operacionaliza `docs/protocolo-colaboracao-claude-codex.md`. O desenho foi proposto pelo Claude, criticado pelo Codex em parecer independente (`colaboracao/pareceres/2026-07-15-consulta-estrutura-colaboracao.md`, produzido por `gpt-5.6-sol`, codex-cli 0.144.4) e decidido por Pedro. As cinco emendas do Codex foram incorporadas.

## Objetivo

Pedro opera um único chat (a sessão do Claude Code). As tarefas são despachadas por raia: Claude lidera código e arquitetura; Codex lidera auditoria metodológica e acadêmica, e pode atuar como implementador designado em tarefas específicas. O Codex é invocado headless (`codex exec`) a partir da sessão do Claude, com handoff por arquivos versionados. Objetivo econômico declarado: uso máximo e eficiente das duas assinaturas, priorizando o token OpenAI (mais subsidiado) onde o papel permitir.

## Decisões de Pedro (15/07/2026)

1. **Estrutura consolidada aprovada:** convenção leve (AGENTS.md + `colaboracao/` + bloco de despacho no CLAUDE.md) + skill `parecer-codex` + núcleo de logging de proveniência + dois níveis de independência.
2. **Rebalanceamento aprovado:** Codex pode ser implementador designado (análise estatística, simulações, checagens mecânicas, rascunhos acadêmicos), com a regra de papéis: quem implementa um artefato não audita esse mesmo artefato; Claude revisa a implementação computacional do Codex, Codex revisa o método do Claude, Pedro aprova o substantivo.
3. **Gate de aprovação:** no nível ordinário, Pedro dá um ok rápido sobre objetivo e custo; no nível crítico, Pedro revisa o manifesto completo (pergunta, escopo, arquivos, critérios de aceite).

## Dois níveis de independência

| Nível | Quando | Como |
|---|---|---|
| **Consulta de raia única** (ordinário) | Tarefas comuns de cada raia | Um modelo só, o dono da raia. Sem duplicação, por economia. Nomeada honestamente como consulta, não como parecer independente bilateral. |
| **Revisão independente** (crítico) | Estimando, corpus, codebook, instrumento de mensuração ou conclusão histórica em jogo | Claude e Codex produzem pareceres separados sobre a mesma evidência, sem ver a resposta do outro, mediante autorização explícita de Pedro. Modo C do protocolo. |

A economia é um gate de risco, não uma proibição de duplicação.

## Componentes

### 1. `AGENTS.md` (raiz do repo)

Arquivo de contexto que o Codex lê ao abrir o repo (equivalente ao CLAUDE.md do Claude). Contém: papel padrão (auditor metodológico), papéis possíveis por tarefa (auditor, parecerista independente, implementador designado), aponta os docs canônicos do projeto (protocolo, avaliação, plano do pipeline, codebook) e as regras invariantes: em papel de auditor não edita código de produção; nunca lê a opinião do Claude antes de formar a sua num parecer independente; guardrails do projeto (orçamento, travessões, modelos pinados). O papel efetivo de cada execução vem do manifesto, não do AGENTS.md.

### 2. `colaboracao/` (versionado)

```
colaboracao/
  manifestos/    # <task_id>.md
  pareceres/     # <task_id>[-claude|-codex].md
  logs/          # <task_id>.jsonl + metadados; entram no git (texto leve)
  templates/
    manifesto.md
    parecer.md
```

`task_id` tem o formato `YYYY-MM-DD-<slug>`. O sufixo `-claude`/`-codex` só aparece no nível crítico, quando há dois pareceres para a mesma tarefa. Se os logs crescerem além de texto leve, a decisão de gitignorá-los é revisitada.

**Template de manifesto** (campos obrigatórios): `task_id`, solicitante, papel solicitado, nível (ordinário ou crítico), objetivo, arquivos de contexto, critérios de aceite, orçamento/limites, **"evidência potencialmente relevante não fornecida"** (seção obrigatória, preenchida pelo redator do manifesto, para tornar omissões visíveis), formato esperado da saída.

**Template de parecer** (formato do protocolo): fatos observados; inferências; riscos; alternativas; recomendação; teste que poderia refutar a recomendação.

O manifesto carrega fatos, caminhos e critérios; nunca as conclusões do redator. A gravação do parecer é feita pelo processo invocador (`--output-last-message` + captura do JSONL), nunca pelo modelo, coerente com o sandbox read-only.

### 3. Bloco de despacho no `CLAUDE.md`

Resumo operacional para o Claude: tabela de raias (herdada do protocolo), regra propõe-aprova com os dois gates, comando canônico, e proibições: Claude não edita `parecer_codex*.md`; a síntese do Claude cita cada divergência com referência verificável ao parecer original e não o substitui; parecer bruto é apresentado a Pedro antes ou junto da síntese.

### 4. Skill `.claude/skills/parecer-codex`

Guia o Claude no fluxo completo: classificar o nível da tarefa, montar o manifesto pelo template, propor a Pedro (gate correspondente ao nível), invocar o comando canônico, registrar parecer e log, apresentar o parecer bruto e só então sintetizar. Autopoliciamento declarado como tal: a salvaguarda estrutural são os artefatos versionados e o gate de Pedro, não a skill.

### 5. Comando canônico com proveniência (núcleo do "B")

Invocação registrada, por execução:

- `codex exec` com prompt via arquivo de manifesto, encoding UTF-8 explícito (bug conhecido: pipe do PowerShell 5.1 corrompe acentos; a implementação define e testa a forma correta de passar o prompt);
- `--sandbox read-only` (pareceres) ou `workspace-write` (implementador designado, escopo aprovado);
- `--ephemeral`, nunca `resume`, para pareceres independentes;
- modelo fixado via `-m` e reasoning effort alto via config (a execução de 15/07 rodou com effort `none`, insuficiente para auditoria);
- `--json` capturado para `colaboracao/logs/` (o `--output-last-message` sozinho não é log integral);
- metadados gravados: commit do repo, hash do manifesto, modelo, versão da CLI, data e hora, código de saída.

Implementado como comando documentado na skill `parecer-codex`, sem script neste primeiro momento; um script fino de conveniência só entra se a repetição manual começar a gerar erro de registro. O despachante completo com validação de manifesto continua adiado até o volume justificar.

## Tolerância a limites de cota

A assinatura OpenAI tem limites de uso; token subsidiado não significa custo marginal fixo nem disponibilidade contínua. Se a cota esgotar, a execução falha visivelmente e a tarefa espera ou é reatribuída por Pedro; o fluxo nunca troca de modelo silenciosamente.

## Validação

1. **Teste do comando canônico:** uma execução curta verificando encoding correto dos acentos, effort configurado, captura de JSONL e metadados completos.
2. **Primeiro uso real:** a auditoria do piloto de 1906 (P0 da avaliação independente).
3. **Piloto cego (de carona no 1906):** proposto pelo Codex como teste refutador; metade dos manifestos redigidos por Claude, metade por Pedro, comparando a diversidade crítica das respostas e a fidelidade das sínteses. Não é pré-condição; roda de carona nas tarefas reais.

## Migração dos artefatos desta consulta

O manifesto e o parecer da consulta de 15/07 (hoje no scratchpad da sessão) entram no repo como primeiros registros: `colaboracao/manifestos/2026-07-15-consulta-estrutura-colaboracao.md` e `colaboracao/pareceres/2026-07-15-consulta-estrutura-colaboracao.md`, com os metadados de execução (modelo `gpt-5.6-sol`, codex-cli 0.144.4, sessão `019f6864-3a76-7b80-ab5f-e4ef9b1c2266`, sem JSONL pois a captura ainda não existia).

## Relação com o pipeline de anotadores

Esta camada de colaboração é distinta de `pipeline/anotadores/`. O Codex **nunca** é anotador de produção nem fornece rótulos (decisão de 14/07 mantida); o instrumento primário segue sendo a API Gemini, com `claude -p` como segundo anotador de robustez. A colaboração aqui é sobre desenvolvimento, auditoria e escrita, não sobre mensuração.

## Fora de escopo

- Script despachante completo com validação de manifesto (adiado).
- OpenRouter como terceiro anotador (extensão futura já registrada em `docs/decisoes.md`).
- Qualquer mudança no protocolo de mensuração, prompts ou codebook.
- O protocolo `docs/protocolo-colaboracao-claude-codex.md` ganha, na implementação, uma nota curta registrando a distinção formal entre consulta de raia única e revisão independente (emenda 5 do parecer), sem reescrita do documento.
