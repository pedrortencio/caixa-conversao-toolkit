# Plano: Batch Mode e camada de anotadores (F3-F4)

Data: 2026-07-14. Status: design aprovado pelo Pedro em sessão com Claude; implementação pendente.
Complementa `docs/plano-pipeline.md` (fases F3 e F4) e a entrada de 2026-07-14 em `docs/decisoes.md`.

## Contexto

Pedro pediu um "integrador" para combinar Claude, Gemini e ChatGPT no trabalho da dissertação,
com dois objetivos: (1) usar mais de um modelo como anotador independente da classificação
(robustez) e (2) reduzir o orçamento de API (~R$830). A investigação de preços e assinaturas
mostrou que um wrapper genérico de CLIs seria a forma errada: CLIs são agentes (system prompt
próprio, ferramentas, comportamento não pinável) e o instrumento de medição deste projeto é
prompt versionado + modelo pinado via API. O caminho certo usa o que o Pedro já paga:

- **Batch Mode da API Gemini**: 50% de desconto em todos os modelos, mesma chamada pinada,
  processamento em até 24h (compatível com os lotes noturnos já planejados).
- **Assinatura Claude**: `claude -p` (headless) roda sem custo por token, limitado pelas
  janelas de uso; serve de segundo anotador a custo marginal zero.
- **Google AI Pro** não cobre a API Gemini (a conta do pipeline segue por token), mas os
  US$10/mês de crédito Google Cloud podem abater parte dela.

## Mudanças no repo

### 1. Batch Mode em `transcreve.py` e `classifica.py` (F3/F4)

Fluxo novo (padrão): montar arquivo JSONL com todas as requisições pendentes, submeter job
batch à API Gemini, aguardar (poll), baixar resultados, gravar. Flags:

- `--sync`: chamada direta um a um, para depurar amostras pequenas (fluxo do plano original).
- `--dry-run`: conta tokens e imprime o teto de custo sem submeter nada (guardrail do CLAUDE.md).

Resume: o que já tem resultado gravado não entra no próximo JSONL. Modelos, prompts e schema
de saída ficam exatamente como o plano define; muda só o transporte e o preço.

### 2. Camada de anotadores (`pipeline/anotadores/`)

Interface única: um anotador recebe (transcrição da edição + bloco de fase do codebook) e
devolve o JSON de classificação no schema atual, sempre registrando `backend`, `modelo` e
versão exata.

- `base.py`: contrato da interface e validação do JSON de saída.
- `gemini_api.py`: **instrumento primário** (encapsula o fluxo batch da seção 1). É o que
  entra como medição no artigo.
- `claude_cli.py`: segundo anotador. Renderiza o mesmo prompt e chama
  `claude -p --model <pinado> --output-format json`, sem ferramentas, uma edição por chamada,
  em lotes noturnos. Modelo padrão: `claude-sonnet-5` (bom equilíbrio qualidade × consumo da
  cota da assinatura; a versão exata devolvida pela CLI é gravada no output de cada edição).
  Quando a janela de uso da assinatura esgota, pausa e retoma sozinho.
- `openrouter_api.py`: NÃO implementado nesta rodada; a interface garante que um terceiro
  anotador entre depois sem retrabalho. Preferência do Pedro para esse futuro: modelo
  ABERTO (DeepSeek, Qwen etc.) via OpenRouter pré-pago; modelos GPT/OpenAI descartados.

### 3. Consolidação (F5)

A tabela `classificacoes` ganha a coluna `backend` além de modelo+versão: uma linha por
edição × anotador.

### 4. Análise de concordância (F6)

Novo `analise/concordancia.py`: κ inter-anotadores par a par por fase, matriz de confusão
Gemini×Claude e lista de edições divergentes exportada para auditoria do Pedro. A amostra de
validação humana (~30 edições/fase) continua aleatória, como no plano; as divergências são
lista de auditoria ADICIONAL, não substituem a validação.

## Orçamento

| Fase | Plano de 13/07 | Com Batch Mode |
|---|---|---|
| Transcrição (Flash) | R$ 400 | ~R$ 200 |
| Escalonamento (Pro) | R$ 160 | ~R$ 80 |
| Classificação (Pro) | R$ 220 | ~R$ 110 |
| Auditoria + validações | R$ 50 | ~R$ 25 |
| Segundo anotador (Claude) | não previsto | R$ 0 (assinatura) |
| **Total** | **~R$ 830** | **~R$ 415** |

Crédito Google Cloud do AI Pro (US$10/mês) abate parte disso. Medir o custo real na regressão
de 1906 antes de qualquer lote completo, como sempre.

## Guardrails preservados

