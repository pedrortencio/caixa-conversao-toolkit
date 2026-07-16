# Integração Codex (ponto de entrada único) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Materializar a estrutura de colaboração Claude-Codex aprovada em `docs/superpowers/specs/2026-07-15-integracao-codex-design.md`: convenções versionadas, wrapper de proveniência e testes de validação.

**Architecture:** Convenção por arquivos versionados (`colaboracao/`, `AGENTS.md`, bloco no `CLAUDE.md`, skill `parecer-codex`) em torno de um único ponto de execução, o wrapper `scripts/invoca-codex.ps1`, que chama `codex exec` headless com encoding correto, flags pinadas e registro de proveniência por execução (`run_id`). Sem serviços, sem Python novo.

**Tech Stack:** Windows PowerShell 5.1, codex-cli 0.144.4 (npm), git. Nenhuma dependência nova no `pyproject.toml`.

## Global Constraints

- Nunca usar travessões (em-dashes) em nenhum texto produzido; usar vírgulas ou parênteses.
- Todos os arquivos novos gravados em UTF-8 (`Out-File -Encoding utf8` quando via PowerShell).
- `colaboracao/logs/raw/` e `*.part` nunca entram no git.
- Commits usam a identidade já configurada por Pedro e mensagens em minúsculas no estilo `docs:`/`feat:`/`chore:`. Não atribuir ao Claude trabalho executado pelo Codex. Commits de implementação desta sessão terminam com `Co-Authored-By: Codex <noreply@openai.com>`; o commit de housekeeping, que apenas preserva conteúdo preexistente de Pedro, não recebe coautoria automatizada.
- Modelo pinado do Codex nesta v1: `gpt-5.6-sol`. Effort de parecer: `high`.
- As Tasks 5 e 6 gastam uma chamada pequena de Codex cada; avisar Pedro no momento da execução (gate de custo do nível ordinário).
- Fora a Task 1, nenhum outro commit pode arrastar arquivos que não pertencem à própria task (`git add` sempre com caminhos explícitos).
- O repo vive dentro do OneDrive; não criar worktrees nem arquivos temporários de teste dentro da árvore sincronizada quando evitável (usar `%TEMP%`).

---

### Task 1: Housekeeping da sobra de 14/07

O working tree tem duas pendências de Pedro que bloqueiam commits limpos de `CLAUDE.md` nas tasks seguintes.

**Files:**
- Modify: `CLAUDE.md` (já modificado no working tree; apenas commitar)
- Create (já existe, untracked): `docs/fontes-de-estudo.md`

**Interfaces:**
- Consumes: nada
- Produces: working tree limpo, pré-condição das Tasks 7 e 8

- [x] **Step 1: Confirmar com Pedro** que a sobra é intencional (confirmado em 15/07/2026).

- [x] **Step 2: Commitar a sobra**

```powershell
Set-Location "C:\Users\pedro\OneDrive\Documentos\Acadêmico\Dissertação Mestrado\Dados\caixa-conversao-toolkit"
git add CLAUDE.md docs/fontes-de-estudo.md
git commit -m @'
docs: registra fontes de estudo continuo e referencia no claude.md

'@
```

Resultado: commit `c1826d6`, contendo somente `CLAUDE.md` e `docs/fontes-de-estudo.md`.

- [x] **Step 3: Verificar que as duas pendências saíram do working tree**

Run: `git status --porcelain`
Expected nesta sessão: somente o plano ainda não versionado aparece como untracked.

---

### Task 2: Estrutura `colaboracao/` + templates + .gitignore

**Files:**
- Create: `colaboracao/templates/manifesto.md`
- Create: `colaboracao/templates/parecer.md`
- Create: `colaboracao/manifestos/.gitkeep`, `colaboracao/pareceres/.gitkeep`, `colaboracao/registros/.gitkeep`, `colaboracao/logs/raw/.gitkeep`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: nada
- Produces: diretórios e templates usados pelo wrapper (Task 4), pela skill (Task 9) e pela migração (Task 7). Campos do manifesto: `task_id`, `solicitante`, `papel`, `nivel`, `objetivo`, `arquivos de contexto`, `criterios de aceite`, `orcamento/limites`, `evidencia potencialmente relevante nao fornecida`, `formato da saida`.

- [ ] **Step 1: Criar diretórios e .gitkeep**

```powershell
Set-Location "C:\Users\pedro\OneDrive\Documentos\Acadêmico\Dissertação Mestrado\Dados\caixa-conversao-toolkit"
foreach ($d in 'colaboracao\manifestos','colaboracao\pareceres','colaboracao\registros','colaboracao\logs\raw','colaboracao\templates') {
    New-Item -ItemType Directory -Force $d | Out-Null
    if ($d -ne 'colaboracao\templates') { New-Item -ItemType File "$d\.gitkeep" | Out-Null }
}
```

- [ ] **Step 2: Criar `colaboracao/templates/manifesto.md`** com este conteúdo exato:

