# O credor externo no debate sobre a Caixa de Conversão

**Feito em:** 2026-08-03, revisto no mesmo dia. **Custo:** US$ 1,27 de API na
camada de leitura por imagem. **Estatuto:** mapeamento descritivo, o objeto 1.
Não atribui posição a jornal, não é escala, não é estimativa.

## Como ler as citações deste documento

Cada citação passou por duas conferências mecânicas, que respondem perguntas
diferentes.

A primeira é a de sempre, por `pipeline/analise/verifica_citacoes.py`: a linha
tem de ser substring literal do OCR da fonte, depois de normalizada. **As 36
citações passam.** Ela garante que a linha não foi inventada. Ela não garante
que o OCR corresponda à página impressa, e é aí que estava o problema desta
primeira versão do relatório: `quando recebeu 111:1 lelcgraiimia de aos-sos
banqueiros em Londres` é uma citação aprovada pela conferência e inutilizável
num capítulo.

A segunda é nova, por `pipeline/analise/confere_citacao_imagem.py`: cada
passagem foi lida **na imagem do scan**, duas vezes, em chamadas separadas ao
Claude Sonnet 5 (visão), e as duas leituras foram confrontadas entre si e contra
o OCR. Os vereditos, sobre 36 citações:

| veredito | n | o que significa |
|---|---|---|
| `estavel` | 23 | as duas leituras coincidiram letra a letra |
| `instavel` | 11 | as duas leituras discordam, quase sempre de uma palavra |
| `divergente_do_ocr` | 2 | a leitura de imagem se afastou da passagem do OCR |

**No corpo do texto abaixo, uso a leitura de imagem quando ela é `estavel` e
mantenho a forma do OCR quando não é.** Toda citação `instavel` ou
`divergente_do_ocr` aparece marcada, com a palavra em disputa nomeada. As duas
formas convivem no manifesto: `citacao_verbatim` continua sendo o OCR literal,
que é o que a conferência de substring precisa para funcionar, e as leituras de
imagem entram em arquivo separado.

**Nada disso é conferência humana.** Duas leituras do mesmo modelo não são dois
anotadores, e erro correlacionado atravessa as duas. A seção 6 mostra um caso em
que isso aconteceu, e ele é justamente o caso que motivou a varredura. A coluna
`conferido_na_imagem` do manifesto continua em `nao` nas 36. O que a camada nova
faz é trocar "conferir 36 citações na página" por "conferir 13 primeiro".

Manifestos: `dados/analise/mencoes_credor_externo.csv` (curadoria e OCR) e
`dados/analise/citacoes_conferidas_imagem.csv` (as duas leituras e o veredito).

## 1. O achado que reorganiza a busca

O credor externo aparece muito mais **por cargo e por perífrase** do que por
nome.

Nas 8.331 páginas que mencionam a Caixa:

| forma de designação | páginas |
|---|---|
| nomeia um Rothschild | 170 |
| usa perífrase ou cargo | 456 |
| usa perífrase de confiança alta | 214 |
| tem as duas coisas | 38 |
| **designa sem nomear** | **418** |

A expressão isolada mais frequente não é um nome, é um cargo: `agentes
financeiros`, com 125 ocorrências, sendo 16 delas coladas pelo OCR como
`agentesfinanceiros`. Uma medida que conte apenas nome próprio perde essas 418
páginas, e perde por cima da perda que o OCR já impõe: a grafia limpa
`rothschild` cobre só 48,6% das ocorrências do nome.

O caso que motivou a varredura é de 1906. A Gazeta de Notícias, comentando a
aprovação do projeto por 115 votos contra 25, escreve que os deputados
favoráveis são indiferentes

> ás opiniões do reidos banqueiros londrinos

O sujeito da frase é Rothschild e o nome não está lá. O OCR colou "rei" e "dos"
na quebra de linha, de modo que nem a busca por "rei dos banqueiros" casaria sem
tolerar a colagem. As duas coisas entraram como teste de regressão.

