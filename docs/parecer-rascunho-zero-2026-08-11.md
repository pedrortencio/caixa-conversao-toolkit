# Parecer sobre o rascunho zero da dissertação

**Feito em:** 2026-08-11. **Objeto:** `dissertacao/`, commit `38ad24e`, sete
capítulos, apêndice, 429 linhas de LaTeX substantivo. **Estatuto:** leitura
crítica do texto, não auditoria da base. Os números do rascunho foram conferidos
contra `docs/MAPA-DO-PROJETO.md` (atualizado em 2026-08-03), `main.toc` e
`docs/relatorio-credor-externo-no-debate.md`.

## Veredito

O rascunho é bom e a arquitetura está certa. Ele faz a coisa mais difícil de um
texto nesse estágio, que é sustentar uma tese metodológica em vez de encadear
paráfrases da bibliografia. A decisão de organizar o debate por objetos de
política, taxa, limite, fundos, competência, agência e custódia, em vez de por
um eixo favorável contra contrário, é o que separa a dissertação de uma
replicação de Torelli, e ela é executada com consistência do capítulo 2 à
conclusão.

O que impede o texto de ir à qualificação como está não é a interpretação. São
quatro coisas: a ausência total de citação direta das fontes, um punhado de
erros aritméticos e de referência legal, a numeração de capítulos deslocada e
uma seção de método que descreve o instrumento computacional abaixo do que o
projeto de fato mede.

## 1. O problema mais sério: nenhuma citação verbatim

Não há uma única citação direta dos quatro jornais em todo o rascunho. Cada
afirmação empírica dos capítulos 3 a 5 é paráfrase, e os marcadores
`\fonteaconferir` apontam justamente para as passagens que precisariam estar
entre aspas.

Isso tem três consequências, e nenhuma é de estilo.

A primeira é que o guardrail central do objeto 1, a conferência mecânica de
citação por substring normalizada, não tem sobre o que operar. O instrumento
existe, `pipeline/analise/verifica_citacoes.py` e
`pipeline/analise/confere_citacao_imagem.py`, mas o texto não o exercita.

A segunda é que um leitor não consegue distinguir o que foi lido na imagem do
que foi reconstruído a partir do OCR ou herdado da monografia. Essa é
exatamente a distinção que o projeto mediu e documentou como perigosa: a coluna
`texto` interpola, sangra e, em ao menos um caso, entrega artigo diferente.

A terceira é que a promessa da introdução, um mapeamento descritivo com citação
verbatim rastreável, fica sem demonstração. O rascunho declara o método e não o
mostra funcionando.

**Recomendação.** Antes da versão de qualificação, promover de oito a doze
passagens âncora por capítulo empírico a citação direta, conferidas na imagem,
com página, coluna, seção e autoria. Escolher as que já sustentam afirmações
fortes: o editorial do `Correio da Manhã` de 11 de março de 1906, a coluna
`Política Republicana` de 29 de agosto, o artigo `Melhorar pelo fogo` de agosto
de 1907, o editorial de `O Paiz` de 14 de maio de 1910, `Minas e o câmbio` de 29
de maio de 1910, o editorial da `Gazeta de Notícias` de 17 de janeiro de 1912 e
as falas de Martim Francisco e Serzedello Corrêa em dezembro de 1914. São sete
peças que carregam sozinhas a espinha argumentativa.

Vale notar que o relatório do credor externo mantém `conferido_na_imagem` em
`nao` nas 36 citações. A cautela do rascunho em não citar é coerente com esse
estado, mas a solução é conferir, não continuar parafraseando.

## 2. Erros numéricos e de referência legal

Estes são concretos e conferíveis.

**2.1. O teto de 1910 não triplicou em mil-réis.** Capítulo 4, seção `Fundos,
limite e novo desenho legal`: "O novo teto triplicou a cifra em mil-réis da lei
original". De 320 mil para 900 mil contos são 2,81 vezes. A triplicação exata
está em libras, de 20 para 60 milhões, porque a taxa mudou de 15 para 16 pence
no mesmo ato. A frase afirma o contrário do que é verdade. Corrigir para algo
como "quase triplicou a cifra em mil-réis e triplicou exatamente o equivalente
em libras, porque a taxa subiu junto".

