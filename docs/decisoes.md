# Registro de decisões metodológicas

Formato: data, decisão, alternativas consideradas, justificativa. Toda mudança em prompts, codebook, modelos ou desenho amostral entra aqui. Este registro alimenta a seção de método do artigo.

---

## 2026-07-13 — Desenho da expansão 1906-1914 (sessão de planejamento com Claude)

1. **Estimando:** distribuição de posições editoriais por edição-dia entre os principais diários de RJ/SP (censo intencional). Alternativa rejeitada: tratar os 5 jornais como amostra da "imprensa brasileira" (generalização insustentável).
2. **Unidade de análise: edição-dia holística.** Alternativas: por artigo (piloto inicial, abandonado; quebraria a comparabilidade com a validação humana κ=0.712) e híbrida (adiada).
3. **Codebook por fase** (1906 criação / 1907-09 operação / 1910-13 taxa 16d / 1914 colapso), com validação humana de ~30 edições por fase nova. Motivo: deriva conceitual, o prompt do piloto está ancorado no debate de criação; "expansionista" em 1906 ≠ 1914.
4. **Corpus por busca exata "caixa de conversão" no DocReader + auditoria de recall** (~15 edições sem hit por jornal, verificadas via Gemini Flash; falso negativo reportado). Alternativas: varredura completa (custo proibitivo) e dump de OCR da BN + busca fuzzy (viabilidade não confirmada).
5. **Escopo de download: página do hit ± 1** (artigos continuam entre páginas; edição inteira multiplicaria custo ~6-10x).
6. **Modelos:** gemini-2.5-flash (transcrição; escala a -pro em falha) e gemini-2.5-pro (classificação). Motivo da troca: gemini-1.5-pro do piloto foi aposentado pelo Google. Mitigação: ponte estatística 1906 (novo × antigo × humano).
7. **Scraping: Selenium adaptando pyHDB** (Eric Brasil, citável). Alternativa rejeitada: requests contra endpoints internos (DocReader é WebForms/Telerik com VIEWSTATE, verificado em 13/07/2026; frágil e sem ganho real com rate limit educado).
8. **Output da classificação ampliado:** n_itens_relevantes, houve_editorial, proeminencia; Neutral/Factual e Mixed/Ambiguous permanecem categorias distintas.
9. **Camada estatística auditável:** DSL (Egami et al. 2023) com amostra humana (~130 edições) + bootstrap por edição + triangulação por dicionário do Cap. 2. Motivo: inferência auditável sobre rótulos de LLM; métodos alternativos ao LLM (dicionário puro, Wordfish, supervisionado clássico) rejeitados como via principal por validade inferior em stance detection com discurso reportado.
10. **Estadão adiado** (não está na Hemeroteca; acervo próprio, fluxo separado no futuro).
11. **Extensões pós-parecer (não incluídas):** teste de mascaramento do nome do jornal, anotador de modelo aberto.

---

## 2026-07-14 — Rota de download reprovada: Cloudflare barra a exportação de PDF (sessão de diagnóstico F1)

Diagnóstico ao vivo da rota de download (scripts `pipeline/scraper/explora_fullres.py`, `explora_pdfpane.py`, `explora_export2.py`, `explora_export3.py`). Achados, do mais ao menos importante:

