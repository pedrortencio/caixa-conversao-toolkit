# Testes do desenho de mensuração

**Data:** 2026-07-19
**Status:** D1 executado em papel (custo zero de API); D5 protocolado com estimativa de custo, para rodar na próxima sessão com orçamento. Insumo da rodada metodológica; não decide o instrumento, que o gate reserva ao benchmark e à aprovação de Pedro.

Base: hipótese de trabalho ratificada em `docs/decisoes.md` (2026-07-19) e recomendações da seção 8 de `docs/sintese-desenho-mensuracao.md`.

## 1. D1 — Teste em papel do esquema de extração de afirmações

Objetivo: verificar, em peças reais do piloto (O Paiz 1906, jornal aprovado 79/79 na regressão), se a camada de extração de afirmações (a) captura a peça, (b) permite reconstruir a escala herdada, (c) faz emergir as justificativas econômicas e (d) separa voz editorial de discurso reproduzido. Fonte: `dados/piloto_1906/jsonO_Paiz_1906/*_classificacao_holistica.json`, campo `supporting_evidence` (citações) mais o rótulo `overall_classification`.

### Esquema de extração proposto (campos por afirmação)

- **peca / localizador:** edição, página, âncora textual.
- **ator_voz:** editorial do jornal, notícia factual da redação, ou terceiro reproduzido (carta, telegrama, discurso parlamentar, imprensa estrangeira).
- **alvo:** a Caixa como instituição, ou um instrumento específico.
- **objeto_politica:** taxa de conversão, conversibilidade, lastro-ouro, emissão de papel-moeda, valorização do café, atração de capital, padrão-ouro.
- **direcao:** apoio, oposição, condicional, ou factual-neutro.
- **justificativa:** câmbio estável para o comércio, defesa do café, atração de capital, crédito e prosperidade, medo de inflação ou quebra do padrão, probidade financeira.
- **evidencia_textual:** citação mais localizador.
- **fase:** 1906 criação (para controlar a deriva conceitual).

Vista derivada (escala): direção agregada das afirmações de voz editorial do jornal, mapeada de ortodoxo (-2) a expansionista (+2). Vistas paralelas: atributos por objeto de política; distribuição de justificativas.

Escala de rótulos observada no piloto: Clearly Orthodox, Leaning Orthodox, Neutral-Factual, Leaning Expansionist, Clearly Expansionist, mais Mixed/Ambiguous e No Relevant Mentions. Em O Paiz 1906: 45 de 78 edições com posição, 33 sem menção relevante.

### Caso 1 — O Paiz ed 07819 (piloto: Clearly Expansionist)

Afirmações extraídas, todas de voz editorial do jornal:

- objeto = emissão de moeda-papel a taxa prefixada mais lastro-ouro; direcao = apoio forte; justificativa = atração de capital estrangeiro, estabilidade cambial, crédito e prosperidade, defesa do café.
- Evidências: a proposta de Nilo Peçanha de câmbio a taxa prefixada; "haverá trabalho, haverá crédito, haverá prosperidade: o café beneficiará directamente dessa medida"; "esses capitaes affluirão" ao mitigar o risco cambial.

Vista escala: todas as afirmações do jornal apoiam a expansão monetária lastreada, reconstruindo Clearly Expansionist (+2). Reconstrução correta. Atributos (emissão, lastro condicionado a ouro, valorização do café, atração de capital) variam de forma coerente e não redundante.

### Caso 2 — O Paiz ed 07834 (piloto: Leaning Orthodox)

Afirmações extraídas:

- B1: ator_voz = terceiro reproduzido (carta publicada pelo jornal); objeto = quebra do padrão-ouro; direcao = preocupação e oposição; justificativa = probidade financeira, medo de elevação artificial do câmbio.
- B2: ator_voz = notícia factual (reporta o Convênio de Taubaté e o empréstimo como lastro); direcao = factual.

Vista escala: o rótulo Leaning Orthodox do piloto vem sobretudo de B1, que é voz reproduzida (uma carta), não posição editorial própria. A escala reconstrói o rótulo, mas a camada de extração expõe que ele se apoia em discurso de terceiro.