**2.2. A tabela do apêndice soma 468 e está rotulada como 453.** O texto diz que
"453 receberam classificação humana", e a tabela `Registro documental das peças
classificadas` lista 239, 169, 45 e mais 15 "sem preenchimento", somando 468. O
`MAPA-DO-PROJETO.md` é claro: "468 itens `keep`, 453 rotulados em três classes".
Ou a legenda passa a se referir às 468 peças, ou a linha das 15 sai da tabela e
vai para o texto. Tabela é o que a banca copia fora de contexto.

**2.3. Lei ou Decreto n. 1.575.** O capítulo 3 escreve "A Lei n. 1.575, de 6 de
dezembro", e o capítulo 5 repete "da Lei n. 1.575". A bibliografia, o
`mapa-reaproveitamento.md` e o LEGIN da Câmara registram "Decreto n. 1.575". As
duas formas circulam, porque a Coleção de Leis do período nomeia como decreto
atos do Congresso sancionados pelo Executivo, enquanto a historiografia costuma
citar como lei. Escolher uma forma, aplicá-la aos três atos, 1.575, 2.357 e
2.862, e explicar a divergência em nota na primeira ocorrência. Hoje o texto usa
"Lei" para 1906 e "Decreto" para 1910 e 1914, o que sugere uma diferença de
natureza jurídica que não existe.

**2.4. A aritmética da Alfândega não fecha com o enquadramento.** Capítulo 4:
"A libra valia no mercado cerca de 16 mil-réis, mas a Alfândega calculava
determinados pagamentos por um padrão de 20 mil-réis", apresentado como questão
sobre "quem se beneficiava do padrão legal". Mas 16 mil-réis por libra é
exatamente 15 pence, a taxa da Caixa, e 20 mil-réis por libra é exatamente 12
pence. O padrão legal de 27 pence corresponde a 8$889 por libra. O número de 20
mil-réis não é o par legal, é a taxa de 12 pence, que nunca foi adotada. Ou o
número está errado, ou o enquadramento está. Reconstruir da fonte antes de
interpretar, porque o argumento do capítulo depende disso.

**2.5. A divergência de 15 contra 20 milhões de libras tem uma pista
aritmética.** O capítulo 3 corretamente se recusa a explicar a diferença antes
da conferência. Vale registrar a restrição que a aritmética impõe: 320 mil
contos equivalem a 20 milhões de libras a 15 pence e a 16 milhões a 12 pence.
Chegar a 15 milhões exigiria 11,25 pence, taxa que ninguém propôs. Portanto a
explicação mais provável não é uma taxa diferente, e sim uma cifra em contos
diferente na versão de julho, ou erro de transcrição. Isso reduz o espaço de
busca da conferência.

## 3. A numeração dos capítulos está deslocada em uma unidade

`\chapter{Introdução}` produz "Capítulo 1". O `main.toc` confirma: Introdução é
1, Fontes é 2, padrão-ouro é 3, criação é 4, experiência é 5, crise é 6,
conclusão é 7. O roteiro da introdução diz "O Capítulo 1 apresenta a imprensa
como fonte", apontando para a própria introdução, e as cinco remissões estão
todas erradas por um.

Conserto: `\chapter*{Introdução}` com `\addcontentsline`, e o mesmo para a
conclusão, ou `\label`/`\ref` em vez de números literais. A segunda opção é mais
segura porque sobrevive à migração para a classe da FFLCH.

## 4. A seção de método subdeclara o instrumento

O capítulo 1 diz: "Modelos de linguagem podem auxiliar essa catalogação". Não
nomeia serviço, modelo, versão, data de execução, temperatura nem versão de
prompt. A regra do projeto e a da escrita acadêmica exigem todos esses itens e
proíbem a formulação genérica.

Mais grave, o rascunho não mostra os ativos metodológicos que o projeto
efetivamente tem:

- a conferência mecânica de citação por substring normalizada, com rejeição e
  nunca correção da linha que não casa;