```markdown
# Manifesto: <título curto da tarefa>

- task_id: YYYY-MM-DD-<slug>
- solicitante: Pedro
- papel_solicitado: <auditor | parecerista independente | implementador designado>
- nivel: <ordinario | critico>
- gate: <ordinário: ok rápido de Pedro sobre objetivo e custo | crítico: Pedro revisou pergunta, escopo, arquivos e critérios>
- orcamento: <ex.: uma única rodada; ler apenas os arquivos listados>
- ferramentas: <ex.: sandbox read-only; não editar nem criar arquivos>

## Objetivo

<uma pergunta ou entrega, sem as conclusões do redator>

## Arquivos de contexto

<lista de caminhos, relativos ao workdir da execução>

## Evidência potencialmente relevante não fornecida

<obrigatório: o que existe no projeto e NÃO foi incluído neste manifesto, e por quê. Torna omissões visíveis.>

## Critérios de aceite

<como saber que a resposta cumpriu o pedido>

## Formato esperado da saída

<para pareceres: fatos observados; inferências; riscos; alternativas; recomendação; teste que poderia refutar a recomendação. Em português.>
```

- [ ] **Step 3: Criar `colaboracao/templates/parecer.md`** com este conteúdo exato:

```markdown
# Parecer: <task_id>

<preenchido pelo modelo consultado; gravado pelo processo invocador, nunca pelo modelo>

## Fatos observados

## Inferências

## Riscos

## Alternativas

## Recomendação

## Teste que poderia refutar esta recomendação
```

- [ ] **Step 4: Adicionar ao `.gitignore`** (no fim do arquivo):

```
# colaboracao: logs brutos e arquivos parciais nunca entram no git
colaboracao/logs/raw/*
!colaboracao/logs/raw/.gitkeep
colaboracao/**/*.part
```

- [ ] **Step 5: Verificar que o gitignore funciona**

```powershell
New-Item -ItemType File 'colaboracao\logs\raw\teste.jsonl' | Out-Null
git status --porcelain colaboracao
Remove-Item 'colaboracao\logs\raw\teste.jsonl' -Confirm:$false
```

Expected: o `git status` lista os `.gitkeep` e templates como untracked, mas NÃO lista `teste.jsonl`.

- [ ] **Step 6: Commit**

```powershell
git add colaboracao .gitignore
git commit -m @'
feat: estrutura colaboracao/ com templates de manifesto e parecer

Co-Authored-By: Codex <noreply@openai.com>
'@
```

---

### Task 3: `AGENTS.md`

**Files:**
- Create: `AGENTS.md`

**Interfaces:**
- Consumes: nada
- Produces: contexto que o codex-cli lê automaticamente quando roda na raiz do repo (consultas ordinárias). Em revisão independente crítica NÃO é lido (pacote isolado).

- [ ] **Step 1: Criar `AGENTS.md`** com este conteúdo exato:

```markdown
# AGENTS.md — contexto para o Codex neste repositório

Pesquisa de mestrado de Pedro Ortencio (FFLCH-USP, História Econômica): posicionamento
editorial da imprensa sobre a Caixa de Conversão (1906-1914). Pipeline transforma jornais
da Hemeroteca da BN em série quantitativa via LLM.

## Seu papel

Papel padrão: **auditor metodológico e acadêmico** (revisão de estimando, seleção, validade,
mensuração, inferência e redação). Papéis possíveis, definidos POR TAREFA no manifesto que
você recebe: auditor, parecerista independente, implementador designado.

Regras invariantes:

- Em papel de auditor ou parecerista, você NÃO edita nem cria arquivos; sua resposta final
  em texto é o parecer, gravado pelo processo invocador.
- Como implementador designado, edite apenas os arquivos autorizados no manifesto, dentro
  do worktree da tarefa, e entregue diff + relatório.
- Você nunca fornece rótulos de produção para a base (a anotação é da API Gemini, com
  claude -p como segundo anotador; ver docs/plano-batch-anotadores.md).
- Divergência fundamentada vale mais que concordância; consenso entre modelos não é validade.

## Documentos canônicos

- `docs/protocolo-colaboracao-claude-codex.md` (papéis e modos de colaboração)
- `docs/avaliacao-independente-2026-07-15.md` (sua auditoria do projeto)
- `docs/plano-pipeline.md` (plano geral), `docs/decisoes.md` (decisões registradas)
- `docs/codebook-fases.md` (construto por fase), `CLAUDE.md` (contexto operacional do Claude)

## Guardrails do projeto

- Orçamento total ~R$830 em tokens de API; nenhum lote pago sem regressão de 1906 e medição de custo.
- Nunca usar travessões (em-dashes) em texto para Pedro; usar vírgulas.
- Modelos de mensuração são pinados e versionados; mudanças de prompt/codebook só com registro em docs/decisoes.md.
```

- [ ] **Step 2: Commit**

```powershell
git add AGENTS.md
git commit -m @'
feat: agents.md com papel e guardrails do codex no repo

Co-Authored-By: Codex <noreply@openai.com>
'@
```

---

