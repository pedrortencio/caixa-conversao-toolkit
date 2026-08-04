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

**janela_id:** `per103730_1914_00217:p005:c24347-30528`
**jornal:** gazeta_noticias   **ano:** 1914

```
rticular,devido ft falta de carvão para mau-ter as suas usinas.A cidado acha-so ameaçada deficar íis escuras, o eem transporte,por falta do combustível,O commercio desta praça encon-tra-so totalmente paralysado, r«l-nundo «pavorosa crise financeira.OPFIOIOSRELIGIOSOS "PRO-PACE"S. SALVADOR, 5 (A. A.) — Oarcebispo D. Jeronymo Thomé 8aSilva, determinou ao clero bahianoque uo final dns missas devera gerrezada a oração "pro-paco".
Repercurssão na
0 "Tomasso di Savoia" seguolevando reservistas de variasnao
BUENOS AIRES, -G (A.-A.) —o No Intuito de evitar as desagrada-veia «manifestaçãos publicas que setem repetido ultimamente contra asnações em guerra na Europa, pelosnaclonaes aqui residentes, a poüoiado Bosario prolilbiu quo fosse-mexhibldos nos cinomatographos osretratos dos soberanos das poten-elas em guerra.
ámeneaÂitcniM0 Club Francez, da Argentina,ampara as famílias dos queram para a guerraIiUBNOe AIRES, 6 (A. A.).—O Olub bYniicoz tomou a.«Mu <3tu*§oa manuta>noile «Us fumflla» frnuc»-Ma :ii*!.-^«l-iii!iin, cujos chefes «e-
BUENOS AIRES, 6 (A. A.).—Segue hojo, com destino aos portosda Itália, o paquete "Tomasso dlSavoia", levando a bordo grandenumero do resorvistas allemaes, In-glezes, francezes, nijssos, nustrla-cos, bolgas, eervlos, suiwos o nion-teuegrlnoe.
1 Argentina pr decretar amoratóriaBUENOS AtiRES, 5 (A. A.).—O governo prejecta deyotar a mo-ratorla vc/lo praso do trinta dias.
Um banquete de despedidas aoaviador francez PailleteBUENOS AIR.ES, C (A. A.).—Os aviadores argentinos offeroco-ram hoje, a noite, um banquete dodespedida ao aviador franeez Pail-leto, quo seguo para a França, afimdo ao Incorporar ao serviço deaviação nUlltar.
A"HaÉn"e as manifestaçõespopulares relativas á guerraBUENOS AffiRiES, G (A. A.).—O jornal "La Naclon", roferln-do-so as manifestações de sympa-thia reallsadns por estudantes opopulares, a favor de algumas dasnações européa.-1, actualmente oraguorna, aconsolha o maior respeitofis -conectividades estrangeiras, nãosô por bem entendido espirito deneutralidade, quo convém observar,como por dever de eortezla paracom os estrangeiros, hospedes daRepublica Argentina o para evitarIncidentes desagradáveis a quoessas manifestações poderiam darlogar.SÍAIS AVIADORES PARA AFRANÇA — UMA MEDIDA DAPOLICIA DE ROSÁRIO PARAEVITiUt.DISTURBIOSBUENOS AIRES, 6 (A. A) —O* aviadores- Caetalbut e Marisehalpartem para a Franca, no primeiropaquete que setrulr do porto destaoapltal, com aquellc «!¦-;'..!:«>. ; fimde tomar parta,» na «turra com *Allemanlia.
A GUERRA EUROPJDA OCOjV-SIONA O FRACASSO DA AR>BITRAGEJI FRANOO-ARGEN-TINaV ?«BUENOS AIRES. 5 (A, A.) — Oparlamento vai suspender a dia-cussão do «tratado do arbitragemIranco-argontlno, para melhor o.p-portunidude, om vista da guerra,em que se aclia empenhada a Fran-ça nesto «momento.A ORI8E FINANCEIRA — UMPRO.TEOTO DO GOVERNOBUENOS AIRES, 5 (A. A.) —O govorno da Republica apresentouao Congresso Nacional um projo-oto suspendendo a convoreão doouro, por papel, sogundo a lei quoogie a Caixa de Conversão, da Re-publica Argentina, ou sejam 4«ícentavos, ouro, por um peso, pa-pol; autorlsando a entrega, aoBanco de "La Naclon".. de 30 mt-Ihõee, ouro, doa depósitos da Caixade Conversão, para applicar 80 "l"em obrigaçõea naclonaes.No mesmo projecto o governo pe-do a decretação da moratória, portrinta dins.
tes nos Estados biiisileiros do eul,so tècha-m preparados para se«çulrpara a Al-lemanlia, sendo grando oenthusiasmo reinante emre todo».
URUGUAI
RESERVISTAS QUE PARTEM EA QUEM SAO FEITAS JFESTASASSUMPiÇÃO, E {A. A.) — Napróxima quinta-feira partem paraa Europa os primeiros reservistasfrancezes e allemaes aqui residon-tes.Hoje, ft noite, a Sociodado LaFranco offerocea-ã uma festa dedespodlda aos sócios o nos membrosda colônia que ee acham de par-tida.Amanhã., os «allemãos aqui resi-dentes se despedirão também, fes-tlvainente, dos seus -compatriotasfine -maroham nara a guerra.Peru
JE' GRAVE A SITUAÇÃO EMMONTEVID06OMONTEVIDÉO, 5 (A. A.)—A si-tuaçã-o 1? considerada grave, nestacapital. O grando numero de desoe-cupados e os medidas .postas omexecução pelo governo, em vistados «eonteclmentos europeus, dãologar a grandes apprehensBes, ha-vendo .receio de quo se venham adar conflictoa entre a policia e ojtrabalhadores desempregados, quepodem ser levados a commetterexcessos, por lhes faltarem nsmelou de aubslstonc'a, devido d fal-ta de traballio o á carestla da vida.O commercio recusa-se a aoeei-tar o papel-rnoeda para pagamen-to das suas tranaaeçBes, erigindomoeda meta!)'ca.O governo, como «medida do pre-caução, ordenou o nquartelaimentoda policia o do todas as forças daguarnlção.MANIFESTA-MO A' FRANOA —RESERVISTAS PKOMPTOS PA-R\ SEGUIRMONTEVIDE'0, 5 (A. A.) —O* estudantes desta capital flzo-ram hojo uma manifestação deapreço aos reservistas francezesiincíoii >li-.i<!«. ¦ o que so acham departida para a França.MONTEVIDE'0, 6 (A. A.) —Tsloi/raramaj*, oaul recobldoa t pra—.Jeden"*»* <lp Rio Grande do Bul,Informam que os allemS«*s rppiitn-
OaVIOIAES PERUANOS QUE PE-DEM LICENÇA PARj\ PARTIR.— OS RESERVISTASLIMA, G (A. A.) — Diverso^ of-flciaes do exercito peruano sollcl-¦tarnim do governo pennissão parase alistar nas fileiras do exercitofrancez.JS' enormo o enthusiasmo que seobsorva entro os colonos europeus,cujos .paizes de «wlgcm eo achamem guerra. Allemaes © francezesembarcam om todos 03 vapores quoeo destinam & Europa, cheios dejiatriotismo o coragem.Os Jornaes de hoje pedem maiscalma aos patriotas em viagem,lembrando—lhes o respeito devido B.dlvnldade doa sentimentos quo osanimam.Chile1.250 FKANCEZI.S QUE PARTEMSANTIAGO, G (A. A.) —A bor-do do vapor "Ilha Havre", parti-ram com destino ft Europa 1.250francezes.
1 Bélgica estásuas forças e chamando apostos as suas reservasOS VAPORES HOLLANDEZE8NAO CONDUZIRÃO RESER-VISTAS — DE BORDO DO-'ZICBLAND1A" SAO DESEM-HAHjCADOS AQUELLES QUE3A HAVIAM TO.MADO PASSA-GEMRecebemos a searuinto notifica-ção:"A le-pição &m Hollanda nesta,capital, na falta do instrucgSes arespeito «lo em governo, leseiyeu,00 intuKo de Doneerviur atricta^-,-,:-. n'.- o» princti-rlans de neutrnll-«Jaile, «Jaa-eml^u-cüT alo vapor''«?S)^»»*l*)i^,,  «w?lü*«* totUm tm
passagfiir.-s i>ertcncenles a qual-qu
```
