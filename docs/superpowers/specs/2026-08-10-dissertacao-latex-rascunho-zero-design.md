# Dissertação em LaTeX, design do rascunho zero

**Data:** 2026-08-10  
**Status:** aprovado por Pedro em conversa, aguardando revisão deste registro escrito  
**Papel do Codex:** implementador designado  
**Escopo autorizado:** criar esta especificação e, após sua revisão, a nova pasta `dissertacao/`. Não alterar `artigo/` nem arquivos preexistentes fora desse escopo.

## 1. Objetivo

Criar no repositório um rascunho zero compilável da dissertação de mestrado sobre o debate jornalístico a respeito da Caixa de Conversão entre 1906 e 1914.

O documento não será apenas um sumário comentado. Ele receberá prosa inicial selecionada da monografia, do relatório de qualificação, do capítulo metodológico em LaTeX e dos relatórios acadêmicos e documentais do repositório. O reaproveitamento deverá preservar a proveniência e distinguir evidência conferida, interpretação provisória e lacuna documental.

O rascunho seguirá o desenho substantivo atualmente aprovado para a pesquisa:

1. os quatro jornais do censo digital constituem o corpus principal;
2. debates parlamentares, cartas, telegramas, legislação e retrospectos comerciais são fontes acessórias e de contextualização;
3. o núcleo da contribuição é inventarial, descritivo e interpretativo;
4. a classificação de posicionamento por LLM não será apresentada como método central nem como resultado estabelecido;
5. a redação será cronológico-analítica e comparará as fontes com a historiografia sempre que a evidência permitir.

## 2. Fontes de reaproveitamento

### 2.1 Materiais externos ao repositório

- `Monografia - Final .pdf`, 56 páginas, especialmente contextualização histórica, metodologia da fonte jornalística e narrativa de 1905 a 1906;
- `Pedro Ortencio - Relatório de Qualificação (Relatório + Capítulo 3).pdf`, especialmente o capítulo metodológico e o registro da evolução do projeto;
- `latex_capitulo3/main.tex`, versão-fonte do capítulo metodológico e dos resultados antigos de 1906;
- `Pedro de Campos Telles (2025-06-18) - Estrutura e Bibliografia.docx`, para recuperar referências e escolhas estruturais anteriores.

### 2.2 Materiais do repositório

- `docs/MAPA-DO-PROJETO.md`, para números consolidados do corpus e suas limitações;
- `docs/contexto-bibliografia-caixa-conversao.md`, para o inventário historiográfico;
- `docs/revisao-bibliografica-artefato2.md`, para lacunas e famílias de literatura;
- `docs/exploracao-base-2026-07-28.md`, para leituras preliminares de editoriais;
- `docs/relatorio-achados-provisorios-2026-08-09.md`, para atores, fontes e debates catalogados;
- `docs/relatorio-achados-esteves-2026-08-09.md`, para credores, empréstimos e documentos reproduzidos;
- `docs/relatorio-credor-externo-no-debate.md`, para banqueiros e agentes financeiros;
- `docs/plano-leitura-fases.md`, para a distribuição do material substantivo e as fases cronológicas;
- documentos canônicos metodológicos indicados por `AGENTS.md`, para ressalvas de validade, cobertura, OCR, voz e inferência.

## 3. Estratégia de reaproveitamento

O texto existente não será importado indiscriminadamente. Cada bloco seguirá uma destas ações:

1. **Aproveitar e atualizar:** prosa historiográfica ou metodológica ainda compatível com o desenho atual;
2. **Reescrever:** formulações úteis cujo argumento permaneça válido, mas cuja linguagem, escopo ou evidência estejam desatualizados;
3. **Converter em nota de trabalho:** interpretação promissora ainda dependente de leitura ou conferência;
4. **Registrar apenas no mapa de reaproveitamento:** resultados antigos de mensuração, composição antiga do corpus e afirmações superadas;
5. **Excluir do rascunho acadêmico:** alegações invalidadas pelo corpus atual ou pelo debate metodológico posterior.

Não serão transportados como resultados válidos:

- estimativas agregadas antigas de posicionamento;
- médias móveis de pontuação editorial;
- afirmações baseadas na antiga composição de cinco periódicos;
- conclusões sobre voz editorial obtidas sem distinguir texto próprio, seção livre, discurso parlamentar ou documento reproduzido;
- alegações de robustez da classificação holística por LLM.

## 4. Arquitetura de arquivos

