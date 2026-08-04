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

**janela_id:** `per178691_1906_08026:p001:c19016-28127`
**jornal:** o_paiz   **ano:** 1906

```
 uma penosa situação dc ancie-dado Irrefreável.Desde os primeiros actas dc gestãofinanceira do quatiiennlo CamposSalles, nossa administração suportartraçou, com linhas fortes, um pro-grnmma do osperanepsa rehablllta-ção do melo olreulaiWe, fundado emdois processos harmônicos : um, quoagia restritivamente, — o da dimi-nuição graduai da massa do papolemlttldo, por via do resgato ; outro,quo agia como saneamento, — o davalorização progressiva do papel ro-mnneseonte, por via do fundo dogarantia.Caminhando cm dirocçOcs oppos-tas,— da perlpherla para o centro,e do centro para a perlphôriao— osdois expedientes administrativos te-riam, infnllivelmente, sou momentodo encontro; o o papel-moeda, ga-rantido. na justa medida, pei0 ouloque a economia naolonal «=tava dc-nodadamento "depofiitando, perderia onndrajo do curso íorçcdo o tranafor-mar-ae-hla om nota.j convorelvels ftvista.A evolução sc-iia lehta j kb3 crado mlstor assim ío«o jaro quô anoECft vida econômica «e wJaDtassc
pouco a pouco ds condiçõei; oroadaspolo iiisiruniento do pefmulas empliases Buccessivas do valoriza çãoascendente.Essa lentidão ora uma ancora :como a confiança Inspirada pelnoffieacia dos meloo empregados paraa. regeneração da moeda ora um In-centlvo no trabalho o um convitesoduetor aos capitães estrangeiros,de que tanto necessitamos para aconstrucoâo da nossa riqueza futura.Prova do que não exageramos,nem nos lllúdlmon, ahl eslft patenteno renascimento do credito brazi-loiro, Outr'ord inimorso na esctirl-dão do uma moratória nfllletivn, edepois floreseente nos centros mo-nòtarloR ondo o prestigio dns nn-çãos é af ferido polo osla lão da sa-bciioria dc suas finanças ; o foi gra-ças a esse florescimento afortunado,quo pudemon experimentar certosmovimentos do orgulho pelos tra-balhos ciiinieheiidido.-i dentro datrajoctoria da civilização o do pro-grosso.Para chegar a essa altura, tive-mos dc machucar ns mãos o os Joe-.lhos num galgar corajoso do escarpas quasi a pique, levando aos hom-bros o poso do impostos excessivos,quo significavam o appollo dirigidopolo Interesse do iodos ao pátrio-Usino de cada um...Exactamcnto agora, quo o oxitocomeça a recompensar o esforço, nmoeda começa a ganhar valor o opeilo nacional começa n dilatar-sefrancamente numa respiração mo-nos oppress.i/—o mesmo poder te-gislatlvo, quo durante oito anuo-consecutivos nos descreveu, comocerto, o roteiro da torra promolllda—muda subitamente do rumo o de-clara ao povo espantado que e in-dispensável coíilblr a alta do cam-blo, aquella altn salvadora para con-seguir a qual tantos sacrlíicH»; ex-Iglu !Positivamente, isto atordoa. Ouo Congresso affirma a sua iheompo-tencla pretérita, ou confessa n suatemeridade aetual. O quo parece delodo Inudmissivel 6 quo so reputecom direito a ser acreditado, querconfosse, quer affirme. E não pôdemerecer credito, porquo o factoom sua realidade palpável, tommaior eloqüência quo os madrlgaesfinanceiros do Sr. Campista o oshyninos pnlinodlcos do Sr. Cnrvn-íhai, offcrtados a slngruiarlsBlmacaixa do conversão com quo aquelledeputado pretendo augmontar o nu-moro dns nossas inutilidades fu-nestas.Confrontando a prosperidade, qm-ostavnmos adquirindo, com ns pro-blomatlcas vantagens decorrentesda dita caixa, o povo ncou intima-mente convencido quo a projectadareforma, pola qual ¦¦..Camura seestft batendo com nrdores de chrls-tfio novo, O antes uma hospodarln
ceiro, ein que a fixação do valorda moeda sirva do pedra fundamen-tal. Nem seria razoável inferir ou-tra iilação.A parto do convênio do Taubaterelativa ft "estabilização" da taxacambial por meio da quebra do pa-drttò monetário, foi recebida commanifesta anlipathia, justificada ounão, o desde logo so suppoz quo, nosolo do Congresso, vozes enérgicascondemnaisom o plano do 20 defevereiro, rofugado aliás pelo presi-dento da Republica, em documentodo riiemoin.vol auecesso.Autos d» subinotiido íi apreciaçãodo podor legislativo, o convênio foicortado cn. duas metades dlstln-cias, uma constituída polo systemaIdeado pnra a valorização do cafénutra figurada polo problema damoeda.Desto ulüi.io.cujii formula solutorlafoi confiada á imaginação poderosado Sr.Düvld Çumplsta.tevo o Congresso conhecimento pelo projecto dnealxa de' .conversão, quo ora se dls-eute e, Bem duvida, serft aceito, soum conse|ho salutar não vier pre-munir-nos' de deslIlUBões tormon-tosas. O intuito primordial do lolenloso deputado mineiro foi comi-liutorio, luto ó, amalgamar cm umncombinação nova o original o desejodos quo pugnavam pela quebra dopadrão com o dos que a combaliamAo espirito Itüolllgente o sagaz doSr. David Campista não passariadespercelíHn a impossibilidade deobter sons accõrdos do Instrumen-tos afinado: por dlapusões tão di-versos, c cirno não 0 do crCr avo-casso e'!o, por autoridade própria,funeção de._ elaborar um substitutivoIo iniivoiiln, surdo, naturalmente,a hypothesc veróslmll do quá sohotivcs.-e incumbido da extra-, agam.-missão, com algumas "restrlcçõcsmenlnes. 'Num opusculo impresso em BeUnHorizonte sob o "Convênio de Tnu-bato", o Siv David Campista publl-cou o sou projecto o cuidou do justl-licai-o.Disse isto : A caixa do convei¦-são receberia o ouro que "esponla-ricamente a procurar e mobiüzal-o-ha no mor"ado por meio do notasespeciacs", otniilidas em uma rela-ção predcU-nnlnada. A fixação dataxa roíere-::o a "essas nolas" e 0como a condição de um "contratoentro a' caixa emissora o o portadordo ouro"—-Nao ha quebra do pa-dríio monetário".Dirigida jsta saudação affoctuosnaos adversários dq quebra do pa-drão, o depois de transcrever umtrecho do livro dc propaganda dosSrs. Marttnez o Lcwundowsky,"IVArgentine au XX e slecle", emquo bo enc reoc nstuclosamAito areforma de J.S99, ou da quebra ef-fectiva do padrio, o autor do opus-culo escreveu:"Assim õ licito acreditar-so queinstituída *__. uia um spsarel))»
comparável ft caixa do conversãoargentina, produzira ello " os mes-mos effoitos ealataros" sobre a os-peculnçfio, quo tanto nos projudi-ca..."E concluiu, afinal :"Afastada assim "do mecanismodo cambio a pressão artificial quenoile tanto influo, as oscilIaçUos dataxa serfio contidas, "no sentido daalia" pola caixa do conversão; queforneço moeda-papel "a cambiolixo cm troca do ouro quo for lielladepositado."Eis, pois, uma caixa comparávelft argentina, capaz do afastar pres-sães artlflçlaes do mecanismo docambio e do fo.rnecor moeda-papelft taxa fixa. listava desenhado o sor-riso para os quo pediam a quebrado padrão, ou pnra ns que a dlssi-mufavam com a locução sophistlca.'o fixaçiu) ou estabilização docambio."a nns, consegulntemonte, o Sr.Campista declara :—„-,„ ha quebrado padrão; a outros, tranqüiliza:*—Isto valo pola quebra, Faltou-lho adeci.-ãp, por ventura, para Inscreveria lei o sou pensamento integral ?Sobrou-lhe rtnura, acaso, para oo-oullar no projecto aquellas restrl-cções mentacs a (|Uo alludimos haAssim nasceu, ínfolizmonte, oplano, quo agora surprehonde o-.iiunilo, de uma ealxa do conversãoquo não converta o papel-moeda doEstado, não dispõe de lastro seu oespora a incursão do ouro espon-tanoo, emitto bilhetes a uma taxa"predeterminada"; quo serft do 15 d.por l?, como seria do íi ou 12, soa tanto se aventurasse o alvedrló doautor, e exige para fites bilhetes o"curso legal", q„0 „ Br< Campistadefino "poder Hberatorlo" llllmltado,sem Indicar oin quo »|0|" Osso cursolegal so apoiara, so m. de 184fl> nftorevogada, so ncisa, ainda cm gos-tação. quo o Congresso approva oparece vai promulgar !Realmento: se os financeiros dovelho continente não comprehen-dessem quo os estadistas brasileirosso oecupam do decifrar charadasOU do compol-as-não devemos bra-dnr, por Isso, que nos estão ellespeito não 6 u
REVOLUÇÃO DE CUBAHavana, .;(.Os chefes dos insurróctOR nonica-ram uma comniissão do selo meni-bros, com plenos podores, para tra-tar com oa delegados do governons condições da paz.Diz-so quo os chofes liboraos estãoconvencidos do quo dessa conforon-cia rosultarfi, a lonninação daa lios-lilidadcH.— Esião promptos a desembarcarquinhentos marinheiros americanospara proteger a cidade, caso .¦cjaatacada pulos rovol losos,(Serviço do "Paiz".)"A Noticia", do 8. Paulo, publicau seguinte Informação :"Estarft de regresso a S. Paulo,no próximo mez, o Dr. Jullo do Mes-quita, director o proprietário do"Estado de S. Paulo". Dopois douma ausência do oito mozes no os-trangoiro, volta, o lllustro Jornalistaa oecupar a sua gloriosa tenda dotrabalho no magnífico jornal a quoelle tom dado, em longos annos deIn de fosso labor, os seus melhores es-forços o os primores da mia pc.nnaencantada, quo tantos trlúmplioÁcolheu, cm outros tantos serviços ácausa publica.Duranto quuRi todo o tempo dasua ausência, tom o Dr. Jullo doMesquita pormáneclda om Portugal,ondo a Imprensa deu, em termoshonroslsslmoe, a noile'*! Op. buc* ch—gada. ¦Em Lisboa, foi freqüentementevisitado por pessoas da alta rodapolítica o literária, o da melhor so-cledade llsbonensc.O presldonte do conselho do ml-nlstros, conselheira João Franco,ofioreeou-llio, om sua residência,uni almoço, a que estiveram pre-soutos alguns dos mais notáveis ro-pi-csontanlei! da política em Portu-gnl, o a quo lambera assistiu o
```
