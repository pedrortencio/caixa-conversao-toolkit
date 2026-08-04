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

**janela_id:** `per103730_1907_00013:p006:c36709-44526`
**jornal:** gazeta_noticias   **ano:** 1907

```
-que era situada fora do coi po principal do '¦ v.^nador a [esta de Nossa Senhora daediiicio o fora destinada6 cavallariçii.sendú ! Aiuda. 0 programmã foi organisiido comlircseiilemenle, llepois doadapladO, rosor-' -rando esmero, havendo grande numero«fada a oulros misteres, taes còinolipi-j ('° tlivorsõoj. A Cantareira terá barcasliodagcm do segunda ordem, deposito de | cilraorilinarias durante todo o dia,ohjeclos du valor, caixotes vasius, olo,:'Conli.mia entregue ao mais coinplelo
Lembrou 110 governo a conslriicção d ¦uma estrada de (erro para o sul de Maltotlrosso, ate Coruinliá, obra essa que cer-lauienle seria de audácia, por ter de ven-cer os extensos pântanos do sul daquelleEslado!Depois referiu-se ao Sr. barão do RioUrauco.o vencedor das Missões, do Amapá«» do-tratado de Petropolis, e. liem assim.aos projerlos.do Sr. marechal Herme3 da[ímiscca, rclatlvamonlo á fundação du umacolônia militar a margem direita do()va|ioc.I.cmlii'i.11 lamhom a còrislrárção de umavia férrea (le Camaquan a Carapainaii, 110Alto llio Negro.Klagioii o sr. ininislro da induslria porhaver .lado ordolis lérminantes para- alei iiiinaçáo da construecão da ostrada dfferro de S. Paulo ao Rio Orando do Sul.'llorminon dizendo quo essa vastaivd ¦ dc via-lcrreas cslrateglcas, se ser-viam para a defesa do paiz. lambem s.-r-viam para eslalieleccr os laços da [ratar-11I1I111I0 liilornaclotiál com os nossos \i-zinhos.(I orador (oi vivamonld ciimpriiiienlailoo (elicilado no leriniiiai' a sua brilhanteconferência, tendo-lho o Sr. li irão do llioBraneo ilaito os mais cordiaes parabéns.A próxima conferência reallsar-se-6sülibiido, sendo orador o Sr. coroneli)r. G.aliricl galgado o cujo thenia 60 «os-lado maior».
r.i/v.ii niinoi hijn :0 Sr. ittiumlc-riiraiiol I-itJuií.m Xavier dallrllo; ^0 Sr. Iif. Alíiarln lllolclilnl, [üncoloiiarlo damlnWorlo do indii.tria;11 Sr, lonontõ llornclo Marlbia, inarlilnisia«In Miihiiu. Iiiglox ;OSr Joruu Slory, osUmado omprogado 110I eoinmorelu;-^>- Por mnllvo do sçn anniversario n.da-llcli),.foi liontem iiiiillociiinniluioiitadn a Sr.Iinilriuucs liiuliusn, socretnrio dn Sr. ininislrodn Iniorlor.AloAidouni rico oppotollto dn porcolanado Húyro-t; ÍS. S. lacoliou da hous CQiu|):tnttoi-r.is ile Ir.ibalhii n amigo! dhersns iininu o.dlniipiiils'. dc dures.BflPNSaDDSlli|ilisa-s.i hnje. na matriz do Sanl'Anii'1.ninoiilno Mario, llllio rio Sr. Alvar» (Ininus.SAu (Kitlriiilins íh íivu*. pntornoBj Sr. liniiim(joí Qoniuü iiiüti.» nofioclaiilo du nosso praçu an Ivvma. Sra. I). llnnerina (lemes.FESTAS IN IM iSNu dia lll du eniroalu, por occaslflo dn sounnnlvorsarlo nalalloio, o Jovon ongoiiliolroDr. José Aúttuito Anosibi oflorecQU tios bpuiamigos o collogas um jniiiar inliiiin. Ao«ttossorl» foram irocãdos amistosos brindes.CHEGADASlio S, Pardo, onde CM-rco inipoitnnlo oarsopublico, chognu a esla capilal com sua lixuia.i:s|)(w;i, oiSr. lír. Josú Mtonto Siibrinliõ, jor-ntilislo o oscrijjlor n i(|iinllu clilnüu-CÃTxÃ D.B-ei)NVBBSSO0 iiiovimeiito (le entradas de ouro naCaixa do Conversão, [oi o sogulnlo : ouronaolouuN:0i)03, H21NQ-0-0, (ranços 120,(raeeõcs ife ouro 73B0B5, 110 total do55:Ü4II!J0Ü3.U movimonlo dn r. tiradas: ouro nncio-uai (i(),s, jt ^70-10-u. moeda subsidiaria21.1000.0 balancete semanal da Caixa aocusa oseguiiila movimonlo, alé liontem: billiMosa omlllir GU.2H4:010sOpO! morda subsidia-ria Lfli.-|70*lr78: 110 lutai papel de GO.300!IS0BP78.A Caixa possuo em depusilo :£ 2.-117.5)91 -00, coricsponilenles D 38.087:9048000. (rs. 1.005.880, eorrcspon-(lenles n Ü39:C82Í)ÍI28; marcos L00, corre-spouilenles a TshõII; dollars 3Ü0, corre-spoudeiitvs a 1:1MÍ8'1SS, o ouro nacional28:4IOfj; corrospiiiidelllos a Dl:lo8s, liotülnl dé 39.370j9898U22.Emissão -bilhetes omlltidòs 39.597:7908,hilni-lcs ivagatadiis 219:3308, bilhetes emcireulaçüo 30.878:40081 notas a oniillir60.284^010; suppriinenlo du TliesouroFederal, em moedas subsidirias OltS18:01)03000. 'Referindo-se á noticio publicada hon-tem nesta secção. relativamoilUi ás recla-inações que lôin surgido sobre as guias(iu- são exigidas pela (liesuuraria da Caixade Conversão para a emissão e resgalodouolas conversíveis, o Sr. Dr. üavid Ciun-pisla, ininislro da fazenda, declarou ao re-preseutaiite da Gazeta que tal providencia[oi adoplada o será mantida, não Imitopara se verificar qualquer falsificação dasnotas conversíveis, mas sim para facilitara escripluração o lieul orientar a eslalis-lica. pois, dado mesmo o caso que algumdeposilante apresenlc um nome apocry-pilo. não é licito acredilar-se que as com-panhias, lirinas o oslalielcciiiiciitiis banca-rios õslrangoiros iiscui de amiolhanlo re-civ-o, que,alias, não teria nenhum alcancepratico, podendo assim o governo saber aprocedência do ouro quo dá entrada na-quelle estabelecimento.S. Hx. acrrescciihm que o uso de (aoscuias está lambem introduzido na Caixade Conversão Argentina o cm alguns cs-tabelecimeiitos bancários õslrangoiros.
¦
i
Fogo!No armazém de se.-cos o molhados darua do Acro 11. 41, honlem, ao meio dia,enlornou-se uma lata de álcool, ineen-diaudo-se o Inilammavel;0 faclo produziu grande alarma, atira-hinrio ao local os bombeiros e a policiada 3' delegacia.1'olizmeiile o togo toi logo abalado emseu inicio.Duas navalhadasCândido da Silva, cai.xeiro do botequimda rna S. Luiz Gonzaga 11. 78; tão malserviu ao barbeiro Hilário do tal, que estolho deu duas navalhadas, no pescoço obraço direito, evadiudo-se em seguida.O ferido quei.xou-se á policia da 11',que procura o aggrcssor, tendo abertoinquérito sobre o (acto.FalloccH aiilc-honlem, ás G horas damanhã, de uma syncopo cardíaca, a illus-tre e eslimadissima Sra. D. Anulada Vi-eira de Toledo, digníssima esposa do Sr.coronel Rodolpho Vieira Carneiro, osli-mudo o prestigioso chefe politico de S. .loãaBaptisla dos Cachoeiras.Ao espalhar-se lão triste nova, a casauiorliiaria ohiilieu-so do parenles o amigosda finada, que gosava de toda òslinia uasociedade cachoeirense.Seu sahiineiilo deu-so lionlcm, às 9 ho-ras, sendo acompanhado por mais do500 pessoas de todas as classes sociaes,cavalheiros do Paraizo o pelo banda mu-sical daquelle logar.
 *<««*<*«v'Ob**»-»i
E.ESPEGTACULOS DE HOJE
caixotes <-xislin.il mais de duzentosque aliuieiilaram poderosamente, o logo.
I
iSáo nus .souberam iiilurniarda origüni.üoincêndio. Oomparerornm ao local o Sr.Dr. Arlhur dn Sá Eiljp, presidente daCâmara, com um pessoal de 50 trabalha-dores da Câmara, o Sr. Dr. Silva Cosia (>José de Oliveira Leito, delegado de. policiaera exercido.Houve grande dlfüculda le em dominaro logo, não obstante ter .icudido au cha-niadii, que lho lui «lirigido, lambem abomlia o mangueira da Fabrica SanlaIsabel. .calculain-soom5:000t os prejuízos cau-sadus.Ficaram levemente feridos dou? criados
abandono ji praça Sele dn Março. 0111 VillaIsabel, 0111V1 a Prefeitura poderia, apro-veilaudo as disp isições Iocaes. fazer umbello jnrdini para recreio da numerosa po-pulaçao desto importantíssimo bairro deslacapital.Aquella praça é apenas utllisada poriporfiim. (|ue mandam, pela maiiliã, pas-seiar alli qs seus auimaes; por iluuus decarroças, que se servem delia para pastoilus respectivos ninares, o pelos criadoresdo ealliutias e cabritos.Além ilissso, a praça A noite apresenta1101 aspòclo leiiKbriLSo, porquo so açoitamnas suas pequenas maltas indivíduos des-occupíii.1o5. malandros de profissão o ga-
1'n.ln'cc Tlieiiti'Oi— A companhiafrance/.a de operetas e vaudeyllles oífo-rece koje, á tarde e á noile, dous magni-(Icos cspoolã lllos aos habilites deslo ole-gaiili» ihcalro,levando iscona a engraçadacomedia Sfratagème.Tomam pari" na representação os ar-lislas mais uolaveisda empreza.Dt«'«.f«'i<>. — O hilariante vaudevilloO homem das leias vai hoje á scena, á lardo á noile.(is que sabem apreciar a engraçadapeça—o conlllm-so milhares—não (aliarãolio in ao Recreio, quo, por esse motivo,vai ler uma casa
```