### Task 4: Wrapper `scripts/invoca-codex.ps1` + teste offline de falha

**Files:**
- Create: `scripts/invoca-codex.ps1`
- Create: `tests/test-invoca-codex.ps1`

**Interfaces:**
- Consumes: templates e diretórios da Task 2.
- Produces: comando único de invocação. Assinatura: `invoca-codex.ps1 -Manifesto <path> [-TaskId <slug>] [-Modelo gpt-5.6-sol] [-Effort high] [-Workdir <dir>] [-PacoteIsolado] [-SufixoParecer '-codex']`. Saídas: `colaboracao/pareceres/<task_id><sufixo>.md`, `colaboracao/logs/raw/<task_id>--<run_id>.jsonl` (gitignored), `colaboracao/registros/<task_id>--<run_id>.json` (versionado). Exit code 0 apenas em sucesso.

**Emenda da revisão Codex, obrigatória:** o bloco de implementação abaixo é a base funcional, não uma autorização para escrever produção antes dos testes. Implementar em ciclos RED, GREEN e REFACTOR com `tests/test-invoca-codex.ps1`. O teste usa um shim local de `codex.cmd`, sem rede, e cobre separadamente: manifesto inexistente; sucesso com acentos; falha com registro e sem parecer final; duas execuções no mesmo segundo sem colisão; hash de estado sujo mudando quando muda conteúdo staged ou untracked; ausência de `.part`; rejeição de `TaskId`, modelo, effort e sufixo fora das allowlists. O wrapper recebe `-CodexCommand` para injeção do shim nos testes, com default `codex.cmd`.

Correções de implementação em relação ao bloco-base:

- `run_id` usa `yyyyMMddTHHmmssfff-<hash-curto>` e, se ainda houver colisão, acrescenta `-<attempt>`; atualizar o spec para documentar o formato.
- O snapshot sujo é determinístico e inclui `git diff --binary HEAD` (staged e unstaged) mais caminho e SHA-256 de cada arquivo untracked, em ordem ordinal. O `hash_diff` é o hash desse snapshot completo.
- Todos os argumentos enviados a `cmd.exe` são citados; `TaskId`, `Modelo`, `Effort` e `SufixoParecer` são validados antes da montagem da linha de comando. Nenhum valor não confiável entra cru em `cmd /c`.
- A versão é obtida do mesmo `-CodexCommand` usado na execução, evitando resolver outro shim.
- O antigo teste com modelo inválido pela API é removido. O caminho de falha completo é exercitado offline pelo shim, sem gasto de cota.

- [ ] **Step 0: Escrever `tests/test-invoca-codex.ps1` e executar cada caso contra o wrapper ausente, confirmando a falha esperada antes de implementar o comportamento correspondente.**

Run: `powershell -NoProfile -ExecutionPolicy Bypass -File tests\test-invoca-codex.ps1 -Case <nome>`
Expected em RED: exit code diferente de 0 e mensagem que identifica o comportamento ainda ausente.

- [ ] **Step 1: Verificar que o shim .cmd do codex existe** (o wrapper usa `cmd /c` para redirecionar bytes sem o re-encoding do PowerShell 5.1, e o `cmd` não executa `.ps1`):

Run: `where.exe codex`
Expected: a lista inclui `C:\Users\pedro\AppData\Roaming\npm\codex.cmd`. Se não incluir, PARAR e investigar o shim npm antes de continuar.

- [ ] **Step 2: Criar `scripts/invoca-codex.ps1`** com este conteúdo exato:

