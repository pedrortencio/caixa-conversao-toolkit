## Fatos observados

1. O protocolo distingue três situações que a proposta do Claude está tratando como se fossem uma só:

   - tarefa executada por um único dono de raia;
   - revisão cruzada de uma implementação;
   - decisão metodológica controversa, que exige pareceres independentes de Claude e Codex sobre a mesma evidência.

2. A regra nova, “cada tarefa vai para um modelo só, sem duplicação”, é compatível com a primeira situação, mas conflita literalmente com:

   - “revisão cruzada obrigatória nos pontos de maior risco”;
   - o Modo C, com pareceres independentes;
   - o princípio segundo o qual ambos recebem a mesma evidência antes da síntese.

3. A proposta A+C cria boa disciplina documental, mas concentra no Claude quatro poderes:

   - enquadrar a pergunta;
   - selecionar a evidência apresentada;
   - acionar o revisor;
   - sintetizar o resultado.

4. O `codex exec` 0.144.4 instalado oferece os mecanismos necessários:

   - `--sandbox read-only`;
   - `--model`;
   - `--cd`;
   - `--ephemeral`;
   - `--ignore-user-config`;
   - `--json`;
   - `--output-last-message`;
   - leitura do prompt por stdin;
   - sessões retomáveis por `exec resume`.

5. `--output-last-message` preserva apenas a mensagem final. Não é um log integral da execução. Para rastreabilidade operacional, é preciso também capturar JSONL, versão da CLI, modelo solicitado, commit, manifesto e mensagens de erro.

## Inferências

A estrutura preserva uma independência limitada, suficiente para uma auditoria adversarial de tarefa claramente delimitada, mas não a independência forte prometida pelo protocolo.

O problema principal não é o Claude transmitir sua conclusão explicitamente. É o viés de enquadramento: ele pode selecionar caminhos, formular a pergunta, omitir alternativas e definir critérios de aceite de maneira que estreite o espaço crítico do Codex. Um manifesto “sem conclusões” ainda pode ser altamente direcionador.

Além disso, a síntese feita exclusivamente pelo Claude cria risco de compressão assimétrica. Mesmo preservando o parecer bruto, Pedro pode acabar decidindo a partir da síntese mais acessível, e não da divergência original.

Portanto, A+C não implementa integralmente o protocolo atual. Implementa uma versão economicamente reduzida dele. Isso é defensável, mas deve ser declarado como alteração do protocolo, não como simples operacionalização fiel.

## Riscos

1. **Independência apenas nominal.** O revisor não vê a opinião do Claude, mas vê um problema já enquadrado pelo revisado.

2. **Seleção estratégica de evidência.** A lista de arquivos pode excluir justamente artefatos que enfraquecem a proposta.

3. **Autopoliciamento.** A skill criada e executada pelo Claude controla o comportamento do próprio Claude. É orientação útil, não salvaguarda independente.

4. **Síntese assimétrica.** Divergências podem ser suavizadas, reclassificadas como detalhes ou separadas de suas evidências.

5. **Rastreabilidade insuficiente.** Adiar completamente B contradiz a exigência do protocolo de registrar modelo, versão, parâmetros, prompt e commit em toda execução relevante.

6. **Regra estática excessiva no `AGENTS.md`.** Dizer que o Codex “não edita código de produção” inviabilizaria o rebalanceamento econômico. O papel deve ser definido por tarefa, não congelado globalmente.

7. **Confusão entre sandbox e gravação da saída.** Em `read-only`, o agente não deve escrever o parecer por comandos próprios. A gravação deve ser feita pelo processo invocador, por `--output-last-message` e captura do stdout. O template não deve instruir o modelo a criar o arquivo.

8. **Sessões e contexto residual.** `codex exec` pode persistir sessões por padrão. Não se deve usar `resume` em parecer independente. `--ephemeral` reduz esse risco, embora instruções do projeto e configurações carregadas continuem influenciando a execução.