**Esta citação é a que mais precisa do seu olho, e a seção 6 explica por quê.**
As duas leituras de imagem devolveram `ás opiniões dos banqueiros londrinos`,
sem o "rei". Se elas estiverem certas, a metáfora que dá nome ao achado não está
na página. Se estiverem erradas, e o `reidos` do OCR sugere que estão, o modelo
engoliu a mesma palavra duas vezes.

## 2. As menções, por tema

### 2.1 A autoridade do credor sobre o debate interno

A mesma peça da Gazeta de 1906 atribui a queda dos títulos ao

> o prestigio dos banqueiros directores da grande banca do jogo universal

e recusa que caiba a eles arbitrar o preço da dívida brasileira. A linha que
registra essa recusa é a mais danificada do conjunto, e o OCR traz

> banqueiros dearbitros de cotações dosnossos titulos

`divergente_do_ocr`: as duas leituras de imagem escaparam para a oração
seguinte, que fala do Banco do Brasil como árbitro da taxa cambial. O trecho
impresso ainda não está estabelecido, e a leitura do sentido depende dele.

O texto liga o banqueiro externo ao diretor da carteira de câmbio do Banco do
Brasil, ao acusar os adversários de irem

> aninhar no exclusivo patriotismo dos banqueiros de Londres e do director da
> carteira de cambio do Banco do Brasil

Quatro anos depois, O Paiz faz o movimento inverso e usa o credor como fonte de
legitimidade para a política do governo:

> Dizem-nos que os nossos banqueiros em Londres consideram a providencia
> adoptada

Em 1913, o Correio da Manhã relata a sessão do Senado em que Pinheiro Machado
usa um telegrama do credor como arma contra Bulhões, lembrando de quando ele

> quando recebeu um telegramma de seus banqueiros em Londres

`instavel`: uma leitura traz "um telegramma", a outra "uma telegramma", e o OCR
tem `aos-sos` onde as duas leram "seus", o que sugere "nossos". Duas falas
adiante, na mesma sessão, aparece o conteúdo do telegrama:

> Bello documento em que aquelles banqueiros davam parabens a v. ex. pela
> situação lisonjeira do paiz

E em 1914, no Correio Paulistano, Bulhões se defende invocando o mesmo credor a
seu favor, dizendo que a elevação da taxa em 1910

> essa elevação obedeceu á força natural do paiz, que então se achava em phase
> de extraordinária prosperidade, como affirmou o próprio sr. Rotschild

O padrão é constante nos nove anos: os dois lados citam o banqueiro como
autoridade, e a divergência é sobre o que ele teria dito.

### 2.2 A posição declarada do credor

A entrevista de Serzedello Corrêa na volta da Europa, na Gazeta de 1907, anuncia
na chamada:

> Os Srs. Rothschild manifestam as suas impressões sobre a nossa política
> economico-financeira

O Retrospecto Commercial do Jornal do Commercio de 1906 transcreve as cartas
recebidas por Custódio Coelho, diretor da carteira de câmbio, e registra que ele

> recebera este dos Srs. Baring Brothers e N. M. Rothschild & Sons

com o fecho

> Seus muito sinceros—N. M. Rothschild & Sons.

O travessão aí é do impresso de 1906, confirmado nas duas leituras de imagem, e
não meu.

O Retrospecto de 1907 traz a formulação mais precisa do conjunto, e é a que
separa as duas coisas que o eixo do construto precisa distinguir:

> os quaes sempre negaram apoio á temeraria operação do Convenio ; mas não
> negaram nunca amparo ao credito do Brasil

Oposição ao Convênio de Taubaté não é hostilidade ao crédito soberano. O
Retrospecto vive fora do censo, porque o Jornal do Commercio não está no acervo
digital recuperável.

### 2.3 A recusa do empréstimo da valorização

Duas fontes independentes registram o mesmo fato. A Gazeta de Notícias, em
fevereiro de 1907, fala da notícia que alarmava a praça, a recusa dos

> poderosos banqueiros londrinos de promoverem ou tomarem parte no emprestimo
> dos 5 milhões esterlinos

`instavel`: a segunda leitura começa a passagem mais adiante, em "promoverem", e
perde a designação. A primeira leitura é a que cobre o trecho pedido.