```text
dissertacao/
|-- main.tex
|-- README.md
|-- configuracao/
|   |-- preambulo.tex
|   |-- metadados.tex
|   `-- notas-rascunho.tex
|-- capitulos/
|   |-- 00-introducao.tex
|   |-- 01-fontes-metodo.tex
|   |-- 02-horizonte-monetario.tex
|   |-- 03-criacao-1906.tex
|   |-- 04-operacao-1907-1910.tex
|   |-- 05-crise-1911-1914.tex
|   `-- 06-conclusao.tex
|-- apendices/
|   `-- construcao-corpus.tex
|-- bibliografia/
|   `-- referencias.bib
|-- figuras/
|-- tabelas/
`-- notas/
    |-- mapa-reaproveitamento.md
    `-- pendencias-documentais.md
```

Arquivos vazios não serão criados apenas para materializar diretórios. As pastas `figuras/` e `tabelas/` só serão adicionadas quando houver conteúdo ou um arquivo curto que explique seu uso.

## 5. Estrutura substantiva

### Introdução

- problema e pergunta de pesquisa;
- hipótese central em estatuto provisório;
- recorte temporal e documental;
- jornais principais e fontes acessórias;
- contribuição inventarial, descritiva e interpretativa;
- visão sintética do percurso entre Funding Loan, Caixa e crise de 1914;
- apresentação dos capítulos.

### Capítulo 1. Imprensa, fontes e método

- imprensa como fonte e como participante do debate;
- crítica e contextualização da fonte jornalística;
- caracterização dos quatro periódicos;
- formação do corpus e cobertura documental;
- gêneros, seções, vozes e documentos reproduzidos;
- fontes acessórias;
- OCR, busca, catalogação e limitações;
- papel auxiliar das ferramentas computacionais;
- procedimento de leitura cronológica e comparação.

### Capítulo 2. O horizonte monetário da Caixa

- padrão-ouro internacional;
- credibilidade, conversibilidade e assimetrias entre centro e periferia;
- crise monetária do início da República;
- Funding Loan e guinada ortodoxa;
- valorização cambial e crise exportadora;
- Convênio de Taubaté;
- propostas de 12, 15 e 27 dinheiros;
- desenho institucional da Caixa.

### Capítulo 3. 1906, criação e paridade

- prelúdio e Convênio de Taubaté;
- tramitação dos projetos;
- taxa de fixação;
- limite de emissão;
- fundos de garantia e resgate;
- competência para alterar a taxa;
- agência em Londres;
- atores, grupos, vocabulário e tratamento comparado pelos jornais.

### Capítulo 4. 1907 a 1910, funcionamento e reforma

- primeiros meses de funcionamento;
- crise financeira internacional de 1907;
- financiamento da valorização do café;
- retomada dos influxos externos;
- operação da Caixa e do Banco do Brasil;
- direitos aduaneiros;
- expansão das reservas;
- debate sobre limite, taxa e valorização;
- elevação para 16 dinheiros em 1910;
- transformação dos argumentos jornalísticos.

### Capítulo 5. 1911 a 1914, vulnerabilidade e suspensão

- depósitos de ouro nos Rothschild;
- natureza jurídica do ouro e agentes financeiros;
- deterioração externa em 1912 e 1913;
- café, borracha, capitais e crédito;
- contração monetária e crise de liquidez;
- guerra, suspensão do troco e emissão de socorro;
- Funding Loan de 1914;
- transformação da crença na estabilidade e na conversibilidade;
- veredito retrospectivo dos jornais sobre a experiência.

### Conclusão

- comparação diacrônica dos periódicos;
- transformação das categorias do debate;
- diferença entre voz editorial e vozes hospedadas;
- confronto entre literatura e fontes;
- resposta à hipótese;
- limites documentais e caminhos de pesquisa.

## 6. Estatutos editoriais no rascunho

O preâmbulo oferecerá uma chave global de compilação:

```latex
\rascunhotrue
```

Quando ativada, quatro comandos produzirão notas visíveis e diferenciadas:

```latex
\lacuna{...}
\fonteaconferir{...}
\interpretacaoprovisoria{...}
\revisarbibliografia{...}
```

Quando desativada, as notas desaparecerão da versão compilada, mas continuarão preservadas no código-fonte.

As macros deverão usar apenas dependências leves e permitir quebra de página. Não deverão interferir na numeração de seções, notas de rodapé, citações ou sumário.

Comentários de proveniência que não interessem ao leitor permanecerão apenas no código:

```latex
% ORIGEM: monografia, p. 21-24; revisto à luz de Luca (2005)
% ESTATUTO: síntese bibliográfica
```

