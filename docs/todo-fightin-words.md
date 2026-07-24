# To-do: análise lexical distintiva (Fightin' Words)

**Data:** 2026-07-23. **Estatuto:** diagnóstico e triangulação aprovados, não instrumento principal nem resultado central. **Gate:** não rodar antes de fechar a limpeza das bases. Decisão registrada em `docs/decisoes.md` (2026-07-23).

## Origem

Pedro perguntou se valia fazer modelo de tópicos no corpus. Dois pareceres convergiram na recusa do modelo de tópicos como método central e na indicação de Fightin' Words como alternativa proporcional ao problema. O argumento comum: tópico modela assunto, não adesão. Ortodoxos e expansionistas usam o mesmo vocabulário (câmbio, conversão, lastro, emissão, 15 dinheiros, café, crédito) e cairiam no mesmo agrupamento. Some-se a unidade documental do jornal, em que uma página mistura editorial, telegrama, movimento do porto e anúncio, e o modelo recupera seção e gênero, não debate. O corpus tem cerca de 117 mil páginas de OCR bruto da Hemeroteca, e OCR sujo é o pior caso para contagem de palavras não supervisionada.

O modelo de tópicos não fica proibido. Fica adiado, com escopo estreito: se um dia entrar, entra sobre o subcorpus substantivo já segmentado, como STM com jornal e ano como covariáveis, para saliência e composição temática, nunca para posição.

## O método

Monroe, Colaresi e Quinn (2008), *Fightin' Words: Lexical Feature Selection and Evaluation for Identifying the Content of Political Conflict*, Political Analysis 16(4). Duas peças:

1. **Prior de Dirichlet informativo.** Cada palavra recebe pseudo-contagem proporcional à sua frequência no corpus inteiro, o que encolhe termos raros na direção da média. É isso que impede que a lista de palavras distintivas vire uma lista de erros de OCR.
2. **Padronização pelo erro padrão.** Para a palavra $w$ nos grupos $i$ e $j$:

$$\hat\delta_w^{(i-j)} = \log\frac{y_{iw}+\alpha_w}{n_i+\alpha_0-y_{iw}-\alpha_w} - \log\frac{y_{jw}+\alpha_w}{n_j+\alpha_0-y_{jw}-\alpha_w}$$

com $\widehat{\mathrm{Var}}(\hat\delta_w) \approx \frac{1}{y_{iw}+\alpha_w} + \frac{1}{y_{jw}+\alpha_w}$, e leitura pelo z-score $\hat\delta_w/\sqrt{\widehat{\mathrm{Var}}}$.

A saída canônica é o gráfico de frequência da palavra no corpus, em log, contra o z-score. Interessam as palavras distantes de zero e frequentes.

## Pré-requisitos, que bloqueiam a rodada

1. Corrigir o vazamento de disclaimer no `limpa_amostra.py` e reprocessar a amostra (`docs/relatorio-rotulagem-registro.md`, bug 1).
2. Fixar `source_year` como chave de ano em toda contagem (bug 2 do mesmo relatório).
3. Decidir e registrar a normalização de vocabulário: ortografia de época e variantes de OCR (conversão e converção, actual e atual). Normalizar vocabulário num corpus definido pelo construto não é pré-processamento neutro, então a decisão entra em `docs/decisoes.md`.
4. Medir a qualidade do OCR por grupo antes de qualquer comparação entre jornais, usando `char_count` e taxa de token fora de léxico da camada de texto embutido.

## As quatro rodadas, em ordem de valor

**1. Relevante contra não relevante.** Objetivo: obter os termos que acompanham o debate e não estão na regra de busca por nome, como candidatos a ampliar a triagem. Insumo direto da auditoria de recall, que o desenho já exige antes de fechar o corpus. Não depende de rótulo humano de posição. Grupos: páginas com match de nome contra amostra de páginas sem match, sobre o OCR embutido. Esta é a primeira porque devolve algo acionável ainda na fase de construção do corpus.

**2. Fase contra fase, no subcorpus substantivo.** Objetivo: testar se a periodização do codebook tem assinatura lexical própria, o que a converte de recorte a priori em achado. Hipótese específica vinda da rotulagem de registro: 1910 e 1913-14 se separam de 1911-12, o que colocaria em questão o bloco 1910-13.

**3. Jornal contra jornal.** Cautela alta. A comparação é confundida com qualidade de digitalização por título e por década, e com a composição de seções de cada diário. Só depois do pré-requisito 4, e com inspeção de que os termos do topo são palavras de verdade.

**4. Ortodoxo contra expansionista.** Só depois dos rótulos humanos de posição. Reporta-se como leitura lexical dos rótulos, jamais como validação independente deles: os grupos são definidos pelos rótulos, então a lista de palavras é descendente deles.

## Especificação técnica

- Implementação em `pipeline/analise/fightin_words.py`, função pura sobre matriz de contagem, com testes antes do código.
- $\alpha_0$ é o único parâmetro de ajuste. Fixar, reportar e apresentar sensibilidade em pelo menos dois valores.
- Saída por rodada: tabela dos 30 termos de cada lado com contagem, $\hat\delta$ e z, mais o gráfico canônico.
- Conferência da implementação contra o pacote `tidylo` em R, que traz o mesmo estimador.
- Proveniência em toda saída: corpus, definição dos grupos, $\alpha_0$, vocabulário, regra de normalização e hash do commit.
- Custo: zero em API, roda local sobre a camada de texto embutido. O custo real é o tempo de leitura das listas.

## Limites a declarar no artigo

- Saco de palavras não vê negação nem discurso reproduzido. "Não somos partidários da Caixa" e "somos partidários da Caixa" são idênticos para o método, o que é o mesmo problema D4 do desenho de mensuração.
- Não é teste de hipótese. São milhares de z-scores. É seleção de atributos e descrição, como os próprios autores apresentam, e não inferência com nível de significância.
- Palavra distintiva não é posição. Vale aqui, em grau menor, a mesma advertência que afastou o modelo de tópicos.
- Comparação entre jornais carrega confundimento com o acervo digitalizado de cada título.

## Papel previsto no artigo

Seção curta ou apêndice metodológico, subordinada ao desenho de mensuração: análise lexical exploratória que qualifica a periodização e orienta a auditoria de recuperação. Se não houver sinal, o custo perdido é baixo, porque as rodadas 1 e 2 já pagam sozinhas como controle de qualidade do corpus.
