# Banqueiros externos no corpus: sondagem exploratória

**Feito em:** 2026-07-26/27, a pedido de Pedro. **Custo:** zero token de API.

> **ISTO NÃO É INSTRUMENTO DE MEDIÇÃO.** É sondagem para decidir se há filão.
> Os padrões dos banqueiros (fora Rothschild) não passaram por calibração
> nenhuma, e nenhuma citação foi conferida contra a imagem da página. Nada aqui
> entra na dissertação sem passar pelo mesmo rito das outras medidas.

## O que foi varrido

As 117.703 páginas da camada de texto embutido (4,32 bilhões de caracteres),
com a `regra_nome` ratificada da triagem para a co-ocorrência com a Caixa.

**Controle de sanidade que dá confiança:** a varredura devolveu exatamente
**8.331 páginas** com o nome da Caixa, o mesmo número da rodada 1 do Fightin'
Words de 25/07. Reproduziu a triagem.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `achados.csv` | 1.709 linhas: jornal, ano, objeto, página, termo, variante de OCR, se tem Caixa, contexto (280 chars) e caminho do .txt |
| `celulas.csv` | agregado por jornal-ano: páginas, páginas com Caixa, com Rothschild, com ambos, e o mesmo para cada casa bancária |
| `variantes_rothschild.csv` | as 126 grafias distintas que o OCR produziu, com frequência |
| `proximidade.csv` | as 170 páginas Rothschild+Caixa, com a distância mínima em caracteres entre as duas menções |

Os scripts que geraram tudo estão em `pipeline/banqueiros/`.

## Os três achados que importam

**1. Grafia exata perde metade.** `rothschild` limpo é 712 de 1.464 ocorrências
(48,6%). O resto se reparte em 125 variantes (`rotschild` 211, `rothsohild` 64,
`rothscliild` 46, `rotlischild` 33...). Nome próprio estrangeiro em tipo gótico
apanha muito mais do OCR que "caixa de conversão", que é frase portuguesa e
redundante. **Consequência de desenho:** nome próprio na camada 2 precisa de
distância de edição, não de regex literal.

**2. Co-ocorrência na página é, em boa parte, vizinhança de coluna.** Mediana da
distância entre as duas menções: **8.077 caracteres**, numa página que tem
41.738 em média. Só 5,3% ficam a menos de 200 caracteres. O caso puro é o
Correio Paulistano de 1911, que imprime a remessa de libras aos Rothschild logo
acima do boletim diário da Caixa: 11 caracteres de distância, zero relação
argumentativa. **Consequência:** se a camada 2 entrar, a unidade de
co-ocorrência tem que ser sub-página, não página.

*Ressalva sobre essa própria medida:* distância em caracteres no texto extraído
não é distância física na página, porque a ordem de leitura do OCR da BN não
respeita coluna de forma confiável. Serve para ordenar candidatos, não como
métrica final.

**3. A perífrase derrota a busca por nome.** A Gazeta de Notícias de 1906
(ed. 282) chama Rothschild de **"o rei dos banqueiros londrinos"**, sem nomeá-lo.
Nenhuma regra de nome próprio pega isso. O construto tem mais superfícies que o
nome canônico, do mesmo jeito que "Caixa de Emissão e Conversão" (registrada em
23/07) e "caixa de emissão ouro e conversão" (achada em O Paiz 1908, ed. 8816).

## Onde estão os exemplares substantivos

Os 15 trechos curados (3 por jornal, mais 3 do Retrospecto do JC) **não estão em
arquivo**: foram entregues no chat de 26/07. Para recuperá-los, os localizadores
estão em `achados.csv` e `proximidade.csv`. Os melhores:

| Jornal | Edição | O que tem |
|---|---|---|
| Gazeta de Notícias 1907 | 210, p1 | entrevista de Serzedelo: os Rothschild acham que a Caixa "tem o grave inconveniente de fazer a estabilisação" |
| Gazeta de Notícias 1906 | 282, p1 | "o rei dos banqueiros londrinos", a perífrase |
| Correio Paulistano 1911 | 17064 e 17069, p2 | governo resolve transferir os depósitos da Caixa aos Rothschild a 2,5%, e a réplica do Correio da Noite |
| Correio Paulistano 1907 | 15757, p1 | "as maiores difficuldades opostas pela firma Rotschild & Sons, de Londres" |
| Correio da Manhã 1913 | 5446, p4 | Senado: Murtinho e a revolução; oposição "até dos proprios srs. Rotschild" |
| Correio da Manhã 1911 | 3809, p1 | "humilhante para os nossos brios de povo independente" |
| O Paiz 1908 | 8722 e 8820, p1 | "conservamos a mesma attitude de combatente"; o ouro "artisticamente attrahido" |
| O Paiz 1914 | 10826, p2 | Senado na crise: Sá Freire contra Bulhões |
| JC Retrospecto 1907 | seção monetária | "sempre negaram apoio á temeraria operação do convenio; mas não negaram nunca amparo ao credito do Brasil" |

Essa última frase é a mais citável do lote: separa oposição ao convênio de apoio
ao crédito soberano, que é exatamente a distinção que o eixo
ortodoxia/expansionismo precisa saber fazer.

## Jornal do Commercio

O diário principal **não está no censo** e não tem rota automatizada (o host
estático não serve o bib 364568). O que existe é o **Retrospecto Commercial**
(bib 180688), anual, com estatuto ainda em aberto. Rothschild aparece nele
**4 vezes, todas em 1906-1907**, e zero de 1908 em diante.

## Se isso virar frente de trabalho

O caminho barato é rotular `registro` (substantivo / operacional_rotina /
incidental) nessas páginas com a planilha que já existe, em vez de inventar
escala nova. Todos os 15 exemplares acima seriam `substantivo`; o ticker de
remessas seria `operacional_rotina`; turfe (4,7%), lista de passageiros (1,8%) e
obituário (1,2%) seriam `incidental`.