1. **A única rota com resolução legível é a exportação oficial de PDF do DocReader**, e ela está atrás do **Cloudflare**. A janela "Download PDF" é aberta por `PDFExportAbre()` → iframe `PDFExport.aspx?id={HiddenID}&pagfis={páginas}&bib={pasta}` → botão **Create** → PDF servido por `SaveAsFile.ashx`. Ao clicar Create com Chrome automatizado (Selenium), a BN retorna **"Attention Required! | Cloudflare — you have been blocked"**. É bloqueio duro (WAF/bot-management), não CAPTCHA: acontece ANTES de qualquer desafio, então API de resolução de CAPTCHA não resolve.
2. **Stealth leve não basta.** Testado `--disable-blink-features=AutomationControlled` + `excludeSwitches=['enable-automation']` + CDP `navigator.webdriver=undefined`: derruba a flag JS (`navigator.webdriver=None`, faixa de automação some) mas o Cloudflare barra assim mesmo (fingerprint TLS/JA3/HTTP2 + reputação de IP + rajada no endpoint pesado de geração de PDF). Três tentativas, bloqueio progressivamente mais duro → sinal de arquitetura errada (não insistir com tentativa nº 4 de força bruta).
3. **A enumeração NÃO é bloqueada.** Busca por deep-link + "Match thumbs" (jornal/ano/edição/página) roda limpa sob automação. O gargalo é só o DOWNLOAD legível, não o inventário de hits.
4. **O piloto baixou os PDFs À MÃO.** `legado/rnc1.0.py` só faz `input_path.glob("*.pdf")` de arquivos locais; não há código de download no piloto. Os PDFs de 1906 foram exportados manualmente no navegador real do Pedro e cortados com PDFsam (nomes `1_PDFsam_...`). Por isso o piloto nunca esbarrou no Cloudflare.
5. **Alvo de legibilidade medido:** PDFs do piloto embutem imagem a **~2016×2985 a 2612×3364 px** (JPEG), resolução em que a validação (κ=0.712) foi feita. A rota de imagem do viewer (`#DocumentoImg` via fetch same-origin) entrega só **517×771 px** (~20× menos pixels): inservível para transcrição sem resolver zoom/tiles. Logo a rota de imagem é beco sem saída p/ legibilidade; a de PDF é a boa, e é a bloqueada.
6. **A janela de exportação oferece "All current folder matchs"** (um PDF com TODAS as páginas de hit da pasta/década de uma vez). Se funcionar para humano, o download inteiro de 1907-14 vira algumas DEZENAS de exportações, não milhares, o que torna o caminho semi-manual (ou automação levíssima) viável e seguro. A confirmar num navegador real.
7. **Decisão de arquitetura em aberto** (fork a decidir com Pedro): (A) automação com fingerprint real (Chrome do usuário via remote-debugging / undetected-chromedriver headed); (B) semi-manual (scraper enumera + gera deep-links; Pedro exporta os PDFs à mão, como em 1906, usando "All matchs" para minimizar cliques); (C) automação levíssima só das exportações "All matchs". Enquanto isso: NÃO martelar o endpoint (risco de ban de IP num acervo essencial); pausar automação contra a BN.

### RESOLVIDO no mesmo dia — host de PDF estático dispensa toda a rota de exportação

**O download NÃO passa pelo DocReader.** Pedro achou o portal `bndigital.bn.gov.br/acervo-digital/paiz/{bib}` (grade de edições por ano), e clicar numa edição serve o PDF de um **terceiro host, estático**: `hemeroteca-pdf.bn.gov.br`. URL construível:

```
https://hemeroteca-pdf.bn.gov.br/{bib}/per{bib}_{ano}_{edição:05d}.pdf
```

Verificado em 14/07/2026:
1. **Sem Cloudflare.** `curl` simples da máquina do Pedro (sem navegador, sem cookie, sem UA especial necessário) e WebFetch de IP externo devolvem ambos **HTTP 200, application/pdf**. O bloqueio era exclusivo do app DocReader/`memoria.bn.gov.br`; o host estático é aberto.
2. **Resolução validada.** `per178691_1906_07890.pdf` do host estático é **byte-idêntico** ao arquivo que Pedro baixou à mão para o piloto (8 pág, 7914 KB, imagem 2016×2985 px). Mesma legibilidade da validação κ=0.712.
3. **Numeração casa direto.** O `{edição:05d}` do nome é o mesmo número que a busca do DocReader retorna no thumb ("Ano 1906\Edição 07890"). Numeração global contínua desde 1884 (1884→00001, 1906→~07890).

**Nova arquitetura F1 (substitui a exportação PDF e o "página ±1"):**
- **F1a Enumeração** (Selenium, já validado, NÃO barra no Cloudflare): busca "caixa de conversão" por bib+pasta → lista de edições-hit com `(ano, edição)` lidos do Match thumbs.
- **F1b Download** (HTTP puro, sem Selenium): para cada hit, `GET https://hemeroteca-pdf.bn.gov.br/{bib}/per{bib}_{ano}_{edição:05d}.pdf`. Rate-limit educado, retry/backoff, resume, 404→log de auditoria. Baixa a **edição inteira** (não página ±1).

**Consequências:** decisão #5 (página do hit ±1) fica OBSOLETA — baixamos a edição-dia inteira, que é a unidade de análise (decisão #2) e é o que o piloto já usava. A saga Cloudflare/`explora_export*.py` vira só registro histórico de por que NÃO usar o DocReader para download; a rota de imagem 517px também é abandonada. Selenium fica restrito à enumeração (F1a).

