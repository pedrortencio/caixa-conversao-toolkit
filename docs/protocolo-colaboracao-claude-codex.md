# Protocolo de colaboração entre Pedro, Claude e Codex

**Versão:** 1.0

**Data de criação:** 15 de julho de 2026

**Status:** proposta operacional aprovada por Pedro

## Objetivo

Este protocolo organiza o uso de Claude e Codex no projeto da Caixa de Conversão. A divisão de trabalho busca combinar especialização sem transformar concordância entre modelos em evidência de validade.

Pedro permanece responsável pelas decisões substantivas, pela codificação humana e pela interpretação histórica. Claude e Codex funcionam como colaboradores com papéis primários distintos e revisão cruzada obrigatória nos pontos de maior risco.

## Princípios

1. **Responsabilidade humana.** Nenhuma decisão metodológica irreversível é tomada apenas porque os dois modelos concordaram.
2. **Independência antes da síntese.** Quando o objetivo for crítica ou validação, Claude e Codex recebem a mesma evidência e produzem pareceres separados antes de conhecer a resposta do outro.
3. **Evidência antes de consenso.** Divergência fundamentada é mais informativa do que consenso sem teste.
4. **Papéis primários, não silos.** Cada sistema lidera uma frente, mas o outro revisa mudanças de alto impacto.
5. **Artefatos explícitos.** Handoffs são feitos por arquivos versionados, testes e relatórios, não por memória informal de conversas.
6. **Rastreabilidade.** Toda execução relevante registra modelo, versão, data, parâmetros, prompt, código e commit.
7. **Reversibilidade.** Mudanças de prompt, codebook e schema são testadas em fixtures antes de alterar resultados em escala.

## Divisão primária de responsabilidades

### Pedro

- Define a pergunta histórica e os limites interpretativos.
- Redige e aprova o codebook substantivo.
- Produz ou supervisiona os códigos humanos.
- Resolve desacordos conceituais e aprova mudanças de estimando.
- Decide quais conclusões entram na dissertação.
- Autoriza lotes pagos após revisar custo e validação.

### Claude, liderança em código e arquitetura

- Implementa pipeline, CLIs, schemas, persistência e automação.
- Mantém testes unitários, integração, resume, retry e observabilidade.
- Produz planos de implementação e migrações de dados.
- Atualiza documentação operacional após mudanças verificadas.
- Realiza revisão de segurança, custos e reprodutibilidade computacional.
- Prepara diffs pequenos, testáveis e acompanhados de evidência de execução.

### Codex, liderança acadêmica e metodológica

- Revisa estimando, seleção, validade de construto, mensuração e inferência.
- Audita coerência entre dissertação, codebook, prompts e dados.
- Avalia desenho da validação humana e escolha de métricas.
- Revisa interpretações históricas para identificar overclaiming.
- Produz pareceres independentes e testes de robustez conceitual.
- Verifica se resultados reportados podem ser reproduzidos pelos artefatos preservados.

## Revisão cruzada obrigatória

| Mudança | Líder | Revisor obrigatório | Aprovação final |
|---|---|---|---|
| Código de scraping e download | Claude | Codex verifica impacto no corpus | Pedro quando afetar seleção |
| Pipeline de transcrição | Claude | Codex revisa protocolo de qualidade | Pedro |
| Prompt ou schema de classificação | Codex e Pedro | Claude revisa implementação e determinismo | Pedro |
| Codebook por fase | Pedro e Codex | Claude testa operacionalização em fixtures | Pedro |
| Amostra de validação | Codex | Claude implementa sorteio reproduzível | Pedro |
| DSL, bootstrap e métricas | Codex | Claude revisa código e testes | Pedro |
| Texto da dissertação | Codex | Claude confere números e caminhos | Pedro |
| Plugin e arquitetura de agentes | Claude | Codex revisa efeitos sobre independência | Pedro |

## Fluxo padrão de trabalho

### 1. Definição

Pedro registra o problema em um arquivo curto contendo objetivo, entrada, saída esperada, restrições e critério de aceite.

### 2. Parecer independente quando houver julgamento

Para mudanças metodológicas, Claude e Codex analisam o problema separadamente. Cada parecer deve distinguir:

- fatos observados;
- inferências;
- riscos;
- alternativas;
- recomendação;
- teste que poderia refutar a recomendação.

### 3. Decisão de Pedro

Pedro escolhe uma alternativa ou solicita experimento adicional. A decisão e sua justificativa entram em `docs/decisoes.md`.

### 4. Implementação

Claude lidera a implementação em unidades pequenas. Cada entrega contém:

- código;
- testes;
- comando de execução;
- resultado dos testes;
- impacto em custo;
- impacto nos dados existentes;
- instrução de rollback ou reprocessamento.

### 5. Auditoria

Codex verifica se a implementação corresponde à decisão metodológica e se os outputs preservam a informação necessária para análise e reprodução.

### 6. Gate humano

Pedro revisa o relatório de auditoria antes de liberar lote pago, alterar o codebook ou atualizar conclusões acadêmicas.

## Protocolo para combinar as CLIs

As CLIs não devem conversar livremente entre si nem produzir uma resposta única sem preservar os pareceres originais. O integrador deve trabalhar com arquivos estruturados.

### Entrada comum

Cada tarefa recebe um manifesto com:

- `task_id`;
- objetivo;
- caminhos de entrada;
- commit do repositório;
- critérios de aceite;
- papel solicitado;
- modelo e configuração;
- orçamento máximo;
- proibição ou autorização de ferramentas.

