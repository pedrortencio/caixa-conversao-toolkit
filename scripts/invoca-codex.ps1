#Requires -Version 5.1
<#
Invoca codex exec com proveniência registrada.
Spec: docs/superpowers/specs/2026-07-15-integracao-codex-design.md
#>
param(
    [Parameter(Mandatory = $true)][string]$Manifesto,
    [string]$TaskId,
    [string]$Modelo = 'gpt-5.6-sol',
    [string]$Effort = 'high',
    [string]$Workdir,
    [switch]$PacoteIsolado,
    [string]$SufixoParecer = '',
    [string]$CodexCommand = 'codex.cmd'
)

$ErrorActionPreference = 'Stop'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ColabDir = Join-Path $RepoRoot 'colaboracao'
if (-not $Workdir) { $Workdir = $RepoRoot }

function Get-HashArquivo([string]$Caminho) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        ([BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($Caminho))) -replace '-', '').ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

function Assert-Pattern([string]$Value, [string]$Pattern, [string]$Name) {
    if ($Value -notmatch $Pattern) {
        throw "$Name invalido: $Value"
    }
}

function Assert-CmdSafe([string]$Value, [string]$Name) {
    if ($Value -match '["%\r\n]') {
        throw "$Name contem caractere inseguro para cmd.exe"
    }
}

function ConvertTo-CmdArg([string]$Value) {
    Assert-CmdSafe $Value 'argumento'
    '"' + $Value + '"'
}

function Get-GitOutput([string[]]$Arguments) {
    $output = @(& git -C $RepoRoot @Arguments)
    if ($LASTEXITCODE -ne 0) {
        throw "git falhou: git -C <repo> $($Arguments -join ' ')"
    }
    $output
}

if (-not (Test-Path -LiteralPath $Manifesto -PathType Leaf)) {
    throw "Manifesto nao encontrado: $Manifesto"
}
$Manifesto = (Resolve-Path -LiteralPath $Manifesto).Path
if (-not (Test-Path -LiteralPath $Workdir -PathType Container)) {
    throw "Workdir nao encontrado: $Workdir"
}
$Workdir = (Resolve-Path -LiteralPath $Workdir).Path
if (-not $TaskId) { $TaskId = [IO.Path]::GetFileNameWithoutExtension($Manifesto) }

Assert-Pattern $TaskId '^[a-z0-9][a-z0-9._-]*$' 'TaskId'
Assert-Pattern $Modelo '^[A-Za-z0-9][A-Za-z0-9._-]*$' 'Modelo'
Assert-Pattern $SufixoParecer '^(-[a-z0-9][a-z0-9._-]*)?$' 'SufixoParecer'
if ($Effort -notin @('minimal', 'low', 'medium', 'high', 'xhigh')) {
    throw "Effort invalido: $Effort"
}

foreach ($entry in @(
    @($Manifesto, 'Manifesto'),
    @($Workdir, 'Workdir'),
    @($RepoRoot, 'RepoRoot'),
    @($CodexCommand, 'CodexCommand')
)) {
    Assert-CmdSafe $entry[0] $entry[1]
}

$codexInfo = Get-Command $CodexCommand -ErrorAction Stop | Select-Object -First 1
$CodexResolved = if ($codexInfo.Path) { $codexInfo.Path } else { $codexInfo.Source }
if (-not $CodexResolved) { throw "CodexCommand nao resolvido: $CodexCommand" }
Assert-CmdSafe $CodexResolved 'CodexCommand resolvido'

$registrosDir = Join-Path $ColabDir 'registros'
$rawDir = Join-Path $ColabDir 'logs\raw'
$parecerDir = Join-Path $ColabDir 'pareceres'
foreach ($dir in @($registrosDir, $rawDir, $parecerDir)) {
    if (-not (Test-Path -LiteralPath $dir -PathType Container)) {
        throw "Diretorio de colaboracao ausente: $dir"
    }
}

$inicio = Get-Date
$hashManifesto = Get-HashArquivo $Manifesto
$attempt = @(Get-ChildItem -LiteralPath $registrosDir -Filter "$TaskId--*.json" -ErrorAction SilentlyContinue).Count + 1
$runId = '{0}-{1}' -f $inicio.ToString('yyyyMMddTHHmmssfff'), $hashManifesto.Substring(0, 8)
$registroFinal = Join-Path $registrosDir "$TaskId--$runId.json"
while (Test-Path -LiteralPath $registroFinal) {
    $runId = '{0}-{1}-{2}' -f $inicio.ToString('yyyyMMddTHHmmssfff'), $hashManifesto.Substring(0, 8), $attempt
    $attempt++
    $registroFinal = Join-Path $registrosDir "$TaskId--$runId.json"
}