---

## 2026-07-14 — Batch Mode e segundo anotador (sessão de design com Claude)

Design completo em `docs/plano-batch-anotadores.md`. Decisões:

1. **Transcrição (F3) e classificação (F4) migram para o Batch Mode da API Gemini**: 50% de desconto por token, mesmos modelos pinados e prompts versionados, latência de até 24h (compatível com os lotes noturnos já planejados). Orçamento estimado cai de ~R$830 para ~R$415. Alternativas rejeitadas: chamadas síncronas como via principal (2× o custo sem ganho; mantidas atrás da flag `--sync` para depuração) e rodar classificação via Gemini CLI sob a assinatura AI Pro (CLI é agente, não chamada pinável: comprometeria o instrumento de medição; além disso o tier gratuito perdeu os modelos Pro em 03/2026).
2. **Segundo anotador: Claude via `claude -p`** (headless, sem ferramentas, modelo pinado e registrado no output), rodando na assinatura existente do Pedro a custo marginal zero, como backend `claude_cli` numa camada `pipeline/anotadores/` de interface única. Papel SUBORDINADO: robustez (κ inter-anotadores por fase, matriz de confusão, lista de divergências para auditoria adicional); o instrumento primário segue sendo a API Gemini, e a amostra de validação humana segue aleatória. Isto retoma parcialmente a extensão "anotador de modelo aberto" adiada em 13/07 (item 11), viabilizada pelo custo zero. Justificativa metodológica para aceitar um wrapper de agente aqui: ruído de wrapper só DERRUBA o κ, nunca o infla, então concordância alta apesar do wrapper é evidência conservadora.
3. **Rejeitados:** integrador genérico de CLIs (Claude+Gemini+Codex) como camada de medição; modelos OpenAI/GPT como anotadores, nesta rodada e como opção futura (revisão do Pedro em 14/07: "o gpt acho que não"). Se houver demanda futura de terceiro anotador, a preferência é MODELO ABERTO (DeepSeek/Qwen) via backend `openrouter_api` pré-pago, pela mesma interface; a chave OpenRouter de quebra habilitaria o mantis-research para pesquisa do Cap. 2.

---

## 2026-07-17 — Fechamento das três decisões reservadas do design da base v2 (Claude + Pedro)

O design da base do corpus (spec v2, `docs/superpowers/specs/2026-07-16-esquema-base-corpus-design-v2.md`, seção 12) reservava três decisões a Pedro antes de autorizar transcrição substantiva. As três foram fechadas nesta sessão, com análise independente do Claude e decisão de Pedro. As três não são independentes: a escolha do censo textual comanda o peso do gate de recall. A Fase A (censo e download dos PDFs inteiros) não dependia delas e seguia em execução; a Fase B depende.

1. **Censo textual: subcorpus recuperado.** Triagem barata em todas as páginas de todas as edições disponíveis, com transcrição de qualidade apenas nas páginas candidatas. Alternativa rejeitada: transcrição integral de todas as páginas (censo textual completo). Justificativa: o volume integral é de 8 a 12 vezes o de uma página por edição, inviável no teto de orçamento de ~R$415, e desalinhado ao estimando, que mede posição editorial sobre a Caixa de Conversão e aparece só nas edições que a discutem. A triagem cobre toda página, não a lista de hits da busca da BN, o que corrige a origem dos 280 casos sem menção do piloto. A camada bruta (PDFs e mastheads) permanece completa e reprocessável. O produto textual passa a se chamar subcorpus recuperado segundo protocolo versionado, e a incerteza de recuperação acompanha os resultados. Substitui e detalha a decisão de 2026-07-13 (item 4, corpus por busca exata com auditoria de ~15 edições por jornal, agora insuficiente).
2. **Gate de recall: limite inferior unilateral de 95% maior ou igual a 0,90, por jornal e fase.** Alternativa rejeitada: limite de 0,95. Justificativa: com zero perdas, 0,90 exige cerca de 29 unidades relevantes na referência por jornal e fase; 0,95 exige cerca de 59. A referência é lida integralmente, então subir para 0,95 dobra a carga de leitura, em token ou em tempo de leitura humana. O gate por jornal e fase já protege a comparação entre jornais, que é o eixo da pergunta. A proteção adicional de 0,95 não é proporcional ao custo no orçamento do projeto. Registra-se em `recall_audits` com `confidence_level` = 0,95 e `minimum_recall_lcb` = 0,90.
3. **Unidade de análise: edição-dia estrita como unidade principal, manifestações modeladas na camada bruta.** Alternativa rejeitada: cada manifestação editorial (matutina, vespertina, extraordinária, suplemento) como unidade. Justificativa: a edição-dia estrita casa com o estimando e com o piloto, onde 67 PDFs corresponderam a 67 edições-dia e 67 dias civis distintos, sinal de que multi-manifestação é rara nos jornais escolhidos. Tratar cada manifestação como unidade mudaria o estimando, dando mais peso a jornais com mais edições. O schema já preserva a granularidade fina em `population_definitions.unit_mode`, então a decisão é revisável. Falta uma regra de agregação pré-registrada para os poucos dias com mais de uma edição, a ser informada pelas cardinalidades reais do censo. Confirma e precisa a decisão de 2026-07-13 (item 2, edição-dia holística), agora com a distinção explícita entre unidade de análise e granularidade documental.

