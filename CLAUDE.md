# caixa-conversao-toolkit

Pesquisa de mestrado de Pedro Ortencio (FFLCH-USP, História Econômica, orientador Ivan Salomão): posicionamento editorial da grande imprensa sobre a **Caixa de Conversão (1906-1914)**. Este repo contém pipeline de dados, toolkit, artigo e fontes. Plano completo: `docs/plano-pipeline.md`. Registro de decisões: `docs/decisoes.md`. Comunidades e fontes de estudo contínuo: `docs/fontes-de-estudo.md`.

## Pergunta e estimando

Qual grupo/tipo de pensamento (ortodoxo vs expansionista) prevaleceu no debate sobre a Caixa entre os principais jornais. Estimando: distribuição de posições editoriais por **edição-dia** (escala -2 ortodoxo ↔ +2 expansionista) entre os principais diários de RJ/SP (censo intencional, não amostra). Resultado principal: shares por categoria; média como resumo; saliência mensal como série complementar.

## Corpus (Hemeroteca Digital da BN — memoria.bn.gov.br)

| Jornal | bib | Regressão 1906 (gabarito do piloto) |
|---|---|---|
| O Paiz | per178691 | 79 edições |
| Correio Paulistano | per090972 | 94 edições |
| Gazeta de Notícias | per103730 | 146 edições |
| Correio da Manhã | per089842 | 110 edições |

Acervos divididos em pastas por década (ex.: `178691_02` = 1890-99). Estadão fica para fase futura (acervo próprio, fora da BN). Nomenclatura de arquivo: `per{bib}_{ano}_{página:05d}`.

## Fases do codebook (deriva conceitual do construto)

1906 criação (Taubaté, 12d vs 27d) · 1907-09 operação/lastro · 1910-13 taxa 16d/expansão · 1914 crise/colapso. Definições operacionais: `docs/codebook-fases.md`. O prompt de classificação recebe o bloco da fase da edição.

## Pipeline (estado em 2026-07-14)

- **F1 em andamento:** enumeração via Selenium validada; download resolvido SEM DocReader, via host estático `hemeroteca-pdf.bn.gov.br/{bib}/per{bib}_{ano}_{edição:05d}.pdf` (`pipeline/scraper/download.py` testado). Falta: enumeração completa 1907-14 + download noturno.
- **F3-F4 com design aprovado:** Batch Mode da API Gemini (50% de desconto; orçamento ~R$830 → ~R$415) + camada `pipeline/anotadores/` (`gemini_api` primário + `claude_cli` segundo anotador via assinatura). Spec: `docs/plano-batch-anotadores.md` (com apêndice técnico pronto para o plano de implementação, que ainda não foi escrito).
- **Codebook:** fases 2-4 são esqueleto; Pedro redige antes de F4.

`pipeline/scraper/` → `pipeline/transcricao/` → `pipeline/classificacao/` → `pipeline/consolidacao/` → `analise/`. Scripts do piloto (referência, não rodar): `legado/`. Prompts versionados (instrumento de medição, mudanças só com registro em `docs/decisoes.md`): `pipeline/prompts/`.

## Ambiente Python

Gerenciado com **uv** (`pyproject.toml` + `uv.lock`; Python pinado em 3.12 via `.python-version`). Rodar qualquer script com `uv run python caminho/script.py` (nunca pip/venv manuais). Dependência nova: editar `pyproject.toml` e `uv sync`. SDK do Gemini: **`google-genai`** (`from google import genai`) — o `google-generativeai` do legado está descontinuado, não usar em código novo. Claude: SDK `anthropic`. Chaves em `.env` (`GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`); modelo em `.env.example`.

## Guardrails (não negociáveis)

- **Nunca rodar lote completo de API sem antes passar a regressão de 1906** (contagens do gabarito acima) e medir o custo real da rodada.
- Orçamento do projeto: ~R$ 830 em tokens no total (~algumas centenas de R$/mês). Estimar custo antes de qualquer lote > 100 chamadas.
- Modelos: transcrição `gemini-2.5-flash` (escala p/ `-pro` só nas falhas); classificação `gemini-2.5-pro`. Sempre registrar a versão exata do modelo no output.
- Scraping da BN: rate limit 2-3 s/requisição, retry com backoff, resume; rodar lotes grandes de madrugada.
- `dados/raw_pdf/` nunca entra no git (gitignored). Transcrições e classificações (texto leve, domínio público) sempre entram.
- API key Gemini em `.env` (`GOOGLE_API_KEY`), nunca commitada.

## Validações obrigatórias antes de interpretar resultados

Ponte 1906 (modelo novo × gemini-1.5-pro do piloto × códigos humanos; piloto: κ=0.712, ρ=0.670) · κ por fase (~30 edições/fase codificadas pelo Pedro) · auditoria de recall (falso negativo por jornal) · DSL + bootstrap na análise final.

## Escrita

Todo texto acadêmico segue a skill `escrita-academica`. Regra mais importante: **nunca usar travessões** (em-dashes) em texto para o Pedro; substituir por vírgulas.

## Colaboração Claude-Codex (despacho)

Pedro opera só este chat; o Codex é invocado daqui. Spec: `docs/superpowers/specs/2026-07-15-integracao-codex-design.md`. Skill: `parecer-codex`.

- Raias (tabela completa no `docs/protocolo-colaboracao-claude-codex.md`): Claude lidera código e arquitetura; Codex lidera auditoria metodológica e acadêmica e pode ser implementador designado (análise estatística, simulações, rascunhos). Quem implementa um artefato não o audita.
- Despacho: Claude propõe, Pedro aprova ANTES de gastar cota. Nível ordinário (consulta de raia única): ok rápido sobre objetivo e custo. Nível crítico (estimando, corpus, codebook, instrumento, conclusão histórica): Pedro revisa o manifesto completo e autoriza pareceres duplos com isolamento estrutural (pacote isolado, parecer do Claude congelado e hasheado antes do despacho).
- Invocação SEMPRE via `scripts/invoca-codex.ps1` (nunca `codex exec` manual): encoding, effort high, `--ephemeral`, `--ignore-user-config`, JSONL e registro em `colaboracao/registros/` são automáticos.
- Proibições: Claude não edita pareceres do Codex; a síntese cita cada divergência com referência ao parecer original e não o substitui; parecer bruto vai a Pedro antes ou junto da síntese; sem fallback silencioso de modelo quando a cota acabar.
- Codex NUNCA anota produção (instrumento primário: API Gemini; segundo anotador: `claude -p`).

## Git

Commits como Pedro Ortencio <pedrortencio@gmail.com> (já configurado no repo). Repo privado `pedrortencio/caixa-conversao-toolkit`.
