# Primeira exploração da base tratada

**Data:** 2026-07-28. **Estatuto:** primeira passada exploratória, deliberadamente
imprecisa. Não decide construto, não altera codebook, não vale como codificação. As
afirmações sobre o teor dos textos são leitura minha e precisam de conferência de
Pedro na página original antes de irem para qualquer capítulo.

**O que foi lido:** as 28 peças classificadas como editorial substantivo, integralmente,
mais os manifestos quantitativos da base. Total lido: cerca de 155 mil caracteres de
fonte.

## 1. O mapa: onde o debate mora

A base tratada são 468 peças com status `keep`, 566 mil caracteres nas 239
substantivas. A distribuição por forma responde à pergunta de onde vale a pena ler.

| forma | substantivas | rotina ou incidental |
|---|---|---|
| notícia | 117 | 114 |
| artigo | 64 | 0 |
| editorial | 28 | 0 |
| telegrama | 20 | 8 |
| tabela e boletim | 4 | 67 |
| lista e anúncio | 4 | 25 |

Três leituras saem daí.

**O argumento mora em artigo e editorial**, 92 peças, e nenhuma delas caiu em rotina.
São as formas com densidade doutrinária, e a mediana do editorial é de 4.652
caracteres contra 636 da notícia.

**O volume mora na notícia**, 117 peças substantivas, mas o gênero é sobretudo relato
de sessão parlamentar. Isso importa para o construto: boa parte do que o corpus
oferece como substantivo é o jornal registrando a fala de terceiros, não falando.

**A rotina é o boletim.** Das 71 tabelas, 67 são rotina ou incidental. O movimento
diário de depósitos e emissões da Caixa é o que faz a menção pelo nome atingir 53% do
acervo. É ruído para posição e é sinal para saliência.

Por jornal, entre as substantivas: O Paiz tem a mediana mais longa, 2.278 caracteres,
porque publica discursos inteiros; Correio da Manhã 1.425; Correio Paulistano 959;
Gazeta de Notícias 878. E O Paiz e Gazeta concentram-se em notícia (33 e 41), enquanto
Correio da Manhã tem a maior fatia de editorial (11 dos 28).

Das 239 substantivas, 129 não têm seção identificada. As seções nomeadas que aparecem
e que importam são `NA CAMARA`, `NO SENADO`, `SECÇÃO LIVRE` e `PARTE COMMERCIAL`.

## 2. Três defeitos do texto extraído, medidos

A coluna `texto` de `amostra_para_rotular.csv` não é a página. É uma reconstrução feita
pelo `claude-sonnet-5` sob o protocolo `recuperacao-artigo-visao 0.1.0`. Ela falha de
três maneiras distintas, e as três apareceram na leitura.

**Interpolação do modelo.** 18 das 468 peças, 3,8%, contêm colchetes escritos pelo
modelo, não pelo jornal. Exemplos literais: `[continua com texto extenso sobre a crise
cambial, emissões, bancos, câmbio, etc.]` em O Paiz de 20/09/1906, e `[texto extenso do
editorial sem menção literal à Caixa de Conversão nesta seção]` em Correio da Manhã de
09/04/1911. A taxa é maior justamente no estrato mais valioso: **4 dos 30 editoriais,
13,3%**.

**Sangria de coluna.** A peça da Gazeta de Notícias de 15/01/1912 começa discutindo as
retiradas da Caixa e termina em estatística populacional do Paraguai de 1867, com
Solano López e número de indígenas no Chaco. O `ocr_contexto` da mesma peça mostra a
causa: o texto vizinho na página tratava de um duelo em Assunção e de telegramas de
Buenos Aires. O extrator atravessou para a coluna ao lado.

**Substituição de artigo.** O caso mais grave. A peça de Correio da Manhã de 26/09/1906
traz, na coluna `texto`, a crônica de um banquete, com o cardápio completo, `Consommé
à la Colbert, Tronçon de bacalhau sauce ravigotte`. Não tem relação com a Caixa. Mas o
`ocr_contexto` da mesma peça guarda o que estava de fato na página: *"affirmam que, no
caso de ser approvado pelas duas casas do congresso, o projecto da caixa de conversão,
o sr. Rodrigues Alves, presidente da republica, o vetará"*. O rótulo de Pedro estava
certo, a peça é substantiva, e o que se perdeu é uma ameaça de veto presidencial ao
projeto em setembro de 1906.