Consequência: o critério de conclusão do design (spec v2, seção 12) está satisfeito. A Fase B fica desbloqueada no que depende de Pedro. Seguem pendentes, independentes destas três, o término do censo (Fase A), o benchmark de economia da identificação (seção 7), o gate de validação de data (seção 8) e a resolução dos 280 casos sem menção e 169 sem data do P0 de 1906.

---

## 2026-07-18 — Pré-registros do censo por união de fontes, antes da Fase B (pareceres duplos Claude + Codex; ratificação de Pedro)

Base: parecer do Claude congelado antes do despacho e parecer do Codex (recomendações 5 a 9 e teste de refutação), ambos de 18/07/2026, em `colaboracao/pareceres/`. Contexto factual: a varredura da Fase A encerrou com 8.889 edições; o índice oficial bndigital enumera 11.981 no recorte 1906-1914; duas extrações independentes do índice produziram conjuntos idênticos (manifestos e snapshots com hash em `dados/censo/`); a rodada de recuperação dos 3.092 alvos do diff está em execução com registro positivo por item. As quatro regras abaixo ficam pré-registradas antes de qualquer resultado substantivo da Fase B.

1. **Agregação de manifestações no mesmo jornal-dia.** Cópias exatas ou reescaneamentos da mesma manifestação são deduplicados por SHA-256, preservando todos os localizadores. Manifestações reais distintas (matutina, vespertina, A/B, suplemento) permanecem na camada documental e produzem uma única unidade analítica, a edição-dia estrita da decisão de 17/07. A classificação considera conjuntamente o conteúdo relevante das manifestações do dia. Uma manifestação substantiva mais outra neutra produz a posição substantiva; posições substantivas opostas produzem Mixed/Ambiguous. `n_itens_relevantes` soma sem duplicatas, `houve_editorial` usa OR, `proeminencia` usa o máximo, para que duas manifestações não dobrem o peso do dia.

2. **Cascata do censo e taxas publicadas por jornal-mês.** Seis quantidades separadas: K (dias civis no jornal-mês), E (localizadores enumerados pela união das fontes), D (edições-dia canônicas, válidas e baixadas), S (edições-dia completamente triadas), R (dias relevantes) e C (dias classificados). Taxas publicadas: cobertura documental D/K com datas de masthead distintas; rendimento de aquisição (arquivos válidos sobre localizadores enumerados); saliência R/S; distribuição de posições sobre C, com não classificados reportados à parte. Lacuna documental nunca vira "sem menção", neutro ou zero; um 404 não entra em S. K fica fixo em dias civis; taxa ajustada por dias de circulação só entra como série secundária e apenas com evidência positiva de não circulação. A identidade precede o denominador: o ano e o dia analíticos vêm do masthead, nunca do rótulo do nome de arquivo; SHA-256 detecta byte-idênticos; as sobreposições de rótulo do Correio da Manhã (3000-3089, 4000-4070) e os números isolados anômalos serão inspecionados a 100% antes de qualquer contagem de edição-dia. Gazeta 1913 entra na cascata como ausência total de acervo digital, sem imputação. O corpus passa a ser descrito como censo do acervo digital identificável e recuperável segundo fotografia datada das fontes da BN (18/07/2026), não como censo das edições publicadas.

