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

**janela_id:** `per090972_1914_18122:p002:c21193-27703`
**jornal:** correio_paulistano   **ano:** 1914

```
zo dos dacollectíviilade, lendo cm vista interesses dcpartido que devem ser collocados cm pia-n.j secundário.Vozes— Muito bem.
O sr. Cunha Pedrosa — Esta declaraçãohonra muilo o caracter rie v. exc,O sr. Pinheiro Machado — t\solni; si*,presidenie, organizou-se o Parlido Republi-cano Conservador, tendo Indiscutivelmentecomo elementos de ponderação e de ncção oauxilio e o concurso do chefe da nação, queuão vinha mais do que constatai* um fuclojá preexistente,Aindn liontem, sr. presidente, o nobre sc-nador pelo Ceará, o nosso digno e illustra-do collega sr. Francisco Sn, quando eu, mereferindo ao bloco, o qualificava dc ephc-mero, s. exe, affirmou: "Não; o partidoé a continuação do bloco." (Apoiados.) Naverdade, sr. presidente, o Partido Republi-cano Cousevudor tem, como seus principaeselementos dc vida, quasi todos os proecresque faziam parte do bloco.O sr. Urbano Santos — Os homens e asopiniões são os mesmos.O sr. Pinheiro Machado — Perdeu, é cer-to, a collaboração prestimosa e inestimáveldo notabilissimo sr. Ruy Barbosa, cuja nu-sencia do nosso ponto de vista politico já-mais deixamos de deplorar. {Muilo bem.)Perdemos, até certo ponto, a collaboraçãodo illustre senador por S. P.udo, o sr.Francisco Glycerio, que, entretanto, poroceasião da organização do Partido Repu-blicano Conservador, lendo o nosso pro-gramma, sinceramente declarou-me queaquelle era o seu programma.E vem a pello neste momento referir-mea um aparte com, que honrou-nv: o honradosenador pelo Rio dc Janciro,_ na oceasiãoem que eu falava da Caixa de' Conversão ealludia á organização do bloco, lendo umanoticia relativa a um almoço que se deraem nossa casa em que. s.: exc, distinguiu-do-mc com uma saudação, qiralifxou-me dechefe dos republicanos brasileiros. S. exc.em aparte que, naturalmente por não serbem apanhado, veiu modificado na publi-cação, porque não foi o qüe s. exc. dissenaquelle logar; s, exc. declarou que o blocofoi uma organização feita contra a inter-venção do presidente nos assumptos politi-cos da nação.0 sr. João Luiz Alves — Nii eleição doseu suecessor.O sr. Pinheiro Machado — V. exc. in-correu em lamentável equivoco. 0 bloco foiorganizado naquelle momento pelos ho-mens que estavam á frente das questõeseconômicas importantes, que interessavam anação.,O sr. Nilo Peçanha —.V. exc. eslá enga-nado. Peço a palavra. E' melhor do que es-tar dando apartes'.O sr. Pinheiro Machado — Eu estima-ria que v. exc. dósse apartes; seria um ser-viço a mim prestado. Tanto eu tenho ra-zão, sr. presidente, que quando se dou a or-gánizíção que importou na eleição do sr.Àftonso Penna', não fazia parte delia o sr..senador Glycerio e foi o sr. Glycerio quemme baptizou c^jin o titulo dc chefe do bió-co.O sr. Nilo Peçanha— Que prova isso?O sr. Pinheiro Machado — Isso provatudo. Si o sr. Glycerio não fazia parte dáorganização politica d'a--qual fez parte v.exc. como figura siiliéntissima...O sr. Nilo Peçanha — Mas v. exc. disse,aqui, que o si. Affonso Penha foi quemlançou a questão econômica da Caixa dcConversão junto de v. exc.O sr. Pinheiro Máçliifdò — O =r. Affon-so Penna foi- eleito pelos elementos republi-canos que sustentavam o principio da Caixade Conversão.0 sr. Nilo Peçanha — Pois si o bloco foiorganizado posteriormente...U sr. Pinheiro Machado — Como eutinha razão em desejar o.s apartes de meuillustre collega I Não ha nada como ex<;-minar essas questões face á face. li' esse0 melhor meio de pulverizar o erro e pes-car a verdade.O sr. senador Glycerio estava com , aquestão econômica da Caixa de Conversãoe d.i valorização do caíé;_ nós tínhamosdado a nossa solidariedade á solução desseproblema; s. exc. entendeu que era coiive-niente normalizar, disciplinar a acção; «:,por isso, invesliu-nie da direcção dessacampanha.Note bem o Senado que a saudação doillustre senador pelo ÜMndo- do Klo é di-versa da do senador pbr-S. Paulo. Q srNilo Peçanha saiiilou-me^eomo chefe dos re--publicanos brasileiros; posteriormente, le-vunlando a sua laça, o sr. Glycerio deu-me as insígnias dc chefe do Bloco ccono-mico; porque não havia mais questão po-litica...O si*. Urbano Santos — Preconizando anecessidade dos republicanos se constitui-rem cm bloco.O sr. Pinheiro Machado — Não haviamais a questão politica da suecessão, poi-(pie já tinha findado com a eleição do s-\Affonso Penna, em 1 de março, sem con-teslação, com o beneplácito, com a annuen-cia dos elementos que nos tinham comba-tido.O sr. Nilo Peçanha — Peço a palavra.O sr. Pinheiro Machado — Creio queeste ponto está perleitamente aclarado.Sáo factos que se pasSaram sob as vistosde todos- nós e cujas conseqüências c aspe-etos se podem perfeitamente afferir peladata cm que elles se deram.Eu disse ha pouco que o aparte que medou o honrado senador e que está inter-calado 110 meu discurso não foi tão com-pleto como está publicado, mas natural-mente era aquelle o pensamento dc s, exc.Parei-eu-iue, lendo esse aparte, que em jéubojo havia uma nota irônica.O sr. Nilo Peçanha — Posso declaraia v. exe. que não.O sr. Pinheiro Machado — Houvesse ounão a intenção de sc referir á questão danão intervenção do chefe do governo, mi-pondo a sua vontade por cima da vontadenacional, houvesse ou não, a nós nos apraztralal-a dè perto.O sr. Niio Peçanha — lanto melhor.Apenas ironia não houve.O sr. Pinheiro Machado — O nosso ponto de vista é immutavel; é o ponto de vista republicano. Aquillo que pensávamosliontein aindn pensamos hoje. (Apoiados.)Islo é. que ao chefe da Nação não é dado.aiaropriiindo-sc das faculdades de poder (jii':lhe cabem, interferir na vida di naça...garroteando a vontade do eleitorado, sobro-pondo as suas sympathias á maioria da-correntes politicas que livremente se ex-pressám sobre problema de tanta magni".i-tle, como é aquelle (pie diz respeito á direc-ção dos destinos da nossa pátria. (Apei.i-das.)Aqui desta tribuna, quando travávamosacceso debate na suecessão do sr. AffonsoPenna, eu declarei: " Nós não intendemos«iuo O presidente da Republica, por sfcr pre-r.idente dn Republica, está desaforado dndireito de intervir com os seus conselho?;com a sua opinião (apoiados) como homempolitico que é, tão interessado ou mais doipie nós pela sua posição, pelos destinosdo paiz, pela sequencia do governo (mu;l >hem; apoiados), estudando a situação, aus-cultando a vont ide nacional. Essa inter-venção do conselho, da persuasão não te-mos o direito de negar a «piem quer queseja no nosso paiz («i/aoíiiifoj), agora a in-terferencia, como meio dc coacção, de vio-lcncia, intervindo na vida dos Estados...O sr. Cun
```