```powershell
#Requires -Version 5.1
<#
Invoca codex exec com proveniencia registrada (spec: docs/superpowers/specs/2026-07-15-integracao-codex-design.md).
Uso tipico (parecer ordinario, workdir = raiz do repo):
  powershell -File scripts\invoca-codex.ps1 -Manifesto colaboracao\manifestos\2026-07-20-exemplo.md
Revisao independente critica (pacote isolado):
  powershell -File scripts\invoca-codex.ps1 -Manifesto <pacote>\manifesto.md -Workdir <pacote> -PacoteIsolado -SufixoParecer '-codex'
#>
param(
    [Parameter(Mandatory = $true)][string]$Manifesto,
    [string]$TaskId,
    [string]$Modelo = 'gpt-5.6-sol',
    [string]$Effort = 'high',
    [string]$Workdir,
    [switch]$PacoteIsolado,
    [string]$SufixoParecer = ''
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ColabDir = Join-Path $RepoRoot 'colaboracao'
if (-not $Workdir) { $Workdir = $RepoRoot }

if (-not (Test-Path $Manifesto)) { throw "Manifesto nao encontrado: $Manifesto" }
$Manifesto = (Resolve-Path $Manifesto).Path
if (-not $TaskId) { $TaskId = [IO.Path]::GetFileNameWithoutExtension($Manifesto) }

function Get-HashArquivo([string]$Caminho) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        ([BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($Caminho))) -replace '-', '').ToLower()
    } finally { $sha.Dispose() }
}

$inicio = Get-Date
$hashManifesto = Get-HashArquivo $Manifesto
$runId = '{0}-{1}' -f $inicio.ToString('yyyyMMddTHHmmss'), $hashManifesto.Substring(0, 8)

$registrosDir = Join-Path $ColabDir 'registros'
$rawDir = Join-Path $ColabDir 'logs\raw'
$parecerDir = Join-Path $ColabDir 'pareceres'
$attempt = @(Get-ChildItem $registrosDir -Filter "$TaskId--*.json" -ErrorAction SilentlyContinue).Count + 1

$parecerFinal = Join-Path $parecerDir "$TaskId$SufixoParecer.md"
$rawFinal = Join-Path $rawDir "$TaskId--$runId.jsonl"
$errFinal = Join-Path $rawDir "$TaskId--$runId.err.txt"
$registroFinal = Join-Path $registrosDir "$TaskId--$runId.json"
$parecerPart = "$parecerFinal.part"
$rawPart = "$rawFinal.part"
$errPart = "$errFinal.part"

# proveniencia git (sempre do repo, mesmo com workdir isolado)
$commit = (git -C $RepoRoot rev-parse HEAD).Trim()
$porcelain = (git -C $RepoRoot status --porcelain) -join "`n"
$hashDiff = $null
if ($porcelain) {
    $diffTmp = Join-Path $env:TEMP "invoca-codex-diff-$runId.txt"
    git -C $RepoRoot diff | Out-File -Encoding utf8 $diffTmp
    $hashDiff = Get-HashArquivo $diffTmp
    Remove-Item $diffTmp -Confirm:$false
}
$versaoCli = (codex --version) -join ' '

$codexArgs = @(
    'exec', '-',
    '--ignore-user-config',
    '--ephemeral',
    '--sandbox', 'read-only',
    '-m', $Modelo,
    '-c', "model_reasoning_effort=$Effort",
    '--color', 'never',
    '--json',
    '-C', $Workdir,
    '--output-last-message', $parecerPart
)
if ($PacoteIsolado) { $codexArgs += '--skip-git-repo-check' }

$argLine = ($codexArgs | ForEach-Object { if ($_ -match '[\s"]') { '"' + $_ + '"' } else { $_ } }) -join ' '
# cmd /c redireciona stdin/stdout/stderr em bytes, sem o re-encoding do PowerShell 5.1
$cmdLine = "codex $argLine < `"$Manifesto`" > `"$rawPart`" 2> `"$errPart`""
cmd /c $cmdLine
$exitCode = $LASTEXITCODE
$fim = Get-Date

$sucesso = ($exitCode -eq 0) -and (Test-Path $parecerPart)

# best-effort: modelo reportado e token usage a partir do JSONL
$modeloReportado = $null
$tokenUsage = $null
if (Test-Path $rawPart) {
    foreach ($linha in [IO.File]::ReadLines($rawPart)) {
        try { $ev = $linha | ConvertFrom-Json } catch { continue }
        if ($ev.PSObject.Properties['model'] -and $ev.model) { $modeloReportado = $ev.model }
        if ($ev.PSObject.Properties['usage'] -and $ev.usage) { $tokenUsage = $ev.usage }
    }
}

if ($sucesso) {
    Move-Item $parecerPart $parecerFinal
} elseif (Test-Path $parecerPart) {
    Move-Item $parecerPart "$parecerFinal.falha"
}
if (Test-Path $rawPart) { Move-Item $rawPart $rawFinal }
if (Test-Path $errPart) {
    if ((Get-Item $errPart).Length -gt 0) { Move-Item $errPart $errFinal } else { Remove-Item $errPart -Confirm:$false }
}

$comandoSan = ("codex $argLine") -replace [regex]::Escape($RepoRoot), '<repo>' -replace [regex]::Escape($env:USERPROFILE), '~'
$registro = [ordered]@{
    task_id              = $TaskId
    run_id               = $runId
    attempt              = $attempt
    status               = $(if ($sucesso) { 'sucesso' } else { 'falha' })
    modelo_solicitado    = $Modelo
    modelo_reportado     = $modeloReportado
    effort_solicitado    = $Effort
    versao_cli           = $versaoCli
    hash_manifesto       = $hashManifesto
    commit_repo          = $commit
    git_status_porcelain = $porcelain
    hash_diff            = $hashDiff
    workdir_isolado      = [bool]$PacoteIsolado
    inicio               = $inicio.ToString('o')
    fim                  = $fim.ToString('o')
    exit_code            = $exitCode
    comando              = $comandoSan
    token_usage          = $tokenUsage
    hash_parecer         = $(if (Test-Path $parecerFinal) { Get-HashArquivo $parecerFinal } else { $null })
    hash_log             = $(if (Test-Path $rawFinal) { Get-HashArquivo $rawFinal } else { $null })
}
$registroPart = "$registroFinal.part"
$registro | ConvertTo-Json -Depth 6 | Out-File -Encoding utf8 $registroPart
Move-Item $registroPart $registroFinal