3. **Novo portão de 1906.** Critério: todo item do gabarito do piloto deve ser atribuído a exatamente uma destas classes: unidade canônica reproduzida; manifestação coalescida em uma edição-dia canônica; ou exceção terminal documentada com fonte. Nenhum item pode ficar inexplicado, e a lista de exceções exige aprovação expressa de Pedro. A ponte entre modelos usa a interseção de unidades com insumo documental disponível, congelada antes de observar os resultados novos; as perdas aparecem como atrito, nunca como exclusão silenciosa. Substitui o critério anterior (gabarito como subconjunto simples do censo), que reprovava sem estado formal para os 4 faltantes confirmados fora das duas rotas verificadas.

4. **Flag cega de origem e margem de refutação.** Cada edição carrega a origem `varredura`, `somente_indice` ou `recuperacao_manual`, mantida cega para a triagem e a classificação. Teste pré-registrado: após a triagem, comparar entre origens, dentro de jornal e mês, a taxa de dias relevantes, a distribuição de posições e a proeminência com presença de editorial; a margem aceitável é diferença absoluta máxima de 5 pontos percentuais. Se os itens `somente_indice` ultrapassarem a margem sistematicamente, a análise por casos disponíveis não é defensável como estimativa do período completo e o resultado será reformulado como descrição do acervo observado. Robustez adicional pré-registrada: repetir a conclusão principal no subconjunto de meses com cobertura de pelo menos 90% nos quatro jornais e sob limites extremos que atribuem aos dias ausentes posições capazes de favorecer alternadamente cada jornal.

Regra operacional consolidada na mesma data, já implementada em `pipeline/base/recupera_indice.py`: 403, 429, 5xx e falha de rede são transitórios e nunca viram ausência; um 404 só é terminal com duas observações separadas. A regra provou valor no primeiro item da rodada: O Paiz 1907_5254, com uma observação de 404 na varredura, foi recuperado com 8 páginas na segunda sondagem.

---

## 2026-07-18 — Camada de texto embutido (OCR da BN) e retomada pós-debate de mensuração (Claude; escopo aprovado por Pedro)

Contexto: o PR #1 (docs/contexto-debate-metodologico-mensuracao.md) foi incorporado à main nesta sessão e reabriu o desenho de mensuração antes da Fase B substantiva. Na mesma sessão descobriu-se que os PDFs do host estático da BN trazem camada de texto embutida (OCR da própria Hemeroteca), verificada em amostra de 6 objetos de 3 jornais (28 a 44 mil caracteres por página).

