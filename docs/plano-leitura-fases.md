# Plano de leitura estratificada para caracterização das fases

**Data:** 2026-07-28. **Estatuto:** rascunho para aprovação de Pedro. Não decide o
construto, não altera o codebook, não autoriza classificação. Implementa o
artefato 4 do protocolo de `contexto-debate-metodologico-mensuracao.md`, a amostra
metodológica estratificada, na perna de leitura das fontes.

**Insumos:** `contexto-bibliografia-caixa-conversao.md` (questões historiográficas,
seções 18 e 19), `codebook-fases.md` (esqueleto a preencher),
`contexto-debate-metodologico-mensuracao.md` (gate e critérios).

## 1. O que este plano existe para produzir

O codebook das fases 2 a 4 precisa sair da leitura das fontes e da historiografia,
não do prompt nem do que um modelo devolve. Um codebook derivado do prompt mediria
o que o modelo já supõe sobre o debate da Caixa, e a validação por κ contra códigos
humanos seria circular: o codificador humano estaria aplicando um padrão de origem
algorítmica.

O produto desta leitura é, por fase, um bloco com três partes:

1. o que cada lado (jornal, grupo, pessoa etc) defendia, com o objeto concreto do desacordo (taxa, lastro,
   emissão, conversibilidade, valorização, dívida externa);
2. o vocabulário de época atestado, verbatim, com citação localizada;
3. de três a cinco casos-limite, com o código que receberiam e a razão.

A parte 3 é o que distingue um codebook operacional de uma descrição. É ela que
sustenta o κ por fase.

## 2. A moldura amostral medida

Todos os números abaixo foram medidos em 2026-07-28 sobre os manifestos versionados.

**Censo de menções** (`dados/triagem/triagem_nome_*.csv`): 6.354 edições com ao
menos uma menção tolerante a ruído, de 11.959 edições no acervo. A menção pelo nome
não discrimina: atinge 53% do acervo.

**Intensidade por edição:** 54,3% das edições com menção têm exatamente uma
ocorrência e 82,0% têm no máximo duas. Apenas 264 edições, 4,2% das que têm menção,
acumulam cinco ocorrências ou mais.

**Amostra de peças já extraída** (`dados/triagem/amostra_para_rotular.csv`): 468
peças com status `keep`, estratificadas por jornal e ano entre 10 e 19 por célula,
com data, título, seção, forma e texto integral. Destas, 453 já foram rotuladas por
Pedro quanto ao registro.

| registro | peças |
|---|---|
| substantivo | 239 |
| operacional_rotina | 169 |
| incidental | 45 |
| em branco | 15 |

**As 239 peças substantivas, por forma:**

| forma | peças |
|---|---|
| notícia | 117 |
| artigo | 64 |
| editorial | 28 |
| telegrama | 20 |
| demais (tabela, lista, anúncio, outro) | 10 |

**As 239 peças substantivas, por fase e jornal:**

| fase | Correio da Manhã | Correio Paulistano | Gazeta de Notícias | O Paiz | total |
|---|---|---|---|---|---|
| F1 (1906) | 17 | 15 | 12 | 10 | 54 |
| F2 (1907-09) | 10 | 6 | 26 | 13 | 55 |
| F3 (1910-13) | 23 | 15 | 20 | 36 | 94 |
| F4 (1914) | 6 | 7 | 14 | 9 | 36 |

## 3. A constatação que governa o plano

O estimando declarado é posicionamento **editorial**. O material editorial
substantivo conhecido são 28 peças no total: 7 em F1, 3 em F2, 16 em F3 e 2 em F4.

Isso não inviabiliza a pesquisa, mas fixa três consequências que precisam de decisão
antes da leitura, não depois:

1. **A leitura começa pelas 28 editoriais.** São o material mais próximo do
   construto e já estão extraídas, datadas e com texto.
2. **Em F2 e F4 a caracterização não pode se apoiar só no editorial.** Com 3 e 2
   peças, qualquer generalização seria anedótica. Nessas fases a caracterização terá
   de vir também de artigo e notícia, e o codebook precisará dizer explicitamente
   como tratar a voz do jornal fora do editorial.
3. **A escassez pode ser do gênero ou da amostra.** As 28 saem de uma amostra de 468
   peças, não do censo. A leitura da camada 3 testa qual das duas explicações vale,
   e a resposta muda o desenho: se for da amostra, ampliar a extração resolve; se for
   do gênero, o estimando por edição-dia precisa ser reformulado.

O item 3 cabe a Pedro, pelo gate de responsabilidade. O plano é construído para
produzir a evidência que sustenta a decisão, não para antecipá-la.

