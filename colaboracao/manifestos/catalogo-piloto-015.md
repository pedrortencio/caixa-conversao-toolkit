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

**janela_id:** `per090972_1906_15474:p002:c34907-42303`
**jornal:** correio_paulistano   **ano:** 1906

```
pncinl quo tlol*xou a estação á mela noite.O sr. dr. Washinglon Luis,om companhia do deputado Bar'ros Penteado o de sua comiliva,parle para ahi polo nocturnoquo passa om Lorena ás 3 omeia horas da madrugada.RIO OE JANEIROSenadofo cxpedionlo foi lida a pro'posição da Câmara dos Deputndos concedondo á viuva dcJosó do Patrocínio a pensão deduzentos o clncoenta mil reismensaes.Como nom um dos srs. sono'dores quizesso usar da palavra,passou-se ú ordem do dia, sendoencerradas, sem debato :n 8.* dif cussão da proposição daCâmara dos Deputados, auetori'zando o sr. presidente do Rc'publica a abrir ao Ministérioda Industria, Viação c ObrasPublicas o credito de 12;000$,supplcmonlnr ú verba 9.a do or'comento vigente, porá pagamen'lo do augmeuto de pessoal deque trata o decrelo n. 1-451, dn29 de dezembro de 1905, comparecer favorável;a segunda da proposição damesma Câmara, auetorizando ogovorno a conceder ao capitãode artilharia João Lopes do Oli'veira Lyrio um anno de licença,com soldo e etapa, para trotardo sua saúde fora do territórioda Republica, com parecer fa'vorovol-Não houvo numero para pro'ceder-se ás volaçOos constantesda ordem do dia.CâmaraApôs a loitura da acla dasessão anterior, os ars. AffonsoCosta, Wenccslau Escobnr, Pau'lo Ramos o Pedro Moocyr de'clororam quo, si estlvossem pre'sentes, honlem, votariam con'tra o projeclo da Caixa de Con"vorsõo.O sr. Germano Hasslooherpediu que ílcasso consignadona acta quo, si houvesso com.parecido hontem á sessão, teriavotado a favor daquelle proje"cio.O sr- Bueno do. Paiva mandouá mesa um requerimento dodr. Sezino Valle, juiz seccionalem Minas Geraes, pedindo umalicença.Depois occupou a Iribuna osr. Francisco Botelho, que diri'giu um appello ao sr. ministrodn Industrio, Viação e ObrasPublicas no sentido do ser íei'ta n reducçõo do tarifas na Es'troda de Ferro Central.Sobre o requerimento de in'formações, apresentado hontempote sr. Figueiredo Rocha, falouo sr. Alencar Guimorães.A discussão foi adiada, ficandocom a palavra, para respondei'na segunda-feira, o nuclor dorequerimento.Eiitrando-se ua ordem do diae não havendo numero poro nsvotações, ficaram encerradas asprimeiras discussões dos pro'jectos :Mandando pôr d disposiçãodos govornos dos Estados dcMinas Geraes, Bahia, Pernom"buco, Alogons o Sergipe a quan*tia do 2.500:000$ pnra soecorreras localidades flagellados peloullima inundação do rio SãoF'rancisco i com votos em sopa'rado dos srs. Scrzedello Corroae David Campisla jeslabclccoiido penas para ocrime dc peculato o dando ou'Iras providoncins com voto emseparado do dr- Germano Ilass"locher.Foi cm seguida annunciadaa discussão única do parecersobre a emenda offerocldo nnterceira discussão do projectoque fixa os vencimentos dosconferontes das capataziás daAlfândega do Rio de Janeiro.Falaram os srs- João Neiva,defendendo a sua emenda cmfavor do pessoal das capataziásda Bahia, a Paula Ramos, com*balcndo-a.A discussão ficou encerrado.—A Commissão de Finanças,reunida hoje, assignou a reda'cção do projecto da Caixa dcConversão, do accôrdo com asemendas approvadas, para sersubmcltido a terceira discussão.—O sr- Jiistiiiiono Serpa apre'sentará brevemente á Câmaraum projecto dc organização dojury.O mesmo deputado, na pro'xima reunião da Commissão deJustiça, lerá o seu parecer favo*ravel ao projecto do sr. Figuei*redo Rocha, equiparando ashoras de trabalho c os venci*mentes dos operários das olfi"cinas da União.Caixa de ConversãoCom extraordinário esforço,consegui saber que o deputadosr. Alcindo Guanabara apresentarã as seguintes emendas.na ler"ceira discussão do projecto quecrêa a Caixa de Conversão :Accresccnle-se: (antes r"!o ar.ligo primeiro):
motiólarlo, oronilo peln loi do11 do setembro de lHid, flcnKiibHlItuhlii pelo do 9$()U0 polaoitavo do 22 quilates, oqttlvo'tentos no cambio do 12 diiibol-ros esterlinos por 1$000.Artigo segundo—Toda a aclualomissão flducinrla «ord couvof'tida om moeda nacional ouro,a obIo cambio.Artigo tòrcõird—'Sorá crendoumn Caixa do Conversão pnroesso fim, sondo n mesmo ridmi'nislrodn por umn diroctorio docinco membros, nomeados pologoverno com approvoção do So'nado.Artigo quarto—Os roeu caosdestinados .por leis vigentes con'slitulrõo os fundos do garantiapara o resgato do papel rnoodn,o o soldo actuoi desses fundospassarão a constituir o fundodc conversão cm ouro, sob aguardo da Caixa do Conversão.Artigo quinto—Na proporçãodos recursos desses fundos, aCaixa de Conversão substituirágradualmente os bilhetes daemissão inconversivel por bi'lhotes representativos do valoreguai no dn moeda ouro quolivor em deposito o nelin con"vorlivois, cornpulíindo-.so essovalor na fôrma do disposto *fartigo primeiro, paragroplio pri»meiro desta loi.Os bilhetes inconvertivois rc'tirados da circulação, serão In"cincrados.Arliga soxlo.— Como o artigoprimeiro do projecto.Supprimam-.sc os artigos ler*ceiríi e quarto do projeclo.Artigo sepllmo.—Como o cjúih"to do projeclo.Arligo ollavo.—Como o sextodo projecto.Artigo r.otto. — Como o sep*ti mo.Arligo décimo. —Como o oflavo.Arligo uiidocimo.—O governoentrará em occôrdo com oBan'co do Brasil para o ílm do mo'diílcar a aclual carteira do cam'bio nesta base.a J—ficará subordinada dirce'lamente ao ràinlslro da Fa'zonda   \b)—terú um dircclor do livrenomeação do governo;c )—cffcctuard a compra c ven'da do letras para o exterior,manloudo a fixidezda taxa cam"bial, estabelecida no arligo pri"meiro desla loi ;d)—terá um fundo dc ummilhão esterlino, retirado dofundo de conversão.No caso do impossibilidade deaccôrdo com Banco, o governoorganizará diroclamciito no Tho*souro uma secção do câmbios.Arligo duodecimo. — Como ,oarligo nono do projecto.Outra emenda quo o sr, Al"cindo Guanabara apresentará.Arligo primeiro— E' o gover'no auetorizado o conceder au-ctorização pura a creaçõo deum Banco Central Hypothòearloo Agrícola, sob ns seguintescondições;a) com um capilal inicial nãointerior r. 1.500-000 libras oslor'Unos;b) com sedo ho Rio do Janeiro e succursal ou delegaçãona praça extrangoira ondo fórlevantado o capital, ou ondo oconcessionário preferir :c) corresponder-so-d com osbancos agrícolas o hypolheca"rios das capitães dos Estados;d) sorá o único Intermedia'rio para lançar na Europa Io'Iras ou obrigações liypotlicca'rias, emillidas pelos inslilulosbrasileiros.e) limitar as operações doempréstimos hypolhccarlos ur'banos e ruraes c os emprosti'mos e pensões agrícolas, feitosdlrocUSmenlo aos lavradores oucomo intermediário dos bancosou syndicatos agrícolas legaliza*dos no Brasil.f) — Os membros, direcionado conselho fiscal o o gerentepoderão ser brasileiros ou ox-trangelros, mas ficarão no Ilio,no mínimo Ires diroclorcs oIres conselhciros-flscaes ;rj) — A duração do banco serádo sessenta annos;h)— Picam Isentos dc selloe dos demais impostos as acções,letras liypolliecorias o dividendodo banco;i) — Os estatutos serão appro'vados pelo governo o nno serãomodificados, sem o seu consen*timcnlo.Em viagem de instrucçãoPor toda a semana próxima,sahiiá deste porto, cm viagemde instrucção, o cruzador Pri'meiro de Março.O «Gustavo SampaU»Um telegramma recebido polosr- vice-almirante Julio do No'rouba, miuislroda Marinha, iu'formo que o ença-torpedeira Gus'taro Sam/mio deixou hoje eporlo da B.ibia com destino aodo Rio, devendo tocar em Vi*ctoria para receber carvão-Para CaxambúEm companhia do sua exma.lamilia segue para Caxambú osr. general Sousa Aguiar.Sua permanência alli será d«um mez.Co
```