1. **Camada de texto embutido materializada para todo o censo, custo zero de token.** Extração determinística (pypdf pinado em protocolo `text_extraction/texto-embutido-pypdf 1.0.0`), sem normalização, seleção ou correção; página sem camada é registro positivo `empty`; falha é `error` com classe. Migração 003 (aditiva: `text_extraction_runs`, `page_text_extractions`, `current_page_text_extractions`, view `v_current_page_texts`; `protocols` ganha o estágio `text_extraction`). Texto em `C:\dados-caixa\texto_embutido\` (fora do git/OneDrive, como os PDFs); manifestos por célula em `dados/texto_embutido/` no git. Contrato completo: `docs/superpowers/specs/2026-07-18-camada-texto-embutido-design.md`. Estatuto: atividade da classe "pode avançar" do contexto de mensuração (reversível, preservação, proveniência byte a byte); NÃO é o instrumento de mensuração nem transcrição do projeto.
2. **Consequência metodológica pré-registrada:** a comparação "OCR da BN vs transcrição LLM" deixa de ser pressuposto e vira hipótese testável da rodada metodológica; pilotos de dicionário, tópicos e ensaios de triagem lexical ficam viáveis sem orçamento. O custo projetado da Fase B (~R$415) passa a ter teto revisável para baixo.
3. **Consumidores e contrato:** mudanças de colunas, statuses ou semântica da camada após o primeiro consumo são breaking e exigem migração + registro aqui.

Pendentes de Pedro (propostos pelo Claude na sessão, ainda não ratificados): time-box de 2 a 3 semanas para a rodada metodológica com critério de parada; reposicionamento do P0 de 1906 (diagnóstico vira insumo da rodada; reparo de codebook absorvido pelo protocolo humano do desenho vencedor); preenchimento do `docs/memorando-quantidades-historicas.md` (artefato 1, destrava os demais).

---

## 2026-07-19 — Memorando de quantidades históricas: núcleo analítico, ambição controlada e gate de voz editorial (parecer Codex; ratificação de Pedro)

Base: `docs/memorando-quantidades-historicas.md`, artefato 1 da rodada metodológica prevista em `docs/contexto-debate-metodologico-mensuracao.md`. Pedro ratificou o parecer de que o memorando é substantivamente promissor, mas precisa reduzir a obrigação métrica para evitar que a dissertação tente mensurar, com o mesmo nível de sistematicidade, saliência, posição institucional, desenhos específicos de política, justificativas econômicas, atores vocalizados, voz editorial, discurso reproduzido, viradas temporais e interesses regionais/grupais.

1. **Pergunta empírica consolidada.** O núcleo passa a ser: explicar como os principais jornais trataram a Caixa de Conversão entre 1906 e 1914, identificando variações de saliência, posicionamento e enquadramento econômico-político entre jornais e fases, com atenção à diferença entre posição editorial própria e vozes/interesses reproduzidos. A formulação evita restringir o capítulo à escala herdada "ortodoxo vs expansionista", mas preserva essa escala como hipótese de mensuração a ser testada.

2. **Hierarquia das dimensões substantivas.** O núcleo essencial da mensuração será: saliência por jornal/fase; posição sobre a Caixa como instituição ou sobre seus principais instrumentos; variação temporal entre jornais e momentos críticos; justificativas econômicas principais; e, quando identificável, distinção entre posição editorial própria e conteúdo publicado/reproduzido. Atores, vozes, interesses regionais/setoriais e composições detalhadas de grupos entram como camadas interpretativas, controles de validade ou análises secundárias, não como promessa de mapeamento exaustivo em escala.

3. **Ortodoxia/expansionismo como hipótese, não premissa.** A perenidade das categorias "ortodoxia" e "expansionismo" ao longo de 1906-1914 não será presumida. A rodada metodológica deve verificar se essas categorias organizam o debate de modo estável entre fases, jornais, gêneros textuais e objetos de política, ou se precisam ser substituídas/complementadas por atributos multidimensionais de política cambial e monetária.

4. **Voz editorial como ganho de validade, com gate de factibilidade.** A distinção entre voz editorial própria, tendência do conteúdo publicado e discurso de terceiros reproduzido é metodologicamente importante, porque reduz o risco de atribuir ao jornal posições presentes apenas em falas citadas, telegramas, discursos parlamentares, cartas ou imprensa estrangeira. Contudo, Pedro registrou corretamente que essa distinção pode ser difícil em escala e não pode travar por muito tempo a execução da Fase B. Decisão: tentar identificar essa diferença primeiro em amostra estratificada/padrão-ouro e em pilotos operacionais; se a identificação se mostrar suficientemente confiável e barata, ela entra como variável estruturante; se não, a análise em escala usará a tendência do conteúdo publicado como medida principal, com a limitação explicitada e a avaliação de vozes de terceiros tratada como camada amostral/qualitativa.

5. **Resultado surpreendente reformulado com dependência explícita.** Um achado que enfraqueceria a hipótese inicial seria baixa estabilidade das categorias ortodoxia/expansionismo entre fases e objetos de política. Outro achado possível seria constatar que diferenças aparentes entre jornais decorrem mais de gênero textual, evento ou voz reproduzida do que de alinhamento editorial consistente; este segundo teste, porém, depende diretamente do êxito mínimo da distinção entre voz editorial e discurso reproduzido. Se esse êxito não for alcançado de modo factível, a conclusão deve ser formulada com menor ambição: tendência do conteúdo publicado, não alinhamento editorial estrito.

6. **Comparações finais priorizadas.** As comparações principais a orientar denominadores e agregações serão: cada jornal antes/depois dos marcos de 1906, 1910 e 1914; diferenças entre jornais em saliência e posição; diferenças entre posição sobre a Caixa como instituição e posição sobre instrumentos específicos; e relação entre posição editorial, quando observável, e vozes/interesses reproduzidos. A expressão "impacto de eventos" deve ser usada com cautela e, salvo desenho causal adicional, tratada como variação temporal associada a eventos de política monetária, não como identificação causal.

7. **Regra de factibilidade para a dissertação.** O projeto deve preservar a ambição substantiva, mas reduzir a obrigação métrica: não é necessário medir todas as dimensões com a mesma granularidade. Se houver tensão entre refinamento classificatório e prazo, prioridade será dada ao conjunto mínimo defensável para concluir o empírico: saliência, posição, variação temporal e justificativas principais, com rastreabilidade até evidência textual e declaração explícita das limitações sobre voz editorial e interesses representados.

---

## 2026-07-19 — Hipótese de trabalho do instrumento: extração de afirmações como camada primária (discussão Claude, ratificação de Pedro)

Base: discussão das decisões de desenho abertas em `docs/sintese-desenho-mensuracao.md` (seção 4). Não é a escolha final do instrumento, que o gate de `docs/contexto-debate-metodologico-mensuracao.md` reserva ao benchmark e à aprovação explícita de Pedro. É a hipótese que orienta os artefatos 3 a 6 da rodada.

**Hipótese de trabalho (ratificada por Pedro):** usar extração estruturada de afirmações por peça como camada primária de representação observável. A escala ortodoxia/expansionismo, os atributos de política e as justificativas econômicas serão vistas derivadas dessa camada. A adoção em escala dependerá de teste barato em amostra do piloto, avaliando confiabilidade, custo, capacidade de reconstruir a escala herdada e utilidade para distinguir voz editorial de discurso reproduzido.

Consequências para as decisões abertas: D1 fica orientado por essa camada (escala -2/+2 e atributos multidimensionais viram vistas, não schema primário); D2 (perenidade das categorias) e D6 (justificativas econômicas) tornam-se campos derivados testados na amostra; D4 (voz editorial) ganha a tag de voz como campo da afirmação, com teste de factibilidade por gênero e seção. O artefato 3 da rodada passa a comparar dois desenhos: extração-primeiro em camadas contra escala-primeiro em score único. D3 (unidade peça versus edição-dia) segue como ponto de atenção a formalizar na próxima sessão e é coerente com a peça como unidade de observação desta camada. As recomendações de trabalho por decisão, com o teste mais barato de cada uma, ficam na seção 8 da síntese.

---

## 2026-07-19 — D3 resolvido: separar posição de saliência (corner case de Pedro; decisão de Pedro)

Contexto: D3 estava como ponto de atenção (unidade peça versus edição-dia). Pedro levantou um corner case decisivo: se a edição-dia for o único denominador de saliência, ela achata a diferença entre um jornal que menciona a Caixa corriqueiramente todo dia (uma nota curta) e um jornal que, em menos dias, concentra várias peças substantivas (editorial, discurso, análise). A edição-dia sozinha capta presença ou ausência diária, não intensidade nem composição.

Decisão:

1. **Níveis distintos.** Unidade de codificação primária = peça relevante (texto que menciona a Caixa). Subunidade de extração = afirmação substantiva (camada de extração da hipótese primária de 2026-07-19). Unidade principal de agregação para posição = edição-dia estrita.

2. **Posição** permanece na edição-dia estrita, para comparabilidade temporal entre jornais e para não superponderar jornais com muitas peças no mesmo dia. A posição da edição-dia deriva das afirmações extraídas das suas peças relevantes; posições substantivas opostas sem dominância clara viram Mixed/Ambiguous.

3. **Saliência decomposta em três quantidades**, porque uma métrica única não segura o corner case:
   - saliência extensiva = `dias_relevantes / dias_triados` (presença diária). É o R sobre S já pré-registrado na cascata de 2026-07-18.
   - intensidade interna = `n_pecas_relevantes` por edição relevante (volume dentro do dia). Usa o campo `n_itens_relevantes` já pré-registrado, agora com papel analítico próprio.
   - proeminência = destaque das peças relevantes na edição (página, seção), por máximo ou média. Usa o campo `proeminencia` (máximo) já pré-registrado.
   - `houve_editorial` (OR das peças) fica como indicador qualitativo de envolvimento editorial.

Justificativa: a edição-dia é adequada para posição e comparabilidade temporal, mas insuficiente como única medida de atenção. Decompor frequência, volume e destaque evita igualar artificialmente jornais que mencionam a Caixa uma vez por dia e jornais que concentram várias peças substantivas em dias específicos. Não contradiz a cascata K, E, D, S, R, C de 2026-07-18: R sobre S continua sendo a saliência extensiva, e a decisão acrescenta intensidade e proeminência como séries complementares. Resolve o ponto de atenção D3 de `docs/sintese-desenho-mensuracao.md` (seção 4) e é coerente com a peça como unidade de observação da camada de extração. A implementação das três métricas é da camada de agregação da Fase B, informada por esta decisão.
