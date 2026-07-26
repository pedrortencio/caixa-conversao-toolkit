# Manifesto de parecer: como medir posição no subcorpus substantivo

- task_id: 2026-07-25-escolha-instrumento-cobertura
- solicitante: Pedro (a decisão final é dele)
- papel_solicitado: parecerista independente (desenho de mensuração e inferência)
- nivel: critico (instrumento, estimando e base das conclusões históricas)
- gate: PENDENTE. Pedro revisa este manifesto e autoriza antes do despacho.
- orcamento: uma única rodada; ler apenas os arquivos do pacote
- ferramentas: sandbox read-only; não editar nem criar arquivos; o parecer é a resposta final em texto
- workdir: pacote isolado, autossuficiente; os arquivos citados estão na raiz do diretório de trabalho

## Objetivo

A medida pivô do desenho foi respondida em 23/07 e reconfirmada em 25/07 depois
da correção de dois bugs de limpeza: o subcorpus substantivo tem entre **3.054
e 3.758 edições** (IC95 de 2.784 a 4.042), o que equivale a algo entre 204 e
251 horas de leitura a 4 minutos por edição. Pedro dispõe de 15 a 20 horas por
semana dentro de um cronograma de cerca de dois meses para fechar o empírico,
com leitura e escrita correndo em paralelo. **A codificação humana da posição
por censo não cabe.**

A saliência já está resolvida sem isso: sai do censo, é determinística e custou
zero. O que está em aberto é apenas a POSIÇÃO no eixo ortodoxo contra
expansionista, cuja unidade de codificação é a peça relevante.

O relatório de estado de 23/07 enunciou três saídas, reproduzidas no arquivo 02.
Pergunta central: **qual desenho de cobertura da posição preserva a validade do
estimando e sustenta as afirmações por jornal e por fase que o núcleo
interpretativo exige?** Especificamente:

1. As três saídas são realmente alternativas mútuas, ou existe entre elas
   relação de dependência que a formulação esconde? Em particular: alguma delas
   dispensa um padrão-ouro humano em amostra?
2. Que resolução a saída por amostra estratificada entrega de fato? O estimando
   é a distribuição de posições por edição-dia, e as afirmações centrais são por
   jornal (4) e por fase (4), o que implica ao menos 16 células com 5 categorias
   de posição. Uma amostra de 400 a 600 edições sustenta leitura por célula, ou
   só o agregado?
3. A saída híbrida por fase (censo humano em 1906, automação nas fases de maior
   volume) troca de instrumento ao longo do eixo temporal que é justamente o
   objeto da comparação. Isso é confundimento fatal, administrável por
   calibração na sobreposição, ou irrelevante na prática?
4. Se houver extensão automatizada, o parecer deve separar LLM de classificador
   supervisionado treinado na amostra humana: diferem em custo, auditabilidade,
   reprodutibilidade e no ônus da prova que 19/07 colocou sobre a LLM. Qual é
   preferível e sob que evidência?
5. Como dimensionar a amostra humana para servir a dois propósitos ao mesmo
   tempo (estimar posição com precisão declarada E treinar ou validar extensão
   automatizada), sem que o segundo uso contamine o primeiro?
6. Que teste barato, executável antes de gastar token pago, poderia refutar a
   recomendação do parecer?

## Restrições que o parecer deve tratar como dadas

- Estimando e escala continuam sujeitos à rodada metodológica em curso
  (arquivo 04). A hipótese de trabalho ratificada em 19/07 é extração
  estruturada de afirmações por peça como camada primária, com a escala como
  vista derivada, adoção em escala condicionada a teste barato.
- Posição e saliência estão separadas desde 19/07 (D3 resolvido). Saliência é
  decomposta em extensiva, intensidade interna e proeminência.
- Orçamento residual de tokens: cerca de R$ 415. Nenhum lote pago roda antes da
  regressão de 1906.
- O codebook das fases 2 a 4 ainda é esqueleto, e é redação de Pedro.
- A camada de texto embutido (OCR da BN) cobre o censo inteiro a custo zero. O
  teste D5, que compara classificar sobre o OCR contra transcrever por LLM, foi
  protocolado com estimativa de poucos reais e NÃO foi executado.

## Arquivos de contexto (todos na raiz do workdir)

1. `02-contexto-projeto.md` (pergunta, estimando, corpus, guardrails)
2. `03-estado-pos-rotulagem.md` (medida pivô, as três saídas, dívidas e riscos)
3. `04-sintese-desenho-mensuracao.md` (D1 a D6, o que está travado e o que está aberto)
4. `05-desenhos-concorrentes.md` (D-Escala, D-Extração, D-Atributos, D-Humano e o contrato comum de avaliação)
5. `06-memorando-quantidades-historicas.md` (o que Pedro considera essencial, desejável e dispensável)
6. `07-registro-decisoes.md` (decisões fechadas, inclusive as de 19/07, 20/07, 23/07 e 25/07)
7. `08-relatorio-rotulagem-registro.md` (a amostra que produziu a proporção substantiva)

## Evidência potencialmente relevante não fornecida

- O banco SQLite, os PDFs e os manifestos brutos do censo não estão anexados.
  Os agregados relevantes constam de 03 e 08.
- O piloto de 1906 (537 classificações por gemini-1.5-pro, validação humana com
  kappa 0,712 e rho 0,670) não está anexado em dado bruto. Sua auditoria, o P0,
  segue pendente e é insumo dos artefatos 4 e 5, não deste parecer.
- Os relatórios de qualidade de OCR e da rodada 1 do Fightin' Words, de 25/07,
  não estão anexados por não tocarem a pergunta de cobertura da posição.
  Sinalize se a ausência limitar alguma resposta.
- Existe parecer independente do Claude sobre esta mesma questão, congelado com
  hash ANTES deste despacho e não anexado, por desenho (isolamento estrutural de
  pareceres duplos).
- A conversa da sessão que produziu esta pergunta não é fornecida; julgue pelos
  artefatos.

## Critérios de aceite

Parecer fundamentado que responda às seis perguntas, diga explicitamente o que
precisa acontecer ANTES de qualquer decisão de cobertura e o que pode esperar,
e aponte discordâncias com decisões já registradas quando houver. Divergência
fundamentada vale mais que concordância. Se a conclusão for que a pergunta está
mal posta, dizer isso e reformulá-la é resposta aceitável.

## Formato esperado da saída (em português)

Estruture em: fatos observados; inferências; riscos (ranqueados); alternativas;
recomendação; teste que poderia refutar a recomendação.
