# Tesseract contra o OCR da Biblioteca Nacional: resultado negativo

**Data:** 2026-08-12. **Instrumento:** `pipeline/transcricao/ocr_tesseract.py`,
protocolo `ocr-tesseract-scans-bn` 1.0.0, 26 testes. **Custo de API: zero.**
Motor: tesseract 5.4.0.20240606 (UB Mannheim), leptonica 1.84.1, `por.traineddata`
das três variantes (`best`, `fast`, `std`).

**Este documento existe para que ninguém refaça este trabalho.** A hipótese era
razoável e foi testada. Ela não passou.

---

## 1. A hipótese e o veredito

**Hipótese:** o OCR embutido nos PDFs da BN é sujo, então reler as mesmas
imagens com um motor próprio produziria uma camada de texto mais inteligível
por máquina, a custo zero de orçamento.

**Veredito:** não. Em todas as configurações testadas, o Tesseract encontra
**menos** menções à Caixa de Conversão que a camada da BN e **nunca encontra
uma que a BN não tenha encontrado**. Em 244 páginas que sabidamente trazem o
nome, a sensibilidade do Tesseract é **0,607** (IC 95%: 0,544 a 0,666), e as
páginas achadas só por ele são **zero**.

Substituir a camada da BN perderia cerca de 39% das páginas com menção. Unir as
duas camadas não ganha nada, porque o conjunto do Tesseract é subconjunto do da
BN.

## 2. O que enganaria quem parasse cedo

A primeira medida, num cabeça a cabeça de 70 páginas sorteadas duas por célula
jornal-ano, parecia excelente:

| métrica | camada da BN | Tesseract psm 3 |
|---|---|---|
| `sem_vogal` (ruído) | 10,08% | **4,66%** |
| `hapax` | 81,3% | 81,9% |
| comprimento médio de token | 4,63 | 4,54 |
| células em que ganhou | 0 de 35 | **35 de 35** |

Redução de mais da metade do ruído, unânime nas 35 células. Com esse número
sozinho a decisão teria sido disparar a rodada do corpus.

**A checagem que derrubou isso** foi contar tokens. O Tesseract entregava 22,6%
menos texto. Um motor que se recusa a emitir o trecho difícil melhora qualquer
métrica de ruído sem ter lido melhor nada. A razão de tokens por página era
bimodal: mediana 0,86, mas 16 das 70 páginas abaixo de 0,60, com casos de 0,17 e
0,03, ou seja, página inteira desaparecendo. Isso é falha de análise de layout,
não de reconhecimento.

Lição que vale para além deste teste: **métrica de ruído sem métrica de volume
mede omissão e chama de limpeza.**

## 3. As correções tentadas

O diagnóstico apontava resolução. O JPEG embutido tem cerca de 2016x2985 px, o
que numa página de jornal dá perto de 135 DPI, metade do que o Tesseract espera.

| tentativa | resultado |
|---|---|
| `psm 4` (coluna única) | pior que `psm 3` no ruído |
| `psm 6` (bloco uniforme) | pior, mistura as colunas |
| `psm 11` (texto esparso) | inviável: estourou 900 s numa única página |
| `psm 12` | não concluído, mesmo custo proibitivo |
| `fast` em vez de `best` | mesmo ruído, 1,6x mais rápido, recall pior |
| **ampliação 2x (Lanczos) antes do OCR** | corrigiu o volume, não corrigiu o recall |

A ampliação merece detalhe porque **funcionou para o que se propunha**. Nas 16
páginas em que o Tesseract mais falhava, os tokens subiram de 35.218 para 62.244.
No braço de sensibilidade inteiro, o déficit de tokens caiu de 16,7% para 4,4%.
O problema de layout era mesmo resolução.

**E a sensibilidade não subiu junto:** 0,607 para 0,634 (IC 95%: 0,572 a 0,693).
As páginas achadas só pelo Tesseract continuaram sendo zero. As menções
encontradas até caíram, de 232 para 215.

## 4. O braço de sensibilidade, que é a medida decisiva

Amostra determinística, semente 20260812, 7 páginas por célula jornal-ano,
sorteadas **entre as páginas que o censo marcou com menção**. Medir aqui é o que
permite dizer se o motor novo enxerga o que o antigo enxergou.

