#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$SkillPath = Join-Path $RepoRoot '.claude\skills\parecer-codex\SKILL.md'

function Assert-Match([string]$Text, [string]$Pattern, [string]$Message) {
    if ($Text -notmatch $Pattern) { throw "ASSERT: $Message" }
}

if (-not (Test-Path -LiteralPath $SkillPath -PathType Leaf)) {
    throw "ASSERT: skill ausente: $SkillPath"
}

$content = Get-Content -LiteralPath $SkillPath -Raw -Encoding utf8
$frontmatter = [regex]::Match($content, '(?s)\A---\s*\r?\n(.*?)\r?\n---').Groups[1].Value
Assert-Match $frontmatter '(?m)^name:\s+parecer-codex\s*$' 'frontmatter deve declarar name parecer-codex'
Assert-Match $frontmatter '(?m)^description:\s+Use when\b' 'description deve começar com Use when'
Assert-Match $frontmatter '(?i)consult|revis|despach' 'description deve cobrir gatilhos de consulta, revisão ou despacho'
Assert-Match $frontmatter '(?i)codex' 'description deve nomear Codex'

$required = @(
    'classificar o n',
    'potencialmente relevante',
    'NUNCA invocar sem o ok',
    'parecer do Claude ANTES',
    '-PacoteIsolado',
    'scripts\invoca-codex.ps1',
    'parecer bruto',
    'editar arquivos de parecer',
    'implementador designado',
    'worktree fora do OneDrive'
)
foreach ($phrase in $required) {
    if ($content.IndexOf($phrase, [StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw "ASSERT: skill deve conter: $phrase"
    }
}

$wordCount = @($content -split '\s+' | Where-Object { $_ }).Count
if ($wordCount -gt 500) { throw "ASSERT: skill excede 500 palavras: $wordCount" }
Write-Output "PASS: parecer-codex skill ($wordCount palavras)"
