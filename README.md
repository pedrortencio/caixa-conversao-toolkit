# caixa-conversao-toolkit

Repositório completo da pesquisa de mestrado sobre o posicionamento da imprensa brasileira frente à **Caixa de Conversão (1906-1914)** — Pedro Ortencio, FFLCH-USP, História Econômica.

## Mapa do repo

| Pasta | O que contém |
|---|---|
| `CLAUDE.md` | Contexto permanente do projeto para sessões do Claude Code (abra o Claude Code SEMPRE da raiz deste repo) |
| `.claude/` | Toolkit: skills (escrita acadêmica, text-as-data, pipeline), agente revisor, permissões |
| `docs/` | Plano do pipeline, registro de decisões metodológicas, codebook por fase |
| `pipeline/` | Código das etapas: scraper da Hemeroteca → transcrição → classificação → consolidação. Prompts versionados em `pipeline/prompts/` |
| `analise/` | Camada estatística: DSL, bootstrap, dicionário, notebooks |
| `dados/` | Dados do projeto. `piloto_1906/` = resultados do piloto; `raw_pdf/` = páginas baixadas (fora do git) |
| `artigo/` | Artigo em LaTeX (`main.tex`, seções, figuras, `referencias.bib`) |
| `fontes/` | Catálogo da bibliografia (`referencias/index.md`) e documentos de arquivo (CPDOC etc.) |
| `legado/` | Scripts originais do piloto de 1906, intactos, como proveniência. Não rodar |

## Como começar (nova sessão de trabalho)

1. Abrir o terminal NA RAIZ deste repo e rodar `claude` (o `CLAUDE.md` e as skills carregam sozinhos).
2. Estado atual e próximos passos: `docs/plano-pipeline.md` (seção Cronograma).
3. Para rodar pipeline: skill `pipeline-hemeroteca` tem os guardrails; nunca pular a regressão de 1906.

## Regras de ouro

- Prompts e codebook são o instrumento de medição: mudanças só com registro em `docs/decisoes.md`.
- `dados/raw_pdf/` e PDFs de bibliografia nunca entram no git (`.gitignore` cuida disso).
- Segredos em `.env` (nunca commitado). API: `GOOGLE_API_KEY`.