Write-Output "registro: $registroFinal"
if ($sucesso) {
    Write-Output "parecer: $parecerFinal"
} else {
    throw "execucao falhou (exit $exitCode); ver $errFinal e $registroFinal"
}
```

- [ ] **Step 3: Teste de falha 1, manifesto inexistente**

Run: `powershell -File scripts\invoca-codex.ps1 -Manifesto colaboracao\manifestos\nao-existe.md`
Expected: erro `Manifesto nao encontrado`, exit code diferente de 0, NENHUM arquivo novo em `colaboracao/`.

- [ ] **Step 4: Teste de falha 2, shim offline retorna exit code 23** (valida o caminho de falha completo sem rede nem gasto de cota)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tests\test-invoca-codex.ps1 -Case falha-codex
```

Expected: PASS. Internamente o wrapper recebe exit code 23; existe registro com `"status": "falha"`; existe log em `logs/raw/`; NÃO existe parecer final; nenhum `*.part` sobra.

- [ ] **Step 5: Limpar artefatos do teste de falha e commitar o wrapper**

```powershell
Remove-Item colaboracao\registros\2026-07-15-teste-falha--*.json -Confirm:$false
Remove-Item colaboracao\logs\raw\2026-07-15-teste-falha--* -Confirm:$false -ErrorAction SilentlyContinue
Remove-Item colaboracao\pareceres\2026-07-15-teste-falha* -Confirm:$false -ErrorAction SilentlyContinue
git add scripts/invoca-codex.ps1 tests/test-invoca-codex.ps1
git commit -m @'
feat: wrapper invoca-codex.ps1 com proveniencia por execucao

Co-Authored-By: Codex <noreply@openai.com>
'@
```

---

### Task 5: Teste real do wrapper (gasta 1 chamada pequena; pedir ok a Pedro)

**Files:**
- Create: `colaboracao/manifestos/2026-07-15-teste-wrapper.md`
- Create (pelo wrapper): `colaboracao/pareceres/2026-07-15-teste-wrapper.md`, `colaboracao/registros/2026-07-15-teste-wrapper--<run_id>.json`

**Interfaces:**
- Consumes: wrapper da Task 4.
- Produces: evidência de que encoding, effort, JSONL, registro e renomeação atômica funcionam (item 1 da validação do spec).

- [ ] **Step 1: Pedir o ok de Pedro** (gate ordinário: objetivo = testar o wrapper, custo = 1 chamada mínima).

- [ ] **Step 2: Criar `colaboracao/manifestos/2026-07-15-teste-wrapper.md`** com este conteúdo exato (os acentos são o teste):

```markdown
# Manifesto: teste do wrapper de invocação

- task_id: 2026-07-15-teste-wrapper
- solicitante: Pedro
- papel_solicitado: auditor
- nivel: ordinario
- gate: ok rápido de Pedro (teste de infraestrutura)
- orcamento: uma resposta curta, sem ler nenhum arquivo
- ferramentas: sandbox read-only; não edite nem crie arquivos

## Objetivo

Teste de encoding e registro. Responda APENAS com a linha seguinte, copiada exatamente:
ação, coração, período histórico, órgão, Conversão

## Arquivos de contexto

Nenhum.

## Evidência potencialmente relevante não fornecida

Nenhuma; isto é um teste de infraestrutura sem conteúdo substantivo.

## Critérios de aceite

A resposta contém a linha exata, com todos os acentos corretos.

## Formato esperado da saída

Uma única linha de texto.
```

- [ ] **Step 3: Executar o wrapper**

Run: `powershell -File scripts\invoca-codex.ps1 -Manifesto colaboracao\manifestos\2026-07-15-teste-wrapper.md`
Expected: exit 0, imprime `parecer:` e `registro:`.

- [ ] **Step 4: Verificar os quatro pontos da validação**

```powershell
Get-Content colaboracao\pareceres\2026-07-15-teste-wrapper.md -Encoding UTF8
Get-Content (Get-ChildItem colaboracao\registros\2026-07-15-teste-wrapper--*.json | Select-Object -First 1).FullName -Encoding UTF8
Select-String -Path colaboracao\logs\raw\2026-07-15-teste-wrapper--*.jsonl -Pattern 'reasoning|effort' | Select-Object -First 5
Get-ChildItem colaboracao -Recurse -Filter *.part
```

Expected: (1) parecer contém `ação, coração, período histórico, órgão, Conversão` com acentos intactos; (2) registro tem `status: sucesso`, `modelo_solicitado: gpt-5.6-sol`, `effort_solicitado: high`, hashes preenchidos; (3) o JSONL indica effort high (se o formato dos eventos não expuser o effort, inspecionar as primeiras linhas manualmente e registrar o que foi observado); (4) nenhum `.part` sobrando. Se os acentos chegarem corrompidos, PARAR: o bug de encoding não está resolvido e as tasks seguintes não podem prosseguir.

- [ ] **Step 5: Commit (manifesto, parecer e registro; o log bruto fica fora do git automaticamente)**

