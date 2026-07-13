# caixa-conversao-toolkit — repo de pesquisa completo + pipeline Hemeroteca (1906-1914) — v3

## Contexto

Pedro quer um **repositório git único e organizado** que contenha toda a pesquisa do artigo/dissertação sobre a Caixa de Conversão: o pipeline de dados (scraping da Hemeroteca → transcrição → classificação → base), o toolkit de Claude Code (skills, agente revisor, CLAUDE.md), o codebook, o artigo em LaTeX e o catálogo de fontes. Ele não tem experiência com organização de repos e quer aprender fazendo — logo o repo deve ser **autodocumentado** (README curto por pasta explicando o que entra ali e por quê). Semear a partir do piloto já baixado em `C:\Users\pedro\OneDrive\Documentos\Acadêmico\Dissertação Mestrado\Dados\AI-RnC-Pedro-main` (ZIP do GitHub, sem `.git`).

As decisões metodológicas do pipeline (v2, fechadas em 13/07/2026) permanecem válidas — ver seção "Decisões metodológicas" abaixo.

## Estrutura do repo (novo: `caixa-conversao-toolkit`, privado, em `...\Dissertação Mestrado\Dados\`)

```
caixa-conversao-toolkit/
├── CLAUDE.md                  # contexto permanente enxuto (projeto, estimando, bibs, comandos, guardrails)
├── README.md                  # mapa do repo + como começar
├── .claude/
│   ├── skills/
│   │   ├── escrita-academica/SKILL.md    # registro acadêmico PT, anti-padrões do Pedro (da memória), ABNT
│   │   ├── text-as-data/SKILL.md         # receitas: κ/ρ, ponte, DSL, bootstrap, reporte de validação, refs canônicas
│   │   └── pipeline-hemeroteca/SKILL.md  # como rodar cada etapa, resume, guardrails de custo, regressão 1906
│   ├── agents/revisor-metodologico.md    # parecerista de ciências sociais aplicadas; read-only; crítica estruturada
│   └── settings.json                     # permissões (python, pip, git) p/ menos prompts
├── docs/
│   ├── plano-pipeline.md      # este plano, versionado
│   ├── decisoes.md            # registro de decisões metodológicas (data + alternativas + porquê)
│   └── codebook-fases.md      # definições operacionais por fase (Pedro redige a partir do Cap. 2)
├── pipeline/
│   ├── scraper/               # jornais.py, busca_hits.py, baixa_paginas.py, inventario.py, auditoria_recall.py
│   ├── transcricao/           # transcreve.py (evolução do rnc1.0.py)
│   ├── classificacao/         # classifica.py (evolução do text_analysis2.0.py)
│   ├── consolidacao/          # consolida.py → SQLite/xlsx/parquet
│   └── prompts/               # transcricao.md, classificacao_base.md + bloco por fase (versionados)
├── analise/                   # dsl_correcao.py, dicionario.py, notebooks/
├── dados/
│   ├── piloto_1906/           # dados do piloto migrados do AI-RnC-Pedro-main (txts, jsons, xlsx) — histórico
│   ├── scraping/              # hits_{jornal}.csv, registros de busca
│   ├── raw_pdf/               # páginas baixadas (GITIGNORED — pesado; fica local/OneDrive)
│   ├── transcricoes/          # txts (versionados — texto leve, domínio público)
│   ├── classificacoes/        # jsons (versionados)
│   └── base/                  # caixa_conversao.db + parquet
├── artigo/                    # main.tex, secoes/, figuras/, referencias.bib
├── fontes/
│   ├── referencias/index.md   # catálogo da bibliografia (PDFs de terceiros GITIGNORED — copyright/ruído)
│   └── cpdoc/                 # documentos CPDOC + catalogação (públicos, versionáveis)
├── legado/                    # scripts originais do piloto intactos (rnc1.0.py etc.) — proveniência
├── requirements.txt
└── .gitignore                 # raw_pdf, fontes/referencias/*.pdf, .env, __pycache__
```

**Princípios:** texto derivado de jornal 1906-14 é domínio público → versionar; PDFs brutos e bibliografia de terceiros → gitignore + catálogo em md; nada de dado pesado no histórico git; prompts e codebook SEMPRE versionados (são o instrumento de medição).

## Fase 0 — Bootstrap do repo e toolkit (~1 sessão)