**Consequência operacional, e é uma correção ao plano de leitura:** a leitura da ficha
deve ser feita na página, não na coluna `texto`. O `ocr_contexto` é a âncora confiável,
porque é OCR determinístico da própria Hemeroteca; `texto` é reconstrução e pode
interpolar, sangrar ou trocar de artigo. O campo `citacao_ancora` da ficha só vale se
transcrito da página.

## 3. O que cada jornal disse

### Correio da Manhã: atravessa o eixo entre 1906 e 1910

Em 1906 é o adversário mais duro. A crônica de 25/09/1906, seção `NA CAMARA`, abre com
a enumeração *"Anarchia mental. Confusão e bacharelia. Contradicções e reservas"* e
acusa David Campista, autor do projeto, de emendas que revelam *"a pouca confiança que
o autor do projecto de Caixa de Conversão tem no seu"* próprio texto. Em 10/11/1906,
sobre o relatório de Custodio Coelho, diretor da carteira de câmbio, o jornal usa o
próprio Coelho contra a Caixa: em março ele chamara de *"immoral"* medida que quebrasse
o padrão legal, em novembro sustenta que a Caixa não o quebra, e o jornal conclui que
os fatos *"provam que s. ex. tinha razão em março e já não tem em novembro"*. O
Convênio de Taubaté aparece como *"aventuras"*.

Em agosto de 1907 a posição já mudou. O artigo "MELHORAR PELO FOGO" registra a queda
do *"fetichismo do padrão a 27"*, diz que a Caixa *"erigiu barreira intransponível"* ao
retorno ao par, e trata a função valorizadora do fundo de garantia como coisa passada
*"para o domínio das chimeras"*. Mais: sugere que a taxa deveria ter sido fixada em 16
dinheiros, e não 15, três anos antes da lei que a fixaria.

Em julho de 1908 defende a emenda Barbosa Lima, que cobraria direitos aduaneiros à taxa
de 15 e não ao padrão legal. O argumento é o do escândalo visível: *"no Brasil, por
toda a parte, no cambista, no negociante em grosso, no negociante a retalho, nos
bancos, a libra esterlina vale sempre 16$000. Só na Alfândega, para a cobrança de
direitos, é que a libra esterlina vale 20$000!"*. E concede, de passagem, que quebrar o
padrão não seria desonesto.

Em 1910 defende manter a Caixa *"no pé em que está"* contra a elevação para 16. O texto
de 29/05/1910, "Minas e o cambio", nomeia quem ganha com a reforma de Bulhões: *"os que
não esquecem os bons tempos em que, com as differenças de cambio, se fizeram em horas
grandes fortunas nas ruas da Alfandega e Candelaria"*, e *"as empresas oneradas de
emprestimos externos em ouro"*. Acusa Wenceslau Braz de sacrificar a lavoura e a
indústria mineiras por politicagem.

A trajetória, portanto, é de oposição ortodoxa em 1906 a defesa do arranjo existente em
1910. Se o eixo for lido de forma ingênua, o mesmo jornal muda de lado. Se for lido
pelo interesse defendido, o comércio importador e a lavoura contra o governo de turno,
há continuidade.

### Correio Paulistano: a defesa técnica, e a ortodoxia pelo instrumento heterodoxo

Em 03/07/1906 apresenta a justificação completa: o balanço internacional não derrubará
o câmbio abaixo da taxa fixada; mesmo esgotada a Caixa não há dano, porque *"a moeda
papel emittida seria recolhida exactamente na proporção do ouro que fosse retirado"*; e
a objeção moral ao par de 27 não procede, porque não se trata de converter papel de
curso forçado e sim de um contrato com o portador do ouro. Mobiliza precedente
internacional com precisão: a Argentina a 0,44, o projeto chileno com certificados de
depósito, e os certificados-ouro do Tesouro norte-americano.

Nesse texto o limite proposto é de 320 mil contos correspondentes a **15 milhões
esterlinos**. Na redação final aprovada, publicada pelo mesmo jornal em 11/10/1906, o
artigo 3º fixa os mesmos 320 mil contos como correspondentes a **20 milhões
esterlinos**. A diferença é a taxa, e o texto de julho já argumenta a 15 dinheiros.

O argumento paulista de 1910 é o mais interessante do ponto de vista do construto:
*"quanto maior fôr a quantidade de ouro em nossa circulação, menor ficará sendo a
porcentagem do papel... mais próxima irá se tornando a circulação metallica"*. Ou seja,
o jornal reivindica o fim ortodoxo, a circulação metálica, pelo instrumento que os
ortodoxos combatiam. Uma escala unidimensional comprime exatamente essa figura.

