# Piloto de catalogação por LLM, documento de leitura

**Gerado em:** 2026-07-31. 
**Prompt:** `pipeline/prompts/catalogacao_debates.md`, sha `61030ebfd7b93485`, o mesmo para os dois anotadores.

Este documento é o **objeto 1**, mapeamento descritivo. Não é atribuição de posição editorial ao jornal, não é escala, não é estimativa. O campo `voz` existe justamente para impedir que hospedar um discurso seja lido como defendê-lo.

A concordância entre os dois anotadores aparece aqui como análise de sensibilidade descritiva. Não é validação humana e não é validade de construto.

## 1. Cobertura e qualidade do lote

| anotador | CLI | janelas concluídas | falhas | registros aceitos | rejeitados | taxa de rejeição |
|---|---|---|---|---|---|---|
| claude | 2.1.220 (Claude Code) | 48 de 48 | 0 | 98 | 7 | 6,7% |
| codex | codex-cli 0.145.0 | 48 de 48 | 0 | 83 | 5 | 5,7% |

A taxa de rejeição é a métrica de qualidade do lote. Citação que não casa com a janela é descartada, nunca corrigida.

## 2. Onde os dois anotadores se encontram

| classe | janelas |
|---|---|
| os dois catalogaram | 26 |
| só o Claude catalogou | 7 |
| só o Codex catalogou | 1 |
| os dois olharam e não catalogaram nada | 14 |

Detecção quer dizer catalogar ao menos um debate na janela. Não mede acordo sobre o conteúdo do que foi catalogado, que é leitura sua.

## 3. Os debates catalogados

### F1, 1906, criação da Caixa

#### Correio da Manhã, 1906, edição per089842_1906_01776, página 1

`per089842_1906_01776:p001:c11-15029`, classe: os dois catalogaram.

**claude**, 2 registro(s):

- **Estoque de ouro da Caixa prova ou não o acerto da lei**
  - voz: `reproduzido_terceiro`
  - objetos e direção: lastro (nao_classificavel), conversibilidade (nao_classificavel), outro (nao_classificavel)
  - posição: Os cem milhões de pesos ouro acumulados na Caixa de Conversão argentina não demonstram o acerto da lei monetária, e sim a riqueza produtiva do país.
  - argumento: A lei não gerou o ouro, apenas obrigou os possuidores a trocá-lo por papel para poder usá-lo nas transacções; sem esse mecanismo o metal estaria nas arcas dos bancos servindo de contra-valor da nota fiduciária. Não há relação de causa e efeito entre o depósito áureo e o sistema monetário.
  - agentes: La Prensa, Fanfulla de São Paulo
  - marcos: 1890-11-04 (lei monetária argentina discutida pelo artigo de La Prensa)
  - citação conferida: > na Caixa dc Conversão não testemunhampor si só o acerto da lei monetária
  - observação do anotador: Trecho é tradução parcial, feita pelo correspondente do Correio da Manhã em viagem ao Prata, de editorial de La Prensa de 10 de março intitulado La combinación monetaria. O artigo trata da Caixa de Conversão argentina, mas o correspondente o mobiliza explicitamente contra os paladinos do Convenio de Taubaté. A grafia da data da lei aparece como 1890 no OCR. Não há assinatura visível na janela.
- **Causa da esterilidade da Caixa nos quatro primeiros annos**
  - voz: `indeterminado`
  - objetos e direção: lastro (nao_classificavel), outro (nao_classificavel)
  - posição: As despesas militares do conflito com o Chile não explicam a inação da Caixa de Conversão nos seus primeiros anos, e o argumento foi mobilizado apenas para legitimar o insucesso da lei de conversão.
  - argumento: Se o fim do alarma de guerra tivesse liberado recursos, os orçamentos posteriores à solução pacífica teriam caído e produzido saldos, mas os próprios números citados por Martinez e Lewandowski mostram que os orçamentos da guerra e da marinha continuaram altos e com tendência a aumentar. A causa efetiva estaria nos saldos da balança econômica, que os autores mencionam sem datar nem correlacionar com o movimento da Caixa.
  - agentes: Martinez, Lewandowski
  - marcos: 1902-01-01 (termina efetivamente o conflicto de limites com o Chile)
  - citação conferida: > a cessação do alarma dcguerra com o Chile não teve pnr effeito adiminuição da»-> despesos militares
  - observação do anotador: Correspondência em primeira pessoa dirigida ao Correio da Manhã, sem assinatura visível na janela, por isso a voz fica indeterminada e não editorial. O texto é continuação da mesma matéria e o correspondente anuncia sequência em outro artigo. O restante da página traz notas políticas e militares sem relação com a Caixa.

**codex**, 3 registro(s):

- **Depósito metálico prova acerto da lei**
  - voz: `assinado`
  - objetos e direção: lastro (nao_classificavel), conversibilidade (nao_classificavel)
  - posição: O ouro depositado na Caixa não demonstra, por si só, o acerto da lei monetária.
  - argumento: O depósito seria resultado da riqueza produtiva e exportadora argentina, enquanto a lei apenas obrigaria os possuidores de ouro a convertê-lo em papel para utilizá-lo nas transações.
  - citação conferida: > cem milhões do pesos ouro arn.;i_euados' na Caixa dc Conversão não testemunhampor si só o acerto da lei monetária
  - observação do anotador: O artigo assinado incorpora e endossa trechos traduzidos de La Prensa. O nome do autor está afetado pelo OCR.
- **Guerra explica esterilidade inicial da Caixa**
  - voz: `assinado`
  - objetos e direção: taxa (nao_classificavel), conversibilidade (nao_classificavel)
  - posição: O conflito com o Chile e as despesas militares não explicam a inatividade inicial da Caixa nem os resultados negativos da fixação cambial.
  - argumento: Se a guerra fosse a causa, a pacificação deveria ter reduzido as despesas militares, mas os orçamentos de guerra e marinha permaneceram elevados.
  - agentes: Martiuez, Itt-waudowski
  - marcos: 1902-01-01 (O conflito com o Chile terminou)
  - citação conferida: > é ocaso de dizer que os srs. Martiriez e r.ewau-dQjvski lançavam mão desse argumentopara»legitimara lusiijcessp da lei da con-versão monetária
  - observação do anotador: A data do término do conflito é informada apenas pelo ano. Os nomes próprios e parte da formulação do argumento estão corrompidos pelo OCR.
- **Saldos comerciais explicam operações da Caixa**
  - voz: `assinado`
  - objetos e direção: conversibilidade (nao_classificavel), outro (nao_classificavel)
  - posição: A explicação da atividade da Caixa pelos saldos da balança econômica precisa demonstrar a correspondência temporal entre ambos.
  - argumento: O texto censura os autores por não indicarem quando surgiram os saldos nem mostrarem sua relação paralela com o crescimento das operações da Caixa.
  - citação conferida: > sem indicar quando esses saldos apparece-raia c mostrar a repercussão parallela <jflagrante entre o augnieuto animal des.:.balança e o movimento crescente das ope-rações ua Caixa de Conversão.
  - observação do anotador: O trecho anuncia uma continuação e não apresenta, nesta janela, a explicação causal considerada verdadeira pelo autor.

#### Correio da Manhã, 1906, edição per089842_1906_01891, página 2

`per089842_1906_01891:p002:c19913-27563`, classe: os dois catalogaram.

**claude**, 1 registro(s):

- **Criação da Caixa de Conversão com câmbio fixado em 15 dinheiros**
  - voz: `documento_oficial`
  - objetos e direção: taxa (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova), lastro (nao_classificavel)
  - posição: O projeto aprovado institui uma caixa que troca ouro por bilhetes ao portador a uma taxa fixa de 15 dinheiros esterlinos por mil réis, com o ouro recebido mantido em depósito exclusivamente para a conversão.
  - argumento: O texto transcrito é dispositivo de lei e não expõe justificativa: amarra a emissão de bilhetes ao ouro efetivamente depositado, veda qualquer outra destinação desse ouro e manda incinerar os bilhetes resgatados, com garantia do Tesouro Nacional e responsabilidade pessoal dos membros da caixa.
  - agentes: Paula Guimarães, Galeão Carvalhal
  - citação conferida: > A Câmara dos Deputados, na sessão dohontom, approvou em 2- discussão, o pro-jecto creanilo a onixn do conversão cflxan-do o cambio em 15 d.
  - observação do anotador: A janela é relato de sessão parlamentar com transcrição literal do art. 1º e parágrafos do projeto, seguida da lista nominal dos 118 votos a favor e do início da lista dos 17 contra, que aparece cortada no fim da janela. Os deputados que votaram contra não têm argumento registrado aqui, então a divergência aparece só como resultado de votação. O lastro entra como desenho do dispositivo (ouro em depósito, incineração dos bilhetes resgatados) e não como tomada de posição no eixo valorização/estabilidade, daí `nao_classificavel`. O OCR está muito degradado nos nomes e o texto não traz data explícita da sessão, apenas "hontem".

**codex**, 1 registro(s):

- **Criação da Caixa e fixação do câmbio**
  - voz: `documento_oficial`
  - objetos e direção: taxa (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova), lastro (estabilidade_taxa_nova)
  - posição: O projeto aprovado cria a Caixa de Conversão, fixa uma nova taxa cambial e determina a conversão dos bilhetes em ouro.
  - argumento: O mecanismo vincula a emissão aos depósitos de ouro, garante o resgate dos bilhetes na Caixa e proíbe que o ouro depositado seja empregado em outra finalidade.
  - agentes: Câmara dos Deputados, Galeão Carvalhal
  - citação conferida: > «Art. 1* li' instituída nma caixa do con-versão especialmente destinada a rocebermoedas do ouro do curso legal o as quoconstam ilo arti 5* desta lei, entregandoom troca bilhotes ao portador representa-tivos rie yalot egual ao dns moedas rio ourorecebidas lixado esto valor om 18 dinholrosostorilnos por mil réis.
  - observação do anotador: Há divergência interna causada possivelmente pelo OCR: a notícia afirma que o projeto fixava o câmbio em "15 d.", enquanto a transcrição do artigo 1º registra "18 dinholros". A janela não permite resolver a discrepância.

#### Correio da Manhã, 1906, edição per089842_1906_01901, página 1

`per089842_1906_01901:p001:c11865-20902`, classe: os dois catalogaram.

**claude**, 3 registro(s):

- **Eficácia e constitucionalidade do projecto da Caixa**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (nao_classificavel), competencia_institucional (nao_classificavel)
  - posição: O orador vota contra o projecto do sr. David Campista, negando que a Caixa possa controlar o cambio e acusando-a de ofender a nao retroatividade das leis.
  - argumento: A Caixa seria mero apparelho automatico de troca, sem poder de impedir baixa ou alta do cambio, e o projecto seria juridicamente insustentavel por atribuir efeitos retroativos, contra o direito moderno.
  - agentes: Arthur Orlando, David Campista
  - citação conferida: > Contestou que a Caixa tenha o poderrie impedir quer a baixa, quer a alta elocambio e entrou a combater o projocloelo ponlo do vista jurídico e constitucio-nnl porque olTcnde francamente os maissagrados princípios da náo retroactivi-dado rins leis.
  - observação do anotador: OCR muito degradado; a natureza exata da objeção retroativa (a que dispositivo se aplica) não fica legível na janela.
- **Oposição de Joaquim Murtinho à Caixa de Conversão**
  - voz: `indeterminado`
  - objetos e direção: outro (nao_classificavel)
  - posição: Nota informa que Joaquim Murtinho renunciaria à cadeira de senador caso a Caixa fosse aprovada, por ser inteiramente contrário a ela.
  - argumento: Ele não quer faltar à solidariedade política com o Bloco, mas também não quer abandonar suas ideias de estadista, contrárias à Caixa.
  - agentes: Joaquim Murtinho
  - citação conferida: > mas, também entende que não deveabandonar as suas iric.is de estadista, in-teir.imeiitc contrarias á Caixa de Con-versão.
  - observação do anotador: Nota noticiosa curta, sem assinatura e sem indicação de ser editorial; o conteúdo do desacordo de Murtinho não é explicitado na janela.
- **Esvaziamento da Câmara na discussão do projecto**
  - voz: `editorial_do_jornal`
  - objetos e direção: competencia_institucional (nao_aplica)
  - posição: O jornal critica a Câmara por discutir a Caixa com apenas 27 dos 212 deputados presentes, tomando isso como falta de seriedade e empenho.
  - argumento: A presença mínima na sessão em que se discute o projecto é apresentada como sintoma de que a assembleia não trata a matéria com a seriedade devida.
  - citação conferida: > para umaCamnra elo 212 deputados náo se podereidizer que esso numero constitua unisimpioma dc seriedade
  - observação do anotador: Comentário do jornal anexo ao relato da sessão; a fronteira entre relato e comentário é tênue e a atribuição de voz editorial é inferida da forma avaliativa.

**codex**, 2 registro(s):

- **Capacidade da Caixa de estabilizar o câmbio**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (nao_classificavel)
  - posição: A Caixa de Conversão não seria capaz de impedir nem a baixa nem a alta do câmbio.
  - argumento: Arthur Orlando contesta a eficácia do mecanismo proposto para controlar as oscilações cambiais.
  - agentes: Arthur Orlando, David Campista
  - citação conferida: > Contestou que a Caixa tenha o poderrie impedir quer a baixa, quer a alta elocambio
  - observação do anotador: O trecho rejeita a capacidade estabilizadora da Caixa, mas não permite reduzir a posição à defesa da valorização ou da estabilidade em uma taxa nova.
- **Constitucionalidade e retroatividade do projeto**
  - voz: `discurso_parlamentar`
  - objetos e direção: outro (nao_classificavel)
  - posição: O projeto da Caixa de Conversão deve ser rejeitado por ofender o princípio da não retroatividade das leis.
  - argumento: Arthur Orlando combate o projeto do ponto de vista jurídico e constitucional, sustentando que ele produziria efeitos retroativos incompatíveis com o direito moderno.
  - agentes: Arthur Orlando, David Campista
  - citação conferida: > entrou a combater o projocloelo ponlo do vista jurídico e constitucio-nnl porque olTcnde francamente os maissagrados princípios da náo retroactivi-dado rins leis.
  - observação do anotador: A passagem não especifica quais disposições do projeto seriam retroativas.

#### Correio Paulistano, 1906, edição per090972_1906_15348, página 2

`per090972_1906_15348:p002:c3904-13949`, classe: os dois catalogaram.

**claude**, 3 registro(s):

- **fixar o cambio a taxa baixa contra o par de 27 dinheiros**
  - voz: `assinado`
  - objetos e direção: taxa (estabilidade_taxa_nova), divida_externa (estabilidade_taxa_nova)
  - posição: Defende fixar o cambio numa taxa que corresponda as transaccoes reais do paiz, contra a volta ao padrao legal de 27 dinheiros.
  - argumento: Sustenta que os adversarios da taxa inferior a 27 erram ao supor que se quebra uma moeda metallica existente, quando o papel-moeda conserva seu valor acquisitivo interno; e que a alta cambial obtida a custa de emprestimos externos é ficticia e prepara a ruina no momento de pagar os compromissos.
  - citação conferida: > todos os antagonÍ8ta9 daflxai*ão do cambio á taxo inferiora 27 laboram no engano de quese traiu dc quebrar o padrão dcuma moeda metallicu existente nopaiz
  - observação do anotador: Texto muito corrompido por OCR; a taxa defendida aparece como 12 d. em varias passagens, inclusive no exemplo da libra a 20$000.
- **resgate do papel contra ampliacao do meio circulante pela Caixa**
  - voz: `assinado`
  - objetos e direção: limite_emissao (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova), lastro (estabilidade_taxa_nova)
  - posição: Defende emitir mais meio circulante por meio da Caixa de Conversao, em notas conversiveis lastreadas em ouro depositado, em vez de queimar papel.
  - argumento: Compara a circulacao por habitante do Brasil com a de cinco paizes europeus para mostrar insufficiencia de numerario que encarece o juro e trava commercio, industria e lavoura; como a emissao seria representativa de ouro em deposito, augmentaria o meio circulante sem deprecial-o, e a Caixa poderia ir trocando gradualmente o papel do Thesouro por notas com lastro metallico.
  - citação conferida: > em vez de estarmosa queimar papal paro inconscien-temente nos empobrecer, precisa-mos emittir mais o nonno do nos-so meio circulante
  - observação do anotador: A janela traz comparacao numerica internacional e um exemplo de conversao de libra a 12 d.; os numeros estao parcialmente ilegiveis no OCR.
- **valorizacao artificial do cafe contra fixacao cambial**
  - voz: `assinado`
  - objetos e direção: valorizacao_cafe (nao_classificavel), taxa (estabilidade_taxa_nova)
  - posição: Condemna a valorizacao artificial do cafe e apresenta como solucao a fixacao do cambio numa taxa que represente a relacao real das transaccoes internacionaes.
  - argumento: Sustenta que a alta cambial derruba o preco do cafe em Santos, e junta tabella de precos acompanhando a alta do cambio como demonstracao pratica; a fixacao do cambio resolveria o problema do cafe e de tudo quanto se produz.
  - agentes: presidentes dos Estados de Minas, Rio e S. Paulo, A Noticia
  - marcos: 1906-02-23 (o autor emitte sua opiniao sobre a valorizacao do cafe a pedido do jornal A Noticia); 1906-02-25 (Convenio de Taubaté, reuniao dos presidentes de Minas, Rio e S. Paulo)
  - citação conferida: > Discordando du opinião corrente,fui obrigado a condemnal-a, upre-sentando como solu«;ao uo proble-ma da valorização do culé
  - observação do anotador: Direcao sobre valorizacao_cafe marcada como nao_classificavel porque o trecho rejeita a valorizacao artificial sem se reduzir ao eixo valorizacao-estabilidade. A data do Convenio é inferida de 'ante-vespera' de 23 de fevereiro e 'dois dias depois', dai confianca media. A janela sangra para a coluna vizinha de Telegrammas e requerimentos da Alfandega de Santos, alheia ao debate.

**codex**, 4 registro(s):

- **fixação do câmbio contra o câmbio-par**
  - voz: `indeterminado`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Defende fixar o câmbio em uma taxa inferior a 27 dinheiros e adequada às transações internacionais.
  - argumento: A estabilidade cambial favoreceria a produção e a prosperidade, enquanto a valorização artificial do câmbio prejudicaria a produção nacional.
  - citação conferida: > advogo com todo o ardor ccom toda a sinceridade, a fixaçãodo cambio e a crenção da Caixa deConversão
  - observação do anotador: O trecho está em primeira pessoa, mas a autoria não aparece na janela.
- **emissão conversível com lastro em ouro**
  - voz: `indeterminado`
  - objetos e direção: limite_emissao (estabilidade_taxa_nova), lastro (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova)
  - posição: Defende ampliar o meio circulante mediante notas da Caixa de Conversão, conversíveis por valor fixo e correspondentes a ouro depositado.
  - argumento: A insuficiência de numerário dificultaria o crédito e o desenvolvimento econômico; o lastro metálico permitiria aumentar a circulação sem depreciá-la.
  - citação conferida: > As funcçõos.da Caixa de Convcr-são se resumem cm emittir pope)conversível em ouro à vontade doportador, por um valor flxo
  - observação do anotador: O trecho está em primeira pessoa, mas a autoria não aparece na janela.
- **valorização artificial do café**
  - voz: `indeterminado`
  - objetos e direção: valorizacao_cafe (nao_classificavel), taxa (estabilidade_taxa_nova)
  - posição: Condena a valorização artificial do café e propõe como solução uma taxa cambial correspondente às transações internacionais.
  - argumento: A fixação cambial é apresentada como alternativa à política de valorização artificial do café e dos demais produtos.
  - marcos: 1906-02-25 (Presidentes de Minas, Rio e São Paulo adotam em Taubaté a orientação de fixação do câmbio.)
  - citação conferida: > fui obrigado a condemnal-a, upre-sentando como solu«;ao uo proble-ma da valorização do culé
  - observação do anotador: O trecho está em primeira pessoa, mas a autoria não aparece na janela; a data do marco resulta de dois dias após 23 de fevereiro de 1906, conforme a sequência afirmada no texto.
- **alta cambial financiada por empréstimos**
  - voz: `indeterminado`
  - objetos e direção: taxa (estabilidade_taxa_nova), divida_externa (nao_classificavel)
  - posição: Rejeita como artificial a alta cambial obtida mediante grandes empréstimos.
  - argumento: O pagamento futuro dos compromissos contraídos produziria uma crise, por isso o câmbio alto não representaria adequadamente o valor da moeda.
  - citação conferida: > o cambioalto obtido á custa dos enormesempréstimos contrahidos, é pre-parar pura o momento do satisfa-cção desses compromissos a verda-deira ruina da pátria.
  - observação do anotador: O texto não identifica os empréstimos nem seus credores.

#### Correio Paulistano, 1906, edição per090972_1906_15418, página 4

`per090972_1906_15418:p004:c8556-16567`, classe: os dois catalogaram.

**claude**, 3 registro(s):

- **Empréstimo à lavoura contra compra e retenção do café**
  - voz: `assinado`
  - objetos e direção: valorizacao_cafe (nao_classificavel)
  - posição: Defende a compra e retenção do café pelo governo, admitindo o empréstimo à lavoura só como complemento e nunca como substituto da valorização.
  - argumento: Sem influir nos preços, o empréstimo seria consumido pelos fazendeiros, chegaria a poucos e agravaria a crise com nova dívida, enquanto a retenção elevaria o preço, beneficiaria todos proporcionalmente à produção e se pagaria pelo consumo crescente.
  - citação conferida: > Como complemento á valo-rizução, seria um bem ; como sub-stilulo, serio um erro gruvissi-mo.
  - observação do anotador: Texto em formato de entrevista, com perguntas marcadas por P. e respostas por R./B.; o OCR alterna as duas letras.
- **Necessidade da caixa de conversão para conter a alta do câmbio**
  - voz: `assinado`
  - objetos e direção: taxa (estabilidade_taxa_nova), conversibilidade (nao_aplica)
  - posição: Defende a criação da caixa de conversão como instrumento para conter o câmbio, distinguindo essa questão monetária da valorização do café.
  - argumento: A alta taxa de câmbio vigente causa prejuízos intoleráveis à lavoura e o presidente, que afirmava poder conter o câmbio sem a caixa, declara hoje não poder impedir a elevação, o que justificaria a medida.
  - agentes: presidente da Republica, Banco da Republica
  - citação conferida: > A caixa deconversão, linhn, como lem, porlim conter
  - observação do anotador: A citação está truncada porque a sequência seguinte traz travessões do OCR; o trecho segue com "não digo baixar" e "conter o cambio". O texto separa explicitamente valorização do café e questão monetária.
- **Quem decide sobre a caixa: Congresso ou veto do Executivo**
  - voz: `assinado`
  - objetos e direção: competencia_institucional (nao_classificavel)
  - posição: Sustenta que cabia ao Congresso resolver sobre a medida e que presidente e conselheiro deveriam manter reserva até a deliberação, criticando o anúncio prévio de veto.
  - argumento: As duas opiniões divergentes se equivaleriam, de modo que o seguimento lógico seria aguardar e acatar a resolução do Congresso, o que não ocorreu porque o presidente não cessou de tornar público que vetaria a lei.
  - agentes: presidente da Republica, conselheiro Affonso Penna, Congresso
  - citação conferida: > Eramantorem-so ambos om naturalreserva c deixarem quc si- pronun-ciasse o Congresso alim cie lheacatarem a resolução.
  - observação do anotador: O trecho também prevê que o Congresso aprovará a lei com grande maioria, sem data no texto.

**codex**, 4 registro(s):