- a taxa de rejeição por anotador como métrica publicada do lote, medida em 6,7
  por cento no Claude e 5,7 por cento no Codex no piloto de catalogação;
- a catalogação das mesmas janelas por dois anotadores com o mesmo prompt, o que
  torna a concordância medida e não presumida;
- a conferência por dupla leitura de imagem, com os vereditos `estavel`,
  `instavel` e `divergente_do_ocr`, e a ressalva de que duas leituras do mesmo
  modelo não são dois anotadores.

Hoje a seção é defensiva, explica o que a pesquisa não fará com LLM. Ela deveria
ser afirmativa, porque o protocolo de conferência é mais rigoroso do que o que a
maioria das dissertações de história econômica com fontes seriais apresenta. É a
seção que a banca vai atacar primeiro, e ela está armada abaixo da sua
capacidade real.

Uma ressalva na direção oposta. O eixo de registro documental, substantivo
contra operacional contra incidental, é processamento que estrutura informação
segundo o construto. Publicar suas contagens no apêndice antes do gate
metodológico é defensável porque o rascunho declara o erro não medido, mas a
declaração precisa estar dentro da tabela, na forma de uma coluna de
proveniência humana ou algorítmica, e não apenas na prosa em volta.

## 5. A afirmação sobre o credor externo está qualitativa e é medida

Capítulo 5 e conclusão dizem que os Rothschild aparecem "com frequência" no
acervo mas "raramente muito próximo" da Caixa, e que o credor é "frequentemente"
designado por perífrase. Isso está medido: nas 8.331 páginas que mencionam a
Caixa, 170 nomeiam um Rothschild, 456 usam perífrase ou cargo, 214 usam
perífrase de confiança alta, 38 têm as duas coisas e 418 designam sem nomear.

Colocar os números, com o denominador explícito e a ressalva de que o ruído de
OCR afeta a recuperação de nome próprio mais do que a de expressão comum. É um
dos achados mais originais do rascunho e está escrito como impressão.

## 6. Tensão entre os capítulos 2 e 3 sobre os 12 pence

O capítulo 2 diz, numa frase só, que "a taxa de 12 pence apareceu em propostas
ligadas à defesa do café e nas emendas de Alcindo Guanabara". O capítulo 3
desfaz cuidadosamente essa associação, mostrando que Alcindo e Serzedello
propunham 12 por razões metalistas, com conversibilidade mais ampla, e não por
interesse cafeeiro. O capítulo 2 pré-carrega o leitor exatamente com a
conflação que o capítulo 3 depois desmonta. Separar as duas origens dos 12
pence já no capítulo 2.

Na mesma seção, a frase "A Caixa, portanto, não foi criada a 12 pence" está sem
destinatário. Ela corrige alguém, provavelmente a literatura ou a monografia,
mas o leitor não sabe quem. Nomear o erro corrigido ou cortar a frase.

## 7. Registro e autorreferência

Não há travessões no rascunho. Conferi com busca por `---`, em-dash e en-dash
nos seis arquivos de capítulo, no apêndice e na configuração. Zero ocorrências.

Duas questões pendentes de registro.

A primeira é a pessoa do texto. O rascunho é uniformemente impessoal, "esta
dissertação investiga", "a pesquisa distingue", "o texto falará em voz
publicada". Isso é defensável para a FFLCH, mas contraria a convenção do projeto
e precisa ser uma decisão registrada, não uma deriva. Se ficar impessoal, ficar
impessoal em tudo, inclusive nas notas de trabalho.

A segunda não depende da primeira. As remissões à monografia estão em terceira
pessoa distanciada: "utilizado na monografia anterior sobre 1905 e 1906", "o
texto acima deriva da monografia, p. 29 a 31", "vem do corpus da monografia". É
trabalho seu. Escrever "minha monografia de graduação". Essa é a correção que
vale independentemente do registro escolhido para o corpo do texto.

## 8. Itens menores

- `beachhanlon2023` está na bibliografia e não é citado em lugar nenhum. Ou
  entra no capítulo 1, onde é o apoio óbvio para os argumentos sobre construção
  de corpus e ruído de OCR, ou sai.
