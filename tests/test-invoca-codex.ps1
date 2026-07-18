#Requires -Version 5.1
param(
    [ValidateSet('manifesto-ausente', 'sucesso-utf8', 'falha-codex', 'colisao', 'parecer-nao-sobrescreve', 'workdir-metacaractere', 'isolamento-verificado', 'versao-stderr', 'hash-sujo', 'validacao', 'all')]
    [string]$Case = 'all'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Wrapper = Join-Path $RepoRoot 'scripts\invoca-codex.ps1'
$TestRoot = Join-Path $env:TEMP ("invoca-codex-tests-{0}" -f $PID)
$ShimPs1 = Join-Path $TestRoot 'fake-codex.ps1'
$ShimCmd = Join-Path $TestRoot 'codex.cmd'
$CallLog = Join-Path $TestRoot 'calls.txt'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$AccentLine = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('YcOnw6NvLCBjb3Jhw6fDo28sIHBlcsOtb2RvIGhpc3TDs3JpY28sIMOzcmfDo28sIENvbnZlcnPDo28='))
$TaskPrefix = "teste-wrapper-$PID"

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "ASSERT: $Message" }
}

function Assert-Equal($Expected, $Actual, [string]$Message) {
    if ($Expected -ne $Actual) {
        throw "ASSERT: $Message. esperado=[$Expected] atual=[$Actual]"
    }
}

function Invoke-Wrapper([string[]]$Arguments) {
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = @(& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Wrapper @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    [pscustomobject]@{ ExitCode = $exitCode; Output = ($output -join "`n") }
}

function Get-Records([string]$TaskId) {
    @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'colaboracao\registros') -Filter "$TaskId--*.json" -ErrorAction SilentlyContinue | Sort-Object Name)
}

function Get-Registro([string]$Path) {
    Get-Content -LiteralPath $Path -Raw -Encoding utf8 | ConvertFrom-Json
}

function Get-ParecerPath($Record) {
    Join-Path $RepoRoot (($Record.parecer) -replace '/', '\')
}

function Remove-Artifacts([string]$TaskId) {
    foreach ($relative in @('colaboracao\registros', 'colaboracao\pareceres', 'colaboracao\logs\raw')) {
        $dir = Join-Path $RepoRoot $relative
        Get-ChildItem -LiteralPath $dir -Filter "$TaskId*" -ErrorAction SilentlyContinue |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }
}

function New-Manifest([string]$TaskId) {
    $path = Join-Path $TestRoot "$TaskId-manifesto.md"
    [IO.File]::WriteAllText($path, "$AccentLine`n", $Utf8NoBom)
    $path
}

function Test-ManifestoAusente {
    $task = "$TaskPrefix-ausente"
    $result = Invoke-Wrapper @('-Manifesto', (Join-Path $TestRoot 'nao-existe.md'), '-TaskId', $task, '-CodexCommand', $ShimCmd)
    Assert-True ($result.ExitCode -ne 0) 'manifesto ausente deve falhar'
    Assert-True ($result.Output -match 'Manifesto nao encontrado') 'erro deve identificar manifesto ausente'
    Assert-Equal 0 (Get-Records $task).Count 'manifesto ausente não deve criar registro'
}

function Test-SucessoUtf8 {
    $task = "$TaskPrefix-sucesso"
    $manifesto = New-Manifest $task
    $result = Invoke-Wrapper @('-Manifesto', $manifesto, '-TaskId', $task, '-CodexCommand', $ShimCmd)
    Assert-Equal 0 $result.ExitCode "shim de sucesso deve produzir exit 0. saida=$($result.Output)"
    $records = Get-Records $task
    Assert-Equal 1 $records.Count 'sucesso deve criar um registro'
    $record = Get-Registro $records[0].FullName
    Assert-Equal 'sucesso' $record.status 'registro deve marcar sucesso'
    Assert-Equal 'gpt-5.6-sol' $record.modelo_solicitado 'modelo solicitado deve ser registrado'
    Assert-Equal 'high' $record.effort_solicitado 'effort deve ser registrado'
    Assert-True ([bool]$record.hash_manifesto) 'hash do manifesto deve existir'
    Assert-True ([bool]$record.hash_parecer) 'hash do parecer deve existir'
    Assert-True ([bool]$record.hash_log) 'hash do log deve existir'
    Assert-True ([bool]$record.sessao_codex) 'sessao_codex deve ser capturada do thread.started'
    Assert-True ([bool]$record.parecer) 'registro deve apontar o caminho do parecer'
    # O parecer é o eco do stdin: prova que o manifesto chega ao Codex por stdin com acentos intactos.
    $parecer = Get-ParecerPath $record
    Assert-True (Test-Path -LiteralPath $parecer) 'parecer final deve existir'
    Assert-Equal $AccentLine ([IO.File]::ReadAllText($parecer, $Utf8NoBom).Trim()) 'acentos do manifesto devem chegar via stdin ao parecer'
    Assert-True ($record.git_status_porcelain -notmatch 'colaboracao/') 'estado sujo não deve listar a papelada de colaboracao/'
    Assert-Equal 0 @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'colaboracao') -Recurse -Filter '*.part').Count 'não deve sobrar arquivo parcial'
}

