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

**janela_id:** `per178691_1907_08314:p002:c28048-35562`
**jornal:** o_paiz   **ano:** 1907

```
francos, que foi divididaem parte* iguaes, para oa náufragosdos tree paii-os.A «ueta quo coube aos brasileirosfoi entregue ao general BernardinoBormann. que, ao «altar em Lisboa,entregoa-a ao cônsul brasileiro paraser remettida ao ministro da mari-nha.
PI.IESTR?.
NOTICIAS 01P8E
d lijubila-
O expedionle da Prefeitura constahoje do seíuinte :Actos do podei- executivo—De-creto abrindo o credito de lü:219í_40liara pagamento de uma contaexercício findo. Nomeações,ção o licença.Directoria geral de policia—Despa-chos de requerimentos. Infracção deposturas. Vistorias. Embargos deobras. Editaes das aifoneias.Directoria geral de fazenda—Paga-mentos. Alvarás de licenças. Predial.Reclamações. Lançamento do impostopredial para IDOS.Dlrectoria geral tle obras o viação—Despachos do prefeito, da directo-ria o das eireumscripções. Sub-dlre-ctoria da carta cadastral.—O Sr. Leonclo Correia, directorgeral do instrucçâo, expedlu o seguin-te oflicio ao sub-director da EscolaNormal :"Em addltamento ao oflicio n. 280do 4 do corrente, no qual vos conimu-níquel ter dispensado, de ordem doSr. Di*. prefeito, da regência de umacadeira c do varias turmas de alu-ninas dessa escola, as cinco professo-ras catliòdrátícás de instrucçâo pri-maria quo ahi têm exercício, o tle!as necessárias inslrueções quanto adistribuição das alumnas que consli-luem as referidas turmas .rocommen-do-vos, também *de ordem daquellaautoridade, que as providencias de-terminadas no citado offieiu sejamsustadas alé o rim. do corrente annolectivo".A nossa funeção do jornalistas, snmuitas vezes nos tra*. pesados dissa-bores, de outras nos proporciona mo-ttyòs do satisfação, quo valem por ver-dàdèiras recompensas ás contrarieda-des peculiares á nossa profissão.Uma dessas recompensas foi-nosdada honlem receber com a cnmmu-nicação que nos fez a União Operariado Engenho de Dentro, conferindo-nos o tilulo do seu soclo benemo-rito.Registrando com os nossos agradeci-méritos essa captivanté gentileza, da-mos a seguir o oflicio com que nosfoi ella communlcàdá.Lisorijôia-nos sobro modo tal dis-tinc.cão: operários como nós, osmembros dessa prospera associaçãovieram trazer-nos com ella o testemu-nho dos seus sentimentos de confra-ternldado.E' este o oflicio quo nos foi diri-gido:"Com bastanto prazer communi-eamps .1 redacçãp do "Pai*"," que aUnião Operaria do Engenho de Pen-tro, om assembléa geral ordinária, de0 do corrente, concedeu-lho o titulodo sócio benemérito.E' esta a única fôrma como pado-mos palidamente recompensar os va-liosos serviços por osso jornal presta-dos A União o á causa do operariadoem geral.Em oceasião opportuna vos seráonlrogue na redacção o respectivodiploma. União, paz o justiça—-TiRO-NlOIA PARROS, 2^ secretaria."!0 Dr. Raul Martins, juiz federal,no Estado do Rio, por sentença, dehonlem annullou o mandado de pos-se expedido a favor do Danço Con-striictoi' do lirazil contra Guinlo Si C.
Café r»»«Sfiio, não tem rival.A propósito da noticia que demosante-hontem sobre dtjiapparecimenlode cédulas na caixa de conversão,recebemos do Dr. Henrique Diniz,vice-presidente desse estabelecimento,uma carta, que abaixo transcrevemos.Apressamo-nos em corrigir o en-gano que houve de nossa parte, dandoo facto como passado na caixa deconversão, quando elle se pasaou nade iimortKaçâo, em que um empre-gado que pela primeira vea se enoar-regou do serviço de notas, commotteuum erro de contagem, entrando, po-rém, desde logo, com a importânciarespectiva.A carta do Dr. Henrique Dinia é aseguinte :"Sr. redactor do "Palii" — Cau-sou verdadeira surpresa aos funecio-narios da caixa de conversão anollcla, que' provavelmente vos foitransinittida por algum maldoso in-.orniante, e A qual vosso jornal deuagazalho na secção editorial de hon-tem, 7, reforente a" um supposto in-querito, a que segundo a alludida no-ticia se e-tã procedendo nesta reptir-tição para descobrir-se o parad-iro doalgumas cédulas conversíveis que,"vindas da Casa da Jloeda, desappa-receram, como por encanto, da mãodo empregado que as recebeu" (sic).Posso felizmente assegurar-vos sercompletamente Infundada tal noticia,quer quando ella se refere a inque-rito, quer quanto a desappareciini.ntodo cedulae.São de 22 de fevereiro do correnteanuo as ultimas remessas de cédulasconversíveis pela Casa da Moeda aesta caixa. Tanto aquelle estabeleci-mento, como o Thesouro Nacional,quo anteriormente fornecera á caixanotas conversíveis, fizeram entrega aodigno ex-thesoureiro interino, Dr.Car-los Cláudio da Silva, de todo o ma-torial de emissão que forneceram ácaixa de conversão.Da escripturação feita nesta repar-tição, consta todo o movimento deentrada dessas notas.Alé áqiiella data foram recolhidasá caixa, com destino á emissão, 174.010:570$, sondo 70.844:800$ reco-bidos do Thesouro Nacional,, R 94.705:200$, da Casa da Moeda.Deduzidos 1.002:430?, do notas in-utilizadas, na conferência desta caixa,por conterem defeitos que as preju-dieavam para a emissão, notas quese acham depositadas em uma dascasas íorles desta repartição, e queahi podem sor vistas o examinadas,restaria 173.547:570$, em notas con-versiveis, aproveitadas para a emissão.Tendo rldo já emittidas até ante-honlem, segundo o balanço semanal,hontem publicado, 100.191:880$, re-slam 73.350:690$, queso acham de-postadas em um dos cofres da caixa.O alludido balanço destrúe porcompleto a informação a que a localdo vosso jornal so refere, e ao con-trario do que insinua um dos tópicosdá referida noticia, posso assegurai'-vos que esta repartição conliiu.a aproceder de modo a não desmerecerda confiança do quo a tem cercadoo publico, desde o inicio da sua insta-lação, e os respectivos funecionarioscontinuam a fazer jús á confiançacom que os tem honrado o governoda Republica.Foi, portanto; illaqueada vossa boafé por vosso informante;Estou certo tle quo recebereis comprazer esta contestação, como brazi-leiro o patriota que sois, o por issoconfio dareis agazalho a esla carta,em a mesma secção do vosso concei-tua do jornal em quo foi aecusadaesta repartição.Antecipando meus agradecimentos,por esta fineza, me subscrevo, etc."Recebemos ainda do barão de ÁguasClaras, secretario da caixa de con-versão, uma carta abundando nasmesmas considerações da anterior.
Os subúrbios vão deitando as man.guinhas de fora: jã têm o seu jornale vão ter, no theatrinho do Club Vintee Quatro de Maio, a sua revi.ia aeacontecimentos locaes, escripta pel0dietineto amador Oscar líotta.Xavier Pinheiro, jornalista laborlo.so e poeta, que conheceu os horroresdo "cárcere duro", por haver rimadoalgumas parelhas de alexandrinos,mettendo á bulha um presidente daRepublica, é õ redactor principal donovo órgão, que so intitula o" Subur-bio", o se diz "independente, noticio-so e literário". O primeiro numero ap-pareceu, ha dias, no Meyer, estaçãocognominada—a capital dos subúrbios,O jornal, por emquanto, 6 semana-rio: appareca aos sabbados; mas, soo ajudarem a levar a cru_i ao Calvário,apparecerá todos os dias, emborachova !Ahi está um jornal,- que, se for bemorientado, poderã prestar os melhoresserviços a toda essa vasta zona, ([,lüde S. Christovão so estende sié .San-la Crua. Até hoje os subúrbios, quotanto concorrem para encher ns co-Ires municipaes, pouca attenção têmmerecido aos conselheiros e prefeitos,Hygiene, luz, esgotos, calçamento, es-colas, policia,—tudo lhes falta, e újueto.é muito justo, tiuo não lhes (ai-te nada.E' extraordinário quo Cascadura,por exemplo, sendo, como é, uniu es-tação importante, caminho daquellasanatório que se chama Jacarépaguã,sô tenha illuminação em noites 
```
