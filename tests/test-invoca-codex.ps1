#Requires -Version 5.1
param(
    [ValidateSet('manifesto-ausente', 'sucesso-utf8', 'falha-codex', 'colisao', 'hash-sujo', 'validacao', 'all')]
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
    $parecer = Join-Path $RepoRoot "colaboracao\pareceres\$task.md"
    Assert-True (Test-Path -LiteralPath $parecer) 'parecer final deve existir'
    Assert-Equal $AccentLine ([IO.File]::ReadAllText($parecer, $Utf8NoBom).Trim()) 'acentos devem ser preservados'
    $records = Get-Records $task
    Assert-Equal 1 $records.Count 'sucesso deve criar um registro'
    $record = Get-Content -LiteralPath $records[0].FullName -Raw -Encoding utf8 | ConvertFrom-Json
    Assert-Equal 'sucesso' $record.status 'registro deve marcar sucesso'
    Assert-Equal 'gpt-5.6-sol' $record.modelo_solicitado 'modelo solicitado deve ser registrado'
    Assert-Equal 'high' $record.effort_solicitado 'effort deve ser registrado'
    Assert-True ([bool]$record.hash_manifesto) 'hash do manifesto deve existir'
    Assert-True ([bool]$record.hash_parecer) 'hash do parecer deve existir'
    Assert-True ([bool]$record.hash_log) 'hash do log deve existir'
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
    $record = Get-Content -LiteralPath $records[0].FullName -Raw -Encoding utf8 | ConvertFrom-Json
    Assert-Equal 'falha' $record.status 'registro deve marcar falha'
    Assert-Equal 23 $record.exit_code 'registro deve preservar exit code'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $RepoRoot "colaboracao\pareceres\$task.md"))) 'falha não deve publicar parecer final'
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
        $recordA = Get-Content -LiteralPath (Get-Records $taskA)[0].FullName -Raw -Encoding utf8 | ConvertFrom-Json
        Remove-Artifacts $taskA
        [IO.File]::WriteAllText($dirty, 'conteudo-b', $Utf8NoBom)
        $manifestoB = New-Manifest $taskB
        $second = Invoke-Wrapper @('-Manifesto', $manifestoB, '-TaskId', $taskB, '-CodexCommand', $ShimCmd)
        Assert-Equal 0 $second.ExitCode 'segundo snapshot sujo deve passar'
        $recordB = Get-Content -LiteralPath (Get-Records $taskB)[0].FullName -Raw -Encoding utf8 | ConvertFrom-Json
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
        foreach ($args in $invalidSets) {
            $result = Invoke-Wrapper $args
            Assert-True ($result.ExitCode -ne 0) "parâmetro inválido deve falhar: $($args -join ' ')"
        }
        Assert-True (-not (Test-Path -LiteralPath $CallLog)) 'validação deve ocorrer antes de invocar codex'
    } finally {
        Remove-Item Env:FAKE_CODEX_CALL_LOG -ErrorAction SilentlyContinue
    }
}

New-Item -ItemType Directory -Force $TestRoot | Out-Null
[IO.File]::WriteAllText($ShimPs1, @'
$utf8 = New-Object System.Text.UTF8Encoding($false)
if (-not $env:FAKE_CODEX_OUTPUT) { throw 'FAKE_CODEX_OUTPUT ausente' }
$line = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('YcOnw6NvLCBjb3Jhw6fDo28sIHBlcsOtb2RvIGhpc3TDs3JpY28sIMOzcmfDo28sIENvbnZlcnPDo28='))
[IO.File]::WriteAllText($env:FAKE_CODEX_OUTPUT, "$line`n", $utf8)
'@, $Utf8NoBom)
[IO.File]::WriteAllText($ShimCmd, @'
@echo off
setlocal
set "SHIM_DIR=%~dp0"
if "%~1"=="--version" (
  echo codex-cli fake-1.0
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
echo {"type":"turn.completed","model":"gpt-5.6-sol","usage":{"input_tokens":1,"output_tokens":1}}
if defined FAKE_CODEX_EXIT (
  echo falha simulada 1>&2
  exit /b %FAKE_CODEX_EXIT%
)
exit /b 0
'@, $Utf8NoBom)

$cases = if ($Case -eq 'all') {
    @('manifesto-ausente', 'sucesso-utf8', 'falha-codex', 'colisao', 'hash-sujo', 'validacao')
} else { @($Case) }

try {
    foreach ($current in $cases) {
        switch ($current) {
            'manifesto-ausente' { Test-ManifestoAusente }
            'sucesso-utf8' { Test-SucessoUtf8 }
            'falha-codex' { Test-FalhaCodex }
            'colisao' { Test-Colisao }
            'hash-sujo' { Test-HashSujo }
            'validacao' { Test-Validacao }
        }
        Write-Output "PASS: $current"
    }
} finally {
    if (-not $env:KEEP_INVOCA_CODEX_TEST_TEMP) {
        foreach ($task in @("$TaskPrefix-ausente", "$TaskPrefix-sucesso", "$TaskPrefix-falha", "$TaskPrefix-colisao", "$TaskPrefix-hash-a", "$TaskPrefix-hash-b", "$TaskPrefix-modelo", "$TaskPrefix-effort", "$TaskPrefix-sufixo")) {
            Remove-Artifacts $task
        }
        Remove-Item -LiteralPath $TestRoot -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        Write-Output "TEST_TEMP: $TestRoot"
    }
}
