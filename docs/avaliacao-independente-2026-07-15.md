# Avaliação independente do projeto

**Data:** 15 de julho de 2026

**Natureza:** auditoria externa realizada pelo Codex, após desenvolvimento inicial conduzido com Claude

**Escopo:** desenho de pesquisa, evidência do piloto de 1906, pipeline computacional, reprodutibilidade e configuração especializada para Claude Code

## Síntese do julgamento

O projeto apresenta uma pergunta de pesquisa relevante e uma arquitetura metodológica mais cuidadosa do que a média dos projetos que empregam modelos de linguagem para classificação de fontes históricas. São pontos fortes a definição explícita do estimando, a escolha da edição-dia como unidade de análise, o reconhecimento da deriva conceitual entre 1906 e 1914, o registro de decisões, a proposta de validação humana por fase, a auditoria de recall, a ponte entre modelos e a intenção de corrigir erro de mensuração por meio de design-based supervised learning.

Apesar disso, o projeto ainda deve ser tratado como um protótipo de pesquisa. A documentação está consideravelmente mais avançada do que a implementação e algumas conclusões do piloto são apresentadas com grau de segurança superior ao permitido pelos arquivos preservados. O próximo passo recomendado não é ampliar imediatamente o corpus para 1907-1914, mas auditar e reparar o piloto de 1906, consolidar o codebook e construir uma suíte de avaliação reproduzível.

O principal risco associado ao desenvolvimento realizado apenas com Claude não é a autoria por IA em si. O risco é a coerência excessiva: planos bem redigidos, skills e agentes revisores produzidos pelo mesmo sistema podem reforçar premissas comuns e fazer problemas de mensuração ainda abertos parecerem resolvidos.

## Diagnóstico por dimensão

| Dimensão | Avaliação |
|---|---|
| Pergunta de pesquisa | Forte e potencialmente publicável |
| Arquitetura metodológica | Promissora, com problemas de identificação ainda abertos |
| Evidência empírica do piloto | Insuficientemente reproduzível |
| Implementação do pipeline | Protótipo inicial, concentrado na F1b |
| Customização para Claude | Boa configuração local de projeto, ainda não um plugin distribuível |
| Alinhamento entre dissertação e repositório | Materialmente defasado |

## Pontos genuinamente fortes

1. **Estimando explícito.** O projeto deixou de tratar poucos jornais como amostra da imprensa brasileira e passou a definir uma quantidade descritiva referente a um corpus intencional de jornais de Rio de Janeiro e São Paulo.
2. **Unidade de análise clara.** A edição-dia holística mantém continuidade com o piloto e reduz decisões ad hoc sobre o que constitui um artigo.
3. **Reconhecimento da deriva do construto.** A separação entre criação, operação, expansão e colapso da Caixa é necessária. A checagem de perenidade do eixo ortodoxo-expansionista em 1914 é especialmente importante.
4. **Prompts tratados como instrumentos de mensuração.** Versionamento, registro de mudanças e ponte entre modelos são práticas corretas.
5. **Preocupação com erro em todas as etapas.** Recuperação, transcrição, classificação e agregação são reconhecidas como fontes distintas de erro.
6. **Proveniência preservada.** Scripts e resultados do piloto foram mantidos como legado, em vez de serem silenciosamente substituídos.
7. **Guardrails operacionais.** Regressão de 1906, medição de custo, rate limit e retomada de lotes são boas decisões de engenharia de pesquisa.

## Problemas maiores

### 1. Atrito elevado entre hits recuperados e edições efetivamente pontuadas

Os cinco arquivos consolidados do piloto contêm 537 registros. Destes, 280, ou 52,1%, receberam `No Relevant Mentions Found`, e somente 259 possuem `stance_score`. A média agregada de aproximadamente -0,29 pode ser reproduzida apenas após excluir os casos sem pontuação.

Essa exclusão não é neutra. As edições entraram no corpus por uma busca exata por "caixa de conversão". Quando o classificador não encontra menção relevante numa edição recuperada por essa busca, as causas possíveis incluem omissão na transcrição, truncamento, erro de leitura, falha do classificador ou discrepância entre a página-hit e o PDF processado. Esses casos não devem ser tratados como ausência aleatória.

**Correção proposta:** auditar os 280 casos, registrar uma variável de motivo da falha, recuperar a página específica do hit, verificar a presença literal do termo e separar ausência substantiva de falha do pipeline. Nenhum resultado agregado deve ser considerado definitivo antes dessa auditoria.

### 2. Datas ausentes comprometem a análise temporal

Em 169 dos 537 registros, ou 31,5%, a data foi substituída por um fallback indicando que não foi encontrada. Isso enfraquece médias móveis, ordenação temporal e associação com eventos históricos.