- **Empréstimo à lavoura versus compra de café**
  - voz: `indeterminado`
  - objetos e direção: valorizacao_cafe (nao_classificavel)
  - posição: O empréstimo à lavoura só seria aceitável como complemento, não como substituto da valorização mediante compra e retenção do café.
  - argumento: O empréstimo não influenciaria os preços, seria consumido pelos beneficiários, agravaria a dívida e alcançaria poucos lavradores. A compra e retenção elevaria os preços e beneficiaria os produtores proporcionalmente à produção.
  - citação conferida: > P. E o que potisu sobro um em-preslimo á lavoura ?B. Como complemento á valo-rizução, seria um bem ; como sub-stilulo, serio um erro gruvissi-mo.
  - observação do anotador: A identidade do entrevistado ou respondente não está legível na janela.
- **Caixa de Conversão e plano de valorização**
  - voz: `indeterminado`
  - objetos e direção: taxa (estabilidade_taxa_nova), valorizacao_cafe (nao_classificavel)
  - posição: A cláusula da Caixa de Conversão não alteraria o plano de valorização e serviria para conter o câmbio.
  - argumento: O empréstimo projetado seria um fator anormal capaz de alterar o câmbio e desorganizar situações existentes, cabendo à Caixa neutralizar essa influência.
  - citação conferida: > Note-se quo mo refiro ú vnlni-i-znçáo do calo o não ii questão mo-m-iario. Nem a cláusula do con-venio, referente á caixu de con-versão, oltorn em uma sò linha aninho dc valoriznção.
  - observação do anotador: O OCR está especialmente corrompido na distinção entre valorização do café e questão monetária.
- **Congresso decide sobre a Caixa**
  - voz: `indeterminado`
  - objetos e direção: competencia_institucional (nao_classificavel)
  - posição: As autoridades executivas deveriam aguardar a decisão do Congresso e acatá-la, em vez de anunciar previamente o veto.
  - argumento: Diante de opiniões divergentes sobre a Caixa, o Congresso deveria pronunciar-se, sendo criticada a declaração presidencial de que a lei seria vetada.
  - agentes: sr. presidente da Republica, sr. conselheiro Afionso Pennn
  - citação conferida: > Eramantorem-so ambos om naturalreserva c deixarem quc si- pronun-ciasse o Congresso alim cie lheacatarem a resolução. Tal não sedou e não cessou o sr. presidenteda Republica de tornar publicoque vetnria a lei
  - observação do anotador: A formulação sobre as duas opiniões contém OCR corrompido, mas a atribuição da decisão ao Congresso e a crítica ao anúncio do veto são legíveis.
- **Caixa contra elevação prejudicial do câmbio**
  - voz: `indeterminado`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: A elevação cambial prejudicial à lavoura demonstraria a necessidade da Caixa de Conversão.
  - argumento: O presidente afirmara poder conter o câmbio sem a Caixa, mas a elevação vigente continuava e produzia prejuízos intoleráveis aos produtores, o que é apresentado como prova da necessidade da instituição.
  - agentes: sr. presidente da Republica
  - citação conferida: > Não eslá abi a justificação ntkcomp Ma e irrecusável da necesti-«lade da caixa de conversão ?
  - observação do anotador: A expressão imediatamente anterior a "irrecusável" está ilegível no OCR.

#### Correio Paulistano, 1906, edição per090972_1906_15474, página 2

`per090972_1906_15474:p002:c34907-42303`, classe: só o Claude catalogou.

**claude**, 3 registro(s):

- **Divisão de votos na Câmara sobre o projeto da Caixa**
  - voz: `discurso_parlamentar`
  - objetos e direção: outro (nao_classificavel)
  - posição: Deputados registram em ata que teriam votado contra o projeto da Caixa de Conversão, e um deles que teria votado a favor.
  - argumento: Nenhum argumento é apresentado na janela: são declarações de voto retroativas de ausentes, sem justificativa.
  - agentes: Affonso Costa, Wenceslau Escobar, Paulo Ramos, Pedro Moacyr, Germano Hasslocher
  - marcos: 1906-01-01 (Comissão de Finanças assina a redação do projeto da Caixa de Conversão, de acordo com as emendas aprovadas, para terceira discussão)
  - citação conferida: > os ars. AffonsoCosta, Wenccslau Escobnr, Pau'lo Ramos o Pedro Moocyr de'clororam quo, si estlvossem pre'sentes, honlem, votariam con'tra o projeclo
  - observação do anotador: A janela registra o alinhamento de votos sem qualquer razão declarada, por isso a direção fica não classificável. O marco da Comissão de Finanças é datado apenas como 'hoje' no texto; o ano vem do metadado da edição, não da janela.
- **Emendas de Alcindo Guanabara fixando padrão em 12 dinheiros**
  - voz: `documento_oficial`
  - objetos e direção: taxa (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova), lastro (estabilidade_taxa_nova), competencia_institucional (nao_classificavel)
  - posição: Substituir o padrão monetário vigente por um de 9$000 pela oitava de 22 quilates, equivalente ao câmbio de 12 dinheiros, e converter toda a emissão fiduciária em moeda nacional ouro a essa taxa, com a Caixa de Conversão substituindo gradualmente os bilhetes inconversíveis e incinerando os retirados.
  - argumento: O texto transcrito das emendas é dispositivo, não argumentativo: fixa a taxa nova por lei, converte os fundos de resgate do papel em fundo de conversão em ouro e encarrega o Banco do Brasil, ou uma seção de câmbios do Tesouro, de manter a fixidez da taxa por compra e venda de letras.
  - agentes: Alcindo Guanabara, Banco do Brasil
  - citação conferida: > flcnKiibHlItuhlii pelo do 9$()U0 polaoitavo do 22 quilates, oqttlvo'tentos no cambio do 12 diiibol-ros esterlinos por 1$000.
  - observação do anotador: OCR muito degradado no bloco das emendas, inclusive no ano da lei citada no artigo primeiro, ilegível. O texto é reprodução das emendas obtida pelo jornal, apresentada como projeto a apresentar na terceira discussão, não como opinião do jornal. A atribuição de competência ao Banco do Brasil ou ao Tesouro fica como não classificável porque a janela não a vincula ao eixo valorização contra taxa nova.
- **Emenda criando Banco Central Hypothecario e Agricola**
  - voz: `documento_oficial`
  - objetos e direção: outro (nao_aplica)
  - posição: Autorizar a criação de um Banco Central Hypothecario e Agricola, com capital mínimo de 1.500.000 libras esterlinas, sede no Rio, monopólio do lançamento de letras hipotecárias brasileiras na Europa e isenção de impostos.
  - argumento: A janela traz apenas o articulado da emenda, com as condições de capital, sede, correspondência com bancos estaduais e limites das operações de empréstimo hipotecário e agrícola, sem justificativa discursiva.
  - agentes: Alcindo Guanabara
  - citação conferida: > Arligo primeiro— E' o gover'no auetorizado o conceder au-ctorização pura a creaçõo deum Banco Central Hypothòearloo Agrícola, sob ns seguintescondições;
  - observação do anotador: Emenda de crédito agrícola e hipotecário apresentada no mesmo pacote da Caixa de Conversão, mas sem posição sobre taxa, lastro ou conversibilidade na janela, por isso a direção é não aplica.

**codex**: olhou e não catalogou nada.

#### Gazeta de Notícias, 1906, edição per103730_1906_00174, página 5

`per103730_1906_00174:p005:c24255-33647`, classe: os dois catalogaram.

**claude**, 3 registro(s):

- **Fixar o câmbio por Caixa de Conversão contra elevação cambial**
  - voz: `indeterminado`
  - objetos e direção: taxa (estabilidade_taxa_nova), valorizacao_cafe (nao_classificavel)
  - posição: Defende fixar o câmbio por meio de uma Caixa de Conversão criada por lei do Congresso, de modo que o empréstimo externo entre no país sem elevar o câmbio.
  - argumento: Como os gastos de produção são feitos em papel, a alta do câmbio reduziria a soma em papel recebida pelo produtor e tornaria impossível valorizar a produção; só com relação estável entre ouro e papel o preço de venda cobre o custo e remunera o capital.
  - agentes: signatários do Convênio
  - citação conferida: > Por esla tórma os lõ milhões do em-presiimo poderão entrar 110 paiz c serlançados em circulação, sem elevaçãocambial qne deprecie os preços dos nossosproduetos
  - observação do anotador: Peça encimada por 'A Lavoura de Minas' e por subtítulos (Convênio de Taubaté, Cambio, Caixa da conversão, Reforma monetaria, Padrão novo), com trecho em primeira pessoa do plural ('exponhamos as nossas ideas e façamos os nossos pedidos'), o que sugere documento ou representação de lavradores transcrita, mas a janela não permite identificar autoria; por isso voz indeterminado. OCR muito degradado, com colunas vizinhas de anúncios e de edital sobre fogos de artifício misturadas.
- **Lastro metálico e conversibilidade das notas da Caixa**
  - voz: `indeterminado`
  - objetos e direção: lastro (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova), limite_emissao (estabilidade_taxa_nova)
  - posição: Defende que a Caixa emita bilhetes à taxa prefixada, conversíveis à vista, garantidos pelo ouro nela depositado, e que converta à mesma taxa o ouro dos fundos de resgate e de garantia e o de particulares.
  - argumento: Emitindo só sobre base metálica e trocando apenas à taxa fixada, a Caixa funciona como aparelho de defesa da produção e de fixação do ouro no país, que hoje foge por medo à instabilidade do seu valor.
  - citação conferida: > Serão essas notes ile papel conversívelgarantidas pelo ouro depositado na Caixa,corno lastro da emissão
  - observação do anotador: O empréstimo é referido como de 15 milhões esterlinos, grafado 'lõ milhões' pelo OCR. Trecho sobre a taxa fixa do troco vem muito corrompido ('â taxa*cambial L\aJ.-i').
- **Jogo do câmbio na Bolsa e instabilidade da moeda**
  - voz: `indeterminado`
  - objetos e direção: taxa (estabilidade_taxa_nova), outro (nao_classificavel)
  - posição: Defende que a flutuação da moeda alimenta especulação imoral e que dar estabilidade ao meio circulante é golpe contra essa imoralidade.
  - argumento: As operações cambiais deixaram de acompanhar as permutas externas e multiplicaram-se pelo jogo, com uma dúzia de câmbios por dia e altas e baixas fictícias, produzindo perdas ao Estado, ao Tesouro e ao Banco da República e lucros roubados à lavoura, à indústria e ao comércio.
  - agentes: visconde de Albuquerque, Peltersen
  - citação conferida: > o qual tornou-so a maisjrendosa das industrias para os especula-dores e banqueiros sem escrúpulos
  - observação do anotador: A janela transcreve, em caixa destacada, discurso do visconde de Albuquerque em sessão de 10 de julho no Senado do Império, mas o ano vem ilegível no OCR ('ISiG'), por isso nenhum marco datado foi registrado. A citação usada é do corpo do artigo, não do discurso.

**codex**, 2 registro(s):

- **Fixação cambial para proteger a produção**
  - voz: `reproduzido_terceiro`
  - objetos e direção: taxa (estabilidade_taxa_nova), valorizacao_cafe (estabilidade_taxa_nova)
  - posição: Defende fixar e estabilizar o câmbio por meio da Caixa de Conversão para sustentar a valorização do café e da produção nacional.
  - argumento: A oscilação do papel em relação ao ouro prejudicaria a relação entre custos e preços, favoreceria a especulação cambial e afastaria o ouro do país. A estabilidade permitiria remunerar a produção e conservar capitais no mercado interno.
  - agentes: signatários do Convênio, Caixa de Conversão
  - citação conferida: > Eslabilisado o cambio para as operaçõesda Caixa de Conversão^ íunecionará ellacomo apparelho de defesa da producçãoe de fixação, 110 paiz, do ouro que dellefoge por medo á instabilidade do seuvalor.
  - observação do anotador: O cabeçalho indica reprodução de A Lavoura de Minas. O OCR mistura colunas e torna ilegível o valor exato da taxa proposta.
- **Emissão conversível garantida por ouro**
  - voz: `reproduzido_terceiro`
  - objetos e direção: lastro (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova), limite_emissao (nao_classificavel)
  - posição: Defende que a Caixa emita papel conversível, garantido pelo ouro depositado, e efetue o troco dos bilhetes por ouro na taxa fixada.
  - argumento: O ouro do empréstimo, dos fundos de resgate e garantia e dos particulares formaria a base metálica da emissão. A vinculação entre emissão, lastro e troco sustentaria a conversibilidade e a estabilidade cambial.
  - agentes: Caixa de Conversão
  - citação conferida: > Serão essas notes ile papel conversívelgarantidas pelo ouro depositado na Caixa,corno lastro da emissão, que hão de servirãs Irahsacções commerciaes do Convênio.
  - observação do anotador: O trecho sustenta emissão limitada pela base metálica, mas não apresenta um teto numérico legível.

#### Gazeta de Notícias, 1906, edição per103730_1906_00185, página 3

`per103730_1906_00185:p003:c24117-49537`, classe: os dois catalogaram.

**claude**, 7 registro(s):

- **fixar taxa nova de 15 dinheiros contra volta ao par**
  - voz: `documento_oficial`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Defende fixar em 15 dinheiros por mil-réis a taxa de emissão da caixa de conversão, sustentando que o nível escolhido importa menos do que a estabilidade obtida.
  - argumento: Garantidos limites à flutuação, a escolha do valor da taxa perderia a importância que se lhe atribui, e a taxa de 15 dinheiros seria a corrente no mercado, sem alterar sensivelmente a situação cambial vigente nem os interesses da indústria e do comércio.
  - agentes: Lorini
  - marcos: 1905-12-30 (lei n. 1.452, sobre a receita pública, citada quanto aos interesses da indústria)
  - citação conferida: > a taxa de 15 ds. por mil réis
  - observação do anotador: A janela é um parecer parlamentar com o projeto que o acompanha, transcrito pelo jornal; o texto está cortado ao final (item VIII interrompido) e há colunas vizinhas ilegíveis intercaladas.
- **limite de emissão como caminho de volta ao par legal**
  - voz: `documento_oficial`
  - objetos e direção: limite_emissao (valorizacao)
  - posição: Defende teto de 320.000:000$, correspondente a 20 milhões de libras ao câmbio de 15 dinheiros, para as emissões da caixa.
  - argumento: A limitação tornaria possível uma elevação legítima das taxas, aproximando-as segura e progressivamente do par legal, sem abalos nem bruscas flutuações, e faria da caixa indicador da verdadeira situação econômica do país.
  - citação conferida: > limita as emissões da caixa de conversão
  - observação do anotador: O trecho combina fixação de taxa baixa com expectativa de valorização futura, o que torna o eixo menos nítido do que nas demais entradas.
- **acusação de quebra do padrão monetário e de imoralidade**
  - voz: `documento_oficial`
  - objetos e direção: taxa (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova)
  - posição: Nega que a fixação da taxa das notas da caixa configure quebra do padrão monetário ou conversão do papel de curso forçado a taxa inferior a 27 dinheiros.
  - argumento: A taxa fixada refere-se apenas às notas especiais emitidas contra depósito de ouro e é condição de contrato entre a caixa emissora e o portador do ouro, não fixação de taxa para conversão do papel de curso forçado; uma fixação dessa natureza seria mera promessa legal, como a de 1846, que permanece sem probabilidade de execução.
  - marcos: 1846-01-01 (promessa legal de conversão invocada como embaraço teórico)
  - citação conferida: > Não ha quebra do padrão monetário.
  - observação do anotador: O texto dá apenas o ano de 1846 para a promessa legal, daí a confiança baixa no marco.
- **resgate do papel inconversível ao lado da caixa**
  - voz: `documento_oficial`
  - objetos e direção: lastro (valorizacao), conversibilidade (valorizacao)
  - posição: Defende reforçar o fundo de resgate para retirar vigorosamente da circulação o papel de curso forçado, ao lado do funcionamento da caixa de conversão.
  - argumento: O fortalecimento crescente do fundo de garantia aumentaria a confiança e permitiria medidas tendentes à conversão definitiva do meio circulante; caixa e resgate juntos dariam ao câmbio a estabilidade indispensável ao desenvolvimento das forças produtoras.
  - marcos: 1899-06-20 (lei que criou os fundos de resgate e de garantia do papel-moeda)
  - citação conferida: > A Caixa de Conversão do um lado e oresgate do papel inconversivel de outro
  - observação do anotador: O OCR une palavras vizinhas na citação, que foi copiada sem correção.
- **caixa como freio à especulação e à alta cambial**
  - voz: `documento_oficial`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Sustenta que a caixa de conversão conteria a especulação sobre o ouro e a alta cambial enquanto permanecesse inalterada a taxa de emissão, respondendo à objeção de que a instituição contraria o interesse nacional na apreciação da moeda.
  - argumento: Nem alta nem baixa são bem em absoluto; o mal é a oscilação permanente de valores. O bom câmbio pode ser produto efêmero de medidas artificiais, e a experiência argentina mostra que a lei de conversão delimitou a especulação desenfreada sobre a piastra papel.
  - agentes: Goschen, A. Martinez, Lewandowski, ministro da fazenda
  - marcos: 1900-01-01 (lei da conversão monetária argentina em vigor, fixando 44 centavos por peso); 1904-01-01 (discurso do deputado Ewards na Câmara chilena sobre caixa de conversão projetada)
  - citação conferida: > Ora, a especulação se exerce para a baixacomo para a alta.
  - observação do anotador: O texto dá apenas o ano para a lei argentina e diz "fins de 1904" para o discurso chileno, daí a confiança baixa. A taxa argentina aparece como 41 e como 44 centavos em pontos distintos, provavelmente erro de OCR.
- **empréstimo externo de 15 milhões de libras como lastro**
  - voz: `documento_oficial`
  - objetos e direção: divida_externa (nao_classificavel), lastro (estabilidade_taxa_nova)
  - posição: Transcreve e endossa a cláusula do Convênio que autoriza São Paulo a contrair até quinze milhões de libras, com garantia da sobretaxa e responsabilidade solidária dos três Estados, aplicáveis como lastro da caixa de emissão e conversão.
  - argumento: A entrada dessa corrente de ouro provocaria súbita elevação da taxa cambial; destinar o produto do empréstimo a lastro evita a perturbação e cria abrigo ao ouro, com as notas emitidas exatamente na proporção do valor metálico do encaixe.
  - citação conferida: > de quinze milhões de libras esterlinas
  - observação do anotador: Trecho é citação do art. do Convênio de Taubaté dentro do parecer, portanto documento oficial em dois níveis.
- **legitimidade da intervenção do Estado na valorização do café**
  - voz: `documento_oficial`
  - objetos e direção: valorizacao_cafe (nao_aplica)
  - posição: Conclui que as medidas do Convênio de Taubaté para regularização do comércio do café não são contrárias aos bons métodos econômicos e que cabe ao Estado auxiliar os produtores.
  - argumento: Obedecem à lei econômica de que o aumento de preço é proporcional à deficiência da oferta; sendo impossível aos produtores organizarem ação comum para graduar a oferta, cabe ao Estado agir como propulsor da prosperidade e do desenvolvimento econômico.
  - citação conferida: > não são contrarias aosbons methodos econômicos
  - observação do anotador: A defesa é da política cafeeira, não da política cambial, por isso a direção no eixo monetário fica em nao_aplica.

**codex**, 7 registro(s):

- **Fixação temporária contra oscilação cambial**
  - voz: `documento_oficial`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Defende fixar em 15 ds. a taxa das notas da Caixa, de modo temporário e alterável conforme as condições do país.
  - argumento: A estabilidade protegeria produção, trabalho e riqueza das variações cambiais que não refletissem a situação econômica efetiva.
  - marcos: 1905-12-30 (A lei n. 1.452 é citada como respaldo à adequação da taxa aos interesses da indústria.)
  - citação conferida: > A fixação não será definitiva, mas pPr«miltiiá sufllciente estabilidade para incre-mentar a riqueza, tonificar a producçãoo o trabalho, pondi -os a coberto das su-bitas variações,alheias ao verdadeiro es-lado econômico,
  - observação do anotador: O nome do autor e o cabeçalho não aparecem na janela. A voz foi classificada como documento oficial porque o texto se identifica como parecer, acompanha um projeto e termina com síntese numerada.
- **Fixação sem quebra do padrão**
  - voz: `documento_oficial`
  - objetos e direção: taxa (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova)
  - posição: Sustenta que a taxa fixa regula apenas as notas especiais da Caixa e não redefine a conversão do papel de curso forçado.
  - argumento: A relação entre ouro depositado e notas emitidas seria condição contratual entre a Caixa e o portador, portanto não constituiria quebra do padrão monetário.
  - citação conferida: > A fliação da taxa refere-se a essas no-tas e é como a condição de um conlractoentre a caixa emissora e o portador doouro. Não ha quebra do padrão monetário.
  - observação do anotador: O trecho distingue a taxa das novas notas de uma eventual taxa para conversão geral do meio circulante.
- **Lastro integral das notas conversíveis**
  - voz: `documento_oficial`
  - objetos e direção: lastro (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova)
  - posição: Defende que cada nota especial corresponda ao ouro depositado e seja conversível segundo a relação prefixada.
  - argumento: As notas seriam certificados de depósitos em ouro, separados da circulação estatal inconversível, o que daria segurança ao novo meio circulante.
  - citação conferida: > As nolas especiaes assim emittidas nãosão mais do que verdadeiros certificadosde depósitos em ouro, independentes eestranhos á circulação inconversivel doEstado.
- **Resgate do papel e conversão futura**
  - voz: `documento_oficial`
  - objetos e direção: lastro (valorizacao), conversibilidade (valorizacao)
  - posição: Propõe reforçar os fundos de resgate e garantia para retirar papel de curso forçado e ampliar progressivamente a circulação conversível.
  - argumento: A retirada do papel inconversível conteria movimentos de baixa, fortaleceria a confiança e prepararia a conversão definitiva do meio circulante.
  - marcos: 1899-06-20 (Lei cria os fundos de resgate e de garantia do papel-moeda.)
  - citação conferida: > Medida de grande conveniência será,bemestudados os nossos encargos e os nossosrecursos, reforçar o fundo de resgate demodo a ser vigorosamente retirado dacirculação o papel de curso forçado o, aomesmo tempo, abrihdo caminho ao alarga-1 mento progressivo da circulação conver-sivel.
  - observação do anotador: O ano da lei aparece como "1S99" em uma ocorrência do OCR, mas o próprio texto também menciona o projeto de 1899.
- **Limite de emissão e retorno ao par**
  - voz: `documento_oficial`
  - objetos e direção: limite_emissao (valorizacao), taxa (valorizacao)
  - posição: Defende limitar a emissão da Caixa para permitir posterior apreciação gradual do meio circulante em direção ao par legal.
  - argumento: Atingido o máximo de emissões e depósitos, a entrada de ouro e o fortalecimento econômico poderiam justificar uma elevação legítima da taxa, sem mudanças bruscas.
  - citação conferida: > O inluito dessa limitação é tornar pos-sivel uma elevação legitima das taxas, ap-proximando-as segura e progressivamentedo par legal, sem abalos e sem bruscasf.ucluações.
  - observação do anotador: O projeto fixa o máximo em 320.000:000$, correspondente a 20 milhões de libras, segundo o trecho.
- **Empréstimo externo convertido em lastro**
  - voz: `documento_oficial`
  - objetos e direção: divida_externa (estabilidade_taxa_nova), lastro (estabilidade_taxa_nova), taxa (estabilidade_taxa_nova)
  - posição: Defende aplicar o produto do empréstimo externo como lastro da Caixa de Emissão e Conversão.
  - argumento: A aplicação evitaria que uma entrada volumosa de ouro provocasse elevação cambial súbita e, simultaneamente, criaria um abrigo para esses capitais.
  - citação conferida: > Ou para evilar essa perturbação ou como intuito de aproveitar capitães para acreação de um apparelho quo sirva deabrigo ao ouro, determinou o Convênioque o produeto do empréstimo seja applf.cado como lastro para uma Caixa de Emis-são e Conversão, tendente 6 fixação dtvalor da moeda.