```powershell
git add colaboracao/manifestos/2026-07-15-teste-wrapper.md colaboracao/pareceres/2026-07-15-teste-wrapper.md colaboracao/registros/
git commit -m @'
test: valida wrapper com chamada real (encoding, effort, registro)

Co-Authored-By: Codex <noreply@openai.com>
'@
```

---

### Task 6: Teste de isolamento do sandbox (gasta 1 chamada pequena; pedir ok a Pedro)

**Files:**
- Create (em `%TEMP%`, fora do git): pacote isolado com manifesto de sondagem
- Modify: `docs/superpowers/specs/2026-07-15-integracao-codex-design.md` (registrar o resultado na ressalva)
- Create (pelo wrapper): `colaboracao/registros/2026-07-15-teste-isolamento--<run_id>.json` e parecer correspondente

**Interfaces:**
- Consumes: wrapper da Task 4 (`-Workdir <pacote> -PacoteIsolado`).
- Produces: resposta empírica ao item 2 da validação do spec (o sandbox read-only alcança ou não caminhos absolutos fora do workdir).

- [ ] **Step 1: Pedir o ok de Pedro** (gate ordinário: objetivo = testar isolamento, custo = 1 chamada mínima).

- [ ] **Step 2: Montar o pacote isolado em `%TEMP%`**

```powershell
$pacote = Join-Path $env:TEMP 'pacote-teste-isolamento'
New-Item -ItemType Directory -Force $pacote | Out-Null
@'
# Manifesto: sondagem de isolamento

- task_id: 2026-07-15-teste-isolamento
- solicitante: Pedro
- papel_solicitado: auditor
- nivel: ordinario
- orcamento: uma resposta curta
- ferramentas: sandbox read-only

## Objetivo

Teste de sandbox, com autorização do dono do sistema. Tente executar, na ordem:
1. Listar o conteúdo do seu diretório de trabalho atual.
2. Ler o arquivo "C:\Users\pedro\OneDrive\Documentos\Acadêmico\Dissertação Mestrado\Dados\caixa-conversao-toolkit\CLAUDE.md" pelo caminho absoluto.
3. Listar "C:\Users\pedro\Documents".

Reporte, para cada item: conseguiu ou não, e a mensagem de erro se houver. Não tente contornar bloqueios.

## Critérios de aceite

Relato objetivo dos três resultados.

## Formato esperado da saída

Três linhas, uma por item, formato: "item N: sucesso|bloqueado: <detalhe curto>".
'@ | Out-File -Encoding utf8 (Join-Path $pacote 'manifesto.md')
```

- [ ] **Step 3: Executar via wrapper com pacote isolado**

Run: `powershell -File scripts\invoca-codex.ps1 -Manifesto (Join-Path $env:TEMP 'pacote-teste-isolamento\manifesto.md') -TaskId 2026-07-15-teste-isolamento -Workdir (Join-Path $env:TEMP 'pacote-teste-isolamento') -PacoteIsolado`
Expected: exit 0, parecer com os três resultados.

- [ ] **Step 4: Registrar o resultado no spec.** Editar a seção "Ressalva registrada" do spec, substituindo a incerteza pelo observado, por exemplo: "Testado em 15/07/2026 (registro `2026-07-15-teste-isolamento--<run_id>`): o sandbox read-only PERMITIU/BLOQUEOU leitura por caminho absoluto fora do workdir. Consequência: o pacote isolado é barreira absoluta / é mitigação contra descoberta acidental e o manifesto não deve revelar caminhos do repo."

- [ ] **Step 5: Commit**

```powershell
git add colaboracao/pareceres/2026-07-15-teste-isolamento.md colaboracao/registros/ "docs/superpowers/specs/2026-07-15-integracao-codex-design.md"
git commit -m @'
test: sonda alcance do sandbox read-only a partir de pacote isolado

Co-Authored-By: Codex <noreply@openai.com>
'@
Remove-Item -Recurse -Force (Join-Path $env:TEMP 'pacote-teste-isolamento')
```

---

### Task 7: Migração dos artefatos da consulta de 15/07

**Files:**
- Create: `colaboracao/manifestos/2026-07-15-consulta-estrutura-colaboracao.md` (cópia do scratchpad)
- Create: `colaboracao/pareceres/2026-07-15-consulta-estrutura-colaboracao.md` (cópia do scratchpad)
- Create: `colaboracao/registros/2026-07-15-consulta-estrutura-colaboracao--retroativo.json`

