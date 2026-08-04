# Quem aparece no debate sobre a Caixa de Conversão

**Feito em:** 2026-08-03. **Custo:** zero token de API. **Estatuto:** medida
exploratória do objeto 1, o mapeamento descritivo. Não é atribuição de posição,
não é escala, não é estimativa. Nenhuma linha vale como citação sem conferência
na página.

Duas bases distintas respondem à pergunta, e elas não dizem a mesma coisa.

1. **Documentos Parlamentares da Caixa de Conversão**, dois volumes, 1.152
   páginas. Aqui o corpus inteiro é o debate, então contar nome na página já é
   contar nome no debate.
2. **As 8.331 páginas de jornal com menção da Caixa**, de 1906 a 1914. Aqui
   contar nome na página não serve, e a seção 3 explica por quê.

## 1. O que foi medido, e o que não foi

A medida conta **nome**, não **ator**. Três coisas ficam de fora por construção,
e as três aparecem no material já lido:

- **perífrase**: a Gazeta de 1906 chama Rothschild de "o rei dos banqueiros
  londrinos", sem nomeá-lo;
- **designação por cargo**: "o ministro da Fazenda" aparece sete vezes entre os
  agentes do piloto de catalogação, e é Bulhões em boa parte do período;
- **sobrenome sozinho quando ambíguo**: "Barbosa" pode ser Rui Barbosa ou
  Barbosa Lima, e a regra só aceita o par adjacente.

Além disso o casamento tolera ruído de OCR por distância de edição 1 em token de
sete caracteres ou mais, e exige forma exata abaixo disso. O corte é
assimétrico porque abaixo de sete caracteres a vizinhança lexical do português
já contém palavra corrente. As colisões recusadas estão em
`pipeline/analise/exclusoes_variantes_nomes.csv`, uma por linha com motivo. As
que mais pesam, medidas nesta base: `carvalhal` casa `carvalho` (2.322
ocorrências), `campista` casa `cambista`, `pinheiro` casa `dinheiro` (1.056),
`sarmento` casa `sargento` (1.204), `ellis` casa `elles` (955).

## 2. Documentos Parlamentares: quem fala e quem é citado

Volume 1 (1906, criação) tem 698 páginas e 405 menções do nome da Caixa em 226
páginas. Volume 2 (1910, taxa de 16 dinheiros) tem 454 páginas e 255 menções em
166 páginas.

A coluna `turnos` conta as vezes em que o nome encabeça uma fala, pelo marcador
`O SR. NOME`. É a coluna que separa quem discursa de quem é citado, e o jornal
não permite fazer essa separação sem leitura.

| nome | menções | v1 1906 | v2 1910 | turnos de fala |
|---|---|---|---|---|
| Barbosa Lima | 212 | 159 | 53 | 105 |
| David Campista | 193 | 164 | 29 | 5 |
| Calógeras | 120 | 0 | 120 | 77 |
| Affonso Costa | 80 | 15 | 65 | 48 |
| Leopoldo de Bulhões | 78 | 4 | 74 | 3 |
| Joaquim Murtinho | 75 | 33 | 42 | 0 |
| Cincinato Braga | 69 | 3 | 66 | 42 |
| Serzedello Corrêa | 64 | 60 | 4 | 19 |
| Paula Ramos | 49 | 37 | 12 | 22 |
| Galeão Carvalhal | 45 | 24 | 21 | 0 |
| Rodolpho Paixão | 43 | 24 | 19 | 23 |
| Alcindo Guanabara | 41 | 30 | 11 | 10 |
| Moniz Freire | 40 | 16 | 24 | 25 |
| Lindolpho Câmara | 37 | 2 | 35 | 18 |
| Felisbello Freire | 35 | 6 | 29 | 13 |
| Duarte de Abreu | 34 | 0 | 34 | 22 |

Manifesto completo em `dados/analise/nomes_documentos_parlamentares.json`.

Três leituras saem daí.

**A relação entre ser nomeado e falar não é constante.** David Campista é o
segundo mais nomeado do conjunto, com 193 menções, e abre apenas 5 turnos de
fala. Barbosa Lima tem 212 menções e 105 turnos. O autor do projeto é o objeto
do debate; o adversário é o sujeito dele. Quem tomar contagem de menção como
proxy de participação inverte os dois papéis.

**O elenco troca entre 1906 e 1910.** Calógeras tem 120 menções, todas no volume
2 e nenhuma no volume 1. Duarte de Abreu e Severino Vieira também aparecem só em
1910. Do outro lado, Serzedello Corrêa concentra 60 das suas 64 menções em 1906.
A troca é grande o bastante para que qualquer série que trate os dois volumes
como um corpus único misture duas composições diferentes.

