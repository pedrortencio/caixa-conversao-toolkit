# Rascunho zero da dissertação

Este diretório contém um texto de trabalho da dissertação sobre o debate jornalístico acerca da Caixa de Conversão, entre 1906 e 1914. A estrutura foi mantida independente de uma classe institucional específica para facilitar a redação, a revisão e a futura migração para o modelo exigido pela FFLCH-USP.

## Compilação

No PowerShell, a partir deste diretório:

```powershell
.\verificar.ps1
```

O verificador confere os arquivos obrigatórios, as regras editoriais e as referências antes de produzir `main.pdf`. A compilação manual continua possível com a sequência `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.

O arquivo `configuracao/notas-rascunho.tex` controla a exibição dos marcadores editoriais. Use `\rascunhotrue` durante a redação e substitua por `\rascunhofalse` para gerar uma versão limpa.

## Organização

Os capítulos estão em `capitulos/`, a construção do corpus em `apendices/`, a bibliografia em `bibliografia/` e as notas de trabalho em `notas/`. Os marcadores `\lacuna`, `\fonteaconferir`, `\interpretacaoprovisoria` e `\revisarbibliografia` identificam, respectivamente, lacunas documentais, referências primárias a conferir, interpretações ainda provisórias e pontos de revisão bibliográfica.
