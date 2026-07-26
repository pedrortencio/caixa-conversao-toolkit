# Qualidade do OCR embutido por célula jornal-ano

Medida determinística (`pipeline/analise/qualidade_ocr.py`), sem API e sem léxico externo, sobre amostra determinística de 25 páginas por célula (semente 20260725). Serve de controle para a análise lexical distintiva: diferença de digitalização entre grupos vira palavra distintiva do grupo pior digitalizado.

`sem_vogal` = tokens sem nenhuma vogal, quase sempre lixo de OCR. `hapax` = proporção do vocabulário que ocorre uma só vez. `compr` = comprimento médio do token, que cai quando o OCR fragmenta palavra.

| jornal | ano | páginas | chars/pág | sem_vogal | hapax | compr |
|---|---|---|---|---|---|---|
| correio_manha | 1906 | 2690 | 37562 | 10.78% | 82.7% | 4.58 |
| correio_manha | 1907 | 2958 | 38246 | 10.84% | 84.4% | 4.66 |
| correio_manha | 1908 | 3298 | 41206 | 14.78% | 84.1% | 4.30 |
| correio_manha | 1909 | 3198 | 39925 | 8.85% | 79.7% | 4.80 |
| correio_manha | 1910 | 3485 | 40274 | 14.07% | 82.2% | 4.38 |
| correio_manha | 1911 | 4157 | 32355 | 13.92% | 82.6% | 4.36 |
| correio_manha | 1912 | 4810 | 40096 | 14.09% | 81.8% | 4.21 |
| correio_manha | 1913 | 5032 | 41872 | 13.58% | 81.5% | 4.23 |
| correio_manha | 1914 | 4248 | 42890 | 13.70% | 81.8% | 4.21 |
| correio_paulistano | 1906 | 2074 | 36219 | 6.56% | 78.4% | 4.95 |
| correio_paulistano | 1907 | 2183 | 33009 | 6.46% | 77.6% | 4.90 |
| correio_paulistano | 1908 | 1688 | 31082 | 7.29% | 77.1% | 4.82 |
| correio_paulistano | 1909 | 2586 | 36515 | 6.95% | 76.9% | 4.92 |
| correio_paulistano | 1910 | 2800 | 30833 | 6.30% | 76.1% | 5.01 |
| correio_paulistano | 1911 | 3556 | 32629 | 6.76% | 75.7% | 4.98 |
| correio_paulistano | 1912 | 3904 | 34943 | 7.69% | 78.9% | 4.94 |
| correio_paulistano | 1913 | 4064 | 29770 | 10.05% | 78.7% | 4.85 |
| correio_paulistano | 1914 | 3168 | 36447 | 9.24% | 76.8% | 4.85 |
| gazeta_noticias | 1906 | 2696 | 40970 | 10.29% | 79.5% | 4.49 |
| gazeta_noticias | 1907 | 2428 | 41913 | 10.74% | 83.7% | 4.60 |
| gazeta_noticias | 1908 | 2513 | 38500 | 12.17% | 84.4% | 4.48 |
| gazeta_noticias | 1909 | 2860 | 34505 | 10.07% | 80.9% | 4.39 |
| gazeta_noticias | 1910 | 2912 | 32845 | 11.56% | 80.9% | 4.25 |
| gazeta_noticias | 1911 | 2848 | 36154 | 9.03% | 80.3% | 4.59 |
| gazeta_noticias | 1912 | 1850 | 33369 | 8.42% | 77.7% | 4.59 |
| gazeta_noticias | 1914 | 2436 | 33133 | 9.34% | 82.3% | 4.67 |
| o_paiz | 1906 | 2472 | 43706 | 14.33% | 85.0% | 4.21 |
| o_paiz | 1907 | 1886 | 40820 | 7.67% | 79.8% | 4.81 |
| o_paiz | 1908 | 3376 | 39935 | 11.37% | 81.7% | 4.50 |
| o_paiz | 1909 | 3816 | 34856 | 4.84% | 73.6% | 4.95 |
| o_paiz | 1910 | 5007 | 31744 | 7.89% | 77.1% | 4.65 |
| o_paiz | 1911 | 4924 | 34513 | 6.03% | 76.1% | 4.84 |
| o_paiz | 1912 | 4694 | 37122 | 6.77% | 77.1% | 4.72 |
| o_paiz | 1913 | 6045 | 35338 | 6.08% | 74.6% | 4.78 |
| o_paiz | 1914 | 5041 | 34386 | 5.73% | 74.3% | 4.92 |

## Amplitude dentro de cada jornal

A variação de um jornal entre seus próprios anos é o que decide se a comparação entre FASES (rodada 2) também está confundida, e não só a comparação entre jornais (rodada 3).

| jornal | sem_vogal mín | sem_vogal máx | razão máx/mín |
|---|---|---|---|
| correio_manha | 8.85% (1909) | 14.78% (1908) | 1.7x |
| correio_paulistano | 6.30% (1910) | 10.05% (1913) | 1.6x |
| gazeta_noticias | 8.42% (1912) | 12.17% (1908) | 1.4x |
| o_paiz | 4.84% (1909) | 14.33% (1906) | 3.0x |