**Nenhum banqueiro estrangeiro é nomeado.** Rothschild, Speyer, Baring, Schröder
e Crédit Lyonnais somam zero menção nos dois volumes. Isso contrasta com a
imprensa, onde Rothschild aparece em 1.464 ocorrências no acervo. A ausência é
achado, não falha de busca, e vale conferir na página antes de virar afirmação
histórica: a hipótese óbvia é que o credor externo se discute por perífrase e por
cargo no plenário, e por nome no jornal.

## 3. Por que a página de jornal não serve como unidade

A sondagem de banqueiros de 26/07 mediu que a co-ocorrência na página é, em boa
parte, vizinhança de coluna: a mediana da distância entre a menção de Rothschild
e a da Caixa foi de 8.077 caracteres, numa página de 41.738, e apenas 5,3%
ficaram abaixo de 200. O caso puro é o Correio Paulistano de 1911, que imprime a
remessa de libras aos Rothschild logo acima do boletim diário da Caixa, a onze
caracteres de distância e sem nenhuma relação argumentativa.

Fiz o teste com janela larga antes de descartá-lo. Com janela de 6.000
caracteres em torno da menção, a mesma que o piloto de catalogação manda ao
anotador, o primeiro colocado é **Hermes da Fonseca**, com 1.192 das 9.146
janelas, e o pico da série cai em 1912. Hermes é presidente da República no
período, não debatedor da Caixa. O ranking por janela larga mede o que o jornal
mais imprime, não o que o debate discute.

Por isso a medida final guarda, para cada par (página, nome), a **distância
mínima em caracteres** até a menção mais próxima. O limiar vira consulta, e a
escolha do limiar fica explícita em vez de embutida.

Ressalva que acompanha a medida e não sai do lado dela: distância em caracteres
do texto extraído não é distância física na página, porque a ordem de leitura do
OCR da Biblioteca Nacional não respeita coluna de forma confiável.

## 4. A imprensa, 1906 a 1914

Denominador: 8.331 páginas com menção da Caixa, distribuídas de forma desigual
pelos anos (570 em 1906, 1.452 em 1910, 828 em 1914). Toda comparação entre anos
usa a taxa por 100 páginas do ano, nunca a contagem bruta.

A varredura achou 27.813 pares (página, nome). A distribuição da distância
mostra por que o limiar importa: a mediana é de 6.967 caracteres, e apenas 3,7%
dos pares ficam abaixo de 200. O número reproduz, com outro elenco e outra
varredura, os 5,3% que a sondagem de banqueiros mediu para Rothschild.

### 4.1 Ranking a 200 caracteres

| nome | ≤200 | ≤1.000 | mesma página | mediana | concentração |
|---|---|---|---|---|---|
| David Campista | 235 | 511 | 1.570 | 3.538 | 15% |
| Leopoldo de Bulhões | 139 | 356 | 1.421 | 5.097 | 10% |
| Hermes da Fonseca | 71 | 431 | 3.359 | 5.309 | 2% |
| Galeão Carvalhal | 41 | 108 | 619 | 6.206 | 7% |
| Nilo Peçanha | 39 | 195 | 1.522 | 6.926 | 3% |
| Affonso Penna | 38 | 138 | 1.098 | 6.128 | 3% |
| Pinheiro Machado | 32 | 155 | 1.508 | 7.322 | 2% |
| Joaquim Murtinho | 32 | 107 | 749 | 7.041 | 4% |
| Barbosa Lima | 31 | 170 | 824 | 6.290 | 4% |
| Serzedello Corrêa | 29 | 100 | 760 | 8.951 | 4% |
| Rodrigues Alves | 27 | 93 | 1.030 | 8.946 | 3% |
| Calógeras | 24 | 56 | 291 | 7.699 | 8% |
| Francisco Glycerio | 22 | 109 | 989 | 6.937 | 2% |
| Alcindo Guanabara | 21 | 71 | 682 | 8.320 | 3% |
| Custódio Coelho | 16 | 43 | 147 | 4.970 | 11% |
| Rothschild | 7 | 24 | 158 | 8.174 | 4% |

A coluna **concentração** é a fração dos casos de mesma página que ficam a 200
caracteres. Ela é mais informativa que a contagem, porque separa duas coisas que
o ranking bruto mistura.

**Campista, com 15%, e Bulhões, com 10%, estão ligados à Caixa.** Custódio
Coelho, diretor da carteira de câmbio do Banco do Brasil, tem 11% sobre uma base
pequena, o que é coerente com um técnico que só aparece quando o assunto é
esse. Calógeras tem 8% e Carvalhal 7%.