**Correção proposta:** construir uma tabela canônica de edições com identificador, jornal, número da edição, data civil, pasta da Hemeroteca, páginas-hit e origem da data. A data não deve depender da capacidade do modelo de encontrá-la na transcrição.

### 3. Validação de 1906 não é reproduzível com o conteúdo preservado

Não foram localizados no repositório os códigos humanos, o sorteio da amostra, o script ou notebook que produziu κ de Cohen = 0,712, ρ de Spearman = 0,670 e o resultado de Bland-Altman. Também não há matriz de confusão nem métricas por classe.

**Correção proposta:** recuperar e versionar a planilha de códigos humanos, o identificador de cada edição, a regra de amostragem, a semente aleatória, o codebook utilizado e um script que reproduza todas as estatísticas a partir dos dados brutos.

### 4. O estimando e o denominador do corpus ainda são ambíguos

O projeto se refere à distribuição de posicionamentos por edição-dia, mas inclui apenas edições recuperadas por uma busca textual. Portanto, há duas quantidades distintas:

1. a distribuição de posições entre edições recuperadas e substantivamente relevantes;
2. a saliência do debate entre todos os dias em que o jornal circulou.

O corpus atual pode sustentar a primeira quantidade após a auditoria. A segunda exige inventário de todos os dias de publicação. A expressão "censo intencional" deve ser substituída por uma definição precisa do universo observado.

### 5. Busca exata introduz seleção substantiva

A busca por "caixa de conversão" pode perder textos que discutem câmbio, emissão, conversibilidade, lastro ou o Convênio de Taubaté sem empregar a expressão exata. Quinze edições negativas por jornal oferecem uma primeira auditoria, mas podem produzir intervalos muito amplos para taxas baixas de falso negativo.

**Correção proposta:** pré-especificar termos alternativos por fase, avaliar busca exata e busca ampliada num conjunto humano e reportar recall com intervalo de incerteza por jornal e fase.

### 6. Posicionamento editorial e conteúdo publicado estão parcialmente confundidos

O prompt instrui o modelo a distinguir reportagem de endosso, mas os resultados do piloto por vezes inferem posição a partir de cobertura positiva, destaque, fala de políticos ou atmosfera favorável. Uma edição pode publicar argumentos expansionistas sem que eles constituam a voz editorial do jornal.

**Correção proposta:** decompor a mensuração. Para cada item relevante, registrar gênero, autoria ou voz, posição, página, proeminência e evidência textual. Uma regra de agregação pré-registrada transforma os itens em posição da edição. A classificação holística pode permanecer como comparação, não como único instrumento.

### 7. Identidade do jornal pode contaminar a classificação

O nome do jornal é fornecido ao modelo. Como o prompt também descreve interesses econômicos e o modelo possui conhecimento histórico, pode reproduzir expectativas sobre O Paiz, Correio Paulistano ou Correio da Manhã.

**Correção proposta:** usar classificação mascarada como especificação principal e comparar com uma rodada não mascarada no conjunto de validação.

### 8. A escala possui seis categorias e cinco valores

As categorias são claramente ortodoxo, tendendo à ortodoxia, neutro/factual, misto/ambíguo, tendendo ao expansionismo e claramente expansionista. São seis categorias, embora neutro e misto recebam o mesmo valor zero. A documentação menciona incorretamente "cinco categorias" em alguns pontos.

**Correção proposta:** tratar o rótulo nominal de seis classes e o score ordinal de cinco pontos como variáveis relacionadas, porém distintas. Shares devem usar seis categorias. Operações ordinais devem declarar como os dois zeros são tratados.

### 9. Estatísticas de validação precisam ser ampliadas

κ nominal, Spearman e Bland-Altman não descrevem adequadamente todos os erros. Bland-Altman é difícil de interpretar numa escala discreta, limitada e com dois rótulos diferentes no zero. Além disso, um único codificador humano não constitui automaticamente um padrão-ouro.

**Correção proposta:** dupla codificação humana de um subconjunto, adjudicação, acordo exato, matriz de confusão, macro-F1, precisão e recall por classe, κ ponderado para o componente ordinal e análise específica da distinção neutro-misto.

### 10. DSL e bootstrap exigem desenho amostral mais explícito

O uso de DSL é promissor, mas a amostra humana precisa ser probabilística em relação à população-alvo e preservar jornal, fase e classes raras. Aproximadamente trinta edições por fase podem ser insuficientes para seis categorias. O bootstrap simples por edição também pode ignorar dependência temporal, campanhas editoriais e textos seriados.

**Correção proposta:** simular precisão esperada antes de fechar o tamanho da amostra, estratificar com probabilidades conhecidas e avaliar bootstrap em blocos temporais e por jornal.

