# Relatório de limpeza da amostra recuperada

Limpeza determinística (`pipeline/triagem/limpa_amostra.py`, sem API/LLM). `keep` = peça válida para rotular; `falha` = visão não capturou o trecho que o OCR indica (registro não determinado); os `drop_*` são ruído de sobreinclusão da recuperação. Perdas por ano para a comparação temporal não ser enviesada por descarte silencioso.

| ano | total | keep | drop_disclaimer | drop_trecho_vazio | drop_amortizacao | drop_sem_nome | falha | keep% | falha% |
|---|---|---|---|---|---|---|---|---|---|
| 1906 | 97 | 55 | 20 | 5 | 2 | 14 | 0 | 57% | 0% |
| 1907 | 82 | 50 | 23 | 2 | 0 | 7 | 0 | 61% | 0% |
| 1908 | 95 | 54 | 33 | 0 | 0 | 8 | 0 | 57% | 0% |
| 1909 | 91 | 57 | 17 | 3 | 8 | 6 | 0 | 63% | 0% |
| 1910 | 115 | 71 | 24 | 1 | 1 | 18 | 0 | 62% | 0% |
| 1911 | 73 | 47 | 11 | 0 | 2 | 12 | 1 | 64% | 1% |
| 1912 | 78 | 40 | 15 | 9 | 1 | 13 | 0 | 51% | 0% |
| 1913 | 68 | 40 | 17 | 6 | 1 | 4 | 0 | 59% | 0% |
| 1914 | 88 | 54 | 20 | 0 | 2 | 12 | 0 | 61% | 0% |
| **tot** | **787** | **468** | **180** | **26** | **17** | **94** | **1** | **59%** | **0%** |

Sem data resolvida (`data_confiavel=0`, coluna `data` vazia): 37 de 787. O ano segue conhecido por `source_year`, que é a chave de ano de toda contagem; `data` só entra onde `data_confiavel=1`, e apenas para série mensal.

Datas confiáveis em ano diferente do `source_year`: 1. São edições de virada de ano, em que o masthead manda sobre o rótulo de ano da pasta do acervo; contadas aqui porque mudam de balde numa contagem por data.