function Test-FalhaCodex {
    $task = "$TaskPrefix-falha"
    $manifesto = New-Manifest $task
    $env:FAKE_CODEX_EXIT = '23'
    try {
        $result = Invoke-Wrapper @('-Manifesto', $manifesto, '-TaskId', $task, '-CodexCommand', $ShimCmd)
    } finally {
        Remove-Item Env:FAKE_CODEX_EXIT -ErrorAction SilentlyContinue
    }
    Assert-True ($result.ExitCode -ne 0) 'falha do codex deve propagar falha do wrapper'
    $records = Get-Records $task
    Assert-Equal 1 $records.Count 'falha deve criar um registro'
    $record = Get-Registro $records[0].FullName
    Assert-Equal 'falha' $record.status 'registro deve marcar falha'
    Assert-Equal 23 $record.exit_code 'registro deve preservar exit code'
    Assert-Equal 0 @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'colaboracao\pareceres') -Filter "$task*" -ErrorAction SilentlyContinue).Count 'falha não deve publicar parecer em pareceres/'
    Assert-Equal 0 @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'colaboracao') -Recurse -Filter '*.part').Count 'falha não deve deixar arquivo parcial'
}

function Test-Colisao {
    $task = "$TaskPrefix-colisao"
    $manifesto = New-Manifest $task
    $first = Invoke-Wrapper @('-Manifesto', $manifesto, '-TaskId', $task, '-CodexCommand', $ShimCmd)
    $second = Invoke-Wrapper @('-Manifesto', $manifesto, '-TaskId', $task, '-CodexCommand', $ShimCmd)
    Assert-Equal 0 $first.ExitCode 'primeira execução deve passar'
    Assert-Equal 0 $second.ExitCode 'segunda execução deve passar'
    $records = Get-Records $task
    Assert-Equal 2 $records.Count 'duas execuções rápidas devem gerar dois registros'
    Assert-True ($records[0].BaseName -ne $records[1].BaseName) 'run_id não pode colidir'
    $p0 = Get-ParecerPath (Get-Registro $records[0].FullName)
    $p1 = Get-ParecerPath (Get-Registro $records[1].FullName)
    Assert-True ($p0 -ne $p1) 'cada execução deve ter parecer próprio'
    Assert-True ((Test-Path -LiteralPath $p0) -and (Test-Path -LiteralPath $p1)) 'os dois pareceres devem coexistir'
}

function Test-ParecerNaoSobrescreve {
    $task = "$TaskPrefix-nosobre"
    $m1 = Join-Path $TestRoot "$task-1.md"
    [IO.File]::WriteAllText($m1, "conteudo-um`n", $Utf8NoBom)
    $r1 = Invoke-Wrapper @('-Manifesto', $m1, '-TaskId', $task, '-CodexCommand', $ShimCmd)
    Assert-Equal 0 $r1.ExitCode 'primeira execução deve passar'
    $m2 = Join-Path $TestRoot "$task-2.md"
    [IO.File]::WriteAllText($m2, "conteudo-dois-diferente`n", $Utf8NoBom)
    $r2 = Invoke-Wrapper @('-Manifesto', $m2, '-TaskId', $task, '-CodexCommand', $ShimCmd)
    Assert-Equal 0 $r2.ExitCode 'segunda execução deve passar'
    $records = Get-Records $task
    Assert-Equal 2 $records.Count 're-execução deve criar novo registro, não sobrescrever'
    $pareceres = @($records | ForEach-Object { Get-ParecerPath (Get-Registro $_.FullName) })
    Assert-True ($pareceres[0] -ne $pareceres[1]) 'pareceres devem ter nomes distintos'
    Assert-True ((Test-Path -LiteralPath $pareceres[0]) -and (Test-Path -LiteralPath $pareceres[1])) 'nenhum parecer pode ter sido sobrescrito'
    $conteudos = @($pareceres | ForEach-Object { ([IO.File]::ReadAllText($_, $Utf8NoBom)).Trim() })
    Assert-True ($conteudos -contains 'conteudo-um') 'parecer da 1a execução deve sobreviver com seu conteúdo'
    Assert-True ($conteudos -contains 'conteudo-dois-diferente') 'parecer da 2a execução deve ter seu próprio conteúdo'
}

