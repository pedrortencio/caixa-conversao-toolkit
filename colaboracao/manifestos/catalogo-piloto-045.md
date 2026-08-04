# Catalogação de debates sobre a Caixa de Conversão

**Versão:** 0.1.0
**Estatuto:** instrumento de medição versionado. Mudança exige registro em
`docs/decisoes.md`.
**Produto:** extração descritiva para alimentar a escrita. NÃO é atribuição de posição
editorial ao jornal, NÃO é escala.

---

Você recebe uma janela de texto extraída de uma página de jornal brasileiro publicada
entre 1906 e 1914. O texto vem de OCR não corrigido: contém erros de reconhecimento,
ortografia da época e, possivelmente, fragmentos de colunas vizinhas sobre outros
assuntos.

Sua tarefa é catalogar os debates sobre a **Caixa de Conversão** e sobre a política
monetária e cambial brasileira presentes nessa janela.

## Regras que não podem ser violadas

1. **Toda citação tem de ser literal.** O campo `citacao_verbatim` deve ser copiado
   caractere a caractere da janela, com no mínimo 20 caracteres. Ele é conferido
   mecanicamente contra o texto de origem e registros que não casarem são descartados.
   Não corrija ortografia, não corrija erro de OCR, não parafraseie, não junte trechos
   distantes.
2. **Não complete com conhecimento externo.** Registre apenas o que está na janela. Se
   você sabe quem era David Campista mas a janela não diz, o campo `papel` fica vazio.
3. **Ausência é resposta válida.** Se a janela só traz cotação, balancete, movimento
   diário de depósitos, anúncio ou menção de passagem sem argumento, devolva lista
   vazia. Isso é o resultado correto e frequente.
4. **Uma entrada por debate**, não por parágrafo. Se a janela discute taxa e lastro
   como dois desacordos distintos, são duas entradas.

## Vocabulário controlado

`objeto_politica`, escolha um ou mais:
`taxa` (nível da taxa de conversão), `limite_emissao`, `lastro` (fundos de resgate e
garantia, reservas), `conversibilidade` (troco das notas por ouro, suspensão),
`valorizacao_cafe`, `alfandega` (cobrança de direitos e qual taxa se aplica),
`divida_externa` (empréstimos, funding, credores), `competencia_institucional` (quem
decide: Congresso, Executivo, Banco do Brasil), `outro`.

`direcao`, por objeto:
- `valorizacao`: defende apreciação do mil-réis, volta ao par legal de 27 dinheiros,
  política deflacionária, resgate do papel;
- `estabilidade_taxa_nova`: defende fixar ou manter uma taxa nova mais baixa, ampliar a
  emissão conversível, estabilidade cambial como fim;
- `nao_aplica`: o trecho não toma posição sobre esse objeto;
- `nao_classificavel`: toma posição, mas não redutível às duas anteriores. **Use este
  valor sempre que houver dúvida.** Ele é informativo e preferível a um palpite.

`voz`: `editorial_do_jornal`, `assinado`, `reproduzido_terceiro`, `telegrama_agencia`,
`discurso_parlamentar`, `documento_oficial`, `secao_livre`, `indeterminado`.

Atenção ao `voz`: reproduzir um discurso não é o jornal defender aquilo. Se o trecho é
fala de deputado, senador, ministro ou documento transcrito, marque a voz
correspondente e não `editorial_do_jornal`.

## Formato de saída

Responda **apenas** com um array JSON válido, sem cercas de código, sem comentário,
sem texto antes ou depois. Array vazio `[]` quando não houver debate.

