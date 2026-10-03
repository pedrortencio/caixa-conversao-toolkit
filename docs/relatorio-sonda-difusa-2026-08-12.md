# Sonda difusa: quanto o censo por nome perdeu

**Data de execução:** 2026-08-12. **Fase 0** da tarefa de segunda testemunha de
OCR. **Custo de API: zero.** Tempo de máquina: 179 segundos para o corpus
inteiro, 14 processos.

**Instrumento:** `pipeline/triagem/sonda_difusa.py`, protocolo
`sonda-difusa-caixa-conversao` 1.0.0, e `pipeline/triagem/inspeciona_sonda.py`,
protocolo `inspecao-sonda-difusa` 1.0.0. 52 testes novos, suíte inteira em 520
testes verdes. Manifestos em `dados/triagem/sonda_difusa/`.

---

## 1. A resposta, em um parágrafo

O censo por nome marcou **8.331 páginas** com menção à Caixa de Conversão e
descartou 109.372. Varrendo as descartadas com um casador deliberadamente mais
tolerante e corrigindo a contagem pela precisão medida por leitura, a estimativa
é de **2.194 páginas perdidas** (IC 95%: 1.933 a 2.208). O censo, portanto,
enxerga cerca de **79% das páginas que mencionam a Caixa pelo nome**, e o número
8.331 subestima o total em torno de **20,8%**. A perda não é uniforme: vai de
7,1% no Correio Paulistano de 1908 a 34,4% na Gazeta de Notícias de 1914.

O número de 8.331 não pode ser apresentado ao Ivan sem essa ressalva. E a
variação por célula é o problema mais sério, porque comparação entre jornais ou
entre anos está confundida por uma taxa de perda que difere por célula.

## 2. Como a sonda funciona, e por que ela é cota inferior

O casador do censo (`regra_nome`, protocolo `nome-caixa-conversao` 1.0.0) é
tolerante a ruído, mas exato no radical: exige a sequência `caixa`, conector
curto começando por `d`, e o radical `conver`. A sonda relaxa isso em duas
etapas.

1. **Geração de candidatos.** Expressão regular que casa `caixa` com até um
   erro (substituição, deleção ou inserção), vão de até 6 caracteres, e `conver`
   com até um erro. Roda em C sobre o texto normalizado pela mesma função do
   censo, a cerca de 34 MB/s.
2. **Pontuação.** Para cada candidato, a distância de edição de Levenshtein
   entre a forma canônica `caixa de conversao` e a melhor subcadeia da janela,
   com início e fim livres do lado da janela.

Os dois instrumentos são módulos separados de propósito. A sonda importa
`regra_nome` e não o altera, e há teste travando isso. Trocar o casador
deslocaria o portão de 1906, cujo gabarito de 426 números distintos é medido
contra o censo atual.

**Por que o número é cota inferior, não estimativa completa.** A sonda precisa
das duas âncoras razoavelmente inteiras. Ela não acha página em que o OCR
destruiu `caixa` e `conver` ao mesmo tempo, nem menção que não usa o nome
(anáfora, "a Caixa", "o troco"). Esse flanco só fecha com OCR novo, que é a
Fase 1.

## 3. A calibração: precisão medida por leitura, não presumida

A contagem de máquina não é taxa de falso negativo, porque a sonda também acerta
ruído. Sorteei uma amostra estratificada por distância, 30 candidatos por faixa,
240 no total, semente 20260812 registrada, e li os 240 trechos com contexto.

| distância | genuínos / lidos | precisão | IC 95% |
|---|---|---|---|
| 1 | 30/30 | 1,000 | 0,886 a 1,000 |
| 2 | 30/30 | 1,000 | 0,886 a 1,000 |
| 3 | 29/30 | 0,967 | 0,833 a 0,994 |
| 4 | 18/30 | 0,600 | 0,423 a 0,754 |
| 5 | 23/30 | 0,767 | 0,591 a 0,882 |
| 6 | 5/30 | 0,167 | 0,073 a 0,336 |
| 7 | 4/30 | 0,133 | 0,053 a 0,297 |
| 8 | 1/30 | 0,033 | 0,006 a 0,167 |

