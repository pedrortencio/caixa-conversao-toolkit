# Dissertação em LaTeX, rascunho zero, Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar um rascunho zero compilável e substancialmente preenchido da dissertação, com reaproveitamento rastreável da monografia, do relatório de qualificação e dos relatórios do repositório.

**Architecture:** A nova pasta `dissertacao/` conterá capítulos independentes da classe documental, configuração LaTeX isolada, bibliografia própria e notas editoriais visíveis controladas por uma chave global. A redação será cronológico-analítica, com quatro jornais como corpus principal e fontes parlamentares, legais, epistolares e comerciais como material acessório.

**Tech Stack:** LaTeX `report`, pdfLaTeX, BibTeX, `natbib`, PowerShell para verificação, Markdown para rastreabilidade interna.

## Global Constraints

- Editar somente `dissertacao/` e este plano, preservando integralmente `artigo/` e as alterações pendentes do usuário.
- Nunca usar travessões em texto destinado a Pedro.
- Não apresentar resultados antigos de classificação por LLM como achados atuais.
- Não descrever o corpus principal como composto por cinco jornais.
- Não atribuir ao periódico falas de terceiros sem evidência de apropriação editorial.
- Não inventar metadados bibliográficos ausentes.
- Marcar citações primárias não conferidas com `\fonteaconferir{}`.
- Marcar interpretações não consolidadas com `\interpretacaoprovisoria{}`.
- Preferir dependências LaTeX já instaladas a qualquer instalação de pacote.
- Não executar lotes pagos nem alterar prompts, codebooks ou modelos de mensuração.

---

## File Map

### Configuração e entrada

- Create: `dissertacao/main.tex`, ponto de entrada e ordem dos capítulos.
- Create: `dissertacao/configuracao/preambulo.tex`, pacotes e configuração tipográfica.
- Create: `dissertacao/configuracao/metadados.tex`, título, autor, programa, orientador e data do rascunho.
- Create: `dissertacao/configuracao/notas-rascunho.tex`, chave `\ifrascunho` e quatro macros editoriais.
- Create: `dissertacao/README.md`, instruções de compilação e estatuto acadêmico do documento.
- Create: `dissertacao/.gitignore`, produtos auxiliares da compilação.

### Conteúdo

- Create: `dissertacao/capitulos/00-introducao.tex`, pergunta, hipótese, recorte e contribuição.
- Create: `dissertacao/capitulos/01-fontes-metodo.tex`, imprensa, corpus, gêneros, procedimento e limites.
- Create: `dissertacao/capitulos/02-horizonte-monetario.tex`, padrão-ouro internacional e trajetória brasileira até 1906.
- Create: `dissertacao/capitulos/03-criacao-1906.tex`, criação, paridade, atores e jornais.
- Create: `dissertacao/capitulos/04-operacao-1907-1910.tex`, primeiros anos, crise de 1907 e reforma de 1910.
- Create: `dissertacao/capitulos/05-crise-1911-1914.tex`, credores, reversão externa, suspensão e crença monetária.
- Create: `dissertacao/capitulos/06-conclusao.tex`, resposta provisória e matriz de comparação final.
- Create: `dissertacao/apendices/construcao-corpus.tex`, cobertura, proveniência e limitações técnicas.

### Bibliografia e rastreabilidade

- Create: `dissertacao/bibliografia/referencias.bib`, referências efetivamente citadas.
- Create: `dissertacao/notas/mapa-reaproveitamento.md`, origem e transformação de cada bloco.
- Create: `dissertacao/notas/pendencias-documentais.md`, lista concentrada de verificações ainda necessárias.

### Verificação

- Create: `dissertacao/verificar.ps1`, checagens estruturais, editoriais e de compilação.

---

### Task 1: Infraestrutura LaTeX e notas de rascunho

**Files:**
- Create: `dissertacao/main.tex`
- Create: `dissertacao/configuracao/preambulo.tex`
- Create: `dissertacao/configuracao/metadados.tex`
- Create: `dissertacao/configuracao/notas-rascunho.tex`
- Create: `dissertacao/README.md`
- Create: `dissertacao/.gitignore`
- Create temporarily for the compilation test: the seven chapter files and appendix with one compilable sentence each. These temporary sentences are replaced in Tasks 3 to 8.

