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

**janela_id:** `per178691_1914_10827:p001:c14018-22109`
**jornal:** o_paiz   **ano:** 1914

```
za desta vida apparece ainda maior.Que scnsjções iniiunicras e diversasnão tem dado a Villaboim essa vida pro-digiosa de intensidade, desde o momentoem que, como um heroe de Balzac, seapresentou no foro de iS. Paulo, aindaimberbe, com uma pasta na mão, vendoem torno de si o movimento colossal dosinteresses, a guerra furiosa dos capitãesentre si, a vibração de uma sociedadeávida de enriquecer, oa qual elle teria
da crise actual; dentro em pouco, ogoverno, armado com essa providen-cia, terá normalizado uma situaçãoque não pódc permanecer como está.Uma discussão mais serena, umestudo mais ponderado da questãomostrou que o receio, de que fizerampretexto para a obstrucção, de podero executivo dar máo emprego ao em-prestimo levantado, não era uma ra- ,zão bastante para a recusa da me-dida solicitada, por isso que havia,como houve agora, o recurso ds.li-mitar, ria própria lei clc autorização,a applicação dos dinheiros aó obje-divo real dessa grande operação dccredito.Certo, nenhum dc nós, os queacompanhamos a marcha administra-tivà do governo actual e vemos osincero empenho dc acertar c o zelocom que tem procurado defenderãonosso credito, manifestados na gestãodo illustre Sr. ministro da fazenda,pódc aceitar como necessária a pre-caução que â commissão de _finanças,por uni movimento dc explicável to-lerancia, admittiu na emenda anperisáá autorização legislativa; a'mesmaopposição, que testemunhou a fir-mc;:a, por vezes rude, com que o go-verno cortou no orçamcnlo vigentetodas as despezas que se apresenta-ram como passíveis de corte, nãotinha o direito de duvidar do modopor que seria apulicado o empresti-mo; entretanto, apresentada - aceitaa entenda alludida, ficou demonstra-do que o pretexto allegado era in-subsistente' e que a hostilidade á me-dida solicitada pelo governo não scjustificava senão por um movimentode politica apaixonada.Foi preciso que os mezes que me-dcaram entre uma 'c outra sessãotrouxessem, com a aggravação dacrise que então se desenhava já, umavisão mais segura dos factos e umjulgamento melhor das coisas; Hojeninguém tem mais duvidas sobre asinceridade com que o governo piei-téótl então essa autorização legislati-va e as razões nue llie sobravam parasemelhante desejo. Os mais extrema-dos opposilores do marechal Hermessó puderam, como derradeiro hostili-zar, fazer a exigência traduzida naemenda que vai ser votada como unidocumento ainda da lisura do proce-dimento do governo.Antes assim. O effeito moral daresolução do Congresso iá está bemnítido na alta cambial e na animaçãoda praça do l\io dc janeiro, neslesdois dias últimos. Não ha melhortberniomclro para a observação dasmelhoras em taes crises do que esseauspicioso movimento de confiança.Assim, o levantamento do empresti-mo, de que fizeram cavallo de bata-lha os inflexíveis censores do gover-110, começa, mesmo antes de effectua-da a operação, a produzir os maiseloqüentes resultados, e isso diz bemda razão com que combatiam a me-,did;
que mandou pagar a divida dc dezenovemil contos á Caixa de Conversão.Que outro qualquer dos nossos políticostivesse ia idéa de aceusar o governo poressa falta, explica-se; mas, que seja oSr. Bulhões quem ouse lembrar esse pec-cado, é caso de se ficar pasmado comtão grande coragem, que, se não sc tra-tasse de personalidade dc tão alto valorintellectual e moral, poderia classificar-sede ihcónsçiencis. y.Dò todos os compromissos assumidospor este- ou por qualquer outro governodo mundo, não ha nenhum, por mais in-defensável que seja, que tenha menos jus-tificação.Foram dezenove mil contos postos pelajanela afora, em 'homenagem ao pyrrho-nismo do Sr. Bulhões, então ministro dafazenda, que, depois de ter mantido, ácusta de sacrifícios inauditos, o cambioa lax-as exageradamente elevadas, fez umultimo esforço a favor da, taxa de 16 di-nheiros para lypo do cambio da Caixa deConversão, que o Congresso foi coagidoa aocjl-ar, como transacção, sem o quenão poderia vencer a resistência do mi-nistro da fazenda na sua má vontadecontra a decretação-da tax-a estável, cujosbenefícios só os sectários de fórmulastheoricas' deixam dc reconhecer. ¦0 que se gastou com áiniaípcntos, comconstrucções, com prolôúgaiíienios ou JHQ-'dificações de traçados dè-tfâtçadas dc fer-ro, com villas militaresfc âj.jerhrias, pôde-ter sido um absurdo o uni'desperdícioimas os armamentos foram recolhidos ásarrectdações, as estradas dc ferro foramou estão sendo consti uidas, as villas mili-tares aquartelam v.irios batalhões do nos-so exercito c as villas operárias eonsti-tuem o lar de centenas dc familias de pro-lçtarios, que todos os dias henulizem ochefe dá Nação que pensou nas sins ne-cessidades c no seu bem estar.Foi-se, talvez, imprevidente, passou-sepor cima da lei, gastaram-se soturnas queo Thesouro não estava habilitado a sup-portar, mas desses erros e desses desper-dicios alguma coisa ficou.Diga-nos o honrado Sr. Bulhões, querepresenta esse sacrifício de 19.000contos?Qual foi a vantagem desse resto de ca-priclib do ministro da fazenda do Sr.Nilo Peçanha?Que compensação teve o paiz com essecolossal ônus, que desvirtuou a própriaessência da Caixa de Conversão, onde sópodia entrar ouro cm espécie e hoje tem,entre os saccos do precioso metal, umvale da responsabilidade do governo de19.000 contos?Não foi feliz o Sr. Bulhões em álludira esse erro colossal c injustificável dasua administração, brilhante sob outrosaspectos, mas une terminou por essedesastre, devido ao seu capricho c ao seuespirito sectário c intransigente.
Chegaram hontem ao porto destacapital, de regresso do Ceará, o cru-zador Barroso e o cruzador-lorpe-deiro Titpy,- pertencentes á divisãode cruzadores, do commando docontra-almirantc Castello Branco.O Sr. ministro da marinha c ochefe do estado-maior da armada es-tiveram a bordo daquellcs navios lo-go depois que elles fundearam.A bordo do cruzador Barroso es-teve tambem o Dr. Herculano dcFreitas, ministro da justiça.,O contraralmi'rántc Castcljp. Bran-co, acompanhado dos ' ca-pitães.' dcfragata César Augusto de Mello eFrancisco de Moura, apresentou-sehontem mesmo ás altas autoridadesnavaes.Telegranimas de Niagará Falls noticiamhoje haver obtido completo exito nas nc-gociações em prol da solução pacifica doconflicto entre os Estados Unidos com oMéxico os delegados, ali reunidos, cmconferência, para este fim.Não temos senão nos ufanar c nos re-gosijar com estas novas, que, confirma-das, serão motivo dc .excepcional júbilo.para as tres nações que tomaram a si atarefa humanitária dc pôr termo a'trai.rcontenda bellica, que sc não justificava denenhum modo, mas qne poderia chegar aresultados das mais dolorosas consequcii-cias..-. Cim seguido o exito a (pie aspirávamos,de pacificar dois povos vizinhos c amigosquese des.ivier.im, conquistamos uma as-cendencia moral extraordinária, não- sóno conceito dos paizes americanos, como110 dos de todo o mundo. K, ao envez"dcsermos nações a policiar, como nos consi-deraram alguns elementos imperialistas dcalguns paizes que alimentavam intuitos detutela sobre nós ou de expansão á nossacusta, passaremos a ser nações que poli-ciam, qiie evitam confliclos, que previnemluclas e que põem termo a guerras"; 1110-slrando aos povos o caminho da ordem, avereda do progresso pacifico, (pie só sol) apaz sc pôde dar o desenvolvimento, sobIodos os aspecto:", dos povos c das nações.Oxalá a marcha das negociações enta-boladas em Niágara Falls sob os auspiciosdo A. B. C.' lenliàm chegado, como lio-ticiou um despacho Iclègrapluco d'ali, .1feliz fim. Auguramos rl"e assim aconteça,não só para a felicidade dos povos ameri-cano c mexicano, como, principalmente,para os dos paizes que se impüzcram ámissão humanitária dc interporem os seusbons officios entre aquelles dois povos,afim dc evitarem hecatombes c desgraçasde uma imprevisivel extensão. Oue sc des-enrolem os snecessos de Ningara Falls dcfórina a serem coroados por um filial sa-tisfatorio para quantos nella tomam parte,eis a grande aspiração dc. que nos fazemosecho, cm 110111c do.s sentimentos de con-fraternidade americana e de solidariedadeuniversal.
A questão do México interessa vi-vãmente Paris, porque há"
```