function Test-WorkdirMetacaractere {
    $task = "$TaskPrefix-metacar"
    $manifesto = New-Manifest $task
    $wd = Join-Path $TestRoot 'pac & ote (x)'   # metacaracteres de cmd, fora do repo
    New-Item -ItemType Directory -Force $wd | Out-Null
    $result = Invoke-Wrapper @('-Manifesto', $manifesto, '-TaskId', $task, '-Workdir', $wd, '-PacoteIsolado', '-CodexCommand', $ShimCmd)
    Assert-Equal 0 $result.ExitCode "workdir com & e () não deve quebrar nem injetar. saida=$($result.Output)"
    $records = Get-Records $task
    Assert-Equal 1 $records.Count 'execução com workdir isolado deve criar um registro'
    $record = Get-Registro $records[0].FullName
    Assert-Equal $true $record.workdir_isolado 'workdir fora do repo deve marcar isolado verificado'
    $parecer = Get-ParecerPath $record
    Assert-Equal $AccentLine ([IO.File]::ReadAllText($parecer, $Utf8NoBom).Trim()) 'acentos preservados mesmo com workdir estranho'
}

function Test-IsolamentoVerificado {
    $task = "$TaskPrefix-isolfail"
    $manifesto = New-Manifest $task
    # -PacoteIsolado sem -Workdir cai no default (raiz do repo, dentro): deve falhar em vez de mentir isolamento.
    $result = Invoke-Wrapper @('-Manifesto', $manifesto, '-TaskId', $task, '-PacoteIsolado', '-CodexCommand', $ShimCmd)
    Assert-True ($result.ExitCode -ne 0) 'PacoteIsolado com workdir dentro do repo deve falhar'
    Assert-True ($result.Output -match 'fora do repositorio') 'erro deve exigir workdir fora do repositorio'
    Assert-Equal 0 (Get-Records $task).Count 'falha de validação de isolamento não deve criar registro'
}

function Test-VersaoStderr {
    $task = "$TaskPrefix-versao"
    $manifesto = New-Manifest $task
    $env:FAKE_CODEX_VERSION_STDERR = '1'
    try {
        $result = Invoke-Wrapper @('-Manifesto', $manifesto, '-TaskId', $task, '-CodexCommand', $ShimCmd)
    } finally {
        Remove-Item Env:FAKE_CODEX_VERSION_STDERR -ErrorAction SilentlyContinue
    }
    Assert-Equal 0 $result.ExitCode "banner em stderr no --version não deve abortar a execução. saida=$($result.Output)"
}

function Test-HashSujo {
    $dirty = Join-Path $RepoRoot "docs\$TaskPrefix-dirty.tmp"
    $taskA = "$TaskPrefix-hash-a"
    $taskB = "$TaskPrefix-hash-b"
    try {
        [IO.File]::WriteAllText($dirty, 'conteudo-a', $Utf8NoBom)
        $manifestoA = New-Manifest $taskA
        $first = Invoke-Wrapper @('-Manifesto', $manifestoA, '-TaskId', $taskA, '-CodexCommand', $ShimCmd)
        Assert-Equal 0 $first.ExitCode 'primeiro snapshot sujo deve passar'
        $recordA = Get-Registro (Get-Records $taskA)[0].FullName
        Remove-Artifacts $taskA
        [IO.File]::WriteAllText($dirty, 'conteudo-b', $Utf8NoBom)
        $manifestoB = New-Manifest $taskB
        $second = Invoke-Wrapper @('-Manifesto', $manifestoB, '-TaskId', $taskB, '-CodexCommand', $ShimCmd)
        Assert-Equal 0 $second.ExitCode 'segundo snapshot sujo deve passar'
        $recordB = Get-Registro (Get-Records $taskB)[0].FullName
        Assert-True ([bool]$recordA.hash_diff) 'estado sujo deve produzir hash_diff'
        Assert-True ($recordA.hash_diff -ne $recordB.hash_diff) 'hash_diff deve mudar com conteúdo untracked'
    } finally {
        Remove-Item -LiteralPath $dirty -Force -ErrorAction SilentlyContinue
    }
}

function Test-Validacao {
    $manifesto = New-Manifest "$TaskPrefix-validacao"
    Remove-Item -LiteralPath $CallLog -Force -ErrorAction SilentlyContinue
    $env:FAKE_CODEX_CALL_LOG = $CallLog
    try {
        $invalidSets = @(
            @('-Manifesto', $manifesto, '-TaskId', 'ruim & comando', '-CodexCommand', $ShimCmd),
            @('-Manifesto', $manifesto, '-TaskId', "$TaskPrefix-modelo", '-Modelo', 'modelo & comando', '-CodexCommand', $ShimCmd),
            @('-Manifesto', $manifesto, '-TaskId', "$TaskPrefix-effort", '-Effort', 'high & comando', '-CodexCommand', $ShimCmd),
            @('-Manifesto', $manifesto, '-TaskId', "$TaskPrefix-sufixo", '-SufixoParecer', '-x & comando', '-CodexCommand', $ShimCmd)
        )
        foreach ($argumentos in $invalidSets) {
            $result = Invoke-Wrapper $argumentos
            Assert-True ($result.ExitCode -ne 0) "parâmetro inválido deve falhar: $($argumentos -join ' ')"
        }
        Assert-True (-not (Test-Path -LiteralPath $CallLog)) 'validação deve ocorrer antes de invocar codex'
    } finally {
        Remove-Item Env:FAKE_CODEX_CALL_LOG -ErrorAction SilentlyContinue
    }
}

