# Design: contexto para o debate metodologico de mensuracao

**Data:** 18 de julho de 2026

**Status:** aprovado por Pedro, aguardando revisao da especificacao antes da implementacao

## Objetivo

Criar um documento canonico que preserve o principal resultado da discussao academica recente:
o corpus documental esta completo, mas ainda nao foi decidido o que exatamente sera mensurado
nem qual desenho de mensuracao deve ser adotado. A escala ordinal de posicionamento, a tarefa de
*stance detection*, o DSL e as regras de agregacao permanecem candidatos, nao premissas
irreversiveis.

O contexto orientara a proxima rodada de debate cientifico-metodologico e impedira que a Fase B
transforme escolhas provisoriais em fatos consumados por meio da triagem, transcricao seletiva,
segmentacao, classificacao ou estrutura dos outputs.

## Artefatos

1. Criar `docs/contexto-debate-metodologico-mensuracao.md` como fonte canonica da decisao
   pendente.
2. Adicionar o documento a `AGENTS.md`, na lista de documentos canonicos, com instrucao para
   consulta em tarefas sobre Fase B, codebook, instrumento de mensuracao e classificacao.
3. Adicionar a `CLAUDE.md` um alerta operacional curto: nenhuma classificacao substantiva em
   lote deve ser implementada ou executada antes da competicao entre desenhos e da aprovacao de
   Pedro.

Nao serao alterados nesta entrega o codebook, os prompts, o schema, o codigo do pipeline nem o
registro historico das decisoes anteriores.

## Estrutura do documento canonico

### 1. Estado da pesquisa

Registrar a conclusao da Fase A, o censo do acervo digital e o inicio da transicao para uma
representacao legivel por maquina.

### 2. Decisao central pendente

Separar quatro objetos que nao devem ser confundidos:

1. construto historico de interesse;
2. representacao observavel nas fontes;
3. instrumento de mensuracao;
4. estimador ou procedimento de agregacao.

### 3. Estatuto das escolhas atuais

Explicitar que a escala `-2/+2`, a unidade edicao-dia, o enquadramento como *stance detection*, o
uso de LLM e o DSL sao hipoteses de trabalho sujeitas a comparacao. Decisoes de inventario,
proveniencia e preservacao do corpus continuam validas e nao dependem da escolha do instrumento.

### 4. Familias candidatas

Apresentar, sem escolher antecipadamente uma vencedora:

1. escala ordinal de posicionamento;
2. codificacao multidimensional de atributos de politica;
3. extracao estruturada de atores, vozes, alvos, afirmacoes e justificativas;
4. classificacao supervisionada a partir de codificacao humana;
5. metodos de escala ou dicionario;
6. metodos nao supervisionados para temas e enquadramentos, como instrumentos exploratorios.

O documento distinguira metodos que respondem a perguntas diferentes, evitando uma competicao
baseada apenas em sofisticacao aparente.

### 5. Criterios de comparacao

Os desenhos serao avaliados por:

1. validade de construto;
2. confiabilidade entre codificadores;
3. estabilidade entre jornais e fases historicas;
4. robustez a OCR e qualidade documental;
5. rastreabilidade ate a evidencia textual;
6. interpretabilidade historica;
7. sensibilidade a modelagem e agregacao;
8. custo computacional e humano;
9. capacidade de representar casos mistos, ambiguos e contraditorios.

### 6. Fronteira antes da Fase B

O contexto diferenciara:

- atividades reversiveis e de preservacao, que podem avancar, como inventario, hashes, OCR ou
  transcricao com proveniencia completa, armazenamento de texto e flags de qualidade;
- atividades que dependem da decisao metodologica, como triagem seletiva orientada pelo
  construto, descarte de contexto, schema classificatorio, rotulos de producao e agregacao final.

Se o processamento implicar perda seletiva de informacao, ele nao sera tratado como neutro.

### 7. Protocolo da proxima rodada

A rodada cientifico-metodologica devera produzir:

1. definicao das quantidades historicas de interesse sem partir de um algoritmo;
2. revisao estruturada de pesquisas comparaveis;
3. matriz entre pergunta, construto, unidade, metodo, validacao e limitacoes;
4. desenhos concorrentes aplicados a uma amostra estratificada;
5. comparacao empirica segundo criterios predefinidos;
6. escolha humana do instrumento principal, triangulacoes e sensibilidades;
7. registro da decisao antes da execucao em escala.

### 8. Gate de decisao

Nenhum consenso entre modelos substitui validade. Claude e Codex podem produzir pareceres
independentes, mas Pedro aprova a definicao substantiva, o codebook, o padrao-ouro e o desenho
final. A classificacao em lote somente sera liberada depois dessa aprovacao e do registro em
`docs/decisoes.md`.

## Requisitos de redacao

- Texto em portugues, autocontido e legivel por uma nova sessao sem acesso a esta conversa.
- Tom de memorando metodologico, nao de decisao final sobre o metodo.
- Distincao explicita entre fatos observados, hipoteses de trabalho e decisoes pendentes.
- Nenhuma alegacao de que um metodo e superior sem revisao ou teste comparativo.
- Nenhum travessao no texto.

## Verificacao

1. Procurar marcadores incompletos, contradicoes e linguagem que transforme candidatos em
   escolhas definitivas.
2. Conferir coerencia com `AGENTS.md`, `CLAUDE.md`, `docs/decisoes.md`,
   `docs/codebook-fases.md` e o handoff vigente.
3. Confirmar que os links adicionados apontam para o documento correto.
4. Revisar o diff para garantir que nenhum arquivo de pipeline ou dado foi alterado.

## Criterios de aceite

A entrega sera aceita quando uma nova sessao do Codex ou Claude conseguir identificar, sem a
conversa original:

1. por que o desenho de mensuracao precisa ser discutido antes da Fase B;
2. quais escolhas permanecem provisoriais;
3. quais atividades podem prosseguir sem antecipar a mensuracao;
4. quais familias e criterios entrarao na competicao;
5. quem tem autoridade para aprovar a decisao final.