### 11. Concordância entre modelos não é validade

Gemini e Claude podem concordar porque recebem o mesmo prompt, compartilham conhecimento histórico ou reproduzem o mesmo estereótipo. A afirmação de que o ruído do wrapper do Claude apenas reduz κ não é garantida.

**Correção proposta:** tratar Claude como análise de sensibilidade subordinada à validação humana. Registrar modelo, versão da CLI, effort, system prompt, ferramentas, data, hashes e resposta bruta. Divergências devem ser auditadas, mas não usadas para escolher retrospectivamente o rótulo mais conveniente.

### 12. O capítulo submetido está defasado em relação ao desenho atual

O relatório de qualificação descreve cinco jornais, incluindo O Estado de S. Paulo, enquanto o pipeline atual trabalha com quatro jornais da Hemeroteca e adia o Estadão. O texto alterna entre artigos e edições como unidade de análise e chama de robustos resultados que ainda possuem atrito elevado e validação não reproduzível.

**Correção proposta:** atualizar o capítulo somente após a auditoria de 1906. Até lá, marcar os números como resultados preliminares do pipeline original e explicitar suas limitações.

## Avaliação do código e da arquitetura

O módulo de download F1b apresenta uma base razoável. A construção da URL, deduplicação, validação da assinatura PDF, rate limit, backoff e resume são decisões adequadas. Entretanto, F1a ainda está em scripts exploratórios e F2-F6 permanecem por implementar. Não há suíte automatizada de testes, integração contínua, schemas formais nem scripts reproduzíveis para figuras e validação.

O script legado de transcrição imprime a chave de API no terminal. Essa linha deve ser removida mesmo que o arquivo seja classificado como legado, pois uma execução acidental expõe o segredo.

O estado correto do projeto é, portanto, protótipo pré-alfa com documentação metodológica avançada, não pipeline concluído.

## Avaliação da customização para Claude

As três skills locais e o agente revisor são úteis. As descrições de gatilho são claras, os guardrails são pertinentes e o revisor metodológico possui uma boa ordem de prioridades. Contudo, a estrutura `.claude/` é uma configuração específica do projeto, não um plugin distribuível de Claude Code.

Um plugin real deve ser criado em diretório próprio, com manifesto `.claude-plugin/plugin.json`, skills e agentes na raiz do plugin, versionamento e testes de acionamento. Também é recomendável separar:

1. conhecimento geral reutilizável sobre text-as-data e imprensa histórica;
2. fatos específicos da Caixa de Conversão, que permanecem no repositório e no codebook;
3. estado operacional mutável do pipeline, que não deve ficar duplicado em vários prompts.

O agente revisor deve ser tornado mais adversarial. Em vez de assumir DSL, o eixo ortodoxo-expansionista e a edição holística como soluções, deve perguntar se cada escolha é necessária e procurar desenhos alternativos que possam falsificar as conclusões.

## Prioridades recomendadas

### Prioridade 0, antes de novo lote pago

1. Recuperar códigos humanos e scripts de validação de 1906.
2. Auditar os 280 casos sem menção relevante e os 169 casos sem data.
3. Definir denominadores distintos para posição e saliência.
4. Concluir a nota de perenidade do eixo e os blocos das fases 2-4.
5. Construir conjunto dourado com dupla codificação e adjudicação.
6. Revisar prompt, schema e regra de agregação.
7. Criar testes, manifestos de proveniência e validação automática de evidências.

### Prioridade 1, ponte e regressão

1. Rodar Gemini novo contra o piloto antigo e contra humanos.
2. Rodar Claude sob configuração controlada e mascarada.
3. Comparar erros por jornal, fase, gênero e classe.
4. Estimar custo real antes de qualquer expansão.

### Prioridade 2, expansão e produto

1. Executar 1907-1914 somente após os gates anteriores.
2. Implementar consolidação, DSL, incerteza e triangulação.
3. Atualizar a dissertação a partir da base auditada.
4. Empacotar as capacidades reutilizáveis como plugin real.

## Conclusão

Recomenda-se continuar o projeto. A pergunta histórica é forte e as decisões registradas revelam boa maturidade metodológica. A contribuição potencial não está apenas nos resultados sobre a Caixa de Conversão, mas também na construção transparente de um instrumento de mensuração para imprensa histórica.

O avanço, contudo, deve ocorrer por validação e reparo, não por simples aumento de escala. A independência entre humano, Claude e Codex deve ser preservada deliberadamente. O objetivo não é obter consenso entre modelos, mas descobrir onde o instrumento falha antes que esses erros sejam convertidos em interpretação histórica.
