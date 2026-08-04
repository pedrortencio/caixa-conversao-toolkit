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

**janela_id:** `per090972_1909_16496:p002:c26892-33091`
**jornal:** correio_paulistano   **ano:** 1909

```
 inaugural do Congresso Bra-sileiro do Estudantes.Não podendo ausentar-mo nctualinenle
Sua exa. fez um longo histórico da suaivida politica, declarando que so desliga-ra do seu jiartido por sor irroductivolnion-to favorável á candidatura do marechalHermes da Fonseca.O sr. Palmeira Rijiper aparteou entãoo orndor, dizendo que na prirnoira reunião |da bancada ^paulista esso sou collega sedeclarara contrario á escolha do marechalpara succòssor do presidente da Ropublicano futuro qualriennio, accoitando qualqueroutro candidate o aponas fazondo questãode quo este fosso apresontado immediata-mente.As galerias proromperam em applausoscalorosos ao sr. Palmeira Ripper, trocando-se no recinto vehonienles apartes que des-nortearam o sr. Jesuino Cardoso, fazendo-operder a calma.O candidate a doputado sr. Nicanor doNnscimento, derrotado nas ultimas eloi-ções, que se aeli.ivn no recinto, foz tignnlós galerias para quo estas intorviessom(.¦outra o sr. Palmeira Ripper.Esso faclo foi denunciado a vários depu-lados, que, verificando a procedência daitit'ormaçã()/'l>i'ote.stariitii coilteji a littitu-do do sr. Nicanor.Nessa ocensião, um grupo do cerca dcocir. desordeiros, muito conhecidos pelas
doso.Os deputados do ambos os lados protes-taram contra a intervenção dos assisten-tes nos debates.Estabeleceu-se grande desordem nas ga-leriaa," sendo siisjMüisn a sessão.Restabelecida a calma, foi reaberta asessão, não havendo, porém, numoro paraas voteções das mnterins da ordem do dia.Foram encerradas as discussões dosprojectos:reorganizando n Bibliotheca do Exor-cite;autorizando o sr. presidento da Ropu-blica n abrir ao ministério da Guorra ocredito especial de 5:000$000 para oocor-rer ao pagamento do uma gratificação doegual importanoia ao professor do Collo-gio Militar, Tliemistoelcs Nogueira Savio,como premio pola sua obra nCurso Elomon-tar do Googrophia»;autorizando o sr. presidente da Repu-blica a aposentar no logar do insjiectorda alfândega do Estado da Parahyba doNorto, com o ordenado correspondente aotempo de serviço publico quo fôr liquida-do, o segundo escripturario da alfândegado Manaus, Júlio Maximiano da Silva(com parecer tia çoininiséão do Finanças.Em seguida foi levantada a sesBao.Nas vizinhanças do edifício du câmaracontinuou a desordem iniciada nas ga-lorias, sondo cffectuada a prisão do- váriosindivíduos.LOTERIAS NACIONAÉS — EXONERA-ÇAO DO FISCAL DO GOVERNOConsta nas rodas politicus desta capi-tal quo o sr. ministro da Fazenda tencio-na exonerar o major Francisco do Asbísd. cargo do fiscal do governo federal jun-to á Companhia das Loterias Nacionaés.MEETING ANTI-HERMISTAOs operários doj subúrbios desta capitalpromovem um grando ((meeting» contra acandidatura do marechal Hermes da Fon-seca á presidência da Ropublica.0 comicio está annuiiciado para ama-nhã.CONGRESSO MEDICO LATINO-AME-RICANOAs republicas do Máxièo e S. Salvadorsorão represenUd-w no Quarto CongrossoMedico Lotino-Amerieano, a reunir-seproxiniamonto nesta capital, polo dr. Ja-cintho do Barros.CAIXA DE CONVERSÃO — EXONERA-COES NEGADAS0 dr. Leopoldo Bulhões, ministro daFazenda, nègou-EÒ a oonceder us demissõessolicitadas jielos drs. Henriquo Diniz o Re-bello Horta, diroctor e thesoureiro daCaixa do Conversão.DR. AFFONSO "PKNNA — EXÉQUIASEM NIGT1TEROYNa Cntliodral tio Nietheroy foram heiecelebradas sólonnes exéquias em súffragióda alma do saudoso presidente da Repvblica, dr. Affonso Ponna.Officiou o bispo daquella diocese revmo.d. Aitostinlui Benassi.
hojo om goso do licença, quo lho foi con¦edida polo Congresso estadual.Ao deixar o governo, s. oxa. passou °exercicio de seu cargo ao sou substitutot!0 dr. Rodrigues Doria embarcou nesteporto com destino á Bahia, a bordo tiopaquoto nacional «Guorany».Compareceram no embarque do B. exa.a-, altas autoridades, senadores, deputados,desembargadores, funecionarios, pessoaBgradas o muitos amigos,Mircas-SeraesEXÉQUIAS DO DR. AFFONSO PENNABELLO HORIZONTE — Telegraphamdn cidado do Pará quo a commissão pro-motora das impon:ntes exéquias quo serãocelebradas na matriz daquella cidado, nodia 13 do corrento, cm suffragio do almado dr Affonso Ponna, saudoso chefe dnNação, emprega os maiores esforços paraquo as solennidades so revistam do maiorbrilhantismo o realce; . . .Essa commissão adquiriu um riquíssimolivro forrado do velludo negro, com in-seripções om letras do ouro, o qual seráposto á disposição dos assistentes paranello lançarem us suas assignaturas.As senhoras daquolla cidado offcrocc-ram uma bella coroa para ser oollocoda nocatafalco.MOVIMENTO POPULAR CONTRA ACANDIDATURA HERMESBELLO HORIZONTE — Estão chogan-do à osto capital muitos doputados quovêm tomar parte nos trabalhos do Congresbo Estadual. ,Já se acham em Bello Horizonte os doputados coronel Soares Cruz, do Montes Ciaros, o Agostinho Pereira, de Mar do Hespunha, ambos propugnadores onthusiast.isdas reivindicações da soberania do povo naquestão dns candidaturas.  A câmara municipal do Seto Lagoasmandará como delegado á Grando Conven-ção do Agosto o seu presidonto, dr. Avcl-lar, quo foi doputado á Constituinte o ex-senador estadual.0 municipio do Sete Lagoas apoia unam-memento a attitudo daquollo volbo pro-pagandista da Ropublica.² Tom causado suecesso o discurso re-centomente proferido pelo sr. Aurélio Pi-res, cunhado do dr. Francisco Sá, ministrodá Viação, contra a candidatura do ma-roehal Hornios da Fonseca.² Sorá amanhã organizado um forte «co-mito» do commorcio do Bollo Horizontepara combater a candidatura Hormos.Sorá aberta uma grando subsoripção ontro os commorciantcs, com o fiyi do insti-tuir-se uma caixa para fazor foco ás dos-posas dé propaganda contra essa cândida-tura.   ...A' fronte do movimento esta o cajntaliBta Manuel Gonçalves do Sousa Moreira,[.residente da Junta'Commercial do Minaso político do prestigio em varias zonas doEstado.Todo o commorcio da capital porfia cmconcorrer para essa lueta pola salvação dapátria, derrotando a candidatura militar,verdadeiro uagello imminorite.Mais uma vez o commercio mineiro le-vnntará os brios do povo, salvando a digni-dndo do Minas o nchincalhando todos osquo não sabem quo o dr. João Pinheironão foi um político o sim um apóstolo quodeixou prosol.ytos, os quaes hão do provarao paiz q
```
