# Contexto para o debate científico-metodológico sobre mensuração

**Data de referência:** 18 de julho de 2026

**Status:** contexto canônico para a decisão metodológica anterior à Fase B

## Finalidade e estatuto

Este documento preserva o principal resultado da discussão acadêmica realizada após a conclusão
do censo digital da pesquisa. Ele deve ser lido antes de qualquer decisão sobre processamento
textual seletivo, codebook, instrumento de mensuração, classificação ou agregação.

O objetivo imediato não é escolher o método mais sofisticado em abstrato. É identificar qual
representação e qual instrumento produzem medidas cientificamente defensáveis para as
quantidades históricas que Pedro decidir investigar.

Este texto não escolhe antecipadamente um método. Ele registra uma decisão anterior: o desenho
de mensuração continua aberto e deve ser comparado empiricamente antes da execução em escala.

## Estado da pesquisa em 18 de julho de 2026

A Fase A foi concluída. O projeto preservou uma fotografia datada do acervo digital dos quatro
jornais selecionados entre 1906 e 1914, com 11.960 objetos digitais materializados e controles de
proveniência, integridade e cobertura. Essa completude se refere ao acervo digital identificado e
disponível, não à totalidade ideal de tudo o que circulou historicamente.

O próximo problema é transformar os PDFs em representação textual legível por máquina. Essa
transição não é apenas uma questão de engenharia. OCR, transcrição, segmentação, triagem,
extração e classificação podem determinar quais fenômenos se tornam observáveis na análise.

As decisões de inventário, download, preservação dos PDFs, hashes, proveniência e manutenção de
uma camada bruta reprocessável permanecem válidas. O que precisa ser reaberto é a passagem entre
essa camada documental e as variáveis substantivas da pesquisa.

## A decisão central ainda está aberta

A pergunta empírica geral é como os jornais selecionados discutiram a Caixa de Conversão entre
1906 e 1914, como essa discussão variou entre jornais e períodos e quais dimensões históricas
organizaram o debate. Ainda não está decidido qual quantidade deve representar melhor essa
discussão.

A escala ordinal herdada do piloto pode ser útil, mas não deve definir sozinha o que será visível
no corpus. Antes da classificação em lote, é preciso perguntar, entre outras possibilidades, se o
objeto principal será:

1. apoio ou oposição à Caixa como instituição;
2. preferência por desenhos específicos de política monetária e cambial;
3. posição diante de taxas, conversibilidade, emissão, lastro ou valorização do café;
4. enquadramentos, justificativas e problemas econômicos mobilizados;
5. atores, interesses, regiões e autoridades aos quais o jornal concede voz;
6. posição editorial própria, conteúdo publicado ou a relação entre ambos;
7. saliência e composição temática do debate ao longo do tempo.

Essas quantidades não são equivalentes. Um único score pode comprimir dimensões que variam de
forma independente e pode atribuir ao jornal posições presentes apenas em falas reproduzidas.

## Quatro níveis que não devem ser confundidos

### 1. Construto histórico

É o conceito substantivo que a pesquisa pretende compreender, como posicionamento editorial,
coalizão de ideias, enquadramento de um problema monetário ou composição do debate público. O
construto vem da pergunta histórica e da literatura, não do algoritmo disponível.

### 2. Representação observável

É a forma pela qual o construto aparece nas fontes: passagens, artigos, editoriais, notícias,
citações de terceiros, atores, afirmações, objetos de política, justificativas, temas e relações
entre esses elementos. A representação precisa preservar evidência suficiente para permitir
auditoria e novas interpretações.

### 3. Instrumento de mensuração

É o protocolo que transforma evidência textual em categorias, atributos, scores ou outras
variáveis. Pode combinar codificação humana, regras, modelos supervisionados, LLMs, dicionários,
métodos de escala ou procedimentos de extração estruturada. O instrumento deve ser validado
contra evidência humana e histórica, não apenas contra outro modelo.

### 4. Estimando e agregação

É a quantidade final calculada, como proporções por categoria, diferenças entre jornais, séries
de saliência, distribuição de atributos, mudança temática ou posição média. Unidade de análise,
denominador, ponderação e tratamento de incerteza pertencem a este nível. Não devem ser definidos
apenas pela conveniência do formato produzido pelo modelo.

