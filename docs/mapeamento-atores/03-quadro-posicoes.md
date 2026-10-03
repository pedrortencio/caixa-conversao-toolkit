# Quadro de posições por objeto e marco (Caixa de Conversão, 1906-1914)

Sessão de 2026-09-30, revista na rodada 3 (leitura detalhada) e na rodada 4 (pendências de 1906, 2026-10-01). Objeto 1 do projeto (mapeamento
descritivo), não estimativa. O quadro registra **posições de atores**, não de jornais: relato de sessão e
secção livre são voz de terceiro, e a posição dos jornais é o objeto 2. As entradas com nome de jornal ("O Paiz (coluna / nota / editorial / artigo sem assinatura)", "Correio da
Manhã (voz do jornal)", "Gazeta de Noticias (resenha do mercado)") registram a voz própria do jornal quando ela
aparece no texto lido; ficam como pista para o objeto 2, não como codificação de posição editorial.

- Dados: `posicoes_por_objeto.csv`, 149 células, 45 atores mais 6 entradas com voz de jornal, uma linha por
  ator, marco e objeto. Cada linha traz o trecho, a fonte (`P:vol:pdf` para os Documentos Parlamentares,
  `I:edição:página` para o OCR-BN), o tipo de voz e o cruzamento imprensa x parlamento.
- **Conferência mecânica das citações** (normalização sem acento nem pontuação, busca literal e, na falta,
  similaridade de janela): **91 literais, 57 aproximadas por OCR (similaridade >= 0,85), 1 rejeitada**
  (Q028, Rodolpho Paixão: o OCR lê "cuntrap'Foâucente"). A rejeitada fica marcada, não corrigida. As 33
  células da rodada 3 (Q107-Q139) e as 10 da rodada 4 (Q140-Q149) passaram todas.
- Marcos: `dados/leitura/marcos_cronologicos.csv`; objetos alinhados a `dados/leitura/debates.csv`.
- Detalhe e contexto de cada célula: `00-vencidos-primeira-linha.md`, `01-vencidos-segunda-linha.md`,
  `02-defensores-e-marcos-posteriores.md`; o que a leitura integral mudou está em `04-leitura-detalhada.md`; as
  pendências de 1906 e a voz de O Paiz estão em `05-pendencias-1906.md`.

Legenda: **+** a favor, **-** contra, **=** aceita com condição ou como transação, número = taxa em
dinheiros por mil-réis, **?** sem evidência.

## A. Criação, 1906 (M001-M008)

| Ator (UF) | Voto | Mecanismo | Taxa | Padrão (quebra) | Fundos de 1899 / lastro |
|---|---|---|---|---|---|
| David Campista (MG), relator | sim | + (Caixa contra a alta, fundos contra a baixa; "complemento" de Murtinho) | 15 = "taxa corrente"; estabilidade acima do nível | quebra só com conversão imediata; "Nem eu" | incorporar; operar câmbio com o fundo de garantia |
| Altino Arantes (SP) | sim | + (rumo à circulação metálica) | 15 | ? | ? |
| Adolpho Gordo (SP) | sim | + (contra a alta; café) | 15 "reflecte a situação" | nega quebra definitiva | ? |
| Alberto Sarmento (SP) | sim | + | 15 como ponto de partida | quebra aceitável | ? ; taxa só por lei do Congresso |
| Galeão Carvalhal (SP) | sim | + | 15 | ? | ? |
| Rodolpho Paixão | sim | + | 15 "muito acceitavel" | quebra futura, a 15 | incorporar os três fundos |
| Rodrigues Peixoto | sim | + | ? | ? | substitutivo de agências do café |
| Barros Franco (RJ) | sim | + ("emancipação economica"; Taubaté) | 15 | ? | ? |
| Alcindo Guanabara (DF) | **sim em 14/09 (confirmado na imagem)**; ausente em 08/10 | + no princípio (fixidez "necessaria"), - no aparelho; "perigoso" após as emendas de 24/09 | **12** | quebra definitiva a 12 | fundos de 1899 num fundo de conversão; contra o fundo de garantia em câmbio |
| Urbano Santos (MA), relator no Senado | sim | + | 15 transitória | nega quebra | fundo de garantia p/ estabilidade |
| Moniz Freire (ES), Senado | sim | + (emendas "em apoio do plano") | 15 | ? | ? |
| Rui Barbosa (BA), Senado | sim | + (voto; reunião com Campista) | ? | ? | ? |
| Serzedelo Corrêa (MT) | não | - ("manco"; só com substituição do papel); aceita o emendado em nov. | - fora de hora: 15 "instavel" agora, 12 "expoliação"; 15 "depressiva" como padrão definitivo | quebra definitiva futura, "taxa sufficientemente alta" (24 no voto em separado), com conversão total | resgate basta; valorização da produção e do café antes da conversão |
| Paula Ramos (SC) | não | - ("não fixa e nem converte") | - | ? | desconfia do lastro do café |
| Cornélio da Fonseca (PE) | não | - (adesão a Paula Ramos) | ? | ? | ? |
| Barbosa Lima (DF) | não em 14/09; ausente em 08/10 | - (programa Murtinho; a Caixa quebra o padrão "de facto") | - (par; ironiza "estavel a 3") | - ("deshonestidade", 24/08 e 26/09) | contra lastro por empréstimo |
| Affonso Costa (PE) | não | - (inflação ou inócuo) | - (>= 18 11/16) | - | ? ; contra a valorização do café |
| Paulino de Souza (RJ) | não | - | - | - (quebra jurídica, lei de 1846) | resgate ao par |
| Wenceslau Escobar (RS) | não | - | ? | + quebra ao valor real | ? |
| Arthur Orlando (PE) | não em 14/09 | - (sem se opor ao café) | ? | - (inconstitucional) | Banco do Brasil operando câmbio |
| Antunes Maciel (RS) | não | - | ? | ? | - desvio dos fundos |
| Anísio de Abreu (PI), Senado | ausente | - ("negativa radical") | - | - (fé dos contratos) | ? |

## B. Operação, 1907-1909 (M009-M013)

| Ator | Objeto | Posição | Fonte |
|---|---|---|---|
| Serzedelo | mecanismo | + estabilização (1907-1908); em 1907 diz que a Caixa evita também a baixa, com o depósito e o fundo de garantia | O Paiz 08210, 08665 |
| Serzedelo | emissão | resgate para compensar a emissão da Caixa (parecer de 1908) | O Paiz 08665 |
| Serzedelo | alfândega | contra cobrar a 15 (relator da receita, 1908); em 1909, direitos 100% em ouro contra a perda fiscal | O Paiz 08687; CM 02872 |
| Barbosa Lima | alfândega | cobrar a 15, "depois da creação da caixa" (M013) | O Paiz 08678 |
| Paula Ramos (com Adolpho Gordo) | alfândega | tarifa móvel, igualar o ouro da Caixa e da Alfândega | CP 15768 |
| Custódio Coelho | taxa | passa a aceitar 15 (M007), **na voz de coluna satírica de O Paiz** | O Paiz 08204 |
| David Campista (ex-ministro) | lastro | depósito da Caixa como encaixe de 50% do papel (1909) | O Paiz 09189 |
| O Paiz (voz própria) | taxa; lastro | 1907: o Banco "recalca" o câmbio a 15 contra a tendência de alta; 1909: o depósito "responde pela emissão", contra Campista | O Paiz 08204; 09189 |

## C. Elevação da taxa e do limite, 1910 (M014-M019)

| Ator (UF) | Taxa | Limite | Fundos de 1899 | Competência | Mecanismo | Voto / papel |
|---|---|---|---|---|---|---|
| Nilo Peçanha / L. de Bulhões (governo) | 16 em 28/04; **18 em 08/11/1910**; baixistas = "detentores do café" | sem limite | restaurar fundo de garantia; depósito é do depositante ("fetichistas do metal amarello") | Executivo eleva | ± emissor a 100% sim; a taxa fixa de 1906 foi "violencia" contra a valorização | duas mensagens |
| Rui Barbosa (BA), plataforma civilista | 15 ("que não se altere") | emitir além do limite | conservar os fundos | ? | + | citado na imprensa e por Carvalhal |
| Francisco Salles (ministro, nov.) | 16 | ? | ? | ? | + | informação à comissão |
| Barbosa Lima (DF), relator | 16 como transação | manter 20; ampliar a 15 seria o ideal dos "valorizadores á rebours" | restaurar | ? | - "irreductivel" | parecer 29/04 |
| Paula Ramos (SC) | 16 como transação; contra o substitutivo | manter 20 | ? | ? | - "respeitar a lei" | não em 18/12 |
| Galeão Carvalhal (SP) | 15, "não estamos pleiteando o cambio baixo"; "proteccionista da producção" | 40 a 15 (substitutivo) | devolver à lei de 1899, mas "resgate basta" ("maravilhas do fundo de garantia") | ? | + (cláusula do Convênio de Taubaté) | substitutivo 28/04; M016 |
| David Campista (MG), fora do governo | 15 e ampliar a emissão (segundo Carvalhal) | ampliar | ? | ? | + | voz de terceiro |
| Alcindo Guanabara (DF), Comissão de Finanças | 15, "a unica taxa possivel" | ? | ironiza a restauração do fundo de garantia ("sortilegio") | ? | - ao projeto (16) | requer adiamento, 23/11 |
| Cincinato Braga (SP) | 15 agora; alta "degráo por degráo" até 27 | 40 (até 60) | escada: 20 mi -> 16, 25 -> 17, 30 -> 18... | lei (fundo como termômetro) | + ("cambio estavel") | M017 |
| Josino de Araujo (MG) | 15 | ilimitado ou 60 | ? | ? | + | emendas |
| Lindolpho Camara (RN) | 15 | ? | ? | ? | + | |
| Rodolpho Paixão | 15, aceita 16 "vencido" | ? | ? | ? | + | |
| Affonso Costa (PE) | 18 e ressarcir portadores | ? | contra a confusão dos fundos | ? | - ("inimigo que fui") | emenda |
| Felisbello Freire (SE) | 18 | sem limite | restaurar | Executivo | + | emenda |
| Pandiá Calógeras (MG) | 18 (expoente do mercado; queda a 16 "por determinação official") | ? | 3 milhões p/ o Banco do Brasil | ? | - extinguir ("condensador de crises") | emenda |
| Honorio Gurgel (DF) | 17, contra fixar | ? | ? | ? | - | emenda |
| José Bezerra (PE) | contra a tese de Affonso Costa | ? | ? | ? | ? | |
| João Luiz Alves (ES), relator no Senado | 16 "optimista" | 60 | restaurar | ? | + | parecer |
| Azeredo (MT) | 17 (aceita 16) | contra 60 ("quasi [...] quebra do padrão") | ? | ? | ? | vencido em parte |
| Severino Vieira (BA) | "expressão real"; adiar | ? | ? | ? | - | pede adiamento |
| Joaquim Murtinho (MT), carta | alta gradual (plataforma de Hermes) | contra 60 ("interesse de classe" baixista) | ? | ? | - ao uso baixista; a Caixa serve para "graduar a elevação do cambio" | carta lida por Azeredo, 27/12 |
| Moniz Freire (ES) | valorização | ? | ? | ? | cético ("sem funcção" sem empréstimos) | |
| Gonçalves Ferreira (PE), Senado | ? | contra 60 | ? | ? | - desde 1906 | vencido |

Resultado: Câmara aprova 16, limite de 60 milhões e fundos restaurados (135 x 10, 18/12/1910); Senado
aprova sem emendas em 29/12/1910.

## D. 1911-1913 (M020-M022)

| Ator | Objeto | Posição | Fonte |
|---|---|---|---|
| Francisco Salles (ministro) | taxa | executa 16, notas "carimbadas" | Gazeta 1911_00006 |
| Rivadavia Corrêa (ministro) | depósitos | intocáveis, "fé dos contractos" (relato do barão de Ibirocahy; os "depositos em Londres" podem não ser o ouro da Caixa) | CP 1913_17979 |
| Carlos Peixoto, Miguel Calmon | emissão / depósitos | contra emissão; contestam Rivadavia; Calmon: emissão "contraria a organização da Caixa" | CP 1913_17979 |
| Augusto Ramos | emissão | a favor, com o "cambio estavel como está" | CP 1913_17979 |
| Francisco Glycério, Alcindo | taxa (retrospecto) | "a taxa verdadeira, que era a de 12"; Alcindo: "Apoiado!" | CM 1913_05446; O Paiz 1913_10674 |
| Pinheiro Machado | taxa (retrospecto) | "a taxa de 15, que era a taxa verdadeira" | CM 1913_05446; O Paiz 1913_10674 |
| Pinheiro Machado | memória de 1906 | contra a Caixa estavam "a acção directa do governo" e "o Jornal do Commercio, o Paiz, o Correio da Manhã e outros" (imagem; no CM, espaço em branco no lugar de "o Paiz"); Murtinho "infenso" | O Paiz 1913_10674 |

## E. Emissão e suspensão do troco, 1914 (M023-M026)

| Ator (UF) | Emissão de papel-moeda | Suspensão do troco | Fonte |
|---|---|---|---|
| Antônio Carlos (MG), relator vencido (voto em separado) | - (letras do Tesouro a 6%) | culpa os bancos estrangeiros pela corrida à Caixa | O Paiz 1914_10907 |
| O Paiz (editorial) | + (projeto do Senado, "o unico alvitre pratico") | defende os bancos estrangeiros | O Paiz 1914_10907 |
| Carlos Peixoto, Homero Baptista, Manoel Borba, T. Moreira, F. Pacheco | - (assinam com o relator) | ? | O Paiz 1914_10907 |
| Cincinato Braga (SP) | + ("attitude de S. Paulo") | ? | O Paiz 1914_10910 |
| Rivadavia Corrêa (ministro) | - pessoal, cede ao governo | ? | O Paiz 1914_10897 |
| Urbano Santos | + por solidariedade ao governo | ? | O Paiz 1914_10897 |
| Martim Francisco (SP) | - ("calote") | - (honra de depositário) | O Paiz 1914_10900; Gazeta 1914_00345 |
| Serzedelo (MT) | = contra em doutrina, aceita por necessidade; a Caixa minorou o dano (ago.) | - ("Suspender a retirada de ouro é deshonesto"; e "trambolho", deixar esgotar; conferido na imagem) | O Paiz 1914_10901; Gazeta 1914_00345 |
| Pandiá Calógeras | - ("crime") | - (não impedir retiradas) | CP 1914_18331 |
| Leopoldo de Bulhões (Senado) | - (prefere bilhetes do Tesouro) | - ("illegal") | CM 1914_05644 |
| Rui Barbosa (Senado) | - (só relato indireto) | ? | CM 1914_05644; O Paiz 1914_10901 |
| Sabino Barroso (ministro) | ? | usa ouro da Caixa p/ o funding | CM 1914_05769 |

## O que o quadro mostra

1. **O objeto do desacordo muda a cada marco, e muitas posições mudam com ele.** Em 1906 a disputa é o
   padrão (quebra ou não) e o próprio mecanismo; em 1910, o número da taxa e o tamanho do limite; em 1914,
   emissão e troco. Serzedelo, Barbosa Lima, Paula Ramos e Affonso Costa se opõem à criação e depois
   defendem a lei de 1906 contra a ampliação, ou pedem taxa mais alta. Em várias linhas isso é mudança de
   objeto, não de lado. Uma escala única de pró ou contra a Caixa leria como incoerência o que é
   deslocamento de objeto.
2. **A oposição de 1906 não é um bloco doutrinário.** Convivem os valorizadores do par ou quase par
   (Affonso Costa, Paulino, Anísio, Barbosa Lima com Murtinho), os que aceitam a quebra mas rejeitam este
   aparelho (Escobar, Orlando), a objeção de oportunidade (Serzedelo: a reforma certa, a quebra definitiva
   com conversão total, só depois de dois anos de "reconstrucção" e a taxa mais alta) e a objeção
   institucional aos fundos (Antunes Maciel). Alcindo é o caso-limite: queria *mais* fixidez que o projeto,
   com quebra definitiva a 12, votou sim no princípio e só se voltou contra depois das emendas de 24/09. A
   leitura integral reforça que o eixo valorização do café x estabilidade não separa os campos: Serzedelo,
   vencido, põe a valorização "especialmente o café" no seu programa. O que se repete no voto é a geografia
   política: Pernambuco rosista, Rio Grande federalista, Rodrigues Alves Filho. **Hipótese, não achado.** A
   memória de Pinheiro Machado em 1913 (governo Rodrigues Alves e parte da imprensa contra; Murtinho
   "infenso"; articulação com Tibiriçá, Campos Sales e Rui) é evidência de terceiro, retrospectiva e
   interessada, que vai no mesmo sentido.
3. **Em 1910 o eixo vira 15 contra alta, com 16 como transação.** Pelos 15: paulistas e mineiros ligados à
   produção (Carvalhal, Cincinato, Josino, Paixão), mais Lindolpho Camara. Pela alta: Affonso Costa e
   Felisbello (18), Calógeras (18 e extinção), Honorio Gurgel e Azeredo (17). O 16 é aceito como transação
   por opositores de 1906 (Barbosa Lima, Paula Ramos), pelo relator do Senado e, segundo Azeredo, pela
   bancada paulista, "uma vez que não podem conseguir a conservação da taxa de 15". Isso bate com o eixo do
   CLAUDE.md: valorização contra estabilidade a taxa nova.
4. **Reviravoltas documentadas**: Custódio Coelho (contra a quebra, passa a sustentar 15, mas a fonte é
   uma coluna satírica de O Paiz); Moniz Freire (sim em 1906, cético em 1910); Cincinato Braga ("inimigo",
   reconhece os serviços em 1910, pede emissão em 1914); Campista (relator em 1906 com a alta gradual até
   27, encaixe de 50% em 1909, pela permanência de 15 em 1910 segundo Carvalhal); Rivadavia (contra a
   emissão, cede em 1914); Serzedelo (em 1906 a Caixa não age na baixa; em 1907, para o público português,
   age com o depósito e o fundo de garantia); Cincinato (vota sim em 14/09/1906 sem discursar e, em abril de
   1910, ele mesmo "diz que foi inimigo da Caixa"; não há texto de 1906 que documente a inimizade); Rui
   Barbosa (o Correio da Manhã lhe atribui "radicaes divergencias" em outubro de 1906; vota sim em 26/11). **Não é reviravolta**: Alcindo, que a leitura integral mostra coerente
   como estabilizador a taxa baixa (12 em 1906, 15 "a unica taxa possivel" em 1910, 12 em 1913).
5. **Em 1914 a oposição à suspensão tem duas razões, mas elas não separam pessoas** (M025): honra de
   depositário (Martim Francisco, Bulhões, Calógeras) e desejo de ver a Caixa acabar. Serzedelo usa as duas
   na mesma fala ("Suspender a retirada de ouro é deshonesto" e "A Caixa é um grande trambolho"). O
   argumento do depósito como propriedade dos portadores já aparece em 1909 na voz de O Paiz e em 1910 em
   Bulhões, que o usa para defender a retirada de ouro pelo Banco do Brasil. São Paulo se divide: Cincinato
   a favor da emissão, Martim Francisco contra.
6. **Leitura integral: os defensores da Caixa não se descrevem como baixistas.** Campista quer "a taxa
   corrente" e a estabilidade como bem em si; Cincinato quer "a alta cambial [...] degráo por degráo",
   amarrada ao fundo de garantia. O que os separa dos altistas não é o destino (27), é o ritmo e a garantia
   metálica. Isso reforça o ponto 1: codificar "pró-Caixa" como "pró-câmbio baixo" seria erro de construto.
7. **Cada lado nomeia uma geografia social.** Campista: resistência "na Capital", da "rua da Alfandega ás
   regiões do officialismo". Cincinato: "classes camponezas" produtoras de ouro contra "classes urbanas"
   consumidoras. Calógeras: 95% de assalariados contra 5% que lucram com câmbio baixo. Os dois últimos
   disputam a imagem da abolição ("nova campanha abolicionista" x "os escravos são, hoje, os fazendeiros").
   São enquadramentos de interesse explícitos, candidatos a código de "interesses invocados" nas fichas.
   A leitura integral acrescenta três: Barbosa Lima (1906) atribui aos "agrarios" o desejo de "cambio
   baixo" e de "regimen colonial"; Bulhões (1910) chama os baixistas de "detentores do café" que represam
   as letras e diz que a moeda depreciada divide o país em "dous grupos"; Murtinho (1910) fala em
   "interesse de classe" dos que pregam a valorização e querem a desvalorização. Do outro lado, Carvalhal:
   "não estamos pleiteando o cambio baixo", mas "o cambio a 15 é proteccionista da producção nacional".
8. **Rui Barbosa em 1910 fica com os 15 e a ampliação**, ao lado dos paulistas, enquanto o governo Nilo e
   Bulhões pedem 16 e depois 18.

## Limites e pendências

- Os Documentos Parlamentares da base cobrem só 1906 e 1910. Para 1907-1909 e 1911-1914 o quadro depende
  de resumos de imprensa (voz de terceiro).
- **Resolvido na rodada 2**: voto de Alcindo (sim, imagem vol. 1 p. 345); atribuição de Serzedelo na
  Gazeta de 12/12/1914 (correta, imagem); mensagens de 1910 (16 em abril, 18 em 08/11/1910; "18 1/4" era a
  taxa do Banco do Brasil); Rui Barbosa (varredura refeita, 196 páginas).
- **Resolvido na rodada 3**: a citação de Murtinho por Barbosa Lima aparece nas duas datas (24/08, em resumo
  da Gazeta; 26/09, literal nos anais); a divergência voto x discursos de Alcindo (aceitação do princípio);
  a lista de jornais contrários em 1906 segundo Pinheiro Machado (imagem de O Paiz e do CM).
- **Resolvido na rodada 4** (`05-pendencias-1906.md`): a acusação a Alcindo pela baixa do câmbio (Correio da
  Manhã de 21/09 e Gazeta de 24 a 27/09/1906); a renúncia de Murtinho ao Senado, de outubro de 1906 e motivada
  pela Caixa; o "inimigo da Caixa" de Cincinato, que é autodescrição de 1910; a fala direta de Rui em agosto de
  1914, que é contra o decreto do feriado por razão de competência, não sobre a emissão; a entrevista de
  Bulhões de agosto de 1914 ("Ella deve ser fiel depositaria").
- Ainda a conferir: o espaço em branco no CM de 1913 onde O Paiz imprime "o Paiz"; o conteúdo da inimizade
  de Cincinato em 1906; fala de Rui sobre a emissão em 1914; o discurso de Bulhões "num banquete politico"
  contra Taubaté em 1906 e a mensagem de Rodrigues Alves, citados pelo Correio da Manhã; quem escrevia a série
  de O Paiz contra a Caixa.
- Leitura integral feita para Campista, Calógeras, Cincinato (rodada 2) e, na rodada 3, Serzedelo (30/08,
  13/09 e 29/11/1906), Alcindo (28/08, 25/09/1906, 23/11/1910), Barbosa Lima (26/09/1906 e parecer de 1910),
  Bulhões (duas exposições de 1910), Galeão Carvalhal (22/11/1910), carta de Murtinho (1910) e nove peças de
  imprensa de 1907-1914. Os demais discursos foram lidos por abertura, fecho e frases com palavras-chave.
- **Pista para o objeto 2 (não codificada):** a voz própria de O Paiz aparece contra a compressão do câmbio
  a 15 (1907), pela integridade do depósito (1909), incluída por Pinheiro Machado entre os opositores de 1906
  (1913) e a favor da emissão (1914). Rodada 4: entre 24/09 e 10/11/1906 a primeira página de O Paiz publica
  uma série de artigos sem assinatura contra a Caixa (dois conferidos na imagem), e o Correio da Manhã de
  21/09/1906 escreve contra a Caixa e contra Taubaté. É inventário de voz, não medida de posição editorial.
- Divergência de data: o parecer da receita de Serzedelo citado em 1910 como "de 1907" sai em O Paiz de
  24/06/1908.
- UF não verificada: Rodolpho Paixão, Rodrigues Peixoto, Custódio Coelho.
- Atores com muitas menções e sem posição extraída: Pinheiro Machado fora de 1913, Nilo Peçanha além das
  mensagens, Wenceslau Braz.
- A busca na imprensa só alcança páginas que nomeiam a Caixa; discursos sobre câmbio sem o nome ficam fora.
