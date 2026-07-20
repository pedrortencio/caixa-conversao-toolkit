# Síntese do desenho de mensuração

**Data:** 2026-07-19
**Status:** rascunho do Claude para Pedro, insumo da rodada metodológica. Não decide nada reservado a Pedro pelo gate de `docs/contexto-debate-metodologico-mensuracao.md`; organiza o que já está travado e enuncia o que ainda falta decidir.

## Finalidade

O artefato 1 da rodada (memorando de quantidades históricas) foi preenchido por Pedro e ratificado em `docs/decisoes.md` (2026-07-19). Este documento faz a ponte entre esse memorando e os artefatos 3 a 6 da rodada: consolida a pergunta, separa o núcleo essencial do secundário, lista o que já está fechado (para não relitigar) e formula, como perguntas testáveis, as decisões de desenho que a competição entre instrumentos precisa resolver antes de qualquer classificação em lote.

## 1. Pergunta consolidada

Explicar como os principais jornais trataram a Caixa de Conversão entre 1906 e 1914, identificando variações de saliência, posicionamento e enquadramento econômico-político entre jornais e fases, com atenção à diferença entre posição editorial própria e vozes ou interesses reproduzidos. A escala herdada "ortodoxo vs expansionista" é preservada como hipótese de mensuração a testar, não como recorte imposto (decisoes 2026-07-19, item 1).

Núcleo interpretativo declarado por Pedro (memorando, seções 3 e 7): a tese de trabalho é que jornais defendem interesses de determinados grupos econômicos e regionais ao longo do tempo, e que isso é identificável no debate sobre a Caixa. Esse é o achado que o instrumento precisa ser capaz de produzir ou refutar.

## 2. Hierarquia das dimensões (o que medir, com que ambição)

**Essencial (a dissertação falha sem):**
- saliência por jornal e fase;
- posição sobre a Caixa como instituição e sobre seus instrumentos principais (taxa, conversibilidade, lastro, emissão, valorização do café);
- variação temporal entre jornais e nos marcos de 1906, 1910 e 1914;
- justificativas econômicas principais;
- viradas identificáveis de posição por jornal.

**Desejável, com gate de factibilidade:**
- distinção entre voz editorial própria e discurso de terceiros reproduzido (citações, telegramas, discursos parlamentares, cartas, imprensa estrangeira).

**Secundário ou interpretativo (camadas de validade, análise amostral ou qualitativa):**
- atores e vozes a quem cada jornal dá espaço;
- interesses regionais, setoriais e de grupo representados.

A regra de factibilidade ratificada (decisoes 2026-07-19, item 7): preservar a ambição substantiva, mas reduzir a obrigação métrica. Sob tensão entre refinamento e prazo, prioridade ao conjunto mínimo defensável (saliência, posição, variação temporal, justificativas), com rastreabilidade até a evidência textual e limitações declaradas.

## 3. O que já está travado (não reabrir sem registro)

1. **Corpus.** Censo do acervo digital identificável e recuperável, fotografia datada das fontes da BN (Fase A completa: 11.960 objetos, camada de texto embutido em todo o censo). Descrição oficial e cascata de denominadores K/E/D/S/R/C por jornal-mês pré-registradas (decisoes 2026-07-18).
2. **Censo textual.** Subcorpus recuperado: triagem barata em toda página, transcrição de qualidade só nas candidatas (decisoes 2026-07-17, item 1). Corrige a origem dos 280 sem menção do piloto.
3. **Gate de recall.** Limite inferior unilateral de 95 por cento maior ou igual a 0,90, por jornal e fase (decisoes 2026-07-17, item 2).
4. **Agregação de manifestações e edição-dia.** Dedupe por SHA-256; manifestações reais do mesmo dia produzem uma edição-dia estrita; `n_itens_relevantes` soma sem duplicata, `houve_editorial` por OR, `proeminencia` por máximo; posições substantivas opostas no dia produzem Mixed/Ambiguous (decisoes 2026-07-18, item 1).
5. **Flag cega de origem** (varredura, somente_indice, recuperacao_manual) com margem de refutação de 5 pontos percentuais (decisoes 2026-07-18, item 4).
6. **Portão de 1906.** Todo item do gabarito atribuído a uma de três classes, nenhuma exceção terminal sem aprovação de Pedro (decisoes 2026-07-18, item 3).
7. **Camada de texto embutido (OCR da BN).** Materializada com proveniência byte a byte, custo zero de token; é insumo reversível, não o instrumento de mensuração (decisoes 2026-07-18, camada de texto).