```
[
  {
    "janela_id": "<copie o janela_id informado>",
    "debate": "rótulo curto do desacordo, em até 10 palavras",
    "objeto_politica": ["taxa"],
    "direcao_por_objeto": [{"objeto": "taxa", "direcao": "estabilidade_taxa_nova"}],
    "posicao_defendida": "uma frase dizendo o que o trecho defende",
    "argumento": "a justificativa mobilizada, em uma ou duas frases",
    "voz": "discurso_parlamentar",
    "agentes": [
      {"nome": "David Campista", "papel": "relator do projeto", "atribuicao": "autor"}
    ],
    "marcos": [
      {"data": "1906-10-10", "descricao": "Câmara aprova a redação final",
       "confianca": "alta"}
    ],
    "vocabulario_epoca": ["padrão legal", "curso forçado"],
    "citacao_verbatim": "trecho copiado literalmente da janela",
    "observacao": "o que ficou ambíguo, ilegível ou cortado"
  }
]
```

Campos obrigatórios: `janela_id`, `debate`, `objeto_politica`, `direcao_por_objeto`,
`posicao_defendida`, `voz`, `citacao_verbatim`. Os demais podem vir vazios ou omitidos.

Em `marcos`, registre apenas evento datado afirmado no texto (lei, sessão, decisão,
operação). `data` em formato ISO; se o texto der só o ano, use `1906-01-01` e ponha
`confianca` em `baixa`, explicando na `observacao`.

---

## Janela a catalogar

**janela_id:** `per178691_1913_10676:p003:c0-16123`
**jornal:** o_paiz   **ano:** 1913