$parecerFinal = Join-Path $parecerDir "$TaskId$SufixoParecer.md"
$rawFinal = Join-Path $rawDir "$TaskId--$runId.jsonl"
$errFinal = Join-Path $rawDir "$TaskId--$runId.err.txt"
$parecerPart = "$parecerFinal.$runId.part"
$rawPart = "$rawFinal.part"
$errPart = "$errFinal.part"
$registroPart = "$registroFinal.part"

$commit = (Get-GitOutput @('rev-parse', 'HEAD') | Select-Object -First 1).Trim()
$statusLines = @(Get-GitOutput @('status', '--porcelain=v1', '--untracked-files=all'))
$porcelain = $statusLines -join "`n"
$hashDiff = $null
if ($statusLines.Count -gt 0) {
    $snapshotTmp = Join-Path $env:TEMP "invoca-codex-snapshot-$runId.txt"
    try {
        $snapshot = New-Object System.Collections.Generic.List[string]
        $snapshot.Add('STATUS')
        foreach ($line in $statusLines) { $snapshot.Add($line) }
        $snapshot.Add('DIFF_BINARY_HEAD')
        foreach ($line in @(Get-GitOutput @('diff', '--binary', 'HEAD', '--', '.'))) { $snapshot.Add($line) }
        $snapshot.Add('UNTRACKED_SHA256')
        $untracked = @(Get-GitOutput @('-c', 'core.quotepath=false', 'ls-files', '--others', '--exclude-standard') | Sort-Object)
        foreach ($relative in $untracked) {
            $full = Join-Path $RepoRoot $relative
            if (Test-Path -LiteralPath $full -PathType Leaf) {
                $snapshot.Add("$relative`t$(Get-HashArquivo $full)")
            }
        }
        [IO.File]::WriteAllLines($snapshotTmp, $snapshot, $Utf8NoBom)
        $hashDiff = Get-HashArquivo $snapshotTmp
    } finally {
        Remove-Item -LiteralPath $snapshotTmp -Force -ErrorAction SilentlyContinue
    }
}

$versaoCli = @(& $CodexResolved --version 2>$null) -join ' '
if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel obter a versao do Codex" }

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

$argLine = ($codexArgs | ForEach-Object { ConvertTo-CmdArg $_ }) -join ' '
$cmdLine = "$(ConvertTo-CmdArg $CodexResolved) $argLine < $(ConvertTo-CmdArg $Manifesto) > $(ConvertTo-CmdArg $rawPart) 2> $(ConvertTo-CmdArg $errPart)"
$cmdPayload = '"' + $cmdLine + '"'
& $env:ComSpec /d /s /c $cmdPayload
$exitCode = $LASTEXITCODE
$fim = Get-Date
$sucesso = ($exitCode -eq 0) -and (Test-Path -LiteralPath $parecerPart -PathType Leaf)

$modeloReportado = $null
$tokenUsage = $null
if (Test-Path -LiteralPath $rawPart -PathType Leaf) {
    foreach ($linha in [IO.File]::ReadLines($rawPart)) {
        if ([string]::IsNullOrWhiteSpace($linha)) { continue }
        $ev = $null
        try { $ev = $linha | ConvertFrom-Json } catch { continue }
        if ($null -eq $ev) { continue }
        if ($ev.PSObject.Properties['model'] -and $ev.model) { $modeloReportado = $ev.model }
        if ($ev.PSObject.Properties['usage'] -and $ev.usage) { $tokenUsage = $ev.usage }
    }
}

if ($sucesso) {
    Move-Item -LiteralPath $parecerPart -Destination $parecerFinal -Force
} elseif (Test-Path -LiteralPath $parecerPart) {
    Move-Item -LiteralPath $parecerPart -Destination "$parecerFinal.falha" -Force
}
if (Test-Path -LiteralPath $rawPart) {
    Move-Item -LiteralPath $rawPart -Destination $rawFinal -Force
}
if (Test-Path -LiteralPath $errPart) {
    if ((Get-Item -LiteralPath $errPart).Length -gt 0) {
        Move-Item -LiteralPath $errPart -Destination $errFinal -Force
    } else {
        Remove-Item -LiteralPath $errPart -Force
    }
}

$comandoSan = "codex $argLine"
$comandoSan = $comandoSan.Replace($RepoRoot, '<repo>').Replace($env:USERPROFILE, '~')
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
    hash_parecer         = $(if (Test-Path -LiteralPath $parecerFinal) { Get-HashArquivo $parecerFinal } else { $null })
    hash_log             = $(if (Test-Path -LiteralPath $rawFinal) { Get-HashArquivo $rawFinal } else { $null })
}
[IO.File]::WriteAllText($registroPart, ($registro | ConvertTo-Json -Depth 6), $Utf8NoBom)
Move-Item -LiteralPath $registroPart -Destination $registroFinal -Force

Write-Output "registro: $registroFinal"
if ($sucesso) {
    Write-Output "parecer: $parecerFinal"
    exit 0
}
throw "execucao falhou (exit $exitCode); ver $errFinal e $registroFinal"
