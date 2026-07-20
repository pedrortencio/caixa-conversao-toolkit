# Desenhos concorrentes de mensuração (artefato 3 da rodada)

**Data:** 2026-07-19
**Status:** especificação operacional dos desenhos que competirão no benchmark (artefato 6). Cumpre o item 3 do protocolo de `docs/contexto-debate-metodologico-mensuracao.md`: pelo menos duas alternativas substantivas além da escala herdada. NÃO escolhe o instrumento, reservado a Pedro após o benchmark. Incorpora a hipótese primária ratificada (2026-07-19) e a decisão D3 (posição versus saliência).

Atualização (2026-07-19): a detecção de stance por LLM passa a possibilidade contingente, não pressuposto. O desenho sem LLM para stance (D-Humano) entra como competidor de primeira classe. O que está em questão é apenas a LLM para stance; o toolkit e o uso de LLM em tarefas que não são stance (recuperação, transcrição de páginas ilegíveis, extração de atores) seguem em uso.

## Contrato comum de avaliação

Para serem comparáveis, todos os desenhos rodam sobre a mesma amostra estratificada (artefato 4) e o mesmo padrão-ouro (artefato 5), e emitem:

- por edição-dia: posição na escala ortodoxo (-2) a expansionista (+2), ou mapeável a ela, com a classe (Clearly ou Leaning Orthodox, Neutral-Factual, Leaning ou Clearly Expansionist, Mixed/Ambiguous, No Relevant);
- saliência decomposta (D3): `dias_relevantes / dias_triados`, `n_pecas_relevantes` por edição relevante, proeminência (máxima ou média);
- rastreabilidade: cada rótulo aponta para evidência textual (citação mais localizador);
- voz (D4): quando o desenho permitir, marca editorial próprio versus discurso reproduzido;
- proveniência: modelo, versão, prompt e custo registrados.

## D-Escala (incumbente, do piloto)

- **Codificação:** holística, a edição-dia inteira produz um rótulo na escala, mais justificativa e evidências de apoio (é o formato dos `classificacao_holistica` do piloto).
- **Posição:** o próprio rótulo holístico.
- **Saliência:** presença diária (edição relevante ou não); intensidade e proeminência ficam fracas, porque não decompõe por peça.
- **Voz:** implícita, não separa discurso reproduzido de editorial. O caso O Paiz 07834 (teste D1) mostrou o risco de atribuir ao jornal a posição de uma carta publicada.
- **Insumo textual:** transcrição LLM do piloto, ou OCR-BN (a testar em D5).
- **Custo:** uma chamada por edição. Barato.
- **Forte em:** comparabilidade temporal, custo, simplicidade. **Fraco em:** rastreabilidade fina, distinção de voz, intensidade da saliência, e não permite testar a perenidade de dentro (D2).

## D-Extração (desafiante primário, hipótese ratificada)

- **Codificação:** por peça relevante, produz um conjunto de afirmações substantivas com os campos ator_voz, alvo, objeto_politica, direcao, justificativa, evidencia_textual, fase (esquema da seção 1 de `docs/testes-desenho-mensuracao.md`).
- **Posição da edição-dia:** derivada das afirmações de voz editorial, pela regra de agregação de 2026-07-18 (soma de itens, editorial por OR, proeminência por máximo, posições opostas sem dominância viram Mixed/Ambiguous).
- **Saliência:** naturalmente decomposta (D3): presença, `n_pecas_relevantes`, proeminência por peça.
- **Voz:** explícita por afirmação. Resolve D4 no nível do dado, marcando quando a posição vem de terceiro reproduzido.
- **Insumo textual:** OCR-BN grátis para triagem e extração (a validar em D5), com transcrição LLM nas páginas candidatas onde o OCR degrada.
- **Custo:** mais chamadas e tokens por edição (peça a peça), mitigável por batch mode e pelo OCR grátis.
- **Forte em:** rastreabilidade, distinção de voz, intensidade, perenidade testável (atributos por afirmação), e reagregação posterior em qualquer vista. **Fraco em:** custo e complexidade de segmentação e vinculação. Viabilidade em papel já demonstrada no teste D1.

## D-Atributos (alternativa intermediária)