**Interfaces:**
- Consumes: nenhum arquivo novo anterior.
- Produces: comandos `\lacuna{}`, `\fonteaconferir{}`, `\interpretacaoprovisoria{}`, `\revisarbibliografia{}` e chave `\rascunhotrue` ou `\rascunhofalse`.

- [ ] **Step 1: Confirmar o ambiente de compilação**

Run:

```powershell
Get-Command pdflatex,bibtex -ErrorAction Stop | Select-Object Name,Source
```

Expected: caminhos executáveis para `pdflatex.exe` e `bibtex.exe`. Se um deles faltar, registrar o diagnóstico no `README.md` e continuar sem instalar pacotes.

- [ ] **Step 2: Criar a configuração mínima**

`preambulo.tex` deve carregar somente:

```latex
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazil]{babel}
\usepackage{lmodern}
\usepackage[a4paper,margin=2.5cm]{geometry}
\usepackage{setspace}
\usepackage{microtype}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{natbib}
\usepackage{url}
\usepackage[hidelinks]{hyperref}
\onehalfspacing
\setlength{\parindent}{1.25cm}
\setlength{\parskip}{0pt}
```

- [ ] **Step 3: Implementar as notas editoriais**

`notas-rascunho.tex` deve usar esta interface:

```latex
\newif\ifrascunho
\rascunhotrue

\newcommand{\marcadorrascunho}[3]{%
  \ifrascunho
    \par\begingroup\small\color{#1}%
    \noindent\textbf{#2:} #3\par
    \endgroup
  \fi
}

\newcommand{\lacuna}[1]{\marcadorrascunho{red!70!black}{Lacuna}{#1}}
\newcommand{\fonteaconferir}[1]{\marcadorrascunho{orange!70!black}{Fonte a conferir}{#1}}
\newcommand{\interpretacaoprovisoria}[1]{\marcadorrascunho{blue!70!black}{Interpretação provisória}{#1}}
\newcommand{\revisarbibliografia}[1]{\marcadorrascunho{violet!70!black}{Revisar bibliografia}{#1}}
```

- [ ] **Step 4: Criar o ponto de entrada**

`main.tex` deve:

1. usar `\documentclass[12pt,a4paper,openany]{report}`;
2. carregar os três arquivos de configuração;
3. produzir página de título provisória;
4. gerar `\tableofcontents`;
5. incluir os sete capítulos e o apêndice;
6. usar `\bibliographystyle{plainnat}` e `\bibliography{bibliografia/referencias}`.

- [ ] **Step 5: Criar a documentação operacional**

O `README.md` deve registrar:

```text
Compilação de trabalho:
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

A chave \rascunhotrue mostra as advertências editoriais.
A chave \rascunhofalse gera uma leitura limpa, sem apagar as advertências do código.
O documento é um rascunho de trabalho, não uma versão pronta para depósito.
```

- [ ] **Step 6: Compilar a infraestrutura**

Run from `dissertacao/`:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Expected: exit code 0 e criação de `main.pdf` e `main.toc`.

- [ ] **Step 7: Testar a chave limpa**

Trocar temporariamente `\rascunhotrue` por `\rascunhofalse`, compilar e verificar que os quatro rótulos não aparecem no PDF extraído. Restaurar `\rascunhotrue` ao final.

Run:

```powershell
pdftotext main.pdf - | Select-String -Pattern 'Lacuna|Fonte a conferir|Interpretação provisória|Revisar bibliografia'
```

Expected with `\rascunhofalse`: nenhuma correspondência.

- [ ] **Step 8: Commit**

```powershell
git add -- dissertacao/main.tex dissertacao/configuracao dissertacao/README.md dissertacao/.gitignore dissertacao/capitulos dissertacao/apendices
git commit -m "feat: cria infraestrutura latex da dissertacao"
```

---

### Task 2: Bibliografia inicial verificável

**Files:**
- Create: `dissertacao/bibliografia/referencias.bib`
- Modify: `dissertacao/capitulos/00-introducao.tex`

**Interfaces:**
- Consumes: `natbib` e `plainnat` definidos na Task 1.
- Produces: chaves estáveis para todos os capítulos seguintes.

- [ ] **Step 1: Criar as famílias bibliográficas mínimas**

Incluir entradas completas, apenas com metadados confirmados, para estas chaves:

```text
Fontes e imprensa:
luca2005, camargo1969, sodre1966, lapuente2015, beachhanlon2023

Caixa, moeda e Primeira República:
oliveirasilva2001, neuhaus1975, fritsch1980, fritsch1990,
fritschfranco1992, franco1988, francolago2011, saes1981,
holloway1978, perissinotto1999, torelli2004

Padrão-ouro internacional:
eichengreen1996, bordokydland1990, bordoschwartz1994

Legislação e documentos:
brasil1906caixa, brasil1910taxa16, brasil1914suspensao,
brasil1914emissao
```

As entradas devem ser reconstruídas a partir da bibliografia da monografia, do capítulo de qualificação, de `docs/contexto-bibliografia-caixa-conversao.md` e das páginas oficiais da Câmara já verificadas. Em caso de conflito de ano ou título, usar `\revisarbibliografia{}` no capítulo e registrar a divergência em `pendencias-documentais.md`, sem escolher por inferência.

- [ ] **Step 2: Criar citações de fumaça**

Inserir temporariamente na introdução:

```latex
\nocite{luca2005,oliveirasilva2001,fritschfranco1992,bordoschwartz1994,brasil1906caixa}
```

- [ ] **Step 3: Compilar a bibliografia**

Run from `dissertacao/`:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Expected: exit codes 0, `main.bbl` criado e nenhuma mensagem `Warning--I didn't find a database entry` em `main.blg`.

- [ ] **Step 4: Remover o teste de fumaça**

Remover o `\nocite` temporário. As entradas passarão a ser chamadas pela prosa das Tasks 3 a 8.

- [ ] **Step 5: Commit**

```powershell
git add -- dissertacao/bibliografia/referencias.bib dissertacao/capitulos/00-introducao.tex
git commit -m "docs: inicia bibliografia da dissertacao"
```

---

### Task 3: Capítulo 1, fontes e método

**Files:**
- Replace: `dissertacao/capitulos/01-fontes-metodo.tex`
- Create: `dissertacao/notas/mapa-reaproveitamento.md`

**Interfaces:**
- Consumes: macros editoriais da Task 1 e chaves de imprensa da Task 2.
- Produces: definição do corpus, hierarquia das fontes e procedimento usado pelos capítulos empíricos.

- [ ] **Step 1: Migrar criticamente a discussão da imprensa como fonte**

Usar como bases:

```text
latex_capitulo3/main.tex, seções 3.1 e 3.2
Monografia - Final .pdf, páginas 21 a 28
Pedro Ortencio - Relatório de Qualificação, páginas 7 a 10
docs/revisao-bibliografica-artefato2.md
```

Preservar a discussão de Luca, Camargo, Lapuente e Sodré, eliminando repetições entre as três versões. A seção deve terminar explicando que parcialidade, posição institucional e organização material não são defeitos externos à fonte, mas elementos da investigação.

- [ ] **Step 2: Atualizar a composição do corpus**

Redigir explicitamente:

```text
Corpus principal: O Paiz, Correio da Manhã, Correio Paulistano e Gazeta de Notícias.
Recorte: 1906 a 1914.
Ausência: Gazeta de Notícias em 1913, sem imputação.
Estatuto: censo do acervo digital identificável e recuperável da BN, não censo de todas as edições historicamente publicadas.
```

Excluir `O Estado de S. Paulo` da descrição do corpus principal. Ele pode aparecer apenas como veículo citado na monografia ou como fonte externa futura, sempre com estatuto explícito.

- [ ] **Step 3: Descrever as camadas documentais**

Incluir as quantidades consolidadas no `MAPA-DO-PROJETO.md`:

```text
11.960 objetos digitais no censo
117.703 páginas com texto
8.331 páginas que mencionam a Caixa
dois volumes de Documentos Parlamentares, 1.152 páginas
nove edições anuais do Retrospecto Commercial
```

Explicar que menção nominal inclui boletins, cotações e rotina, portanto não equivale a debate.

- [ ] **Step 4: Definir gêneros e vozes**

Criar subseção que distinga:

```text
editorial próprio
artigo assinado
notícia
seção livre e espaço pago
discurso parlamentar reproduzido
carta ou telegrama transcrito
boletim operacional
menção incidental
```

