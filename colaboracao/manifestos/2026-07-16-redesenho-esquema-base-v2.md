# Manifesto: redigir a v2 do spec do esquema da base do corpus

- task_id: 2026-07-16-redesenho-esquema-base-v2
- solicitante: Pedro (a decisao final e dele)
- papel_solicitado: implementador designado (redigir um documento de design; nao editar arquivos, sua resposta final e o documento)
- nivel: critico (envolve o corpus)
- gate: autorizado por Pedro em 16/07/2026; a v1 do spec passou por um painel de olhos frescos e pela sua auditoria, e a direcao de redesenho foi aceita. Voce escreve a v2; a revisao independente da v2 sera do Claude e do Pedro (voce nao audita o que implementa)
- orcamento: uma unica rodada; leia os arquivos listados
- ferramentas: sandbox read-only; sua saida final e o documento v2 completo em markdown, nada mais
- workdir: repo principal (branch main), commit d47f364

## Objetivo

Escrever a v2 completa do spec do esquema da base do corpus, substituindo a v1 (`docs/superpowers/specs/2026-07-16-esquema-base-corpus-design.md`), incorporando a sua propria auditoria e o consenso do painel de revisao. A v2 deve ser um documento pronto para o Pedro revisar e para virar plano de implementacao.

## Contexto: consenso das quatro vozes (painel de 3 lentes + sua auditoria) sobre a v1

A v1 comprimia quatro universos distintos (inventario do que existe; o que a busca recuperou; o que o identificador escolheu; o que foi transcrito) em um bit `is_hit`, ausencia de linha e estados sobrescreviveis. Diagnostico central aceito: a decisao de postura pode ser adiada para a rodada metodologica, mas a definicao operacional de inclusao no corpus (identificacao de pagina e mecanica do censo) e desenho de corpus e precisa estar fechada antes da coleta seletiva.

## Requisitos da v2 (o que o design tem que resolver)

1. **Separar fisicamente as camadas** (em vez de `edicoes` + `paginas` da v1):
   - **Inventario do objeto digital da BN:** uma linha por objeto digital, com identificador/URL de origem, bib, ano, chave do arquivo/numero da BN, hash, status HTTP, data de obtencao, numero de paginas.
   - **Unidade analitica edicao-dia separada do objeto fisico:** mapeamento de um ou mais objetos digitais para uma `edicao_dia`, com regra explicita para suplementos, edicoes extraordinarias, mais de uma edicao no mesmo dia e divergencia entre numero do arquivo da BN e numero impresso. Nao assumir "1 PDF = 1 edicao = 1 edicao-dia"; isso precisa ser testavel no piloto.
   - **Paginas com avaliacao explicita:** uma linha barata por pagina fisica, com resultado em {relevante, nao_relevante, incerta, erro, nao_avaliada}. Nunca inferir negativo de ausencia de linha.
   - **Execucoes append-only de busca e identificacao:** tabelas tipo `search_runs`, `search_hits`, `page_assessments`, onde cada decisao de relevancia referencia protocolo, versao, modelo, prompt e resposta bruta ou hash, e data. Reexecucao gera nova linha, nunca sobrescreve; uma decisao vigente pode apontar para a execucao atual sem apagar as anteriores.
   - **Transcricoes versionadas:** nao sobrescrever texto quando modelo ou prompt mudar; registrar hash da entrada visual, versao do prompt e resposta.
   - **Data como sub-registro:** preservar `data_literal`, pagina e regiao da evidencia, parser e versao, data normalizada e status `observada` ou `imputada`. Vizinhanca gera data imputada separada, nao equivalente ao masthead. O masthead deve ser transcrito para toda edicao, nao so as relevantes, para a data nao ficar correlacionada com a variavel de interesse.
