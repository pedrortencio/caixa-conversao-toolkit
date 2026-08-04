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

**janela_id:** `per089842_1910_03211:p002:c0-7390`
**jornal:** correio_manha   **ano:** 1910

```
: , - "¦¦ [ ..
.sjSfi-Sglg»*
ÜÒRltEfÒ SÁ MANHÃr'— Terça-feira, 3 de Maio de iWO f^PPPgS«t*g
dueto do Estado de S. Paulo, a realizar-seno periodo de cinco mezes, como suecedeucom a saíra actual, em vez de se dividir pelomino inteiro, o que obsta a que os produeto-Rs possam reagir contra conluios da espe-cuhção no gênero, produzindo ao mesmotempo superabiindancia de. cambiaes cm unsmeze-s ç escassez em outros, não ha meio defixar, por modo directo, si o actual stockdo precioso metal é excessivo, ou niio, parao desenvolvimento das condições cconomi-cas do pai;: c seu progresso.Resulta do facto aue os adversários daCaixa dc Conversão suí-tentam que a conti-niiação das emissões da Caixa á taxa actualrepresenta, nada menos, nada mais do queum obstáculo insuperável á prosperida-de do Brasil, em proveito apenas dosproduetores, desvalorizando o meio cir-culante inconvcrsivel ! Que, por isso mes-mo, sc toma urgente mudar o padrão dasemissões da Caixa dc Conversão.Os defensores da instituição sustentamopinião diametralmente opposta, apontandop.ira a Argentina, que se acha cm plenaprosperidade, com um stock de ouro de maisdo duplo do limite máximo da Caixa deConversão brasileira, com um territóriomuito menor e uma população corrcspon-dente a um terço da brasileira.O slock do ouro actnal na nossa Caixade Conversão é, na opinião destes, inferiorao de que necessita o Brasil..Mas, si não ha meio directo de aprecia-ção, lia, todavia, um indireclo.;Com effeito, não c só nos paizes em quenão ha circulação metalliea que pódc haverMelhora do ouro. Nos de circulação regu-lar e normal, o balanço econômico pôde dar,c dá, lotfar a graude acetuniilação do stockdc ouro. A isso deve a França o ter-se tor-nado o banqueiro do mundo, tendo já ido,pnr mais dc uma vez, em soecorro da pro-pria ínglatorra e dos Estados Unidos, quelém o mais importante stock mctallico domundo. Por isso o juro é mais barato emFrança do que cm qualquer outro paiz.Nos palzes onde sc dá a plethora dc ouro,manifestam-se dois phenomenos que nãooceorrem no llrasil: Io, a taxa do juro sof-fre notável diminuição; 2", o capital exce-dente As necessidades'do movimento eco-nomico vae procurar collocação mais ren-'dosa no estrangeiro, ou sc emprega nos ti-liilos da divida externa do próprio paiz.l) primeiro desses dois phenomenos jà schecentuou na Argentina, onde a taxa dojuro regula por 5 o|o, 110 niinimo, c 7 o|o,110 máximo.Si a abundância dc capital, na própria Ar-genlina, ainda não convida a empregar cmdivida externa do próprio paiz, pela sua altacotação tia Europa, o estabelecimento denina filial do liauco Hespanhol do Rio da1'rata, uo-Brasil, onde a taxa do juro éllittilO mais elevada, do que na Argentina,é prova inconcussa dc que o capital queéxisICaiiii vizinha republica, nacional c es-Irangeiro, é já mais que suffiçicntc para osrn movimento normal interno.Com o estabelecimento da Caixa de Con-Versão lio lira*il, o juro ainda sc coiisctvaalio (a 8 o[o nn niinimo, mais do que omáximo ria Argentina'); havendo, apenas,por emquanto, maior facilidade 110 credito,conio o demonstram os balancetes bancáriosnacionaes e estrangeiros, Claro esta que nosreferimos a credito propriamente commer-ciai, c não a descontos, como 03 que alidha-r.un as carteiras dc alguns bancos, 110 tem-po (lo cncillinhicnlo, pois qne esses repre-tentavam somente agiotagem dc bolsa, quetrouxe a queda dos estabelecimentos bati-trios, que animaram a jogatina com papel111 valor — o qn'.' í bom accentuar, para,11' nãn haja confusões entre operações decommercio e de especulação, ou antes, ágio--i*H"*m bolsista, propriamente dita.Não tendo baixado o juro a taxas quepermitiam n ropnlrinçilo da divida publicanacional un estrangeiro ilm vendo largo cam-po pa-.i explorar cm lodni os ramos da acti-viil-ulo e da rique/a material do paiz, claron.á que ri actinl stock liUtalÜCO, concen-Irado na Caixa dc Convcfiíô, não dcsvalo-ri/a o meio circulante inconvcrsivel, c lan-ln i»»io !» cxncto, que não falta empregop.ir.-i capital nò llrasil, e sim capitães paraemprego seguro c rendoso, como está -.de-in»iis.iramlo a constituição, no estrangeiro,dr empresas para diversas .explorações cçiíí-nimclaes, industriaes c agrícolas,Km arligo subsequente demonstraremosns cUnu lios de que se serviu a especulaçãopsra ac: limiar ouro ua Caixa de Conver-são.Tal cuido c tanto mais indispensável,111MI1I0 é certo que a lei que areou n Caixadr Conversão não dispõe imperativamenteUi',* será alterada a taxa da emissão, quan-duns depósitos em ouro tiftinjam a 20 mi-llt',". esterlinos. Apenas dispõe que PODKRA1<er -Itei-.ida. A falia dc obrigatoriedade daílltitlííteacíni do cambio da Caixa presuppSca p»i*siliilidiide dc ser conveniente cousrr-1:11 a taxa actual.ataSegundo o orçamento vigente, a? receitaseni ouro excedem, em cerca tle 48.000 0*11-|,vi, a despesa na mesma especie. Como oTHcsnuró revende aquelle excesso, obtém1» tco contos em |u|>ol para fazer face ádes|»i -a cm moeda .corrente, Para obter ,1rticsitm receita rrti papel, ao cambio de 16 d.,í necessário que os impostos cm ouro, emve* de (M-ulercm a despeja rui 48.000 con-tn». a excedam em ft-,000 contos, numerosredondos. Preparem-se o comihèrció Jm-n»"-t.ailnr p tnaU o consumidor para mais¦ '«enefício !
Um vulclo em actividadeIMA lORKIiNTK DU l_\VA despenhan-a íc pala' enviei d,t montanha, 14111! rio defogo! ijiuii crMera em franca erupç/lo, itrrom.-».findn par.1 o ,tr ninrni dr vapar,acomj>anha<laile pttK-aj cadentes; í r-r.e n eapectaculo queapresenta a aetittida parte tia erupçia tio Etna,ipn* » ri hoje exhtMtia mi Cltttma Ideal,
Ift OINIOSf.^ti; mi»:/, m-Oi-..VMi_Potlt-pola finíssimoL FJHEST Lata 1J1 OOMAspargosP. CA NAU D Lata 1*^600Mlàillp.-^ns ftiMilla |i.ir iiiilmiiiM <>in1'eiti defiut.i-.lo ll.irli.ta I.ima foi hontemaprrientai.lt» I Câmara a seguinte reiiucri-mento í"Rítjtteiro que * felicitem tio podor exe-cõtivti, a* sfíuíniei informaçõesl»' —* Uual -t importam,"» (Us despesas rea-li*,.(J_« emu a tLxpQstçfto Mactoual d.t praia\Vi_elb.l, tm n»v, e a CÍfcctuada duranteO tsf.so de 100S;í* — Qi!.il a importância arrecadada eo-norecria «lufactí a nse^nu expoíiç,lo, nrove-«icttV dc cMrad,n, etviintmiçix!! de Mitgu.1pa?t h»»!t!jitiii*, íiitentatORtapho* c outrotdtwrtimeKthWs * de qitactqirer outra* fontesde tanda evfrjordstidrk;x* — Qut.-* »> vrtha« ,1o orçamento. <»**er(«.ünark», ip>i*r «ttppíemer.tar. quor c\lr,»,->r*»|>n*uK a q«»í foratn imputadas ttqueitei *h.-petlí;*,' — Oi*».t a imp<*rt.\ní!a pajn a tiisdo demtifín^Jtüi, ^r ii>rtit«ârta>. t\aet e\i»_i»r-dit'»ridí. tm *»fi«l* d. iviw*! rvtetvatkx .uon|«m de ^tiahjtirr mtnresa. p»?r tt»«>tirodf**f» eapwíçjA a pe*?ot* que, a jt;írt» á-tps-semct. trilham jvv_5,to wrmjas **mH»5íp»r (ÍW ^»»»e»t rV** ehantadí» mu«en bd«tr_t| 5U«-rimw_r»{-.-- «e «-.«e* j_t-_a**>t*t!K>»i p.w tmtWlKhkMi e oM_.i-.ta úot «r--ÍÇíMtS5* — 0»»e «Je*«>KO tii-eram »« ^_ac»t!at sr.rv-italad»» e»}H!X> twet*a »ui»rÍB»«i pela »t--¦ v**'*-» «híriestí a .iwrsma expí-itÉçia,*. "Ií«** tmtwrwwt*» K*4 ikwí-íío mtueti tp*s*^-*»*í>> peb C-ir*-.t*-»k raa 1 «n*!-» h.r»*«ir*i <»*n tapararta* iftisv-ji^ ,> -v ># Il« ti-t^ue D-»it«uv t C napm. Ur-fruajrwa n.H»'tO«t» IV»-» lll.\HH(l<t.\T SBO-SEHlUi OE HAVANAOna HiaJa» * sur** xjika WM>(wldfíC_tO tnl(n-W 4* vtts**Mfa £» (Vain «k»^IWÍmet vr. AasStaf Warf-Ww-si ... &*»«*«s a :,_i.* Att tuaiii-W .V*rS4 C-t^í** t*-nrt «<«tv** *> »K**isw*l»»i*t éttum ttt_k 
```
