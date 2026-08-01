# Camada de texto corrigido dos Documentos Parlamentares

Data: 2026-08-01. Aprovação de escopo por Pedro na conversa de origem.

## Objetivo

Produzir uma camada derivada, legível para leitura e pesquisa, dos dois volumes
digitalizados de *Caixa de Conversão* de 1906 e 1910. A camada melhora a forma do
OCR embutido sem modernizar a ortografia histórica, sem alterar silenciosamente o
conteúdo e sem substituir a extração bruta já preservada.

## Fontes e vínculo de proveniência

As fontes são `dados/raw_pdf/caixa_conversao_v1.pdf` e
`dados/raw_pdf/caixa_conversao_v2.pdf`. O insumo textual imediato são os JSONL
brutos em
`dados/texto_embutido/fontes_parlamentares/caixa_conversao/`, com um registro por
página física e hashes do PDF e do texto extraído.

Cada registro corrigido deve preservar:

1. nome e SHA-256 do PDF de origem;
2. volume e número da página física do PDF;
3. SHA-256 do texto bruto da página;
4. SHA-256 do texto corrigido;
5. versão do protocolo de correção;
6. contagem e tipos das transformações aplicadas.

O texto bruto permanece imutável e continua sendo a referência para citação e
auditoria.

## Escopo da correção

A correção é conservadora e orientada à leitura. Ela pode:

1. normalizar finais de linha para `LF`;
2. remover espaços horizontais repetidos e espaços indevidos antes de pontuação;
3. rejuntar palavras divididas por hífen no fim da linha quando a evidência formal
   indicar hifenização tipográfica;
4. rejuntar linhas que pertencem ao mesmo parágrafo;
5. preservar quebras que sinalizem título, sessão, lista, tabela, fala parlamentar
   ou mudança de parágrafo;
6. corrigir símbolos espúrios e padrões lexicais recorrentes apenas por regras
   explícitas de alta confiança;
7. aplicar correções lexicais somente a partir de uma lista permitida versionada,
   com forma bruta, forma corrigida, justificativa e escopo.

A correção não pode:

1. modernizar grafias como `ph`, `th`, `y`, consoantes dobradas ou acentuação de
   época;
2. reescrever sintaxe, pontuação autoral ou estilo;
3. completar palavras incertas por plausibilidade contextual;
4. fundir páginas ou perder a correspondência com a página física;
5. remover passagens consideradas ruído sem registrar sua origem;
6. usar correção livre por LLM no corpus integral;
7. transformar a camada em instrumento de classificação substantiva.

Casos duvidosos permanecem como no OCR bruto. A prioridade é evitar falsos
consertos, mesmo que alguns erros permaneçam visíveis.

## Abordagem técnica

Uma rotina reproduzível em `pipeline/base/` recebe os JSONL brutos e produz a
camada corrigida. As transformações são funções puras, aplicadas em ordem fixa:

1. limpeza estrutural de espaços e caracteres;
2. identificação de linhas especiais que não podem ser fundidas;
3. dehifenização conservadora;
4. reconstrução de parágrafos;
5. aplicação da lista permitida de correções lexicais;
6. cálculo de métricas, hashes e registro das operações.

A dehifenização deve exigir letras dos dois lados da quebra. Não se aplica a
travessias de página, números, sinais matemáticos, palavras com hífen lexical
reconhecível ou linhas classificadas como tabela, título ou lista. Quando a regra
não puder decidir com segurança, o hífen e a quebra são preservados.

A reconstrução de parágrafos deve usar apenas sinais formais, como terminação da
linha, indentação recuperável, caixa tipográfica, marcadores e padrão de fala
parlamentar. Ela não deve inferir estrutura pelo sentido econômico do trecho.

## Produtos

A saída fica em
`dados/texto_corrigido/fontes_parlamentares/caixa_conversao/`, separada da camada
bruta, com:

1. `caixa_conversao_v1_texto_leitura.txt` e
   `caixa_conversao_v2_texto_leitura.txt`, com marcadores de página;
2. `caixa_conversao_v1_paginas_corrigidas.jsonl` e
   `caixa_conversao_v2_paginas_corrigidas.jsonl`, com um registro por página;
3. `manifesto_correcao_paginas.csv`, com hashes, métricas e status;
4. `correcoes_lexicais_permitidas.csv`, lista explícita das substituições
   recorrentes autorizadas;
5. `relatorio_qualidade_correcao.json`, com cobertura, transformações e resultados
   da validação.

Os TXT são produtos de leitura. Os JSONL e manifestos são os produtos de pesquisa
e auditoria. Citações acadêmicas devem continuar sendo conferidas no PDF.

## Tratamento de falhas

Toda página do insumo gera um registro de saída. Os status são:

1. `ok`, correção executada;
2. `unchanged`, página não vazia sem transformação;
3. `empty`, página bruta vazia;
4. `error`, falha registrada com classe e mensagem.

Uma falha numa página não permite omiti-la. A execução deve terminar com erro se
as contagens de páginas diferirem do insumo ou se houver quebra de proveniência.

## Validação

A implementação precisa demonstrar:

1. 1.152 registros de saída, 698 no volume 1 e 454 no volume 2;
2. mesma ordem e numeração de páginas do OCR bruto;
3. zero alteração nos arquivos brutos;
4. hashes válidos para texto bruto e corrigido;
5. replay determinístico sem divergências;
6. testes unitários para espaços, pontuação, títulos, listas, tabelas, falas,
   dehifenização válida e casos em que o hífen deve permanecer;
7. comparação visual de amostra estratificada dos dois volumes;
8. revisão de todas as páginas que mencionam Arthur Orlando;
9. relatório de todas as substituições lexicais e suas frequências;
10. busca comparativa de nomes e termos centrais antes e depois da correção.

A amostra visual deve incluir páginas textuais comuns, páginas esparsas, capas,
tabelas, sessões parlamentares e páginas com OCR degradado. Toda diferença que
possa alterar o sentido suspende a regra correspondente até revisão.

## Critério de aceitação

A camada é aceita quando melhora a continuidade de leitura, preserva ortografia e
estrutura histórica, mantém rastreabilidade página a página e não apresenta
correções sem regra explícita. Ela é uma representação auxiliar para leitura e
pesquisa, não uma edição crítica nem uma transcrição diplomática.
