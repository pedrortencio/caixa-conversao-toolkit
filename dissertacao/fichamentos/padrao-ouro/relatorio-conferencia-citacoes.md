# Conferência mecânica das citações das fichas

**Data:** 2026-09-03. **Instrumento:** `confere_citacoes.py`. **Custo de API: zero.**

Cada `\chave{texto}{página}` das fichas é normalizada (maiúsculas, acentos,
pontuação, hifenização de fim de linha) e procurada como substring literal no
texto extraído do PDF de origem. A regra é a do projeto: citação que não casa é
rejeitada, nunca corrigida.

## Vereditos

| veredito | significado |
|---|---|
| casada | substring literal da fonte normalizada |
| com lacuna | prefixo e sufixo casam e cobrem 90% ou mais das palavras, com material intercalado na fonte |
| rejeitada | o resto |

`com lacuna` não é aprovação. É pendência de conferência na imagem.

## Resultado da rodada de 03/09

Sobre 30 fichas e 80 citações: **65 casadas, 15 com lacuna, 0 rejeitadas (0,0%)**.

As quinze com lacuna têm três causas identificadas, todas de extração e nenhuma
de conteúdo: cabeçalho de página no meio do parágrafo, perda de ligadura (o texto
extraído traz `nancially` no lugar de `financially`), e elipse deliberada da
citação, caso de Hanke e Schuler.

O resultado partiu de 40% de rejeição aparente e caiu em três etapas, todas de
conserto do instrumento e do acervo, nenhuma de alteração de citação: leitura em
latin-1 dos textos em português, desfazimento da hifenização de fim de linha, e
reextração do artigo de Fonseca e Mollo.

## O que a conferência pegou

A primeira versão da ficha `almeida2010` trazia três citações. Duas não existem
em nenhum texto de Almeida do acervo, e a palavra `emissionistas` de uma delas
só aparece na monografia de Marinho (2021). As páginas citadas, 51, 52 e 66, não
cabem num artigo de 22 páginas. A ficha foi movida para `quarentena/` e refeita
por um agente novo, com instrução explícita de conferir cada citação no texto
antes de gravar e de usar `p. N do PDF` quando não houver paginação impressa.

O agente que produziu a versão reprovada foi interrompido no meio por limite de
gasto da conta, o que pode ter deixado um rascunho não revisado no disco. Isso
não altera o veredito: a ficha não era conferível e por isso não entrou.

## Três defeitos de extração corrigidos no acervo

1. **Meissner (2005)**, `_texto/...w9233.txt`: metade das linhas saía cifrada com
   deslocamento de três posições no ASCII, por codificação de fonte quebrada no
   PDF (`Hlqdxgl` para `Einaudi`). 963 de 2.010 linhas foram decifradas; o
   original está preservado no arquivo `.txt.orig` ao lado.
2. **Textos em português**: `pdftotext` grava em latin-1, e o leitor original da
   conferência os lia como UTF-8, destruindo todo acento. Antes da correção a
   taxa de rejeição aparente era de 40%.

3. **Fonseca e Mollo (2012)**: artigo em duas colunas, cujo texto o `pdftotext
   -layout` entregava com as colunas intercaladas linha a linha, o que reprovava
   citações corretas. A extração sem `-layout` preserva a ordem de leitura e as
   duas citações passaram a casar. O arquivo antigo ficou como `.txt.layout`.

## Limite conhecido do instrumento

A conferência compara a ficha com o **texto extraído**, não com a página. Em caso
de divergência, a página do PDF decide, não o `.txt`. Outros artigos em duas
colunas do acervo podem ter o mesmo defeito do item 3 sem que uma citação o tenha
revelado; a reextração sem `-layout` é o teste barato quando surgir suspeita.

A conferência valida a **literalidade** da citação, não a **fidelidade
interpretativa** da ficha. Uma ficha pode ter todas as citações casadas e ainda
assim atribuir ao autor tese que ele não sustenta. Essa leitura é do Pedro.