### Saídas separadas

Cada sistema grava:

- `parecer_claude.md` ou `parecer_codex.md`;
- `resultado.json` quando houver saída estruturada;
- log de execução;
- versão do modelo e da CLI;
- lista de arquivos lidos e alterados;
- testes executados.

### Síntese

A síntese deve mostrar concordâncias e divergências. Ela não substitui os pareceres originais e não escolhe automaticamente a opinião majoritária. Quando a divergência afetar o estimando, o corpus, o codebook ou uma conclusão histórica, a decisão é encaminhada a Pedro.

## Configuração do Claude como anotador

O uso de `claude -p` como segundo anotador é uma análise de sensibilidade, não o instrumento primário. A chamada deve:

- usar modelo fixo;
- fixar effort;
- substituir o system prompt por um prompt específico de mensuração;
- iniciar em modo bare;
- remover ferramentas internas e MCPs;
- registrar versão da CLI;
- gravar a resposta bruta;
- executar fora do contexto normal de desenvolvimento;
- validar o JSON contra schema;
- verificar cada citação como substring da transcrição.

Uma configuração controlada deve considerar flags equivalentes a:

```text
claude --bare -p \
  --model <modelo-fixo> \
  --effort <nivel-fixo> \
  --tools "" \
  --disallowedTools "mcp__*" \
  --system-prompt-file <prompt-de-mensuracao> \
  --output-format json
```

O comando definitivo deve ser testado e versionado antes da primeira rodada.

## Modos de colaboração

### Modo A, implementação

Claude implementa, Codex revisa método e evidência, Pedro aprova impactos substantivos.

### Modo B, revisão acadêmica

Codex produz o primeiro parecer, Claude confere números, artefatos e consistência computacional, Pedro revisa a redação final.

### Modo C, decisão metodológica controversa

Claude e Codex produzem pareceres independentes. Pedro escolhe após examinar evidência, experimento ou amostra manual.

### Modo D, anotação de robustez

Gemini permanece como instrumento primário planejado. Claude atua como segundo anotador controlado. Codex não fornece rótulo de produção, mas audita desenho, métricas, divergências e reporte.

### Nota operacional (15/07/2026)

A implementação distingue formalmente dois níveis: a **consulta de raia única** (um único modelo, dono da raia, sem duplicação; não constitui parecer independente bilateral) e a **revisão independente** (Modo C, com pareceres separados, isolamento estrutural via pacote neutro e autorização explícita de Pedro). Detalhes em `docs/superpowers/specs/2026-07-15-integracao-codex-design.md`.

## Gates obrigatórios

Nenhum lote completo de 1907-1914 é autorizado antes de:

1. recuperar ou reconstruir a validação humana de 1906;
2. auditar os casos sem menção e sem data;
3. completar o codebook das fases 2-4;
4. definir o denominador de posição e saliência;
5. implementar schemas e checagem de evidência;
6. criar testes de regressão com fixtures;
7. passar a ponte 1906 com critérios definidos previamente;
8. medir o custo real numa amostra;
9. obter aprovação explícita de Pedro.

## Tratamento de desacordos

1. Registrar a divergência sem apagá-la.
2. Identificar se o desacordo é factual, conceitual, estatístico ou de implementação.
3. Para desacordo factual, consultar fonte primária ou documentação oficial.
4. Para desacordo conceitual, criar exemplo-limite e pedir codificação humana.
5. Para desacordo estatístico, executar simulação ou análise alternativa.
6. Para desacordo de implementação, escrever teste que represente o comportamento esperado.
7. Se a evidência permanecer inconclusiva, reportar sensibilidade em vez de forçar uma escolha.

## Antipadrões

- Pedir a um modelo que resuma o outro antes de produzir sua própria análise.
- Escolher o rótulo em que dois modelos concordam sem comparação humana.
- Permitir que o agente de código altere prompt ou codebook como efeito colateral.
- Permitir que o agente acadêmico edite código de produção sem teste e revisão.
- Usar confiança autorrelatada pelo modelo como probabilidade calibrada.
- Atualizar resultados sem registrar modelo, prompt e commit.
- Interpretar ausência de erro de execução como validade metodológica.
- Usar consenso entre modelos para substituir a decisão do pesquisador.

## Artefatos mínimos de cada fase

| Fase | Artefatos mínimos |
|---|---|
| F1-F2 | manifesto de busca, inventário, hits, negativos auditados, log de download |
| F3 | prompt, modelo, transcrição, contagem de páginas, flags de qualidade |
| F4 | codebook, schema, rótulo, evidência verificável, backend, versão |
| Validação | amostra, semente, códigos humanos, adjudicação, métricas e script |
| F5 | banco, dicionário de dados, constraints e relatório de integridade |
| F6 | scripts, tabelas, intervalos, diagnósticos e configuração da análise |
| Escrita | tabela ou figura rastreável até script, dados e commit |

## Critério de sucesso do protocolo

O protocolo funciona quando um terceiro consegue identificar:

1. quem propôs cada decisão;
2. qual evidência foi examinada;
3. onde Claude e Codex discordaram;
4. quem aprovou a escolha;
5. qual código e prompt produziram cada resultado;
6. como reproduzir ou contestar a conclusão.

O objetivo da colaboração não é acelerar todas as etapas. É aumentar a velocidade sem perder independência crítica, rastreabilidade e responsabilidade acadêmica.