1. Repo **já criado pelo Pedro: `pedrortencio/caixa-conversao-toolkit`** (acesso local verificado via `ls-remote`, branch `main` já existe). `git clone https://github.com/pedrortencio/caixa-conversao-toolkit` em `Dados\` e configurar no repo `git config user.name "Pedro Ortencio"` / `user.email pedrortencio@gmail.com` (para os commits não saírem como CptB42).
2. Montar estrutura acima; migrar conteúdo de **`Dados\AI-RnC-Pedro-main`** (versão atualizada do piloto, já baixada pelo Pedro — é a fonte da verdade, não o clone do scratchpad): scripts → `legado/`, dados → `dados/piloto_1906/`, prompts extraídos dos scripts → `pipeline/prompts/`.
3. Escrever `CLAUDE.md` (migrando fatos da memória automática: estimando, corpus, bibs `per178691/090972/103730/089842`, fases, gabarito regressão 1906: Paiz 79/CorreioP 94/CorreioM 110/Gazeta 146, orçamento, decisões-chave).
4. Escrever as 3 skills + agente revisor + settings.json + READMEs por pasta.
5. `main.tex` esqueleto do artigo em `artigo/` (estrutura: intro, contexto histórico, dados e método, resultados, conclusão) + `referencias.bib` inicial.
6. Commit inicial + push. Smoke test: abrir sessão nova do Claude Code na raiz, verificar CLAUDE.md carregado e skills disparando.
7. **A partir daqui, Pedro abre o Claude Code sempre da raiz do repo** (memória automática nova fica atrelada a essa pasta).

## Decisões metodológicas (fechadas 13/07/2026 — inalteradas da v2)

1. **Estimando explícito:** distribuição de posições editoriais por edição-dia (ortodoxo -2 ↔ expansionista +2) entre os principais diários das duas capitais (censo intencional). Resultado principal: shares por categoria; média como resumo.
2. **Unidade:** edição-dia holística (preserva validação do piloto, κ=0.712); saliência mensal como série complementar.
3. **Codebook por fase** (corrige deriva conceitual): criação (1906) / operação-lastro (1907-09) / taxa 16d-expansão (1910-13) / crise-colapso (1914). Validação humana: ~30 edições/fase codificadas por Pedro; κ por fase.
4. **Corpus:** busca exata "caixa de conversão" no DocReader + auditoria de recall (edições sem hit amostradas, verificadas via Flash; falso negativo por jornal reportado).
5. **Output ampliado:** + `n_itens_relevantes`, `houve_editorial`, `proeminencia`; Neutral ≠ Mixed na análise.
6. **Modelos:** transcrição `gemini-2.5-flash` (→ `-pro` nas falhas); classificação `gemini-2.5-pro`; **ponte 1906** (novo × 1.5 Pro × humano).
7. **Scraping: Selenium adaptando pyHDB** (citável; DocReader = WebForms/Telerik com VIEWSTATE, verificado 13/07; sem API limpa). Sondar `SaveAsFile.ashx` p/ download em lote na sessão.
8. **Camada estatística auditável:** DSL (amostra humana ~130 edições) + bootstrap + triangulação por dicionário do Cap. 2 — retrofit sobre a base, zero API.
9. **Fora desta rodada:** mascaramento do jornal, anotador de modelo aberto, Estadão (fonte própria, futuro).

## Fases 1-6 — Pipeline (como na v2, caminhos sob `pipeline/` e `analise/`)

- **F1 Scraper:** `jornais.py` (bibs + pastas de década), `busca_hits.py` (Selenium, registra termo+data de busca), `baixa_paginas.py` (hit ±1, rate limit 2-3s, resume, nomenclatura `per{bib}_{ano}_{pág:05d}.pdf`). **Regressão 1906 contra gabarito do piloto antes de qualquer coisa.**
- **F2 Inventário + auditoria de recall:** hits por jornal×mês, flags de meses zerados em períodos quentes; ~15 edições sem hit/jornal → Flash → taxa de falso negativo.
- **F3 Transcrição:** `transcreve.py` com CLI, skip, retry; prompt do piloto inalterado.
- **F4 Classificação:** `classifica.py` com bloco de fase do codebook; regex data `(190[6-9]|191[0-4])`; ponte 1906; validação por fase.
- **F5 Consolidação:** SQLite (`edicoes`, `classificacoes` c/ modelo+versão pinada e fase, `codigos_humanos`, `buscas`) + xlsx + parquet.
- **F6 Análise auditável:** `dsl_correcao.py` (shares corrigidos + ICs bootstrap), `dicionario.py` (léxico do Cap. 2; correlação com série LLM).

## Custos

≈ 4-6 mil páginas novas. Flash transcrição ≈ R$400; Pro escalonamento ≈ R$160; Pro classificação ≈ R$220; auditoria ≈ R$30; ponte/validações < R$20. **≈ R$830 total**, medir custo real na regressão de 1906 antes do lote.

## Cronograma (2 meses)

| Semanas | Entrega |
|---|---|
| 1 | Fase 0 (repo+toolkit) + scraper Selenium + regressão 1906 |
| 2 | Download 1907-14 (noturno) + inventário + auditoria de recall |
| 3-4 | Transcrição em lote; Pedro redige codebook e codifica amostras de validação |
| 5 | Classificação completa + ponte 1906 + κ por fase |
| 6 | Base consolidada + DSL/bootstrap + dicionário |
| 7-8 | Interpretação e artigo |

## Verificação

1. **F0:** sessão nova na raiz carrega CLAUDE.md; cada skill dispara com pedido correspondente; revisor roda sobre o Cap. 3 como teste.
2. **F1:** regressão 1906 = gabarito; 5 PDFs aleatórios contêm o termo.
3. **F2:** falso negativo < ~10% (senão rediscutir triagem).
4. **F3:** 3 transcrições vs imagem original.
5. **F4:** ponte 1906 e κ por fase ≥ ~0.7.
6. **F5/F6:** linhas de `classificacoes` = edições com txt; série sem buracos não explicados; DSL e dicionário rodam da base sem API.

## Riscos

- BN instável / layout muda → resume em tudo, Selenium isolado, rodar de madrugada.
- Recall baixo em algum jornal → auditoria pega na semana 2, dá tempo de ampliar termos.
- κ baixo numa fase → revisar codebook daquela fase antes do lote completo.
- OneDrive × git (repo dentro do OneDrive): aceito como backup; se o sync atrapalhar (locks em `.git`), mover o repo para fora e deixar só `dados/` espelhado.
