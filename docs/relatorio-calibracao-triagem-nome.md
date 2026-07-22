# Calibração da triagem por nome contra o gabarito 1906

Gerado em 2026-07-21T23:22:52+00:00. Regra: `triagem/nome-caixa-conversao 1.0.0`. Escopo: piloto 1906, agregado por objeto digital (proxy 1:1 da edição-dia). Estadão fora (não está no acervo digital da BN).

## Recall sobre os positivos do gabarito

Critério: das edições que o piloto codificou com menção/posição, quantas a regra por nome sinaliza como relevantes. Recall baixo = OCR garbled demais para o nome; mede o que a camada 2 (termos) recuperaria.

| Jornal | bib | positivos | recuperados | recall | perdidos |
|---|---|---|---|---|---|
| o_paiz | 178691 | 45 | 41 | 0.911 | per178691_1906_08014, per178691_1906_08090, per178691_1906_08114, per178691_1906_08117 |
| correio_manha | 089842 | 68 | 66 | 0.971 | per089842_1906_01824, per089842_1906_01837 |
| correio_paulistano | 090972 | 44 | 43 | 0.977 | per090972_1906_15338 |
| gazeta_noticias | 103730 | 74 | 69 | 0.932 | per103730_1906_00058, per103730_1906_00130, per103730_1906_00241, per103730_1906_00284, per103730_1906_00331 |
| **Total** | | **231** | **219** | **0.948** | |

## Sonda de precisão sobre os "No Relevant Mentions Found"

Não é precisão medida: os negativos do gabarito vêm de busca da BN, não de leitura de toda página. Um hit da regra aqui é candidato a menção que o método antigo perdeu, para inspeção humana.

| Jornal | bib | não-relevantes | com hit da regra | flagados |
|---|---|---|---|---|
| o_paiz | 178691 | 33 | 29 | per178691_1906_07831, per178691_1906_07842, per178691_1906_07849, per178691_1906_07885, per178691_1906_07890, per178691_1906_07892, per178691_1906_07908, per178691_1906_07912, per178691_1906_07942, per178691_1906_07947, per178691_1906_07958, per178691_1906_07959, per178691_1906_07996, per178691_1906_07997, per178691_1906_08000 (+14) |
| correio_manha | 089842 | 36 | 34 | per089842_1906_01751, per089842_1906_01754, per089842_1906_01765, per089842_1906_01775, per089842_1906_01806, per089842_1906_01820, per089842_1906_01857, per089842_1906_01876, per089842_1906_01878, per089842_1906_01880, per089842_1906_01886, per089842_1906_01891, per089842_1906_01892, per089842_1906_01894, per089842_1906_01899 (+19) |
| correio_paulistano | 090972 | 48 | 48 | per090972_1906_15290, per090972_1906_15307, per090972_1906_15351, per090972_1906_15362, per090972_1906_15364, per090972_1906_15366, per090972_1906_15367, per090972_1906_15369, per090972_1906_15414, per090972_1906_15428, per090972_1906_15429, per090972_1906_15441, per090972_1906_15446, per090972_1906_15448, per090972_1906_15453 (+33) |
| gazeta_noticias | 103730 | 70 | 67 | per103730_1906_00072, per103730_1906_00092, per103730_1906_00097, per103730_1906_00098, per103730_1906_00100, per103730_1906_00106, per103730_1906_00110, per103730_1906_00112, per103730_1906_00114, per103730_1906_00120, per103730_1906_00126, per103730_1906_00128, per103730_1906_00168, per103730_1906_00172, per103730_1906_00174 (+52) |

## Avisos

- 178691: 1 saída(s) inválida(s) do piloto (não codificável), fora das duas métricas.
- 089842: 2 saída(s) inválida(s) do piloto (não codificável), fora das duas métricas.
- 089842: 2 id(s) do gabarito sem objeto no censo: per089842_1906_01869, per089842_1906_01870.
- 090972: 1 id(s) do gabarito sem objeto no censo: per090972_1906_15276.
- 103730: 1 saída(s) inválida(s) do piloto (não codificável), fora das duas métricas.
- 103730: 1 id(s) do gabarito sem objeto no censo: per103730_1906_00078.
