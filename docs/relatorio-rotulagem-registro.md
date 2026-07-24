# Relatório de revisão da rotulagem de registro

**Data:** 2026-07-23. **Insumo:** `dados/triagem/rotulagem_registro.xlsx`, 487 peças `keep`, rotuladas por Pedro. **Revisão:** Claude, determinística, sem API. **Contrato:** `docs/superpowers/specs/2026-07-21-decomposicao-registro-substancia-design.md`.

## Cobertura

456 de 487 rotulados (93,6%). 31 células em branco (6,4%), conforme a política de 2026-07-23: branco significa indeterminado, não pendência. Sete itens marcados na coluna de problemas (1,4%).

Dos 31 em branco, 8 são vazamento da limpeza e deveriam ter sido descartados antes de chegar à planilha (bug 1, abaixo). O indeterminado genuíno é 23 de 479, ou 4,8%.

## Distribuição por registro e ano

Chave de ano: `source_year` (ver bug 2).

| ano | incidental | operacional_rotina | substantivo | rotulados | em branco |
|---|---|---|---|---|---|
| 1906 | 0 | 0 | 54 | 54 | 2 |
| 1907 | 5 | 26 | 19 | 50 | 3 |
| 1908 | 6 | 28 | 17 | 51 | 9 |
| 1909 | 1 | 35 | 19 | 55 | 4 |
| 1910 | 7 | 13 | 50 | 70 | 5 |
| 1911 | 4 | 26 | 11 | 41 | 7 |
| 1912 | 7 | 22 | 10 | 39 | 1 |
| 1913 | 5 | 11 | 24 | 40 | 0 |
| 1914 | 12 | 8 | 36 | 56 | 0 |
| **tot** | **47** | **169** | **240** | **456** | **31** |

Em proporção dos rotulados de cada ano: substantivo 100% em 1906, 33% a 38% em 1907-08, 35% em 1909, 71% em 1910, 27% em 1911, 26% em 1912, 60% em 1913, 64% em 1914.

Por jornal: *Gazeta de Notícias* 72 substantivo contra 21 de rotina; *O Paiz* 68 contra 27; *Correio da Manhã* 57 contra 47; *Correio Paulistano* 43 contra 74. O paulista é o único em que a rotina domina.

## Testes pré-registrados

**Teste do artefato de gênero: passa.** A predição registrada em 2026-07-21 dizia que `incidental` e `operacional_rotina` deviam concentrar em 1907 em diante e ser raros em 1906, porque a Caixa não operava em 1906 e portanto não havia boletim de movimento. Resultado: 1906 tem 54 de 54 substantivo, zero incidental, zero operacional. A predição vinha da história, não do instrumento, e podia ter falhado. É o teste mais informativo desta rodada.

**Margem de suficiência: passa.** Nenhum quarto gênero frequente apareceu. Os 7 itens marcados como insuficientes ou inconsistentes (1,4%) não formam classe.

**Coerência com a `forma`.** A coluna `forma` veio do modelo de recuperação, a coluna `registro` veio da leitura de Pedro. Não são independentes, o texto é o mesmo, mas são atos de medição separados.

| forma | incidental | operacional_rotina | substantivo |
|---|---|---|---|
| editorial | 0 | 0 | 28 |
| artigo | 0 | 0 | 64 |
| tabela_boletim | 1 | 66 | 5 |
| lista | 16 | 1 | 3 |
| anuncio | 9 | 0 | 1 |
| telegrama | 2 | 6 | 20 |
| noticia | 19 | 96 | 117 |

Editorial e artigo são substantivos sem exceção. Boletim é rotina em 92% dos casos. O telegrama se reparte pelos três registros, o que confirma a decisão de design de 2026-07-21: telegrama é veículo, não registro, e classifica-se pelo conteúdo.

**Consequência de projeto para o detector.** Toda a ambiguidade mora em `noticia`: 232 itens repartidos em 117 substantivo, 96 rotina e 19 incidental. As demais formas são quase determinadas pela própria forma. O `classificador_registro.py` pode usar `forma` como prior forte e concentrar os detectores em `noticia`, o que reduz o problema difícil de 487 para 232 casos. Ressalva: `forma` é saída de modelo, então usá-la como atributo importa o erro do modelo para dentro do detector, e esse erro precisa ser medido, não presumido.

## Dois bugs na camada de limpeza

**Bug 1, vazamento de disclaimer.** Onze itens de 487 (2,3%) trazem no `trecho_caixa` a marca de que a peça não menciona a Caixa, e ainda assim passaram pelo `drop_sem_nome` do `limpa_amostra.py`, porque a redação do disclaimer varia. Oito ficaram em branco, o que mostra que Pedro os reconheceu na leitura. Dois foram rotulados `incidental` com nota de ignorar. Um foi rotulado `substantivo`:

- rotulado indevidamente: `per089842_1910_03440:p008:i3` (substantivo), `per089842_1914_05551:p001:i1` e `per089842_1914_05712:p006:i2` (incidental, com nota de ignorar);
- em branco por disclaimer, a descartar e não rotular: `per089842_1910_03212:p001:i1`, `per090972_1906_15459:p002:i3`, `per090972_1909_16592:p003:i2`, `per090972_1909_16592:p003:i3`, `per090972_1911_17181:p003:i2`, `per178691_1907_08206:p005:i3`, `per178691_1910_09522:p002:i1`, `per178691_1910_09522:p002:i3`.

O caso rotulado `substantivo` infla o denominador substantivo de 1910, justamente o ano com o maior desvio da série. Correção: ampliar o padrão de `limpa_amostra.py` para as variantes de redação e reprocessar.

**Bug 2, chave de ano.** A data resolvida diverge de `source_year` em 26 dos 487, e 25 têm `data_confiavel=0`. Tabelas por ano montadas sobre `data` perdem 18 itens só em 1910, o que sozinho distorce o ano mais atípico da série. Regra: `source_year` é a chave de ano para qualquer contagem; `data` só entra onde `data_confiavel=1`, e apenas para série mensal.

## Um achado substantivo, com cautela

A composição de registro acompanha as fases do codebook, e a medida não foi construída para detectar fase. O substantivo domina em 1906 (criação), a rotina domina em 1907-09 (operação), o substantivo volta em 1910 (taxa de 16 dinheiros), a rotina retorna em 1911-12 e o substantivo volta em 1913-14 (crise).

Três cautelas antes de qualquer leitura histórica:

1. A amostra é estratificada por jornal e ano sobre matches, e passou pela limpeza, cujas taxas de `keep` variaram de 51% a 66% por ano. As proporções são da amostra sobrevivente de matches, não da população de edições. A recomposição para o denominador de edições ainda não foi feita.
2. O ano de 1910 concentra o efeito do bug 1 e do bug 2. Refazer antes de interpretar.
3. O refluxo de 1911-12 contra os picos de 1910 e 1913-14 sugere que o bloco 1910-13 do codebook pode ser grosso demais. É hipótese a testar, não achado.

A hipótese do item 3 é testável de forma barata e independente pela análise lexical descrita em `docs/todo-fightin-words.md`.

## Estado

A rotulagem cumpre o contrato do design e libera o passo seguinte, que é o detector determinístico. Ordem recomendada: corrigir os dois bugs, reprocessar a amostra, recompor os denominadores, e só então implementar o `classificador_registro.py` contra este conjunto de referência.