```
O PATZ — TERÇA-FEIRA, 30 DE DEZEMBRO DE 1913
o % nu iuuii ijunm iumlO Sr. Alfredo Ellis faz uma rectificação —O eminente chefe do P. R. C. respondeao senador paulista efaz consideraçõesinteressantes a propósito de sua atti-tude em relação ás oligarchias e á in-tervenção nos Estados — O Sr. AffonsoPenna Junior confirma as declaraçõessobre a Caixa de Conversão.©amos abaixo os discursos hontemproferidos rio Senado pelo Sr. Alfre-do Ellis e pelo general Pinheiro Ma-chado. O senador paulista foi a, tri-buna fazer. !uma rectificação a umadas orações anteriores do eminentechefe do P. R. fe Este respondeucabal e immediatamente, e proseguiunas declarações que desde alguns dUsvem patrioticamente, com a maiorfirmeza e lealdade, fazendo á Nação.Como das vezes anteriores em qusfalou o Sr. Pinheiro Machado, asgalerias e corredores estavam cheiost as suas palavras causaram profundaImpressão.O Sr. Alfredo Ellis—Começa dlzen-do não protender fazer um discurso.Tendo apenas poucos minutos da ho-ra do expediente, concedidos pelo Sr.Pinheiro Machado, que estava com apalavra desde ante-hontem, e que na-turalmente oecupará toda hora, liml-tar-se-hla a brevíssima rectificação.O facto de vir á tribuna não impor-ta em disputar primazias nem glo-rias; o povo de S. Paulo, principal-mente a lavoura paulista, sabe que aquestão da valorização do café foino Senado tratada exclusivamentepelo orador. Vindo, pois, ã baila essaquestão, o orador não podia mantersilencio, reconhocendo-se obrigado aclarear factos, não tinha outro intuitosenão dizer a verdade. Ao seu ladoestava o Sr. Glycerio, ao qual pediaque, se porventura alguma inexacti-dão ou exagero houvosse na sua de-Bcripç ão, tratasse de corrigil o».A autorização para o empréstimode 15 milhões, promovida na Câmarados Deputados pela bancada paulista,veiu no orçamento da receita, em de-cem bro de 1905. O relator era o Sr.Jtamiro Barcellos, que naquelle tem-po IIlustrava uma das cadeiras na re-presentação do Rio Grande do Sul.Por oceasião da discussão desse dis-positivo no seio da commissão de fi-nánças, foi elle o unico advogado domesmo, encontrando da parte de to-dos os outros collegas a mais irredu-tlvel, a mais feroz opposição. Tantolato ê certo que, ao ser assignado oparecer, S. Ex., retirando-se, depoisde uma hora do discussão, da com-missão de finanças, commttnicava aoorador que tinha assignado vencido.E nessa oceasião referiu-lhe a luetaterrível, tremenda, que tivera no seioda commissão, no sentido de impres-elonár os seus membros para adnpçãode uma medida que viria resguardar,não um produeto paulista, mas oprodueto nacional.Recorda-se bem o orador que nessaoceasião o representante do RioGrande do Sul lhe declarou que omais acerrimo inimigo da medida ti-nha sido o senador por Pernambuco,Sr. Rosa e Silva, que, durante duashoras, discutira o assumpto com ver-da deira implacabilldàde.Portanto, o parecer da commissão. ao orçamento da receita era contrarioa essa modida. Para os paulista ern,no entanto, ella uma questão do vidae morte, porque determinaria se sepoderia executar o plano formuladoda valorização do café.O Sr. Glycerio—Alias, nós só que-riamos o endosso; nós éramos re-eponsaveis e pagávamos.O orador acha opportuna a ocea-siâo para dizer que esse endosso daUnião, prestado de accordo com a lei,não existe mais, porquanto esse em-presumo já foi resgatado.O seu nobre amigo, Sr. Glycerio,naturalmente revoltado contra a du-reza do orador e sabendo que elle fô-ra incumbido de discutir o assumptono Senado, chamando outro repre-sentante dc S. Paulo, infelizmentefallecido, o Sr. Lopes Chaves, com-binou que no dia seguinte, após o dis-curso do relator da receita, o oradorviesse á tribuna fazer um discursoviolento para resalvar a rcspónsábili-dade da bancada paulista. Dc facto,no dia seguinte, o orador achava-seapparelhado para desempenhar ocompromisso que houvera tornadocom os seus collegas, aguardando ahora da abertura da sessão, quando,ao entrar no recinto o Sr. PinheiroMachado, lhe disse: "Então, Sr. ge-ncral, quer liquidar o Estado de SãoPaulo, evitando que fique consignadano orçamento da receita a medidanecessária para levarmos a effeito oplano da valorização do café?"Da resposta que obteve recorda-sebem:—V. bem sabe, meu amigo, quepela Caixa de Conversão farei tudo;mas sempre fui infenso ao plano davalorização do café.A' vista desta declaração, o oradorreplicou:—Como amor com amor so paga,como V. Ex. nos nega a medida ne-cessaria á solução da lavoura dn cafédo Estado do S. 1'aulo, nós negare-mos ao orçamento da viação o dispo-sitlvo que dá 20 mil contos de réispara abrir a barra do Rio Grande doSul.Irritado, o Sr. Pinheiro Machadoperguntou-lhe:— l'or que e como?—Porque nós furemos obstrucção.E' a unica medida de que nós pode-mos lançar mão para corroborar oditado de que "amor com amor so¦ O orador entrou na salínho do café.D'ahi n 10 minutos, ou um quarto dehora, recebia um bilhete do Sr. Ra-miro Barcellos, bilhete este que temem seu archivo, dizendo que. se ospaulista estavnm dispostos a dar to-das us garantias para resguardar aUnião. o7le não hesitaria em modificaro parecer.Consultados a este respeito os Srs.GÍycerlò o Chaves, responderam im-mediatámerite que aceitavam, tantomais quanto S. Paulo nada mais que-ria. nem exigia, a não ser o endossoe isso mesmo porque os banqueirosfaziam questão delle, não sendo abso-lutamonté sua intenção prejudicar aUnião numa só libra que fosse. Tendoo Sr. Ramiro Barcellos modificado oparecer, o Sr. Glycerio declarou aoorador: Fm logar de um discurso violen-to, vibrante. V. vai fazer um discursode luva de pellica, emquanto eu voutrabalhar e expor aos amigos e sena-dores a conveniência de votar a me-dida. Foi assim que o orador se man-teve na tribuna do Senado nté as 8horas da noite, só se sentando depois¦ de ter conhecimento dc estar ganha acausa.Esta ('¦ a verdade histórica, affiniiao orador, nccrcscentnndo não dispu-tar primazia nem gloria.Entendeu fazer a rectificação ne-cessaria, porquanto os paulista sa-liiam que '> Sr. Pinheiro Machadoera infenso ao plano da valorizaçãotio café.Aproveitando a oceasião, declaraqi.e a iniciativa sobre a Caixa de(Smversão; de justiça, pertence ao se-nador Toledo iiza, que a ventilou d#
volta de uma viagem il RepublicaArgentina. Nada mais natural que oSr. Pinheiro Machado aproveitasse aopportunidade para fazer a escnptu-ração de sua vida política, dos actosde benemerencia que tem praticadona Republica. O orador estimaria atéque o representante do Rio Grandedo Sul só pudesse éscriplurar benefi-cios. favores e sacrifícios. Reconhecea intervenção efficaz do Sr. PinheiroMachado quanto ao estabelecimentoda Caixa de Conversão. Velho repu-blicano, o orador, comquanto man-tendo divergências quo abrem umlargo fosso entre o Sr. Pinheiro Ma-chado, ê e será incapaz abso-tamento de diminuir por qualquerfôrma os serviços por S. Ex. pratica-dos em prol da Republica.Mas, com a mesma justiça, lembra-va que o representante do Rio Gran-de do Sul-devia tumbom escripturaro seu debito, porque a sua responsa-bilidade é tremenda, é tão grave, taopesada, que só os hombros do um gi-gante, de um Hercules as poderiamsupportar. Cabem-lhcao par de gran-des serviços prestados .1 Republicagrandes e graves responsabilidades ; a tribuna
lorlzaçao, a politica dominante de SãoFoi nesse sentido que eu proferi amais a invectlveí por nos ter abando-nado; porque, entre nós, não haviacontrato que a prendesse â nossa ao-ção politica.Foi nesse sentido que eu proferi aphrase que despertou commentariosdo illustre órgão da Imprensa, a "Ga-zeta", onde tenho, ha muitos annos,desde a Constituinte, entre seus reda-ctores, uma affeição inalterável e du-radoura — que estranhou que eutivesse censurado a condueta dps po-lltlcos de S. Paulo. Não ha tal. Euquiz tornar bem patente que entreS. Paulo e o obscuro orador nãotinha, havido contrato algum secreto,prendendo os políticos daquella terraao programma político a que nosachamos vinculados. O meu objei/.-vo foi outro; foi o de, que não se dissés-se jamais que os políticos paulistas ti-nham tirado proveito de nossos esfor-ços e depois nos tinham abandonado;eu quiz tornar bem patente que nos-sa acção, como a, de S. Paulo, foicommum em uma questão de ordemeconômica, que poderia, estar, comoesteve, perfeitamente divorciada dosinteresses políticos de outra natureza.E' por isse tambm que, fazendonotar que Unhamos tido interferênciaactiva na união dos diversos clemen-tos políticos de S. Paulo, então separa,dos, ficou patente — e meu illustrecollega o amigo de infância o e.onfir-mou — que foi devido á minha ao-ção quo a notável agremiação poli-tioa chamada "a dissidência" se con-gra cara com a situação dominante.O Sr. Adolpho Gordo — Eu soubepositivamente que assim foi.O SR. PINHEIRO MACHADO— E'preciso que o Senado e a Nação saibamque esses illustres moços, desde aConstituinte, se conservaram sempredivorciados de nossa acção politica,só se congregando quando se tratouda candidatura, do Sr. Campos Saltes.Portanto, não era nenhum interes-se pessoal nu subalterno que me le-vava a competir pela unidade da po-lltlca paulista, fazendo com que esseselementos, incontestavelmente degrande valor naquelle Estado, prestas-s«n Ftiü apoio ao governo do Sr. Ty-birlçfi.Posto de lado esse incidente, vouentrar no assumpto que me trouxeperante os attentados, os desmandos eos desregramontos commettidos peloactual governo. Em qualquer caso,cabe-lhe ter sido solidário, pelo silen-cio mantido, por factos que nao en-contram parallelo no registro da nos-sa historia.O orador termina fazendo ver quea dôr mais profunda, a amarguramais dilacerante apunhalam a sua
Teneiono fazer considerações rapi-das, synthetlcas, para não tomar otempo, jâ tão estreito, do Senado, i\aliás, como as affirmaçÓos que tenhoa fazer nobre a questão das oligar-ehlas e da Intervenção nos Estadosserão todas acompanhadas de do-cumentos, não precisarão, portanto,de extensa explanação.No correr de minha exposição te-rei opportunidade. também de responalma, o seu coração d» yel>1^ao pronunciar palavras que denotam ^ . ^ senador por S. Paulo,a situação miserrima que atunessa D (pRdo so]lcita(](, (]o or.ulor aRepublica.O Sr. Pinheiro Machado — Sr.presidente, devo dar graças â minhafortuna, por ter suggerido ao illustresenador por S. Paulo, cuja ausênciadeploro, o discurso que S. Ex. acabade proferir e que veiu preparar oexordio da oração que vou ter a hôri-ra dc dirigir ao Senado.Devem ter noticia os meus illus-tres collegas que, por angustia detempo, preóccupado com muitos as-sumptos importantes que nos pren-dam a attenção neste fim dc sessão,tenho tido a honra de me dirigir aesta illustre corporação, sem de ante-mão preparar, como aliás faço sem-pre, as minhas arengas. São ellasproferidas desordenadamente, mascom o cunho da maior sinceridade,procurando inspirar-me sempre naverdade, que não precisa de eloquen-cia para se impor.O meu illustre collega por S. Pau-lo. que tinha antes solicitado que eulhe cedesse a palavra para uma re-ctificação ao meu discurso anterior,deu ensejo, com os conceitos queemittiu.a que o Senado verificasse bemcomo fórum exaetns as proposiçõesque tive a honra de emittir desta tri-buna, na sessão passada. S. Ex. nãorectificou absolutamente nenhum dosconceitos aqui por mim proferidos.O Sr. Alfredo Ellis — Esclareciapenas.O SR. PINHEIRO MACHADO —S. Ex. apenas veiu declarar que a suaIllustre Individualidade também tinhasido i>'U'té netivn. na celebre questãoda valorização do café.Disso não me oecupei, como nãome oecupei da collaboração não mi-nos importante de innumeros perso-nagens politicos que tomaram parte,não só na questão da valorização docafé, como na da Caixa de Conver-são.Devo, porém, tornar evidente queha um lamentável equivoco da partodo meu Illustre collega, aquelle emque S. Ex. incorreu quando declarouao Senado que, ao saber que a com-missão de finanças, cm sua quasi to-talidade, era lnfensa ao projecto deempréstimo, e, encontrando-se com-migo, lhe declarara, eu: "Sou Intensotambém á valorização, menos á Caixade Conversão".S. Ex. está equivocado, porque nes-sa oceasião ainda não so agitava aquestão da Caixa de Conversão, e,assim sendo, .ainda não estando acaixa na tela da discussão, evidente-mente eu não podia proferir taes pa-lavras.O Sr. Alfredo Ellis — Dezenas dovezes V. Ex. pronunciou estas pala-vras, em conversa commigo, aqui noSenado.O SR. PINHEIRO MACHADO —Posteriormente; naquella oceasião,não.Devo dizer mais an Senado que, an-te-hontem, declarei desta tribuna, aoler a carta do illustre Sr. Borges deMedeiros, que S. Ex., como eu, erairifelíso ao projecto de valorização.Portanto, o nobre senador por SãoPaulo nada adiantou quanto n. esteponto, e quando muito veiu apenasconfirmar proposições por mim emit-lidas desta tribuna nntc-hbntcm.Sempre, Sr. presidente, declarei aosIllustres paulistas, que commigo seentendiam, e mesmo em carta, quedirigi ao Dr. Jorge Tybirlçá, que re-ceava, pelos resultados do plano devalorização; que me parecia estoplano por de mais avrnturoso.sem ba-sr> r:i realidade' das oojsas, c que. paraimpedir que elle fracuçasse, era ne-cessarjn no menos diminuir os í-ousperigos, amparando-o com a Caixa deConversão.Nós todos sabemos que, devido acausas varias, mas felizes, o planovingou, produzindo effeitos benéficospara S. Paulo, razão por que todosdevemos estar de parabéns com estaoperação.O Pr. Alfred.-i Ellis — Àpoindo.O SR. PINHEIRO MACHADO—MasIneoiUcSliivelmenle, !-'. I0x., no seu ele-Vildo critério, deve reconhecer queo plano continha termos aleatóriose périgosissimós; que, se as safrasseguintes fossem avnltad.is, talvez osesforços c os sacrifícios de S. Paulofossem impotentes para conseguir aalta do preço dc caféjO Sr. Francisco Glycerio — Masem grande parte o êxito da operaçãofoi devido k capacidade dos adminis-tradores de S. Paulo.O Pr. Alfredo Rtlis — Apoiado.O SR; PINHEIRO MACHADO—In-negnvelmente.mns lambem á coopera-ção que o Congresso o o governo da.Rr-publica prestaram a S. Ppulo.O Sr. Francisco Glycerio — Nósnão negamos isto: pelo contrario|agradecemos a cooperação do gover-no da l'r.i."i".Os Srs Alfredo Ellis e AdolphoGordo — Apoiado.o sk pinheiro machado—Naoregistramos esses factos, Sr. presi-dente, como acto de benemerencianossa para despertar o sentimento degratidão de quem quer que seja, massomente para domonstrsaSque a no.-saacção politica tem girado sempre emtorno dos intereses supremos do paiz,onde quer que eiles se achem. E porIsso eu dizia anle-iiontem que nãofiz accordo algum de ordem politicacom S. Paulo, no sentido de prendera politica paulista á. nossa esteira.Tanto que, concluída a campanha, acelebre e acirrada campanha da \flk»
que, tendo solicitado do orador a palavra para fazer uma rectificação,se aproveitou do momento para umaaggresão incontestavelmente menosopportuna. (Apoiados.)Sr. presidente, neste paiz, entre oshomens políticos de responsabilidade,nenhum me tomou a dianteira na con-demnação das oligarchias. E' verdadeque não 'mereceram minha approva-ção projectos appareoldos na Câmara,eaqui no Senado, tendentes todos, in.directamente, a cercear o abuso que seestava infiltrando nos costumes poli-ticos dos detentores do poder nos Es-tados de se apropiarem das posiçõespara nell.is permanecerem indefinida-mente, succedendo-so.procurandn seussuecessores na própria familia, estabe-leccndo uma estruelura politica oadministrativa tão apertada, que emvários Estados da Republica já osmais vehementes protestos surgiamcontra esse 'processo evidentementeanti-republicano.Aqui no Senado o Sr. senador EricoCoelho c o nosso -mallogrado e saudo-so correligionário, senador VirgílioDamasio, apresentaram um projectoevidentemente attentatorio á Consti-tuição, procurando, não interpretal-a,mas remoidelal-a, de modo a golpearde morte as oligarchias.Taes eram os abusos que este pro-jecto procurava eliminar, que elle dês.pertou sympathias no espirito de mui-tos constituciònàllstas republicanosdesta casa, esquecidos de que procura-vam debellar esses costumes—por quonão dlzol-o?—criminosos, praticandouwi -mal maior, que era o de deturparo pensamento, a letra, e o espirito danossa Constituição.Nessa oceasião, Sr. presidente, fuif
```