2. **`fase` e `relevante` saem do nucleo** e viram visoes ou classificacoes versionadas a jusante, para nao acoplar o corpus a decisoes metodologicas mutaveis.
3. **Cascata de populacoes explicita:** inventariadas -> disponiveis -> avaliadas -> recuperadas -> substantivamente relevantes -> transcritas -> classificadas. O denominador da saliencia e definido sobre edicao-dias elegiveis e efetivamente avaliadas, nunca sobre hits. Distinguir "nao circulou", "circulou mas falta no acervo" e "existe no acervo mas falhou no pipeline".
4. **Ligacoes reproduziveis** busca -> hit -> objeto/edicao -> pagina, para reproduzir o corpus e resolver os 280 casos sem mencao do P0.
5. **Recall com gancho de dados no proprio esquema** (tabela/campos para registrar amostragem e resultado, amarrados por FK) e amostra estatisticamente valida: a auditoria de ~15 edicoes negativas por jornal e insuficiente (mesmo zero falhas em 15 deixa o limite superior de 95% perto de 20%). Dimensionar para um gate de recall com limite inferior de confianca por jornal e por fase.
6. **Gate de economia da identificacao:** propor triagem barata sobre TODAS as paginas (OCR existente da BN, OCR local ou visao de baixo custo) e transcricao de qualidade so nos candidatos, com amostra estratificada de edicoes lida por inteiro para medir o que a triagem perde. O design deve exigir medir o custo real da triagem antes de comprometer a arquitetura, porque o custo de imagem de entrada pode dominar.
7. **Faseamento explicito:** Fase A (gate-free, pode comecar apos o contrato minimo de inventario): enumeracao do censo e download dos PDFs inteiros. Fase B (antes de gastar token com transcricao): fechar identificacao, denominador, recall, validacao de data e os gates do P0 de 1906.
8. **Nomear com honestidade:** se a transcricao for seletiva, o corpus textual e um "subcorpus recuperado segundo o protocolo X"; a camada bruta (PDFs) deve ser completa, duravel e reprocessavel. Deixar isso escrito.
9. **Manter o que era bom na v1:** SQLite em `dados/base/caixa_conversao.db`; contrato imposto no banco (CHECK nos enums, NOT NULL, UNIQUE, FOREIGN KEY com PRAGMA foreign_keys=ON); versionamento por migracoes numeradas com `PRAGMA user_version`; layout `pipeline/base/` (db.py, schema.sql, migrations); banco gitignored com backup OneDrive; export de transcricoes em texto versionado no git.

## Decisoes genuinamente em aberto (apresente recomendacao e alternativa, nao decida sozinho)

- Perseguir o censo textual completo (transcrever metadados de toda edicao) versus assumir e nomear um subcorpus recuperado por protocolo. Diga o custo e o vies de cada caminho.
- Se a unidade e edicao-dia estrita ou se comporta multiplas edicoes no dia.

## Arquivos de contexto (leia, relativos ao workdir)

1. docs/superpowers/specs/2026-07-16-esquema-base-corpus-design.md (a v1 a substituir)
2. docs/avaliacao-independente-2026-07-15.md (sua auditoria anterior)
3. docs/plano-pipeline.md (plano geral)
4. CLAUDE.md (guardrails; entre eles: nunca usar travessoes em texto para o Pedro, modelos pinados)

## Evidencia potencialmente relevante nao fornecida

- Os dados reais do piloto 1906 e o parecer completo que voce emitiu sobre a v1 nesta mesma data nao estao anexados; os requisitos acima ja destilam o consenso, mas se precisar do material bruto para uma decisao, sinalize.
- As saidas do painel de 3 lentes nao estao anexadas; seus pontos convergentes ja estao nos requisitos.

## Criterios de aceite

Um documento v2 completo, com DDL concreto para cada tabela nova, a cascata de populacoes, o faseamento A/B, os gates (economia da identificacao, recall dimensionado, validacao de data), e as duas decisoes em aberto apresentadas como recomendacao mais alternativa. Coerente, sem placeholders.

## Formato esperado da saida

O documento v2 inteiro em markdown, em portugues, SEM travessoes (use virgulas), pronto para salvar como o novo spec. Nao inclua comentarios fora do documento.
