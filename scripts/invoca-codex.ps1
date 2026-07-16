#Requires -Version 5.1
<#
Invoca codex exec com proveniência registrada.
Spec: docs/superpowers/specs/2026-07-15-integracao-codex-design.md

A invocação usa System.Diagnostics.Process (não cmd redirects): o Workdir vai em
WorkingDirectory, o manifesto entra por stdin como bytes UTF-8 crus e a saída do Codex
é gravada num arquivo temporário de nome ascii. Assim nenhum caminho controlado pelo
usuário entra na linha de comando do cmd.exe, evitando quebra ou injeção por
metacaracteres, e os acentos do manifesto chegam intactos ao Codex.
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

function Test-PathContida([string]$Filho, [string]$Pai) {
    $f = [IO.Path]::GetFullPath($Filho).TrimEnd('\', '/')
    $p = [IO.Path]::GetFullPath($Pai).TrimEnd('\', '/')
    if ($f -eq $p) { return $true }
    $f.StartsWith($p + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)
}

function Get-GitOutput([string[]]$Arguments) {
    $output = @(& git -C $RepoRoot @Arguments)
    if ($LASTEXITCODE -ne 0) {
        throw "git falhou: git -C <repo> $($Arguments -join ' ')"
    }
    $output
}

# Lança "cmd /d /s /c "<exe> <args>"" via Process, com stdin/stdout/stderr redirecionados.
# O Codex é um shim .cmd do npm, por isso o launcher continua sendo o cmd.exe, mas nenhum
# caminho estranho vai na linha: Workdir vira WorkingDirectory e o manifesto entra por stdin.
function Invoke-CodexProcess {
    param(
        [Parameter(Mandatory = $true)][string]$Exe,
        [string[]]$Argumentos = @(),
        [byte[]]$StdinBytes,
        [string]$WorkingDirectory
    )
    $tokens = @($Exe) + $Argumentos
    $inner = ($tokens | ForEach-Object { ConvertTo-CmdArg $_ }) -join ' '
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $env:ComSpec
    $psi.Arguments = '/d /s /c "' + $inner + '"'
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = $Utf8NoBom
    $psi.StandardErrorEncoding = $Utf8NoBom
    if ($WorkingDirectory) { $psi.WorkingDirectory = $WorkingDirectory }
    $proc = [System.Diagnostics.Process]::Start($psi)
    # Drena stdout/stderr de forma assíncrona ANTES de escrever o stdin, para não travar
    # caso o filho comece a emitir saída enquanto ainda mandamos o manifesto.
    $outTask = $proc.StandardOutput.ReadToEndAsync()
    $errTask = $proc.StandardError.ReadToEndAsync()
    try {
        if ($StdinBytes -and $StdinBytes.Length -gt 0) {
            $proc.StandardInput.BaseStream.Write($StdinBytes, 0, $StdinBytes.Length)
            $proc.StandardInput.BaseStream.Flush()
        }
    } finally {
        $proc.StandardInput.Close()
    }
    $proc.WaitForExit()
    [pscustomobject]@{
        ExitCode = $proc.ExitCode
        StdOut   = $outTask.Result
        StdErr   = $errTask.Result
    }
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

# Isolamento verificado, não autodeclarado: -PacoteIsolado exige Workdir fora do repo.
$workdirDentroRepo = Test-PathContida $Workdir $RepoRoot
if ($PacoteIsolado -and $workdirDentroRepo) {
    throw "PacoteIsolado exige Workdir fora do repositorio; Workdir atual esta dentro de <repo>"
}
$workdirIsolado = [bool]$PacoteIsolado -and (-not $workdirDentroRepo)

$codexInfo = Get-Command $CodexCommand -ErrorAction Stop | Select-Object -First 1
$CodexResolved = if ($codexInfo.Path) { $codexInfo.Path } else { $codexInfo.Source }
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

# Snapshot do estado sujo EXCLUINDO colaboracao/, que só guarda a papelada deste fluxo
# (manifestos, pareceres, registros) e poluiria o "estado sujo" do corpus/codebook.
$excluiColab = ':(exclude)colaboracao/'
$commit = (Get-GitOutput @('rev-parse', 'HEAD') | Select-Object -First 1).Trim()
$statusLines = @(Get-GitOutput @('status', '--porcelain=v1', '--untracked-files=all', '--', '.', $excluiColab))
$porcelain = $statusLines -join "`n"
$hashDiff = $null
if ($statusLines.Count -gt 0) {
    $snapshotTmp = Join-Path $env:TEMP "invoca-codex-snapshot-$([guid]::NewGuid().ToString('N')).txt"
    try {
        $snapshot = New-Object System.Collections.Generic.List[string]
        $snapshot.Add('STATUS')
        foreach ($line in $statusLines) { $snapshot.Add($line) }
        $snapshot.Add('DIFF_BINARY_HEAD')
        foreach ($line in @(Get-GitOutput @('diff', '--binary', 'HEAD', '--', '.', $excluiColab))) { $snapshot.Add($line) }
        $snapshot.Add('UNTRACKED_SHA256')
        $untracked = @(Get-GitOutput @('-c', 'core.quotepath=false', 'ls-files', '--others', '--exclude-standard', '--', '.', $excluiColab) | Sort-Object)
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

# attempt = número da tentativa desta tarefa (contagem histórica), independente da
# desambiguação de colisão de run_id, que usa um sufixo próprio.
$attempt = @(Get-ChildItem -LiteralPath $registrosDir -Filter "$TaskId--*.json" -ErrorAction SilentlyContinue).Count + 1
$runBase = '{0}-{1}' -f $inicio.ToString('yyyyMMddTHHmmssfff'), $hashManifesto.Substring(0, 8)
$runId = $runBase
$sufixoColisao = 0
# Reserva atômica do slot: cria o registro parcial (.part, gitignored) com CreateNew, que
# falha se já existir. Fecha a janela de corrida entre "checar" e "escrever" de duas
# invocações simultâneas, e nenhum .json final chega a existir vazio (um crash deixa só um
# .part, ignorado pelo git, nunca um registro vazio commitável).
while ($true) {
    $registroFinal = Join-Path $registrosDir "$TaskId--$runId.json"
    $registroPart = "$registroFinal.part"
    try {
        $fs = [IO.File]::Open($registroPart, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        $fs.Close()
        break
    } catch [IO.IOException] {
        $sufixoColisao++
        $runId = "$runBase-$sufixoColisao"
    }
}

# Parecer com run_id no nome: cada execução preserva o seu, nunca sobrescreve o anterior.
$parecerFinal = Join-Path $parecerDir "$TaskId$SufixoParecer--$runId.md"
$parecerRelativo = "colaboracao/pareceres/$TaskId$SufixoParecer--$runId.md"
$rawFinal = Join-Path $rawDir "$TaskId--$runId.jsonl"
$errFinal = Join-Path $rawDir "$TaskId--$runId.err.txt"
$parecerFalha = Join-Path $rawDir "$TaskId--$runId.parecer-falha.md"
# Saída do Codex num temp de nome ascii, fora de qualquer caminho com metacaracteres.
$saidaTmp = Join-Path $env:TEMP "invoca-codex-saida-$runId.txt"

$registroEscrito = $false
try {
    $versaoInfo = Invoke-CodexProcess -Exe $CodexResolved -Argumentos @('--version')
    if ($versaoInfo.ExitCode -ne 0) { throw "Nao foi possivel obter a versao do Codex" }
    $versaoCli = ($versaoInfo.StdOut -split "`r?`n" | Where-Object { $_ } | Select-Object -First 1)
    if ($versaoCli) { $versaoCli = $versaoCli.Trim() }

    $codexArgs = @(
        'exec', '-',
        '--ignore-user-config',
        '--ephemeral',
        '--sandbox', 'read-only',
        '-m', $Modelo,
        '-c', "model_reasoning_effort=$Effort",
        '--color', 'never',
        '--json',
        '--output-last-message', $saidaTmp
    )
    if ($PacoteIsolado) { $codexArgs += '--skip-git-repo-check' }

    $stdinBytes = [IO.File]::ReadAllBytes($Manifesto)
    $exec = Invoke-CodexProcess -Exe $CodexResolved -Argumentos $codexArgs -StdinBytes $stdinBytes -WorkingDirectory $Workdir
    $exitCode = $exec.ExitCode
    $fim = Get-Date
    $sucesso = ($exitCode -eq 0) -and (Test-Path -LiteralPath $saidaTmp -PathType Leaf)

    # Log bruto (gitignored) sempre gravado para diagnóstico.
    [IO.File]::WriteAllText($rawFinal, $exec.StdOut, $Utf8NoBom)
    if (-not [string]::IsNullOrEmpty($exec.StdErr)) {
        [IO.File]::WriteAllText($errFinal, $exec.StdErr, $Utf8NoBom)
    }

    $modeloReportado = $null
    $sessaoCodex = $null
    $tokenUsage = $null
    foreach ($linha in ($exec.StdOut -split "`r?`n")) {
        if ([string]::IsNullOrWhiteSpace($linha)) { continue }
        $ev = $null
        try { $ev = $linha | ConvertFrom-Json } catch { continue }
        if ($null -eq $ev) { continue }
        if ($ev.PSObject.Properties['thread_id'] -and $ev.thread_id) { $sessaoCodex = $ev.thread_id }
        if ($ev.PSObject.Properties['model'] -and $ev.model) { $modeloReportado = $ev.model }
        if ($ev.PSObject.Properties['item'] -and $ev.item -and $ev.item.PSObject.Properties['model'] -and $ev.item.model) { $modeloReportado = $ev.item.model }
        if ($ev.PSObject.Properties['usage'] -and $ev.usage) { $tokenUsage = $ev.usage }
    }

    if ($sucesso) {
        Move-Item -LiteralPath $saidaTmp -Destination $parecerFinal -Force
    } elseif (Test-Path -LiteralPath $saidaTmp) {
        Move-Item -LiteralPath $saidaTmp -Destination $parecerFalha -Force
    }

    $comandoSan = "codex $(($codexArgs | ForEach-Object { ConvertTo-CmdArg $_ }) -join ' ')"
    $comandoSan = $comandoSan.Replace($saidaTmp, '<saida>').Replace($env:USERPROFILE, '~')
    $registro = [ordered]@{
        task_id              = $TaskId
        run_id               = $runId
        attempt              = $attempt
        status               = $(if ($sucesso) { 'sucesso' } else { 'falha' })
        modelo_solicitado    = $Modelo
        modelo_reportado     = $modeloReportado
        effort_solicitado    = $Effort
        versao_cli           = $versaoCli
        sessao_codex         = $sessaoCodex
        hash_manifesto       = $hashManifesto
        commit_repo          = $commit
        git_status_porcelain = $porcelain
        hash_diff            = $hashDiff
        workdir_isolado      = $workdirIsolado
        parecer              = $(if ($sucesso) { $parecerRelativo } else { $null })
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
    $registroEscrito = $true
} finally {
    Remove-Item -LiteralPath $saidaTmp -Force -ErrorAction SilentlyContinue
    if (-not $registroEscrito) {
        # Falha antes de gravar o registro: libera o slot reservado (.part); nenhum .json foi criado.
        Remove-Item -LiteralPath $registroPart -Force -ErrorAction SilentlyContinue
    }
}

Write-Output "registro: $registroFinal"
if ($sucesso) {
    Write-Output "parecer: $parecerFinal"
    exit 0
}
throw "execucao falhou (exit $exitCode); ver $errFinal e $registroFinal"