- **Codificação:** por edição-dia, mas multidimensional: um vetor de posições por objeto de política (taxa de conversão, conversibilidade, emissão, lastro, valorização do café), sem a camada completa de afirmações.
- **Posição:** agregada dos atributos por uma regra a definir; a escala é derivável.
- **Saliência:** presença mais intensidade grosseira (quantos atributos acionados), sem granularidade por peça.
- **Voz:** parcial (pode marcar presença de editorial, não atribui por afirmação).
- **Custo:** intermediário.
- **Papel no benchmark:** isola quanto do ganho vem da multidimensionalidade e quanto vem da granularidade por afirmação. Se D-Atributos empata com D-Extração, a camada de afirmações pode não valer o custo; se D-Extração vence com folga, a granularidade por peça se justifica.

## D-Humano (codificação humana, sem LLM para stance) — competidor de primeira classe

- **Codificação:** a posição (ortodoxo ou expansionista, apoio ou oposição) é atribuída por leitura humana, sobre uma amostra estratificada forte, ou sobre o subcorpus relevante inteiro se couber nas horas de Pedro. A LLM não atribui direção de stance aqui; pode auxiliar em tarefas que não são stance (triagem sobre OCR, marcação de gênero e seção, extração de atores), sempre auditável.
- **Posição:** humana, padrão-ouro. Para as edições não codificadas, a posição é inferência baseada em amostra, com intervalo de confiança, não censo. É um produto legítimo e em geral mais honesto que um censo automático com erro de modelo não medido.
- **Saliência:** censo completo pela camada de OCR (presença, intensidade, proeminência), sem LLM, igual aos demais desenhos.
- **Voz (D4):** humana, direta, no nível da peça e da afirmação.
- **Insumo textual:** OCR-BN grátis para saliência e triagem; leitura das páginas para a posição; transcrição LLM só onde o OCR impedir a leitura humana.
- **Custo:** horas de Pedro (15 a 20h por semana), tokens quase zero para stance. A dupla codificação num subconjunto dá o kappa.
- **Forte em:** validade (padrão-ouro), transparência, reprodutibilidade, ausência de risco de modelo, e alinhamento direto com o objetivo central de processamento e exposição robustos. **Fraco em:** cobertura, a posição fica no nível de amostra e não de censo, limitada pelas horas.

## Dicionário e léxico (triangulação, não competidor primário)

Dicionário ortodoxo ou expansionista aplicado ao OCR-BN, de graça. Dentro de D-Humano funciona como triangulação de validade e cobertura; isolado, como baseline de transparência. Não é instrumento principal de posição (o contexto adverte que dicionário confunde presença de vocabulário, discurso reportado e posição do jornal). Roda sem orçamento sobre a camada de texto embutido.

## Como o benchmark decide (aponta para o artefato 6)

- **Pergunta central:** a posição atribuída por LLM (D-Escala, D-Extração) supera a codificação humana em amostra (D-Humano) o suficiente para justificar seu custo e seu erro de modelo não medido, dado o tamanho do subcorpus relevante? O ônus da prova é da LLM.
- Mesma amostra estratificada e mesmo padrão-ouro para todos.
- Critérios pré-definidos do contexto (seção Critérios), com peso especial em validade de construto, confiabilidade entre codificadores, distinção de voz (D4), perenidade das categorias (D2), rastreabilidade e custo.
- Regra do contexto: não premiar só a concordância numérica; um desenho pode concordar e ainda representar mal o fenômeno. Casos de desacordo informam as fronteiras do construto.
- A decisão registrada (artefato 7) escolhe o instrumento principal, as triangulações, as sensibilidades e as condições de reprocessamento.

## Dependências e próximos passos

- **Medida pivô, barata e primeira:** o tamanho do subcorpus relevante, pela triagem sobre o OCR (sem stance, custo zero). Se couber nas horas de Pedro, D-Humano cobre a posição no subcorpus inteiro e a LLM para stance vira opcional; se não couber, a LLM ou um classificador supervisionado reganha lugar para cobertura, validado contra D-Humano.
- Precede este benchmark: a amostra estratificada (artefato 4) e o protocolo humano (artefato 5), para haver padrão-ouro.
- O teste D5 (OCR-BN versus transcrição LLM) informa o insumo textual de todos os desenhos e o custo, e é barato (protocolo em `docs/testes-desenho-mensuracao.md`).
- O teste D1 já mostrou a viabilidade de D-Extração em papel; falta a confiabilidade entre codificadores, que vem do artefato 5.