**Hermes da Fonseca, com 2%, é ambiente.** Ele está em 3.359 páginas com menção,
mais que qualquer outro, e quase nunca perto dela. Rui Barbosa, com 1%, e
Wenceslau Braz, com 1%, idem. São nomes que o jornal imprime todo dia, não nomes
do debate.

### 4.2 A distribuição no tempo

Taxa por 100 páginas com menção do ano, no limiar de 200 caracteres:

| nome | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|
| David Campista | 10,0 | 6,9 | 8,4 | 3,3 | 1,1 | 0,3 | 0,0 | 1,0 | 0,1 |
| Leopoldo de Bulhões | 0,5 | 0,5 | 0,3 | 2,4 | 5,2 | 0,7 | 0,4 | 1,4 | 0,8 |
| Galeão Carvalhal | 0,5 | 0,8 | 0,7 | 0,6 | 1,3 | 0,0 | 0,0 | 0,1 | 0,0 |
| Nilo Peçanha | 0,4 | 0,0 | 0,0 | 0,6 | 1,2 | 0,1 | 0,1 | 0,8 | 0,6 |
| Barbosa Lima | 1,9 | 0,0 | 0,1 | 0,4 | 1,0 | 0,0 | 0,0 | 0,0 | 0,0 |
| Serzedello Corrêa | 2,6 | 0,2 | 0,4 | 0,3 | 0,0 | 0,0 | 0,2 | 0,0 | 0,5 |
| Calógeras | 0,0 | 0,0 | 0,7 | 0,9 | 0,6 | 0,0 | 0,0 | 0,0 | 0,2 |
| Hermes da Fonseca | 0,0 | 0,1 | 0,3 | 1,1 | 1,4 | 1,0 | 1,4 | 0,7 | 0,7 |

O desenho é de **substituição, não de acumulação**. Campista domina 1906 a 1908 e
sai: dez ocorrências próximas por 100 páginas em 1906 contra zero em 1912.
Bulhões faz o movimento inverso, sobe de 0,3 em 1908 para 5,2 em 1910 e cai
depois. Barbosa Lima, Serzedello e Alcindo Guanabara concentram-se em 1906.
Calógeras aparece em 1908 e some depois de 1910.

As duas fases do debate têm elencos quase disjuntos, e o corte fica entre 1908 e
1909. Isso bate com a troca no Ministério da Fazenda, e é a mesma troca de
elenco que os dois volumes dos Documentos Parlamentares mostram.

**Ressalva que limita a leitura da série:** o ruído de OCR varia por célula
jornal-ano, de 4,84% a 14,33% em O Paiz. Parte da variação entre anos é
digitalização, não história. A série serve para ler entrada e saída de ator,
não para comparar níveis entre anos com precisão.

### 4.3 Por jornal

No limiar de 200, Campista aparece 83 vezes no Correio Paulistano, 68 em O Paiz,
47 na Gazeta e 37 no Correio da Manhã. Bulhões, 52 no Correio Paulistano e 17 na
Gazeta. O Correio Paulistano é o que mais nomeia perto da menção, o que é
coerente com o jornal que publicou a justificação técnica completa do projeto em
julho de 1906.

Um caso destoa: Pinheiro Machado tem 13 no Correio da Manhã, 11 no Correio
Paulistano, 8 em O Paiz e **zero** na Gazeta de Notícias.

### 4.4 Precisão, medida e não presumida

Sorteei 20 pares com distância até 200 caracteres e li cada um na página.

**Primeira medida, 12 acertos em 20, 60%**, intervalo de confiança de Wilson de
95% entre 34,6% e 74,1%. A leitura expôs um defeito nomeável: a escala da guarda
do quartel imprime "na caixa de conversão, tenente Peixoto", e a chave `peixoto`
sozinha transformava o alferes de serviço em Carlos Peixoto, a 28 caracteres da
menção. O deputado aparecia em terceiro lugar do ranking por causa disso.
Corrigi a chave para exigir o nome composto, fiz o mesmo com Custódio Coelho, e
o caso virou teste de regressão.

**Segunda medida, no instrumento corrigido e com sorteio independente, 16
acertos em 20, 80%**, intervalo de Wilson de 95% entre 54,4% e 87,9%. Três dos
quatro erros restantes são Hermes da Fonseca e um Martim Francisco advogado, ou
seja, adjacência de notas curtas na mesma coluna. Fora Hermes, a precisão da
amostra é 16 em 18.

Exemplos de acerto, para dar a medida do que o número quer dizer: "entende o sr.
Serzedello Correia que a caixa de conversão, como está, quebra o padrão
monetário" (O Paiz, 1906, distância 24); "a renúncia do saudoso sr. dr. Joaquim
Murtinho do cargo de senador, por ser infenso à caixa de conversão" (Correio
Paulistano, 1913, distância 49). Exemplo de erro: "chegou hoje a esta capital o
dr. Martim Francisco, advogado nos auditórios da comarca de Santos", seguido
imediatamente do boletim diário da Caixa (Correio Paulistano, 1910, distância
79).