- **Auxílio estatal à valorização do café**
  - voz: `documento_oficial`
  - objetos e direção: valorizacao_cafe (nao_classificavel), competencia_institucional (nao_classificavel)
  - posição: Defende que o Estado auxilie os produtores a graduar a oferta e melhorar os preços do café.
  - argumento: Como os produtores não conseguiriam organizar sozinhos uma ação comum, caberia ao Estado intervir em favor da prosperidade e do desenvolvimento econômico.
  - citação conferida: > Na impossibilidade de organisarenaos produclores a sua acção commum, ten-dente á graduação da offerta e melhoriados preços de consumo, cabe ao Estadoauxilial-os como propulsor, quo é, da pro-speridade edo desenvolvimento economicedo paiz.
  - observação do anotador: A posição favorável à intervenção e à valorização é clara, mas não se reduz às direções monetárias de valorização do mil-réis ou estabilidade de uma taxa nova.

#### Gazeta de Notícias, 1906, edição per103730_1906_00265, página 2

`per103730_1906_00265:p002:c414-20557`, classe: os dois catalogaram.

**claude**, 3 registro(s):

- **Caixa de Conversão e estabilidade cambial contra o Jornal do Commercio**
  - voz: `assinado`
  - objetos e direção: taxa (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova)
  - posição: Defende a aprovação da Caixa de Conversão e a estabilização do câmbio, contra a campanha do Jornal do Commercio que alarma sobre a baixa cambial e o crédito do país.
  - argumento: A oscilação cambial recente não é excepcional, e o Jornal silenciou diante de variação maior um ano antes; sustentar o país exige preços remuneradores à agricultura e uma situação estável para o valor da moeda, condição de confiança das forças econômicas.
  - agentes: Augusto Ramos, conselheiro Penna, Jornal do Commercio, Witte
  - marcos: 1906-01-01 (Congresso discute a Caixa de Conversão e prepara-se para votá-la em terceira discussão); 1906-09-21 (Data de assinatura do artigo, no Rio)
  - citação conferida: > Denlro de poucos dias será uma lei dopaiz a Caixa de Conversão.
  - observação do anotador: Texto muito corrompido por OCR e cortado por colunas vizinhas (concurso de recenseamento, notas policiais). O nome do autor aparece como 'AlICLSTO P.UIOS'.
- **Crédito externo, banqueiros e informações prestadas ao Times**
  - voz: `assinado`
  - objetos e direção: divida_externa (nao_classificavel)
  - posição: Sustenta que as relações com os banqueiros estrangeiros são apenas comerciais e que informações falsas sobre a situação brasileira têm sido enviadas aos Rothschild e ao Times, não devendo o crédito externo ditar a política monetária.
  - argumento: A boa harmonia com os banqueiros só subsiste enquanto o Brasil for próspero e solvável, e a solvência depende de sustentar as classes produtoras, não de agradar credores; sentimentos afetivos não entram nesse cálculo.
  - agentes: Augusto Ramos, Srs. Rothschild, Times
  - citação conferida: > Somos deis negociantes, nada mais.
  - observação do anotador: Grafia dos nomes deturpada pelo OCR ('Rolbschlld', 'Rolli-scliil.l'). A citação escolhida é curta porque os trechos maiores estão muito corrompidos.
- **Curso forçado como causa das dificuldades e urgência da reforma**
  - voz: `discurso_parlamentar`
  - objetos e direção: conversibilidade (estabilidade_taxa_nova), taxa (estabilidade_taxa_nova)
  - posição: Em discurso na Câmara, defende a criação da Caixa de Conversão e a solução do problema monetário para tornar o câmbio estável, combatendo o curso forçado do papel inconversível.
  - argumento: O curso forçado, ao lado da escravidão, corroeu o organismo do país desde a Independência; resolvido o problema político, urge resolver o monetário, e a estabilidade da moeda beneficia classes produtoras e consumidoras.
  - agentes: Galeão Carvalhal
  - citação conferida: > Combateu o curso forçado donosso papel inconversivel, como fonle detodas as clillicuIdades
  - observação do anotador: É apanhado sucinto feito pelo jornal do discurso, não transcrição integral. A sequência do discurso está partida por colunas intercaladas (notas judiciais e sobre pescadores), o que deixa incerto onde termina a fala.

**codex**, 4 registro(s):

- **Estabilização cambial pela Caixa de Conversão**
  - voz: `assinado`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Defende a Caixa de Conversão como instrumento de estabilização do câmbio.
  - argumento: A estabilidade do valor da moeda daria tranquilidade e confiança ao comércio e sustentaria a prosperidade das classes produtoras.
  - agentes: Augusto Ramos, Penna
  - citação conferida: > A Caixa de Conversão não lem oulroobjeclivo senão esses que deixo enuncia-dos; e foi exaclamenle por haver ado -piado esse prograinma que o Sr. conse-Ibeiro Penna, muito antes do Convênio deTaubaté, já se declarara partidário daeslabilisação do cambio
  - observação do anotador: O texto contrapõe essa defesa às críticas atribuídas ao Jornal do Commercio.
- **Caixa de Conversão e crédito externo**
  - voz: `assinado`
  - objetos e direção: divida_externa (nao_classificavel)
  - posição: Sustenta que as relações com banqueiros estrangeiros dependem da solvência brasileira, não da rejeição da Caixa de Conversão.
  - argumento: A continuidade do crédito seria garantida pela prosperidade e solvência do Brasil, obtidas mediante o apoio às atividades produtoras.
  - agentes: Augusto Ramos, Rolbschlld
  - citação conferida: > K*.sa boa harmonia, porém, sõ pôde sub-sistir, como é natural, emquanto se- man-liver prospero c solvavel o Brasil e em-quanto, por conseguinte, íõr um homcliente para os Srs. Rolbschlld.
  - observação do anotador: O nome dos banqueiros apresenta OCR defeituoso.
- **Congresso mantém tramitação da Caixa**
  - voz: `assinado`
  - objetos e direção: competencia_institucional (nao_classificavel)
  - posição: Aprova a continuidade da deliberação congressual sobre a Caixa, apesar das pressões contrárias.
  - argumento: O Congresso é apresentado como impassível diante das críticas da imprensa, do governo e dos agentes financeiros estrangeiros.
  - agentes: Augusto Ramos, Congresso
  - citação conferida: > Em compensação vai o Congresso, irre-verente e rebelde, continuando impassívelo s- u caminho, discutindo a Caixa dcConversão c preparando-se para volal-aem .i* dis.-ussão por ISO votos conladniios.
  - observação do anotador: O número e a referência à discussão estão prejudicados pelo OCR.
- **Curso forçado e papel inconversível**
  - voz: `discurso_parlamentar`
  - objetos e direção: conversibilidade (nao_classificavel)
  - posição: Combate o curso forçado do papel inconversível.
  - argumento: O regime monetário é apontado como origem de dificuldades econômicas, financeiras e mais amplas na vida nacional.
  - agentes: Galeão Carvalhal
  - citação conferida: > Combateu o curso forçado donosso papel inconversivel, como fonle detodas as clillicuIdades que, mesmo fora daordem econômica e financeira, lem asso-berbado a vida da nação, quer 11a Monar-chia, quer na Rpullici.
  - observação do anotador: O jornal declara apresentar apenas um resumo muito sucinto do discurso.

#### O Paiz, 1906, edição per178691_1906_08005, página 4

`per178691_1906_08005:p004:c31479-42902`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### O Paiz, 1906, edição per178691_1906_08026, página 1

`per178691_1906_08026:p001:c19016-28127`, classe: os dois catalogaram.

**claude**, 4 registro(s):

- **Coibir a alta do câmbio contra continuar a valorização**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (valorizacao), lastro (valorizacao)
  - posição: Defende a continuidade do programa de resgate do papel e valorização progressiva pelo fundo de garantia, e condena a decisão de conter a alta cambial.
  - argumento: A alta do mil-réis foi conquistada com oito anos de impostos excessivos e sacrifícios, e é ela que restaurou o crédito brasileiro no exterior e atrai capitais estrangeiros; deter a alta agora desperdiça o êxito no momento em que ele começa a recompensar o esforço.
  - agentes: Campos Salles, Sr. Campista, Sr. Cnrvníhai
  - citação conferida: > muda subitamente do rumo o de-clara ao povo espantado que e in-dispensável coíilblr a alta do cam-blo, aquella altn salvadora para con-seguir a qual tantos sacrlíicH»; ex-Iglu !
  - observação do anotador: OCR muito degradado; grafias como 'coíilblr' e 'sacrlíicH»' são do original. A janela mistura, ao final, colunas alheias ao assunto (telegrama sobre a Revolução de Cuba e nota sobre Julio de Mesquita).
- **Projeto Campista dissimula a quebra do padrão monetário**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (valorizacao), lastro (nao_classificavel), conversibilidade (nao_classificavel)
  - posição: Rejeita o projeto da caixa de conversão, sustentando que a taxa predeterminada de 15 dinheiros é quebra do padrão sob outro nome e que a caixa nasce sem lastro próprio.
  - argumento: Campista teria conciliado, por fórmula ambígua, quem pedia a quebra do padrão e quem a combatia, dizendo a uns que não há quebra e a outros que isto vale pela quebra; a caixa resultante não converte o papel-moeda do Estado, não dispõe de lastro seu, espera ouro espontâneo e emite bilhetes de curso legal cuja base não é indicada, sendo os 15 dinheiros tão arbitrários quanto seriam 8 ou 12.
  - agentes: David Campista, Congresso
  - marcos: 1906-02-20 (plano de 20 de fevereiro, parte monetária do convênio de Taubaté, recusado pelo presidente da República)
  - citação conferida: > uma ealxa do conversãoquo não converta o papel-moeda doEstado, não dispõe de lastro seu oespora a incursão do ouro espon-tanoo, emitto bilhetes a uma taxa"predeterminada"; quo serft do 15 d.por l?, como seria do íi ou 12
  - observação do anotador: O texto refere ainda uma lei 'de 184fl' (ano ilegível no OCR) como base possível do curso legal; não registrei como marco por não ser datável com segurança.
- **Defesa de Campista: caixa fixa o câmbio sem quebrar o padrão**
  - voz: `reproduzido_terceiro`
  - objetos e direção: taxa (estabilidade_taxa_nova), lastro (estabilidade_taxa_nova)
  - posição: Trecho transcrito do opúsculo de David Campista sustenta que a caixa de conversão fornece moeda-papel a câmbio fixo em troca de ouro depositado, afastando a pressão artificial sobre o câmbio, sem quebra do padrão monetário.
  - argumento: A fixação da taxa referir-se-ia apenas às notas especiais emitidas, como condição de um contrato entre a caixa emissora e o portador do ouro; instituída à semelhança da caixa argentina, produziria os mesmos efeitos salutares sobre a especulação e conteria as oscilações da taxa no sentido da alta.
  - agentes: David Campista, Marttnez, Lcwundowsky
  - marcos: 1899-01-01 (reforma monetária argentina, apresentada no texto como quebra efetiva do padrão)
  - citação conferida: > as oscilIaçUos dataxa serfio contidas, "no sentido daalia" pola caixa do conversão; queforneço moeda-papel "a cambiolixo cm troca do ouro quo for lielladepositado."
  - observação do anotador: É citação que o jornal faz do opúsculo de Campista para em seguida refutá-la; a posição é do autor citado, não do jornal. O texto do opúsculo aparece com aspas internas do próprio original, mantidas na transcrição.
- **Autoridade do Congresso para reverter o rumo monetário**
  - voz: `editorial_do_jornal`
  - objetos e direção: competencia_institucional (nao_classificavel)
  - posição: Nega crédito ao Congresso para decidir a matéria, por ter durante oito anos sustentado o rumo oposto ao que agora adota.
  - argumento: Ao mudar de direção, o poder legislativo ou admite ter sido incompetente antes ou confessa ser temerário agora, e em qualquer dos casos não pode reputar-se com direito a ser acreditado.
  - agentes: Congresso
  - citação conferida: > Ouo Congresso affirma a sua iheompo-tencla pretérita, ou confessa n suatemeridade aetual. O quo parece delodo Inudmissivel 6 quo so reputecom direito a ser acreditado, querconfosse, quer affirme.
  - observação do anotador: Separei do primeiro debate por incidir sobre a credibilidade e a competência do órgão decisor, e não sobre o mérito da política cambial.

**codex**, 3 registro(s):

- **conter ou permitir a alta cambial**
  - voz: `indeterminado`
  - objetos e direção: taxa (valorizacao)
  - posição: A alta do câmbio deve prosseguir como resultado da valorização monetária, em vez de ser contida pela Caixa de Conversão.
  - argumento: A alta cambial é apresentada como resultado benéfico dos sacrifícios fiscais e da política de resgate e valorização, enquanto a estabilização proposta interromperia essa recuperação.
  - agentes: Congresso, David Campista
  - citação conferida: > muda subitamente do rumo o de-clara ao povo espantado que e in-dispensável coíilblr a alta do cam-blo, aquella altn salvadora para con-seguir a qual tantos sacrlíicH»; ex-Iglu !
  - observação do anotador: A janela começa no meio do texto e não permite determinar com segurança se a voz principal é editorial ou assinada.
- **lastro e conversibilidade da Caixa**
  - voz: `indeterminado`
  - objetos e direção: lastro (valorizacao), conversibilidade (valorizacao)
  - posição: A Caixa proposta é rejeitada por não converter o papel-moeda estatal nem possuir lastro próprio.
  - argumento: O texto contrapõe a Caixa ao programa gradual de resgate, valorização e garantia em ouro, cujo resultado esperado seria retirar a moeda do curso forçado e torná-la conversível à vista.
  - agentes: David Campista
  - citação conferida: > uma ealxa do conversãoquo não converta o papel-moeda doEstado, não dispõe de lastro seu oespora a incursão do ouro espon-tanoo, emitto bilhetes a uma taxa"predeterminada";
  - observação do anotador: A crítica ao lastro e à conversibilidade aparece junto de outras objeções ao desenho da Caixa.
- **credibilidade da reversão legislativa**
  - voz: `indeterminado`
  - objetos e direção: competencia_institucional (nao_classificavel)
  - posição: A mudança de orientação do Congresso retira credibilidade à sua condução da política monetária.
  - argumento: Segundo o texto, ao abandonar a política seguida por oito anos, o Congresso teria de admitir incompetência anterior ou temeridade presente.
  - agentes: Congresso
  - citação conferida: > Ouo Congresso affirma a sua iheompo-tencla pretérita, ou confessa n suatemeridade aetual. O quo parece delodo Inudmissivel 6 quo so reputecom direito a ser acreditado, querconfosse, quer affirme.
  - observação do anotador: A direção não é redutível às alternativas substantivas de valorização ou estabilização, pois o objeto imediato é a credibilidade institucional.

#### O Paiz, 1906, edição per178691_1906_08040, página 1

`per178691_1906_08040:p001:c8775-21557`, classe: só o Claude catalogou.

**claude**, 2 registro(s):

