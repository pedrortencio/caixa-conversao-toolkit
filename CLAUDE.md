# caixa-conversao-toolkit

Pesquisa de mestrado de Pedro Ortencio (FFLCH-USP, História Econômica, orientador Ivan Salomão) sobre o posicionamento da grande imprensa a respeito da **Caixa de Conversão (1906-1914)**.

**Este arquivo contém apenas o que não muda de semana em semana: regras, guardrails, proibições e ponteiros.** Estado datado não mora aqui, porque o CLAUDE.md está sempre em contexto e ninguém relê o que já sabe de cor, então um número desatualizado aqui vira mentira que se propaga. O estado medido mora em `docs/MAPA-DO-PROJETO.md`, com data no cabeçalho. O histórico de por que cada coisa é como é mora em `docs/decisoes.md`, append-only.

**Comece por `docs/MAPA-DO-PROJETO.md`.** Se ele estiver com data muito anterior ao último commit, confie no git e nos manifestos, não nele, e avise o Pedro.

Outros ponteiros: plano do pipeline em `docs/plano-pipeline.md`; debate metodológico aberto em `docs/contexto-debate-metodologico-mensuracao.md`; fontes de estudo em `docs/fontes-de-estudo.md`. Documentos de estado antigos (`handoff-2026-07-16-base-corpus.md`, `estado-2026-07-23-pos-rotulagem.md`, `retomada-2026-07-26.md`) valem como histórico da data em que foram escritos, não como estado atual.

## Pergunta, e os dois objetos que não devem ser confundidos

A pergunta histórica é qual tipo de pensamento prevaleceu no debate sobre a Caixa entre os principais diários de RJ e SP. Dela saem **dois produtos distintos**, com exigências metodológicas diferentes. Confundi-los já produziu erro registrado (`docs/decisoes.md`, 2026-07-28).

**Objeto 1, mapeamento descritivo.** Catalogar debates, agentes, posições e marcos ao longo do tempo, com citação verbatim rastreável. Alimenta a escrita e a leitura próxima. O guardrail que o governa é a conferência mecânica de citação, não κ nem bootstrap. Está em execução.

**Objeto 2, estimativa quantitativa.** Distribuição de posições por unidade de análise entre os jornais. É a ele que se aplicam padrão-ouro, κ por fase, DSL e bootstrap. **Ainda não tem instrumento escolhido.**

### O que está aberto no objeto 2

Nada do desenho herdado do piloto está decidido. A escala de -2 a +2, a unidade edição-dia, o enquadramento como *stance detection*, o uso de LLM para detectar posição, o DSL e as regras de agregação são candidatos, não escolhas. Antes de implementar triagem substantiva, schema classificatório ou classificação em lote, ler `docs/contexto-debate-metodologico-mensuracao.md`, que é o gate, e `docs/desenhos-concorrentes.md`, que especifica os concorrentes.

Regra que decorre disso: **processamento que seleciona, descarta ou estrutura informação segundo o construto não é neutro** e precisa passar pelo gate. Inventariar, transcrever com proveniência e preservar contexto são reversíveis e podem avançar.

O eixo substantivo do período é **valorização contra emissão e estabilidade a taxa nova**, não metalismo contra papelismo. A clivagem metalismo-papelismo pertence ao Encilhamento e em 1906 já não divide os campos. Ver a correção de 2026-07-28 em `docs/decisoes.md` e o achado 4 de `docs/exploracao-base-2026-07-28.md`.

## Corpus (Hemeroteca Digital da BN, memoria.bn.gov.br)

| Jornal | bib | Gabarito do piloto 1906 (arquivos / números distintos) |
|---|---|---|
| O Paiz | per178691 | 79 / 79 |
| Correio Paulistano | per090972 | 94 / 93 |
| Gazeta de Notícias | per103730 | 146 / 146 |
| Correio da Manhã | per089842 | 110 / 108 |
| **total** | | **429 / 426** |

A diferença entre as duas colunas é a coalescência de variantes A e B com o mesmo número BN no mesmo dia. **O portão de 1906 conta números distintos, 426, não arquivos.** Citar 429 como "edições" é erro.

Acervos divididos em pastas por década (ex.: `178691_02` = 1890-99). Nomenclatura de arquivo: `per{bib}_{ano}_{página:05d}`. Estadão fica para fase futura (acervo próprio, fora da BN). O Retrospecto Commercial do Jornal do Commercio (bib 180688) entrou como material anual de apoio, com estatuto no desenho ainda em aberto.

