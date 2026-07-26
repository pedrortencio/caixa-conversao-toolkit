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

1. ~~Corrigir o vazamento de disclaimer no `limpa_amostra.py` e reprocessar a amostra~~ **feito em 2026-07-25** (19 itens descartados, `keep` 487 para 468; ver `docs/decisoes.md`).
2. ~~Fixar `source_year` como chave de ano em toda contagem~~ **feito em 2026-07-25** (a coluna `data` deixa de guardar o ano nu e fica vazia quando não há data resolvida).
3. ~~Decidir e registrar a normalização de vocabulário~~ **decidido por Pedro em 2026-07-25: regime mínimo, minúsculas e remoção de acento**, sem regras de ortografia de época. A sonda mostrou que os termos do construto quase não se repartem em variantes e que qualquer regime colapsa no máximo 6% do vocabulário, então o ruído fica a cargo do prior de Dirichlet mais piso de frequência. Registro em `docs/decisoes.md`.
4. ~~Medir a qualidade do OCR por grupo antes de qualquer comparação entre jornais~~ **feito em 2026-07-25**: `pipeline/analise/qualidade_ocr.py` (TDD) e `docs/relatorio-qualidade-ocr.md`. **Achado que muda este to-do:** O Paiz varia 3,0x em ruído entre 1909 (4,84%) e 1906 (14,33%), então a rodada 2, fase contra fase, está confundida pela digitalização tanto quanto a rodada 3, e não só a 3 como este documento supunha. Ver a ressalva acrescentada à rodada 2.

## As quatro rodadas, em ordem de valor

**1. Relevante contra não relevante.** ~~Objetivo: obter os termos que acompanham o debate e não estão na regra de busca por nome~~ **RODADA EM 2026-07-25**, ver `docs/relatorio-fw-rodada1-relevancia.md` e a entrada do dia em `docs/decisoes.md`. 8.331 páginas contra 8.331, controle estratificado por célula jornal-ano. Devolveu: confirmação empírica da camada 2 de termos (`cambio`, `cambial`, `moeda`, `circulacao`, `libras`, `amortizacao`), atores nomeados não procurados (`campista`, `bulhoes`, `rivadavia`) e o predomínio da seção de atos oficiais no grupo relevante. Limite achado na própria rodada: o controle é dominado por anúncio classificado, então o contraste é em parte de gênero de página.

**2. Fase contra fase, no subcorpus substantivo.** Objetivo: testar se a periodização do codebook tem assinatura lexical própria, o que a converte de recorte a priori em achado. Hipótese específica vinda da rotulagem de registro: 1910 e 1913-14 se separam de 1911-12, o que colocaria em questão o bloco 1910-13.

> **Ressalva de 2026-07-25, do pré-requisito 4.** Fase é recorte de ANOS, e o ruído de OCR varia por ano dentro do mesmo jornal (O Paiz: 4,84% em 1909 contra 14,33% em 1906, 3,0x). Como 1906 é fase inteira e é o pior ano de O Paiz, a assinatura lexical da fase 1 pode ser assinatura do scanner. Controle mínimo antes de ler a rodada 2: repetir a comparação dentro de cada jornal separadamente e reter só os termos que aparecem nos quatro, e conferir se o topo da lista não é lixo sem vogal.

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