- **Fixar a taxa em 15 contra as leis que mandam buscar 27**
  - voz: `indeterminado`
  - objetos e direção: taxa (valorizacao), lastro (nao_aplica)
  - posição: O trecho ataca a fixação da taxa em 15 como contraditória, porque o país ficaria obrigado a trabalhar ao mesmo tempo para o câmbio subir a 27, pelas leis anteriores, e para não passar de 15, pela lei da caixa.
  - argumento: Campista justifica a fixação em 15 para impedir a alta do câmbio exterior, mas isso coloca o Brasil em situação em que as leis de resgate e garantia continuam vigorando ao lado da caixa, e nos moldes da economia antiga tal concepção não caberia, embora o autor a qualifique de cúpula do edifício financeiro e remate da obra de valorização.
  - agentes: Campista
  - citação conferida: > Para que essa fixação da taxa de15 ? O Sr. Campista respondo; paraImpedir a alta do cambio... oxte-rior.
  - observação do anotador: As datas das leis citadas como ainda vigentes estão corrompidas pelo OCR, aparecendo como loi de 194(1 e a de 1S3D, esta última descrita como a que instituiu os fundos de resgate e de garantia; por isso nenhum marco datado foi registrado. O objeto lastro entra apenas como menção aos fundos, sem posição própria no trecho.
- **Se a taxa nova constitui quebra do padrão monetário**
  - voz: `indeterminado`
  - objetos e direção: taxa (valorizacao)
  - posição: O trecho afirma que a conversão da emissão fiduciária a câmbio inferior é quebra do padrão, e que Campista errou ao negar que seu projeto a produza.
  - argumento: O artigo da lei argentina citada manda converter toda a emissão fiduciária de curso legal em moeda de ouro cunhado ao câmbio de um peso moeda de curso legal por 44 centavos de peso ouro, o que é quebra do padrão; diante disso Campista elaborou seu projeto afirmando que aqui não há quebra do padrão.
  - agentes: Campista
  - citação conferida: > E' n quebra do padiúo.Era presença de semelhante ia-cto o Sr. Campista elaborou o seuprojecto c aíürmoj : "Não hi que-bra do padrão", aqui, "seb o solcandente do Drazil".
  - observação do anotador: Entrada separada da anterior porque o desacordo aqui é sobre a caracterização do ato como quebra do padrão, não sobre o nível da taxa. A numeração do artigo da lei argentina invocado está ilegível no OCR.

**codex**: olhou e não catalogou nada.

### F2, 1907 a 1909, operação, lastro e alfândega

#### Correio da Manhã, 1907, edição per089842_1907_02028, página 1

`per089842_1907_02028:p001:c26270-32290`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### Correio da Manhã, 1907, edição per089842_1907_02097, página 1

`per089842_1907_02097:p001:c31126-37146`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### Correio da Manhã, 1907, edição per089842_1907_03017, página 1

`per089842_1907_03017:p001:c6402-12802`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### Correio Paulistano, 1907, edição per090972_1907_15588, página 2

`per090972_1907_15588:p002:c32986-39019`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### Correio Paulistano, 1907, edição per090972_1907_15619, página 1

`per090972_1907_15619:p001:c26636-36649`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### Correio Paulistano, 1909, edição per090972_1909_16496, página 2

`per090972_1909_16496:p002:c26892-33091`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### Gazeta de Notícias, 1907, edição per103730_1907_00013, página 6

`per103730_1907_00013:p006:c36709-44526`, classe: os dois catalogaram.

**claude**, 1 registro(s):

- **exigência de guias na emissão e resgate de notas conversíveis**
  - voz: `reproduzido_terceiro`
  - objetos e direção: conversibilidade (nao_classificavel), competencia_institucional (nao_classificavel)
  - posição: O ministro da fazenda defende manter a exigência de guias na tesouraria da Caixa de Conversão, contra as reclamações levantadas.
  - argumento: A providência não visa apurar falsificação de notas, mas facilitar a escrituração e orientar a estatística, permitindo ao governo saber a procedência do ouro depositado; alega ainda que o mesmo uso existe na Caixa de Conversão Argentina e em estabelecimentos bancários estrangeiros.
  - agentes: David Campista
  - citação conferida: > que tal providencia[oi adoplada o será mantida, não Imitopara se verificar qualquer falsificação dasnotas conversíveis, mas sim para facilitara escripluração o lieul orientar a eslalis-lica.
  - observação do anotador: Nome do ministro aparece corrompido pelo OCR ('üavid Ciun-pisla'); normalizado para David Campista apenas no campo agentes, não na citação. Declaração prestada a representante da Gazeta, portanto fala reproduzida de terceiro e não editorial. O restante da seção CAIXA DE CONVERSÃO é boletim de movimento e balancete, sem argumento, e não gerou entrada. A janela tem sangria pesada de colunas vizinhas (conferência sobre estradas de ferro, notas sociais, ocorrências policiais, espetáculos).

**codex**, 1 registro(s):

- **Exigência de guias nas operações da Caixa**
  - voz: `reproduzido_terceiro`
  - objetos e direção: outro (nao_classificavel)
  - posição: Defende a manutenção das guias exigidas para a emissão e o resgate de notas conversíveis.
  - argumento: A exigência facilitaria a escrituração, melhoraria a estatística e permitiria ao governo conhecer a procedência do ouro depositado. A adoção de guias em instituições argentinas e estrangeiras é apresentada como precedente.
  - agentes: David Campista
  - citação conferida: > tal providencia[oi adoplada o será mantida, não Imitopara se verificar qualquer falsificação dasnotas conversíveis, mas sim para facilitara escripluração o lieul orientar a eslalis-lica.
  - observação do anotador: O OCR apresenta corrupção no nome do ministro e em partes da justificativa. As reclamações que motivaram a declaração não são detalhadas.

#### Gazeta de Notícias, 1907, edição per103730_1907_00023, página 3

`per103730_1907_00023:p003:c21173-33278`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### Gazeta de Notícias, 1907, edição per103730_1907_00112, página 1

`per103730_1907_00112:p001:c36521-43373`, classe: os dois catalogaram.

**claude**, 4 registro(s):

- **Saída de ouro da Caixa indica falha ou funcionamento normal**
  - voz: `editorial_do_jornal`
  - objetos e direção: conversibilidade (nao_classificavel), lastro (nao_classificavel)
  - posição: O jornal sustenta que a primeira semana com saídas de ouro superiores às entradas na Caixa de Conversão não é motivo de estranheza, e sim prova de sua utilidade como reservatório de ouro da economia nacional.
  - argumento: Quando o ouro encarece por escassez de letras de câmbio, recorrer à Caixa trocando notas por ouro resolve a pressão sem abalos na praça, de modo que a retirada é uma das faces úteis do mecanismo.
  - marcos: 1907-04-20 (semana de 15 a 20 de abril de 1907, período coberto pelo balancete comentado da Caixa de Conversão)
  - citação conferida: > E' um facto dos mais naturaes, quo vemapenas revelar uma das faces uleis daCaixa do Conversão, esso grando reserva-torlo do ouro da economia nacional.
  - observação do anotador: A data do marco vem do cabeçalho '(IS A 20 DE ABRIL DE 1907)', com o dia inicial corrompido pelo OCR; os valores do balancete estão fortemente danificados pelo reconhecimento.
- **Quem deve dominar o mercado de câmbio no país**
  - voz: `editorial_do_jornal`
  - objetos e direção: competencia_institucional (nao_classificavel)
  - posição: O jornal defende que a direção do mercado cambial deve permanecer com o Banco do Brasil, e lamenta a possível saída de Custodio Coelho da carteira cambial, esperando que o governo lhe prorrogue a licença em vez de dispensá-lo.
  - argumento: Antes dessa direção nacional, o câmbio estava à mercê dos bancos estrangeiros e dos especuladores, que o faziam subir e descer conforme suas conveniências, e a aptidão do diretor da carteira cambial teria afastado esses agentes.
  - agentes: Custodio Coelho, Banco do Brasil
  - citação conferida: > c o Sr.Custodio Coelho os arredòu da direcçãód.-ssc mercado, tornando unico domina-dor do mosmo o Danço da Republica,mais tarde Banco do Brasil.
  - observação do anotador: O texto noticia o pedido de demissão por motivo de saúde sem datá-lo, por isso nenhum marco foi registrado.
- **Monopólio do Banco do Brasil sobre a expedição de vales-ouro**
  - voz: `editorial_do_jornal`
  - objetos e direção: competencia_institucional (nao_classificavel), alfandega (nao_aplica)
  - posição: O jornal critica o Banco do Brasil por monopolizar a expedição de vales-ouro e ainda exigir a assinatura de seus diretores, o que atrasa o serviço e empurra o público para a Caixa de Conversão.
  - argumento: A morosidade criada pelo monopólio e pela exigência de assinatura impede atender a todos os que recorrem ao banco, tornando mais expedito buscar o ouro diretamente na Caixa, o que explica parte do aumento das retiradas.
  - agentes: Banco do Brasil
  - citação conferida: > alim dc haver monopolisado esse serviço,ainda torna obrigatória a assignatura dosseus directores nos referidos vales
  - observação do anotador: O objeto alfandega foi listado apenas por proximidade temática dos vales-ouro no período, e marcado como nao_aplica porque a janela não trata da cobrança de direitos.
- **Alargar as compras oficiais de café ou suspender o acordo**
  - voz: `editorial_do_jornal`
  - objetos e direção: valorizacao_cafe (nao_classificavel)
  - posição: O jornal considera explicável a aflição dos commissarios, mas não acha acertado o pedido que apresenta ao governo a alternativa entre alargar as compras oficiais e suspender o acordo de valorização.
  - argumento: Alargar as compras exige dinheiro, e se São Paulo não as alargou mesmo agindo em conjunto com Minas e Rio, colocar o governo entre as duas pontas do dilema pode levá-lo a recuar.
  - agentes: Estado de São Paulo, commissarios
  - citação conferida: > não achamos Irancatnoiile acertado quero-rem os referidos commissarios collocar ogoverno entro as duas pontas do ura di-lemma
  - observação do anotador: A direção fica nao_classificavel porque o desacordo é sobre financiamento da valorização do café, não redutível ao eixo valorização cambial contra estabilidade a taxa nova. O trecho termina cortado no meio da frase sobre Minas e Rio.

**codex**, 1 registro(s):

- **Caixa como reservatório de ouro**
  - voz: `editorial_do_jornal`
  - objetos e direção: lastro (nao_classificavel), conversibilidade (nao_classificavel)
  - posição: A Caixa de Conversão é defendida como reserva útil de ouro, da qual se pode retirar metal mediante o troco de notas sem causar perturbações no mercado.
  - argumento: A saída líquida de ouro não seria motivo de estranheza, mas demonstração da utilidade da Caixa quando a escassez de letras de câmbio encarece o metal. As retiradas também são atribuídas à demora do Banco do Brasil na expedição de vales-ouro.
  - agentes: Banco do Brasil
  - citação conferida: > Nada ha em lal facto quo possa causarestranheza.E' um facto dos mais naturaes, quo vemapenas revelar uma das faces uleis daCaixa do Conversão, esso grando reserva-torlo do ouro da economia nacional.
  - observação do anotador: O trecho defende a função operacional da Caixa, mas não explicita preferência entre valorização do mil-réis e estabilidade em uma taxa nova; por isso, as direções foram classificadas como não classificáveis.

#### O Paiz, 1907, edição per178691_1907_08314, página 2

`per178691_1907_08314:p002:c28048-35562`, classe: os dois catalogaram.

**claude**, 1 registro(s):

- **Desmentido sobre sumiço de cédulas na Caixa de Conversão**
  - voz: `assinado`
  - objetos e direção: outro (nao_aplica)
  - posição: A direcção da Caixa de Conversão sustenta que não houve inquérito nem desaparecimento de cédulas conversíveis, e que a escripturação e o balanço semanal publicado comprovam o montante recolhido, o emittido e o saldo em cofre.
  - argumento: Invoca a contabilidade da repartição, 174.010:570$ recolhidos, 1.002:430$ inutilizados, 100.191:880$ emittidos e 73.350:690$ em cofre, e a possibilidade de exame das notas depositadas, para concluir que a notícia é infundada e que a confiança pública na repartição se mantém; o jornal, por sua vez, retrata-se atribuindo o erro de contagem à Caixa de Amortização.
  - agentes: Henrique Diniz, Carlos Cláudio da Silva, barão de Águas Claras
  - marcos: 1907-02-22 (ultimas remessas de cédulas conversíveis da Casa da Moeda à caixa de conversão)
  - citação conferida: > Posso felizmente assegurar-vos sercompletamente Infundada tal noticia,quer quando ella se refere a inque-rito, quer quanto a desappareciini.ntodo cedulae.
  - observação do anotador: Controvérsia administrativa sobre a gestão da Caixa, sem tomada de posição sobre taxa, lastro ou limite de emissão, por isso direcção nao_aplica. A janela mistura duas vozes no mesmo episódio, a carta assinada pelo vice-presidente e a retratação editorial do próprio jornal, registradas como um único debate. OCR degradado nos números e nos nomes; o texto está cortado ao fim e há colunas vizinhas sobre assuntos alheios.

**codex**, 1 registro(s):

- **Suposto desaparecimento de cédulas conversíveis**
  - voz: `assinado`
  - objetos e direção: outro (nao_aplica)
  - posição: A notícia sobre inquérito e desaparecimento de cédulas na Caixa de Conversão é infundada, pois as notas recebidas, emitidas, inutilizadas e depositadas estariam contabilizadas.
  - argumento: O vice-presidente apresenta os registros de entrada e emissão e afirma que o saldo de cédulas permanece depositado em um cofre da repartição. O jornal reconhece que o erro de contagem ocorreu na Caixa de Amortização, e não na Caixa de Conversão.
  - agentes: Dr. Henrique Diniz, Dr. Carlos Cláudio da Silva, barão de Águas Claras
  - marcos: 1907-02-22 (Últimas remessas de cédulas conversíveis pela Casa da Moeda à Caixa de Conversão)
  - citação conferida: > Posso felizmente assegurar-vos sercompletamente Infundada tal noticia,quer quando ella se refere a inque-rito, quer quanto a desappareciini.ntodo cedulae.
  - observação do anotador: A carta rebate uma acusação administrativa e não formula posição sobre taxa, emissão, lastro ou conversibilidade. Os valores têm possíveis erros de OCR e aparente inconsistência aritmética, por isso não foram corrigidos.

#### O Paiz, 1908, edição per178691_1908_08585, página 2

`per178691_1908_08585:p002:c4301-14198`, classe: os dois catalogaram.

**claude**, 4 registro(s):

- **Caixa é inútil; Banco do Brazil deveria assumir suas funções**
  - voz: `editorial_do_jornal`
  - objetos e direção: competencia_institucional (nao_classificavel), limite_emissao (estabilidade_taxa_nova)
  - posição: A Caixa de Conversão é um aparelho caro e supérfluo, e suas atribuições deveriam passar ao Banco do Brazil, que emitiria as notas conversíveis e abriria contas correntes em ouro e papel.
  - argumento: A única vantagem real da Caixa foi trazer 90.000 contos para a circulação, e essa mesma emissão poderia ter sido feita pelo Banco do Brazil com utilidade maior para o comércio, criando circulação ouro interna e evitando que os bilhetes fossem entesourados.
  - agentes: Dr. Campista, Banco do Brazil, Gazeta de Noticias
  - citação conferida: > a caixa dê conversão é umainstituição quasi inútil e dispendiosa,cujas attribuições podiam ser desempenha-das com vantagem pelo Banco do Brazil.
  - observação do anotador: A direção em competencia_institucional não é redutível ao eixo valorização/estabilidade: o jornal disputa o desenho institucional, não o nível da taxa. OCR com quebras de sílaba dentro das palavras.
- **Retiradas de ouro da Caixa ameaçam ou não a instituição**
  - voz: `editorial_do_jornal`
  - objetos e direção: lastro (nao_classificavel), conversibilidade (nao_classificavel)
  - posição: As fortes retiradas de ouro, desproporcionais aos depósitos, não têm significação alarmante, e mesmo o esvaziamento total do depósito não traria inconveniente econômico ou financeiro.
  - argumento: Como a instituição é considerada quase inútil, o volume de seu depósito em ouro seria indiferente; o alarme das aves de mau agouro em torno da Caixa não se justifica.
  - agentes: Gazeta de Noticias
  - citação conferida: > isso nada quer dizer e, mesmo que a cai-xa ficasse sem uma libra
  - observação do anotador: O Paiz declara acordo com a Gazeta neste ponto específico, e discorda dela nos demais.
- **Pagamento de direitos aduaneiros: vales ouro ou notas conversíveis**
  - voz: `editorial_do_jornal`
  - objetos e direção: alfandega (nao_classificavel)
  - posição: As alfândegas deveriam receber os bilhetes conversíveis da Caixa em pagamento dos direitos, acabando com o regime dos vales ouro.
  - argumento: Os vales ouro constituem uma terceira moeda artificial, absurda e complicada, que cria embaraços ao comércio e exige escrituração dispensável nos bancos emissores e nas repartições da fazenda; receber notas conversíveis daria aplicação útil à emissão e levaria o Tesouro a deter os depósitos da Caixa.
  - agentes: Dr. Campista
  - citação conferida: > recebessem os bi-lhetes conversiveis para pagamento dosdireitos aduaneiros, acabando com esseregimen condemnado e laborioso dos valesouro.
  - observação do anotador: Medida de circulação e arrecadação, sem tomar posição explícita sobre o nível da taxa, por isso nao_classificavel.
- **A fixidez do câmbio é ou não mérito da Caixa**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (nao_classificavel)
  - posição: Atribuir à Caixa de Conversão a fixidez do câmbio, o aumento da importação e a melhora da fiscalização aduaneira é alegação infantil.
  - argumento: O jornal nega o nexo causal alegado pela Gazeta, mas não afirma no trecho qual seria a taxa desejável nem defende alteração dela.
  - agentes: Gazeta de Noticias
  - citação conferida: > de serdevida á caixa a fixidez do cambio eaugmentos de importação e fiscalizaçãoaduaneira, etc, nem vale a pena tratardisso, de tal modo é infantil a allegação
  - observação do anotador: Disputa sobre atribuição causal da estabilidade cambial, não sobre o nível da taxa; por isso nao_classificavel no eixo valorização/estabilidade.

**codex**, 5 registro(s):

- **Risco das retiradas de ouro**
  - voz: `editorial_do_jornal`
  - objetos e direção: lastro (nao_classificavel)
  - posição: As retiradas de ouro, mesmo que esvaziassem a Caixa, não produziriam inconveniente econômico ou financeiro.
  - argumento: A Caixa é apresentada como instituição quase inútil, dispendiosa e substituível pelo Banco do Brasil.
  - citação conferida: > mesmo que a cai-xa ficasse sem uma libra, nenhum incon-.eniente de ordem econômica ou finan-ceira d'ahi podia advir, pela simples ra-/ão de que a caixa dê conversão é umainstituição quasi inútil e dispendiosa
  - observação do anotador: O OCR fragmenta palavras e torna ilegível parte da palavra correspondente a inconveniente.
- **Transferência das atribuições da Caixa**
  - voz: `editorial_do_jornal`
  - objetos e direção: competencia_institucional (nao_classificavel)
  - posição: As atribuições da Caixa de Conversão deveriam passar ao Banco do Brasil.
  - argumento: O Banco do Brasil poderia emitir as notas conversíveis e associá-las a operações comerciais, sem manter um aparelho burocrático separado.
  - agentes: Banco do Brazil
  - citação conferida: > Em resumo: parece-nos que haveriatoda a vantagem em passar as attribuiçõesda caixa de conversão para o Banco doBrazil
- **Notas conversíveis nos direitos aduaneiros**
  - voz: `editorial_do_jornal`
  - objetos e direção: alfandega (nao_classificavel)
  - posição: As alfândegas deveriam aceitar notas conversíveis no pagamento dos direitos aduaneiros e abandonar os vales ouro.
  - argumento: O regime dos vales ouro é descrito como complicado, oneroso para o comércio e gerador de escrituração dispensável.
  - agentes: Dr. Campista
  - citação conferida: > orde-nantlo ás alfândegas que recebessem os bi-lhetes conversiveis para pagamento dosdireitos aduaneiros, acabando com esseregimen condemnado e laborioso dos valesouro.
  - observação do anotador: A palavra inicial da citação apresenta erro de OCR.
- **Contas correntes em ouro**
  - voz: `editorial_do_jornal`
  - objetos e direção: outro (nao_classificavel)
  - posição: O Banco do Brasil deveria estabelecer contas correntes em ouro.
  - argumento: As contas permitiriam empregar as notas conversíveis em operações comerciais e favorecer uma circulação de ouro no país.
  - agentes: Banco do Brazil
  - citação conferida: > O Banco do Brazil que estabeleça ascontas correntes em ouro.
- **Caixa como causa da fixidez cambial**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (nao_aplica)
  - posição: A Caixa de Conversão não deve ser considerada responsável pela fixidez do câmbio.
  - argumento: O texto rejeita como infantil a alegação atribuída à Gazeta de que a Caixa teria causado a fixidez cambial e outros resultados econômicos.
  - agentes: Gazeta
  - citação conferida: > Quanto a essa.pilhéria, que os collegasda Gazeta põem em circulação, de serdevida á caixa a fixidez do cambio eaugmentos de importação e fiscalizaçãoaduaneira, etc, nem vale a pena tratardisso, de tal modo é infantil a allegação-
  - observação do anotador: O trecho contesta uma atribuição causal, mas não defende um nível específico para a taxa de câmbio.

#### O Paiz, 1909, edição per178691_1909_08983, página 2

`per178691_1909_08983:p002:c8829-18014`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

### F3, 1910 a 1913, taxa de 16 dinheiros e ampliação do limite

#### Correio da Manhã, 1910, edição per089842_1910_03211, página 2

`per089842_1910_03211:p002:c0-7390`, classe: os dois catalogaram.

**claude**, 3 registro(s):

- **Mudar o padrão de emissão da Caixa ou conservar a taxa**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova), limite_emissao (nao_classificavel)
  - posição: O artigo sustenta que a taxa atual das emissões da Caixa pode e deve ser conservada, contra os que pedem mudança urgente do padrão.
  - argumento: Os adversários alegam que continuar emitindo à taxa atual desvaloriza o meio circulante inconversível e só beneficia os produtores; o artigo replica que a lei diz apenas que a taxa PODERÁ ser alterada quando os depósitos atingirem 20 milhões esterlinos, e que a falta de obrigatoriedade pressupõe a conveniência de conservá-la.
  - citação conferida: > sc toma urgente mudar o padrão dasemissões da Caixa dc Conversão.
  - observação do anotador: O trecho citado enuncia a posição dos adversários; a posição do jornal aparece adiante, na leitura do 'PODERÁ' da lei. OCR muito degradado nesse ponto, o que impediu citar o período sobre a facultatividade.
- **Se o stock de ouro da Caixa é excessivo para o país**
  - voz: `editorial_do_jornal`
  - objetos e direção: lastro (estabilidade_taxa_nova)
  - posição: O stock de ouro acumulado na Caixa é insuficiente, não excessivo, e não desvaloriza o meio circulante inconversível.
  - argumento: Compara com a Argentina, que teria mais do dobro do limite máximo da Caixa brasileira com território menor e um terço da população, e usa como prova indireta o juro, que na Argentina cai a 5 a 7 por cento enquanto no Brasil se conserva alto, a 8 por cento no mínimo, sinal de que não há pletora de ouro no país.
  - citação conferida: > O slock do ouro actnal na nossa Caixade Conversão é, na opinião destes, inferiorao de que necessita o Brasil.
  - observação do anotador: O artigo anuncia que em artigo subsequente tratará dos meios pelos quais a especulação teria acumulado ouro na Caixa, tema não desenvolvido nesta janela.
- **Efeito do câmbio de 16 dinheiros sobre a receita em ouro**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova), alfandega (nao_classificavel)
  - posição: Elevar o câmbio a 16 dinheiros obrigaria a aumentar muito os impostos em ouro para manter a mesma receita em papel, onerando o comércio importador e o consumidor.
  - argumento: Pelo orçamento vigente as receitas em ouro excedem a despesa na mesma espécie em cerca de 48.000 contos, que o Tesouro revende para fazer face à despesa em moeda corrente; ao câmbio de 16 dinheiros esse excesso teria de subir a cerca de 65.000 contos, o que o artigo comenta com ironia.
  - citação conferida: > Segundo o orçamento vigente, a? receitaseni ouro excedem
  - observação do anotador: Os números aparecem corrompidos pelo OCR (48.000 contos legível, o segundo valor sai como 'ft-,000'). A direção quanto à alfândega ficou como não classificável porque o trecho discute o efeito fiscal sem defender regime de cobrança.

**codex**, 3 registro(s):

- **Excesso do estoque de ouro**
  - voz: `editorial_do_jornal`
  - objetos e direção: lastro (nao_classificavel), taxa (estabilidade_taxa_nova)
  - posição: O estoque de ouro não é excessivo e a emissão à taxa atual não desvaloriza o meio circulante.
  - argumento: A persistência de juros elevados e a demanda por capitais indicariam que o estoque metálico ainda é insuficiente para as necessidades econômicas brasileiras.
  - citação conferida: > O slock do ouro actnal na nossa Caixade Conversão é, na opinião destes, inferiorao de que necessita o Brasil..
  - observação do anotador: O início da janela está cortado. O texto contrapõe adversários e defensores da Caixa e, em seguida, desenvolve argumentos favoráveis aos defensores.
- **Obrigatoriedade de alterar a taxa**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova), limite_emissao (nao_classificavel), competencia_institucional (nao_classificavel)
  - posição: A lei permite, mas não obriga, a alteração da taxa quando os depósitos atingem o limite mencionado.
  - argumento: A ausência de determinação imperativa na lei é apresentada como fundamento para conservar a taxa vigente.
  - citação conferida: > Apenas dispõe que PODKRA1<er -Itei-.ida. A falia dc obrigatoriedade daílltitlííteacíni do cambio da Caixa presuppSca p»i*siliilidiide dc ser conveniente cousrr-1:11 a taxa actual.
  - observação do anotador: O OCR está muito corrompido, mas a oposição entre possibilidade e obrigatoriedade de alteração permanece legível.
- **Efeito fiscal do câmbio de 16 dinheiros**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (valorizacao), alfandega (nao_classificavel)
  - posição: O texto rejeita a valorização do câmbio a 16 dinheiros por exigir maior arrecadação de impostos em ouro.
  - argumento: Para manter a receita do Tesouro em papel com o câmbio de 16 dinheiros, seria necessário elevar o excedente das receitas em ouro, transferindo o ônus ao comércio importador e ao consumidor.
  - citação conferida: > Para obter ,1rticsitm receita rrti papel, ao cambio de 16 d.,í necessário que os impostos cm ouro, emve* de (M-ulercm a despeja rui 48.000 con-tn». a excedam em ft-,000 contos, numerosredondos.
  - observação do anotador: Os valores numéricos e algumas palavras estão parcialmente ilegíveis por falhas de OCR.

#### Correio da Manhã, 1910, edição per089842_1910_03388, página 1

`per089842_1910_03388:p001:c19566-33229`, classe: os dois catalogaram.

**claude**, 3 registro(s):

- **Banco do Brasil compra libras a 16$ contra taxa legal de 15**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (nao_classificavel), conversibilidade (nao_classificavel), competencia_institucional (nao_classificavel)
  - posição: Denuncia como ilegal e ruinosa a retirada de um milhão esterlino da Caixa ao câmbio de 16$, quando a lei e a própria nota fixam 15, atribuindo o prejuízo de 2.850 contos ao Thesouro.
  - argumento: A Caixa de Conversão só opera ao câmbio de 15 por determinação legal impressa nas notas, de modo que a operação a 16$ não tem amparo em lei e a perda recai sobre o Thesouro, isto é, sobre o país, por capricho de um homem.
  - agentes: Banco do Brasil, ministro da Fazenda
  - citação conferida: > E' sabido, é de lei, que a Caixa de Con-versão só opera ao cambio de 15; em cadanota emittida pela Caixa isso mesmo estáescripto.
  - observação do anotador: Trecho de coluna polêmica não assinada, aparentemente 'Pingos e Respingos'; o ministro da Fazenda não é nomeado na janela. Números do prejuízo aparecem em duas versões no OCR (2.850 contos e 'tres mil contos').
- **Intervenção do ministro para forçar a alta contra a taxa nova de 16 dinheiros**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova), lastro (nao_classificavel)
  - posição: Acusa o ministro da Fazenda de burlar o acordo de fixar em 16 dinheiros a nova taxa da Caixa e de empenhar as reservas metálicas do Thesouro para forçar artificialmente a alta do câmbio.
  - argumento: Forçar a alta serviu à vaidade do ministro e à desmoralização da Caixa, contra o protesto das classes produtoras, e a alegação de combate à especulação é falsa, porque não há especulação baixista sem altista e um banco que sacasse e se cobrisse de imediato não teria prejuízo.
  - agentes: ministro da Fazenda, marechal Hermes, classes productoras, Sattamini, Castro Maya, Wileman
  - citação conferida: > fixarem .t6 dinheiros a nova taxa da Caixa deConversão, a despeito dos protestos' dasclasses prodttcloras.
  - observação do anotador: OCR corrompe 16 como '.t6' e o pronome de tratamento; a atribuição de posição ao jornal supõe que a coluna é comentário próprio e não matéria reproduzida, o que a janela não confirma.
- **Defesa da Caixa como anteparo contra a queda do câmbio**
  - voz: `editorial_do_jornal`
  - objetos e direção: conversibilidade (estabilidade_taxa_nova), taxa (estabilidade_taxa_nova)
  - posição: Sustenta que a Caixa de Conversão impede a queda do câmbio, a ponto de o próprio adversário do aparelho ter sido obrigado a recorrer a ela.
  - argumento: O Banco pagou 16$ porque não encontrava ouro por 15, 14 ou 13 mil réis na praça; sem a Caixa teria pago ainda mais caro, o que prova que o aparelho sustenta a taxa que presidiu sua criação.
  - agentes: Banco do Brasil
  - citação conferida: > E eis ahi como esse apparelho tao guer-reado impede de cair o cambio que lhe pre-sidiu a creação
  - observação do anotador: O 'próprio homem que mais o combateu' não é nomeado na janela, embora o contexto sugira o ministro da Fazenda.

**codex**, 3 registro(s):

- **Caixa como barreira à queda cambial**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Defende que a Caixa de Conversão impede a queda do câmbio abaixo da taxa que orientou sua criação.
  - argumento: A dificuldade do Banco do Brasil para obter ouro por preço inferior ao da Caixa é apresentada como evidência de que o mecanismo sustenta a taxa cambial.
  - agentes: Banco do Brasil, Caixa de Conversão
  - citação conferida: > E eis ahi como esse apparelho tao guer-reado impede de cair o cambio que lhe pre-sidiu a creação
  - observação do anotador: A taxa e alguns valores monetários aparecem parcialmente corrompidos pelo OCR.
- **Intervenção para forçar a alta cambial**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova), lastro (nao_classificavel)
  - posição: Condena a intervenção destinada a forçar a alta do câmbio e defende conter a taxa próxima do nível anteriormente combinado.
  - argumento: O texto afirma que o ministro mobilizou reservas do Tesouro para elevar artificialmente o câmbio, apesar do acordo sobre uma nova taxa e dos protestos das classes produtoras.
  - agentes: ministro da Fazenda, Banco do Brasil, classes prodttcloras
  - citação conferida: > motivada pela intervenção do ministro nomercado, com o fim de forçar a alta docambio.
  - observação do anotador: O nome do ministro não aparece de forma identificável na janela. A grafia da taxa combinada está corrompida pelo OCR, embora o contexto indique valor próximo de 16 dinheiros.
- **Legalidade do prejuízo imposto ao Tesouro**
  - voz: `editorial_do_jornal`
  - objetos e direção: lastro (nao_classificavel), competencia_institucional (nao_classificavel)
  - posição: Sustenta que o ministro não tinha fundamento legal para impor ao Tesouro as perdas da operação cambial.
  - argumento: A diferença entre o preço de compra e o preço de venda das libras é apresentada como perda colossal suportada pelo Tesouro, associada ao capricho e à intervenção do ministro.
  - agentes: ministro da Fazenda, Tliesotiro, Banco do Brasil
  - citação conferida: > A lei ? Não ha lei para o figurante de tacsaventuras
  - observação do anotador: Os valores da operação apresentam inconsistências de OCR. A crítica à competência institucional é formulada como ausência de direito e de lei, sem indicação de norma específica.

