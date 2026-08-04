# Manifestos de análise

Nenhum arquivo desta pasta é instrumento de medição do objeto 2. São medidas
exploratórias do objeto 1, o mapeamento descritivo, e nenhuma linha vale como
citação sem conferência na página.

## `referente_argentino.csv`

Uma linha por janela de menção do corpus triado, com a classe do referente
(`estrita`, `moeda`, `nenhuma`). Gerado por
`pipeline/analise/referente_argentino.py`. Contexto em
`docs/nota-referente-argentino.md`.

## `nomes_distancia.csv`

Uma linha por par (página, ator) nas 8.331 páginas com menção da Caixa, com a
distância mínima em caracteres entre o nome e a menção mais próxima. Gerado por
`pipeline/analise/nomes_no_debate.py`.

Colunas: `bib`, `jornal`, `ano`, `objeto`, `pagina`, `nome`, `classe`,
`ocorrencias_na_pagina`, `distancia_minima`, `mencoes_na_pagina`,
`chars_pagina`.

A distância é medida no texto normalizado, e a ordem de leitura do OCR da BN
não respeita coluna de forma confiável. Ela separa adjacência de vizinhança
argumentativa e ordena candidatos, não é métrica final.

## `nomes_variantes_ocr.csv`

Toda forma do vocabulário que o casamento tolerante aceitou como representando
um token-chave, com frequência. É a tabela de conferência da medida acima: quem
duvidar de um número olha aqui primeiro. As formas recusadas estão em
`pipeline/analise/exclusoes_variantes_nomes.csv`, com o motivo de cada uma.

## `perifrase_banqueiro.csv`

Uma linha por ocorrência de perífrase ou cargo que designa o credor externo sem
nomeá-lo, nas 8.331 páginas com menção, com família, padrão, confiança declarada
e distância até a menção. Gerado por `pipeline/analise/perifrase_banqueiro.py`,
padrões versionados em `pipeline/analise/padroes_perifrase_banqueiro.csv`.

Piso de descoberta, nunca censo: não existe lista fechada das formas que a língua
de 1906 usava para dizer credor, e o recall não é estimável por dentro.

## `mencoes_credor_externo.csv`

As citações curadas do relatório `docs/relatorio-credor-externo-no-debate.md`,
com localizador, tema, forma de designação e o trecho verbatim. **Todas passam
por conferência mecânica** em `pipeline/analise/verifica_citacoes.py`, que exige
que a citação normalizada seja substring literal da fonte. A coluna
`conferido_na_imagem` indica se alguém leu a página, e não a camada de texto.

## `nomes_documentos_parlamentares.json`

Menções e turnos de fala por ator nos dois volumes de *Documentos
Parlamentares*, gerado por `pipeline/analise/nomes_parlamentares.py`. O insumo é
a camada corrigida, que em 2026-08-03 ainda não tem rotina versionada no repo.
