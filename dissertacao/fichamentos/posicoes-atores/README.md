# Fichamento de fontes primárias: posições dos atores sobre a Caixa de Conversão

Material de trabalho para os capítulos de 1906 a 1914. Ficha o que os atores do
debate disseram, com citação direta e localização na fonte, a partir dos
Documentos Parlamentares (volumes de 1906 e de 1910) e de quatro diários da
Hemeroteca Digital. É produto do mapeamento descritivo (objeto 1). A ficha 8
registra a voz própria dos jornais como inventário, não como medida de posição
editorial (objeto 2).

Compila sozinho neste diretório:

    pdflatex main; bibtex main; pdflatex main; pdflatex main

Usa o preâmbulo e o `referencias.bib` da dissertação, mais `fontes-primarias.bib`
(os dois volumes parlamentares e 30 edições de jornal, com data, número e
identificador do objeto na Hemeroteca).

## Conferência mecânica das citações

Toda citação direta passa por `\tr[FONTE]{texto}` ou `\cit[FONTE]{texto}{referência}`.
O código da fonte não é impresso: `P:vol:pdf` (página do PDF dos Documentos
Parlamentares; a impressa é pdf - 6) ou `I:edição:página` (texto embutido da
Hemeroteca).

    uv run python dissertacao/fichamentos/posicoes-atores/confere_citacoes.py

O script gera `relatorio-conferencia-citacoes.md` e `conferencia-status.tex`, que
põe uma adaga, no PDF, nas citações aproximadas. Rodar antes de compilar. Regra do
projeto: citação que não casa é rejeitada, nunca corrigida.

Resultado em 01/10/2026: 120 citações, 69 literais, 51 aproximadas, 0 rejeitadas.
Uma citação foi retirada do texto por ficar abaixo do limiar (coluna de O Paiz de
21/03/1907 sobre Custódio Coelho). As aproximadas pedem conferência na imagem
antes de entrar no texto da dissertação.

## Origem

Resume `docs/mapeamento-atores/` (arquivos 00 a 05 e `posicoes_por_objeto.csv`),
onde estão as matrizes de posição por objeto e o detalhe de cada leitura.