#### Correio da Manhã, 1910, edição per089842_1910_03449, página 2

`per089842_1910_03449:p002:c22393-40752`, classe: só o Claude catalogou.

**claude**, 5 registro(s):

- **Elevar a taxa da Caixa para 16 ou mantê-la em 15**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Defende a permanência da taxa cambial de 15 dinheiros e apresenta substitutivo contra o projeto da maioria da Commissão de Finanças, que a eleva a 16.
  - argumento: Quatro anos de estabilidade a 15 trouxeram tranquilidade monetária, entrada de capital estrangeiro e prosperidade, de modo que mexer na taxa reintroduziria a instabilidade cambial e seus efeitos imediatos sobre a economia; a fixidez vale mais que a contingência das altas.
  - agentes: Galeão Carvalhal, Leopoldo de Bulhões, Honorio Gurgel, Duarte de Abreu, Rodolpho Paixão, Barbosa Lima
  - marcos: 1910-11-22 (Discurso pronunciado na Câmara abrindo o debate sobre o projeto da Commissão de Finanças); 1906-12-06 (Lei que instituiu a Caixa de Conversão, cujo art. 9 transferiu para ela os fundos de resgate e de garantia)
  - citação conferida: > E' opporttino declarar que não -_tamo_pleiteando o cambi- baixo; defendemos aestabilidade na taxa de 15 cem o naturalreceio da instabilidade c seus resultadosimmediatos na economia nacional.
  - observação do anotador: O texto oscila entre 13 e 15 dinheiros ao designar a taxa vigente, provavelmente por erro de OCR ou de composição; a taxa de criação citada adiante é de 15 dinheiros esterlinos por mil réis.
- **Ampliação da emissão conversível além do limite legal**
  - voz: `discurso_parlamentar`
  - objetos e direção: limite_emissao (estabilidade_taxa_nova)
  - posição: Registra e endossa a posição de que a emissão a cargo da Caixa deve ser ampliada além do limite prescrito, mantida a taxa.
  - argumento: A lógica do próprio sistema autorizaria emissões conversíveis acima do limite, e a ampliação é urgente porque a Caixa caminhava rapidamente para completar o limite de emissão; Campista e Rui Barbosa, antes favoráveis à elevação periódica do câmbio, convergiram para a permanência da taxa com ampliação da emissão.
  - agentes: David Campista, Ruy Barbosa
  - citação conferida: > O conselheiro Riiy Barbosa na sua pia-tafor-ma támbcm ndoptou a me.má' opi-mão, affirmartdo ' que a lógica do sy.lcmaautorisa as emissões conversíveis alem dolimite presenipto.
  - observação do anotador: Trecho muito corrompido pelo OCR, inclusive no nome do orador citado e em "limite presenipto" (limite prescripto).
- **Papel dos fundos de garantia e de resgate na valorização do papel**
  - voz: `discurso_parlamentar`
  - objetos e direção: lastro (nao_classificavel)
  - posição: Sustenta que a valorização do papel de curso forçado resultou do resgate, e não do fundo de garantia, ao mesmo tempo em que elogia a lei de 1899 que instituiu os dois fundos.
  - argumento: O resgate retirou de circulação quantidades tidas por excessivas de papel, enquanto o fundo de garantia formava o lastro ouro para conversão futura; a fixidez da taxa teria vindo do primeiro mecanismo, não do segundo, cujas vantagens o orador diz não estarem demonstradas.
  - agentes: Galeão Carvalhal, Lindolpho Câmara
  - marcos: 1899-06-20 (Lei n. 581, que instituiu os fundos de garantia e de resgate do papel moeda)
  - citação conferida: > si elle st manteve fixo naquella taxa, íoiantes como conseqüência do resgate e nãoem virtude do fundo de garantia
  - observação do anotador: O aparte de Lindolpho Câmara introduz uma terceira causa, os empréstimos externos, e a resposta do orador fica cortada no fim da janela.
- **Delegar ao Executivo o poder de elevar a taxa da Caixa**
  - voz: `discurso_parlamentar`
  - objetos e direção: competencia_institucional (nao_classificavel), taxa (valorizacao)
  - posição: Reproduz o pedido da exposição de Leopoldo de Bulhões para que o Poder Executivo receba capacidade legal de proceder a sucessivas elevações da taxa cambial da Caixa.
  - argumento: As elevações sucessivas seriam feitas de acordo com as condições gerais do país, o desenvolvimento da atividade industrial, a valorização crescente do papel moeda e a massa de ouro depositada.
  - agentes: Leopoldo de Bulhões, presidente da Republica
  - citação conferida: > (r) conferir-se ao Poder Exe-' ctitivo capacidade legal .paraproceder a suecessivas eleva-ções da taxa cambial cstabelc-cida na Caixa de áccòrdo comas condições geraes do paiz
  - observação do anotador: A voz é do deputado que transcreve item de documento oficial em seu discurso; a proposta é de Bulhões, não do orador, que se opõe às elevações. A mensagem é datada apenas como do mês de abril do corrente ano.
- **Estabilidade cambial como condição da valorização do café**
  - voz: `discurso_parlamentar`
  - objetos e direção: valorizacao_cafe (estabilidade_taxa_nova), taxa (estabilidade_taxa_nova)
  - posição: Defende que a Caixa foi criada como peça do programa do Convênio de Taubaté, para dar estabilidade cambial e proteger a produção exportável contra a alta do câmbio.
  - argumento: O empréstimo de 15 milhões de libras influiria diretamente sobre o câmbio elevando suas taxas e alterando os preços nos mercados nacionais, e qualquer alta vertiginosa acarretaria prejuízos avultados à lavoura, de modo que o câmbio a 15 é protecionista da produção nacional.
  - agentes: Jorge Tibiriçá, Francisco Salles, Nilo Peçanha
  - marcos: 1906-02-25 (Celebração do Convênio de Taubaté); 1903-12-30 (Lei de orçamento da receita que autorizou o governo a acordar com os estados cafeeiros sobre valorização do café)
  - citação conferida: > na verdade qualquer alta vertigirro-sa do cambio acarretaria prejuízos avultado3.
  - observação do anotador: O empréstimo é citado como de 15 milhões de libras com garantia da sobretaxa ouro e responsabilidade solidária de três estados, sem data no trecho.

**codex**: olhou e não catalogou nada.

#### Correio Paulistano, 1910, edição per090972_1910_16872, página 8

`per090972_1910_16872:p008:c18037-28832`, classe: só o Claude catalogou.

**claude**, 3 registro(s):

- **Quebra do padrão fere ou não compromissos externos**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova), divida_externa (nao_aplica)
  - posição: Defende que fixar legalmente uma taxa mais baixa, isto é quebrar o padrão, é medida interna legítima e não desonra o país perante credores estrangeiros.
  - argumento: As dívidas externas são pagas em ouro sob qualquer padrão, de modo que a alteração é apenas de letreiros de títulos monetários, um arranjo do país consigo mesmo; outros países, Rússia, França, Inglaterra, Áustria, quebraram o padrão, e o escrúpulo dos adversários é espantalho que encobre a espoliação dos produtores.
  - agentes: sr. ministro da fazenda
  - citação conferida: > as dividas externas são pa-gas em ouro, e, portanto não mu-dam absolutamente do situação paracpmnoscp
  - observação do anotador: Texto de OCR muito corrompido, com palavras concatenadas e hifenização de linha preservada. O trecho é a continuação de um artigo cujo início não está na janela; a numeração romana IV indica seção de série editorial.
- **Câmbio livre impede acumular ouro e desarma o país**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova), lastro (estabilidade_taxa_nova), limite_emissao (estabilidade_taxa_nova), competencia_institucional (nao_classificavel)
  - posição: Defende manter a Caixa de Conversão funcionando com taxa limite fixa de 15, contra o projeto do ministro da fazenda que eleva o limite da taxa e deixa o câmbio subir.
  - argumento: Pela lei de Gresham, moeda que flutua é moeda má e afugenta o ouro, de modo que país de câmbio livre não retém nem acumula metal; a Caixa, com taxa impedida de subir, injetou notas-ouro e permitiu reunir 20 milhões esterlinos, e sem reservas metálicas o país fica indefeso numa guerra, pois o câmbio alto cai no dia seguinte e os navios não servem sem ouro.
  - agentes: sr. ministro da fazenda, Napoleão, Gresham
  - citação conferida: > meios do inutilisar o Caixa do Con-versão é elevar o limito do sim taxacambial
  - observação do anotador: A janela menciona a compra por ingleses e franceses de ações da Mogyana e da Paulista e empréstimos recentes como causas da entrada de ouro, sem data. Diz que as emissões da Caixa cessaram, sem indicar quando.
- **Alta cambial atual e volta à taxa de 15**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova), valorizacao_cafe (nao_classificavel)
  - posição: Defende que a alta do câmbio para perto de 17 é acidental e não constitui obstáculo, mas sim motivo adicional para restabelecer prontamente a taxa de 15.
  - argumento: Toda a estrutura econômica e os adiantamentos da colheita se acomodaram à taxa de 15, e a alta, resultante de ofertas acidentais de ouro e de operações antecipadas sobre a safra de café, arranca cerca de dez por cento aos lavradores, muitos dos quais não apuravam nem oito por cento; quanto mais subir o câmbio, mais atingidos ficam e maior o direito a compensação.
  - agentes: sr. ministro da fazenda
  - citação conferida: > está so elevando, otiranüo sobreos ip.pbrPs lavradores préjuizos queos esmagam o liquidam
  - observação do anotador: A janela é cortada no fim, em meio ao cálculo sobre a média de 21 dinheiros atribuída ao ministro. A referência a taxa já estabelecida por lei ha 3 ou 6 mezes não é datada explicitamente, por isso não virou marco.

**codex**: olhou e não catalogou nada.

#### Correio Paulistano, 1910, edição per090972_1910_17028, página 9

`per090972_1910_17028:p009:c0-20842`, classe: os dois catalogaram.

**claude**, 3 registro(s):

- **Manter a taxa em 15 ou elevá-la a 16 dinheiros**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Defende a manutenção da estabilidade cambial na taxa de 15 dinheiros, divergindo do projeto da maioria da comissão de Finanças que eleva a taxa a 16.
  - argumento: Quatro anos de tranquilidade monetária a 15 trouxeram capitais estrangeiros, crédito e crescimento das receitas; a fixidez vale mais que a contingência das altas, cujos ganhos não compensam os riscos da instabilidade, e o câmbio a 15 protege a produção nacional.
  - agentes: Galeão Carvalhal, David Campista, Honorio Gurgel, Duarte de Abreu
  - marcos: 1906-02-25 (Celebração do Convênio de Taubaté, assinado por Jorge Tibiriçá, Francisco Salles e Nilo Peçanha)
  - citação conferida: > opportuno declarar quo nao esta-mos pleiteando o cambio baixo; d.fon-demos a estabilidado nn taxa do 15
  - observação do anotador: OCR muito degradado; o início da frase aparece como ",1-", provavelmente "É". O discurso é reproduzido na íntegra pelo jornal, que apenas o apresenta como importante, sem tomar posição própria na janela.
- **Restaurar os fundos de garantia e de resgate do papel-moeda**
  - voz: `discurso_parlamentar`
  - objetos e direção: lastro (nao_classificavel)
  - posição: Defende restituir ao fundo de garantia a função originária fixada na lei de 20 de junho de 1899 e restaurar os fundos de garantia e de resgate nos termos das leis que os instituíram.
  - argumento: A lei de 1899 foi lei sábia porque de um lado diminuía a massa de papel em circulação e de outro formava o lastro-ouro para a futura conversão; foi o resgate, e não o fundo de garantia, que determinou a valorização do papel de curso forçado.
  - agentes: Galeão Carvalhal, Leopoldo de Bulhões, Campos Salles, Joaquim Murtinho
  - marcos: 1899-06-20 (Lei n. 581, que institui os fundos de resgate e de garantia do papel-moeda); 1906-12-06 (Lei que cria a Caixa de Conversão e, pelo art. 9º, transfere para ela os fundos de resgate e de garantia); 1905-12-30 (Lei de orçamento da receita geral que autoriza o governo a acordar com os Estados cafeeiros)
  - citação conferida: > rcstitúir no fundo de garantiua sua. funeção originaria marcada nalei do 20 de junho de 1899
  - observação do anotador: Direção marcada como não classificável: o trecho defende os fundos como instrumento consensual e atribui a valorização do papel ao resgate, mas o orador nega pleitear apreciação cambial, o que impede reduzir a posição a uma das duas direções. Trecho da lei aparece transcrito em bloco fora de ordem na coluna.
- **Delegar ao Executivo elevações sucessivas da taxa**
  - voz: `discurso_parlamentar`
  - objetos e direção: competencia_institucional (nao_classificavel), taxa (valorizacao)
  - posição: A exposição que acompanhou a mensagem presidencial pede que se confira ao Poder Executivo capacidade legal para proceder a elevações sucessivas da taxa cambial estabelecida na Caixa.
  - argumento: As elevações se fariam de acordo com as condições gerais do país, o desenvolvimento da atividade industrial, a valorização crescente do papel-moeda e a massa de ouro que solicitar depósito.
  - agentes: Leopoldo de Bulhões, presidente da Republica
  - citação conferida: > con feri r-so ap Poder Executivocâpaoidado legal unia proceder a sue-cessivas elevações da taxa cnnibinl
  - observação do anotador: Pedido enumerado dentro do discurso, item c) da exposição de Bulhões; a voz registrada é a do discurso parlamentar que o enumera, não a do documento original. OCR corrompido em "con feri r-so ap" e "capacidade legal para".

**codex**, 7 registro(s):

- **Manutenção da taxa de quinze dinheiros**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Galeão Carvalhal defende a estabilidade cambial na taxa de quinze dinheiros.
  - argumento: A alteração da taxa produziria instabilidade e efeitos imediatos prejudiciais à economia nacional.
  - agentes: Galeão Carvalhal
  - citação conferida: > pleiteando o cambio baixo; d.fon-demos a estabilidado nn taxa do 15 com onatural recoio dn instabilidao o seus re-saltados inimcdiatos na economia nacio-nal.
  - observação do anotador: O início da frase está parcialmente corrompido pelo OCR.
- **Ampliação da emissão da Caixa**
  - voz: `discurso_parlamentar`
  - objetos e direção: limite_emissao (estabilidade_taxa_nova)
  - posição: Defende-se ampliar a emissão da Caixa de Conversão mantendo a taxa de quinze dinheiros.
  - argumento: A ampliação permitiria conservar o regime cambial existente sem elevar a taxa de emissão.
  - agentes: David Campista, Galeão Carvalhal
  - citação conferida: > O dr. David Campista;o relator do parecor sobro o projecto, loio primeiro a reconhecer a conveniênciada pbrmanonoia da taxa do 15 dinheiros,sondo urgoiito a ampliação da omissão acargo da Caixa do Conversão.
  - observação do anotador: A posição de David Campista é apresentada por Galeão Carvalhal.
- **Fundos de garantia e resgate**
  - voz: `discurso_parlamentar`
  - objetos e direção: lastro (nao_classificavel)
  - posição: Defende-se a manutenção dos fundos de garantia e de resgate do papel-moeda.
  - argumento: Os fundos reduziriam o papel em circulação e formariam lastro em ouro para uma conversão futura.
  - agentes: Galeão Carvalhal
  - marcos: 1899-06-20 (Lei institui os fundos de resgate e de garantia do papel-moeda)
  - citação conferida: > Doum lado diminuía a massa do papel omi-irculação e de outro lado formava o las-tro-ouro para a futura conversão.
- **Conversibilidade contra especulação cambial**
  - voz: `discurso_parlamentar`
  - objetos e direção: conversibilidade (estabilidade_taxa_nova)
  - posição: Defende-se a emissão de notas conversíveis como instrumento de estabilidade cambial.
  - argumento: A conversibilidade produziria equilíbrio e reduziria a exposição da carteira cambial à especulação associada ao papel de curso forçado.
  - agentes: Galeão Carvalhal
  - citação conferida: > A omia-são do notas convertivois trazia o neces-sario equilibriò, o a carteira cambial selibertar., das garras da especulação.
- **Delegação das elevações da taxa**
  - voz: `documento_oficial`
  - objetos e direção: competencia_institucional (nao_classificavel), taxa (valorizacao)
  - posição: A exposição que acompanhou a mensagem presidencial propõe autorizar o Poder Executivo a elevar sucessivamente a taxa da Caixa.
  - argumento: As elevações seriam realizadas de acordo com as condições do país, a atividade industrial, a valorização do papel-moeda e os depósitos de ouro.
  - agentes: Leopoldo do Bulhões
  - citação conferida: > con feri r-so ap Poder Executivocâpaoidado legal unia proceder a sue-cessivas elevações da taxa cnnibinl
  - observação do anotador: A proposta oficial é reproduzida dentro do discurso parlamentar.
- **Estabilidade cambial e valorização do café**
  - voz: `discurso_parlamentar`
  - objetos e direção: valorizacao_cafe (nao_classificavel)
  - posição: Defende-se a estabilidade cambial como proteção das operações destinadas à valorização do café.
  - argumento: A alta abrupta do câmbio poderia alterar os preços internos e causar grandes prejuízos às operações financiadas pelo empréstimo.
  - agentes: Galeão Carvalhal
  - marcos: 1906-02-25 (Celebração do Convênio de Taubaté)
  - citação conferida: > Procurando valorizar o café no exto-rior, o grando empréstimo influindo di-rectíimente sobro o cambio o elevando «ibsuns taxas; podia modificar os proços nosmercados nacionaes, arrebatando as sunsdiferença, cm papel, o na vordado qual-quer alta vertiginosa do cambio ncarrota-ria projuizos avultados.
  - observação do anotador: O ano do Convênio aparece parcialmente corrompido no OCR, mas é indicado no contexto imediato como 1906.
- **Moratória do Funding-loan**
  - voz: `discurso_parlamentar`
  - objetos e direção: divida_externa (nao_classificavel)
  - posição: Galeão Carvalhal declara ter apoiado a moratória associada ao Funding-loan.
  - argumento: A moratória é apresentada como medida que salvou a situação financeira e iniciou uma política restauradora da confiança.
  - agentes: Galeão Carvalhal, Joaquim Murtinho
  - citação conferida: > Apesar do op-posicionista nnquella época, apoiei since-ramonte a moratória, o roconhooi immo-diatnmonto quo a situação financeira os-tava salva.

#### Correio Paulistano, 1911, edição per090972_1911_17351, página 3

`per090972_1911_17351:p003:c34520-42342`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### Gazeta de Notícias, 1910, edição per103730_1910_00078, página 5

`per103730_1910_00078:p005:c11793-17814`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### Gazeta de Notícias, 1910, edição per103730_1910_00120, página 1

`per103730_1910_00120:p001:c36659-43149`, classe: só o Claude catalogou.

**claude**, 6 registro(s):

- **Elevar a taxa cambial de 15 para 16 dinheiros**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Defende manter a taxa atual e não elevá-la, porque a estabilidade é o que importa preservar.
  - argumento: A estabilidade favorece mais a produção nacional do que a elevação da taxa; nenhuma voz das classes produtoras pediu a elevação, que seria um terremoto para a praça paulista, e a Caixa acabou com as oscilações que atraíam especulação e afugentavam capital estrangeiro.
  - agentes: Galeão Carvaihal, Paula Ramos
  - citação conferida: > A favor da elevaçãoda taxa ainda náo foi ouvida uma sóvoz partida das classseg productoras
  - observação do anotador: Há na janela um terceiro orador cujo nome o OCR corrompe ('O Sr. O"; no inato Brujín'), que declara ter sido inimigo da Caixa mas reconhece serviços prestados e apoia o substitutivo; não transcrevi o nome como agente por não ser legível com segurança.
- **Elevação da taxa como caminho para a valorização do meio circulante**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (valorizacao)
  - posição: Defende elevar a taxa cambial para 16 dinheiros, sustentando que sem isso a valorização do meio circulante nunca se fará.
  - argumento: Com a Caixa reformada nos termos propostos, os depósitos crescerão sempre à medida que o limite for completado, de modo que a valorização fica indefinidamente adiada; invoca promessa de David Campista de que a taxa seria elevada.
  - agentes: Barbosa Lima, Homero Baptista, David Campista, Francisco Veiga
  - citação conferida: > Assim nunca aefará. a valorisação do nosso meioeircularit-e
  - observação do anotador: O additivo de Homero Baptista, que eleva a taxa a 16 d. mantendo o limite do art. 3º da lei 1.575, foi aprovado por sete votos contra um (Galeão Carvaihal); a sessão não está datada na janela, por isso não registrei marco.
- **Ampliação do limite de emissão da Caixa de Conversão**
  - voz: `documento_oficial`
  - objetos e direção: limite_emissao (estabilidade_taxa_nova)
  - posição: Defende elevar o máximo das emissões da Caixa a 40 milhões esterlinos, e cogita-se em aparte elevá-lo a 60 milhões se novos depósitos entrarem.
  - argumento: Informação dada quase oficialmente à commissão indica que 30 milhões esterlinos estão prontos a entrar para a Caixa em breve prazo, o que exigiria alargar o limite legal.
  - agentes: Galeão Carvaihal, Paula Ramos
  - marcos: 1906-12-06 (lei 1.575, que creou a Caixa de Conversão)
  - citação conferida: > Fica elevado ao máximo-e 40 milhões esterlinos o valor das
  - observação do anotador: Texto de projecto substitutivo transcrito pelo jornal dentro do relato da reunião da commissão; a cifra de 60 milhões aparece em aparte, não no articulado.
- **Destino dos fundos de garantia e resgate do papel-moeda**
  - voz: `discurso_parlamentar`
  - objetos e direção: lastro (nao_classificavel)
  - posição: Disputa-se se os fundos de garantia e resgate voltam a ser regidos exclusivamente pela lei 581 de 1899, com revogação dos arts. 9 e 10 da lei da Caixa.
  - argumento: De um lado se sustenta restaurar os fundos criados em 1899; de outro se afirma que retirar os fundos de garantia e resgate da Caixa nenhum mal fará à taxa cambial, que continuará sustentada pelos capitais de que a Caixa já dispõe.
  - agentes: Barbosa Lima, Galeão Carvaihal
  - marcos: 1899-07-20 (lei 581, que criou os fundos de garantia e de resgate do papel-moeda)
  - citação conferida: > Os fundos especiaes pararesgate e garantia do papel nvoedaem cireulaçáo serão regulados ex-clusivamente pela lei 581, de 20de julho de 1S99
  - observação do anotador: Marquei direcao como nao_classificavel porque os dois lados invocam o mesmo dispositivo com finalidades opostas e o trecho não permite reduzir a disputa sobre o lastro ao eixo valorização/estabilidade sem inferência externa. As duas propostas aparecem em articulados distintos, mas tratam do mesmo desacordo.
- **Classes produtoras paulistas telegrafam contra a mudança da taxa**
  - voz: `telegrama_agencia`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Entidades paulistas apelam à Câmara para impedir a modificação da taxa de câmbio vigente.
  - argumento: A taxa atual tem trazido grandes benefícios ao país e sua elevação seria um desastre de funestas consequências para a agricultura, o comércio e a indústria.
  - agentes: Sociedade Paulista de Agricultura, Commercio e Industria, Centro Agrícola de São Paulo, Câmara Municipal de Monte Alto
  - citação conferida: > appella para o patriotismoda Câmara, afim de impedir a mo-dificação da actual taxa do cam-bio
  - observação do anotador: São telegramas de entidades transcritos pelo jornal; marquei telegrama_agencia por falta de valor mais preciso no vocabulário, embora não sejam de agência noticiosa.
