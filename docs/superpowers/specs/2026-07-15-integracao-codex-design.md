# Design: integração do Codex no fluxo de trabalho via ponto de entrada único

**Data:** 15 de julho de 2026

**Status:** design aprovado, implementação pendente. Segunda rodada de revisão (encaminhada por Pedro em 15/07) incorporada: cinco emendas estruturais aceitas após verificação técnica.

**Origem:** operacionaliza `docs/protocolo-colaboracao-claude-codex.md`. O desenho foi proposto pelo Claude, criticado pelo Codex em parecer independente (produzido por `gpt-5.6-sol`, codex-cli 0.144.4, sessão `019f6864-3a76-7b80-ab5f-e4ef9b1c2266`; hoje no scratchpad da sessão, destino planejado em `colaboracao/pareceres/`), emendado em segunda revisão e decidido por Pedro.

## Objetivo

Pedro opera um único chat (a sessão do Claude Code). As tarefas são despachadas por raia: Claude lidera código e arquitetura; Codex lidera auditoria metodológica e acadêmica, e pode atuar como implementador designado em tarefas específicas. O Codex é invocado headless (`codex exec`) a partir da sessão do Claude, com handoff por arquivos versionados. Objetivo econômico declarado: uso máximo e eficiente das duas assinaturas, priorizando o token OpenAI (mais subsidiado) onde o papel permitir.

"Frentes paralelas" neste documento significa organização do trabalho (por exemplo, auditoria do 1906 e F1 avançando na mesma semana), nunca dois agentes escrevendo simultaneamente no mesmo working tree.

## Decisões de Pedro (15/07/2026)

1. **Estrutura consolidada aprovada:** convenção leve (AGENTS.md + `colaboracao/` + bloco de despacho no CLAUDE.md) + skill `parecer-codex` + wrapper fino de proveniência + dois níveis de independência com isolamento estrutural.
2. **Rebalanceamento aprovado:** Codex pode ser implementador designado (análise estatística, simulações, checagens mecânicas, rascunhos acadêmicos), com a regra de papéis: quem implementa um artefato não audita esse mesmo artefato; Claude revisa a implementação computacional do Codex, Codex revisa o método do Claude, Pedro aprova o substantivo.
3. **Gate de aprovação:** no nível ordinário, Pedro dá um ok rápido sobre objetivo e custo; no nível crítico, Pedro revisa o manifesto completo (pergunta, escopo, arquivos, critérios de aceite).

## Dois níveis de independência

| Nível | Quando | Como |
|---|---|---|
| **Consulta de raia única** (ordinário) | Tarefas comuns de cada raia | Um modelo só, o dono da raia. Sem duplicação, por economia. Nomeada honestamente como consulta, não como parecer independente bilateral. |
| **Revisão independente** (crítico) | Estimando, corpus, codebook, instrumento de mensuração ou conclusão histórica em jogo | Pareceres separados com isolamento estrutural (fluxo abaixo), mediante autorização explícita de Pedro. Modo C do protocolo. |

A economia é um gate de risco, não uma proibição de duplicação.

### Fluxo de revisão independente (isolamento estrutural, não autopoliciamento)

1. Claude grava seu parecer primeiro; o arquivo é congelado e seu hash registrado em `colaboracao/registros/`.
2. Monta-se um **pacote isolado**: diretório temporário neutro contendo apenas manifesto, evidências comuns e instruções neutras. Sem caminho do repositório, sem parecer do Claude, sem arquivos de síntese.
3. O Codex roda com `codex exec -C <pacote-isolado> --skip-git-repo-check --sandbox read-only`.
4. Só depois dos dois pareceres congelados (com hashes registrados) começa a síntese.
5. Revisões críticas exigem snapshot commitado do repo; se houver mudanças não commitadas, o manifesto registra explicitamente que a análise usa estado sujo, com hash do diff.

Ressalva validada em 15/07/2026 (registro `2026-07-15-teste-isolamento--20260715T233827696-9a0d57fc`): em uma sondagem segura com dados sintéticos, o sandbox read-only permitiu ler um arquivo-canário e listar seu diretório por caminhos absolutos fora do workdir. A tentativa inicial com caminhos privados foi bloqueada antes da execução pela camada de segurança. Consequência: o pacote isolado reduz descoberta acidental, mas não é barreira absoluta; o manifesto nunca deve revelar caminhos do repo nem de dados privados.

