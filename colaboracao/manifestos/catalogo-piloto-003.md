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

**janela_id:** `per089842_1906_01901:p001:c11865-20902`
**jornal:** correio_manha   **ano:** 1906

```
antiga cinvencível, que dosloa como uma anti-Iheseda sua superioridade no manejoda penna o na elaboração deis suas leioreputadas monographias e nos seuslivros leio admirados nos quaes a dinlc-clica, a cultura e a originalidade brilhamcom egiiiil esplendor.No seu discurso de hontem, o sr. Ar-lliur Orlando não teve em mira oonquis-lar, por simples capricho inlol.ectua],o bastão de marechal da arle oratória.S. ex. nem leve esta preoecupação nemmostrou a falsei modéstia elos <>ue appel-Inm para ,i generosidade rios ouvintesnllm dc evitar criticas o renioques.Consciente ria sua capacidade monlnle ria sua força do estudioso, o.sr. ArlliurOrlando, depois derelenibrar em iodasas sueis phnses principaes o memoráveldebato que ainda continua, tratou eleexplicar as razões pelas quaes votou o-volleirti a votar contra o projecto do sr.David Campista.Risse quo a Caixa ele Conversão insl.i-tuida pelo projecto elo sr. David Cam-pisla não é a caixa dos Ires desejos : —eimnr, querer e aborrecer porque o pro-jecto neio mostra a quem e quo a Caixauma, quer ou aborrece, nem quem (ique aniei, quer ou aborrece a Caixa. Nãoé tampouco comparável a uma caixa dnseffmeis porque o sr. David Campista epierorganizar um apparolho que recolha li-liras esterlinas cm ouro e não simplesnickeis e não tem ajpretençào de conver-ler nlma nenhuma. Acredita que a Caixaelo si*. Campista pôde ser comparada lãoseimenle a uma dessns caixas auto-mnlicas nas ejuaes, em Iroca elo umnmoeda de nickel lançaria numa fenila, sevè sair de outra fenda um objeclo cor-respondente ao valor do nickel.Contestou que a Caixa tenha o poderrie impedir quer a baixa, quer a alta elocambio e entrou a combater o projocloelo ponlo do vista jurídico e constitucio-nnl porque olTcnde francamente os maissagrados princípios da náo retroactivi-dado rins leis. mostrando (pie o direitomoderno jã não tem nada de commumcom as instituições emligas que admit-liam leis com effeitos retroaclivos. licitou largamente a legislação portu-gueza dos'últimos dois séculos.Eram jã ns 4 hora so 20minutos da lar-de. 0 sr.Avthur Orlando eslava cançndo eobteve licença pnra concluir o sen agra-riavel diseurso na sessão dc lioje. ——Durante os dois discursos dos srs. Uo-dvigues Teixeira c Arlliur Criando, es-tavam presentes na sessão'dc hontemos seguintes deputados:—James Darcy,Wenceslão Escobar, Cinçinato1 Uruga,Pnubt liamos, Miguel Calmou, Dencdietode Souza, Darbosa Lima.Antunes Maciel,
Thomaz Cavalem I o, Mnlaqiiias Gonçalves,Lobo Jurumonliíi, FranciscoVeign, The-niisloc.les do Almeida, llodolplio Pnixão,Apoüonio Zenajrios; Mello Mntlos, Fr.m-cisco Brcssanò, Joviniafto ele Carvalho,Alberto Sarmento, Oliveira Vnllaile.o,Adalberto Ferrei:.; além elo presidenle,ArnÒlpíio ele Azevedo', do Incder, CarlosPeixoto e elo eaUor elo projecto, sr. Da-viri Campista.Ao todo 27 rcprcsòntaiiÍGS, para umaCamnra elo 212 deputados náo se podereidizer que esso numero constitua unisimpioma dc seriedade e do empenho..om que a assembléa quer discutir oprojecto da Caixa do Conversão.
épicos enoticias0 TEmPÒUm dia frioi-oiitd; convidando ao nconeliC!?*rio lar, o do lioluein, pontuado, nela manha, tlcclima ««no caiu mais túrtc-o continua pela inrde.Tivemos a temperatura ao mínimo rio 10.!!' cno máximo de )!)¦ centígrados._HONTBMDcspi-clion eou*. o presidente da Kopu-blica o rir. Felix Gaspar, ministro rio inte-rior.Estiveram uo palácio rio Cattcte ossrs, senador Ani"io de Abreu, deputadoPaes "Carreto, rirs. Felisbello Freire cOlyiit.io ric Magalhães e o rev. GeraldoColien, abbade rio Mosteiro de S. Bento.Em conferência com o ministro ria viaçãoestiveram, entre multas pessoas, os se-g-iiintes srs. : drs. Btinrque de Macedo.Pereira Braga, Rego Bacios, capitão defragata Vital rie eiliveirn, senadores Ri-cliard, Catunda, Virgílio Bamiisio; depu-tndos José Bonifácio,-Alencar Guimarães,Elyseu Guilherme, Paula Ramos; rirs. Er»nesto Otero, Graça Ccttto, Eaniotuiier Go-riofredo, Eucly.des Barroso, Conto, Osórioric Almeida, Paulo Frontin e Joaquim Ca-trambv.Confcrcnciarnm com o ministro da fa-açudei o drs. Anísio ele Abreu, HoracioGuimarães, Buarquc de Macedo, Raymun-do Corrêa, José Eusebio, Francisco Bcr-n.irdino c Sérgio íiaboya,Eslivcráni no gabinete rio ministro dajustiça e interior os senador Belfort Viclrn,deputados Cornciio da Fonseca e AinclioAmorim, drs. Alfredo Pinto, João Corroarie ijoraes, Eliiv.-.T Tavares, PliilemonForres; srs. Sohmidt Kratípcr e Mnclten-'/Ac, general Américo Pereira ria Silva,capitão "Domingos Jesuino rie AlbuquerqueJúnior, rir. Domingos do Araujo.CAiiltllOCiifoo oflicialrnAÇAS PO n/v A vistaSobre Londres  ii>:,n issitu» Paris  rui n.i)» Hamburgo  752 'ot;» llnliu  ² lijii» Poriusnl  ² :r.i» Nova Yoi-li  ² ll.ülfil.lhr.i eslorllnn em nioodn  15.IM)Ouro nacional em vaies por lt í.filIlnncurlo  Ifi!) Ifl 15 211/MCaixa matriz '.  15 9/10 li 'ttf.üRenda ila Alfani1e_aPenda elo ella 21;Elll ouro  12Õ:0ÒÕS082llm papel  lil-.yjlin; 3l7:82"iSS-lUcnda dn dia I n 2-1 ,1o corronto 5.l)07:DlfiiO„9Em eg.inl porlorio Je 1905  5. i87i!URS'.,fjilUlrTercnçit a inalor cm ifjOQ  "iii.í.iüisníiHOJE ^^"^
Reune-se cm sci.-üo ordinária, sob a pre-sidciicia rio ministro dn fazenda, a juntaadministrativa ria Caixa rie Amortisaçáo.Está ric serviço na repartição central riePolicia, o V dcicg.ido auxiliar,'" MISSASIlOznm-SO as ser-iilnlo-, por alma'ile:Dr. Manoel RodriKtios do Flguolrodo, .ás 7lioras, na matrl/. rin Engenho Vciiio e ús o i/i*hoi-.iK, nn egrojn de s. Francisco de Paula Ilr. Artliur Ccsai llios, ás o 1/2 horas' naogroja rio s. Francisco rio Paula ;Senador Artliur lllos, ás',) horns, na malfiz deSnntn Antônio rios Pobres ;Dr. Joiio Marlins Teixeira, fts 9 lioras, na ma-triz do S- Jono llap.isl.a, om Nlctlioroy.A' NOITRBECÍIEIO-A Filha tln Feiticeiro. —~*UKI.XDA — A casn da Siiztitina."í;/,/,'-'; '/íí 'í. 7,", -°- /.'':",' "*-1 .¦"*-.'<- rm i sea Al.lo.moi i.i,\ noilCE — 1'rogrtimma variado.».*,-:!/,'{''' HEA T"!-- líspcctaeulo variado.il/.l/.sejiV — 1-iiiicçno variada.Caso seja approvado cm 3? discussão, naCâmara, o projecto creando a Caixa deConversão, o sr. dr. Joaquim Murtinlio re-signarã a sua cadeira ric senador por MattoGrosso.S. cx. não quer faltar aos seus compro-missos rie solidariedade politica com oBloco; mas, também entende que não deveabandonar as suas iric.is de estadista, in-teir.imeiitc contrarias á Caixa de Con-versão.Dalti a sua renuncia, que todos os brasi-leíros devem lamentar porque o rir. Joa-quim Murtinlio i, inquestionavelmente, umhomem dc extraordinário vnlor.Tios srs, ]¦'. Ouimeireles k «:., ma elo Rosário33, rm pago liuiu. in, pela Loteria Fodoral, o W-llioten. 11,premiado om ;'i com I2:i)i()jaj.Firmado pelos srs. Carlos Augusto deVasconcellos Tavares, Cinçinato Martins uCosta e rir. Heitor Guedes Coellio, recebe-mos o convite parn o almoço que, cm nomeria Cumaru Mutlicip.il ile Santos, offercceiná Municlpetlldaile rio Kio rie Janeiro.O almoço terá logar Imje, ao meio-dia,no salão ria acreditada confeitaria Pas-choal, que tanto se tem rcconimendadopelaexcclleiicia do serviço.Agradccidoü pelo convite.Do mais acreditado fabricante de, eíal-cario ele borracha dos Estados Unidosrecebeu lia pouco a Casa Clark um varia-dissimo soriimento de gnloehas o sei-patos.Com o ministro da viação esteve liou-tem eui conferência o deputado federalJosé Carlos do Carvallio..Foi motivo da mesma o novo materialfluoluanlc rio Lloyd Brasileiro; o qualdeve ser adquirido de accordo com ocontraelo.Nos soffrlmonlos da. dontlção, MatrlcarlaOutra. ^_Hoje, ás 2 horas da lardo, no minislc-rio da viação, serei assignado o contratoreferente A construcçáo rins obreis elemelhoramento do porio .le Massiambú,no Estado dc Santa Catharina, contratoesse que importa lambem no arrenda-mento ela Estrada de Furrò D. TtieresaChrislina.Pelo engenheiro Rlmer Lourenço Cor-tliiill, eoiitrnteirite, assignará o sr. Can-dido Geiffrée.Assistirão no neto diverfos (lopulados,pessoas gradas o representantes dei im-prensa.Puroen -0 moiiior purgativo da octualldadeO presidente da Republica dirigiu hon-tem -u Con-resso Nacional dnaa i-cnau-
gens, solicitando, numa, a concessão docredito dc 120 contos aupplcuientai? A verban. 15 do ártico 2' da lei do orçamerlto doexercício corrente, para a rubrica: diíi-gencias policiacs ; e, na outra, pedindo aconcessão do credito extraordinário de 80contos para oceorrer ás despesas qne devemser feitas com a transferencia do ArchivoPublico Nacional, para o novo edilicio, si-tuado d praça da Republica, c com o mato-rial necessário.Foi nomeado lente da cadeira dc medi-cina legal da Faculdade da Bahia odr.Josino Corroa Cotias, substituto da 4.secção.Matrlcarla Dutra, vende-so cm todas txiplinrniaciase drogarias.Ao projocto rio reorganização do exercito,ora om discussão na Câmara dos DepuiurioS,apresentará o sr. Ignacio Tosla, segundo é sa-bielo, unia emenda ¦garantindo aos soldados aunais ampla liberdade para o exercício dos'cnllos, de modo a não serem cllos embaraçadosoin seus devores religiosos, sob o pretexto ricrevistas o serviços que coUicleni cornos devoresda sua religião
```