- Regressão de 1906 antes de qualquer lote pago (agora também mede o custo real com desconto).
- Estimativa de custo (`--dry-run`) antes de submeter qualquer batch.
- Versão exata do modelo registrada em todo output, em todos os backends.
- Prompts e codebook inalterados (qualquer mudança neles segue exigindo `docs/decisoes.md`).

## Verificação (critérios de aceite)

1. Regressão 1906 via batch pequeno bate com o gabarito (Paiz 79 / CorreioP 94 / CorreioM 110 /
   Gazeta 146) e o custo real fica registrado.
2. Cinco edições do piloto classificadas por `claude_cli` produzem JSON válido no schema e κ
   calculável contra o Gemini.
3. `--dry-run` imprime o teto de custo sem submeter nada.
4. Interrupção no meio de um lote noturno do `claude_cli` retoma sem duplicar linhas.

## Fora de escopo

- Modelos OpenAI/GPT como anotadores, nesta rodada ou no futuro (decisão do Pedro em 14/07;
  o slot de terceiro anotador, se vier, será um modelo aberto via OpenRouter).
- OpenRouter/mantis-research (extensão futura a considerar, pela mesma interface).
- Estadão; qualquer mudança em prompts ou codebook.

## Apêndice: notas técnicas para o plano de implementação (apuradas em 14/07/2026)

Levantamento feito na sessão de design para o plano detalhado (ainda não escrito) não partir do zero.

**Batch API no SDK `google-genai` (verificado na doc oficial):**
- Criar job: `client.batches.create(model=..., src=<lista inline | nome de arquivo JSONL enviado via client.files.upload>, config={'display_name': ...})`.
- Requisição inline aceita `config` por item (`response_mime_type`, `response_schema`, `system_instruction`); linha de JSONL tem formato `{"key": "id", "request": {<GenerateContentRequest>}}`.
- Poll: `client.batches.get(name=job.name)`; estados terminais `JOB_STATE_SUCCEEDED/FAILED/CANCELLED/EXPIRED`. Resultados inline em `job.dest.inlined_responses` (NA ORDEM das requisições, sem key: o script precisa gravar um manifesto ordem→edição por job); resultados de arquivo via `client.files.download(file=job.dest.file_name)`.
- Limites: inline 20MB por job; JSONL até 2GB; job expira em 48h se pendente; resultados ficam 6 semanas.
- **Transcrição:** PDFs entram por referência (upload via Files API → part `file_data` com `file_uri`), nunca inline (edições têm ~8MB). Upload imediatamente antes de criar o job (TTL do Files API ~48h).
- **Classificação:** texto puro; requisições inline com chunking por bytes (~15MB por job, margem sob os 20MB); manter paridade com o piloto: `temperature=0.2` + `response_mime_type='application/json'`.

**`claude -p` como anotador (claude_cli):**
- Prompt via stdin (transcrições longas estouram linha de comando no Windows); `--output-format json` devolve envelope com o texto em `.result` (tirar cercas de código antes do `json.loads`); `--model claude-sonnet-5`.
- Rodar com cwd NEUTRO (fora do repo) para não injetar CLAUDE.md/skills no contexto do anotador; em modo `-p` pedidos de ferramenta são negados por padrão.
- Sem controle de temperatura pela CLI (aceito: ruído de wrapper só derruba o κ). Limite de uso da assinatura: detectar na saída de erro e pausar/retomar (sleep ~30min).

**Roteamento de fase:** decidível pelo ano do nome do arquivo (`per{bib}_{ano}_{ed:05d}`): 1906→bloco do piloto (já no prompt base), 1907-09/1910-13/1914→blocos do `docs/codebook-fases.md` (hoje ESQUELETO; enquanto Pedro não redigir, classificar só 1906).

**Esqueleto de tarefas do plano:** T1 `pipeline/anotadores/base.py` (render de prompt, parse/validação do JSON, carimbo backend+modelo) + pytest como dev dep (`uv add --dev pytest`; repo ainda não tem testes); T2 `transcricao/transcreve.py` (batch com file refs, manifesto, `--sync`, `--dry-run`, resume por .txt existente); T3 `classificacao/classifica.py` (batch texto, chunking, saída em `dados/classificacoes/gemini/`); T4 `anotadores/claude_cli.py` (saída em `dados/classificacoes/claude/`); T5 `analise/concordancia.py` (κ par a par por fase via sklearn, matriz de confusão, CSV de divergências); T6 verificação gated (regressão 1906 em batch pequeno + custo real). Convenção nova de pastas: `dados/classificacoes/{backend}/per..._.json`.

## Referências de preço (verificadas em 14/07/2026)

- Batch Mode 50%: https://ai.google.dev/gemini-api/docs/pricing
- Benefícios do Google AI Pro (crédito Cloud, sem API): https://support.google.com/googleone/answer/14534406
- Cotas do Gemini CLI: https://geminicli.com/docs/resources/quota-and-pricing/
