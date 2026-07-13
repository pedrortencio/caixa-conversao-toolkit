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
