# Relatório de limpeza da amostra recuperada

Limpeza determinística (`pipeline/triagem/limpa_amostra.py`, sem API/LLM). `keep` = peça válida para rotular; `falha` = visão não capturou o trecho que o OCR indica (registro não determinado); os `drop_*` são ruído de sobreinclusão da recuperação. Perdas por ano para a comparação temporal não ser enviesada por descarte silencioso.

| ano | total | keep | drop_disclaimer | drop_trecho_vazio | drop_amortizacao | drop_sem_nome | falha | keep% | falha% |
|---|---|---|---|---|---|---|---|---|---|
| 1906 | 97 | 56 | 13 | 5 | 2 | 20 | 0 | 58% | 0% |
| 1907 | 82 | 53 | 20 | 2 | 0 | 7 | 0 | 65% | 0% |
| 1908 | 95 | 60 | 26 | 0 | 0 | 9 | 0 | 63% | 0% |
| 1909 | 91 | 59 | 14 | 3 | 8 | 7 | 0 | 65% | 0% |
| 1910 | 115 | 75 | 20 | 1 | 1 | 18 | 0 | 65% | 0% |
| 1911 | 73 | 48 | 10 | 0 | 2 | 12 | 1 | 66% | 1% |
| 1912 | 78 | 40 | 15 | 9 | 1 | 13 | 0 | 51% | 0% |
| 1913 | 68 | 40 | 17 | 6 | 1 | 4 | 0 | 59% | 0% |
| 1914 | 88 | 56 | 17 | 0 | 2 | 13 | 0 | 64% | 0% |
| **tot** | **787** | **487** | **152** | **26** | **17** | **103** | **1** | **62%** | **0%** |

Datas a conferir (`data_confiavel=0`): 37 de 787 (parser de OCR ou ano divergente do source_year).