- "pence" contra "dinheiros". O rascunho usa pence em todo lugar; o codebook de
  fases usa dinheiros. Ambos são uso de época. Unificar e registrar, porque
  codebook e dissertação não podem chamar a mesma unidade por nomes diferentes.
- A `Gazeta de Notícias` em 1913. O capítulo 1 diz que ela "não possui objetos
  recuperados para 1913 no censo atual". O `MAPA-DO-PROJETO.md` afirma coisa mais
  forte e já verificada: "a Gazeta de 1913 não existe em acervo nenhum". A versão
  forte muda o estatuto epistêmico da lacuna, de limite da recuperação deste
  projeto para ausência do registro. Usar a versão forte, com a fonte da
  verificação.
- A introdução diz "11.960 objetos digitais, com 117.703 páginas dotadas de
  texto". O total é 117.705, com duas vazias registradas positivamente. Dar os
  dois números, como fazem o capítulo 1 e o apêndice, porque o registro positivo
  da ausência é parte do método.
- `lapuente2015`, `torelli2007` e `francolago2011` carregam `note` admitindo
  metadados incompletos. Já está na lista de pendências, sem urgência.

## 9. O que está bom e não deve ser mexido

- O trio voz enunciadora, ato de publicação e apropriação editorial é o núcleo
  intelectual do trabalho e está formulado com precisão no capítulo 1 e aplicado
  sem escorregões nos capítulos empíricos. É o que impede o erro que o campo
  comete o tempo todo.
- O parágrafo do compromisso de 1906, no fim do capítulo 3, "Fixou 15, mas não
  revogou formalmente o padrão de 27", é o melhor parágrafo do rascunho e está
  publicável como está.
- A seção sobre incompatibilidade de compromissos, no capítulo 5, é contribuição
  analítica própria e se declara como tal, sem atribuir à literatura uma fórmula
  que ela não tem. Boa prática, manter a declaração.
- O caso de Martim Francisco e Serzedello Corrêa, mesmo voto por razões opostas,
  é a melhor evidência isolada de toda a tese metodológica. Considerar promovê-lo
  à introdução como caso emblemático, porque ele justifica em dez linhas a recusa
  de uma escala única.
- Manter a lacuna da `Gazeta` em 1913 como lacuna, sem imputação, aparece três
  vezes com formulação consistente. Correto.
- O aparato de marcadores editoriais é incomum e honesto. Manter `\rascunhotrue`
  até a qualificação inclusive, e virar para `\rascunhofalse` só no depósito.

## 10. Ordem de prioridade

1. Conferir na imagem e converter em citação direta as sete peças âncora
   listadas na seção 1.
2. Corrigir os cinco itens numéricos e legais da seção 2.
3. Consertar a numeração dos capítulos.
4. Reescrever a subseção computacional do capítulo 1 declarando serviço, modelo,
   versão, data, temperatura, versão de prompt, conferência de citação e taxa de
   rejeição por anotador.
5. Inserir os números do credor externo no capítulo 5 e na conclusão.
6. Separar as duas origens dos 12 pence no capítulo 2.
7. Corrigir as remissões à monografia e decidir o registro de pessoa.

## 11. Estado da execução, 2026-08-11

Portão de 1906 rodado antes de qualquer chamada paga: **APROVADO**, exit 0, 426
itens de gabarito, 422 reproduzidos, 4 exceções ratificadas por Pedro, zero
inexplicados.

Aplicado no rascunho, com `verificar.ps1` passando e zero referências
indefinidas:

- item 3, numeração. Introdução e conclusão passaram a `\chapter*` com entrada
  no sumário. Os capítulos numerados vão de 1 a 5 e as cinco remissões do
  roteiro da introdução ficaram corretas sem edição do texto.
- item 2.1, a triplicação do teto de 1910, corrigida para 2,81 vezes em mil-réis
  e três vezes exatas em libras, com a razão da diferença explicitada.
- item 2.2, a tabela do apêndice, recomposta para as 468 peças, com subtotal de
  453 classificadas, as 15 sem preenchimento em linha própria e coluna de origem
  da classificação.