9. **Cota não equivale a preço previsível.** A execução autenticada pela assinatura OpenAI usa os limites aplicáveis à conta. “Tokens mais subsidiados” é uma boa razão operacional, mas não garante custo marginal fixo nem disponibilidade contínua. O fluxo precisa tolerar limite de uso sem trocar silenciosamente de modelo.

## Alternativas

### Alternativa 1: A+C como proposto

É a opção mais barata, mas deve ser denominada “consulta de raia única”, não “parecer independente bilateral”. Serve para a maioria das tarefas ordinárias.

### Alternativa 2: A+C com automação mínima agora

Manter o script despachante completo adiado, mas criar desde já um comando canônico que fixe e registre:

- commit;
- hash ou cópia imutável do manifesto;
- modelo solicitado;
- versão da CLI;
- data e hora;
- `--sandbox read-only`;
- `--ephemeral`;
- stdout JSONL;
- stderr;
- mensagem final separada;
- código de saída.

Isso captura a parte essencial de B sem construir um sistema elaborado.

### Alternativa 3: dois níveis de independência

- **Nível ordinário:** um único modelo, dono da raia.
- **Nível crítico:** pareceres separados de Claude e Codex quando estiverem em jogo estimando, corpus, codebook, instrumento de mensuração ou conclusão histórica.

Esse nível crítico pode ser raro e explicitamente autorizado por Pedro. A economia deixa de ser uma proibição absoluta de duplicação e passa a ser um gate de risco.

## Recomendação

Adotar A+C, mas não exatamente como proposto.

As salvaguardas mínimas são:

1. Pedro aprova não apenas o gasto, mas também pergunta, escopo, arquivos e critérios de aceite do manifesto.

2. O manifesto contém uma seção obrigatória de “evidência potencialmente relevante não fornecida”, preenchida pelo Claude. Isso torna omissões deliberadas mais visíveis.

3. O parecer bruto é apresentado diretamente a Pedro antes da síntese do Claude, ou lado a lado com ela.

4. A síntese deve citar cada divergência por referência verificável ao parecer original. Claude pode interpretar, mas não substituir nem editar o texto do Codex.

5. O protocolo deve distinguir formalmente consulta de raia única de revisão independente. Decisões críticas continuam permitindo duas análises, mediante aprovação específica de Pedro.

6. Implementar já o núcleo de logging de B. Adiar validação sofisticada é razoável; adiar proveniência básica não é.

7. O `AGENTS.md` deve dizer que o Codex não edita produção **quando atua como auditor**. Em tarefas em que seja implementador designado, pode editar código dentro do escopo aprovado.

8. Para pareceres, usar execução nova e efêmera, modelo fixado e sandbox read-only. Não usar `resume`.

9. Capturar `--json` além de `--output-last-message`. O segundo não é log bruto completo.

Quanto ao rebalanceamento, ele faz sentido. Codex pode assumir:

- código de análise estatística;
- simulações e checagens mecânicas;
- scripts reprodutíveis de validação;
- rascunhos acadêmicos;
- auditorias de consistência documental.

A separação correta é por artefato e papel, não por marca do modelo. Se o Codex implementar uma análise estatística ou redigir uma seção, ele não deve ser apresentado como auditor independente daquele mesmo artefato. Claude pode revisar a implementação computacional, e Pedro mantém a aprovação substantiva. Uma nova sessão do mesmo Codex não restaura independência forte.

## Teste que poderia refutar esta recomendação

Realizar um piloto cego com 6 a 10 decisões já conhecidas:

1. Pedro prepara ou aprova um pacote de evidências comum.
2. Em metade dos casos, Claude redige o manifesto.
3. Na outra metade, Pedro redige o manifesto factual.
4. Codex responde sem conhecer a origem.
5. Comparam-se problemas identificados, alternativas consideradas, severidade dos riscos e omissões.
6. Pedro avalia também a fidelidade da síntese do Claude ao parecer bruto.

Se os manifestos redigidos pelo Claude não reduzirem sistematicamente a diversidade crítica, e as sínteses preservarem integralmente as divergências, a exigência de salvaguardas adicionais terá sido excessivamente conservadora. Até esse teste, tratar A+C como independência plena não é justificado.
