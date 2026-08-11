# Rascunho zero da dissertação

Este diretório contém um texto de trabalho da dissertação sobre o debate jornalístico acerca da Caixa de Conversão, entre 1906 e 1914. A estrutura foi mantida independente de uma classe institucional específica para facilitar a redação, a revisão e a futura migração para o modelo exigido pela FFLCH-USP.

## Compilação

No PowerShell, a partir deste diretório:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

O arquivo `configuracao/notas-rascunho.tex` controla a exibição dos marcadores editoriais. Use `\rascunhotrue` durante a redação e substitua por `\rascunhofalse` para gerar uma versão limpa.

## Organização

Os capítulos estão em `capitulos/`, o inventário do corpus em `apendices/`, a bibliografia em `bibliografia/` e as notas de trabalho em `notas/`. Os marcadores `\lacuna`, `\fonteaconferir`, `\interpretacaoprovisoria` e `\revisarbibliografia` identificam, respectivamente, lacunas documentais, referências primárias a conferir, interpretações ainda provisórias e pontos de revisão bibliográfica.

