# Estado da pesquisa após a rotulagem de registro

**Data:** 2026-07-23. **Autor:** Claude, a pedido de Pedro. **Estatuto:** relatório de estado, não decide nada reservado a Pedro pelo gate de `docs/contexto-debate-metodologico-mensuracao.md`.

## Resumo

A Fase A está fechada e a camada textual gratuita cobre o censo inteiro. A rotulagem de registro terminou e passou nos dois testes pré-registrados. Com ela, a **medida pivô do desenho de mensuração deixou de estar em aberto**: o subcorpus substantivo tem entre 3.000 e 3.750 edições, o que equivale a algo entre 200 e 250 horas de leitura. O número responde a pergunta que condicionava a escolha do instrumento desde 19/07, e a resposta é que a codificação humana por censo não cabe no cronograma. A rodada metodológica avança para os artefatos 2, 4 e 5, agora com o parâmetro que faltava.

## 1. O que está pronto

| camada | estado | número |
|---|---|---|
| Censo digital (Fase A) | fechado | 11.960 objetos, com proveniência e hashes |
| Texto embutido (OCR da BN) | fechado | 117.705 páginas, determinístico, custo zero |
| Triagem por nome | rodada e calibrada | 6.354 edições nomeiam a Caixa, recall 0,948 contra o gabarito de 1906 |
| Decomposição de registro | rotulada e revisada | 487 peças, 456 decididas |
| Retrospecto Commercial do JC | extraído, estatuto pendente | 136 páginas, 748 mil caracteres |

Detalhe da rotulagem em `docs/relatorio-rotulagem-registro.md`. Os dois testes pré-registrados passaram: 1906 tem 54 de 54 substantivo, com zero registro mecânico, exatamente como a predição histórica exigia, e nenhum quarto gênero emergiu.

## 2. A medida pivô, respondida

`docs/desenhos-concorrentes.md` definiu a dependência: *"Medida pivô, barata e primeira: o tamanho do subcorpus relevante. Se couber nas horas de Pedro, D-Humano cobre a posição no subcorpus inteiro e a LLM para stance vira opcional; se não couber, a LLM ou um classificador supervisionado reganha lugar para cobertura."*

O cálculo combina dois artefatos que já existiam, sem API: o censo de matches por edição e a proporção de matches substantivos da amostra rotulada. Script em `pipeline/triagem/estima_subcorpus.py`.

### Calibração contra o gabarito de 1906

Antes de projetar, o método foi testado no único ano com padrão-ouro:

| jornal | previsto | gabarito |
|---|---|---|
| Correio da Manhã | 113 | 110 |
| Correio Paulistano | 96 | 94 |
| Gazeta de Notícias | 146 | 146 |
| O Paiz | 81 | 79 |
| **total** | **436** | **429** |

Erro de 1,6%. O teste resolveu uma questão que estava embutida no cálculo: se os 300 descartes da limpeza (disclaimer, trecho vazio, sem nome) devem deflacionar a projeção. Se deflacionassem, 1906 daria 243 edições contra as 429 conhecidas, um erro de 43%. Sem deflacionar, dá 436. **Conclusão: os descartes são falhas da recuperação por visão em localizar o trecho, não evidência de que o match não seja substantivo.** Isso muda o estatuto dos 300 descartes, que deixam de ser ruído e passam a ser não medidos.

Ressalva importante sobre o alcance deste teste: em 1906 a proporção substantiva é 1,000, então o previsto é simplesmente a contagem de edições com match. O teste valida com força a precisão da triagem por nome e a decisão de não deflacionar. Ele **não** valida a proporção substantiva de 1907 em diante, que não tem padrão-ouro e repousa apenas na amostra de cerca de 50 peças por ano.

### Projeção

| ano | edições com match | p substantivo | n rotulado | piso | teto |
|---|---|---|---|---|---|
| 1906 | 436 | 1,000 | 54 | 436 | 436 |
| 1907 | 687 | 0,380 | 50 | 261 | 352 |
| 1908 | 604 | 0,333 | 51 | 201 | 271 |
| 1909 | 901 | 0,345 | 55 | 311 | 419 |
| 1910 | 948 | 0,714 | 70 | 677 | 805 |
| 1911 | 933 | 0,268 | 41 | 250 | 374 |
| 1912 | 663 | 0,256 | 39 | 170 | 221 |
| 1913 | 564 | 0,600 | 40 | 338 | 397 |
| 1914 | 618 | 0,643 | 56 | 397 | 475 |
| **total** | **6.354** | | **456** | **3.043** | **3.750** |

O piso supõe que os registros são perfeitamente correlacionados dentro da edição, o teto supõe independência. A verdade está entre os dois, e a faixa é estreita porque a mediana de matches por edição é 1. Bootstrap por ano com 2.000 reamostragens: piso 3.043, IC95 de 2.788 a 3.321; teto 3.750, IC95 de 3.463 a 4.026.

### O que isso custa em horas