## 4. As quatro camadas

### Camada 0, censo do material substantivo já disponível

Ler as 28 editoriais e as 64 artigos substantivos, 92 peças. Custo de amostragem
zero: estão extraídas, datadas e com texto no manifesto. Cobrem as quatro fases e os
quatro jornais.

Esta camada é censo, não amostra. Nenhuma inferência amostral depende dela.

### Camada 1, episódios comparados

As janelas cronológicas da seção 19 de `contexto-bibliografia-caixa-conversao.md`
que caem no recorte, lidas nos quatro jornais na mesma data, para comparar como o
mesmo evento é enquadrado:

| episódio | janela | por que importa |
|---|---|---|
| Convênio e criação | ago/1906 a dez/1906 | fase 1, já operacionalizada no piloto |
| Empréstimo de Paris | 1908 | concorrência financeira internacional e redução do monopólio Rothschild |
| Lei da taxa de 16d | dez/1910 | fase 3, mudança do objeto concreto do desacordo |
| Suspensão | ago/1914 | fase 4, onde o eixo pode deixar de discriminar |

A leitura simultânea dos quatro jornais na mesma janela é o que permite separar
posição editorial de repercussão de um mesmo despacho telegráfico.

### Camada 2, sorteio estratificado

Sorteio aleatório com semente registrada, do estrato substantivo, por fase e jornal,
nas células que as camadas 0 e 1 deixarem descobertas. Serve de contraprova: se a
caracterização construída a partir dos episódios não sobreviver às peças sorteadas,
ela estava enviesada pelo episódio.

### Camada 3, negativos e fronteira

Três alvos distintos:

1. peças rotuladas `operacional_rotina` e `incidental`, para fixar por escrito o que
   não conta como debate. A fronteira negativa entra no codebook;
2. edições com uma ou duas menções apenas, para confirmar que o estrato de baixa
   intensidade é mesmo cotação e balanço;
3. edições sem menção nenhuma, estratificadas por fase e jornal, para a auditoria de
   recall prevista na CLAUDE.md.

## 5. Proteção do conjunto de teste

Nenhuma peça lida nesta leitura entra no padrão-ouro de validação. O conjunto de
teste será sorteado depois, com semente própria, do complemento da moldura, isto é,
das peças que este plano não selecionou.

A razão é a mesma do item 1: um codebook construído lendo as peças X não pode ser
validado contra códigos humanos atribuídos às mesmas peças X. O κ resultante mediria
a consistência do leitor consigo mesmo.

O rótulo de registro já atribuído às 453 peças não contamina nada, porque distingue
substantivo de rotina, não posição. A leitura desta rodada é que contamina, e por
isso a seleção fica gravada em manifesto.

## 6. A ficha

Uma linha por peça lida, em `dados/leitura/fichas_leitura.csv`. As colunas de
identificação vêm pré-preenchidas pelo amostrador. As demais são preenchidas na
leitura.

**Identificação, pré-preenchida:** `item_id`, `camada`, `estrato`, `motivo_selecao`,
`jornal`, `data`, `source_identifier`, `page_number`, `forma`, `secao`, `titulo`.

**Preenchidas na leitura:**

| campo | conteúdo | por que existe |
|---|---|---|
| `data_masthead` | data lida no cabeçalho | não há mapa edição-data para 1907-14; a leitura o constrói |
| `voz` | editorial_do_jornal, assinado, reproduzido_terceiro, telegrama_agencia, discurso_parlamentar, indeterminado | critério 4 da lista de comparação: separar voz editorial de discurso reproduzido |
| `objeto_politica` | taxa, conversibilidade, lastro, emissao, valorizacao_cafe, divida_externa, outro | seção 18.1 do contexto bibliográfico; múltiplos separados por ponto e vírgula |
| `direcao_por_objeto` | por objeto: ortodoxo, expansionista, nao_aplica, nao_classificavel | substitui o veredito holístico na escala, ver seção 9 |
| `posicao_declarada` | o que a peça defende, em uma frase | insumo direto do bloco da fase |
| `argumento` | a justificativa mobilizada | seção 18.1 e 18.3 |
| `atores_nomeados` | pessoas, bancos, estados, instituições | seção 18.2 |
| `interesses_invocados` | a quem a peça atribui ganho ou perda | hipótese de heterogeneidade da elite cafeeira |
| `vocabulario_epoca` | termos verbatim, ponto e vírgula entre eles | **é o inventário lexical**, atestado e não inferido |
| `citacao_ancora` | trecho literal que sustenta a leitura | rastreabilidade até evidência verificável |
| `localizacao` | página e coluna | idem |
| `confianca` | 1 a 3 | onde cair para 1, há caso-limite |
| `dificuldade` | o que tornou a codificação difícil | **alimenta os casos-limite do codebook** |
| `dialogo_historiografia` | com que leitura a peça conversa ou colide | cruzamento previsto na seção 22 do contexto bibliográfico |
| `minutos` | tempo gasto na peça | mede a taxa que decide a viabilidade do D-Humano por censo, ver seção 9 |

