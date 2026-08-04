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

**janela_id:** `per090972_1906_15418:p004:c8556-16567`
**jornal:** correio_paulistano   **ano:** 1906

```
publicado, uliás, porvarias vozes.P. E esso cafó que fosse agoracomprado, teriu o governo de ro-tel-o sempre'!R. Por certo que não.Si, como devia ler feito, bou-vesso intervido o governo ho 2 ouIres nnnos. comprando cafc, quan-do, cm virtude da grande sulrnde 1901 (2, o slock orn superior o\2 milhões do saecus, ó cluro qucu esln horn lorio vendido quasi 8milhões dc suecos, islo c, u diffe-rençu do filock daquella epochacm relação no de hoje, que nnovni nlcm dc !l l|2 milhões. Foi oconstituo que nlisorveii essa diffe-rençu ile quusi 3 milhões «lc sue-cas." Será o consumo que denlrodo |ioueos unnos absorverá o caféque o governo.agora comprar, rcs-tiluindo-iios o dinheiro que agorafór em]ircgado e bobililando-posporlnnto a resgatar todo o oin-preslimo quo se vai icvuntor.Esse. cotiBiimo, como ó sabido,atigmentn sempro, uo pusso quo unossn producção poderá crescercm um ou oulro unno, como Bgo-ra, mus acabará por diminuir.Pura tunto influirão necessuria-mente a uusenciu do oulésnos no-vos eo envelhecimento dos cafòsacsexistentes.P. E o que potisu sobro um em-preslimo á lavoura ?B. Como complemento á valo-rizução, seria um bem ; como sub-stilulo, serio um erro gruvissi-mo.Si os preços continuarem mino-sos, os fazendeiros contempladosconsumirão mnis o dinheiro quoobtiverem, assim como hão con-sumido ns lortuíias suus c dc seusnmigos, parentes o conimissorior, :c evidente, o dispensa ex|ilunações.Nuo podendo influir nos preços, oempréstimo iiciú um dosustre por-que u criso continuará, aggravadaaindu pelu nova divido.E' Fallido oinda que taes empres-limos são lentnineiitc processados,c sónierilc concedidos a muilo pou-cos lavradores, embora á etistu dotodos.Aliás, a elevação dos preços pormeio da compra e retenção do cn-lè, de accôrdo com o Convênio, si-gniflca um empreslimo: tombem áiavourn, empreslimo quo locn otodos, proporcional menle á produ-cçfio dc cadu um : empréstimo queó promplo e dispensa formalidadese prolecçfio c que por isso ó oqui-lutivo e eiTiciiz, empreslimo, emlim,quo contém umu virtude ineslitnn-vel; é-exigir ser applicado umo sóvez, emquanto que os benefíciosrOsulahles (nlta do preço) no rc-pe-lem Iodos os annos enriquecendou luvoura o o pniz.I . Porque motivo, enlão, ha on-contraclo ttinlu opposição uniu me-dida lão niinples o tão vantajosa,qual a da valorização Vlt. t) principal c a ignorância ;mus ha outro: n inilillcrençu, o des-amor, pura não dizer mais, pelasclasses protlüctora . Sobro o casoha um lacto publico que mo iiIibc-nho dc explicar: porque motivo osr. presidonlo dn Republica, dejioistle haver patrocinado o projeclo devalorização, duranto mozes, rc|iu-diou-o nn mensagem, acnusandoos Iros jiresidenles dos Eslados deombobirem o lavoura com promes-sus irronlizuveis ? Si eram irrenli-;:;:u>:s |iorque as endossou'' Porqueus repclliu si náo eram?Note-se quo mo refiro ú vnlni-i-znçáo do calo o não ii questão mo-m-iario. Nem a cláusula do con-venio, referente á caixu de con-versão, oltorn em uma sò linha aninho dc valoriznção. A caixa deconversão, linhn, como lem, porlim conter—não digo baixar—con-ter o cnmbio, ou sublrahil-o ainfluencia do um lnc'or nnormalrepresenlado pelo empreslimo pro-jectado. Esse empreslimo viriaullerur o esludo de coisas cxislen-tc, islo e, prejudicor u muito gen-lo, desorganizando situações : eradever tios Estados—por ellc res-ponsaycis--indicar, sulicitar umamedida capaz dc evitar semelhnn-tes males. Ao Congresso cabia ocabe concedcl-a ou não. Nadamais correcto o mnis justo.I*. Dizem, poróm, quc o sr.presidente du Republica semprese mostrou adverso ú caixa dcconversão...lt. E' exuclo c jior si^nul queconfessava não a haver suffic-icn-temente estudado. Seja porém,como lór, s. exa. linhn o diroitode pensar do um certo modo odo o declarar. O sr. conselheiroAfionso Pennn pensava c penso,porém, do modo diverso o o tor-nou publico. As duas opiniõesconcedamos quc so eptivaltom.Qual o segtiimenlo lógico? Eramantorem-so ambos om naturalreserva c deixarem quc si- pronun-ciasse o Congresso alim cie lheacatarem a resolução. Tal não sedou e não cessou o sr. presidenteda Republica de tornar publicoque vetnria a lei 1VT Diz-se, porém, quc o sr. pre-sidente da llepublica offlrmàra po-der conter o cambio sem o caixade conversão"B. E' verdade, mas si assim è.porque motivo declara boje quenão pode impedir a octua! eleva-ção do cambio, quando, com razãosc queixa a lavoura pelos prejtii-zot intoleráveis resultantes de sc-mediante elevação. Poucas letras *,, .: ¦ i.. no mercado e ¦ pelabaixa, naturalmente, que se inter-essam cs respectivos ; ..*>-*.. ! on -.A" intervenção proposital do Bancoda llepublica se deve, pois, exclu-sivamenia a alta e desaslrosa taxade cambio vigente.Si. conforme declarou antes dareunião d: Taubaté, icconhecia osr. presidente da Rcpubli us in-convenientes de subida áa camboe me sentia app&ielhado para evi-t%l-a. porque motivo procede «go-ra de modo contrario. aggTavan-do a «tuaçio des produetores?Não eslá abi a justificação ntkcomp Ma e irrecusável da necesti-«lade da caixa de conversão ?
P. E a lei quo croo ossn coixado conversão, sorá ella udopiada?B. Som duvida, com absoltilusegurança. Beconhoco-lho o Con-grosso ii nccciisiiliido o a approva-rá com grundo maioria,O qno cumpro á Iavourn, omquanto não vigorar osso loi, ó on-viar pouco enfò uo mercado alimde não fornocor loiiho para o cam-hio do governo, lão deeapicdndo oniiuoso. Convém nintlii limitar ossuquos u descoberto, uílm do nãocolloodr ei commorcio nm situaçãodiíllcil, intolerável, Süo poucosmozes, npcnnii, do sacrifícios : nãose recuso ninguém n suppnrtnl-os :nfio oo Iara demorar o rcoompon-sn».lüiíu lfoi-naril'»Aehn-RO ligeirniiioiito enfermo osr. Alvuro Rumos, auxiliar de ro-dacção da Gaiola tle São Ber-nanlo.—Bcolizoii-so no dia I í* o con-soroio do sr. Frniioistíò Fòrnozórocom a exmn. ¦ senhorita InositnIsolu, (Ilha do abastado industrialsr. Halo Isolo, rosidonlo nn cn-pilai.² Fnllecott n gulnnlo Iznbol, (1-I li i ii li fi tio sr. capitão SolodinoCardoso Franco—A 11 do vigente, partiu puraa Europa o sr. Soares Fernandes,gerente da fabrica do lecidos Ypi-rnnguiiilm, de propriedade da lir-mn Silvu Sou bra tí Comp.—Acha-se ligeiramente enfermoo sr. Alfredo Finquei', intendentemunicipal deste município.ItOllIC.IllilVindos do S. Paulo, estão nn ci^dnde o sr. Anlonio Gonçalves Pu-checo o sua exma. osposa, quovém novamente residir em suapropriedade agricola.² Boje terão logor us lesiivido-des religiosos de S. Vicento doPuulo.² Esteve limito concorrida umissn rezado quinta-feira om in-tonçãodaalma do finudo sr. Fron-cisco Freire Villas Hoas.—Em regosijo pelo regresso doslilhos do sr. Henrique. Giesselor—Eduardo e Paulu, quo ha tintiosestavam no Rio Grando do Sul,um griqio dc amigos seus promo-vou uma mniiüesla.f.o.Na noite cie quarto feira surpre-enderam o sr. uiossolcr com tiiiinbunda de musica c muilos togue-tos.² Itinlizou honlem om Pyrnm-boiu o enlace malrimoninl cio sr.Joaquim Coelho Pereira, dignoprolessor, com u ciilecln filhn dosr. Antônio I.luyiio, ulli residente.² Estiveram nn cidade, os cxmos.srs. dr. Josó Pedro de Cnslro. juizdo direito do Agudos, c coronelUolphino do Oliveira Machado,abastado fnzendeiro naquelle. mu-nicipio.
COniUCSPONIlF.NCIASllnlibnDo coiTesjiondcnte*, em 20:.Depois de longos c nlrozcs sof-(rimemos cjue o torturavam desdeha muilos dias, acabou dc fallecernesta cidade, nu munhã clc 16 dos-lo, o dr. João dos Suntos Rangel,conceituado clinico.O íallccido cra bahiano e lixararesidência nestu ha vinte o tantosunnos, conseguindo captar a sym-patbla da população, que muilo ocor idei-uvn.ra um medico distinclo, ao qua'muito devo a pobreza clItntiba,principalmente' n Santa Gusa deMisericórdia quc sempre, dosde usun fundação, recebeu grutuituineii-to os setís serviços médicos.Pesamos ii suo oxma. familia.— Achn-so entro nós u Coinpa-nino Dramática Couto-Cnndelnrin.tondo já dodo um espectaculo do-mingo ultimo. A troupe è nume-rosn o distineta e ojititiins os |ic-ças theutrues quo pretende levur.áscenn.A pojiulnçüo dc Itatiba, ondo ra
```