## Fases do codebook (deriva conceitual do construto)

1906 criação (Taubaté, taxa baixa contra o par legal de 27 dinheiros) · 1907-09 operação, lastro e alfândega · 1910-13 taxa de 16 dinheiros e ampliação do limite · 1914 suspensão do troco. Definições operacionais em `docs/codebook-fases.md`.

As fases 2 a 4 são esqueleto e sua redação é do Pedro. O bloco de cada fase sai da **leitura das fontes e da historiografia**, nunca do prompt nem do que um modelo devolve: codebook derivado de prompt mede o que o modelo supõe, e a validação por κ contra códigos humanos vira circular. Protocolo em `docs/plano-leitura-fases.md`.

## Onde as coisas vivem

**No repo (o instrumento):** código, prompts versionados, manifestos, decisões, pareceres com hash, amostras leves. O repo é um instrumento de medição versionado, e isso governa o que entra.

**Em `C:\dados-caixa` (o acervo):** PDF bruto, camada de texto e o banco. Grandes, reprodutíveis a partir dos manifestos, fora do git e fora do OneDrive. Backup em `G:\My Drive\caixa-conversao`.

Fluxo: `pipeline/scraper/` → `pipeline/base/` (banco, censo, portão) → `pipeline/triagem/` → `pipeline/catalogo/` → `pipeline/analise/`. Scripts do piloto em `legado/` são referência e não devem ser rodados.

`pipeline/prompts/` guarda os prompts, que **são instrumento de medição**: mudança exige versão nova e registro em `docs/decisoes.md`.

## Ambiente Python

Gerenciado com **uv** (`pyproject.toml` + `uv.lock`, Python pinado em 3.12 via `.python-version`). Rodar sempre com `uv run python caminho/script.py`, nunca pip ou venv manuais. Dependência nova: editar `pyproject.toml` e `uv sync`.