- item 2.3, padronização em Decreto n. 1.575, n. 2.357 e n. 2.862, com nota de
  rodapé na primeira ocorrência explicando que a historiografia cita o de 1906
  como Lei n. 1.575 e que não há dois atos. Decisão reversível.
- item 2.4, a Alfândega. Não corrigido, porque não tem conserto sem a fonte.
  Convertido em `\fonteaconferir` que registra a aritmética: 16 mil-réis por
  libra é 15 pence, 20 mil-réis é 12 pence, o par legal de 27 pence é 8$889.
- item 2.5, a divergência de 15 contra 20 milhões de libras, com a restrição
  aritmética acrescentada ao marcador para estreitar a busca.
- item 4, subseção nova `O instrumento computacional e suas guardas`, declarando
  prompt versionado 0.1.0 e `hash` 61030ebfd7b93485, os dois anotadores sobre as
  48 janelas, a conferência mecânica por substring, as taxas de rejeição de 6,7
  e 5,7 por cento, a camada de imagem com `claude-sonnet-5` e protocolo 1.0.0, a
  ancoragem no OCR antes da comparação entre leituras, os vereditos 23, 11 e 2,
  e as duas ressalvas sobre erro correlacionado.
- item 5, os números do credor externo no capítulo 5 e na conclusão, 170 páginas
  que nomeiam contra 456 que usam perífrase e 418 que designam sem nomear, sobre
  as 8.331, com a ressalva de que o ruído de OCR atinge nome próprio mais que
  expressão comum e a razão é piso, não medida.
- item 6, as duas origens dos 12 pence separadas no capítulo 2, com remissão por
  `\ref` ao capítulo da criação.
- item 7a, as quatro remissões à monografia passadas a primeira pessoa.

### Achado novo, gerado pela execução do item 4

O `docs/relatorio-piloto-catalogacao.md` registra as versões de interface dos
dois anotadores, 2.1.220 e 0.145.0, e o `hash` do prompt, mas **não registra o
identificador de modelo nem a temperatura**. A regra do projeto exige serviço,
modelo, versão exata e prompt no output de toda anotação. Recusei-me a inventar
os campos e deixei `\lacuna` no capítulo 1. Ou os campos são recuperados dos
registros da rodada, ou a rodada é declarada não reprodutível nesse aspecto
antes que qualquer contagem derivada dela entre no texto.

### Pendente

- item 1, a conferência na imagem das sete peças âncora. Piloto amostral de duas
  peças despachado, com teto de US$ 1,00, para medir custo real e viabilidade de
  localização.
- item 7b, o registro de pessoa do corpo do texto, que é decisão de Pedro.

### Obstáculo medido para o item 1

A base **não resolve data para objeto**: `edition_days` tem 67 linhas para
11.960 objetos digitais. Localizar "Correio da Manhã de 11 de março de 1906" não
é consulta, é busca no texto de `C:\dados-caixa\texto_embutido`. O custo de API
da conferência é trivial, cerca de US$ 0,025 por página; o gargalo do item 1 é a
localização, não o gasto.

## 12. Resultado do piloto pago, 2026-08-11

Duas peças, dez passagens, quatro chamadas de visão. **Custo real US$ 0,08**,
contra teto de US$ 1,00, ou US$ 0,04 por página nas duas leituras. Vereditos: 6
`estavel`, 3 `instavel`, 1 `leitura_ausente`.

### 12.1. Correção de data, aplicada

O editorial da `Gazeta de Notícias` sobre as retiradas é de **17 de janeiro de
1912**, objeto `per103730_1912_00017` p. 1, e não de 15, como o rascunho, o
parecer e as notas de pendência registravam. Conferi de forma independente: o
masthead de `00016` traz terça-feira 16 de janeiro, o de `00018` traz 18 de
janeiro, e 17 de janeiro de 1912 caiu numa quarta-feira, o que o masthead de
`00017` confirma. O objeto de 15 de janeiro não contém a peça, só o boletim de
rotina da Caixa. Corrigido nos capítulos 4 e 5 e nas notas.

### 12.2. Um furo no protocolo, encontrado no piloto