Explicar que hospedar uma voz é um dado sobre o periódico, mas não equivale automaticamente à posição editorial.

- [ ] **Step 5: Reescrever o papel computacional**

Substituir a classificação holística antiga pela descrição atual:

```text
extração do OCR embutido nos PDFs da BN
triagem tolerante a ruído
catalogação de peças, gêneros, atores, argumentos e marcos
quantificação descritiva de cobertura e composição
leitura próxima e conferência na imagem
LLM como auxiliar de catalogação, sem autoridade interpretativa final
```

Incluir as variações medidas de ruído do OCR e a consequência de que comparações lexicais entre anos e jornais exigem cautela.

- [ ] **Step 6: Registrar o reaproveitamento**

Criar `mapa-reaproveitamento.md` com uma tabela contendo estas colunas:

```markdown
| destino | origem | intervalo | ação | atualização | pendência |
```

Registrar ao menos as três fontes textuais usadas nesta Task e a exclusão da antiga seção de resultados por LLM.

- [ ] **Step 7: Verificar o capítulo**

Run:

```powershell
rg -n -S "cinco periódicos|classificação holística|constitui uma ferramenta robusta|O Estado de S\. Paulo" dissertacao/capitulos/01-fontes-metodo.tex
```

Expected: nenhuma descrição do corpus como cinco periódicos, nenhuma alegação de robustez da classificação antiga. Menção a `O Estado de S. Paulo` só é permitida se a frase explicitar que ele não integra o censo principal atual.

- [ ] **Step 8: Commit**

```powershell
git add -- dissertacao/capitulos/01-fontes-metodo.tex dissertacao/notas/mapa-reaproveitamento.md
git commit -m "docs: redige fontes e metodo da dissertacao"
```

---

### Task 4: Capítulo 2, padrão-ouro e antecedentes brasileiros

**Files:**
- Replace: `dissertacao/capitulos/02-horizonte-monetario.tex`
- Modify: `dissertacao/notas/mapa-reaproveitamento.md`

**Interfaces:**
- Consumes: referências monetárias da Task 2 e macros editoriais da Task 1.
- Produces: contexto conceitual e histórico pressuposto pelos capítulos cronológicos.

- [ ] **Step 1: Redigir o padrão-ouro internacional antes do caso brasileiro**

Organizar a seção em:

```text
definição da unidade monetária em ouro
conversibilidade
liberdade de movimento do ouro
relação entre reservas e meios de pagamento
credibilidade e expectativa de manutenção da paridade
ajuste assimétrico entre centro e periferia
regra contingente e suspensões extraordinárias
```

Usar Oliveira e Silva para a apresentação das regras e Eichengreen, Bordo e Schwartz, Franco, Fritsch e Franco para assimetria e credibilidade. Não projetar automaticamente essas categorias sobre os jornais.

- [ ] **Step 2: Reaproveitar a contextualização da monografia**

Usar:

```text
Monografia - Final .pdf, capítulos 2.1 a 2.3, páginas 10 a 20
docs/contexto-bibliografia-caixa-conversao.md
Franco e Lago (2011), seções sobre Encilhamento, Funding Loan e Taubaté
```

Reescrever em sequência:

```text
expansão e crise da primeira década republicana
problemas fiscais e cambiais
Funding Loan de 1898
contração, equilíbrio e valorização cambial
efeitos distributivos sobre exportadores, importadores, Estado e credores
crise cafeeira e políticas de defesa
Convênio de Taubaté
```

- [ ] **Step 3: Corrigir o eixo doutrinário**

Explicar que a Caixa não representou simples retorno do papelismo. Formular o conflito como disputa sobre:

```text
nível da taxa
ritmo de valorização
limites da emissão conversível
fundos de resgate e garantia
custos distributivos da estabilidade
```

Marcar como `\interpretacaoprovisoria{}` qualquer passagem que transforme essa hipótese em consenso documental de todo o período.

- [ ] **Step 4: Distinguir 12, 15 e 27 dinheiros**

Registrar:

```text
12 dinheiros: proposta vinculada a setores cafeeiros e às emendas de Alcindo Guanabara
15 dinheiros: projeto de David Campista e taxa da lei de 1906
27 dinheiros: par legal e horizonte dos valorizadores ortodoxos
```

Evitar a formulação de que a Caixa foi criada a 12 dinheiros.

