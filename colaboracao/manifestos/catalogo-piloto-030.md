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

**janela_id:** `per103730_1907_00112:p001:c36521-43373`
**jornal:** gazeta_noticias   **ano:** 1907

```
nlissimo Sacramento, poralma do D. Cândida Vasques da Cosia, no1' anniversario do seu passamento; fls.Khora. na igroja de S. João Raplista, poralma do I. Augusta Amélia Lins Sa-pho le às 8 112 horas, na matriz da Can-Solaria por alma do João Augusto Pereirado Amorim; na igroja do Rosário, pora nado D.Maria do Rosário JacomnPorto;às 9 horas, na igreja do S. Francisco doPaula por nlmn do D. Julia Gonçalves daSilva Niiiins; ás 9 ll2 lioras, na Igreja deS Francisco do Paula, por alma do DonaFrancisea de Rarros Cavalcantecorda. do La-
SECÇÍ.0 DO PUBLICOPublicamos hoje;Café Ideal; A questão das cer-vejas; A Equitativa; Salve!; De-claração; Loteria da Capital Fe-deral; Junta Commercial; va-rios aui-uncios e outrasmações.infor-
CHRONICA DA PRAÇAE DOS MERCADOS
nal, estamos convoncldos do quo o ro-verno não dlsponsará os sorviços do diro-ctor da carteira cambial do Danço do Dra-lil, sendo mesmo certo quo lhe. prorogaráa licença do quo necossila para recuperartoda a sua saude.(IS A 20 DE ABRIL DE 1907)Pubilcou-se que o Sr. Custodio Coelhochegou a pedir a sua demissão ao go-Verno. O illustre banqueiro teí-o-la leitopela necessldado do» prolongar o trata-mento da sando, a conselho de médicos,o que olmpedirla do continuar dirigindoa Impoi-lantlssima carteira cambial doBanco do Ilrasil.A impressão quo a noticia causou napraça não Iol,nem podia ,r>r,das melhores,dada a Inegável nplidão do'Sr. CustodioCoelho para negócios de camiiiò.*Com elTeilo, difTlrlImeiito serão esque-cidos os serviços ja prestados por essebanqueiro, quando o cambio eslava amercê dos bancos estrangeiros o dos espe-culadores, qfle o faziam subir e doscerconforme as suas conveniências, c o Sr.Custodio Coelho os arredòu da direcçãód.-ssc mercado, tornando unico domina-dor do mosmo o Danço da Republica,mais tarde Banco do Brasil.A nuljcia da sua retirada não podia,pois, deixar inullo boa impressão ^ entre-tanto, secundando o quo ja disse um jor-
luncclonar aDesde que começou aCaixa «Io Coiivorsão, a semanapassada ioi a primeira durante a qualpodemos observar terom sido muito inlo-i-iores as suas enlradas do ouro, cmrelação às sabidas.Na verdade, as enlradas loram do 31. .70libras, 1.MO trancos, 80 marcos, 5 dol-lars, 100 liras, 80 coroas austríacas o_:9_59 dc ouro nacional, tendo allingidoas sahidas a G9.005 libras, 14.600 francos,700 marcos o a 2:975. do ouro nacional,polas quaes loram trocados 1.119:480$ emnotas da Caba, tendo sido emiltidos me-nos do 300 contos.A Caixa, quo havia encerrado o lialan-cete da semana anterior com um depositodc £ 5.164.609-10 shlllings, ficou no ul-limo sabbado com £5.133.374-10 shll-lings, ou uma difícrença do 31.235 libraspara menos.A somma de 10 540.350 Irancos fleoureduzida a 10.526.S90 e ado 700 marcosa 80, tendo augmentado o deposito deouro nacional de 1-.970. e, quanto ás do-
mais moedas, do 5 dollars, 100 liras o 80coroas austríacas. sNada ha em lal facto quo possa causarestranheza.E' um facto dos mais naturaes, quo vemapenas revelar uma das faces uleis daCaixa do Conversão, esso grando reserva-torlo do ouro da economia nacional.Com etfelto, quando, num raomontodado, o ouro possa lornar-so mais caro,devido a uma outra siluação da praça,creada pela escassez do letras do cambio,6 o caso do irem procural-o na Caixa doConvorsão, mediante o troco do suas no-tas, sem quo o expcdlonto venha a produzir abalos ou incoveniente3.Foi o quo, principalmente, sc deu du-ranlo a semana passada, o numa oscalasom Importância, podondo-so lambem |accrcscentar a este phenomono mais umaoutra causa d» augmento das retiradas doouro, qual seja a morosidado da expediçãodo vales-ouro pelo Baneo do Brasil, que,alim dc haver monopolisado esse serviço,ainda torna obrigatória a assignatura dosseus directores nos referidos vales, nãopodendo assim allender a Iodos quo a ellorecorrem e acham mais expedido volla-rem-se para a Caixa de Conversão.
velou aló certa firmeza, ombora nãolossom avullados os negócios. Houvopouca oCfcrla do papeis., Indirectos o pou-cos tomadores, principalmente depois dasmalas do Allantiquc o do Thames.0 Banco do Brasil sacou a 15 3|16, oHalo Brasiliano a 15 5|32 c os oulrosestabelecimentos oslrangoiros, a princípio,a 15 1|6 o logo depois a 151(8, taxas ostasem que foram realisados os últimos ue-goclos no sabbado.O llanco do Brasil, logo no primeirodia da ..emana, passou a operar a prazo,vondendo ate às ultimas malas do iuuho,ombora restringisse as vendas para maladeterminada, com aviso priivio de 8 dias.Islo veiu estabelecer corta conliança napraça, confiança esta que dispensaríamos! para formação do nosso juizo. Nonhuinreceio tomos.de presenciar tão cedo gran-dos baixas do cambio, principalmente porestarmos convencido do quo o negocio docate não será desamparado.
0 mercado de emublo mantove-soestável durante a ullima semana o re-
0 mercado do enfé continuou em po-slção das mais criticas. Vai-se tornandocada vez mais dilllcil a siluação dos com-mlssarios, em vista das limitadas compraspor couta de S. Paute, do iclrahiinculodos ensaccadores o exportadores c dascontinuas entradas do gênero no mercado,
onde o já enorme stock ostà so avolumandodia a dia.Tamboin não ha-lembrança do tamanhasaíra no Brasil. Para lormar-so uma Id.abem approximada da sua lartura, baslàráconsiderar qüo, da presento colheita, do1* dc julho ao fim da primeira quinzenado corrente mez, as entradas alliiigiram,aqul'o om Santos, a 16.143.351 saccas,existindo, segundn-teira passada (flui da.ultima quinzena), nesses dous mercados,um stock do 3.518.824 saccas.Os compradores olllciaes continuaram aoperar nos limites dos preços e qtiautl-dados costumeiras;,* fora delles, poróm, omercado mantovo-so apatbico, desanimadomosmo, eflecluando-so alguns negócios Iaus preços dc 58400 e 58300 para um vo-lumo de 10.000 durante toda a semana. |Essa apalhia do mercado, lóra das com-pras ultlciaes, lem a justificativa nas bai-xas constantes da bolsa do Nova York enas entradas de calo a avolumarem inces-santemonlc o slock.A siluação da maioria dos commissariosó, pois, como dizíamos, cada dia pcior; etâo allllctiva já so vai tornando que essaimportante classo de neguciantes deliberouoiíiciar ao governo, pedindo para seremalargadas as compras olliclacs, ou, na im-possibilidade do. «overno !azel-o, para sersuspenso o accordo pelo qual são ast mesmas realisadas.
Embora explicável lal pedido pola dura ico-tlngoncia dos commissarios, quo adean-tam dinheiro aos fazondelros o dosles ro-cobora o calo, do qual não podom disporsenão por solecção o mínimas parcellas,não achamos Irancatnoiile acertado quero-rem os referidos commissarios collocar ogoverno entro as duas pontas do ura di-lemma, das quaes bem pôde acontecer quoesle recrie.Do lacto, para alargar as compras docalo, ó necessário dinheiro; o, so o Estado ido São Paulo não alargou laes compras,, do grandodando conjunctanicnlo com os do Minas oRio ex
```