Em `cm1906-aventura`, as duas leituras acrescentaram `cidas aventuras.`, vinte
caracteres **ausentes de todo o OCR da página**. O veredito saiu `estavel`,
porque as duas leituras concordam, e concordam porque o erro é correlacionado. É
exatamente o modo de falha que o docstring do módulo prevê, agora observado.

A causa é estrutural: `omissoes_vs_ocr` mede o que a leitura tirou, e nada mede o
que ela acrescentou. Duas correções possíveis, ambas mudança de instrumento e
portanto decisão de Pedro: acrescentar coluna `adicoes_vs_ocr` simétrica, ou
rebaixar automaticamente para `instavel` toda passagem com
`legibilidade=parcial`, que foi o único sinal disponível neste caso.

Há também vazamento da âncora para dentro da transcrição. Em `cm1906-quebra`, a
segunda leitura devolveu lixo do OCR, inclusive os hífens de quebra de linha que
o prompt manda juntar. As três `instavel` são todas desse tipo.

Em contrapartida, a guarda de sangria funcionou. `gn1912-sangria` é um span que
atravessa a coluna e cola o fim do editorial numa matéria sobre o Paraguai. As
duas leituras recusaram em vez de inventar frase plausível.

### 12.3. Defeito no script, dados restaurados e verificados

`confere_citacao_imagem.py` deriva o nome dos arquivos de passe com nome fixo, de
modo que `--saida` troca só o arquivo reconciliado. As dez linhas do piloto foram
apensadas aos passes do relatório do credor externo. Foram separadas e
restauradas, e **conferi a restauração de forma independente**: 36 linhas em cada
um dos três arquivos, distribuição 23 `estavel`, 11 `instavel` e 2
`divergente_do_ocr`, idêntica à de 03/08, e zero identificadores de âncora
vazados. Nada se perdeu.

Contorno sem tocar no instrumento: apontar `--saida` para um diretório próprio.
Conserto de fundo, que é mudança de instrumento: derivar o nome do passe do nome
do manifesto.

### 12.4. Recuperação de data por masthead, medida

Percentual de objetos cuja página 1 entrega a data ao parser, e cujo ano confere:

| jornal | objetos | data no OCR | ano confere |
|---|---|---|---|
| Correio da Manhã | 3.238 | 64,4% | 51,5% |
| O Paiz | 3.086 | 62,9% | 50,4% |
| Correio Paulistano | 3.128 | 43,2% | 31,3% |
| Gazeta de Notícias | 2.505 | 33,3% | 21,8% |

Localizar por data é moeda ao ar, e pior na Gazeta. O caminho robusto é
aritmético: o número do objeto é o número da edição e é contíguo no tempo, então
uma âncora vizinha legível resolve por interpolação. Vale construir esse
utilitário determinístico antes de seguir, porque ele serve ao resto da
dissertação e derruba as cinco localizações restantes para poucos minutos cada.

### 12.5. Extensão às cinco peças restantes

US$ 0,20 a US$ 0,28 de API, três ordens de grandeza abaixo do orçamento. O tempo
é de uma a três horas, quase todo em localização e na curadoria das passagens,
que exige ler a peça e não se automatiza.

Nenhuma das dez citações entra na dissertação antes de Pedro olhar a página. O
que a camada compra é a ordem de leitura.

## 13. Os três itens aprovados em 11/08

Suíte inteira verde ao fim: **442 testes passando, 47 subtests**, contra 422
antes. `verificar.ps1` passando, zero travessões, zero referências indefinidas.

### 13.1. Utilitário de objeto por data

`pipeline/triagem/objeto_por_data.py`, 20 testes novos. Duas decisões de desenho
saíram de defeito medido, não de preferência.

O parser lê **dia e mês, e ignora o ano impresso**, ao contrário de
`parse_observed_date` em `pipeline/base/carrega_piloto.py`, que exige o ano e
está fixado em 1906. O ano é a parte menos confiável do masthead e é a única
desnecessária, porque já está no nome do objeto: `per103730_1912_00017` traz
`dé 1913` e `per103730_1912_00016` traz `de i91S`.

