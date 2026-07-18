# Manifesto de auditoria: esquema da base do corpus

- task_id: 2026-07-16-auditoria-esquema-base-corpus
- solicitante: Pedro (a decisao final e dele)
- papel_solicitado: auditor metodologico
- nivel: critico (envolve o corpus); modo AUDITORIA (voce le o spec e o audita), nao parecer independente isolado
- gate: autorizado por Pedro em 16/07/2026 para consulta ao Codex antes da coleta de dados
- orcamento: uma unica rodada; leia apenas os arquivos listados
- ferramentas: sandbox read-only; NAO edite nem crie arquivos; o parecer e sua resposta final em texto
- workdir: repo principal (branch main), commit d47f364; o spec auditado esta untracked neste commit

## Objetivo

Auditar o desenho da base de dados do corpus (o spec listado abaixo) antes de a equipe iniciar a coleta e o processamento dos dados. A base e a fonte da verdade operacional que torna o corpus da Hemeroteca (1906-1914) legivel por maquina. A camada de medicao (classificacao de postura, codigos humanos) esta deliberadamente fora deste spec e sera redesenhada numa rodada metodologica posterior, com a sua participacao.

Questao central: este desenho de corpus e solido e seguro para comecar a coleta agora? Que riscos metodologicos ou de engenharia de dados voce ve, em especial quanto a:

1. a extracao cirurgica (transcrever apenas paginas identificadas como relevantes a Caixa) pre-condicionar a metodologia de medicao futura;
2. o denominador da saliencia e o tratamento de censo versus apenas hits;
3. a unidade edicao-dia e a resolucao de data pelo masthead;
4. recall (o que a identificacao nao pega nunca e transcrito);
5. qualquer coisa relevante que o desenho ignore, a luz da sua auditoria anterior e do P0 que voce levantou.

## Arquivos de contexto (leia apenas estes, relativos ao workdir)

1. docs/superpowers/specs/2026-07-16-esquema-base-corpus-design.md (o spec auditado)
2. docs/plano-pipeline.md (plano geral do pipeline)
3. docs/avaliacao-independente-2026-07-15.md (sua auditoria anterior; continuidade)
4. CLAUDE.md (contexto operacional e guardrails)

## Evidencia potencialmente relevante nao fornecida

- Os dados reais do piloto 1906 (transcricoes em dados/piloto_1906/data_processed/, PDFs em dados/raw_pdf/piloto_1906/, analises em dados/piloto_1906/analises_json/) nao estao anexados; o spec resume os achados de validacao na secao 3, mas voce nao ve o material bruto.
- O prompt de classificacao (pipeline/prompts/classificacao_base.md) e o codebook (docs/codebook-fases.md) existem mas nao estao na lista, por a medicao estar fora de escopo; se julgar necessario para avaliar o agnosticismo do corpus, sinalize.
- A discussao que produziu o spec nao e fornecida; julgue o artefato como esta.
- O denominador da saliencia e a mecanica do censo estao marcados como questoes em aberto (secao 10 do spec), nao resolvidos.

## Criterios de aceite

Um parecer que diga, com fundamentacao, se o desenho pode sustentar a coleta agora, quais riscos sao bloqueantes versus toleraveis, e o que mudaria antes de comecar. Divergencia fundamentada vale mais que concordancia.

## Formato esperado da saida (responda em portugues)

Estruture em: fatos observados; inferencias; riscos (ranqueados); alternativas; recomendacao (pode comecar a coleta ou nao, e o que ajustar antes); teste que poderia refutar sua recomendacao.