A precisão não cai de forma monótona, e a razão é concreta: `caixas de
conservas` fica a distância exatamente 4 e 6 da forma canônica, e o corpus tem
milhares de linhas de manifesto de carga de navio. A distância 5 pega menos
delas do que a 4. Por isso a estimativa pondera cada faixa pela sua própria
precisão, em vez de aplicar uma média.

**O limiar de decisão é 3.** Acima disso a precisão desaba. Abaixo dela a leitura
não encontrou praticamente nada que não fosse a Caixa: em 90 trechos lidos nas
faixas 1 a 3, o único falso positivo foi uma "caixa de conservas que continha
uma lâmpada de essência".

**Quem leu foi um modelo, não você.** A amostra está em
`dados/triagem/sonda_difusa/amostra_inspecao.csv` com a coluna `julgado_por`, e o
julgamento é reconferível linha a linha. Os casos que considerei mais
discutíveis, e que valem sua releitura, são dois: "porteiro da caixa dc
convencao, joaquim" (lista de jurados, julguei genuíno porque a Caixa de
Conversão tinha porteiro e "Caixa de Convenção" não existia) e "caixa de
convenio / entradas: libras 1.798" (julguei genuíno porque é o boletim diário de
movimento). Se os dois virarem falso positivo, a estimativa cai pouco, cerca de
30 páginas.

## 4. O número, por célula jornal-ano

Estimativa com limiar 3, ponderada pela precisão da faixa. "% a mais" é o quanto
a célula cresceria em relação ao que o censo já tem.

| jornal | ano | censo | estimadas perdidas | % a mais |
|---|---|---|---|---|
| correio_manha | 1906 | 133 | 34 | 20,6% |
| correio_manha | 1907 | 200 | 57 | 22,3% |
| correio_manha | 1908 | 59 | 25 | 29,4% |
| correio_manha | 1909 | 204 | 40 | 16,2% |
| correio_manha | 1910 | 336 | 101 | 23,1% |
| correio_manha | 1911 | 295 | 88 | 23,0% |
| correio_manha | 1912 | 254 | 67 | 21,0% |
| correio_manha | 1913 | 302 | 60 | 16,5% |
| correio_manha | 1914 | 252 | 64 | 20,2% |
| correio_paulistano | 1906 | 116 | 22 | 15,8% |
| correio_paulistano | 1907 | 152 | 24 | 13,5% |
| correio_paulistano | 1908 | 220 | 17 | 7,1% |
| correio_paulistano | 1909 | 276 | 44 | 13,7% |
| correio_paulistano | 1910 | 268 | 62 | 18,7% |
| correio_paulistano | 1911 | 227 | 53 | 18,8% |
| correio_paulistano | 1912 | 200 | 29 | 12,6% |
| correio_paulistano | 1913 | 87 | 17 | 16,2% |
| correio_paulistano | 1914 | 221 | 35 | 13,6% |
| gazeta_noticias | 1906 | 219 | 41 | 15,7% |
| gazeta_noticias | 1907 | 275 | 83 | 23,2% |
| gazeta_noticias | 1908 | 150 | 78 | 34,2% |
| gazeta_noticias | 1909 | 221 | 75 | 25,2% |
| gazeta_noticias | 1910 | 406 | 119 | 22,7% |
| gazeta_noticias | 1911 | 320 | 121 | 27,5% |
| gazeta_noticias | 1912 | 95 | 47 | 33,0% |
| gazeta_noticias | 1914 | 89 | 47 | 34,4% |
| o_paiz | 1906 | 102 | 28 | 21,4% |
| o_paiz | 1907 | 200 | 31 | 13,3% |
| o_paiz | 1908 | 258 | 24 | 8,4% |
| o_paiz | 1909 | 344 | 30 | 8,0% |
| o_paiz | 1910 | 442 | 97 | 17,9% |
| o_paiz | 1911 | 518 | 153 | 22,8% |
| o_paiz | 1912 | 281 | 145 | 34,1% |
| o_paiz | 1913 | 343 | 125 | 26,7% |
| o_paiz | 1914 | 266 | 115 | 30,2% |