## 4. Decisões de desenho ainda ABERTAS

Cada item é uma pergunta que a competição entre instrumentos (artefatos 3 e 6 da rodada) deve resolver, com a restrição que já a condiciona. A escolha final é de Pedro.

**D1. Instrumento de posição.** A posição sobre a Caixa será medida por escala ordinal -2/+2 (hipótese herdada), por codificação multidimensional de atributos de política (taxa, conversibilidade, emissão, lastro, valorização, efeitos distributivos) ou por extração estruturada de afirmações (ator, alvo, objeto, direção, justificativa, evidência)? Restrição: o instrumento tem que conseguir separar posição sobre a instituição de posição sobre instrumentos específicos (decisoes 2026-07-19, item 6).

**D2. Perenidade de ortodoxia e expansionismo.** As categorias organizam o debate de modo estável entre fases, jornais, gêneros textuais e objetos de política, ou precisam ser substituídas ou complementadas por atributos multidimensionais? Teste explícito antes de adotar a escala como medida principal (decisoes 2026-07-19, item 3). Prioritário e cedo: a factibilidade da dissertação depende de haver ao menos evidência mínima de posicionamento ortodoxo ou expansionista datável (memorando, seção 8).

**D3. Unidade de codificação versus unidade de agregação (ponto de atenção, discutir na próxima sessão).** O memorando (seção 5) diz que a unidade de análise principal são as peças que mencionam a Caixa; a decisão de 2026-07-17 (item 3) travou a edição-dia estrita como unidade principal, com manifestações na camada documental. Leitura provisória de Pedro (2026-07-19): as duas parecem compatíveis, a peça sendo a unidade de observação e codificação e a edição-dia estrita a unidade de agregação e denominador (coerente com a regra de agregação de 2026-07-18). Sem decisão fechada ainda: Pedro marcou para discutir e formalizar na próxima sessão, porque a distinção muda o estimando e o denominador. Nada registrado em `docs/decisoes.md` até essa discussão.

**D4. Gate de voz editorial.** Como testar, barato, na amostra estratificada padrão-ouro, se a distinção entre voz editorial própria e discurso reproduzido é confiável o bastante para virar variável estruturante? Se não for factível em escala, a medida principal passa a ser a tendência do conteúdo publicado, com a avaliação de vozes de terceiros tratada como camada amostral ou qualitativa (decisoes 2026-07-19, itens 4 e 5). O achado central de Pedro (interesses de grupo) depende diretamente do êxito mínimo desse gate.

**D5. OCR da BN versus transcrição LLM.** A camada de texto embutido permite pilotos de dicionário, tópicos e ensaios de triagem lexical sem orçamento. A comparação entre a qualidade do OCR da BN e da transcrição por LLM deixou de ser pressuposto e virou hipótese testável (decisoes 2026-07-18, camada de texto, item 2). Resolver cedo pode rebaixar o teto de custo da Fase B.

**D6. Esquema de justificativas econômicas.** Que categorias de justificativa entram no codebook (câmbio estável para o comércio, defesa do café, medo da inflação, ortodoxia metalista, entre outras) e com que granularidade? Decisão de codebook, reservada a Pedro, informada pela amostra estratificada.

## 5. Estado dos artefatos da rodada

Contra o protocolo de `docs/contexto-debate-metodologico-mensuracao.md` (seção Protocolo da próxima rodada):

1. Memorando de quantidades históricas: **feito** (ratificado 2026-07-19).
2. Revisão estruturada de pesquisas comparáveis (matriz de literatura): **próximo candidato**. Codex pode ser implementador designado (não audita o que implementa).
3. Conjunto de desenhos concorrentes (ao menos duas alternativas além da escala atual): pendente, alimentado por D1.
4. Amostra metodológica estratificada (jornais, fases, gêneros, qualidade, casos claros, negativos, mistos, contraditórios): pendente.
5. Protocolo humano (codebook, dupla codificação, adjudicação, teste protegido): pendente, alimenta D2, D4, D6.
6. Benchmark dos desenhos pelos 12 critérios pré-definidos: pendente.
7. Decisão registrada em `docs/decisoes.md`: fecha a rodada e libera a Fase B substantiva.

## 6. Restrições que o desenho respeita