### O Paiz: hospeda o debate, e a voz própria é outra coisa

O Paiz é o caso que separa duas coisas que não devem ser confundidas: hospedar vozes e
ter posição. As duas são dado, e só a segunda é o estimando.

Em 22/12/1910, na `SECÇÃO LIVRE`, publica o
discurso de Cincinato Braga contra qualquer taxa acima de 15, com resenha internacional
de Itália, Áustria, Estados Unidos, Rússia, Japão e Índia, e uma tabela de necessidades
de ouro de 77 milhões esterlinos para o ano agrícola de 1910-11. Dois dias depois, em
24/12/1910, publica o parecer da comissão de finanças do Senado, relator João Luiz
Alves, favorável à elevação para 16, com a tese de que *"mais do que a questão da taxa,
o que interessa á Nação é a fixidez do valor da sua moeda"* e citação de Rafalovich e
Ansiaux. Em 29/12/1910 publica, de novo em secção livre, o discurso de Galeão Carvalhal
contra a elevação.

Três peças em oito dias, duas contra e uma a favor, e ao menos duas em espaço pago. Uma
codificação por edição-dia atribuiria a O Paiz posições opostas na mesma semana. Mas o
fato de o jornal abrigar os dois lados em oito dias não é apenas ruído de medição, é
uma informação sobre a função que ele cumpre no debate, e vale ser medida por si, como
composição de vozes hospedadas. `SECÇÃO LIVRE` é espaço pago e precisa de tratamento
explícito no codebook. O que define a posição do jornal é o editorial.

A voz própria de O Paiz aparece em 14/05/1910, num editorial doutrinário que abre com o
Gun-Club de Júlio Verne para dizer que *"no mundo economico, como no kosmico, existem
leis que ao homem não é licito desprezar"*. Elogia Joaquim Murtinho, aponta o paradoxo
de que *"o papel-moeda inconvertivel era taxado mais alto que o convertivel"*, e conclui
que a Caixa é potente para evitar a baixa e impotente para conter a alta. É ortodoxo. E
em 21/12/1908 chama a instituição de *"doudíssima caixa de conversão"*, mas no contexto
de atacar a candidatura de Campista à presidência, o que é briga sucessória e não
doutrina monetária.

### Gazeta de Notícias: declara-se parte

Em 15/01/1912 a Gazeta faz o que nenhum outro faz na amostra, declara por escrito a
própria posição acumulada: *"Esta folha teve uma grande responsabilidade no auxilio que
prestou á tarefa da Caixa"*, atribui a si intervenção *"em prol dos protestos da Camara
contra a tarefa destruidora"* do ministro Bulhões, e elogia o *"formidavel discurso do
Sr. Cincinato Braga"*. O motivo imediato é desdramatizar retiradas de três mil contos,
*"cerca de um por cento"* dos depósitos, e a peça sustenta que a Caixa é instituição de
emissão, não de depósito.

É uma declaração de posicionamento editorial explícita, com datas e nomes, e serve de
âncora para calibrar tudo o que o jornal publicou antes e depois.

## 4. A fase 4 confirma o risco já registrado

O parecer sobre a perenidade do eixo, registrado em `codebook-fases.md`, previa que em
1914 defender a suspensão pudesse ser consenso pragmático e não posição. A leitura
confirma, e dá os marcadores.

Na sessão de 12/12/1914, reproduzida pela Gazeta, dois deputados votam contra a
prorrogação da suspensão do troco por razões incompatíveis. **Martim Francisco** usa o
registro da honra contratual: *"O artigo 1º autorisa o governo a faltar a sua palavra;
autorisa o governo a, como depositario, não restituir o que lhe foi confiado. Pela
primeira vez se aconselha a patria brasileira a ser desonesta"*. **Serzedello Corrêa**
quer o contrário: que a Caixa funcione normalmente e, esgotados os depósitos, morra.
*"A Caixa é um grande tramboiho, e nada mais"*, e a riqueza nacional presa à taxa de 15
torna a conversibilidade uma catástrofe para o patrimônio privado.

Os dois são contra a suspensão. Um defende o compromisso, o outro quer o fim do câmbio
fixo. Em 1914 a variável "posição sobre a suspensão" não é projetável no eixo. O que
discrimina são outros marcadores: veredito retrospectivo sobre a Caixa, regime desejado
depois, e natureza da emissão de socorro. É exatamente a subdivisão que o parecer de
14/07 antecipou.