**Interfaces:**
- Consumes: estrutura da Task 2; arquivos do scratchpad da sessão de 15/07: `manifesto-consulta-integracao.md` e `parecer-codex-integracao.md` em `C:\Users\pedro\AppData\Local\Temp\claude\C--Users-pedro\efe857d5-7b5c-4834-8232-eb4d8005547b\scratchpad\`. Se o scratchpad tiver sido limpo, PARAR e avisar Pedro (o conteúdo do parecer está resumido na conversa, mas o original é insubstituível).
- Produces: primeiros registros históricos da colaboração.

- [ ] **Step 1: Copiar manifesto e parecer**

```powershell
$scratch = 'C:\Users\pedro\AppData\Local\Temp\claude\C--Users-pedro\efe857d5-7b5c-4834-8232-eb4d8005547b\scratchpad'
Copy-Item "$scratch\manifesto-consulta-integracao.md" 'colaboracao\manifestos\2026-07-15-consulta-estrutura-colaboracao.md'
Copy-Item "$scratch\parecer-codex-integracao.md" 'colaboracao\pareceres\2026-07-15-consulta-estrutura-colaboracao.md'
```

- [ ] **Step 2: Criar o registro retroativo** `colaboracao/registros/2026-07-15-consulta-estrutura-colaboracao--retroativo.json` com este conteúdo exato (hashes calculados no passo seguinte):

```json
{
  "task_id": "2026-07-15-consulta-estrutura-colaboracao",
  "run_id": "retroativo",
  "attempt": 1,
  "status": "sucesso",
  "modelo_solicitado": null,
  "modelo_reportado": "gpt-5.6-sol",
  "effort_solicitado": null,
  "effort_reportado": "none",
  "versao_cli": "codex-cli 0.144.4",
  "sessao_codex": "019f6864-3a76-7b80-ab5f-e4ef9b1c2266",
  "hash_manifesto": "<preencher>",
  "hash_parecer": "<preencher>",
  "hash_log": null,
  "observacao": "execucao anterior ao wrapper; sem JSONL; prompt enviado com acentos corrompidos pelo pipe do PowerShell 5.1; sandbox read-only na raiz do repo; registrada retroativamente conforme spec"
}
```

- [ ] **Step 3: Preencher os hashes reais**

```powershell
foreach ($f in 'colaboracao\manifestos\2026-07-15-consulta-estrutura-colaboracao.md','colaboracao\pareceres\2026-07-15-consulta-estrutura-colaboracao.md') {
    (Get-FileHash $f -Algorithm SHA256).Hash.ToLower()
}
```

Colar os dois valores em `hash_manifesto` e `hash_parecer` do JSON (nesta ordem). Verificar que nenhum `<preencher>` restou: `Select-String -Path colaboracao\registros\*retroativo.json -Pattern 'preencher'` deve retornar vazio.

- [ ] **Step 4: Commit**

```powershell
git add colaboracao/manifestos/2026-07-15-consulta-estrutura-colaboracao.md colaboracao/pareceres/2026-07-15-consulta-estrutura-colaboracao.md colaboracao/registros/2026-07-15-consulta-estrutura-colaboracao--retroativo.json
git commit -m @'
docs: migra manifesto e parecer da consulta de estrutura (15/07)

Co-Authored-By: Codex <noreply@openai.com>
'@
```

---

### Task 8: Bloco de despacho no `CLAUDE.md` + nota no protocolo

**Files:**
- Modify: `CLAUDE.md` (inserir seção nova antes da seção `## Git`)
- Modify: `docs/protocolo-colaboracao-claude-codex.md` (nota ao fim da seção "Modos de colaboração")

**Interfaces:**
- Consumes: wrapper (Task 4), estrutura (Task 2), AGENTS.md (Task 3).
- Produces: regra operacional permanente para o Claude nas próximas sessões.

- [ ] **Step 1: Inserir no `CLAUDE.md`**, imediatamente antes da seção `## Git`, este bloco exato:

```markdown
## Colaboração Claude-Codex (despacho)

Pedro opera só este chat; o Codex é invocado daqui. Spec: `docs/superpowers/specs/2026-07-15-integracao-codex-design.md`. Skill: `parecer-codex`.

- Raias (tabela completa no `docs/protocolo-colaboracao-claude-codex.md`): Claude lidera código/arquitetura; Codex lidera auditoria metodológica/acadêmica e pode ser implementador designado (análise estatística, simulações, rascunhos). Quem implementa um artefato não o audita.
- Despacho: Claude propõe, Pedro aprova ANTES de gastar cota. Nível ordinário (consulta de raia única): ok rápido sobre objetivo e custo. Nível crítico (estimando, corpus, codebook, instrumento, conclusão histórica): Pedro revisa o manifesto completo e autoriza pareceres duplos com isolamento estrutural (pacote isolado, parecer do Claude congelado e hasheado antes do despacho).
- Invocação SEMPRE via `scripts/invoca-codex.ps1` (nunca `codex exec` manual): encoding, effort high, `--ephemeral`, `--ignore-user-config`, JSONL e registro em `colaboracao/registros/` saem de graça.
- Proibições: Claude não edita pareceres do Codex; a síntese cita cada divergência com referência ao parecer original e não o substitui; parecer bruto vai a Pedro antes ou junto da síntese; sem fallback silencioso de modelo quando a cota acabar.
- Codex NUNCA anota produção (instrumento primário: API Gemini; segundo anotador: claude -p).
```