## Estatuto das escolhas atuais

A escala ordinal de -2 a +2, a unidade edição-dia, o enquadramento como *stance detection*, o uso
de LLM, o DSL e as regras de agregação são hipóteses de trabalho. Nenhuma delas deve ser tratada
como irreversível apenas porque aparece no piloto ou na documentação anterior.

Isso não significa descartar o trabalho já realizado. O piloto fornece casos, erros, categorias
limítrofes e evidência para a comparação. A escala atual deve entrar como uma candidata e pode
permanecer como medida principal, secundária ou análise de sensibilidade se demonstrar validade
superior para a pergunta escolhida.

Também não se deve presumir que todos os métodos concorram para responder à mesma pergunta.
Modelos de tópicos, escalas latentes, dicionários, classificação de stance e extração de
afirmações produzem objetos diferentes. A comparação deve começar pelas quantidades históricas
de interesse e explicitar o papel que cada método pode cumprir.

## Por que a decisão antecede parte da Fase B

Se uma etapa de processamento selecionar, descartar, resumir ou estruturar informação segundo
uma definição substantiva, ela integra o desenho de mensuração e precisa ser discutida antes da
execução em escala.

Podem avançar atividades reversíveis e orientadas à preservação, desde que mantenham ligação com
o PDF original e não eliminem informação relevante:

1. inventário, hashes e metadados documentais;
2. renderização, OCR ou transcrição com proveniência completa;
3. armazenamento de texto integral ou de recortes rastreáveis;
4. segmentação que preserve páginas, coordenadas, ordem e contexto;
5. flags de qualidade, legibilidade e falha;
6. pequenos pilotos estratificados destinados a comparar instrumentos.

Precisam aguardar o debate ou funcionar apenas como pilotos metodológicos:

1. triagem seletiva orientada por uma definição substantiva de relevância;
2. descarte de páginas, passagens ou contexto após a triagem;
3. schema que imponha antecipadamente a escala ou as categorias finais;
4. rótulos de produção e classificação em lote;
5. agregação que transforme conteúdo publicado em posição editorial;
6. escolha definitiva de amostra dourada, métricas e gates de validação.

No desenho atual, a triagem barata de todas as páginas seguida de transcrição seletiva exige uma
definição de recuperação e relevância. Portanto, ela não deve ser considerada totalmente neutra.
Pode ser testada numa amostra, mas sua execução em escala deve ser informada pela decisão sobre
o que precisa ser recuperado e mensurado.

## Famílias de desenhos a comparar

### Escala ordinal de posicionamento

Classifica o conteúdo num contínuo substantivo, como ortodoxo a expansionista. É compacta e
facilita comparação temporal, mas exige demonstrar unidimensionalidade, invariância entre fases
e distinção entre voz editorial e discurso reproduzido.

### Codificação multidimensional de atributos de política

Registra separadamente posições sobre taxa cambial, conversibilidade, emissão, lastro,
valorização, crédito, efeitos distributivos e outros componentes. Reduz compressão conceitual,
mas aumenta complexidade, demanda de codificação e decisões sobre agregação.

### Extração estruturada de afirmações e relações

Registra ator ou voz, alvo, objeto de política, direção da afirmação, justificativa e evidência
textual. Aproxima a variável da fonte e pode permitir diferentes agregações posteriores, mas
exige regras claras de segmentação, vinculação e tratamento de ambiguidades.

### Classificação supervisionada a partir de codificação humana

Aprende categorias definidas e anotadas por pesquisadores. Pode oferecer um benchmark mais
convencional e reproduzível, mas depende da qualidade do codebook, do tamanho da amostra, da
distribuição das classes e da estabilidade temporal do vocabulário.

### Dicionários e métodos de escala

Oferecem transparência ou estimação de dimensões lexicais, mas podem confundir presença de
vocabulário, discurso reportado e posição do jornal. Devem ser avaliados como instrumentos
principais, triangulações ou diagnósticos conforme a pergunta.

### Métodos não supervisionados para temas e enquadramentos