E o Retrospecto do Jornal do Commercio, no balanço do mesmo ano:

> Embora conhecida a opinião desfavoravel dos banqueiros Rothchild, o Governo
> tentou junto delles um emprestimo e obteve... reiteração de formal recusa para
> o fim aleatorio.

O empréstimo acabou lançado em outubro de 1907 pelos mesmos banqueiros. É o par
recusa e crédito que a frase do item anterior resume.

### 2.4 Onde fica o ouro, e o episódio de 1911

Em 1908, O Paiz já põe a questão em termos doutrinários, três anos antes de ela
virar decisão. O OCR traz

> Dir-se-ha que e indiffe-rente o governo ter o ouro aqui no palaciodourado da
> avenida, ou tel-o em londrescom os nossos agentes financeiros

`divergente_do_ocr`, e este é o caso em que o OCR é a testemunha melhor. Uma
leitura de imagem devolveu "aqui no cofre" e a outra "aqui no palacio", as duas
perdendo "dourado da avenida". O palácio dourado da avenida é a ironia da frase,
e ela some nas duas leituras. Uso o OCR aqui de propósito.

Em 1911 o governo decide. O Paiz traz a versão mais completa:

> está resolvido a transferir para a casa dos Srs. Rothschilds and Sons, nossos
> antigos banqueiros em Londres, os depositos ouro da Caixa de Conversão

`instavel` numa palavra: o OCR tem `os deposito? ouro`, uma leitura preservou o
ponto de interrogação do scan e a outra leu "depositos".

com o preço declarado:

> Os juros que aquelles banqueiros pagarão ao governo pelos depositos serão de
> 2 1|2 o|o ao anno e destinados ao reforço do fundo de garantia

O Correio Paulistano reproduz a objeção do Correio da Noite, que

> extranha a resolução, que se attribue ao governo, de transferir aos banqueiros
> Rothschild os depositos da Caixa de Conversão, com os juros de 2 e meio por
> cento

E o Correio da Manhã ataca pelo direito, com o argumento de que o ouro é de
particulares e o governo

> não pôde, por outro, dispôr a seu bel prazer, da fortuna particular,
> negociando com ella

sobre um juro

> que desde já foi promettido pelos banqueiros inglezes

A Gazeta de Notícias, no mesmo ano, descreve o mecanismo pelo qual o lastro da
Caixa vira remessa ao credor:

> o Thesouro Nacional remetterá para os Srs. N. M. Rothschild and Sons, em
> Londres, £ 1.000.000, em espécie. Esse ouro será retirado hoje da Caixa de
> Conversão pelo Thesouro Federal, que entregará á mesma Caixa, para esse fim,
> 15.000:000$, em notas conversíveis

`instavel` na preposição, "remetterá para os Srs." contra "remetterá aos Srs.".
O valor, que o OCR entregava como `S. i.ooo.ooo`, as duas leituras leem como
£ 1.000.000.

Este é o feixe mais denso do material. Quatro jornais tratam do mesmo ato em
1911, e a discussão é sobre a natureza jurídica do depósito, não sobre a taxa.

### 2.5 A remessa como sinal da taxa de facto

Em 1910, a mesma peça sai na Gazeta de Notícias e no Correio da Manhã. A Gazeta:

> aos seus e aos nossos agentes financeiros em Londres, os Srs. Rotschilds. Esse
> facto, em toda a sua singeleza, indica que o Banco do Brasil adoptou
> officialmente a taxa de 15 d.

O Correio da Manhã, com outro OCR e o mesmo texto:

> aos nossos agentes financeiros em Londres, os srs. Rothschilds

O argumento é que a remessa de um milhão esterlino tirado da Caixa revela a taxa
real, contra o discurso oficial. Registro de método: **esta é uma peça só, e
contá-la duas vezes atribuiria a dois jornais a mesma opinião**. É o caso que a
regra de deduplicação existe para tratar.

### 2.6 A tutela externa como acusação

O Correio da Manhã de 1910, ao narrar a manobra de Bulhões para permanecer no
ministério:

> Chegaram a propalar esses intimos que Rothsohild havia recommendado ao sr.
> Hermes á continuação do sr. Bulhões

`instavel`: uma leitura traz "esses intimos", a outra "esses intuitos". O OCR
tem `inti-nios`, e o período anterior fala dos "íntimos, que lhe recebiam as
confidências", o que favorece "íntimos".

A forma importa: o jornal relata um boato atribuído aos íntimos do ministro, não
afirma o fato. O campo `voz` do codebook existe exatamente para não transformar
isso em posição do jornal.

Em 1913, o mesmo Correio da Manhã, relatando o Senado, põe a figura do outro
lado, com a oposição ao projeto vindo

> da opposição acerba movida por elle Rodrigues Alves, diga-se a verdade, alli
> dos próprios srs. Rotschild

`instavel`, e é a pior discordância do conjunto. A primeira leitura traz
"acerba", que casa com o `ncerba` do OCR; a segunda desandou para "nem por isso
deixaram de", que não casa com nada. A passagem está sendo lida em voz alta a
partir de uma carta, o que soma uma camada de voz sobre a outra.

### 2.7 A quebra do padrão como calote

O argumento doutrinário mais forte do conjunto está em O Paiz de 1912, que
constrói a analogia entre desvalorizar a moeda e reduzir o valor devido aos
credores, e conclui:

> Que diriam de tal acto? Pois a quebra do padrão, sem tirar nem pòr, é a mesma
> coisa.

Isso liga diretamente o eixo do construto, valorização contra estabilidade a
taxa nova, ao vínculo com o credor externo. Quem defende a volta ao par legal
está defendendo, no mesmo gesto, o portador do título.

### 2.8 A genealogia da dívida

O Paiz de 1913 traça a linha do funding de 1898 até a Caixa:

> operação chamada do Funding Loan,

> combinada com a casa Rotschild

As duas linhas são contíguas na página impressa e entram como citações separadas
porque o OCR intercala as duas colunas da página, e não existe span contíguo que
junte as duas. A segunda é a que carrega o credor, e a primeira versão deste
relatório citava só a primeira.

Na Câmara de 1910, em sessão relatada por O Paiz, Galeão Carvalhal recorre à
mesma memória:

> tantos abalos, que foi preciso fazer concordata com os nossos credores

E em 1914 a Gazeta ainda registra que a remessa de ouro do momento se destina a

> Essa importancia se destina a pagamentos decorrentes do antigo funding-loan

Dezesseis anos depois, o funding continua sendo o horizonte da política
monetária.

### 2.9 O crédito soberano e o protocolo com o credor

Em 1908, O Paiz registra que Campista

> recebeu telegramma dos nos-sos banqueiros em Londres, communicando que o
> emprestimo de libras 3.000.000, por antecipação de receita, foi ante-hontem
> lançado naquella praça com exito extraordinario

`instavel` em duas palavras, e cito a segunda leitura inteira. A primeira traz
"dos seus banqueiros" e "fora ante-hontem", a segunda "dos nos-sos banqueiros" e
"foi ante-hontem". O OCR tem `nos-sus`, que favorece "nossos", e `fora`, que
favorece a primeira. O possessivo importa, porque "nossos banqueiros" é a forma
de designação que a varredura de perífrase persegue.

Em 1909, o jornal transcreve na íntegra o telegrama dos Rothschild a Campista na
saída do ministério. A designação:

> recebeu dos nossos agentes financeiros em Londres, Mrs. Rotschild and Sons, o
> seguinte telegramma

E o telegrama:

> Agradecemos muito sinceramente a V. Ex. o seu amavel telegramma

Em 1914, a troca de ministro da Fazenda é comunicada ao credor antes de mais
nada:

> Barroso telegrapharam hontem aos srs. N. M. Rothschild and Sons, agentes
> financeiros do Brasil na Europa

`instavel` só na cauda: a segunda leitura continua em "o pronto reembolso", que a
primeira não vê.

### 2.10 A guerra, 1914

O registro muda de tom com a guerra. O Correio da Manhã:

> banqueiros estrangeiros não estão em guerra. Contra nós, para nos arrancar
> couro e cabello