| medida | camada da BN | Tesseract nativo | Tesseract 2x |
|---|---|---|---|
| páginas comparadas | 244 | 244 | 238 |
| páginas em que o nome é achado | 244 | 148 | 151 |
| **sensibilidade** | (referência) | **0,607** | **0,634** |
| menções encontradas | 376 | 232 | 215 |
| tokens | 1.632.690 | −16,7% | −4,4% |
| **páginas achadas só pelo Tesseract** | | **0** | **0** |
| segundos por página por processo | | 45,9 | 88,0 |
| corpus estimado, 14 processos | | 107 h | 205 h |

A ampliação 2x introduziu ainda um modo de falha novo: 7 páginas voltaram vazias.

**A leitura conjunta das linhas de ruído e de sensibilidade é o achado real.** O
Tesseract produz menos lixo grosseiro (token sem nenhuma vogal cai pela metade) e
ao mesmo tempo erra mais o suficiente para quebrar o nome. São coisas
compatíveis: `sem_vogal` mede destruição grosseira, e o que arruína um casamento
de nome é o erro sutil de um caractere. O motor da BN, provavelmente comercial,
é melhor exatamente onde importa para busca.

## 5. Limite desta conclusão

A amostra foi sorteada entre páginas **com** menção, então ela mede sensibilidade
e não mede diretamente se o Tesseract acha menção em página que a BN perdeu por
completo. É uma inferência, não uma medida: um motor que acha zero páginas novas
em 244 onde o outro acerta dificilmente será complementar onde o outro falha, mas
"dificilmente" não é "não".

O teste que fecharia esse flanco é rodar o Tesseract sobre uma amostra das
páginas descartadas pelo censo, ou sobre as 2.211 que a sonda difusa sinalizou.
Cerca de 30 minutos de CPU. Não foi feito.

## 6. O que fica

**A camada da BN continua sendo a melhor base de busca disponível para este
corpus,** e isso agora é afirmação medida, não suposição herdada.

**O ganho de recall que existe é o da sonda difusa:** 2.194 páginas recuperadas,
IC 95% de 1.933 a 2.208, a custo de 179 segundos de CPU, documentado em
`docs/relatorio-sonda-difusa-2026-08-12.md`. É melhor retorno que qualquer coisa
que o OCR novo entregaria em 205 horas.

**Um uso residual sobrevive.** Com ampliação 2x o Tesseract entrega texto com
4,4% menos tokens e metade do lixo grosseiro, o que é melhor para **leitura
humana**. A cerca de 90 segundos por página, isso é viável sob demanda para as
poucas centenas de páginas de leitura próxima, e inviável para as 117.703. O
script já suporta isso: é retomável, aceita amostra, e a camada da BN nunca é
tocada.

**O que não deve ser feito:** rodar o corpus inteiro com Tesseract em qualquer
das configurações testadas. Enquanto a sensibilidade não passar de 0,95, a
camada resultante encontra menos do que a que já temos.

## 7. Advertência

Concordância entre dois OCRs não é verdade. Os dois leem a mesma imagem degradada
e podem errar junto, com erro correlacionado. Consenso é sinal de confiabilidade,
nunca validação. Vale também para a discordância medida aqui: que a BN ache mais
não prova que ela esteja certa, prova que ela emite mais forma casável. A última
palavra continua sendo a imagem da página.

## Onde ficou cada coisa

| arquivo | o que é |
|---|---|
| `pipeline/transcricao/ocr_tesseract.py` | o instrumento, protocolo 1.0.0 |
| `tests/test_ocr_tesseract.py` | 26 testes |
| `dados/transcricao/ocr_tesseract/manifesto_varredura_*.csv` | varredura de parâmetro |
| `dados/transcricao/ocr_tesseract/manifesto_sensibilidade_*.csv` | os dois braços de sensibilidade |
| `dados/transcricao/ocr_tesseract/relatorio_*.json` | motor, versão, parâmetros, tempos |
| `C:\dados-caixa\tessdata\{best,fast,std}` | os `traineddata` baixados |
| `C:\dados-caixa\_varredura\` | texto das rodadas de teste, descartável |