| jornal | censo | perdidas | % a mais |
|---|---|---|---|
| Correio da Manhã | 2.035 | 536 | 20,8% |
| Correio Paulistano | 1.767 | 301 | 14,6% |
| Gazeta de Notícias | 1.775 | 610 | 25,6% |
| O Paiz | 2.754 | 747 | 21,3% |
| **total** | **8.331** | **2.194** | **20,8%** |

A Gazeta perde uma em cada quatro páginas, o Correio Paulistano uma em cada
sete. Essa diferença de 11 pontos entre jornais é diferencial de digitalização,
não de conteúdo, e entra direto em qualquer comparação de saliência entre
títulos.

**A perda não é explicada pelo ruído global de OCR.** Correlacionando a taxa de
perda por célula com a métrica `sem_vogal` de `docs/relatorio-qualidade-ocr.md`,
sobre as 35 células pareadas: ρ de Spearman = 0,229 (p = 0,186), r de Pearson =
0,194 (p = 0,264). Nenhum dos dois é significativo. Ou seja, não dá para usar a
métrica de ruído já existente como proxy da perda de recall, e corrigir por ela
seria corrigir pela coisa errada.

## 5. O que causou as perdas

Classifiquei os 2.374 candidatos a distância no máximo 3 nas páginas descartadas
por um critério mecânico: colar o trecho removendo tudo que não é letra ou
dígito e perguntar se o casador do censo passaria a achá-lo.

| causa | candidatos | fração |
|---|---|---|
| letra trocada pelo OCR | 1.447 | 61,0% |
| pontuação ou espaço dentro do nome | 927 | 39,0% |

Os 39% de pontuação e espaço são formas como `caixa de con-versao` com hífen
fora de quebra de linha, `caixa de. conversao`, `ca xa de conversao`,
`caixa.de conversao`. São perdas que uma normalização determinística
recuperaria, sem OCR novo e sem julgamento. **Não mexi no casador**, porque
mexer nele desloca o portão de 1906 e a decisão é sua.

Os 61% restantes são letra trocada dentro do nome (`caixa rio conversao`,
`caixa dc convorsao`, `cnixa de conversro`) e exigem tolerância a erro, que é o
que a sonda faz e o casador exato não faz por desenho.

## 6. Achado colateral: as páginas que o censo já tem também perdem menções

No braço de calibração, as 8.331 páginas que o censo marcou, a sonda encontrou
**1.914 candidatos a distância no máximo 3 fora do span que o casador exato
achou**, distribuídos em 1.412 páginas. São menções adicionais na mesma página,
corrompidas pelo OCR.

Isso não muda a contagem de páginas, que é a unidade do censo. Muda a contagem
de menções, que é a base de qualquer medida de saliência ou intensidade. Se
alguma análise futura contar menções por página ou por edição, esse déficit
precisa entrar.

## 7. Verificações feitas

- **Determinismo.** Rodada de 8.000 páginas com 14 e com 7 processos: os quatro
  arquivos de saída saíram com sha256 idêntico.
- **Consistência com o censo.** Zero páginas descartadas têm candidato a
  distância 0. Se houvesse, um dos dois instrumentos estaria errado.
- **Cobertura.** 117.705 páginas examinadas, que é o total do censo. 117.703 com
  texto, 2 com o arquivo ausente no acervo, gravadas como linha em
  `falhas.csv` com status próprio, nunca omitidas.
- **Testes.** 52 testes novos, incluindo sete trechos reais transcritos do
  acervo que o casador exato comprovadamente perde. Suíte inteira: 520 testes.

## 8. Advertência que vale para esta fase e para a próxima