- Orçamento residual de tokens: aproximadamente R$415 para a Fase B, teto revisável para baixo pela camada de texto embutido.
- Cronograma: cerca de 2 meses para fechar o empírico, com esforço paralelo de leitura e escrita.
- Codificação humana de Pedro: 15 a 20 horas por semana.
- Prioridade às frentes empíricas mínimas necessárias para um trabalho pronto a tempo; o piso é evidência datável de posicionamento ortodoxo ou expansionista por jornal (memorando, seção 8).

## 7. Recomendação de sequência

Ordenada por retorno por token e por dependência, sem gastar API paga até o benchmark:

1. Discutir e formalizar D3 na próxima sessão (unidade de observação versus agregação). Leitura provisória de compatibilidade já registrada; não bloqueia os passos seguintes.
2. Artefato 2 (revisão de pesquisas comparáveis) e artefato 3 (desenhos concorrentes), que juntos instruem D1 e D2.
3. Desenhar a amostra estratificada (artefato 4) reusando o subcorpus e a camada de texto embutido, o que também habilita os pilotos de D4 e D5 a custo baixo.
4. Protocolo humano (artefato 5) e benchmark (artefato 6).
5. Decisão registrada (artefato 7), que libera a Fase B.

O P0 do piloto de 1906 entra como diagnóstico dentro de 4 e 5, não como etapa isolada (reposicionamento proposto em 2026-07-18, a ratificar).

## 8. Hipótese primária ratificada e recomendações de trabalho

**Hipótese de trabalho ratificada por Pedro (2026-07-19):** usar extração estruturada de afirmações por peça como camada primária de representação observável. A escala ortodoxia/expansionismo, os atributos de política e as justificativas econômicas serão vistas derivadas dessa camada. A adoção em escala dependerá de teste barato em amostra do piloto, avaliando confiabilidade, custo, capacidade de reconstruir a escala herdada e utilidade para distinguir voz editorial de discurso reproduzido. Registrada também em `docs/decisoes.md` (2026-07-19). Não é a escolha final do instrumento, reservada ao benchmark e à aprovação de Pedro pelo gate; é o que orienta os artefatos 3 a 6.

Sob essa hipótese, as recomendações de trabalho do Claude por decisão, a testar, não decididas:

- **D1 (instrumento).** Camada de extração de afirmações (ator ou voz, alvo, objeto de política, direção, justificativa, evidência textual) como primária; escala e atributos como vistas. Teste barato, custo zero de token: codificar à mão 10 a 15 peças do piloto nessa estrutura e verificar se a escala se reconstrói e se os atributos variam de forma independente.
- **D2 (perenidade ortodoxia e expansionismo).** Hipótese: perenidade parcial, o eixo segura como ordenação grosseira, mas o conteúdo de política que posiciona muda por fase. Teste barato: casos-âncora, 2 a 3 claros por fase, codificados na escala e nos atributos, verificando se um único eixo os separa de modo consistente entre fases ou se o eixo gira.
- **D4 (voz editorial).** Dividir o gate: (a) editorial versus não-editorial por gênero e seção, como variável estruturante barata; (b) atribuição fina de posição de terceiros como camada amostral ou qualitativa. Teste barato: na amostra dourada, medir a confiabilidade humana da tag de voz e quanto o gênero e a seção sozinhos já recuperam a distinção.
- **D5 (OCR-BN versus transcrição LLM).** Hipótese: OCR-BN grátis basta para a triagem de toda página; a dúvida orçamentária é se a classificação também roda em OCR limpo. Teste barato e de maior alavancagem financeira: nas páginas do piloto com transcrição LLM, rodar o prompt de classificação sobre OCR-BN e sobre a transcrição LLM e comparar os rótulos.
- **D6 (justificativas econômicas).** Não fixar a lista de cima para baixo; deixar emergir como campo codificado na camada de extração sobre a amostra estratificada, agrupar, e Pedro fecha o vocabulário (conjunto enxuto de 6 a 10 códigos). Decisão de codebook, de Pedro.

Todos os testes acima usam o piloto e a camada de texto embutido sem API paga, exceto o de D5, que exige rodar o prompt de classificação em amostra pequena (custo baixo, estimar antes e passar pelo guardrail de estimativa de custo).

Execução: o teste D1 foi feito em papel em 2026-07-19 sobre dois casos reais de O Paiz e PASSOU (a camada reconstrói a escala herdada e expõe o problema de voz reproduzida do memorando, seção 4); o teste D5 foi protocolado com estimativa de custo. Resultados e protocolo em `docs/testes-desenho-mensuracao.md`.