- **Banqueiros pedem cautela e incineração de notas conversíveis**
  - voz: `reproduzido_terceiro`
  - objetos e direção: taxa (estabilidade_taxa_nova), limite_emissao (nao_classificavel)
  - posição: Directores de bancos estrangeiros pedem ao ministro da fazenda que a praça não seja comprometida por elevação brusca da taxa, sugerindo incinerar 20.000:000$ em notas conversíveis.
  - argumento: A incineração evitaria os prejuízos decorrentes da elevação e da sustentação do câmbio a 16 d., mitigando o choque sobre a praça.
  - agentes: Seamens, Outsehow, Norberto Ferreira, Pandiá Calogeras
  - citação conferida: > pediram a atteny»ção do Sr. ministro da fazenda pa*ra que não sejam compromettldo»oa interesses da nossa praç-a com.a brusca elevação da taxa cambial
  - observação do anotador: A conferência ocorreu 'hontem' no ministério da fazenda, sem data explícita na janela, por isso não registrei marco. Os nomes dos directores estrangeiros vêm corrompidos pelo OCR e foram copiados como aparecem. O ministro aceitou o alvitre apenas como elemento de estudo, não como decisão.

**codex**: olhou e não catalogou nada.

#### Gazeta de Notícias, 1910, edição per103730_1910_00150, página 1

`per103730_1910_00150:p001:c24581-31580`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### O Paiz, 1910, edição per178691_1910_09573, página 11

`per178691_1910_09573:p011:c15871-24655`, classe: os dois catalogaram.

**claude**, 4 registro(s):

- **Caixa visa estabilidade cambial, não baixa do câmbio**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: O orador defende que a Caixa de Conversão existe para fixar e estabilizar o câmbio na taxa adotada, e nega que seus defensores queiram câmbio baixo.
  - argumento: Acusar os sustentadores da Caixa de querer a baixa do câmbio é sectarismo, pois eles se empenham para que o câmbio nunca caia abaixo da taxa da Caixa; o ministro Campista teria empregado todos os meios para que o câmbio não baixasse de 15.
  - agentes: Campista
  - citação conferida: > Os sus-tentadores delia não querem, nuncaquizeram, que o cambio desça al':iixoda taxa que ella adoptou. Ao contra-rio, empenham-se sinceramente emque nunca o cambio se precipiteabaixo da taxa ela caixa.
  - observação do anotador: Discurso na Câmara, orador não nomeado na janela; a taxa citada como piso é 15 dinheiros.
- **Limite de depósitos da Caixa e perda da tranquilidade cambial**
  - voz: `discurso_parlamentar`
  - objetos e direção: limite_emissao (estabilidade_taxa_nova)
  - posição: O trecho sustenta que a interrupção do funcionamento pleno da Caixa, por atingido o limite legal de depósitos, destruiu a estabilidade do valor da moeda.
  - argumento: Enquanto a Caixa funcionou sem restrição, comércio, lavoura e indústria fizeram suas transações sem surpresa quanto ao valor da moeda; bastou o limite travar suas funções para desaparecer a tranquilidade cambial.
  - citação conferida: > por terem os seus depo-sitos attingido o limita imposto aoseu funecionamento, e immedlata-mente desappareccu a tranqüilidadecom relação ao valor da moeda.
  - observação do anotador: A defesa da ampliação do limite é implícita, o texto não pede explicitamente elevação do teto nesta janela.
- **Resgate do papel e reserva metálica contra o curso forçado**
  - voz: `discurso_parlamentar`
  - objetos e direção: lastro (valorizacao), conversibilidade (nao_classificavel)
  - posição: Defende fortalecer o fundo de garantia, incinerar o papel resgatado e acumular reserva metálica até o troco das notas, tratando o curso forçado como doença e período transitório.
  - argumento: A economia orçamentária contraposta ao curso forçado levaria, quase insensivelmente e sem injustiças maiores, à circulação metálica; enquanto a reserva não se acumula, o pior sofrimento não é a anemia do valor-ouro do papel, mas as crises de alta e baixa, que medidas de repouso devem atenuar.
  - citação conferida: > Incinerar o papel resgatado,e simultaneamente aecummular re-serva metálica, devem ser a preoc-eupnção essencial, substancial no tra-tamento.
  - observação do anotador: Direção híbrida e por isso marquei a conversibilidade como não classificável: o trecho defende resgate do papel e volta à circulação metálica, marcas de valorização, mas ao mesmo tempo rejeita explicitamente a apreciação do câmbio e quer a taxa fixa. Há na mesma janela um trecho anterior sobre equivalência entre importação e exportação e balança comercial que não trata de objeto de política monetária e não foi catalogado.
- **Empapelamento e depreciação do papel do Tesouro pela emissão da Caixa**
  - voz: `reproduzido_terceiro`
  - objetos e direção: limite_emissao (valorizacao), taxa (valorizacao)
  - posição: Os adversários citados sustentavam, em 1906, que as emissões da Caixa aumentariam a massa do meio circulante, depreciariam o papel-moeda do Tesouro e precipitariam o câmbio abaixo da taxa fixada; o orador os reproduz para declará-los derrotados pelos fatos.
  - argumento: Segundo os citados, moeda nova não solicitada pelo aumento das transações diminui o poder aquisitivo do papel existente e qualquer circulação fiduciária excessiva age sobre os câmbios; o orador contrapõe que o papel inconvertível manteve 15 dinheiros e subiu cerca de 20%, e que a baixa abaixo da taxa da Caixa só é possível com a Caixa vazia.
  - agentes: Lourenço de Albuquerque, Goschen, Serzedello Correia, Affonso Costa, Barbosa Lima
  - marcos: 1906-01-01 (discussão da lei de criação da Caixa de Conversão, com voto vencido de Serzedello Correia na comissão de finanças da Câmara)
  - citação conferida: > Augmentem, comopretendem, o meio circulante, com-mettam mais esta insatlia, e as con-seqüências não se farão esperar
  - observação do anotador: As posições são falas de terceiros reproduzidas dentro do discurso parlamentar, não posição do orador nem do jornal. O texto diz apenas o ano 1906 para a discussão da lei, daí a data ISO aproximada e a confiança baixa. A janela termina cortada em "de simultânea bai".

**codex**, 4 registro(s):

- **Resgate gradual do papel e reserva metálica**
  - voz: `discurso_parlamentar`
  - objetos e direção: lastro (valorizacao), conversibilidade (valorizacao)
  - posição: Defende retirar o papel resgatado e acumular reservas para o futuro troco das notas.
  - argumento: O curso forçado é apresentado como período transitório, cuja superação exige redução do papel-moeda e formação gradual de reserva metálica.
  - citação conferida: > Incinerar o papel resgatado,e simultaneamente aecummular re-serva metálica, devem ser a preoc-eupnção essencial, substancial no tra-tamento.
  - observação do anotador: O OCR parece corromper algumas palavras próximas, mas o sentido geral da defesa do resgate e da acumulação de reservas é explícito.
- **Estabilidade cambial na taxa da Caixa**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Defende câmbio fixo e estável, sem queda abaixo da taxa adotada pela Caixa.
  - argumento: A estabilidade da medida de valor é apresentada como proteção ao comércio, à lavoura, à indústria e aos demais agentes econômicos.
  - agentes: Sr. Campista
  - citação conferida: > O que queremos é cam-blo "estável", cambio "fixo", tantoejuanto possivel.
  - observação do anotador: A unidade da taxa 15 não é explicitada nessa passagem.
- **Limite da Caixa e instabilidade cambial**
  - voz: `discurso_parlamentar`
  - objetos e direção: limite_emissao (estabilidade_taxa_nova), taxa (estabilidade_taxa_nova)
  - posição: Sustenta que a interrupção do funcionamento pleno da Caixa, após o limite dos depósitos, eliminou a tranquilidade monetária.
  - argumento: O funcionamento da Caixa teria permitido transações sem surpresas quanto ao valor da moeda, enquanto a incidência do limite teria restaurado a incerteza.
  - citação conferida: > Bastou inter-romper a Caixa a plenitude de suas |funeções, por terem os seus depo-sitos attingido o limita imposto aoseu funecionamento, e immedlata-mente desappareccu a tranqüilidadecom relação ao valor da moeda.
  - observação do anotador: O trecho critica o efeito do limite, mas está cortado antes de formular explicitamente uma proposta de alteração.
- **Emissões conversíveis e depreciação do papel**
  - voz: `discurso_parlamentar`
  - objetos e direção: limite_emissao (estabilidade_taxa_nova), taxa (estabilidade_taxa_nova)
  - posição: Rejeita a previsão de que as emissões da Caixa depreciariam o papel-moeda e derrubariam o câmbio.
  - argumento: O desempenho observado é mobilizado contra os adversários de 1906: o papel inconvertível teria mantido o valor de 15 dinheiros por mil-réis, em vez de sofrer a queda prevista.
  - agentes: Sr. Lourenço de Albuquerque, Goschen, Dr. Serzedeilto Correia, Dr. Affonso Costa, Sr. Barbosa Limia
  - citação conferida: > Entretanto, o que se está vendo éo contrario disso. O papel inconver-tivel (para nós) mantém seu valorde 15 dinheiros por mil réis;
  - observação do anotador: Os nomes Serzedeilto Correia e Barbosa Limia foram mantidos conforme o OCR. A passagem reúne diversas previsões adversárias como manifestações do mesmo debate sobre os efeitos das emissões.

#### O Paiz, 1910, edição per178691_1910_09574, página 9

`per178691_1910_09574:p009:c15348-36294`, classe: os dois catalogaram.

**claude**, 4 registro(s):

- **Taxa de 18 não se sustenta na situação econômica real**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Defende que a alta recente do câmbio de 15 para 18 1/4 não tem base econômica e que a taxa da Caixa deve ser mantida em 15 dinheiros.
  - argumento: Compara os saldos comerciais anteriores e posteriores a 1906 com as necessidades anuais de ouro, que teriam subido de cerca de 13 para cerca de 25 milhões esterlinos, e conclui que não há prosperidade nova que sustente câmbio mais alto; lembra que já em 1906 os altistas prometiam taxa de 18 e a taxa de 15 quase quebrou em 1908.
  - marcos: 1906-01-01 (Criação da Caixa de Conversão); 1907-01-01 (Caixa começa a operar com a taxa de 15)
  - citação conferida: > Neste facto está prova provada, in-sophismavel, irretorquivel, de que arecente alta de 15 a IS 1|4 não se fun-da em prosjieridade econômica.
  - observação do anotador: OCR corrompe repetidamente o algarismo 18 como 'IS' e '1U0S' por 1908; as séries numéricas de saldos aparecem com dígitos trocados.
- **Elevação do limite de emissões da Caixa a 40 milhões**
  - voz: `discurso_parlamentar`
  - objetos e direção: limite_emissao (estabilidade_taxa_nova)
  - posição: Defende a emenda da bancada paulista que eleva o limite dos depósitos da Caixa de 20 para 40 milhões esterlinos, e sugere que o algarismo lógico seria até 60 milhões.
  - argumento: A produção exportável brasileira é intermitente, concentrada em café e borracha, enquanto as obrigações em ouro são permanentes; a Caixa precisa de reservas suficientes para cobrir anos de déficit, e o exemplo argentino de 1906 e 1907 mostra dois anos seguidos de falha na produção.
  - agentes: Galeão Carvalhal
  - marcos: 1906-01-01 (Lei de 1906 fixa limite de 20 milhões às emissões da Caixa)
  - citação conferida: > a representação de S. Paulo propoz alimitação das emissões da Caixa a 40milhões esterlinos.
  - observação do anotador: O texto dá o ano de 1906 apenas por referência à lei de creação; a data exata da lei não é afirmada na janela.
- **Caixa ou banco como órgão regulador do câmbio**
  - voz: `discurso_parlamentar`
  - objetos e direção: competencia_institucional (nao_classificavel)
  - posição: Defende que a função de regular o valor da moeda cabe à Caixa e não a um banco, ainda que oficial ou quase oficial.
  - argumento: Um banco é casa de negócio e opera à cata de lucro sobre diferenças no valor do papel-moeda, com o critério individual do diretor da carteira cambial; na Caixa o critério é o da lei e não há lucro.
  - agentes: Otto Pettersen
  - citação conferida: > Os próprios antagotilstas dn Caixade Conversão reconhecem a necessi-dade de um"orgão qualquer que exer-ça essa funeção. implicam com a cai-xa ; mas confiam essa missão a uinbanco, e aceitam que esse banco sejaofficial ou quasi official.
  - observação do anotador: A menção a Otto Pettersen aparece como exemplo hipotético de mau diretor de carteira cambial, entre parênteses corrompidos pelo OCR; o papel dessa figura não é explicitado na janela.
- **Como limitar a emissão e rumo à conversão metálica em 27 d.**
  - voz: `discurso_parlamentar`
  - objetos e direção: limite_emissao (valorizacao), lastro (valorizacao), conversibilidade (valorizacao)
  - posição: Sugere conjugar organicamente a Caixa de Conversão com os fundos de resgate e de garantia no combate ao papel-moeda, e declara preferir a ascensão prudente e gradativa das taxas até a paridade de 27 dinheiros à quebra do padrão.
  - argumento: Reconhece que a ilimitação absoluta das emissões pode significar virtualmente quebra do padrão e distingue dois processos de limitação em lei, um por quantum predeterminado de depósitos de ouro, adotado pela lei de creação, outro por prazo durante o qual os depósitos são permitidos, opção implícita da mensagem de Leopoldo Bulhões.
  - agentes: Leopoldo Bulhões
  - marcos: 1910-04-01 (Mensagem de abril de 1910 do Sr. Leopoldo Bulhões, que opta implicitamente pela limitação no tempo)
  - citação conferida: > em vez da que-bra do padrão, prefiro a política da J||ascensão prudente e gradativa .das-taxas para a paridade de 27 d.
  - observação do anotador: A citação carrega ruído de OCR ('J||') no meio da frase, preservado literalmente. O texto dá apenas mês e ano da mensagem de Bulhões, por isso a data foi fixada em 1910-04-01 com confiança baixa. O trecho termina cortado no meio da discussão sobre os partidários da determinação de um limite.

**codex**, 6 registro(s):

- **Sustentabilidade da taxa de 18**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (nao_classificavel)
  - posição: A taxa de 18 não estaria sustentada pelas condições econômicas do país.
  - argumento: A experiência da Caixa na taxa de 15 e a insuficiência dos saldos comerciais diante das necessidades de ouro são apresentadas como evidências contra a permanência da taxa de 18.
  - marcos: 1906-01-01 (Criação da Caixa de Conversão)
  - citação conferida: > Neste facto está prova provada, in-sophismavel, irretorquivel, de que arecente alta de 15 a IS 1|4 não se fun-da em prosjieridade econômica.
  - observação do anotador: A data da criação é informada apenas pelo ano. O trecho critica a sustentabilidade econômica da taxa de 18, mas não formula neste ponto uma alternativa normativa entre as duas direções controladas.
- **Limite das emissões da Caixa**
  - voz: `discurso_parlamentar`
  - objetos e direção: limite_emissao (nao_classificavel), lastro (estabilidade_taxa_nova)
  - posição: Defende-se limitar as emissões mediante um depósito suficientemente grande para enfrentar anos consecutivos de escassez de ouro.
  - argumento: A produção exportável seria intermitente e poderia gerar déficits elevados em anos sucessivos, exigindo reservas capazes de impedir a queda do câmbio abaixo da taxa da Caixa. A representação paulista propõe 40 milhões de libras, enquanto o orador afirma que os cálculos poderiam justificar 60 milhões.
  - agentes: Galeão Carvalhal, representação de S. Paulo
  - citação conferida: > Aqui tambem pôde acontecer omesmo. E se calculando por baixo,como retro fizemos, mostrámos quenão é nada impossível no Brazil aetualum "déficit" de.20 milhões "em umanno", ê evidente que garantirmo-noscom 20 milhões para dois annos, nãotem nada de extraordinário.
  - observação do anotador: O OCR oscila entre a proposta institucional de 40 milhões e a sugestão pessoal de elevar a proteção a 60 milhões.
- **Caixa como amortecedor cambial**
  - voz: `discurso_parlamentar`
  - objetos e direção: lastro (estabilidade_taxa_nova), conversibilidade (estabilidade_taxa_nova), taxa (estabilidade_taxa_nova)
  - posição: A Caixa deve acumular ouro nos anos favoráveis e fornecê-lo nos anos de escassez para evitar a baixa cambial.
  - argumento: Como as receitas de exportação são intermitentes e as obrigações externas são permanentes, os depósitos acumulados funcionariam como reserva limitada para sustentar a taxa da Caixa.
  - citação conferida: > Noanno das vaccas gordas, nossosaldo abundante vai todo parar nasarcas da Caixa de Conversão. Nos an-nos de falha, ou de pleno "déficit",vaccas magras, os depósitos da caixasupprem as necessidades de ouro, evi-tando a baixa cambial
  - observação do anotador: O trecho ressalva que o poder estabilizador da Caixa é limitado pelas economias efetivamente acumuladas.
- **Caixa pública ou banco**
  - voz: `discurso_parlamentar`
  - objetos e direção: competencia_institucional (nao_classificavel)
  - posição: Prefere-se a Caixa regulada por lei a um banco que administre o câmbio segundo interesses lucrativos e o critério individual de seus diretores.
  - argumento: O banco seria uma casa de negócio interessada nas diferenças de valor do papel-moeda, enquanto a Caixa operaria sem buscar esses lucros e segundo critério legal.
  - citação conferida: > o banco, que éuma casa dc negocio, exerce essa fun-cção á cata «Jo lucros sobre dtrfereti-ças maiores ou menores, no valor dopapel-moeda, ao imsso que a caixa éimpassível no operar sem Üto algumcm taes lucros
  - observação do anotador: Há forte corrupção de OCR na passagem, mas a contraposição institucional entre banco e Caixa permanece legível.
- **Retorno gradual à paridade de 27**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (valorizacao), conversibilidade (valorizacao), lastro (valorizacao)
  - posição: Defende-se a elevação prudente e gradual das taxas até a paridade de 27 dinheiros e a conversão metálica definitiva.
  - argumento: A Caixa de Conversão e os fundos de resgate e garantia deveriam atuar de forma conjunta e orgânica na redução do papel-moeda e na marcha para a conversão metálica.
  - citação conferida: > Eu J4 declarei que, em vez da que-bra do padrão, prefiro a política da J||ascensão prudente e gradativa .das-taxas para a paridade de 27 d.', po." 'mil réis.
  - observação do anotador: A frase contém corrupção de OCR, mas a preferência pela ascensão gradual até 27 dinheiros está explícita.
- **Quantidade ou prazo das emissões**
  - voz: `discurso_parlamentar`
  - objetos e direção: limite_emissao (nao_classificavel), competencia_institucional (nao_classificavel)
  - posição: O limite das emissões pode ser estabelecido por um montante máximo de depósitos ou pelo período durante o qual depósitos e emissões são permitidos.
  - argumento: O texto contrapõe o critério quantitativo adotado na lei de criação da Caixa ao critério temporal atribuído à mensagem de Leopoldo Bulhões.
  - agentes: Leopoldo Bulhões
  - citação conferida: > A lei da creação da Caixa de Con-versão ad-optou o primeiro alvItTe.A mensagem de abril do correnteanno, do Sr. Leopoldo Bulhões, im-plicitamente opta pelo segundo.
  - observação do anotador: A janela termina antes de esclarecer se o orador escolheria definitivamente o limite quantitativo ou o temporal.

#### O Paiz, 1913, edição per178691_1913_10676, página 3

`per178691_1913_10676:p003:c0-16123`, classe: os dois catalogaram.

**claude**, 5 registro(s):

- **Endosso da União ao empréstimo de valorização do café**
  - voz: `discurso_parlamentar`
  - objetos e direção: valorizacao_cafe (nao_classificavel), divida_externa (nao_classificavel)
  - posição: Alfredo Ellis defende a autorização do empréstimo de 15 milhões com endosso da União, contra a oposição da comissão de finanças.
  - argumento: A medida resguardaria não um produto paulista, mas o produto nacional, e São Paulo dava todas as garantias à União, pedindo apenas o endosso exigido pelos banqueiros; o empréstimo já foi resgatado e o endosso não existe mais.
  - agentes: Alfredo Ellis, Ramiro Barcellos, Rosa e Silva, Francisco Glycerio, Lopes Chaves
  - marcos: 1905-12-01 (Autorização para o empréstimo de 15 milhões vem no orçamento da receita, promovida na Câmara pela bancada paulista)
  - citação conferida: > de uma medida que viria resguardar,não um produeto paulista, mas oprodueto nacional.
  - observação do anotador: O texto data o dispositivo em dezembro de 1905, sem dia; por isso a confiança baixa no marco. A ameaça de obstrucção ao dispositivo de 20 mil contos para a barra do Rio Grande é referida como episódio de barganha, não como debate monetário.
- **Apoio à Caixa de Conversão contra oposição à valorização do café**
  - voz: `discurso_parlamentar`
  - objetos e direção: valorizacao_cafe (nao_classificavel), outro (nao_classificavel)
  - posição: Pinheiro Machado, na fala reproduzida por Ellis, declara-se disposto a tudo pela Caixa de Conversão, mas sempre contrário ao plano de valorização do café.
  - argumento: O trecho não explicita a justificativa; contrapõe o compromisso com a Caixa à recusa do plano de valorização como duas atitudes distintas.
  - agentes: Pinheiro Machado, Alfredo Ellis
  - marcos: 1913-12-29 (Sessão do Senado em que Alfredo Ellis faz a rectificação e Pinheiro Machado responde)
  - citação conferida: > pela Caixa de Conversão farei tudo;mas sempre fui infenso ao plano davalorização do café.
  - observação do anotador: É diálogo particular recordado de memória dentro do discurso, e sua exatidão é justamente o que Pinheiro Machado contesta adiante na mesma janela.
- **Caixa de Conversão como amparo aos riscos do plano de valorização**
  - voz: `discurso_parlamentar`
  - objetos e direção: valorizacao_cafe (nao_classificavel), outro (nao_classificavel)
  - posição: Pinheiro Machado sustenta que só aceitou o plano de valorização amparado pela Caixa de Conversão, como forma de reduzir seus perigos.
  - argumento: O plano lhe parecia aventuroso demais e sem base na realidade das coisas, com termos aleatórios; safras seguintes avultadas poderiam tornar impotentes os sacrifícios de S. Paulo, e a Caixa serviria para impedir o fracasso.
  - agentes: Pinheiro Machado, Jorge Tybiriçá, Borges de Medeiros, Francisco Glycerio
  - citação conferida: > paraimpedir que elle fracuçasse, era ne-cessarjn no menos diminuir os í-ousperigos, amparando-o com a Caixa deConversão
  - observação do anotador: Trecho com OCR bastante corrompido; a citação foi copiada como está. O orador reconhece em seguida que o plano vingou e produziu efeitos benéficos para S. Paulo.