### 4.5 O teto de recall, e o que ele escondia

O elenco de 52 nomes veio de fontes que já saíram do próprio corpus. Nome que
nenhuma delas registrou não podia aparecer, por mais frequente que fosse. Para
medir esse teto, rodei um ranking **aberto**, que colhe o nome depois de
tratamento ("o sr.", "o conselheiro", "o deputado") dentro de 1.000 caracteres
da menção, sem elenco definido de antemão.

O topo confirma o ranking fechado: David Campista com 349 ocorrências em 309
páginas, Leopoldo com 250, Hermes com 217, Pinheiro Machado com 169, Nilo
Peçanha com 163.

E revela o que faltava. **Francisco Salles**, ministro da Fazenda depois de
Bulhões, aparece 132 vezes, concentradas em 1911 com 47 e 1912 com 32, e não
estava no elenco. **Tavares de Lyra** aparece 146 vezes, concentradas em 1907 e
1908. Os dois entram na próxima versão do elenco.

O ranking aberto também confirma o artefato da guarda: `alferes` aparece 96
vezes, `meira` 106 e `frota` 77, todas concentradas entre 1910 e 1912, que é
exatamente o período em que a escala do quartel passa a listar a Caixa de
Conversão entre os postos de guarda.

O que nenhum dos dois rankings alcança continua fora: perífrase sem tratamento,
designação por cargo sem nome, e sobrenome sozinho quando ambíguo.

### 4.6 O contraste entre as duas bases

| nome | parlamento (menções) | imprensa (páginas a ≤200) |
|---|---|---|
| Barbosa Lima | 212 | 31 |
| David Campista | 193 | 235 |
| Calógeras | 120 | 24 |
| Affonso Costa | 80 | 12 |
| Leopoldo de Bulhões | 78 | 139 |
| Cincinato Braga | 69 | 9 |
| Hermes da Fonseca | 14 | 71 |
| Rothschild | 0 | 7 |

As duas bases não elegem os mesmos protagonistas. **O parlamento é dominado por
quem discursa contra**, com Barbosa Lima em primeiro e 105 turnos de fala. **A
imprensa é dominada por quem executa**, com Campista e Bulhões, os dois
ministros da Fazenda do período, somando mais que todo o resto do elenco junto
no limiar de 200.

Isso é hipótese a testar, não conclusão: a explicação óbvia é que o jornal
noticia ato de governo com nome de ministro todo dia, enquanto o debate de
plenário é onde o adversário fala. Antes de virar afirmação histórica precisa
passar pela leitura das peças, com o campo `voz` separando notícia de ato,
relato de sessão e editorial.

O caso de Rothschild é o mais nítido dos dois lados: zero menção nos dois volumes
parlamentares, sete páginas de jornal com o nome a menos de 200 caracteres da
menção, e 1.464 ocorrências no acervo inteiro, quase todas longe da Caixa. O
banqueiro externo aparece no jornal e não aparece no plenário. Vale conferir na
página antes de afirmar, porque a hipótese concorrente é que o plenário o trate
por perífrase e por cargo, exatamente o que a medida não alcança.

## 5. Reprodução

```bash
uv run python -m pipeline.analise.nomes_no_debate
```

```bash
uv run python -m pipeline.analise.relatorio_nomes --limiar 200
```

```bash
uv run python -m pipeline.analise.nomes_parlamentares
```

```bash
uv run python -m pipeline.analise.nomes_abertos
```

Elenco em `pipeline/analise/elenco_debate.csv`, exclusões em
`pipeline/analise/exclusoes_variantes_nomes.csv`, manifestos em
`dados/analise/`. Testes em `tests/test_nomes_no_debate.py`.

## 6. O que fazer com isto

1. **Acrescentar Francisco Salles e Tavares de Lyra ao elenco** e rodar de novo.
   São 15 minutos de máquina.
2. **Decidir se a escala da guarda entra na lista de exclusão por padrão.** Ela
   é ruído para nome e sinal para outra coisa: a Caixa vira posto de guarda
   militar entre 1910 e 1912, o que é fato sobre a instituição.
3. **Levar a hipótese do executivo contra o plenário para a leitura das peças.**
   O campo `voz` da ficha existe para isso e está zerado nas 185 linhas.
4. **Não publicar número desta medida sem a conferência na página.** A precisão
   medida é de 80% com intervalo entre 54,4% e 87,9%, sobre 20 casos. Para
   sustentar afirmação em capítulo, a amostra tem de crescer.
