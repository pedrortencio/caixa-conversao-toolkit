# Manifesto de parecer: incorporação do índice bndigital ao censo e tratamento das lacunas

- task_id: 2026-07-18-lacunas-enumeracao-censo
- solicitante: Pedro (a decisão final é dele)
- papel_solicitado: parecerista independente (metodologia de corpus)
- nivel: critico (corpus e denominador da série)
- gate: aprovação de Pedro registrada na sessão de 18/07/2026 antes do despacho
- orcamento: uma única rodada; ler apenas os arquivos do pacote
- ferramentas: sandbox read-only; não editar nem criar arquivos; o parecer é a resposta final em texto
- workdir: pacote isolado, autossuficiente; os arquivos citados estão na raiz do diretório de trabalho

## Objetivo

A Fase A construiu o censo 1906-1914 por varredura número a número do host
estático da BN (8.889 edições baixadas; relatório no arquivo 03). Depois do
encerramento, verificou-se que as páginas públicas de acervo da BN trazem
uma enumeração oficial, por ano, de cada edição digitalizada, apontando para
o mesmo host (arquivo 04). Essa segunda fonte é superconjunto estrito do
censo obtido: contém 3.092 edições a mais (quase todas do Correio da Manhã
1907-1914 e da Gazeta de Notícias 1914), lista alguns arquivos que o host
não serve (404 confirmado em amostra), apresenta anomalias de rotulagem
(números repetidos sob rótulos de ano distintos no CM; números espúrios
isolados) e não cobre trechos que faltam também no host (Gazeta 1913
inteira, fim de 1907 de O Paiz, parte de 1908 do Correio Paulistano,
buracos da Gazeta 1910-1912). Além disso, 4 edições usadas no piloto de
1906 não existem nem no host nem no índice (3 delas são edições duplas de
um mesmo número, baixadas manualmente no DocReader durante o piloto), o que
hoje faz a regressão do gabarito 1906 reprovar em 3 dos 4 jornais.

Pergunta central: como o censo e o corpus devem incorporar essa segunda
fonte e tratar as lacunas e anomalias, preservando a validade do
denominador e a comparabilidade entre jornais? Especificamente:

1. A recuperação guiada pelo índice (baixar as 3.092 edições do diff, com
   registro positivo de sucesso e ausência por item) deve acontecer antes
   da Fase B? Sob que protocolo e com que registro de proveniência, dado
   que a extração do índice exige navegador (Cloudflare barra requests)?
2. Como o denominador e a cascata do censo devem tratar: (a) as lacunas
   reais de digitalização (Gazeta 1913; O Paiz fim de 1907; CP 1908;
   Gazeta 1910-12); (b) as 4 edições do piloto ausentes do host e do
   índice; (c) itens listados no índice mas ausentes do host?
3. Que regras precisam de pré-registro antes da Fase B? Em particular: a
   agregação de dias com mais de uma edição (duplas A/B), o tratamento das
   sobreposições de rótulo de ano do CM (mesmos números sob 1907 e 1909,
   por exemplo) e a publicação de taxas de cobertura por jornal-mês.
4. O critério do portão da regressão 1906 (hits do piloto são subconjunto
   do censo) deve mudar diante de edições que a BN não serve mais? Para
   qual formulação?
5. Que riscos metodológicos a incorporação cria (viés de disponibilidade,
   comparabilidade entre jornais, proveniência de extração manual) e como
   mitigá-los?

## Arquivos de contexto (todos na raiz do workdir)

1. 02-contexto-projeto.md (pergunta de pesquisa, estimando, corpus e guardrails do projeto)
2. 03-relatorio-cobertura-censo.md (cobertura da varredura por jornal-ano e regressão 1906)
3. 04-indice-bndigital-fatos.md (a segunda fonte: proveniência, validação ao vivo, diff por célula e anomalias)
4. 05-registro-decisoes.md (decisões metodológicas já fechadas, inclusive as três reservadas de 17/07)

## Evidência potencialmente relevante não fornecida

- O spec v2 completo da base do corpus (44 tabelas, cascata do censo,
  identidade edição-dia por masthead) não está anexado, por tamanho; os
  arquivos 03 e 04 resumem o que dele importa aqui. Sinalize se a ausência
  limitar alguma resposta.
- Os manifestos CSV brutos (varredura e índice, dezenas de milhares de
  linhas) não estão anexados; os agregados por (bib, ano) constam de 03 e 04.
- Os PDFs baixados e o banco SQLite não estão anexados.
- Existe parecer independente do Claude sobre a mesma questão, congelado
  com hash ANTES deste despacho e não anexado, por desenho (isolamento
  estrutural de pareceres duplos).
- A discussão da sessão que levantou os fatos não é fornecida; julgue pelos
  artefatos.

## Critérios de aceite

Parecer fundamentado que responda às cinco perguntas, diga explicitamente o
que deve preceder a Fase B e o que pode esperar, e aponte discordâncias com
fatos ou decisões já registradas quando houver. Divergência fundamentada
vale mais que concordância.

## Formato esperado da saída (em português)

Estruture em: fatos observados; inferências; riscos (ranqueados);
alternativas; recomendação; teste que poderia refutar a recomendação.