**O `.venv` do repo é uma junction para `C:\dados-caixa\envs\`**, porque a política de Application Control do Windows bloqueia executável dentro do OneDrive. Consequência prática: `uv run pytest` falha com `os error 4551`, e a forma que funciona é **`uv run python -m pytest`**. Se qualquer comando quebrar com "Application Control policy has blocked this file", refazer a junction é o conserto.

SDKs: Gemini via **`google-genai`** (`from google import genai`), pois o `google-generativeai` do legado está descontinuado; Claude via `anthropic`. Chaves em `.env`, nunca commitadas.

## Guardrails (não negociáveis)

- **Nunca rodar lote pago de API sem antes passar o portão de 1906** e sem medir o custo real da rodada. O portão é executável por `/regressao-1906` e o hook `.claude/hooks/gate_lote_pago.py` barra as etapas pagas enquanto ele reprovar. A lista de exceções só vale com aprovação escrita do Pedro no manifesto; **modelo não se auto-aprova exceção**.
- Orçamento de tokens de API: cerca de R$ 830 no total. Estimar custo antes de qualquer lote acima de 100 chamadas.
- **Nenhum fornecedor de IA está pré-escolhido.** Qual serviço e qual modelo executam cada tarefa sai de avaliação comparativa de efetividade dentro do orçamento, registrada em `docs/decisoes.md`. O que é obrigatório em qualquer caso: gravar serviço, modelo, versão exata e prompt no output de toda anotação.
- **Toda citação devolvida por qualquer anotador é conferida mecanicamente** contra o texto de origem: normalizada, tem de ser substring literal da janela. Linha que não casa é rejeitada, nunca corrigida. A taxa de rejeição por anotador é métrica de qualidade do lote e é publicada.
- Scraping da BN: rate limit de 2 a 3 s por requisição, retry com backoff, resume, e lotes grandes de madrugada.
- PDF bruto e banco nunca entram no git. Transcrições, anotações e classificações (texto leve, domínio público) sempre entram.
- Trabalho por esta sessão consome a assinatura do Claude Code, que é recurso escasso. Preferir passo determinístico a chamada de modelo, e avisar o custo antes de etapa cara.

## Armadilhas medidas nas fontes

- **A coluna `texto` de `dados/triagem/amostra_para_rotular.csv` não é a página.** É reconstrução de modelo e falha de três maneiras medidas: interpola resumo próprio entre colchetes (3,8% das peças e 13,3% dos editoriais), sangra para a coluna vizinha e, em ao menos um caso, entrega artigo diferente. **Ler na página, ou no `ocr_contexto`**, que é OCR determinístico da Hemeroteca. Citação só vale se transcrita da página.
- **O ruído de OCR varia por célula jornal-ano**, de 4,84% a 14,33% em O Paiz. Comparação entre anos ou entre jornais está confundida pela digitalização, e isso já derrubou uma justificativa de análise.
- **A mesma peça circula entre jornais.** Discursos parlamentares são reproduzidos por vários diários; sem deduplicação o corpus conta o mesmo argumento como opinião de dois jornais.
- **Hospedar voz não é ter posição.** `SECÇÃO LIVRE` é espaço pago, e relato de sessão parlamentar é fala de terceiro. Atribuir ao jornal a posição de quem ele publica é o erro que o campo `voz` existe para impedir.
- **A menção pelo nome não discrimina:** atinge 53% do acervo, em boa parte por boletim diário de movimento da Caixa. É ruído para posição e sinal para saliência.

## Validações obrigatórias antes de interpretar resultados

Aplicam-se ao **objeto 2**, a estimativa quantitativa, e não são pré-requisito do mapeamento descritivo.

Ponte 1906 (instrumento novo contra o piloto contra códigos humanos; o piloto deu κ=0.712 e ρ=0.670) · κ por fase, com cerca de 30 edições por fase codificadas pelo Pedro · auditoria de recall, com falso negativo por jornal · DSL e bootstrap na análise final. Nenhuma peça usada para construir o codebook entra no conjunto de teste.

Concordância entre modelos é análise de sensibilidade, **não** validação humana nem validade de construto, e precisa aparecer assim no artigo.

## Ferramental determinístico do repo

Regra que não pode falhar não pode morar em skill, porque skill é discricionária. Hook e comando são executados pelo harness.

- Comandos: `/regressao-1906` roda o portão e reporta o veredito; `/suite` roda os testes.
- Hook: `.claude/hooks/gate_lote_pago.py` barra etapa paga com o portão fechado.
- Agente: `revisor-metodologico`, para crítica de rascunho por quem não participou da escrita.
- Skills do projeto: `pipeline-hemeroteca`, `escrita-academica`, `parecer-codex`, `text-as-data`.

## Escrita

Todo texto acadêmico segue a skill `escrita-academica`. Regra mais importante: **nunca usar travessões** (em-dashes) em texto para o Pedro, substituir por vírgulas.

## Colaboração Claude-Codex (despacho)

Pedro opera só este chat e o Codex é invocado daqui. Spec em `docs/superpowers/specs/2026-07-15-integracao-codex-design.md`, protocolo completo em `docs/protocolo-colaboracao-claude-codex.md`, skill `parecer-codex`.

- Raias: Claude lidera código e arquitetura; Codex lidera auditoria metodológica e acadêmica e pode ser implementador designado (análise estatística, simulações, rascunhos). **Quem implementa um artefato não o audita.**
- Despacho: Claude propõe, Pedro aprova ANTES de gastar cota. Nível ordinário (consulta de raia única): ok rápido sobre objetivo e custo. Nível crítico (construto, estimando, corpus, codebook, instrumento, conclusão histórica): Pedro revisa o manifesto completo e autoriza pareceres duplos com isolamento estrutural, com o parecer do Claude congelado e hasheado antes do despacho.
- Invocação SEMPRE via `scripts/invoca-codex.ps1`, nunca `codex exec` à mão: encoding, effort high, `--ephemeral`, `--ignore-user-config`, JSONL e registro em `colaboracao/registros/` são automáticos.
- Proibições: Claude não edita parecer do Codex; a síntese cita cada divergência com referência ao parecer original e não o substitui; parecer bruto vai a Pedro antes ou junto da síntese; sem fallback silencioso de modelo quando a cota acabar.
- **Codex pode anotar** (autorizado em 2026-07-28). No piloto de catalogação, Claude e Codex anotam as MESMAS janelas com o MESMO prompt, para concordância entre anotadores medida e não presumida.

## Gate de responsabilidade

Claude e Codex podem pesquisar métodos, formular alternativas, produzir pareceres, implementar benchmarks e procurar problemas. **Nenhum consenso entre modelos constitui validade científica.** Pedro mantém autoridade sobre a pergunta histórica, a definição do construto, o codebook e o padrão-ouro, a escolha entre desenhos, e a interpretação publicada. Decisão que altere qualquer um desses cinco vai a ele, não é tomada em sessão.

## Git

Commits como Pedro Ortencio <pedrortencio@gmail.com>, já configurado no repo. Repo privado `pedrortencio/caixa-conversao-toolkit`.