- [ ] **Step 5: Atualizar o mapa de reaproveitamento**

Registrar as páginas da monografia utilizadas, os blocos reescritos e as correções conceituais.

- [ ] **Step 6: Compilar e verificar citações**

Run from `dissertacao/`:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
Select-String -Path main.log -Pattern 'Citation.*undefined|There were undefined references'
```

Expected: compilação completa e nenhuma citação indefinida.

- [ ] **Step 7: Commit**

```powershell
git add -- dissertacao/capitulos/02-horizonte-monetario.tex dissertacao/notas/mapa-reaproveitamento.md
git commit -m "docs: redige horizonte monetario da Caixa"
```

---

### Task 5: Introdução e Capítulo 3, criação em 1906

**Files:**
- Replace: `dissertacao/capitulos/00-introducao.tex`
- Replace: `dissertacao/capitulos/03-criacao-1906.tex`
- Modify: `dissertacao/notas/mapa-reaproveitamento.md`

**Interfaces:**
- Consumes: problema metodológico da Task 3 e contexto da Task 4.
- Produces: argumento provisório e primeira análise cronológica.

- [ ] **Step 1: Redigir a introdução provisória**

Incluir, nesta ordem:

```text
objeto e relevância
pergunta sobre como os jornais organizaram o debate da Caixa
recorte 1906 a 1914
corpus principal e fontes acessórias
hipótese central provisória
contribuição inventarial e interpretativa
estrutura da dissertação
```

Usar `\interpretacaoprovisoria{}` para a hipótese:

```text
Em 1906, o campo do debate já atribuía ampla legitimidade à estabilidade e à conversibilidade, enquanto o conflito incidia sobre taxa, ritmo de valorização, emissão, lastro e custos distributivos. Entre 1912 e 1914, a crise separou desejabilidade, viabilidade e custo da estabilidade.
```

- [ ] **Step 2: Reaproveitar a cronologia de 1905 e 1906**

Usar:

```text
Monografia - Final .pdf, capítulo 4, páginas 29 a 49
docs/relatorio-achados-provisorios-2026-08-09.md, fase 1
docs/exploracao-base-2026-07-28.md, editoriais de 1906
Documentos Parlamentares já inventariados no repositório
```

Organizar o capítulo em:

```text
prelúdio do Convênio
Convênio de Taubaté
convocação extraordinária
separação dos projetos
projeto Campista
tramitação e aprovação
desenho legal da Caixa
```

- [ ] **Step 3: Organizar os cinco debates documentados de 1906**

Criar uma seção para cada objeto:

```text
nível da taxa de fixação
limite de emissão
fundos de resgate e garantia
competência do Congresso ou Executivo
agência da Caixa em Londres
```

Para cada objeto, usar a matriz:

```text
decisão institucional
polos documentados
atores e grupos
vocabulário de época
tratamento pelos jornais
comparação com a historiografia
```

- [ ] **Step 4: Incorporar documentos primários reproduzidos**

Incluir como fontes hospedadas:

```text
justificação do projeto publicada pelo Correio Paulistano em 03/07/1906
texto do projeto publicado pelo Correio Paulistano em 11/10/1906
emendas de Alcindo Guanabara a 12 dinheiros
parecer da comissão de finanças publicado pela Gazeta de Notícias
relatório de Custódio Coelho debatido pelo Correio da Manhã
```

Toda passagem ainda sem conferência na imagem deverá usar `\fonteaconferir{}`. Não apresentar o conteúdo reproduzido como posição editorial automática.

- [ ] **Step 5: Atualizar o mapa de reaproveitamento**

Registrar quais subseções da monografia foram preservadas, comprimidas, corrigidas ou deslocadas.

- [ ] **Step 6: Verificar afirmações proibidas**

Run:

```powershell
rg -n -S "criada a 12|Caixa.*12 dinheiros|papelismo.*1914|cinco jornais" dissertacao/capitulos/00-introducao.tex dissertacao/capitulos/03-criacao-1906.tex
```

Expected: nenhuma afirmação de criação a 12 dinheiros, nenhuma restauração do papelismo em 1914 e nenhuma descrição do corpus como cinco jornais.

- [ ] **Step 7: Commit**

```powershell
git add -- dissertacao/capitulos/00-introducao.tex dissertacao/capitulos/03-criacao-1906.tex dissertacao/notas/mapa-reaproveitamento.md
git commit -m "docs: redige introducao e criacao da Caixa"
```

---

### Task 6: Capítulo 4, operação entre 1907 e 1910

**Files:**
- Replace: `dissertacao/capitulos/04-operacao-1907-1910.tex`
- Modify: `dissertacao/notas/mapa-reaproveitamento.md`

**Interfaces:**
- Consumes: mecanismo do padrão-ouro da Task 4 e desenho legal da Task 5.
- Produces: ponte entre criação, aparente sucesso e vulnerabilidade posterior.

- [ ] **Step 1: Redigir a cronologia conjuntural**

Usar Oliveira e Silva, Fritsch, Fritsch e Franco e Franco e Lago para organizar:

```text
início das operações
crise financeira internacional de 1907
ameaça ao financiamento da valorização do café
apoio federal e preservação da experiência
retorno dos capitais em 1908
borracha, exportações e expansão monetária
acumulação de ouro em 1909 e 1910
```

Explicar que o êxito inicial não pode ser separado da conjuntura externa e das decisões de apoio ao café.

- [ ] **Step 2: Incorporar os debates observados nos jornais**

Usar `docs/relatorio-achados-provisorios-2026-08-09.md` e `docs/exploracao-base-2026-07-28.md` para tratar:

```text
direitos aduaneiros ao padrão legal de 20$000 ou à taxa efetiva
queda do fetichismo do par de 27 no Correio da Manhã
função do Banco do Brasil
limite da emissão
fixidez contra valorização progressiva
```

Marcar a interpretação da trajetória do `Correio da Manhã` como provisória, pois a continuidade pode estar no interesse defendido e não na direção de uma escala.

- [ ] **Step 3: Redigir a reforma de 1910**

Explicar:

```text
depósitos de ouro atingem £20 milhões em maio de 1910
reabertura da disputa sobre taxa e limite
posições de Cincinato Braga, Galeão Carvalhal e João Luiz Alves
elevação para 16 dinheiros pelo Decreto 2.357
novo limite de 900 mil contos ou £60 milhões
restauração dos fundos de garantia e resgate
```

Tratar as peças publicadas em `Seção Livre` como vozes hospedadas.

- [ ] **Step 4: Atualizar o mapa de reaproveitamento**

Registrar que este capítulo deriva principalmente da bibliografia e dos relatórios do repositório, e não da monografia, cujo recorte termina em 1906.

- [ ] **Step 5: Compilar e revisar a transição**

Run:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Expected: exit codes 0. Ler o fim do Capítulo 3 e o início do Capítulo 4 no texto extraído para confirmar que a reforma de 1910 não aparece antes da explicação da operação inicial.

- [ ] **Step 6: Commit**

```powershell
git add -- dissertacao/capitulos/04-operacao-1907-1910.tex dissertacao/notas/mapa-reaproveitamento.md
git commit -m "docs: redige operacao da Caixa ate 1910"
```

---

### Task 7: Capítulo 5, vulnerabilidade e suspensão

**Files:**
- Replace: `dissertacao/capitulos/05-crise-1911-1914.tex`
- Create: `dissertacao/notas/pendencias-documentais.md`
- Modify: `dissertacao/notas/mapa-reaproveitamento.md`

**Interfaces:**
- Consumes: dinâmica de expansão da Task 6 e referências sobre padrão-ouro da Task 2.
- Produces: interpretação provisória da crise e agenda de leitura das fontes de 1911 a 1914.

- [ ] **Step 1: Redigir 1911 como problema de custódia e autoridade**

Usar os relatórios sobre credores para tratar:

```text
transferência dos depósitos de ouro aos Rothschild
remuneração de 2,5% destinada ao fundo de garantia
natureza jurídica do depósito
autoridade do governo sobre ouro entregue por particulares
designações nominais e perifrásticas do credor externo
```

Não apresentar o episódio como causa macroeconômica da crise posterior. Formulá-lo como janela para confiança, soberania, custódia e poder financeiro.

- [ ] **Step 2: Redigir a reversão de 1912 e 1913**

Distinguir os mecanismos:

```text
déficits e preocupação dos credores
dificuldade de novos empréstimos
queda da borracha diante da produção asiática
venda dos estoques de café nos Estados Unidos
contração dos capitais europeus associada às Guerras Balcânicas
reversão do balanço de pagamentos
retirada de ouro e contração monetária
recessão anterior à guerra
```

Não atribuir causalidade única às Guerras Balcânicas. Comparar explicitamente Oliveira e Silva com a narrativa mais abrangente de Fritsch.

- [ ] **Step 3: Explicar a incompatibilidade de compromissos**

Redigir uma subseção que mostre a colisão entre:

```text
conversibilidade imediata
preservação do lastro
defesa da taxa de 16
liquidez bancária
atividade econômica
finanças públicas
serviço da dívida externa
```

Apresentar “incompatibilidade” como síntese analítica, não como expressão literal da literatura.

- [ ] **Step 4: Redigir a suspensão em 1914**

Tratar:

```text
feriado bancário e medidas emergenciais
Decreto 2.862, suspensão do troco e preservação jurídica do ouro
Decreto 11.091, emissão de 150 mil contos, dos quais 100 mil para bancos
Funding Loan de 1914
estabilização posterior abaixo da paridade pré-guerra
```

Usar “suspensão”, “fim operacional da conversibilidade” ou “encerramento da experiência”. Não usar “dissolução” sem norma formal de extinção.

- [ ] **Step 5: Organizar a mudança da crença monetária**

Usar como perguntas às fontes:

```text
a estabilidade continuava desejável?
a conversibilidade continuava viável?
o custo da defesa da taxa era aceitável?
a suspensão era temporária ou veredito definitivo?
qual regime e qual paridade eram desejados depois da crise?
```

Incorporar o caso em que Martim Francisco e Serzedello Corrêa se opõem à suspensão por razões opostas. Usar esse caso para demonstrar por que posição formal sobre o troco não identifica sozinha o regime desejado.

- [ ] **Step 6: Criar as pendências documentais**

`pendencias-documentais.md` deve listar, com fonte e ação:

```text
conferência visual de todas as citações primárias usadas
data e base legal do início efetivo das operações
estatuto jurídico da agência em Londres
cronologia mensal das retiradas entre 1912 e 1914
norma de extinção formal da Caixa, se houver
tratamento de 1913 diante da ausência da Gazeta
verificação das posições dos periódicos além dos editoriais já lidos
normalização dos metadados incompletos de Torelli e Ribeiro
```

- [ ] **Step 7: Commit**

```powershell
git add -- dissertacao/capitulos/05-crise-1911-1914.tex dissertacao/notas/pendencias-documentais.md dissertacao/notas/mapa-reaproveitamento.md
git commit -m "docs: redige crise e suspensao da Caixa"
```

---

### Task 8: Conclusão provisória e apêndice do corpus

**Files:**
- Replace: `dissertacao/capitulos/06-conclusao.tex`
- Replace: `dissertacao/apendices/construcao-corpus.tex`
- Modify: `dissertacao/notas/mapa-reaproveitamento.md`

**Interfaces:**
- Consumes: todos os capítulos anteriores.
- Produces: síntese provisória e documentação técnica separada do argumento histórico.

- [ ] **Step 1: Criar a conclusão em estatuto provisório**

Organizar a conclusão em quatro blocos:

```text
o que a dissertação pergunta
o que o material já permite sustentar
o que ainda depende da leitura comparada
contribuição documental e limites
```

Registrar como `\interpretacaoprovisoria{}`:

```text
o debate não se reduz a metalismo contra papelismo
as categorias mudam entre criação, operação, reforma e crise
publicar vozes divergentes é uma função do periódico distinta de endossá-las
1914 separa desejabilidade, viabilidade e custo da estabilidade
```

Criar uma matriz de redação, não uma tabela de resultados, com uma subseção para cada jornal e perguntas a preencher após a leitura final.

- [ ] **Step 2: Redigir o apêndice do corpus**

Documentar:

```text
identificadores bibliográficos dos quatro periódicos
número de objetos por jornal
ausência da Gazeta em 1913
censo digital versus edições publicadas
camada de texto e páginas vazias
triagem nominal e diferença entre nome e debate
amostra substantiva e gêneros
ruído variável do OCR
fontes acessórias fora do censo principal
```

Evitar repetir no corpo metodológico detalhes operacionais que possam ficar no apêndice.

- [ ] **Step 3: Atualizar o mapa de reaproveitamento**

Registrar `MAPA-DO-PROJETO.md`, `plano-leitura-fases.md` e os relatórios quantitativos como origem do apêndice.

- [ ] **Step 4: Compilar**

Run from `dissertacao/`:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Expected: exit codes 0, sumário com sete capítulos e um apêndice.

- [ ] **Step 5: Commit**

```powershell
git add -- dissertacao/capitulos/06-conclusao.tex dissertacao/apendices/construcao-corpus.tex dissertacao/notas/mapa-reaproveitamento.md
git commit -m "docs: adiciona conclusao provisoria e apendice"
```

---

### Task 9: Verificação integrada e entrega

**Files:**
- Create: `dissertacao/verificar.ps1`
- Modify if needed: files under `dissertacao/` only

**Interfaces:**
- Consumes: documento completo.
- Produces: verificação reproduzível e PDF de trabalho local, ignorado pelo Git.

- [ ] **Step 1: Implementar a verificação estrutural**

`verificar.ps1` deve falhar com exit code 1 quando:

```powershell
$required = @(
  'main.tex',
  'configuracao/preambulo.tex',
  'configuracao/metadados.tex',
  'configuracao/notas-rascunho.tex',
  'capitulos/00-introducao.tex',
  'capitulos/01-fontes-metodo.tex',
  'capitulos/02-horizonte-monetario.tex',
  'capitulos/03-criacao-1906.tex',
  'capitulos/04-operacao-1907-1910.tex',
  'capitulos/05-crise-1911-1914.tex',
  'capitulos/06-conclusao.tex',
  'apendices/construcao-corpus.tex',
  'bibliografia/referencias.bib',
  'notas/mapa-reaproveitamento.md',
  'notas/pendencias-documentais.md'
)
```

Cada item deve ser testado com `Test-Path -LiteralPath` a partir da pasta do script.

- [ ] **Step 2: Implementar as regras editoriais**

O script deve procurar, em `.tex`, `.bib` e `.md` da pasta:

```text
caractere U+2014
caractere U+2013 usado como pontuação, preservando intervalos numéricos escritos com -- no LaTeX
“classificação holística constitui uma ferramenta robusta”
“corpus definitivo de cinco periódicos”
“Caixa foi criada a 12 dinheiros”
“restauração do papelismo em 1914”
```

O script deve imprimir o arquivo e a linha de qualquer ocorrência proibida e encerrar com exit code 1.

- [ ] **Step 3: Implementar a compilação**

O script deve executar, com checagem de `$LASTEXITCODE`:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Depois deve procurar em `main.log` e `main.blg`:

```text
Citation.*undefined
There were undefined references
I didn't find a database entry
```

Qualquer correspondência deve gerar exit code 1.

- [ ] **Step 4: Executar a verificação**

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\verificar.ps1
```