## Componentes

### 1. `AGENTS.md` (raiz do repo)

Arquivo de contexto que o Codex lê ao abrir o repo (equivalente ao CLAUDE.md do Claude). Contém: papel padrão (auditor metodológico), papéis possíveis por tarefa (auditor, parecerista independente, implementador designado), aponta os docs canônicos do projeto (protocolo, avaliação, plano do pipeline, codebook) e as regras invariantes: em papel de auditor não edita código de produção; guardrails do projeto (orçamento, travessões, modelos pinados). O papel efetivo de cada execução vem do manifesto, não do AGENTS.md. Em revisão independente o AGENTS.md nem é lido, pois o Codex roda no pacote isolado.

### 2. `colaboracao/` (versionado, exceto logs brutos)

```
colaboracao/
  manifestos/    # <task_id>.md
  pareceres/     # <task_id>[-claude|-codex].md
  registros/     # <task_id>--<run_id>.json (metadados compactos, versionados)
  logs/raw/      # <task_id>--<run_id>.jsonl (JSONL bruto, GITIGNORED)
  templates/
    manifesto.md
    parecer.md
```

- `task_id`: identidade da pergunta, formato `YYYY-MM-DD-<slug>`. O sufixo `-claude`/`-codex` nos pareceres só aparece no nível crítico.
- `run_id`: identidade da execução, formato `YYYYMMDDTHHMMSSfff-<hash-curto>` (milissegundos), com campo `attempt`; uma colisão residual recebe ainda o sufixo `-<attempt>`. Uma tarefa repetida (falha, effort diferente, manifesto revisado) gera novo registro, nunca sobrescreve.
- **Registro** (versionado) contém: task_id, run_id, attempt, modelo solicitado e modelo efetivamente reportado, versão da CLI, hash do manifesto, commit do repo, `git status --porcelain`, hash do diff se o working tree estiver sujo, hora inicial e final, exit code, comando sanitizado, token usage quando disponível, hashes do parecer e do JSONL bruto.
- **Log bruto** (gitignored) pode conter prompts, trechos de fontes, caminhos locais e saídas de ferramentas; só é versionado mediante aprovação explícita de Pedro, após sanitização.

**Template de manifesto** (campos obrigatórios): `task_id`, solicitante, papel solicitado, nível (ordinário ou crítico), objetivo, arquivos de contexto, critérios de aceite, orçamento/limites, **"evidência potencialmente relevante não fornecida"** (seção obrigatória, preenchida pelo redator do manifesto, para tornar omissões visíveis), formato esperado da saída.

**Template de parecer** (formato do protocolo): fatos observados; inferências; riscos; alternativas; recomendação; teste que poderia refutar a recomendação.

O manifesto carrega fatos, caminhos e critérios; nunca as conclusões do redator. A gravação do parecer é feita pelo processo invocador, nunca pelo modelo, coerente com o sandbox read-only.

### 3. Bloco de despacho no `CLAUDE.md`

Resumo operacional para o Claude: tabela de raias (herdada do protocolo), regra propõe-aprova com os dois gates, invocação sempre via wrapper, e proibições: Claude não edita `*-codex.md` em `pareceres/`; a síntese do Claude cita cada divergência com referência verificável ao parecer original e não o substitui; parecer bruto é apresentado a Pedro antes ou junto da síntese.

### 4. Skill `.claude/skills/parecer-codex`

Guia o Claude no fluxo completo: classificar o nível da tarefa, montar o manifesto pelo template, propor a Pedro (gate correspondente ao nível), invocar o wrapper, registrar parecer e registro, apresentar o parecer bruto e só então sintetizar. Autopoliciamento declarado como tal: as salvaguardas estruturais são o pacote isolado, o wrapper, os artefatos versionados e o gate de Pedro; a skill apenas garante que o Claude siga o caminho.

### 5. Wrapper `scripts/invoca-codex.ps1` (núcleo mínimo de proveniência, entra na v1)

