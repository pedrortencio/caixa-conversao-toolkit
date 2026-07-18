# Manifesto de consulta: estrutura de colaboração Claude-Codex

- task_id: 2026-07-15-consulta-estrutura-colaboracao
- solicitante: Pedro (a decisão final é dele)
- papel_solicitado: parecer crítico e adversarial sobre a proposta de operacionalização do protocolo de colaboração
- orcamento: uma única rodada; seja econômico, leia apenas os arquivos listados abaixo
- ferramentas: sandbox read-only; NÃO edite nem crie nenhum arquivo; o parecer é sua resposta final em texto

## Contexto (leia estes arquivos do repositório)

1. `docs/protocolo-colaboracao-claude-codex.md` (você o produziu com Pedro em sessão anterior)
2. `docs/avaliacao-independente-2026-07-15.md` (sua auditoria)
3. `CLAUDE.md` (contexto geral do projeto)

## Fatos novos decididos por Pedro hoje (2026-07-15)

- Ponto de entrada único: a sessão do Claude Code (modelo Fable). Pedro não quer operar dois terminais.
- Divisão por raia mantida: Claude lidera código pesado e arquitetura; Codex lidera auditoria metodológica e acadêmica.
- Quando uma tarefa cair na raia do Codex, o Claude invoca `codex exec` headless a partir da sessão dele, passando um manifesto como este.
- Regra de despacho: Claude propõe a invocação, Pedro aprova antes de gastar cota. Cada tarefa vai para UM modelo só (o dono da raia), sem duplicação, por economia de tokens.
- Restrição econômica nova: a assinatura OpenAI de Pedro tem tokens mais subsidiados (custo menor) que os da assinatura Claude. Objetivo declarado: uso máximo e eficiente das duas assinaturas contratadas.
- Ambiente: Windows 11, codex-cli 0.144.4, repo `caixa-conversao-toolkit`.

## Proposta do Claude (o objeto da sua crítica)

- **A (convenção leve):** `AGENTS.md` na raiz definindo o papel do Codex (auditor, não edita código de produção, escreve parecer em arquivo, não vê a opinião do Claude antes de formar a sua) + diretório `colaboracao/` com `manifestos/` e `pareceres/` e dois templates versionados + bloco de despacho no `CLAUDE.md` (tabela de raias, comando `codex exec` canônico com sandbox read-only e saída em arquivo, proibição de o Claude editar pareceres do Codex).
- **C (disciplina do lado do Claude):** skill `.claude/skills/parecer-codex` que guia o Claude no fluxo: montar manifesto com fatos e caminhos (nunca conclusões próprias), propor a Pedro, invocar, registrar parecer bruto, só então sintetizar concordâncias e divergências.
- **B (adiado):** script despachante versionado (valida manifesto, chama `codex exec` com flags fixas, grava log com modelo, versão da CLI, data e commit). Ficaria para quando o volume de pareceres justificar.
- Recomendação do Claude: A + C agora, B depois.

## Perguntas

1. **Central:** essa estrutura preserva a independência exigida pelo protocolo, considerando que o revisado (Claude) redige o manifesto, invoca o revisor (Codex) e sintetiza o parecer? Quais salvaguardas mínimas faltam?
2. **Secundária:** dado o custo menor do token OpenAI, faz sentido rebalancear as raias, por exemplo o Codex assumir mais trabalho além da auditoria (código de análise estatística, rascunhos de seção, checagens mecânicas), sem violar a separação entre instrumento e auditor definida no protocolo?
3. **Prática:** algo no desenho conflita com como o `codex exec` de fato funciona (sandbox, AGENTS.md, sessões, cota da assinatura)?

## Formato do parecer (responda em português)

Estruture em: fatos observados; inferências; riscos; alternativas; recomendação; teste que poderia refutar sua recomendação. Seja direto; divergência fundamentada vale mais que concordância.