E O Paiz justifica a suspensão do troco perante o credor:

> não pôde e não deve abalar o seu credito junto aos nossos credores exter-nos

## 3. O que a varredura ensinou sobre a própria busca

**Contar nome próprio subestima o ator por duas vias somadas.** A primeira é o
OCR, que reparte `rothschild` em 126 grafias. A segunda é a língua, que designa o
credor por cargo (`agentes financeiros`), por praça (`banqueiros londrinos`), por
relação (`nossos credores`) e por metáfora (`rei dos banqueiros`, `grande banca do
jogo universal`). A segunda perda é maior que a primeira: 418 páginas designam
sem nomear, contra 132 que nomeiam sem designar.

**O OCR cola palavras na quebra de linha, e isso derruba padrão com espaço
obrigatório.** `reidos banqueiros`, `agentesfinanceiros`, `casabancaria`,
`pracade londres`, `praca delondres`. Os padrões passaram a aceitar espaço
opcional, e a primeira versão, que exigia espaço, não achava o único caso que
justificava a varredura.

**Padrão largo não é padrão.** A primeira rodada usava `mercado de` e devolveu
2.312 ocorrências, quase todas mercado de café e mercado de câmbio. Virou
`mercado ingles`, `mercado de londres`, `mercado europeu`, e o total caiu para
85. O padrão descartado está registrado na justificativa da linha corrigida.

**Sete das minhas transcrições estavam erradas** e o conferidor mecânico as
recusou. O caso exemplar: eu li `indifferente` onde o OCR tem `indiffe-rente`. Se
a conferência não existisse, uma citação levemente higienizada teria entrado no
relatório com aparência de fidelidade.

**Recall é desconhecido e não dá para estimar por dentro.** Não existe lista
fechada das formas que a língua de 1906 usava para dizer credor. A varredura
garante piso, nunca censo. O modo de medir o teto seria ler uma amostra de
páginas sem nenhum casamento e contar quantas falam do credor assim mesmo, e isso
não foi feito.

## 4. Cinco citações que a curadoria tinha cortado curto demais

Além do ruído de OCR, a primeira versão tinha um defeito de recorte: citações
que paravam antes da designação do credor, e por isso não sustentavam sozinhas o
tema sob o qual estavam listadas.

| citação | o que faltava |
|---|---|
| `gn1910-taxa` | parava em "adoptou officialmente a taxa de 15 d.", sem os "agentes financeiros em Londres" |
| `gn1911-remessa` | começava no ouro já retirado, sem o destinatário nomeado |
| `op1909-telegrama` | trazia o telegrama sem a linha que diz de quem ele é |
| `op1913-funding` | trazia "operação chamada do Funding Loan" sem "combinada com a casa Rotschild" |
| `cm1913-parabens` | anunciava o telegrama sem mostrar o que ele dizia |

As três primeiras foram estendidas dentro da mesma frase impressa. As duas
últimas viraram citação nova, porque o OCR intercala colunas num caso e porque
há duas falas de permeio no outro. O manifesto passou de 33 para 36 linhas, e as
36 continuam passando na conferência de substring.

## 5. O silêncio parlamentar continua de pé

Nos dois volumes de *Documentos Parlamentares* sobre a Caixa, 1.152 páginas,
Rothschild, Speyer, Baring, Schröder e Crédit Lyonnais somam **zero menção pelo
nome**. A varredura de perífrase ainda não foi rodada sobre esses volumes, e essa
é a próxima checagem óbvia: se o plenário também designar o credor por cargo, o
silêncio some e vira outra coisa.

## 6. O que a leitura por imagem custou aprender

**Campo aberto convida invenção.** A primeira versão do conferidor pedia, junto
da transcrição, o "contexto em volta" de cada passagem. As transcrições saíram
boas e os contextos saíram confabulados: parágrafos inteiros, plausíveis, em
português de época, ausentes da página. Num caso o modelo devolveu como contexto
uma reconstrução de página inteira, com números de balancete que não estão no
OCR. Campo ancorado num trecho que já existe não fez isso. O schema perdeu o
campo de contexto e a rodada foi descartada e refeita, ao custo de US$ 0,43.