Decisão revista na segunda revisão: a chamada canônica já envolve encoding, effort, captura de JSONL, hashes, metadados, exit code e arquivos parciais; repetir isso manualmente é a opção arriscada (o primeiro teste real já produziu encoding corrompido e effort `none`). O wrapper:

- lê o manifesto em UTF-8 (contornando a corrupção de acentos do pipe do PowerShell 5.1);
- cria `run_id` e grava saídas primeiro como `.part`, renomeando atomicamente após sucesso;
- executa `codex exec` com `--ignore-user-config` (imuniza o instrumento contra mudanças futuras no `~/.codex/config.toml`; a autenticação continua via `CODEX_HOME`) e configura explicitamente modelo, reasoning effort (alto para pareceres), sandbox, cor e `--output-last-message`;
- usa `--ephemeral` e nunca `resume` em pareceres;
- captura o stdout JSONL sem conversão indevida de encoding;
- verifica exit code e existência do parecer; produz registro de falha quando a execução não completa;
- calcula hashes e grava o registro em `colaboracao/registros/`;
- em caso de esgotamento de cota, falha visivelmente; o fluxo nunca troca de modelo silenciosamente.

O despachante completo com validação de manifesto continua adiado até o volume justificar.

### 6. Worktree isolado para implementador designado

`workspace-write` nunca roda na árvore principal (que pode ter alterações pendentes de Pedro). Quando o Codex for implementador designado:

- cria-se worktree específico da tarefa, **fora da árvore sincronizada pelo OneDrive** (o repo vive no OneDrive; worktree dentro dela sofreria conflito de sincronização nos metadados do git);
- o commit-base é registrado no manifesto, junto com a lista de arquivos autorizados;
- testes rodam dentro do worktree;
- a entrega é diff + relatório; Claude revisa antes de integrar;
- implementação nunca roda sobre working tree sujo.

## Validação

1. **Teste do wrapper:** execução curta verificando encoding correto dos acentos, effort configurado, captura de JSONL, registro completo com run_id e renomeação atômica.
2. **Teste do isolamento:** a partir de um pacote isolado, verificar se o sandbox read-only alcança arquivos fora do workdir por caminho absoluto; registrar o resultado no spec ou no registro da execução.
3. **Primeiro uso real:** a auditoria do piloto de 1906 (P0 da avaliação independente).
4. **Piloto cego (de carona no 1906):** metade dos manifestos redigidos por Claude, metade por Pedro; Codex responde sem conhecer a origem. Métricas pré-definidas: **diversidade crítica** = número de riscos distintos apontados e de alternativas não presentes no manifesto; **fidelidade da síntese** = recall das divergências (toda divergência do parecer bruto aparece na síntese, com referência verificável). Não é pré-condição; roda de carona nas tarefas reais.

## Migração dos artefatos desta consulta

O manifesto e o parecer da consulta de 15/07 (hoje no scratchpad da sessão) entram no repo na implementação, como primeiros registros: `colaboracao/manifestos/2026-07-15-consulta-estrutura-colaboracao.md` e `colaboracao/pareceres/2026-07-15-consulta-estrutura-colaboracao.md`, com registro retroativo dos metadados conhecidos (modelo `gpt-5.6-sol`, codex-cli 0.144.4, sessão `019f6864-3a76-7b80-ab5f-e4ef9b1c2266`, sem JSONL pois a captura ainda não existia).

## Relação com o pipeline de anotadores

Esta camada de colaboração é distinta de `pipeline/anotadores/`. O Codex **nunca** é anotador de produção nem fornece rótulos (decisão de 14/07 mantida); o instrumento primário segue sendo a API Gemini, com `claude -p` como segundo anotador de robustez. A colaboração aqui é sobre desenvolvimento, auditoria e escrita, não sobre mensuração.

## Fora de escopo

- Despachante completo com validação de manifesto (adiado).
- OpenRouter como terceiro anotador (extensão futura já registrada em `docs/decisoes.md`).
- Qualquer mudança no protocolo de mensuração, prompts ou codebook.
- O protocolo `docs/protocolo-colaboracao-claude-codex.md` ganha, na implementação, uma nota curta registrando a distinção formal entre consulta de raia única e revisão independente, sem reescrita do documento.