Os campos `vocabulario_epoca` e `dificuldade` são os dois que o codebook consome
diretamente. Os demais sustentam o capítulo.

## 7. Ordem de trabalho

1. rodar `pipeline/triagem/amostra_leitura.py`, que gera a ficha com identificação
   pré-preenchida e grava o manifesto de seleção;
2. ler a camada 0 por fase, começando por F1, onde o bloco do piloto serve de
   controle: se a leitura de 1906 não reproduzir o bloco já validado, o instrumento
   de leitura é que está frouxo;
3. em paralelo, fichar a fila de leitura da seção 6 do contexto bibliográfico,
   começando por Abreu (2014), Oliveira e Silva (2001) e Saes (1981);
4. redigir o bloco de cada fase cruzando as duas pernas;
5. só então escrever o prompt, como tradução mecânica do bloco.

## 8. Dimensionamento

O amostrador rodou em 2026-07-28 com semente 20260728 e selecionou 185 peças: 92 na
camada 0, 67 na camada 1, 11 na camada 2 e 15 na camada 3. Todas as 16 células de
fase e jornal ficaram com 6 peças ou mais. A 5 a 10 minutos por peça, são de 8 a 15
horas para a camada 0 e de 15 a 31 horas para o conjunto. O `desenhos-concorrentes.md`
orça o D-Humano em 15 a 20 horas por semana, então o conjunto cabe em uma a duas
semanas e o tempo não é a restrição operativa.

## 9. Três decisões tomadas em 2026-07-28

**Ler o conjunto, não só a camada 0, e cronometrar.** A leitura tem dois produtos. Os
blocos do codebook saem das camadas 0 e 1, que são seleção intencional. A taxa de
minutos por peça só sai honesta com a camada 3 dentro, porque em produção as peças de
rotina também seriam lidas para serem descartadas, e medir só o substantivo produz
taxa otimista. Essa taxa é o que estreita a projeção do D-Humano por censo: a medida
pivô diz 3.054 a 3.758 edições substantivas, o que a 5 a 10 minutos por peça e 1 a 2
peças por edição custa entre 250 e 600 horas. A faixa é larga demais para decidir um
instrumento, e a leitura é o jeito barato de estreitá-la. A conversão de peça para
edição-dia usa o `source_identifier` da própria ficha.

**Não decidir agora sobre a escassez de editoriais, porque o teste está dentro da
camada 0.** A coluna `forma` não foi atribuída por Pedro: veio do `claude-sonnet-5`,
protocolo `recuperacao-artigo-visao 0.1.0`, conforme `relatorio-rotulagem-registro.md`.
As 28 editoriais são contagem de modelo com erro não medido, e há sinal de que o
rótulo é conservador: das peças que o modelo chamou de editorial, 28 de 28 foram
julgadas substantivas, sem nenhuma incidental ou de rotina. Isso aponta subdetecção,
com editorial escondido entre os 64 artigos e as 117 notícias. A escassez portanto tem
três explicações, do gênero, da amostra ou do rótulo, e o campo `voz` da ficha
distingue as três ao custo zero, porque as 64 peças já estão na camada 0. Se a
explicação for o rótulo, `forma` deixa de servir como estrato em qualquer desenho sem
correção, e isso atinge o artefato 4 inteiro.

**Registrar direção por objeto de política, não veredito na escala.** O contrato comum
de avaliação já exige que todos os desenhos emitam posição mapeável à escala, então a
escala como moeda de comparação está comprometida de qualquer modo. O que não está é a
escala como formato de codificação. Registrar veredito holístico por peça adota o
formato do D-Escala, o incumbente cujas fraquezas estão registradas: não separa voz,
não decompõe saliência, e o caso O Paiz 07834 mostrou atribuição ao jornal da posição
de uma carta publicada. Ancorar 185 leituras nesse formato antes do benchmark escolhe
o incumbente sem rodar a competição. A escala é derivável dos atributos, o caminho
inverso não existe, e o esforço de leitura é o mesmo. Ganho adicional: a leitura passa
a ser o primeiro teste de codificação humana no formato do D-Atributos e do
D-Extração, que o artefato 5 exigirá de qualquer maneira.