**O modelo alisa, e alisa duas vezes igual.** É a limitação séria da camada. Onde
o scan está sujo, a leitura devolve uma frase limpa, mais curta que a impressa, e
devolve a mesma nas duas passagens, porque o erro é correlacionado. Dois casos
medidos:

- `gn1906-282-rei`: o OCR tem `reidos banqueiros londrinos`, e as duas leituras
  devolveram `dos banqueiros londrinos`. A palavra que sumiu é "rei", que é a
  metáfora que dá título ao achado da seção 1.
- `op1908-ouro-onde`: o OCR tem `palaciodourado da avenida`, e as duas leituras
  devolveram "cofre" e "palacio", perdendo a ironia.

Por isso o manifesto tem a coluna `omissoes_vs_ocr`, que lista mecanicamente as
palavras presentes no OCR e ausentes da leitura de imagem. Ela acusa 8 das 36
citações. Cinco dessas 8 são ruído de OCR sendo corretamente desfeito
(`antigofuiuling-loan` virando `antigo funding-loan`), e três são perda real.

**A conferência mecânica de substring continua necessária e continua
insuficiente.** Ela barra citação inventada. Ela não barra citação ilegível. As
duas camadas juntas ainda não substituem a leitura na página, e o que elas
entregam é ordem de prioridade.

## 7. O que depende de você

1. **Ler na página, primeiro, estas três:** `gn1906-282-rei` (a Gazeta de 1906
   diz "rei dos banqueiros londrinos" ou não?), `gn1906-282-arbitros` (a oração
   está danificada e o sentido depende dela) e `op1908-ouro-onde` (confirmar
   "palacio dourado da avenida"). As três estão na mesma faixa de páginas e são
   as que sustentam afirmações do relatório.
2. **Depois, as 11 `instavel`**, onde já sei qual é a palavra em disputa. A
   coluna `omissoes_vs_ocr` e as duas leituras estão no manifesto.
3. **Decidir se a varredura de perífrase entra no instrumento** ou fica como
   sondagem. Hoje é sondagem, no mesmo patamar da de banqueiros de 26/07.
4. **Decidir o estatuto da camada de leitura por imagem.** Ela é recuperação com
   proveniência, do objeto 1, e não passou pelo gate de mensuração. Se em algum
   momento ela virar insumo de classificação, aí passa.
5. **Acrescentar padrão**, se a leitura mostrar forma que faltou. Cada padrão
   novo exige linha em `padroes_perifrase_banqueiro.csv` com justificativa, e
   registro em `docs/decisoes.md`, porque muda o que a busca enxerga.

## 8. Reprodução

```bash
uv run python -m pipeline.analise.perifrase_banqueiro
uv run python -m pipeline.analise.verifica_citacoes
uv run python -m pipeline.analise.confere_citacao_imagem --passe 1
uv run python -m pipeline.analise.confere_citacao_imagem --passe 2
uv run python -m pipeline.analise.confere_citacao_imagem --reconciliar
```

O conferidor de imagem tem `--so-estimar`, que resolve as páginas e imprime o
custo sem chamar a API, teto padrão de US$ 3,00 e retomada por citação já
gravada. Modelo `claude-sonnet-5`, protocolo
`conferencia-citacao-imagem/claude-sonnet-5 1.0.0`, prompt versionado no próprio
módulo, gravados em toda linha de saída.

Padrões em `pipeline/analise/padroes_perifrase_banqueiro.csv`, manifestos em
`dados/analise/perifrase_banqueiro.csv`,
`dados/analise/mencoes_credor_externo.csv` e
`dados/analise/citacoes_conferidas_imagem.csv`, leituras brutas em
`dados/analise/leitura_imagem_passe1.csv` e `leitura_imagem_passe2.csv`, testes
em `tests/test_perifrase_banqueiro.py`, `tests/test_verifica_citacoes.py` e
`tests/test_confere_citacao_imagem.py`. A sondagem por nome de 26/07 continua em
`dados/banqueiros_externos/`.