Registro adjacente: o relator da comissão, Carlos Peixoto Filho, preferia um imposto
sobre a exportação de ouro amoedado à suspensão do troco, *"a exemplo do que se fizera
no anno immediato ao da creação da Caixa"*. E Martim Francisco aponta que a Caixa
responde por cerca de 19.890.000$ excedentes ao depósito.

## 5. Cinco achados que mexem no codebook

1. **A mesma peça circula entre jornais.** O discurso de Cincinato Braga aparece em O
   Paiz e em Correio da Manhã; o de Galeão Carvalhal aparece em Gazeta e em O Paiz. Sem
   deduplicação, o corpus conta o mesmo argumento como opinião de dois jornais.
2. **Espaço pago é voz de terceiro.** `SECÇÃO LIVRE` precisa de tratamento explícito no
   codebook, e o campo `voz` da ficha já o comporta.
3. **Hostilidade ao autor não é hostilidade à política.** O Paiz de dez/1908 é o caso
   modelo, e vira caso-limite do bloco da fase 2.
4. **O eixo não é metalismo contra papelismo, e a monografia já dizia isso.** O Correio
   Paulistano de 1910 defende a circulação metálica via ampliação da emissão
   conversível, e isso não é anomalia: é a regra do período. A monografia (p. 9)
   registra que a Caixa *"não representou cisão com o pensamento metalista"*, que
   *"mesmo aqueles que defendiam o projeto, apoiavam-se na 'sã doutrina' da circulação
   metálica"*, e que *"nenhum grupo estava em condições de negar o padrão-ouro"*
   (TORELLI, 2007). E define o eixo correto: disputa entre *"os setores que defendiam a
   permanência da política deflacionária [...] até que se restaurasse o 'par legal' de
   27 dinheiros"* e *"os setores que propunham a expansão monetária e a estabilidade do
   câmbio a uma taxa nova"* (NEUHAUS, 1975). O eixo operante é **valorização contra
   emissão e estabilidade a taxa nova**, não metalismo contra papelismo.

   Isso contradiz o que `codebook-fases.md` afirma hoje na linha 11, que trata o eixo
   ortodoxo e expansionista como *"encarnação, no debate da Caixa, da clivagem
   metalismo×papelismo"*. A contradição é entre dois documentos do projeto e precisa de
   decisão registrada, porque muda a definição do construto e não apenas a redação de
   um bloco.
5. **A alfândega é objeto de política e não está no esqueleto.** A cobrança de direitos
   à taxa da Caixa ou ao padrão legal é disputa concreta de 1908 e merece entrar no
   bloco da fase 2, ao lado de lastro, limite e taxa.

Marcos cronológicos que a leitura fixou e que servem de janela: veto presidencial
ameaçado em set/1906; limite passa de 15 para 20 milhões esterlinos entre julho e
outubro de 1906; taxa de fato a 16 pelo Banco do Brasil em maio de 1910, antes da lei;
lei de dez/1910 elevando a taxa a 16 e o limite a 60 milhões esterlinos; fundo de
garantia declarado inexistente ou desfalcado no debate de 1910, com requerimentos de
informação recusados nas duas casas; fuga de ouro associada à guerra dos Bálcãs;
suspensão do troco pela lei 2.862 de 15/08/1914, prorrogada em 15/09 e de novo em
dez/1914 até o fim de 1915.

## 6. Próximo passo na sequência

Antes desta leitura continuar, três coisas em ordem de custo.

1. **Rotular os 40 descartes sorteados.** Uma tarde. Converte a medida pivô de
   calibrada num ano só para com viés medido, e é a pendência que a retomada de 25/07
   põe em primeiro lugar.
2. **Decidir se a extração é refeita para as 92 peças de artigo e editorial.** A taxa
   de 13,3% de interpolação no estrato editorial é alta para o material que vai fundar
   o codebook. A alternativa barata é ler direto da página e ignorar `texto`, que é o
   que recomendo, porque não custa chamada de API nenhuma.
3. **Ler a camada 0 pela ficha**, começando pela fase 1, onde o bloco do piloto serve
   de controle.

O que esta exploração não tocou e ficou pendente: as 64 peças de artigo substantivo,
que são o dobro do volume dos editoriais e onde o campo `voz` deve responder se há
editorial escondido sob outro rótulo.