Concordância entre dois leitores da mesma imagem degradada não é verdade. Os
dois leem o mesmo scan e podem errar junto, com erro correlacionado. Consenso é
sinal de confiabilidade, nunca validação, e essa frase precisa aparecer em
qualquer relatório que use a segunda testemunha.

A sonda difusa não é exceção. Ela lê o mesmo OCR da BN que o censo leu. O que
ela adiciona não é uma leitura independente da página, é uma tolerância maior
sobre a mesma leitura. Independência de fato só vem de OCR novo sobre a imagem,
que é a Fase 1.

## 9. Estado das fases 1 e 2

**Fase 1, piloto do Tesseract: bloqueada.** Conferido nesta sessão, `tesseract
--version` responde "command not found" e `where tesseract` não acha nada. Não
instalei nada. Para destravar, a sugestão é a build UB Mannheim com o
`traineddata` do português:

```
winget install UB-Mannheim.TesseractOCR
```

e conferir que `por.traineddata` está em `tessdata`. Depois disso o piloto são
dois braços, cerca de 3.000 páginas sorteadas entre as descartadas e cerca de
400 entre as com menção, aproximadamente uma hora de CPU somando os dois, custo
zero de orçamento.

**Fase 2, corpus inteiro: não executada, por instrução.** Estimativa de custo,
com o parâmetro de 15 s por página e 14 processos: 117.703 páginas dão cerca de
**35 horas de CPU de fundo**, custo zero de orçamento e zero de token. O
parâmetro de 15 s por página não pude verificar, porque o Tesseract não está
instalado. Não há custo de disco se a imagem for extraída, passada ao OCR e
descartada, que é como o script deve ser escrito.

## 10. Decisões que são suas

1. **Adotar ou não o censo corrigido.** Adotar desloca o portão de 1906, que
   mede contra o censo atual com gabarito de 426 números distintos. Pede entrada
   em `docs/decisoes.md`.
2. **Se o número 8.331 sai com ressalva.** Minha leitura é que sim, e a ressalva
   é de uma frase: o censo por nome recupera cerca de 79% das páginas que
   mencionam a Caixa, com perda que varia de 7% a 34% conforme a célula
   jornal-ano.
3. **Se vale corrigir a normalização** para recuperar os 39% de perdas por
   pontuação e espaço. É barato e determinístico, mas é mudança de instrumento
   de medição.
4. **Se a Fase 1 roda.** Depende de instalar o Tesseract.
5. **A auditoria de recall de 64 edições** em
   `dados/leitura/auditoria_recall_edicoes.csv` está com a coluna
   `achou_mencao_na_leitura` inteiramente vazia. Ela ainda não é estimativa de
   nada. Se for preenchida agora, vira validação humana da estimativa da
   máquina, que é o papel mais valioso que ela pode ter.

---

## Onde ficou cada coisa

| arquivo | o que é |
|---|---|
| `pipeline/triagem/sonda_difusa.py` | a sonda, protocolo 1.0.0 |
| `pipeline/triagem/inspeciona_sonda.py` | sorteio, apuração e estimativa |
| `tests/test_sonda_difusa.py` | 28 testes |
| `tests/test_inspeciona_sonda.py` | 24 testes |
| `dados/triagem/sonda_difusa/candidatos.csv` | 17.440 candidatos com contexto |
| `dados/triagem/sonda_difusa/celulas.csv` | contagens por célula e braço |
| `dados/triagem/sonda_difusa/trechos_para_inspecao.csv` | 200 trechos junto do limiar |
| `dados/triagem/sonda_difusa/amostra_inspecao.csv` | 240 trechos com julgamento |
| `dados/triagem/sonda_difusa/apuracao_inspecao.json` | precisão e estimativa |
| `dados/triagem/sonda_difusa/relatorio.json` | manifesto da rodada, com hashes |
| `dados/triagem/sonda_difusa/falhas.csv` | as 2 páginas sem arquivo |