Podem revelar assuntos, associações lexicais e mudanças de atenção sem impor todas as categorias
do pesquisador. São especialmente úteis para exploração e descrição temática, mas tópicos não
devem ser interpretados automaticamente como posições, atores ou mecanismos históricos.

As famílias podem ser combinadas. Uma representação estruturada pode preservar atributos e
evidências, enquanto escalas, classificações ou tópicos funcionam como diferentes vistas sobre a
mesma camada textual.

## Critérios predefinidos de comparação

Antes do benchmark, a próxima rodada deve definir como os desenhos serão comparados. No mínimo:

1. validade de construto e de conteúdo;
2. confiabilidade entre codificadores humanos;
3. estabilidade entre jornais, gêneros textuais e fases históricas;
4. capacidade de distinguir voz editorial de discurso reproduzido;
5. robustez a OCR, ortografia histórica e qualidade documental;
6. rastreabilidade de cada variável até evidência textual verificável;
7. representação de casos mistos, ambíguos, condicionais e contraditórios;
8. interpretabilidade histórica e utilidade para escrita e leitura próxima;
9. sensibilidade a prompts, modelos, pré-processamento, unidade e agregação;
10. quantificação e propagação da incerteza;
11. custo humano, computacional e financeiro;
12. comparabilidade com pesquisas anteriores e possibilidade de reprodução por terceiros.

Concordância entre modelos pode ser uma análise de sensibilidade, mas não substitui validação
humana, validade de construto ou confronto com fontes primárias.

## Protocolo da próxima rodada

A rodada científico-metodológica deverá produzir os seguintes artefatos antes da liberação da
classificação em escala:

1. **Memorando de quantidades históricas:** quais perguntas descritivas ou explicativas o corpus
   deve responder, sem partir de um algoritmo.
2. **Revisão estruturada de pesquisas comparáveis:** matriz contendo pergunta, corpus, unidade,
   construto, representação, método, validação, principais limitações e possibilidade de
   reprodução.
3. **Conjunto de desenhos concorrentes:** especificação operacional de pelo menos duas
   alternativas substantivamente plausíveis, além da escala atual.
4. **Amostra metodológica estratificada:** jornais, fases, gêneros, qualidade documental, casos
   claros, negativos, mistos e contraditórios.
5. **Protocolo humano:** codebook, codificação independente, adjudicação, registro de desacordos
   e conjunto de teste protegido.
6. **Benchmark:** aplicação das alternativas à mesma evidência e comparação pelos critérios
   predefinidos.
7. **Decisão registrada:** escolha do instrumento principal, triangulações, sensibilidades,
   limitações e condições para reprocessamento.

O benchmark não deve premiar apenas a maior concordância numérica. Uma medida pode ser confiável
e ainda não representar adequadamente o fenômeno histórico. Casos de desacordo devem ser lidos
como informação sobre as fronteiras do construto.

## Gate de decisão e responsabilidade

Claude e Codex podem pesquisar métodos, formular alternativas, produzir pareceres independentes,
implementar benchmarks e procurar problemas epistemológicos. Nenhum consenso entre modelos
constitui validade científica.

Pedro mantém a autoridade e a responsabilidade sobre:

1. a pergunta histórica;
2. a definição substantiva do construto;
3. o codebook e o padrão-ouro;
4. a escolha entre os desenhos;
5. a interpretação histórica e as conclusões publicadas.

A classificação substantiva em lote somente será liberada após a competição entre desenhos, a
aprovação explícita de Pedro e o registro da decisão em `docs/decisoes.md`.

## Instrução para novas sessões

Ao receber tarefa relacionada à Fase B, processamento textual, recuperação substantiva,
codebook, classificação, stance, tópicos, DSL ou agregação:

1. ler este documento e os registros metodológicos citados pela tarefa;
2. não tratar a escala ou o pipeline herdado como decisão final;
3. separar fatos observados, inferências, alternativas e evidência necessária;
4. identificar se a etapa proposta é reversível ou incorpora seleção substantiva;
5. propor testes capazes de refutar a recomendação;
6. encaminhar a Pedro decisões que alterem construto, estimando, corpus analítico ou
   interpretação histórica.

Este contexto permanece vigente até ser substituído por decisão metodológica explícita,
registrada e aprovada por Pedro.