New-Item -ItemType Directory -Force $TestRoot | Out-Null
# Shim PS: emite o schema JSONL real do codex-cli (thread.started, turn.*, item.*),
# SEM campo model no topo, e ecoa o stdin recebido para --output-last-message. Assim o
# teste exercita a passagem UTF-8 do manifesto por stdin, não um literal embutido.
[IO.File]::WriteAllText($ShimPs1, @'
$utf8 = New-Object System.Text.UTF8Encoding($false)
[Console]::Out.Write('{"type":"thread.started","thread_id":"test-thread-0001"}' + "`n")
[Console]::Out.Write('{"type":"turn.started"}' + "`n")
$ms = New-Object System.IO.MemoryStream
[Console]::OpenStandardInput().CopyTo($ms)
$texto = $utf8.GetString($ms.ToArray())
if ($env:FAKE_CODEX_OUTPUT) { [IO.File]::WriteAllText($env:FAKE_CODEX_OUTPUT, $texto, $utf8) }
[Console]::Out.Write('{"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"ok"}}' + "`n")
[Console]::Out.Write('{"type":"turn.completed","usage":{"input_tokens":10,"cached_input_tokens":0,"output_tokens":3,"reasoning_output_tokens":0}}' + "`n")
'@, $Utf8NoBom)
[IO.File]::WriteAllText($ShimCmd, @'
@echo off
setlocal
set "SHIM_DIR=%~dp0"
if "%~1"=="--version" (
  echo codex-cli fake-1.0
  if defined FAKE_CODEX_VERSION_STDERR echo aviso de telemetria 1>&2
  exit /b 0
)
if defined FAKE_CODEX_CALL_LOG echo called>>"%FAKE_CODEX_CALL_LOG%"
:parse
if "%~1"=="" goto execute
if "%~1"=="--output-last-message" goto capture_output
shift
goto parse
:capture_output
shift
set "FAKE_CODEX_OUTPUT=%~1"
shift
goto parse
:execute
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SHIM_DIR%fake-codex.ps1"
if defined FAKE_CODEX_EXIT (
  echo falha simulada 1>&2
  exit /b %FAKE_CODEX_EXIT%
)
exit /b 0
'@, $Utf8NoBom)

$cases = if ($Case -eq 'all') {
    @('manifesto-ausente', 'sucesso-utf8', 'falha-codex', 'colisao', 'parecer-nao-sobrescreve', 'workdir-metacaractere', 'isolamento-verificado', 'versao-stderr', 'hash-sujo', 'validacao')
} else { @($Case) }

try {
    foreach ($current in $cases) {
        switch ($current) {
            'manifesto-ausente' { Test-ManifestoAusente }
            'sucesso-utf8' { Test-SucessoUtf8 }
            'falha-codex' { Test-FalhaCodex }
            'colisao' { Test-Colisao }
            'parecer-nao-sobrescreve' { Test-ParecerNaoSobrescreve }
            'workdir-metacaractere' { Test-WorkdirMetacaractere }
            'isolamento-verificado' { Test-IsolamentoVerificado }
            'versao-stderr' { Test-VersaoStderr }
            'hash-sujo' { Test-HashSujo }
            'validacao' { Test-Validacao }
        }
        Write-Output "PASS: $current"
    }
} finally {
    if (-not $env:KEEP_INVOCA_CODEX_TEST_TEMP) {
        foreach ($task in @("$TaskPrefix-ausente", "$TaskPrefix-sucesso", "$TaskPrefix-falha", "$TaskPrefix-colisao", "$TaskPrefix-nosobre", "$TaskPrefix-metacar", "$TaskPrefix-isolfail", "$TaskPrefix-versao", "$TaskPrefix-hash-a", "$TaskPrefix-hash-b", "$TaskPrefix-validacao", "$TaskPrefix-modelo", "$TaskPrefix-effort", "$TaskPrefix-sufixo")) {
            Remove-Artifacts $task
        }
        Remove-Item -LiteralPath $TestRoot -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        Write-Output "TEST_TEMP: $TestRoot"
    }
}
