$ErrorActionPreference = 'Stop'

$raizDissertacao = $PSScriptRoot
$arquivosObrigatorios = @(
    'main.tex'
    'configuracao/preambulo.tex'
    'configuracao/metadados.tex'
    'configuracao/notas-rascunho.tex'
    'capitulos/00-introducao.tex'
    'capitulos/01-fontes-metodo.tex'
    'capitulos/02-horizonte-monetario.tex'
    'capitulos/03-criacao-1906.tex'
    'capitulos/04-operacao-1907-1910.tex'
    'capitulos/05-crise-1911-1914.tex'
    'capitulos/06-conclusao.tex'
    'apendices/construcao-corpus.tex'
    'bibliografia/referencias.bib'
    'notas/mapa-reaproveitamento.md'
    'notas/pendencias-documentais.md'
)

$erros = [System.Collections.Generic.List[string]]::new()

foreach ($arquivoRelativo in $arquivosObrigatorios) {
    $caminho = Join-Path $raizDissertacao $arquivoRelativo
    if (-not (Test-Path -LiteralPath $caminho -PathType Leaf)) {
        $erros.Add("Arquivo obrigatório ausente: $arquivoRelativo")
    }
}

$arquivosTextuais = Get-ChildItem -LiteralPath $raizDissertacao -Recurse -File |
    Where-Object { $_.Extension -in @('.tex', '.bib', '.md') }

$expressoesProibidas = @(
    [char]0x2014
    [char]0x2013
    'classificação holística constitui uma ferramenta robusta'
    'corpus definitivo de cinco periódicos'
    'Caixa foi criada a 12 dinheiros'
    'restauração do papelismo em 1914'
)

foreach ($arquivo in $arquivosTextuais) {
    $conteudo = Get-Content -LiteralPath $arquivo.FullName -Raw -Encoding UTF8
    foreach ($expressao in $expressoesProibidas) {
        if ($conteudo.IndexOf($expressao, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $relativo = $arquivo.FullName.Substring($raizDissertacao.Length).TrimStart('\', '/')
            $erros.Add("Expressão ou sinal proibido em ${relativo}: $expressao")
        }
    }
}

if ($erros.Count -gt 0) {
    $erros | ForEach-Object { Write-Error $_ }
    exit 1
}

function Invoke-LatexCommand {
    param(
        [Parameter(Mandatory)]
        [string]$Comando,

        [Parameter(Mandatory)]
        [string[]]$Argumentos
    )

    $preferenciaAnterior = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $saida = & $Comando @Argumentos 2>&1
        $codigoSaida = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $preferenciaAnterior
    }
    if ($codigoSaida -ne 0) {
        $saida | ForEach-Object { Write-Host $_ }
        throw "Falha ao executar: $Comando $($Argumentos -join ' ')"
    }
}

Push-Location $raizDissertacao
try {
    Invoke-LatexCommand -Comando 'pdflatex' -Argumentos @('-interaction=nonstopmode', '-halt-on-error', 'main.tex')
    Invoke-LatexCommand -Comando 'bibtex' -Argumentos @('main')
    Invoke-LatexCommand -Comando 'pdflatex' -Argumentos @('-interaction=nonstopmode', '-halt-on-error', 'main.tex')
    Invoke-LatexCommand -Comando 'pdflatex' -Argumentos @('-interaction=nonstopmode', '-halt-on-error', 'main.tex')

    $problemasLatex = Select-String -Path 'main.log' -Pattern @(
        'Citation.*undefined'
        'There were undefined references'
    )
    $problemasBibtex = Select-String -Path 'main.blg' -Pattern "I didn't find a database entry"

    if ($problemasLatex -or $problemasBibtex) {
        throw 'A compilação terminou com citações ou referências indefinidas.'
    }
}
finally {
    Pop-Location
}

Write-Host 'VERIFICAÇÃO CONCLUÍDA: rascunho compilável e sem violações detectadas.' -ForegroundColor Green
