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