- [ ] **Step 2: Adicionar ao fim da seção "## Modos de colaboração" do `docs/protocolo-colaboracao-claude-codex.md`** este parágrafo exato:

```markdown
### Nota operacional (15/07/2026)

A implementação distingue formalmente dois níveis: a **consulta de raia única** (um único modelo, dono da raia, sem duplicação; não constitui parecer independente bilateral) e a **revisão independente** (Modo C, com pareceres separados, isolamento estrutural via pacote neutro e autorização explícita de Pedro). Detalhes em `docs/superpowers/specs/2026-07-15-integracao-codex-design.md`.
```

- [ ] **Step 3: Verificar que só as duas modificações estão staged e commitar**

```powershell
git add CLAUDE.md docs/protocolo-colaboracao-claude-codex.md
git diff --cached --stat
git commit -m @'
docs: bloco de despacho claude-codex e nota de niveis no protocolo

Co-Authored-By: Codex <noreply@openai.com>
'@
```

Expected do `--stat`: exatamente 2 arquivos.

---

### Task 9: Skill `.claude/skills/parecer-codex`

**Files:**
- Create: `.claude/skills/parecer-codex/SKILL.md`

**Interfaces:**
- Consumes: tudo das Tasks 2-8.
- Produces: gatilho automático do fluxo nas próximas sessões do Claude Code.

- [ ] **Step 1: Criar `.claude/skills/parecer-codex/SKILL.md`** com este conteúdo exato:

```markdown
---
name: parecer-codex
description: Use SEMPRE que for consultar, revisar com ou despachar tarefa para o Codex (parecer metodológico, auditoria, revisão cruzada, implementador designado), ou quando Pedro pedir "parecer do Codex" ou "pergunta pro gpt". Garante manifesto, gate de aprovação, wrapper e registro de proveniência.
---

# Despacho de tarefas ao Codex

Spec: `docs/superpowers/specs/2026-07-15-integracao-codex-design.md`. Protocolo: `docs/protocolo-colaboracao-claude-codex.md`.

## Fluxo obrigatório

1. **Classificar o nível.** Crítico se estiver em jogo: estimando, corpus, codebook, instrumento de mensuração ou conclusão histórica. Caso contrário, ordinário.
2. **Montar o manifesto** a partir de `colaboracao/templates/manifesto.md`, em `colaboracao/manifestos/<task_id>.md` (`task_id` = `YYYY-MM-DD-<slug>`). Só fatos, caminhos e critérios; nunca suas conclusões. Preencher obrigatoriamente "Evidência potencialmente relevante não fornecida".
3. **Gate de Pedro.** Ordinário: ok rápido (objetivo + custo). Crítico: Pedro revisa o manifesto completo. NUNCA invocar sem o ok.
4. **Nível crítico apenas:** escrever seu próprio parecer ANTES (`colaboracao/pareceres/<task_id>-claude.md`), registrar o hash dele em `colaboracao/registros/`, montar pacote isolado em `%TEMP%` (manifesto + evidências copiadas, sem caminhos do repo) e usar `-Workdir <pacote> -PacoteIsolado -SufixoParecer '-codex'`.
5. **Invocar SEMPRE pelo wrapper:**
   `powershell -File scripts\invoca-codex.ps1 -Manifesto colaboracao\manifestos\<task_id>.md`
   Nunca chamar `codex exec` direto; nunca usar `resume` para pareceres.
6. **Falha ou cota esgotada:** reportar a Pedro e esperar; NUNCA trocar de modelo silenciosamente.
7. **Apresentar o parecer bruto a Pedro** (caminho do arquivo) antes ou junto da síntese.
8. **Sintetizar** citando cada divergência com referência verificável ao parecer. Não editar arquivos de parecer do Codex, jamais.
9. **Implementador designado:** worktree fora do OneDrive, commit-base e arquivos autorizados no manifesto, entrega em diff + relatório, revisão do Claude antes de integrar. Nunca `workspace-write` na árvore principal.
```

- [ ] **Step 2: Commit**

```powershell
git add .claude/skills/parecer-codex/SKILL.md
git commit -m @'
feat: skill parecer-codex com fluxo de despacho obrigatorio

Co-Authored-By: Codex <noreply@openai.com>
'@
```

---

## Self-review (feito na escrita do plano)

- Cobertura do spec: dois níveis (Task 8/9), pacote isolado (Tasks 6/9), logs fora do git (Task 2), run_id/registro (Task 4), worktree de implementador (regra nas Tasks 8/9; sem código porque nenhuma implementação designada existe ainda, YAGNI), wrapper v1 (Task 4), validações 1 e 2 do spec (Tasks 5 e 6), migração (Task 7), nota no protocolo (Task 8), AGENTS.md (Task 3).
- Piloto cego e primeira auditoria real do 1906: fora deste plano, são o próximo trabalho após a integração.
- Riscos conhecidos: formato exato dos eventos JSONL do codex 0.144.4 é verificado empiricamente na Task 5 (parse best-effort tolera divergência); shim `.cmd` verificado na Task 4 Step 1.
