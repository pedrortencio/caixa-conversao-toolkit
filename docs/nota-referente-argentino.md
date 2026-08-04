# A Caixa de Conversão argentina no corpus: referente, não ruído

**Escrito em:** 2026-07-31. **Motivo:** ao ler o piloto de catalogação eu
afirmei que as menções à Caixa argentina eram contaminação da amostra. Pedro
objetou que a seção de Buenos Aires pode estar discutindo indiretamente a
Caixa brasileira, e pediu investigação no contexto mais amplo. A objeção
procede. Esta nota registra a evidência, corrige dois erros de medida meus e
deixa a decisão de construto onde ela pertence.

## 1. A objeção procede, e a evidência é direta

Quatro peças, lidas na página, em que o caso argentino é o argumento dentro do
debate brasileiro.

**Correio da Manhã, 23/05/1906** (`per089842_1906_01776`, p. 1). Correspondente
no Prata traduz editorial de *La Prensa* contra o otimismo com o estoque de
ouro da Caixa argentina, e enquadra a tradução contra os defensores do Convênio
de Taubaté: "contra a opinião geral de toda a gente em Buchos Aires ha vozes
como esta de La Prensa, autorlsadissiuias, que quebram a harmonia optimista".
O alvo é a política brasileira, o material é argentino.

**Gazeta de Notícias, 1906** (`per103730_1906_00185`, p. 3). Peça longa que
constrói o argumento a favor da Caixa brasileira por analogia com a lei
argentina de 1899, citando Martinez e Lewandowski, comparando as duas
economias e o projeto chileno: "é licito acreditar-se que instituido, entre
nós, um apparelho comparavel á caixa de conversão argentina, produzirá elle os
mesmos effeitos salutares sobre a especulação".

**O Paiz, 1910** (`per178691_1910_09495`, p. 2), artigo assinado por Rodolpho
Abreu. Depois de discutir a organização da Caixa argentina, conclui: "E' o que
devemos querer, reformando a lei da nossa Caixa de Conversão, alargando-lhe a
esphera de liberdade". Argentina como precedente para reformar a lei
brasileira, em plena fase 3.

**O Paiz, 1910** (`per178691_1910_09337`, p. 5), telegrama de Buenos Aires. *El
Diário* comenta a reforma **brasileira**, a elevação da taxa para 16 dinheiros,
e prevê que o Congresso não a aprovará porque prejudicaria os produtores.
Imprensa estrangeira opinando sobre a decisão brasileira em discussão.

Excluir esse material por ser argentino removeria do corpus parte do debate.

## 2. Dois erros meus na primeira medida

**Erro 1, o marcador media a si mesmo.** Contei como argentina qualquer janela
com a raiz `argentin`, e cheguei a 9,9% das vizinhanças de menção. A expressão
que mais casava era "pesos argentinos", que aparece na **lista de moedas do
boletim diário de movimento da Caixa brasileira**, junto de libras, francos,
liras e marcos. É rotina operacional brasileira, e o que ela informa é que a
Caixa recebia ouro argentino, não que o jornal falasse da Argentina.

**Erro 2, fronteira de palavra.** O marcador `la nacion` casava dentro de
"Escola Nacional de Bellas-Artes". Dois dos oito casos que li vinham daí.

Medida corrigida, sobre as 9.939 janelas de menção do corpus triado:

| classe | janelas | % |
|---|---|---|
| marca argentina estrita | 365 | 3,7% |
| só a linha de moeda do boletim | 267 | 2,7% |
| nenhuma | 9.307 | 93,6% |

Por ano, a concentração é 1914 (7,5%), 1909 (4,5%), 1906 (4,4%), contra 1,3% em
1907. O pico de 1914 é a guerra e a crise cambial no Prata.

Medida em `pipeline/analise/referente_argentino.py`, manifesto em
`dados/analise/referente_argentino.csv`, reprodutível por
`uv run python pipeline/analise/referente_argentino.py`. Os falsos positivos
acima estão fixados como teste em `tests/test_referente_argentino.py`.

## 3. Tipologia, a partir da leitura de 20 janelas

Amostra aleatória com semente 20260731, lida na página.

1. **Caso argentino mobilizado no debate brasileiro.** As quatro peças da seção
   1. É debate brasileiro e entra no corpus sem ressalva.
2. **Imprensa argentina comentando a política brasileira.** O *El Diário* sobre
   a taxa de 16 dinheiros. Também é o debate, com a voz correspondente.
3. **Notícia estrangeira sobre a Caixa argentina.** Coluna de telegramas de
   Buenos Aires com o movimento da Caixa argentina no meio de duelo, congresso
   ferroviário e festas da independência (`per178691_1914_10818`,
   `per178691_1914_11013`). Não há voz do jornal brasileiro.
4. **Vizinhança sem relação.** "Los Alpes, de Buenos Aires" na lista de vapores
   entrados, ao lado do boletim da Caixa. Adjacência de coluna, não conteúdo.

No piloto de catalogação, que é amostra estratificada e não retrato do corpus,
os registros do Claude tocam material argentino em 10 das 48 janelas e os do
Codex em 3. A diferença entre os dois anotadores no mesmo material já indica
que a fronteira não é óbvia nem para leitor atento.

## 4. Por que uma regra determinística não resolve

Na peça do Correio da Manhã de 1906, o vínculo com o debate nacional está na
expressão que o OCR entregou como "paladinos do Cou-veniode T abate". Nenhuma
regra de nome casa isso com "Convênio de Taubaté". Um filtro determinístico
classificaria como estrangeira justamente a peça mais argumentativa da amostra.
O tipo 1 se distingue do tipo 3 pelo enquadramento, que é o que o OCR mais
corrompe e o que uma regra de superfície menos alcança.

## 5. Consequências para o instrumento

**Saliência.** Se o denominador conta menções, o tipo 3 infla a série. São
poucas, na ordem de 3% das janelas de menção, mas concentradas em 1914, onde
a inflação seria maior justamente na fase da suspensão do troco.

**Medida pivô.** As 3.054 a 3.758 peças estimadas não precisam ser revistas
para baixo por causa disso. O tipo 3 é minoria e os tipos 1 e 2 são debate.

**Prompt.** A saída não é cláusula de exclusão. É registrar o referente por
peça, e deixar a agregação decidir depois. Proponho a versão 0.2.0 com dois
campos novos: `referente` (`brasileira`, `argentina`, `ambas`, `outra`) e
`mobilizacao_no_debate_brasileiro` (`sim`, `nao`, `indeterminado`). Com eles a
série pode ser publicada nos dois recortes, e a decisão fica registrada peça a
peça em vez de embutida num filtro.

## 6. O que depende de você

1. **Aprovar ou recusar o prompt 0.2.0** com os dois campos. Se aprovar, o
   piloto das 48 janelas roda de novo com os dois anotadores, custo em
   assinatura e cerca de uma hora, e passa a registrar o referente. Exige
   entrada em `docs/decisoes.md`, porque prompt é instrumento de medição.
2. **Definir o estatuto do tipo 3** no corpus: dentro com marcação, para
   permitir as duas séries, ou fora com registro positivo da exclusão. Minha
   recomendação é dentro com marcação, porque exclusão sem marca é
   irrecuperável depois.
3. **Decidir se o tipo 2** (imprensa argentina sobre a política brasileira) tem
   voz própria no codebook. Hoje ele cairia em `reproduzido_terceiro`, que não
   distingue jornal estrangeiro de carta de leitor.

Nada disso foi executado. O prompt segue na versão 0.1.0 e o piloto continua
como está.