### Veredito do D1

1. **Reconstrução da escala herdada: OK** nos dois casos. A camada recupera Clearly Expansionist e Leaning Orthodox a partir das direções das afirmações.
2. **Atributos de política variam de forma independente** e carregam o conteúdo específico da fase (café, capital, padrão-ouro, emissão). Sustenta tratar a perenidade (D2) como campo testável, não premissa.
3. **Justificativas emergem como campo (D6):** café, capital, prosperidade, inflação, probidade. Confirma a estratégia bottom-up de D6.
4. **Ganho de validade (D4) em dado real:** o caso 07834 mostra o risco concreto do memorando §4, atribuir ao jornal uma posição presente só numa carta reproduzida. A camada de extração torna isso explícito por afirmação; o score holístico único o esconde.

Conclusão: a hipótese de trabalho primária passa no teste em papel sobre O Paiz. Recomendo formalizar o esquema como o desenho extração-primeiro do artefato 3 e submetê-lo, contra o escala-primeiro, ao benchmark. Antes disso, um teste humano em 10 a 15 peças estratificadas (artefato 5) confirma a confiabilidade entre codificadores.

Ressalva: teste em 2 casos de um único jornal, ilustrativo do mecanismo e da viabilidade, não confiabilidade estatística. Serve para mostrar que o desenho funciona, não para decidir.

## 2. D5 — Protocolo executável (OCR-BN vs transcrição LLM) e estimativa de custo

Objetivo: decidir se a classificação pode rodar sobre o texto embutido (OCR da BN, grátis) em vez da transcrição LLM paga, o que pode liberar quase todo o orçamento de R$415 da Fase B.

Prerequisitos, já existentes: camada de texto embutido (view `v_current_page_texts` no banco); transcrições LLM do piloto; prompt de classificação versionado (`pipeline/prompts`) com bloco da fase 1906; rótulos holísticos do piloto.

Procedimento:

1. Amostra: edições O Paiz 1906 do piloto, estratificadas pelos 5 rótulos mais alguns No Relevant como negativos. Cerca de 30 edições, ou as 78, ainda barato.
2. Para cada edição, montar dois insumos textuais da(s) página(s) relevante(s): (a) OCR-BN de `v_current_page_texts`, (b) transcrição LLM do piloto.
3. Rodar o mesmo prompt de classificação (gemini-2.5-pro, versão pinada, bloco da fase 1906) sobre (a) e sobre (b). Registrar modelo e versão no output.
4. Comparar: (i) concordância OCR-BN vs LLM (kappa e match exato na escala de 5 pontos); (ii) cada um contra o rótulo holístico do piloto; (iii) leitura qualitativa dos casos onde o OCR sujo vira o rótulo.
5. Regra de decisão pré-registrada: se kappa(OCR-BN, LLM) maior ou igual a 0,70 sem viés sistemático, e a concordância OCR-BN vs piloto for aproximadamente igual à de LLM vs piloto, então a classificação roda sobre OCR-BN grátis, e a transcrição LLM fica reservada só às páginas onde o OCR degrada o rótulo. Caso contrário, manter transcrição LLM nas candidatas.

Estimativa de custo: cerca de 60 chamadas de classificação (2 por edição vezes 30), entrada dominada pelo OCR (aproximadamente 10 a 13 mil tokens por página) mais a transcrição LLM (2 a 4 mil), saída pequena (aproximadamente 300 tokens de JSON). Total da ordem de meio milhão de tokens de entrada. A poucos dólares por milhão de tokens do gemini-2.5-pro (confirmar o preço vigente antes de rodar; o batch mode dá 50 por cento de desconto), o teste custa da ordem de poucos reais, muito abaixo do gate de custo e das 100 chamadas. Ou seja: a decisão de gastar ou não os R$415 da Fase B é resolvida por um teste de poucos reais.

Guardrail: a estimativa de custo está feita e o teste fica sob 100 chamadas; ainda assim, rodar só com a versão do modelo registrada e sem tratar o resultado como liberação de lote substantivo, que continua condicionado ao benchmark e à aprovação de Pedro.
