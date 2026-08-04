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

**janela_id:** `per103730_1910_00120:p001:c36659-43149`
**jornal:** gazeta_noticias   **ano:** 1910

```
o !iiicrBaelo«a»i — Crandiasat.titãs.mvKRsasS. J«a«t* — .Nova 'trouja^".Clrct» Si»lae>Ul — "O Pinta Men^fi"lavrada.
nm*t!a*-rt da produe«;ão nacional doque «1 .elevação da mesma taxa. Estaestabilíd-ade ê que so deve, an-tes do mais, procurar manter.Recorda que o Pr. >íüo Pcçanbafigurava na lista dos pa-ntidarins datnx.-( do 12 ã. A favor da elevaçãoda taxa ainda náo foi ouvida uma sóvoz partida das classseg productoras,as qu.ies. 00 contrario, estão apavo-raesis com a ameaça, da elcvacJto.Tudo estÃ,Indicando que nuLo se de-ve tomar medidas de afogadilho,não atten.der.do a graylssimaa re-elamações. Se a taxa t*or mudada, oprejnizo.da praça pauiista, como dedifferentes outras praças, será cnor-me. Dirá mesmo que tal mudançavalerá -para 3. Paulo como um ver-dadeiro terremoto.1 Terinina apresentando projectosubstitutivo ao do Sr. BarbosaTá ma :"O Congresso Nacional decreta :Art. Io. Fica elevado ao máximo-e 40 milhões esterlinos o valor dasèmlss<"5es dc nue trata.o art. 3** dale! 1.575, de 6 de dezembro de1900. que creou a Caixa de Con-versão.Art. 2"\ Os fundos especiaes pararesgate e garantia do papel nvoedaem cireulaçáo serão regulados ex-clusivamente pela lei 581, de 20de julho de 1S99, revogados os arts.9 e 10 dã 161 citada n. 1.575, de 6de dezembro de 1906.-Art. 3*. Revogam-se as dísposi-ções em contrario."Posto em discussão este substitu-tivo. é. dada a. palavra ao Sr. PaulaRamos.S. Ex. diz qne, segundo infomia-ções aue foram dadas quasi offi-cialm/sníe a. commissão. 30 milhO-sesterlinos estão promptos a entrarpara a Carxa em breve prazo. Se talaco^itoeer, que se fará ?—Neste caio se elevará o máximodos depósitos a 60 milhões, diz o Sr.Carvaihal.—Então V. Ex. ê inimigo da ele-vaçáo da taxa ca.mbral, sejam quaesforem os prejuízos do consumidor,portador de notas inconv-ersivefas,pois que o valor acquisitivo dasmesmas ficará, sempre muito baixo.Replica o Sr. Carvaihal que taesportadores terão as vantagens ladi-rectas, advindas do progresso dopaiz.O Sr. Barbosa Lima pergunta sea Caixa reformada como a cruer oSr. Galeão Carvaihal, permittlra avalorisação. 5>enaa qu« nuntía, poisos depósitos serão sempre augmen-tados á proporção true forem sen-do completados. Assim nunca aefará. a valorisação do nosso meioeircularit-e; no emtamto, o St. Da-vid Campista promett«eu que a taxaseria «levada 1* 1*3 -d. E* o que ag>ona acontece, mas nâo se quer elevara taxa. " _ -----
O Sr. O"; no inato Brujín diz qae íoiinimlfro d.i Caixa, mas lealm-rn-te.confessa qae ella pr«t«u>u e «síitãprestando sérios serviços. -\o paiai.KUa acabou com as OBc-Hlações que-tanto mal faziam ao commercio,dando iogar a tremenibu*! esi>ccula-ções. Os eapi1a.es estran-?eiros üfflui-ram e aqui estilo, confiados ita «navtabilidade da taxa.Tudo úndica, pois, que se <l«rve>adoptar a.s medidas contidas neprojecto substitutivo <10 Sr. Ciu-va-lha!, qae será salutar á .-rir,*, ae-tual.A um aparte do St*. "Barbosa Ta*ma, diz o Sr. Carvaihal que a rerti-rada dos fundos de f.irintia ,. re.s-*<a.te da Caixa de Conversão nenhuntimal fará á taxa cambial, que e-on-tuinará a .-*-?! sustentada eom os ea-pitaes de que atrora diepõe a lilixa.IDc-pois de alirum debate, o Sr.Homero Haptista propOe u;n iiddi-tivo ao projecto do Sr. Barbosa.Cima, apresentado na anterior rounião da comantssSo.A favor deste addüiv-o votaram osfirs. Francisco Vei-ía. (-presitten-te),Paula Ilii-iios*, Barbosa Cima., Bue.-no de Pa-iva, Sermo Saboya e líloyde Souza e eonttra iqiemu.11 Sr. «;.,leã0 Carvaihal.l-Y este 11 additlvo r"Accreaeente-80 :Art. Kiea elevada a 10 ã. a.taxa cambial a que se refere oart. Io da lei 1.575, rte.C de dezem-loo do 190*5, mantido o limite eon-stanto do art. 3*- e executado o dis-posto no art. 4" da mesma lei, «i-uan-to ao troco do.-» bilhetes ..-niàttidos a-15 d."O projecto tio íir. Barbosa lAon.a que se refere o addttivo, í o s/;-iruint* :"O Crpgressa Nu<*ioiia] decreta :Art. 1*. Ficam restaurados, no»termos das dfcrposiçíSes le-çíslatlva»que os instituíram, 0:5 fundos do ga-rantla e de resgate do papel-niocda,creados pela lei n. &31, de 20 dojulho de 1899.   .Ar?. 2*. Ficam revogados os artt-gos 9 e 10 -1.1 !eí n. 1.575, de 0 dedezembro de 1906, bem como todasas disposições em. contrario do ar-tigro 1" dá presente lei.*'\pp?:r.rA)s a* oa.mauiA' Gamara dos Deputados, to; .rígido de S, Paulo um telegrammaem que a Sociedade Paulista dc*Agricultura, Commercio c Industria,om nome das classes laboriosas dcEstado, appella para o patriotismoda Câmara, afim de impedir a mo-dificação da actual taxa do cam-bio, que, diz o telegramma, tã«Jgrandes benefícios tem trazido aapaiz. a mesma sociedade consideraa elevação da taxa um verdadeirodesastre, de funestas conseqüência»para a agricultura, commercio o 'n-duKtrla.Nr, mesmo sentido envifirarn tanubem telegramrn-is á Câmara a dlr<yctorta do Centro Agrícola do SScPaulo e a Câmara Municipal deMonte Alto, no mesmo Estado.ÜMA BECNiAO 1MPOKTA.NTKBea'.isou-se hontem, no ministe*rio da fazenda, a annunelada con-ferencia entre~õ Sr. ministro da fa-zenda e os directores de bftncos, ao-bre a Caixa de Conversão.Tomaram parte nessa eonfereoi-cia, que foi de cerca de d-uas horas,os díreotores do Ri ver Plate Bank,BrazIUanisch Bank fur Deutsch-land e o Dr. Ndrberto Ferreira, dl-reetor eanubial do Banco do Brasile o deputado Pandiá Calogeras.Versou essa conferência, sobre aelevação da taxa cambial de 15 pa-ra 1G d., tendo os díreotores do»bancos estrangeiros lembrado ao-Sr. ministro da fazenda o alvttre -taIncineraçáo de 20.000:000$ em no»tas conversíveis, para evitar os pr«e«»íulzos decorrentes da elevaajato ?sustentação do catrrrblo a. It.O Sr. ministro da fazenda ae<5«*a—tou «*Hs#e alvitife, apenas como -¦*elemento paraíeâtndo da questão.Ajrites de se reüra.-em., oa 6r«».Seamens e Outsehow. dIreetore« do»RI ver Plait* e do BrazllianLsch Ban"«fur Deujtschland pediram a atteny»ção do Sr. ministro da fazenda pa*ra que não sejam compromettldo»oa interesses da nossa praç-a com.a brusca elevação da taxa cambialNOVAS EXTRAD.XSSerão recolhidos proximameate XCaixa de Conversão pelo Bajico da»Brasil 9.000 000 de francos e peloLonilün and Brazilian Bank £ 55.009a chegarem proxlmamem-c*.O movimento de entradas de ourofoi hontem de 5.174.-S9OJS0O e o dax«ahidas importou em **l,6,:Q94'í-673.elevando-se a exístOne^ao-buro eu>eofre a 2tí.0t5:02*»tí6|f?
...
iWmW!^^^^^^^^^1^;. . «. 
  A _, '  . , 2zlj^L~í B ___^ *—^.— ¦__.... A LJl - ^ .:/¦-¦ ¦."-.: ..-,.-1 *¦¦¦*-¦:¦ .-i... .L ¦-.'.--..--¦,¦:.: *r*T' "f"*- - -'.-.A.
```
