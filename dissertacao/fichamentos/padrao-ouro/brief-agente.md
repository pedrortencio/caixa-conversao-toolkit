# Brief para o agente de fichamento

Você vai produzir uma ficha de leitura acadêmica, em LaTeX e em português, de um
texto da literatura sobre o padrão-ouro. A ficha alimenta o capítulo 2 de uma
dissertação de mestrado em História Econômica (FFLCH-USP) sobre o debate da
imprensa brasileira acerca da Caixa de Conversão (1906-1914).

## O que você recebe

- `CHAVE`: a chave BibTeX da ficha (por exemplo `gremaud1997`).
- `PDF`: caminho do PDF original.
- `TEXTO`: caminho do texto extraído (`_texto/...txt`). Leia o texto inteiro.
  Se um trecho estiver ilegível (os três digitalizados têm ruído de OCR), abra a
  página correspondente do PDF com a ferramenta de leitura.
- `PARTE`: em qual parte do caderno a ficha entra (I a IV, ver abaixo).
- `RECORTE`: para livros e textos longos, quais capítulos ou seções ler.

## Contexto do capítulo, para as pontes com as fontes primárias

O capítulo 2 situa o debate brasileiro de 1906-1914 na discussão internacional
sobre o padrão monetário. Estrutura prevista: (I) o padrão-ouro como regra,
credibilidade e assimetria centro-periferia; (II) banqueiros, dívida soberana e
enforcement das instituições ortodoxas, com os Rothschild e o funding loan de
1898; (III) a importação das categorias inglesas (bulionismo, currency school e
banking school) pelo debate imperial entre metalistas e papelistas, e sua
herança nos agentes de 1906; (IV) caixas de conversão, com a Caja argentina
como comparação.

As fontes primárias são quatro jornais do Rio e de São Paulo (O Paiz, Correio
da Manhã, Gazeta de Notícias, Correio Paulistano) e os Documentos
Parlamentares. Os objetos do debate já identificados: o nível da taxa (12, 15
ou 27 pence por mil-réis), o limite de emissão da Caixa, os fundos de resgate e
de garantia, a competência da Caixa frente ao Tesouro e ao Banco do Brasil, a
agência de Londres, a custódia do ouro (1911), a suspensão de 1914. Agentes
recorrentes: David Campista, Leopoldo de Bulhões, Joaquim Murtinho, Serzedello
Corrêa, Alcindo Guanabara, Barbosa Lima, Rui Barbosa, os Rothschild. A
dissertação usa o eixo "ortodoxo, expansionista" como síntese analítica e
trata "metalista" e "papelista" como vocabulário de época. Uma ponte útil diz
o que procurar nos jornais, com que vocabulário, e que hipótese da literatura
esse achado confirmaria ou negaria. Não invente o que os jornais dizem.

## Formato da ficha

Grave em `fichas/CHAVE.tex`, usando as macros de `modelo-ficha.tex`:

```latex
\ficha{Autor (ano), título curto}{CHAVE}

\begin{identificacao}
Referência ABNT completa. Depois, em linha própria: tipo de texto, extensão
lida (páginas ou capítulos), idioma, e a versão lida se diferir da publicada
(por exemplo, working paper do NBER em lugar do artigo).
\end{identificacao}

\bloco{Problema e tese}
\bloco{Argumento}
\bloco{Conceitos e definições operacionais}
\bloco{Evidência e método}
\bloco{Agentes e vertentes}
\bloco{Críticas e limites}
\begin{dialogo} \item ... \end{dialogo}
\usonocapitulo{...}
```

- Problema e tese: um parágrafo. Que pergunta o texto responde e qual é a
  resposta.
- Argumento: os passos do raciocínio, em três a seis parágrafos curtos ou uma
  lista numerada. Cite página quando reproduzir uma afirmação específica,
  no formato `(p. 12)`.
- Conceitos: como o autor define padrão-ouro, conversibilidade, lastro,
  paridade, credibilidade, regra, currency board, ou o que for central no texto.
  Definições operacionais, não glossário.
- Evidência e método: fontes, dados, período, técnica, contrafactual.
- Agentes e vertentes: quem o texto nomeia (autores, escolas, políticos,
  banqueiros) e em que campo os situa. Se não houver, escreva "Não se aplica".
- Críticas e limites: o que o texto não sustenta, o que a literatura posterior
  contestou, o que não transfere para o caso brasileiro.
- Pontes para as fontes primárias: dois a cinco itens, cada um com o que
  procurar nos jornais e que hipótese da literatura isso testa.
- Uso no capítulo: em qual parte entra e para que afirmação serve.
- Citações-chave: até três, curtas, verbatim, com página, via
  `\chave{texto}{p. X}`. Podem aparecer dentro de qualquer bloco.

Extensão: 700 a 1.000 palavras para artigo, até 1.500 para livro ou leitura
seletiva. Econômico, sem repetir o resumo do próprio autor.

## Entrada BibTeX

Grave em `fichas/CHAVE.bib` uma entrada completa, com os dados conferidos no
PDF (autores, título, periódico, volume, número, páginas, ano, editora, DOI se
houver). Se leu um working paper, registre a versão publicada na entrada e
anote a versão lida na ficha. Se a chave já existir em
`bibliografia/referencias.bib`, ainda assim grave o `.bib` para conferência.

## Regras de escrita

- Sem travessões, nem em-dash nem en-dash. Vírgula no lugar. A compilação
  falha se houver um.
- Ortografia atual. Grafia de época só dentro de citação direta.
- Frases declarativas curtas. Nada de "cabe ressaltar", "é importante
  destacar", "nesse sentido".
- Terminologia: "padrão-ouro", "Caixa de Conversão", "mil-réis", "Convênio
  de Taubaté", "pence" (não "dinheiros").
- Citação direta sempre com página. Paráfrase sem página só para a tese geral.
- Não atribua ao texto o que ele não diz. Se o texto não trata do Brasil,
  diga isso no bloco de uso, em vez de forçar a ponte.
- LaTeX puro, sem pacotes além dos já carregados. Aspas duplas com dois
  acentos graves na abertura e dois apóstrofos no fechamento. Caracteres
  especiais escapados (porcentagem, e comercial, cifrão).

## Antes de terminar

Releia a ficha uma vez procurando só travessões, outra procurando afirmação
sem página onde a página era exigida, outra procurando frase que o texto não
sustenta. Confirme que os dois arquivos existem e que a ficha começa com
`\ficha{...}{CHAVE}`. Responda apenas com: chave, caminho dos dois arquivos,
número de palavras da ficha, e até três dúvidas de leitura que o orquestrador
deva conferir.