A resolução usa a **maior cadeia crescente** entre número e data, e não as
leituras isoladas. Medi que 16,4% das datas lidas em O Paiz 1910 são falsas,
19,5% na Gazeta e 31,3% no Correio Paulistano, porque o padrão casa com data
citada dentro de matéria que caiu nas primeiras linhas. A cadeia descarta o
ruído por construção, sem limiar arbitrário.

A guarda: a aritmética só vale se o intervalo de números bater com o de dias.
Quando não bate, houve dia sem edição no meio e a saída é `incerto`, com o
candidato e a razão da dúvida, nunca resposta errada com cara de certa.

Resultado sobre as peças âncora: seis das sete resolvem, quatro por masthead
direto e duas por vizinhos. O Paiz de 14 de maio de 1910 fica `incerto`, com
âncoras em 13 e 21 de maio, seis edições para oito dias. O candidato
`per178691_1910_09354` é quase certamente correto, mas vira conferência de
masthead de uma página só.

Achei e consertei um bug meu no caminho: eu ordenava as âncoras por número do
objeto e as escolhia por comparação de data, o que devolvia a última em ordem de
número em vez da mais próxima em data. Com 141 datas legíveis no ano, isso
escolhia 5 de fevereiro e 30 de dezembro para cercar 14 de maio.

### 13.2. Guarda de adição, protocolo 1.1.0

Feito, testado e registrado em `docs/decisoes.md`. Ver a seção 12.2 acima para o
defeito e a entrada de decisão para a especificação. O ponto que exige ação de
Pedro está em 13.4.

### 13.3. Registro de pessoa

Corpo do texto passado a primeira pessoa do singular nas passagens em que Pedro
é o agente: introdução, capítulo de método, capítulo 3, capítulo 4 e conclusão.
Não converti as passagens em que "o projeto" e "o texto" designam o projeto de
lei de 1906 ou o editorial do jornal, nem as passivas em que o agente não é o
autor. A conversão foi de autorreferência, não de estilo geral.

### 13.4. Correção do que escrevi na seção 12.2

A seção 12.2 acima trata as quatro `estendida` como texto acrescentado pelo
modelo. **Isso está errado em três dos quatro casos.** Reexecutar a leitura de
imagem não resolveria, porque o erro é correlacionado e a terceira leitura
tenderia a repetir a adição. A checagem que resolve é outra, determinística e de
custo zero: se a adição está impressa, alguma versão dela existe no OCR da
página inteira, ainda que corrompida.

| citação | adição | casa na página | leitura |
|---|---|---|---|
| `op1912-quebra` | `Que diriam de tal acto?` | 1,00 | âncora curta |
| `cm1914-posse` | `Barroso` | 1,00 | âncora curta |
| `op1910-concordata` | `tantos abalos,` | 0,92 | âncora curta |
| `cm1913-murtinho` | quatro palavras, leitura 2 | 0,56 | inconclusivo |
| `cm1906-aventura` | `desconhecidas aventuras.` | ausente | invenção |

A leitura de imagem estava certa nos três primeiros. O que estava curto era o
`citacao_verbatim` curado, e a leitura leu além da âncora. As citações do corpo
do `relatorio-credor-externo-no-debate.md` estão substantivamente corretas, e o
relatório **não precisa da correção de conteúdo que eu havia anunciado**. O
único caso de texto inexistente na página é `cm1906-aventura`, do piloto, que
não está em relatório nenhum.

A guarda continua valendo. Ela separa corretamente um grupo que precisa de olho,
e pegou uma invenção real em cinco sinalizações. O que o nome `estendida` sugere,
invenção, é a causa minoritária: a dominante é âncora curta. Por isso a passagem
`estendida` não deve ser descartada, e sim mandada para a checagem de página.

Implementado como `casamento_na_pagina`, com quatro testes. Registrado em
`docs/decisoes.md` como entrada nova, que é append-only, e não como emenda da
anterior.

### 13.5. Pendente

Estender `citacao_verbatim` das três citações de âncora curta para cobrir a
passagem impressa, como já foi feito em 03/08 com cinco citações curtas demais.
Feito isso, a conferência de substring volta a passar sobre o span maior e o
veredito sai de `estendida`. É curadoria de manifesto publicado e fica com Pedro.