- **Paternidade da iniciativa da Caixa de Conversão**
  - voz: `discurso_parlamentar`
  - objetos e direção: outro (nao_aplica)
  - posição: Ellis atribui a iniciativa da Caixa de Conversão ao senador Toledo Piza, reconhecendo ao mesmo tempo a intervenção eficaz de Pinheiro Machado no seu estabelecimento.
  - argumento: Toledo Piza teria ventilado a ideia na volta de uma viagem à República Argentina; a rectificação visa separar créditos, não disputar primazia nem glória.
  - agentes: Toledo Piza, Pinheiro Machado, Alfredo Ellis
  - citação conferida: > a iniciativa sobre a Caixa de(Smversão; de justiça, pertence ao se-nador Toledo iiza
  - observação do anotador: O nome aparece corrompido no OCR como "Toledo iiza" e "Caixa de(Smversão"; a citação preserva o erro. O fim do parágrafo está cortado no fecho da coluna ("que a ventilou d#").
- **Se a Caixa de Conversão já se discutia em 1905**
  - voz: `discurso_parlamentar`
  - objetos e direção: outro (nao_aplica)
  - posição: Pinheiro Machado nega ter dito, à época do empréstimo, ser infenso à valorização e não à Caixa, porque a questão da Caixa ainda não estava em discussão.
  - argumento: Cronologia: na ocasião do parecer sobre o empréstimo a Caixa ainda não estava na tela da discussão, logo as palavras atribuídas a ele não poderiam ter sido proferidas; Ellis replica que ele as pronunciou dezenas de vezes, e Pinheiro admite tê-las dito posteriormente.
  - agentes: Pinheiro Machado, Alfredo Ellis
  - citação conferida: > porque nes-sa oceasião ainda não so agitava aquestão da Caixa de Conversão
  - observação do anotador: Desacordo factual sobre datas, não sobre o mérito da política; registrado porque baliza quando a Caixa entra na agenda parlamentar segundo os próprios protagonistas.

**codex**, 4 registro(s):

- **Endosso federal ao empréstimo da valorização**
  - voz: `discurso_parlamentar`
  - objetos e direção: valorizacao_cafe (nao_classificavel), divida_externa (nao_classificavel)
  - posição: Alfredo Ellis defende o endosso da União ao empréstimo necessário para executar a valorização do café.
  - argumento: A bancada paulista considerava a medida indispensável ao plano e aceitava oferecer garantias para que a União não sofresse prejuízo.
  - agentes: Alfredo Ellis, Ramiro Barcellos, Rosa e Silva
  - citação conferida: > Para os paulista ern,no entanto, ella uma questão do vidae morte, porque determinaria se sepoderia executar o plano formuladoda valorização do café.
  - observação do anotador: O texto menciona empréstimo de 15 milhões, banqueiros e pagamento em libras, mas não identifica explicitamente os credores nem a moeda do valor principal.
- **Caixa como amparo à valorização**
  - voz: `discurso_parlamentar`
  - objetos e direção: valorizacao_cafe (nao_classificavel), outro (nao_classificavel)
  - posição: Pinheiro Machado apresenta a Caixa de Conversão como meio de reduzir os riscos do plano de valorização do café, do qual desconfiava.
  - argumento: O plano seria aventuroso e sujeito ao fracasso, especialmente diante de safras elevadas, e por isso precisaria ser amparado pela Caixa de Conversão.
  - agentes: Pinheiro Machado, Jorge Tybirlçá
  - citação conferida: > Sempre, Sr. presidente, declarei aosIllustres paulistas, que commigo seentendiam, e mesmo em carta, quedirigi ao Dr. Jorge Tybirlçá, que re-ceava, pelos resultados do plano devalorização; que me parecia estoplano por de mais avrnturoso.sem ba-sr> r:i realidade' das oojsas, c que. paraimpedir que elle fracuçasse, era ne-cessarjn no menos diminuir os í-ousperigos, amparando-o com a Caixa deConversão.
  - observação do anotador: Alfredo Ellis atribui a Pinheiro Machado uma declaração mais enfática de apoio à Caixa e oposição à valorização. Pinheiro contesta apenas que ela tivesse sido feita naquela ocasião, afirmando que a Caixa ainda não estava em discussão.
- **Iniciativa da Caixa de Conversão**
  - voz: `discurso_parlamentar`
  - objetos e direção: outro (nao_aplica)
  - posição: Alfredo Ellis atribui a iniciativa da Caixa de Conversão ao senador Toledo iiza.
  - argumento: Segundo Ellis, o senador levantou a proposta depois de retornar de uma viagem à República Argentina.
  - agentes: Alfredo Ellis, Toledo iiza, Pinheiro Machado
  - citação conferida: > a iniciativa sobre a Caixa de(Smversão; de justiça, pertence ao se-nador Toledo iiza, que a ventilou
  - observação do anotador: O nome de Toledo e a expressão Caixa de Conversão estão corrompidos pelo OCR. O mesmo discurso reconhece a intervenção eficaz de Pinheiro Machado no estabelecimento da Caixa.
- **Causas do êxito da valorização**
  - voz: `discurso_parlamentar`
  - objetos e direção: valorizacao_cafe (nao_aplica)
  - posição: Glycerio atribui grande parte do êxito da valorização aos administradores paulistas, enquanto Pinheiro Machado acrescenta a cooperação federal.
  - argumento: O desacordo trata da contribuição relativa da administração de São Paulo e do apoio do Congresso e do governo da República para o resultado da operação.
  - agentes: Francisco Glycerio, Pinheiro Machado, Alfredo Ellis
  - citação conferida: > O Sr. Francisco Glycerio — Masem grande parte o êxito da operaçãofoi devido k capacidade dos adminis-tradores de S. Paulo.O Pr. Alfredo Rtlis — Apoiado.O SR; PINHEIRO MACHADO—In-negnvelmente.mns lambem á coopera-ção que o Congresso o o governo da.Rr-publica prestaram a S. Ppulo.
  - observação do anotador: A passagem registra uma divergência de atribuição causal, não uma defesa de direção monetária.

### F4, 1914, suspensão do troco

#### Correio da Manhã, 1914, edição per089842_1914_05642, página 2

`per089842_1914_05642:p002:c12218-20882`, classe: os dois catalogaram.

**claude**, 3 registro(s):

- **Suspender ou não o troco das notas da Caixa**
  - voz: `discurso_parlamentar`
  - objetos e direção: conversibilidade (nao_classificavel), competencia_institucional (nao_classificavel)
  - posição: Carlos Peixoto declara-se contrário à suspensão do troco das notas da Caixa de Conversão, mas, vencido pela maioria, sugere que se autorize o governo a modificar a medida conforme as conveniências do mercado cambial; João Luiz Alves propõe igualar o prazo da não conversão ao da moratória e permitir suspensão contínua, intermitente ou troca de quantias diárias prefixadas.
  - argumento: A conveniência do mercado cambial é invocada como critério para dar ao Executivo margem de manejo sobre a suspensão, uma vez adotada a ideia pela maioria da comissão.
  - agentes: Carlos Peixoto, João Luiz Alves, Tavares de Lyra, Glycerio
  - citação conferida: > embora contrario i suspciisâu do trocodenotas da Caixa do Conversão
  - observação do anotador: Relato de sessão de comissão parlamentar; a posição é dos membros, não do jornal. Grafia dos nomes corrompida pelo OCR ("Carlos 1'eixoto", "Alvca"). A sessão não é datada explicitamente na janela.
- **Oposição a toda emissão de papel-moeda**
  - voz: `discurso_parlamentar`
  - objetos e direção: limite_emissao (valorizacao)
  - posição: Homero Baptista declara-se contrário a toda emissão de papel-moeda.
  - argumento: Nenhuma justificativa é dada na janela; consta apenas a declaração de posição em telegrama que justifica a ausência à sessão.
  - agentes: Homero Baptista
  - citação conferida: > no qual te declara contrario * todficmltsio dc papcl-mocda.
  - observação do anotador: Posição transmitida por telegrama lido na sessão, não discurso proferido; classificada como discurso_parlamentar por ser fala de senador registrada nos trabalhos. "todficmltsio" corresponde provavelmente a "toda emissão". A janela também informa que os projetos de Homero Baptista e Manoel Borba foram tomados por base para a solução definitiva da crise.
- **Projeto suspende troco e delega prazo ao Executivo**
  - voz: `documento_oficial`
  - objetos e direção: conversibilidade (nao_classificavel), competencia_institucional (nao_classificavel), lastro (nao_classificavel), outro (nao_aplica)
  - posição: O projeto redigido suspende por trinta dias, prorrogáveis pelo governo até o máximo de cento e vinte, a exigibilidade de obrigações comerciais e a troca de notas da Caixa de Conversão, autorizando o governo a tornar a suspensão contínua ou intermitente, e mantém o ouro existente na Caixa depositado exclusivamente para a conversão das notas por ela emitidas.
  - argumento: Trata-se de medida de caráter provisório diante da crise, com o lastro metálico preservado sob as garantias e penalidades da lei que criou a Caixa, enquanto a comissão passa a estudar as medidas definitivas.
  - agentes: commissão de Finanças do Senado, presidente da Republica, Sá Freire
  - marcos: 1907-12-06 (lei n. 1.575, cujas garantias e penalidades contra desvio do ouro ficam mantidas); 1914-08-03 (ato do presidente da Republica que decretou feriado até 15 do mesmo mês, aprovado pelo projeto); 1914-06-17 (lei n. 2.857, cujo art. 1º, letra C, suspendeu obras do Ministério da Viação)
  - citação conferida: > Ficam suspensas, a contarda data desta lei, pelo prazo dc 30 dias
  - observação do anotador: O objeto 'outro' cobre a moratória bancária e das letras de câmbio, que não é matéria cambial nem monetária no vocabulário controlado. O parágrafo sobre o lastro consta como "O ouro existentena Caixa dc -Conversão continuaria' ali-depositado'". A data da lei n. 1.575 aparece como ".6 .dc dezembro .".de t,90?", lida como 6 de dezembro de 1907.

**codex**, 5 registro(s):

- **Crédito da Caixa para financiar a safra**
  - voz: `assinado`
  - objetos e direção: valorizacao_cafe (nao_classificavel), limite_emissao (nao_classificavel), taxa (estabilidade_taxa_nova), lastro (nao_classificavel)
  - posição: Defende que a Caixa de Conversão emita notas especiais para financiar o café depositado, com resgate previsto e conversão a 16 dinheiros.
  - argumento: O empréstimo substituiria a venda imediata em mercados paralisados pela guerra. O café depositado e parte do produto de sua venda serviriam para garantir e resgatar a emissão.
  - citação conferida: > A Caixa de Conversão dará ü $. por sacca,l cm inot.is de curso legal, especiaes. resgata-: veis! até 30 de junho de ioi5- «o camMo«le 16 d. |*or i$aoo.
  - observação do anotador: O valor concedido por saca e a assinatura estão prejudicados pelo OCR.
- **Oposição a toda emissão de papel-moeda**
  - voz: `indeterminado`
  - objetos e direção: limite_emissao (nao_classificavel)
  - posição: Homero Haplista declara-se contrário a qualquer emissão de papel-moeda.
  - agentes: Homero Haplista
  - citação conferida: > O ir. Homero Haplista jusiiíi-cou a auá ausência, por telcgramtna'no qual te declara contrario * todficmltsio dc papcl-mocda.
  - observação do anotador: A posição é comunicada por telegrama pessoal reproduzido no relato dos trabalhos, não por telegrama de agência.
- **Suspensão do troco das notas da Caixa**
  - voz: `discurso_parlamentar`
  - objetos e direção: conversibilidade (nao_classificavel)
  - posição: A maioria adota a suspensão temporária da troca das notas da Caixa de Conversão, apesar da oposição de Carlos Peixoto.
  - argumento: Carlos Peixoto registra sua oposição à suspensão, mas reconhece a decisão majoritária. João Luiz Alves propõe que a não conversão acompanhe o prazo ampliado da moratória.
  - agentes: Carlos Peixoto, João Luiz Alves
  - citação conferida: > O tr. Carlos 1'eixoto ponderou que,embora contrario i suspciisâu do trocodenotas da Caixa do Conversão, umavez que foi esta idéa adoptada pelamaioria
  - observação do anotador: O trecho não identifica nominalmente os integrantes da maioria favorável à suspensão.
- **Poder executivo sobre a suspensão do troco**
  - voz: `documento_oficial`
  - objetos e direção: competencia_institucional (nao_classificavel)
  - posição: Defende autorizar o governo a tornar a suspensão contínua ou intermitente e a permitir trocas diárias limitadas.
  - argumento: A flexibilidade permitiria ajustar a conversão das notas às condições do mercado cambial durante o prazo excepcional.
  - agentes: Carlos Peixoto, João Luiz Alves
  - citação conferida: > podendo o governo, dentro-dosprazos dcs.e artigo, tornar a suspcrisf*pcontinua ou intermittente, assim comopermittir a troca dc quantias diária^mente prefixadas;
  - observação do anotador: A citação pertence ao projeto que seria formulado conforme a votação da comissão.
- **Vinculação do ouro ao resgate das notas**
  - voz: `documento_oficial`
  - objetos e direção: lastro (nao_classificavel)
  - posição: Determina que o ouro da Caixa permaneça depositado exclusivamente para converter as notas por ela emitidas.
  - argumento: O projeto mantém garantias e penalidades legais para impedir que o ouro seja desviado de sua finalidade de resgate.
  - citação conferida: > O ouro existentena Caixa dc -Conversão continuaria' ali-depositado' pam o fim,' exclusivo ' daconversão de notas por cila eiuitti.das;.'-mantidas, para qualquer* desvio, as iga-'rànti.s e penalidades Cslatuidas : pelalei ln. 1.575, de. .6 .dc dezembro .".det,90?.
  - observação do anotador: A numeração e a data da lei estão parcialmente corrompidas pelo OCR.

#### Correio da Manhã, 1914, edição per089842_1914_05644, página 2

`per089842_1914_05644:p002:c11130-17130`, classe: só o Codex catalogou.

**claude**: olhou e não catalogou nada.

**codex**, 3 registro(s):

- **Elevação do meio circulante**
  - voz: `reproduzido_terceiro`
  - objetos e direção: limite_emissao (nao_classificavel)
  - posição: Defende a elevação do meio circulante.
  - argumento: A medida integra uma representação formulada após exame da situação do comércio, da lavoura e da indústria.
  - agentes: Associação Commercial do Rio de Janeiro
  - citação conferida: > A elevação do meio circulante.
  - observação do anotador: O trecho não informa como a elevação seria executada nem sua relação com uma taxa cambial específica.
- **Suspensão do troco das notas**
  - voz: `reproduzido_terceiro`
  - objetos e direção: conversibilidade (nao_classificavel)
  - posição: Defende a suspensão do troco das notas da Caixa de Conversão.
  - argumento: A medida integra uma representação formulada após exame da situação do comércio, da lavoura e da indústria.
  - agentes: Associação Commercial do Rio de Janeiro
  - citação conferida: > Suspensão do troco das* notas daCaixa de Conversão.
  - observação do anotador: O asterisco e a ausência de espaço em "daCaixa" são erros ou marcas do OCR preservados na citação.
- **Suspensão de emissões da dívida pública**
  - voz: `reproduzido_terceiro`
  - objetos e direção: outro (nao_classificavel)
  - posição: Defende a suspensão das autorizações para emissões de títulos da dívida pública.
  - argumento: A medida integra uma representação formulada após exame da situação do comércio, da lavoura e da indústria.
  - agentes: Associação Commercial do Rio de Janeiro
  - citação conferida: > Suspensão das autorizações paraemissões dc tif.ilos da Divida Pitliliia,
  - observação do anotador: O texto não permite determinar se a dívida mencionada é externa; por isso, o objeto foi classificado como "outro".

#### Correio da Manhã, 1914, edição per089842_1914_05736, página 2

`per089842_1914_05736:p002:c9833-17138`, classe: os dois catalogaram.

**claude**, 2 registro(s):

- **Suspensão das operações da Caixa foi erro grave**
  - voz: `editorial_do_jornal`
  - objetos e direção: conversibilidade (estabilidade_taxa_nova), taxa (estabilidade_taxa_nova)
  - posição: Suspender as transacções da Caixa de Conversão foi erro grave, porque arruina a instituição e deixa o câmbio sem instrumento que o equilibre.
  - argumento: A medida foi tomada sem pensar nas consequências e sem organizar qualquer outro serviço destinado a equilibrar o câmbio, que, abandonado, cairia e perturbaria toda a vida econômica do país; a Caixa era instituto artificial destinado a desaparecer, mas só na hora própria, quando houvesse substituto preparado.
  - citação conferida: > Foi, pois, erro c erro grave, aqui*Ia medida restrictiva da funeção
  - observação do anotador: Trecho da secção intitulada "A Caixa de Conver-sio i o governo", muito corrompido por OCR e entrecortado por matéria alheia (notícias militares, Cáes do Porto). O texto atribui a escassez de ouro à conflagração europeia e aos deficits da balança commercial, mas a frase correspondente está truncada na janela.
- **Legalidade da retirada de 200.000 libras da Caixa**
  - voz: `editorial_do_jornal`
  - objetos e direção: lastro (nao_classificavel), competencia_institucional (nao_classificavel)
  - posição: A retirada de 200.000 libras da Caixa de Conversão por ordem do ministro da Fazenda foi ilegal, por dispensar o pedido de crédito ao Congresso Nacional.
  - argumento: Dispositivo legal citado obrigaria o Poder Executivo a submeter ao Congresso Nacional pedido de crédito, e só despesa feita sobre crédito legalmente aberto poderia ser computada; a operação expõe um regime de ilegalidades e incoerências.
  - agentes: ministro da Fazenda, Congresso Nacional
  - citação conferida: > das 200.000 libras retiradas da Caixadc Conversão por ordem do minis-tro' dã Fazenda, põem a descobertoo regimen de ilk-galidades
  - observação do anotador: A janela cita "paragrapíio 5°" de um "decreto n. 2,409, de 23 de..4e^fcbra de 1891", mas a data e o número estão ilegíveis o bastante para não permitir registro de marco confiável. O ministro não é nomeado na janela. O início do parágrafo está cortado pela quebra de coluna.

**codex**, 2 registro(s):

- **Legalidade da retirada de fundos da Caixa**
  - voz: `editorial_do_jornal`
  - objetos e direção: lastro (nao_classificavel), competencia_institucional (nao_classificavel)
  - posição: A retirada de 200 mil libras da Caixa por ordem do ministro da Fazenda é apresentada como ilegal.
  - argumento: A operação é tratada como evidência do regime de ilegalidades e incoerências atribuído ao governo.
  - agentes: ministro da Fazenda
  - citação conferida: > as 200.000 libras retiradas da Caixadc Conversão por ordem do minis-tro' dã Fazenda, põem a descobertoo regimen de ilk-galidades c das in-coiierèn-ias mais completas cm quc ollrasil tem vivido ultimamente.
  - observação do anotador: O OCR mistura o início do artigo com fragmentos de coluna vizinha; não é possível determinar pela janela o fundamento jurídico preciso da alegada ilegalidade.
- **Suspensão das operações da Caixa de Conversão**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova), conversibilidade (nao_classificavel)
  - posição: A suspensão das transações da Caixa é condenada, defendendo-se sua manutenção até que existisse um substituto capaz de estabilizar o câmbio.
  - argumento: Embora considerada artificial e destinada a desaparecer, a Caixa teria reduzido as oscilações cambiais e permitido tranquilidade ao comércio; sua suspensão sem serviço substituto deixaria o câmbio sujeito à exploração e à queda.
  - citação conferida: > Foi, pois, erro c erro grave, aqui*Ia medida restrictiva da funeção <ía'Caixa de Conversão, a qual tinhapara a dirigir lei própria, tão priva-tíva quanto severa
  - observação do anotador: O trecho posterior sobre a conflagração europeia, a crise interna e a escassez de ouro está cortado e parcialmente misturado com outra coluna.

#### Correio Paulistano, 1914, edição per090972_1914_18122, página 2

`per090972_1914_18122:p002:c21193-27703`, classe: os dois catalogaram.

**claude**, 1 registro(s):

- **Origem do bloco: questão econômica da Caixa ou política**
  - voz: `discurso_parlamentar`
  - objetos e direção: outro (nao_classificavel), valorizacao_cafe (nao_classificavel)
  - posição: Pinheiro Machado sustenta que o bloco nasceu da questão econômica da Caixa de Conversão e da valorização do café, e não como reação à intervenção do presidente na sucessão, como afirma Nilo Peçanha.
  - argumento: Alega que os homens à frente das questões econômicas organizaram o bloco, que Affonso Penna foi eleito pelos elementos que sustentavam o princípio da Caixa e que Glycerio, já com a questão econômica em curso, o investiu da direção da campanha, quando a questão política da sucessão já estava encerrada.
  - agentes: Pinheiro Machado, Nilo Peçanha, Francisco Glycerio, Affonso Penna, João Luiz Alves, Urbano Santos, Francisco Sá, Ruy Barbosa
  - citação conferida: > O sr. senador Glycerio estava com , aquestão econômica da Caixa de Conversãoe d.i valorização do caíé;_ nós tínhamosdado a nossa solidariedade á solução desseproblema
  - observação do anotador: Trecho de debate no Senado, não editorial. A Caixa aparece como causa política aglutinadora, sem que se discuta taxa, lastro ou limite de emissão, por isso a direção fica não classificável. O texto menciona a eleição de Affonso Penna 'em 1 de março' sem indicar o ano, e por isso nenhum marco datado foi registrado. OCR muito degradado, com nomes corrompidos ('Pinheiro Máçliifdò', 'caíé') e palavras coladas.

**codex**, 1 registro(s):

- **Origem econômica do bloco e apoio à Caixa**
  - voz: `discurso_parlamentar`
  - objetos e direção: valorizacao_cafe (nao_classificavel), outro (nao_classificavel)
  - posição: Pinheiro Machado sustenta que a articulação política mencionada se formou em torno de questões econômicas e apoiou a Caixa de Conversão e a valorização do café.
  - argumento: O orador afirma que os republicanos que elegeram Affonso Penna sustentavam o princípio da Caixa e que Glycerio e seu grupo haviam dado solidariedade à solução conjunta da Caixa de Conversão e da valorização do café.
  - agentes: Pinheiro Machado, Francisco Glycerio, Nilo Peçanha, Affonso Penna
  - citação conferida: > O sr. senador Glycerio estava com , aquestão econômica da Caixa de Conversãoe d.i valorização do caíé;_ nós tínhamosdado a nossa solidariedade á solução desseproblema; s. exc. entendeu que era coiive-niente normalizar, disciplinar a acção; «:,por isso, invesliu-nie da direcção dessacampanha.
  - observação do anotador: O trecho discute principalmente a origem e a composição de uma articulação política. Embora atribua apoio à Caixa de Conversão e à valorização do café, não informa taxa, mecanismo monetário, lastro ou forma concreta da política defendida.

#### Correio Paulistano, 1914, edição per090972_1914_18244, página 4

`per090972_1914_18244:p004:c4370-14838`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### Correio Paulistano, 1914, edição per090972_1914_18417, página 4

`per090972_1914_18417:p004:c31478-38082`, classe: os dois catalogaram.

**claude**, 1 registro(s):

- **Uso de ouro da Caixa após seu fechamento e efeito no câmbio**
  - voz: `documento_oficial`
  - objetos e direção: conversibilidade (nao_classificavel), lastro (nao_classificavel), taxa (nao_classificavel), divida_externa (nao_aplica)
  - posição: Nota oficial do Ministério da Fazenda nega ter reaberto a Caixa clandestinamente a um banco amigo para elevar o câmbio, e sustenta que a única troca feita após o fechamento foi de 3.000 contos, em libras remetidas a Londres para pagar coupon do empréstimo de 1903 das obras do porto.
  - argumento: A operação teria sido feita às claras, com autorização escrita e publicada na imprensa, dando lucro ao Thesouro; e evitou que o governo interviesse num mercado de câmbio sensibilíssimo, intervenção que contribuiria fatalmente para a baixa.
  - agentes: O Imparcial, Banco Nacional Ultramarino
  - citação conferida: > apenas or-denou a troca da quantia dc 3.000 contos,correspondente a 200 mil libras, as quaesforam enviadas para Londres
  - observação do anotador: O nome do ministro da Fazenda e o do director da Caixa não aparecem na janela, por isso ficam vazios. O fechamento da Caixa é afirmado como fato consumado, sem data no texto, e por isso não foi registrado como marco. A acusação de 'O Imparcial' chega apenas mediada pela nota que a nega. A direção nos objetos foi marcada como nao_classificavel porque o texto é defesa administrativa de uma operação pontual, não tomada de posição sobre valorização ou estabilidade a taxa nova, embora o preço de 16$000 por libra e a menção à baixa do câmbio apareçam. OCR degradado ('dc' por 'de', 'abtr-to' por 'aberto', 'v/03' por '1903').

**codex**, 1 registro(s):

- **Troca de notas após fechamento da Caixa**
  - voz: `documento_oficial`
  - objetos e direção: conversibilidade (nao_classificavel), taxa (valorizacao), divida_externa (nao_aplica)
  - posição: O Ministério da Fazenda nega a abertura clandestina da Caixa e defende como regular uma troca excepcional destinada ao pagamento de dívida externa.
  - argumento: A nota afirma que a única troca posterior ao fechamento foi autorizada por escrito e divulgada pela imprensa. Sustenta que a operação gerou lucro para o Tesouro e evitou uma intervenção governamental que provocaria a baixa do câmbio.
  - agentes: ministro da Fazenda, Banco Nacional Ultramarino, O Imparcial
  - citação conferida: > O ministro da Fazenda, após o fecha-mento da Caixa de Conversão, apenas or-denou a troca da quantia dc 3.000 contos,correspondente a 200 mil libras, as quaesforam enviadas para Londres, por mter-médio do Banco Nacional Ultramarino,afim de acudir ao pagamento do coupondo empréstimo de v/03, para as obras doporto do Rio dc Janeiro.
  - observação do anotador: A identificação do empréstimo está corrompida pelo OCR como "v/03". A data traz apenas o dia 24, sem mês legível na janela, por isso não foi registrada em marcos.

#### Gazeta de Notícias, 1914, edição per103730_1914_00140, página 6

`per103730_1914_00140:p006:c7735-13735`, classe: só o Claude catalogou.

**claude**, 1 registro(s):

- **Causa das retiradas de ouro da Caixa de Conversão argentina**
  - voz: `telegrama_agencia`
  - objetos e direção: lastro (nao_classificavel), conversibilidade (nao_aplica)
  - posição: Banqueiros de Buenos Aires sustentam que as retiradas contínuas de ouro da Caixa de Conversão não indicam problema da instituição, mas resultam da retração dos negócios.
  - argumento: A saída de ouro é atribuída à falta de transações e à diminuição da exportação de produtos para o exterior, isto é, a causas do comércio externo e não à política monetária em si.
  - agentes: principaes banqueiros de Buenos Aires
  - citação conferida: > retiradas de ouro da Cai-',xa dc pqnversão
  - observação do anotador: ATENÇÃO: telegrama de Buenos Aires sobre a Caja de Conversión ARGENTINA, não a Caixa de Conversão brasileira. Registrado por conter argumento causal sobre regime de conversibilidade, mas não é fonte sobre política brasileira e não deve ser contado como tal. O restante da janela é telegrama internacional sem relação (Albânia, França, Japão, Roosevelt) e nota religiosa. OCR muito degradado: 'pqnversão' por 'conversão', 'nttrilntcm-n'as' por 'attribuem-n'as', 'TransacçÒcs' por 'transacções'. Direção não redutível ao eixo valorização/estabilidade a taxa nova.

**codex**: olhou e não catalogou nada.

#### Gazeta de Notícias, 1914, edição per103730_1914_00217, página 5

`per103730_1914_00217:p005:c24347-30528`, classe: os dois olharam e não catalogaram nada.

**claude**: olhou e não catalogou nada.

**codex**: olhou e não catalogou nada.

#### Gazeta de Notícias, 1914, edição per103730_1914_00288, página 1

`per103730_1914_00288:p001:c0-6180`, classe: os dois catalogaram.

**claude**, 2 registro(s):

- **uso das notas da Caixa para remeter ouro a Londres**
  - voz: `editorial_do_jornal`
  - objetos e direção: conversibilidade (nao_classificavel), taxa (nao_classificavel), lastro (nao_aplica)
  - posição: O jornal aprova a decisão do ministro da Fazenda de converter em espécie 3.000 contos em notas da Caixa de Conversão para pagar o coupon do empréstimo das obras do porto, em vez de recorrer a saques no mercado cambial.
  - argumento: Saques exigiriam procura efetiva de libras num mercado sensível, que a especulação usaria como pretexto para novas depressões da taxa; pela Caixa o governo obteria as libras a preço muito menor, com ganho de cerca de 700 contos para o Tesouro.
  - agentes: Caixa de Conversão
  - marcos: 1914-08-15 (lei de 15 de agosto, art. 1º, letra d, que suspende por 30 dias a troca por ouro das notas da Caixa de Conversão); 1914-09-15 (lei de 15 de setembro prorroga por 90 dias os prazos da lei de 15 de agosto)
  - citação conferida: > teveo, excellento inspiração do fazerconverter cm espécie 3.000 contos
  - observação do anotador: OCR muito degradado; o nome do ministro não aparece na janela, só o cargo. A direção fica não classificável porque o texto elogia uma operação administrativa e defende o câmbio contra depressão especulativa, sem tomar posição sobre nível de taxa nem sobre volta ao par.
- **se a dívida das obras do porto está incluída no funding**
  - voz: `editorial_do_jornal`
  - objetos e direção: divida_externa (nao_classificavel)
  - posição: O jornal refuta o boato de que a remessa de ouro provaria não haver funding, sustentando que os empréstimos das obras do porto são operações especiais, com fundo próprio, e que a dívida externa está toda compreendida no novo funding, exceto o funding vigente.
  - argumento: Os empréstimos do porto têm garantia especializada e nem figuram no quadro de juros e amortização da dívida externa do orçamento; além disso não se poderia exigir do mesmo credor concessão idêntica à que ele já fizera. O ministro obteve que as amortizações entrassem no novo funding, continuando pagos em espécie apenas os juros.
  - citação conferida: > os ompre.-ti-mos para as obras do porto consti-tvtem operações espeeiaos, comfundo especial nara o respectivoServiço
  - observação do anotador: Trecho cercado de matéria de guerra europeia na mesma coluna; a citação foi tomada apenas da parte econômica.

**codex**, 2 registro(s):

- **Conversão de notas para remessa ao exterior**
  - voz: `editorial_do_jornal`
  - objetos e direção: conversibilidade (nao_classificavel), divida_externa (nao_classificavel)
  - posição: Defende a conversão excepcional de notas da Caixa em ouro para pagar o cupom do empréstimo das obras do porto.
  - argumento: A operação evitaria pressionar o mercado de câmbio e permitiria ao Tesouro obter libras por preço inferior ao dos saques, gerando economia.
  - agentes: Sr. ministro da Fazenda
  - citação conferida: > teveo, excellento inspiração do fazerconverter cm espécie 3.000 contosd.» notas da Caixa Jo Convõrsãri,obtendo desto modo as í rMO.OOr)iiara a necessidade ocoiirrento.
  - observação do anotador: O valor em libras está fortemente corrompido pelo OCR.