## 7. Bibliografia

Será criada uma bibliografia própria para a dissertação. O arquivo não será uma simples cópia de `artigo/referencias.bib`, que está incompleto e concentrado em text-as-data.

O primeiro passe deverá:

- migrar referências efetivamente usadas no texto inicial;
- recuperar referências da monografia, do capítulo de qualificação e do documento de estrutura;
- incorporar o núcleo sobre padrão-ouro, política monetária brasileira, café, imprensa e credores externos;
- deduplicar autores, títulos e edições;
- manter itens incompletos claramente marcados no código BibTeX;
- não inventar metadados ausentes.

O estilo bibliográfico deverá ser compatível com o ambiente LaTeX instalado e permanecer substituível por um template institucional posterior.

## 8. Classe documental e portabilidade

Como não foi localizado um modelo oficial da FFLCH nos documentos examinados, o conteúdo será escrito de forma independente da classe documental.

O primeiro `main.tex` usará uma classe estável disponível no ambiente, com capítulos, sumário, citações e bibliografia. Configuração visual e elementos pré-textuais ficarão isolados em `configuracao/`, de modo que uma futura migração para `abntex2` ou para um template institucional não exija reescrever os capítulos.

Não serão implementados nesta primeira entrega ficha catalográfica, folha de aprovação definitiva, dedicatória, agradecimentos ou elementos que dependam de dados institucionais ainda não informados.

## 9. Mapa de reaproveitamento

`notas/mapa-reaproveitamento.md` registrará, por capítulo:

- material de origem;
- intervalo de páginas ou seção;
- ação aplicada, aproveitar, reescrever, converter em nota ou rejeitar;
- justificativa;
- principais atualizações realizadas;
- pendências de conferência.

Esse mapa não substitui citações acadêmicas. Ele é um instrumento interno de rastreabilidade e proteção contra reaproveitamento acrítico.

## 10. Tratamento de fontes primárias

Uma passagem de fonte primária só poderá aparecer como evidência normal quando estiver localizada de modo reproduzível e tiver estatuto suficiente nos relatórios.

Casos ainda indicados como “a conferir”, trechos obtidos apenas de OCR ou interpretações cuja voz não esteja definida deverão usar `\fonteaconferir` ou `\interpretacaoprovisoria`.

Documentos reproduzidos nos jornais serão descritos como documentos hospedados ou transcritos pelo periódico, não como voz editorial, salvo evidência explícita de apropriação pelo jornal.

## 11. Compilação e verificação

A implementação deverá ser verificada em quatro níveis:

1. **estrutura:** todos os arquivos referenciados existem e o documento não contém inclusões quebradas;
2. **compilação:** a sequência de compilação disponível no ambiente termina sem erro fatal;
3. **bibliografia:** chaves citadas existem, entradas usadas aparecem e referências não são inventadas para eliminar avisos;
4. **conteúdo:** busca mecânica confirma ausência de travessões, de resultados antigos apresentados como atuais e de referências ao corpus definitivo de cinco jornais.

Se o ambiente não dispuser de uma dependência LaTeX necessária, a implementação deverá preferir simplificação do preâmbulo a instalação não autorizada de pacotes.

## 12. Critérios de aceite

A primeira entrega será aceita quando:

- `dissertacao/main.tex` compilar no ambiente disponível ou houver diagnóstico preciso e reproduzível da única dependência externa faltante;
- o sumário representar a estrutura substantiva aprovada;
- os capítulos 1, 2 e 3 contiverem prosa reaproveitada e atualizada;
- os capítulos 4 e 5 contiverem narrativa inicial, marcos, debates e notas de evidência;
- a conclusão contiver um esqueleto argumentativo coerente;
- as notas de rascunho puderem ser ativadas e ocultadas por uma única chave;
- todo reaproveitamento material estiver registrado;
- a bibliografia inicial contiver apenas referências reais e identificáveis;
- nenhuma alteração preexistente fora de `dissertacao/` e desta especificação tiver sido modificada, incluída em commit ou sobrescrita.

## 13. Fora de escopo nesta primeira entrega

- conclusão definitiva sobre a postura de cada periódico;
- preenchimento de citações primárias ainda não conferidas;
- nova classificação em lote ou novo gasto de API;
- gráficos finais de posicionamento;
- template institucional definitivo;
- revisão estilística final da dissertação;
- normalização integral de toda a bibliografia local não citada;
- edição de `artigo/`;
- alteração dos relatórios que servem como fonte do rascunho.

