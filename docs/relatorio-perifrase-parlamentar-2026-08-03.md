# O silêncio parlamentar sobre o credor externo, testado por perífrase

**Feito em:** 2026-08-03. **Custo:** zero token de API. **Estatuto:** mapeamento
descritivo, o objeto 1. Não atribui posição, não é escala, não é estimativa.

**A checagem que este documento faz.** A varredura de 03/08 mediu zero menção
pelo nome a Rothschild, Speyer, Baring, Schröder e Crédit Lyonnais nas 1.152
páginas dos *Documentos Parlamentares* sobre a Caixa. Na imprensa, porém, 418
páginas designam o credor sem nomeá-lo, contra 132 que nomeiam sem designar, e a
perífrase derrota a busca por nome por margem grande. Enquanto a mesma varredura
de perífrase não rodasse sobre os volumes, o zero podia ser artefato do
instrumento e não propriedade da fonte.

Reprodução: `uv run python -m pipeline.analise.perifrase_parlamentar`.
Manifesto em `dados/analise/perifrase_parlamentar.csv`, testes em
`tests/test_perifrase_parlamentar.py`.

## 1. O silêncio resiste ao teste, mas não é silêncio absoluto

Os mesmos 23 padrões, em 8 famílias, que rodaram na imprensa:

| corpus | páginas | páginas com perífrase | taxa | só confiança alta |
|---|---|---|---|---|
| imprensa (páginas que mencionam a Caixa) | 8.331 | 456 | 5,47% | 2,57% |
| Documentos Parlamentares | 1.152 | 14 | 1,22% | 0,78% |

A densidade no plenário é cerca de quatro vezes e meia menor, e a comparação é
conservadora contra o achado: as páginas de jornal apenas **mencionam** a Caixa,
enquanto os volumes parlamentares são **integralmente** sobre ela. O ambiente
mais concentrado no tema é o que menos nomeia o credor.

Então o zero por nome não era artefato. É achado, e agora com a forma correta:
**no plenário o credor externo é raro em qualquer designação, não apenas no nome
próprio.** Na imprensa ele é onipresente e anônimo; no Congresso é ausente.

## 2. As 14 ocorrências, e o que elas mudam

Distribuição: 8 no volume 1 (1906, criação) e 6 no volume 2 (1910, taxa de 16
dinheiros). Por família, `credor` domina com 6, seguida de
`banqueiro_estrangeiro` e `capital_externo` com 2 cada.

### 2.1 A maioria invoca o credor como memória, não como ator presente

Quatro das seis ocorrências da família `credor` falam do funding de 1898, não da
Caixa em curso. No volume 1:

> foi nesta posicao desgq:tcada, neste momento infeliz, que o governo se viu
> obrigado a celebrar cqm os nossos credores em londres o contracto conhecido
> pelo nome de funding-loan

e

> trazendo como consequencia fatal para o thesouro a concordata com os credores
> externos, a suspensao das amortizacoes e do pagamento dos juros

No volume 2, a mesma memória, duas vezes, com o mesmo enquadramento de lição
aprendida.

Isto é uma distinção que o capítulo precisa carregar: **no plenário o credor
aparece como restrição passada e consumada; na imprensa, como ator presente que
negocia, telegrafa, recusa empréstimo e recebe o ouro em depósito.** Não é a
mesma figura retórica, e tratar as duas fontes como registros do mesmo objeto
apagaria justamente o contraste.

### 2.2 A exceção, e é a peça mais forte do lote

O volume 1, `pdf_page` 500, tem o credor como ator presente e como sujeito
político, sem nome, exatamente na forma que a busca por nome próprio nunca
acharia:

> esquecidos de que somos os devedores e elles os credores hypothecarios..., nao
> me parece que isto seja de grande moralidade, mas emfim damos de barato que ~e
> ja uma prova de que sao abelhudos estes credores estrangeiros, e~ tes
> banqueiros que se preoccupam com as condicoes em que vae ficar 1) seu ouro. mas
> a inglaterr ~, de onde ponhficam estes b'anqueiros

O trecho tem tudo: a relação hipotecária
declarada, a irritação com a tutela, a localização em Londres por perífrase
(`de onde pontificam estes banqueiros`) e o objeto concreto, o ouro. É o par
parlamentar do `rei dos banqueiros londrinos` da Gazeta de 1906.

Uma peça não desfaz o padrão das outras treze, mas fixa que o silêncio é de
frequência e não de possibilidade. O credor **podia** ser nomeado por perífrase
no plenário e quase nunca foi.

### 2.3 Duas ocorrências são a mesma peça

`v1 p66` e `v1 p636` trazem o mesmo texto sobre o diretor da carteira de câmbio
do Banco da República e o empréstimo de São Paulo, reimpresso em dois pontos do
volume. Contá-las como dois registros infla a contagem, e é o mesmo problema de
deduplicação que a CLAUDE.md registra para a peça que circula entre jornais.
Descontando, são 13 ocorrências em 13 páginas.

## 3. Um defeito do instrumento, medido de passagem

O padrão `grande\s*banca` casou dentro de **bancarrota**:

> diz, referindo-se a quebra do padrao, decretada pela austria em 1811, a grande
> bancarrota da austria

Medi o alcance na imprensa: das 6 ocorrências de `grande banca` no manifesto de
lá, 1 é o mesmo falso positivo, e é a mesma passagem, um discurso reproduzido em
jornal. Então o defeito é real e pequeno, 1 em 6 no padrão, 1 em 456 páginas da
varredura da imprensa.

**Não corrigi o padrão.** Acrescentar ou alterar padrão é mudança do instrumento
de busca e exige linha em `padroes_perifrase_banqueiro.csv` com justificativa e
registro em `docs/decisoes.md`, porque muda o que a busca enxerga. A correção
óbvia é exigir fronteira de palavra, `grande\s*banca\b`, e ela precisa da sua
aprovação e de uma nova rodada nas duas varreduras, para que os números deste
documento e do relatório do credor externo permaneçam auditáveis contra a versão
do padrão que os produziu.

## 4. O que este documento não autoriza

**Nenhum número daqui entra em texto ainda**, por duas razões independentes:

1. o insumo é a camada corrigida dos *Documentos Parlamentares*, que é hoje
   produto sem instrumento: a rotina que a gerou não está no repositório
   (`docs/auditoria-da-base-2026-08-03.md`, seção 2.1). Enquanto o replay
   determinístico não passar, a camada serve para ler e não para publicar
   número;
2. as citações acima são transcrições do OCR corrigido e **nenhuma foi conferida
   na imagem da página**. Antes de qualquer uma ir para a dissertação, precisa
   ser lida no PDF.

**Recall continua desconhecido.** Não existe lista fechada das formas que a
língua de 1906 usava para dizer credor, e a varredura garante piso, nunca censo.
A diferença entre 5,47% e 1,22% é grande o bastante para não ser explicada por
lacuna de padrão, já que os padrões são os mesmos nos dois corpora, mas o piso
continua sendo piso.

## 5. O que depende de você

1. Aprovar ou recusar a correção de `grande\s*banca` para `grande\s*banca\b`, com
   registro em `docs/decisoes.md` e nova rodada das duas varreduras.
2. Decidir se a varredura de perífrase, agora com dois corpora, sobe de sondagem
   a instrumento. Continua sendo sondagem por decisão sua de 03/08.
3. Conferir na imagem as citações que forem para o capítulo, em particular a de
   `v1 p500`, que é a que carrega o argumento.