Expected: mensagem final `VERIFICAÇÃO CONCLUÍDA: rascunho compilável e sem violações detectadas.` e exit code 0.

- [ ] **Step 5: Inspecionar o PDF**

Renderizar o PDF em páginas de imagem numa pasta temporária fora do Git e inspecionar:

```text
página de título
sumário
primeira página de cada capítulo
uma página com cada tipo de nota editorial
bibliografia
apêndice
```

Verificar ausência de texto cortado, notas sobrepostas, caracteres ausentes, títulos órfãos e referências quebradas.

- [ ] **Step 6: Comparar o escopo do Git**

Run:

```powershell
git status --short
git diff --name-only HEAD
```

Expected: as alterações da tarefa aparecem somente em `dissertacao/` e no plano. Alterações preexistentes fora desses caminhos continuam intactas e não são adicionadas ao índice.

- [ ] **Step 7: Commit final**

```powershell
git add -- dissertacao/verificar.ps1 dissertacao
git commit -m "docs: conclui rascunho zero da dissertacao"
```

- [ ] **Step 8: Relatório final**

Entregar:

```text
estrutura criada
capítulos substancialmente preenchidos
fontes reaproveitadas
extensão aproximada do texto
resultado da compilação
resultado da verificação editorial
principais lacunas ainda visíveis
commits criados
confirmação de que nenhuma mudança alheia foi incluída
```