A 4 minutos por edição, que é otimista para leitura de trecho com decisão de posição, o subcorpus inteiro exige de 203 a 250 horas. A 15 ou 20 horas por semana, são 10 a 17 semanas dedicadas apenas a codificar, dentro de um cronograma de cerca de 2 meses para fechar o empírico e com leitura e escrita correndo em paralelo.

## 3. Consequência para a escolha do instrumento

O censo humano de posição não cabe. Isso não elimina D-Humano, reposiciona: ele continua sendo o padrão-ouro e o competidor de validade, mas não pode ser a via de cobertura. As três saídas, que são **decisão de Pedro e de nível crítico** pelo protocolo de colaboração:

1. **D-Humano por amostra estratificada.** Posição medida em 400 a 600 edições (27 a 40 horas), reportada com intervalo de confiança. Honesta e barata, mas a posição vira estimativa amostral e não censo, o que enfraquece afirmações por jornal e fase, justamente onde o núcleo interpretativo mora.
2. **LLM ou classificador supervisionado para cobertura, validado contra codificação humana em amostra, com correção por DSL.** Recupera o censo e mantém erro medido. O ônus da prova continua sendo da LLM, e o custo entra no orçamento residual de cerca de R$415.
3. **Híbrido por fase.** Censo humano onde o volume permite e a densidade histórica justifica, com 1906 como candidato natural (436 edições, cerca de 30 horas, e já existe gabarito), e cobertura automática nas fases de maior volume. Permite dizer que a fase decisiva foi lida inteira por humano.

O número também informa o custo da via 2: cerca de 3.000 a 3.750 edições substantivas, não 6.354, o que reduz em torno de 45% o volume de classificação em lote em relação a rodar sobre todas as edições que nomeiam a Caixa.

## 4. Estado dos sete artefatos da rodada metodológica

| # | artefato | estado |
|---|---|---|
| 1 | Memorando de quantidades históricas | feito, ratificado em 19/07 |
| 2 | Revisão estruturada de pesquisas comparáveis | **não iniciado**, candidato a implementação designada ao Codex |
| 3 | Desenhos concorrentes | feito, e a dependência que ele declarava está agora resolvida |
| 4 | Amostra metodológica estratificada | pendente, mas o subcorpus e os registros já dão a moldura de estratificação |
| 5 | Protocolo humano (codebook, dupla codificação, adjudicação, teste protegido) | pendente, alimenta D2, D4 e D6 |
| 6 | Benchmark pelos 12 critérios | pendente, depende de 4 e 5 |
| 7 | Decisão registrada, que libera a Fase B | pendente |

Das seis decisões de desenho abertas em `docs/sintese-desenho-mensuracao.md`, D3 está resolvida desde 19/07 e D5 está protocolada. D1, D2, D4 e D6 seguem abertas e dependem do padrão-ouro.

## 5. Dívidas e riscos abertos

1. **Dois bugs de limpeza**, com correção especificada em `docs/relatorio-rotulagem-registro.md`: 11 disclaimers vazaram do `drop_sem_nome`, e a chave de ano precisa passar a ser `source_year`. Ambos se concentram em 1910, que é o ano mais atípico da série e o maior contribuinte isolado do subcorpus substantivo.
2. **Viés não medido nos 300 descartes.** A decisão de não deflacionar está calibrada em 1906, onde não há variação de registro. Se a recuperação por visão falha mais em tabelas densas de boletim do que em texto corrido, a amostra `keep` super-representa o substantivo e a projeção está inflada. Teste barato: rotular o registro de cerca de 40 descartes sorteados e comparar a composição com a dos `keep`.
3. **Proporção substantiva de 1907 em diante sem padrão-ouro**, apoiada em cerca de 50 peças por ano, pooled entre quatro jornais. As células jornal por ano têm cerca de 13 peças e não sustentam leitura isolada.
4. **Codebook das fases 2 a 4 ainda é esqueleto.** Bloqueia o protocolo humano, que bloqueia o benchmark.
5. **Estatuto do Retrospecto Commercial pendente** (decisão de escopo de nível crítico, aberta desde 23/07).
6. **`pipeline/triagem/estima_subcorpus.py` não tem testes.** O número principal deste relatório sai dele. Antes de citar 3.000 edições em texto acadêmico, o script precisa de teste sobre fixture pequena, como os demais do `pipeline/triagem/`.

## 6. Sequência recomendada

Ordenada por dependência, sem gastar API:

1. Corrigir os dois bugs de limpeza e reprocessar a amostra. Recalcular a projeção depois, porque 1910 muda.
2. Rotular os cerca de 40 descartes sorteados, que fecha o risco 2 e converte a projeção de estimativa calibrada em um ano para estimativa com viés medido.
3. Levar a decisão do item 3 deste relatório a Pedro, com parecer duplo isolado pelo protocolo, por ser de nível crítico (escolha do instrumento e do estimando).
4. Artefato 2 (revisão de pesquisas comparáveis), que instrui D1 e D2 e pode correr em paralelo.
5. Artefato 4 (amostra estratificada) usando o subcorpus substantivo e os registros como eixos de estratificação, seguido do artefato 5.
6. Fightin' Words, rodadas 1 e 2, quando a limpeza estiver fechada (`docs/todo-fightin-words.md`).
