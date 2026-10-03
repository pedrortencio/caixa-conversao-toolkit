# Anchor: fichamento padrão-ouro (sessão 2026-09-01)

## Missão
Produzir, com agentes Opus, fichas de leitura em LaTeX da literatura sobre o padrão-ouro
para o capítulo 2 da dissertação, revisar cada ficha contra o texto, fundir os .bib,
compilar `main.tex` e escrever `sintese.tex`. Pedro decide construto e interpretação.
Restrições: sem travessão em nenhum arquivo; nada de commit sem ordem do Pedro;
fichas em português; Fable orquestra, Opus ficha.

## Plano
`README.md` desta pasta (fila de chaves, partes, esforço, status) e `brief-agente.md`
(instrução de cada agente). Acervo: `Referencias Ivan/Padrão Ouro/` com `Internacional/`
e `_texto/` (texto extraído de todos os PDFs, 52 arquivos).

## Cursor
- Feito: acervo completo (Pedro trouxe Abreu, Eichengreen, Summerhill, Weller 2018,
  Topik, Flandreau-Zumer, Flores Zendejas, mais Flandreau-Flores Peaceful Conspiracy);
  texto extraído; skeleton LaTeX compila; brief e fila escritos.
- Em andamento: definir recorte dos cinco livros pelo sumário; disparar lote 1.
- Próxima ação ao retomar: ler `README.md` (coluna status) e `fichas/`; toda chave com
  `fichas/<chave>.tex` existente e status ainda `pronto` precisa de revisão e inclusão
  no `main.tex`; chaves sem arquivo precisam de agente. Não relançar agente para chave
  cujo `.tex` já existe.

## Estado em 2026-09-03 02:50
32 das 33 fichas entregues e no caderno; `main.pdf` com 182 páginas, 32 bibitems,
zero travessão, zero citação indefinida. Conferência mecânica de citações criada
(`confere_citacoes.py`, relatório em `relatorio-conferencia-citacoes.md`):
80 citações, 65 casadas, 15 com lacuna, 0 rejeitadas.
`almeida2010` REPROVADA (duas citações inexistentes na fonte), movida para
`quarentena/`, refação em voo. É a única que falta.
Depois disso: revisar conteúdo ficha a ficha e escrever `sintese.tex`.

As pendências que os agentes levantaram estão consolidadas em
`pendencias-do-fichamento.md`: divergências entre textos (Thornton em qual
escola), contradições internas dos próprios artigos, metadados a fechar, e o
achado metodológico de que Marinho (2021) atribui posição editorial a partir de
voz hospedada em três casos, que é material do capítulo 1.

## Trabalho em voo (histórico)
Histórico: lote 1 (2026-09-01 23h) e uma primeira tentativa do lote 2 (02/09 03h)
caíram por limite mensal de gasto da conta (HTTP 429). Sobreviveram 19 fichas .tex.

2026-09-02 21:40: limite reaberto (a própria sessão voltou a responder). Relançadas as
14 chaves que faltavam, todas em voo agora: topik1987, flandreauzumer2004, triner1996,
mollo1994, salomao2017, villela2001, gremaud1997, gambi2015, abreu2014, marinho2021,
taosalomao2020, almeida2010, dellapaolerataylor2001, hankeschuler2015.

Já gravadas (19): bordokydland1990, bordorockoff1996, bordoschwartz1994, eichengreen1996,
fergusonschularick2012, flandreauflores2012, flandreauflores2012io, floreszendejas2016,
fonsecamollo2012, franco1988, fritschfranco1992, germerouro, gontijo2014, marcondes1998,
meissner2005, obstfeldtaylor2003, summerhill2015, weller2015, weller2018.

Guarda: antes de relançar qualquer chave, verificar se `fichas/<chave>.tex` já existe.
Depois de cada lote: `uv run python .../verifica_fichas.py`, depois
`uv run python .../monta_caderno.py`, depois compilar.

## Invariantes
- Um agente por chave, modelo opus; recorte explícito para livros.
- Agente grava só `fichas/<chave>.tex` e `fichas/<chave>.bib`; o orquestrador funde no
  `bibliografia/referencias.bib` e descomenta o `\input` no `main.tex`.
- Compilar: `pdflatex main; bibtex main; pdflatex main; pdflatex main` na pasta.
- Para livros, a ficha abre com um parágrafo sobre o que o livro propõe antes do recorte.

## Último estado bom
`main.tex` compila (9 páginas, só a apresentação). Nenhuma ficha ainda. Nada commitado;
`dissertacao/fichamentos/` está untracked.

## Passos de retomada
1. Ler este arquivo e `README.md`.
2. `ls fichas/` e comparar com a fila.
3. Continuar do cursor.

<!-- anchor:tail -->

## Decisões
- 2026-09-01: seleção por compatibilidade com o capítulo; 12 textos do acervo do Ivan
  fora do escopo (teoria marxista do dinheiro, Gambi 2011/2019, etc.).
- 2026-09-01: estrutura do capítulo em quatro partes, com dobradiça sobre importação
  das categorias e comparação argentina ao fim.