- **Remessa de ouro e existência do funding**
  - voz: `editorial_do_jornal`
  - objetos e direção: divida_externa (nao_classificavel)
  - posição: Rejeita que a remessa de ouro demonstre a inexistência do novo funding.
  - argumento: Sustenta que os empréstimos das obras do porto constituem operações especiais e que, no novo funding, suas amortizações foram incluídas, permanecendo apenas os juros pagáveis em espécie.
  - agentes: Sr. ministro da Fazenda
  - citação conferida: > Mas para os pro-prios empréstimos destinados ísobras do porto o Sr. ministro daFazenda obteve que'as ajnorUsaçüaaentrem no réglmen do r.ovo "fim-ding", continuando a sor pagos cmespécie súmento os juros.
  - observação do anotador: As formas relativas a funding e amortizações estão corrompidas pelo OCR.

#### O Paiz, 1914, edição per178691_1914_10818, página 4

`per178691_1914_10818:p004:c7023-16392`, classe: só o Claude catalogou.

**claude**, 3 registro(s):

- **Causa das retiradas contínuas de ouro da Caixa**
  - voz: `telegrama_agencia`
  - objetos e direção: lastro (nao_classificavel), conversibilidade (nao_classificavel)
  - posição: Os banqueiros da praça de Buenos Aires sustentam que as retiradas contínuas de ouro da Caixa de Conversão não indicam fragilidade do instituto, mas decorrem do estado do comércio exterior.
  - argumento: A saída de ouro é atribuída à falta de transações e à queda das exportações de produtos, isto é, a causas comerciais e não monetárias.
  - citação conferida: > interrogados sobre as conti-nuas retiradas de ouro, da Caixa deConversão, attribuem-n'as á falta detransácções e á diminuição da expor-tação de produetos para o exterior.
  - observação do anotador: Telegrama datado de Buenos Aires: a Caixa de Conversão em questão é a instituição argentina, não a brasileira. A janela não discute política monetária do Brasil, e as direções do vocabulário controlado (valorização contra estabilidade a taxa nova) não se aplicam a este eixo. Data do telegrama dada só como dia 20, sem mês.
- **Solidez da situação financeira contra o clamor pessimista**
  - voz: `telegrama_agencia`
  - objetos e direção: lastro (nao_classificavel), outro (nao_classificavel)
  - posição: A situação financeira do país é sólida e não justifica a celeuma em torno do crédito nacional, tendo a Caixa de Conversão sido consolidada pelo auxílio das instituições de crédito.
  - argumento: Publicações informativas dos bancos sobre as transações dos últimos quatro meses forneceriam dados positivos que desmentem as opiniões pessimistas, cujo efeito é retrair operações comerciais; a resistência à crise mundial de dinheiro teria sido amparada pelas instituições de crédito, sem comprometer a estabilidade delas.
  - citação conferida: > nas liberalidades das instituições decredito, que consolidaram a Caixade Conversão, concédendo-lhe os au-xilios necessários, sem, entretanto,comprometter a sua própria estabi-lidade e amplo ftmecionamento.
  - observação do anotador: Mesma ressalva: trata-se da Caixa de Conversão argentina, em telegrama de Buenos Aires. O texto é relato de imprensa sobre publicações bancárias, não editorial de O Paiz. OCR corrompido em vários pontos ('economico-fi-iianceira', 'ftmecionamento').
- **Saque de ouro para pagar dívida externa e circulação monetária**
  - voz: `telegrama_agencia`
  - objetos e direção: divida_externa (nao_classificavel), lastro (nao_classificavel)
  - posição: A retirada do ouro depositado na Caixa de Conversão para pagamento da dívida externa é apontada como fator determinante da contração da circulação monetária, e o país teria capacidade de solvê-la.
  - argumento: A solvência é garantida pelo repositório econômico da produção agrícola e industrial; a redução dos saldos também se explica pela clientela usar depósitos para honrar compromissos assumidos em empréstimos.
  - citação conferida: > terminante da circulação da moedaé a retirada do ouro em deposito naCaixa de Conversão, para pagamen-tos de divida externa
  - observação do anotador: Caixa de Conversão argentina, telegrama de Buenos Aires. O início do trecho aparece cortado na janela ('sua reducção pelo facto de se vêr a clientela obrigada...'), sem o começo do parágrafo, o que impede saber a que grandeza a redução se refere.

**codex**: olhou e não catalogou nada.

#### O Paiz, 1914, edição per178691_1914_10827, página 1

`per178691_1914_10827:p001:c14018-22109`, classe: os dois catalogaram.

**claude**, 3 registro(s):

- **Autorização legislativa do empréstimo externo contra a obstrucção**
  - voz: `editorial_do_jornal`
  - objetos e direção: divida_externa (nao_classificavel), competencia_institucional (nao_classificavel)
  - posição: O trecho defende a autorização legislativa pedida pelo governo para levantar o empréstimo, tratando a oposição a ela como politicamente motivada e já desmentida pelos fatos.
  - argumento: O receio de mau emprego do dinheiro foi neutralizado pela emenda que limita, na própria lei, a aplicação dos recursos ao objetivo da operação de crédito; e o efeito moral da resolução do Congresso já se traduziu em alta cambial e animação da praça do Rio de Janeiro.
  - agentes: marechal Hermes, commissão de finanças
  - citação conferida: > o levantamento do empresti-mo, de que fizeram cavallo de bata-lha os inflexíveis censores do gover-110
  - observação do anotador: O nome do ministro da fazenda em exercício não aparece no trecho, só a referência a "illustre Sr. ministro da fazenda". O texto tem forte ruído de OCR, inclusive "gover-110" por "governo".
- **Taxa de 16 dinheiros contra taxa estável na Caixa**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: O trecho defende a decretação de uma taxa estável para o câmbio da Caixa de Conversão e censura Bulhões por ter forçado a taxa de 16 dinheiros e resistido à estabilidade.
  - argumento: Bulhões manteria o câmbio em taxas exageradamente elevadas à custa de sacrifícios inauditos, e o Congresso só aceitou os 16 dinheiros como transação para vencer a má vontade do ministro contra a taxa estável, cujos benefícios apenas sectários de fórmulas teóricas negariam.
  - agentes: Sr. Bulhões, Congresso
  - citação conferida: > contra a decretação-da tax-a estável, cujosbenefícios
  - observação do anotador: O texto não data a fixação dos 16 dinheiros; a referência temporal é indireta, pela menção ao ministério da fazenda no governo Nilo Peçanha. OCR corrompe "tax-a" e "lypo".
- **Vale de 19.000 contos no lastro da Caixa de Conversão**
  - voz: `editorial_do_jornal`
  - objetos e direção: lastro (nao_classificavel)
  - posição: O trecho condena o pagamento da dívida de dezenove mil contos à Caixa de Conversão, por ter posto no lugar de ouro em espécie um vale de responsabilidade do governo, desvirtuando a natureza do lastro.
  - argumento: Só ouro em espécie poderia entrar na Caixa; o vale de 19.000 contos foi despesa sem contrapartida alguma, ao contrário de armamentos, estradas de ferro e vilas operárias, que ao menos deixaram algo, e por isso é o compromisso menos justificável já assumido.
  - agentes: Sr. Bulhões, Sr. Nilo Peçanha
  - citação conferida: > desvirtuou a própriaessência da Caixa de Conversão, onde sópodia entrar ouro cm espécie
  - observação do anotador: O trecho critica a composição do lastro sem se enquadrar em valorização nem em estabilidade a taxa nova, daí a direção não classificável. O início do parágrafo que menciona a lei do pagamento está cortado no topo da janela.

**codex**, 2 registro(s):

- **Taxa elevada contra câmbio estável**
  - voz: `editorial_do_jornal`
  - objetos e direção: taxa (estabilidade_taxa_nova)
  - posição: Defende a decretação de uma taxa cambial estável e critica a manutenção do câmbio em níveis elevados.
  - argumento: A resistência de Bulhões à taxa estável é apresentada como sectária e responsável por sacrifícios, embora seus benefícios fossem reconhecíveis.
  - agentes: Sr. Bulhões
  - citação conferida: > depois de ter mantido, ácusta de sacrifícios inauditos, o cambioa lax-as exageradamente elevadas, fez umultimo esforço a favor da, taxa de 16 di-nheiros para lypo do cambio da Caixa deConversão, que o Congresso foi coagidoa aocjl-ar, como transacção, sem o quenão poderia vencer a resistência do mi-nistro da fazenda na sua má vontadecontra a decretação-da tax-a estável, cujosbenefícios só os sectários de fórmulastheoricas' deixam dc reconhecer.
  - observação do anotador: O OCR torna parcialmente ilegíveis algumas palavras, mas a oposição entre taxas elevadas e a decretação de uma taxa estável está explícita.
- **Dívida governamental no lastro da Caixa**
  - voz: `editorial_do_jornal`
  - objetos e direção: lastro (nao_classificavel)
  - posição: Condena o pagamento de dezenove mil contos à Caixa mediante um vale governamental em lugar de ouro em espécie.
  - argumento: O texto sustenta que a operação impôs um ônus sem compensação ao país e desvirtuou a composição prevista para os ativos da Caixa de Conversão.
  - agentes: Sr. Bulhões
  - citação conferida: > Que compensação teve o paiz com essecolossal ônus, que desvirtuou a própriaessência da Caixa de Conversão, onde sópodia entrar ouro cm espécie e hoje tem,entre os saccos do precioso metal, umvale da responsabilidade do governo de19.000 contos?
  - observação do anotador: A janela não esclarece a natureza jurídica do vale nem fornece data precisa para a operação.

#### O Paiz, 1914, edição per178691_1914_10907, página 2

`per178691_1914_10907:p002:c13657-20011`, classe: os dois catalogaram.

**claude**, 2 registro(s):

- **quem forçou a alta do câmbio contra a Caixa**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (estabilidade_taxa_nova), valorizacao_cafe (nao_classificavel)
  - posição: O orador sustenta que Bulhões provocou deliberadamente a alta do câmbio para impedir e depois matar a valorização do café e a Caixa de Conversão.
  - argumento: Acusa Bulhões de ter elevado o câmbio a 18 no governo Nilo Peçanha usando os mesmos processos empregados no governo Rodrigues Alves, e invoca os algarismos como prova pública de que ele forçou a alta nos dois períodos.
  - agentes: João Luiz Alves, Leopoldo de Bulhões, Rodrigues Alves, Nilo Peçanha, Pinheiro Machado
  - citação conferida: > querendo impe-dir a valorização do café e a Caixa deConversão, S. Ex. fez a alta do cambio,levando-o a 18 no governo Nilo Peçanha,e, querendo matal-a, usou dos mesmosprocessos.
  - observação do anotador: Debate travado na sessão do Senado sob o título de expediente "A emissão do papel-moeda e a Caixa de Conversão"; réplica a discurso de Bulhões da sessão anterior, cujo teor não está na janela. OCR muito degradado.
- **se Bulhões seguiu ou abandonou a política Murtinho**
  - voz: `discurso_parlamentar`
  - objetos e direção: lastro (valorizacao), taxa (nao_classificavel)
  - posição: O orador define a política Murtinho como equilíbrio orçamentário mais fundos de resgate e garantia para valorização gradual da moeda, e sustenta que Bulhões não a seguiu, tendo criado câmbio artificial e deixado escrituração precária do fundo de resgate.
  - argumento: Contrapõe a receita nova, o corte de despesa e os fundos de resgate e garantia à política de grandes dispêndios inaugurada no governo Rodrigues Alves, e apresenta cifras de saldo e arrecadação do fundo de resgate do papel-moeda como demonstração.
  - agentes: João Luiz Alves, Leopoldo de Bulhões, Murtinho, Rodrigues Alves
  - citação conferida: > A politica Murtinho consistiu em au-ginento de receita, por novos impostos,diminuição de deSpe-zas, -para tquilibraros orçamentos, na creação dos fundos deresgate e ele gramntia para valorizaçãogradual da moeda.
  - observação do anotador: As cifras do fundo de resgate (saldo de 1902 e arrecadado de 1903 a ...) vêm cortadas pela borda da janela e com OCR corrompido, não sendo possível ler o período completo nem o total. O trecho descreve a política Murtinho favoravelmente, mas a adesão do próprio orador à valorização não é afirmada em termos diretos.

**codex**, 2 registro(s):

- **Alta cambial contra a Caixa**
  - voz: `discurso_parlamentar`
  - objetos e direção: taxa (nao_classificavel), valorizacao_cafe (nao_classificavel)
  - posição: João Luiz Alves sustenta que Leopoldo de Bulhões forçou a alta do câmbio para prejudicar a valorização do café e a Caixa de Conversão.
  - argumento: A alta até 18 é apresentada como resultado deliberado dos procedimentos de Bulhões, e não como simples movimento espontâneo do câmbio.
  - agentes: João Luiz Alves, Leopoldo de Bulhões
  - citação conferida: > Vem fíuei-o para confirmar que, nogoverno Rodrigues Alves, querendo impe-dir a valorização do café e a Caixa deConversão, S. Ex. fez a alta do cambio,levando-o a 18 no governo Nilo Peçanha,e, querendo matal-a, usou dos mesmosprocessos.
  - observação do anotador: O trecho atribui intenção e responsabilidade pela alta cambial, mas não formula diretamente qual taxa alternativa deveria prevalecer.
- **Fundos para valorização gradual da moeda**
  - voz: `discurso_parlamentar`
  - objetos e direção: lastro (valorizacao)
  - posição: A política atribuída a Murtinho empregava fundos de resgate e garantia para promover a valorização gradual da moeda, política que Bulhões não teria seguido.
  - argumento: O equilíbrio orçamentário, obtido por aumento de receitas e diminuição de despesas, é associado à criação dos fundos destinados ao resgate e à garantia da moeda.
  - agentes: João Luiz Alves, Murtinho, Bulhões
  - citação conferida: > A politica Murtinho consistiu em au-ginento de receita, por novos impostos,diminuição de deSpe-zas, -para tquilibraros orçamentos, na creação dos fundos deresgate e ele gramntia para valorizaçãogradual da moeda.O Sr. Bulhões não seguiu essa politica.
  - observação do anotador: A atribuição da política a Murtinho é explícita, mas o OCR torna algumas palavras incertas.

## 4. Apêndice, registros rejeitados na conferência de citação

- **claude**, `per089842_1914_05642:p002:c12218-20882`, motivo `citacao_ausente_da_janela`: Emissão especial da Caixa para socorrer o café
  - citação recusada: A Caixa de Conversão dará ü $. por sacca,l cm inot.is de curso legal, especiaes.
- **claude**, `per089842_1914_05644:p002:c11130-17130`, motivo `citacao_ausente_da_janela`: Associação Commercial pede suspender troco e ampliar circulante
  - citação recusada: A elevação do meio circulante.² Suspensão do troco das* notas daCaixa de Conversão.² Suspensão das autorizações paraemissões dc tif.ilos da Divida Pitliliia,
- **claude**, `per090972_1910_17028:p009:c0-20842`, motivo `citacao_ausente_da_janela`: Ampliar a emissão conversível além do limite legal
  - citação recusada: autoriza as emissões conversíveis alem olimito proscripto
- **claude**, `per103730_1914_00217:p005:c24347-30528`, motivo `citacao_ausente_da_janela`: Suspensão da conversão do ouro na Argentina e moratória
  - citação recusada: O govorno da Republica apresentouao Congresso Nacional um projo-oto suspendendo a convoreão doouro, por papel, sogundo a lei quoogie a Caixa de Conversão, da Re-publica Argentina
- **claude**, `per178691_1906_08005:p004:c31479-42902`, motivo `citacao_ausente_da_janela`: Quebra do padrão e fixação de taxa nova como base da reforma
  - citação recusada: Assim, Sr, prosidonto, Iodos os paizes, que nestas ulíimas décadas procuraram vencer us liuctuacões
- **claude**, `per178691_1906_08005:p004:c31479-42902`, motivo `citacao_ausente_da_janela`: Encaixe metálico como garantia da conversibilidade
  - citação recusada: 2". Formar uni poderoso encaixe metálico parn ganintir o foxer
- **claude**, `per178691_1906_08040:p001:c8775-21557`, motivo `citacao_ausente_da_janela`: Se a caixa de Campista converte de fato papel em ouro
  - citação recusada: A argeiuina converte, o per .''. jchama-se "Jo convcríãov; mas a doIllustre deputado chama-?: "de con-ver.-ão" precisamente por-T-ie... r.fioconverto. Extraordinário !
- **codex**, `per089842_1910_03449:p002:c22393-40752`, motivo `citacao_vazia`: 
- **codex**, `per090972_1910_16872:p008:c18037-28832`, motivo `citacao_vazia`: 
- **codex**, `per103730_1910_00120:p001:c36659-43149`, motivo `citacao_vazia`: 
- **codex**, `per178691_1906_08005:p004:c31479-42902`, motivo `citacao_vazia`: 
- **codex**, `per178691_1906_08040:p001:c8775-21557`, motivo `citacao_vazia`: 
