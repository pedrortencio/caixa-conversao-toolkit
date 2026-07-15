---
name: pipeline-hemeroteca
description: Use ao rodar, implementar ou modificar qualquer etapa do pipeline de dados (scraper da Hemeroteca, transcrição, classificação, consolidação, análise) e ao estimar custos de API.
---

# Pipeline Hemeroteca → base Caixa de Conversão

## Mapa e estado (atualizar este bloco quando uma fase for concluída)

| Etapa | Pasta | Estado |
|---|---|---|
| F1a Scraper — ENUMERAÇÃO de hits | `pipeline/scraper/` | receita validada (Selenium); falta produtizar em script + testar ao vivo |
| F1b Scraper — DOWNLOAD legível | `pipeline/scraper/download.py` | FEITO e testado: HTTP puro, byte-idêntico ao piloto (ver abaixo) |
| F2 Inventário + auditoria recall | `pipeline/scraper/` | a implementar |
| F3 Transcrição | `pipeline/transcricao/` | a implementar (evolução de `legado/rnc1.0.py`) |
| F4 Classificação | `pipeline/classificacao/` | a implementar (evolução de `legado/text_analysis2.0.py`) |
| F5 Consolidação SQLite/xlsx/parquet | `pipeline/consolidacao/` | a implementar |
| F6 DSL + dicionário | `analise/` | a implementar |

Detalhes de cada fase: `docs/plano-pipeline.md`. Scripts do piloto em `legado/` são REFERÊNCIA de lógica e prompts, não para rodar (modelo aposentado, caminhos hardcoded).

## Guardrails de execução

1. **Regressão 1906 primeiro.** Nenhum lote de API roda antes de o scraper reproduzir o gabarito do piloto: Paiz 79, CorreioP 94, CorreioM 110, Gazeta 146 edições. Divergência = investigar, não prosseguir.
2. **Custo antes do lote.** Qualquer rodada > 100 chamadas: rodar 10, medir custo real extrapolado, comparar com o orçamento (~R$ 830 no projeto) e só então liberar.
3. **Resume em tudo.** Toda etapa pula outputs existentes; rodadas são retomáveis após queda da BN ou da API.
4. **BN com educação:** 2-3 s entre requisições, backoff exponencial, lotes grandes de madrugada. O DocReader é WebForms/Telerik (VIEWSTATE); mudanças de layout quebram o Selenium, manter seletores isolados em um módulo.
5. **Nomenclatura imutável:** `per{bib}_{ano}_{página:05d}` (compatível com o piloto). Downloads em `dados/raw_pdf/{jornal}/` (gitignored), transcrições em `dados/transcricoes/{jornal}/`, classificações em `dados/classificacoes/{jornal}/`.
6. **Prompts são instrumento de medição:** vivem em `pipeline/prompts/`, qualquer mudança exige entrada em `docs/decisoes.md` e reavaliação de validação.
7. **Modelos:** transcrição `gemini-2.5-flash` (escalar página a página para `-pro` apenas em saída truncada/ilegível); classificação `gemini-2.5-pro` com temperatura baixa e `response_mime_type=application/json`. Registrar versão exata do modelo em cada output.
8. Chaves em `.env` na raiz (nunca commitado): `GOOGLE_API_KEY` (Gemini) e `ANTHROPIC_API_KEY` (Claude, robustez multi-modelo). Executar sempre via `uv run python ...`. Código novo usa o SDK `google-genai` (`from google import genai`), NÃO o `google-generativeai` do legado (descontinuado).

## Fatos técnicos da Hemeroteca (verificados 13/07/2026, diagnóstico ao vivo)

- Viewer: `https://memoria.bn.gov.br/DocReader/DocReader.aspx?bib={bib}_{pasta}`. **Mapa completo das pastas que cobrem 1906-1914** (títulos conferidos página a página):

| Jornal | Pastas | Cobertura |
|---|---|---|
| O Paiz | `178691_03` + `178691_04` | 1900-09 + 1910-19 |
| Correio Paulistano | `090972_06` | 1900-1919 (única) |
| Gazeta de Notícias | `103730_04` | 1900-1919 (única) |
| Correio da Manhã | `089842_01` + `089842_02` | 1901-09 + 1910-19 |

- **Deep-link de busca funciona:** `DocReader.aspx?bib={...}&pesq=caixa%20de%20convers%C3%A3o` — o JS do viewer preenche `PesquisarTxt` e clica `Pesquisar2Btn` sozinho. Ponto de entrada do Selenium: carregar a URL com `pesq` e ler a lista de hits do DOM (não precisa digitar no campo).
- Busca por frase exata com aspas, dentro do periódico.
- Sem API limpa (WebForms/Telerik, VIEWSTATE); handler de download `SaveAsFile.ashx?id=...` com id de sessão (sondar para download em lote dentro da sessão Selenium).
- Servidor respondeu rápido e estável no diagnóstico (~200 KB/página, 18 requisições, nenhum bloqueio com 1 req/s).
- Ferramenta de referência: pyHDB (Eric Brasil) — Selenium, citável na metodologia.

### Teste real do Selenium (13/07/2026, scripts em `pipeline/scraper/explora_*.py`)

- **Selenium PURO funciona** (sem undetected-chromedriver, que aliás quebra com `--headless=new` no Chrome 150; UC só como fallback em modo headed se a BN algum dia bloquear).
- Deep-link `&pesq="caixa de conversão"` **dispara a busca sozinho até em headless**: O Paiz 1900-09 (`178691_03`) → **"Matchs 1/701"** (701 ocorrências na década; 1906 é subconjunto).
- Metadados do hit atual: `span#PastaTxt` com `title="Ano 1902\Edição 06388"`; página dentro da edição em campo "N/M"; contador em `#ocorrenciaatualdiv`.
- **Limitação headless:** a imagem principal e o painel "Match thumbs" (menu `#ThumbsBtn` → dock `#ThumbsRadDock`) NÃO renderizam em headless (spinner eterno, dock vazio). Próximo passo: testar headed.
- **RECEITA VALIDADA de enumeração de hits (testada de ponta a ponta em 13/07, headed):**
  1. Carregar `DocReader.aspx?bib={pasta}&pesq="caixa de conversão"` (busca dispara sozinha; contador em `#ocorrenciaatualdiv`).
  2. Fechar modais Telerik (`div.TelerikModalOverlay` visível → clicar `a.rwCloseButton`/`span[title=Close]` via JS; helper `fecha_modais` em `explora_thumbs.py`).
  3. **CAPTCHA: human-in-the-loop VALIDADO** — detectar (src/id/class com "captcha"), pausar, Pedro resolve na janela, script segue (`espera_humano_resolver_captcha`). Apareceu 1x na sessão de teste, resolvido, fluxo continuou sem erro.
  4. Clicar `#ThumbsBtn` (nativo) → item de menu com texto "Match thumbs" (procurar no DOM inteiro por XPath; RadMenu renderiza fora do `#ThumbsMenu`).
  5. **Cada thumb do dock entrega tudo:** `img#ThumbsRadDock_C_ThumbsImg{i}` com `title="Folder:Ano 1906\Edição 07819"` (ano+edição) e checkbox `#ThumbsRadDock_C_ThumbsChk{i}` com `onclick="ThumbsChk('10966')"` (página absoluta). 8 thumbs por vista; paginar com as setas do carrossel (~88 vistas para 701 hits ≈ minutos por pasta).
  6. **Os números de edição batem com os nomes de arquivo do piloto** (per178691_1906_07819 = Edição 07819) → regressão de 1906 compara direto.
  7. Thumbs/imagens só renderizam em modo HEADED (headless: busca e contador funcionam, imagens não). Rodar lotes headed; janela pode ficar em segundo plano.
  8. **Download TESTADO (13/07, `explora_download.py`):** `fetch` same-origin dentro da sessão Selenium baixa a imagem do `#DocumentoImg` (salva `dados/raw_pdf/teste/pagina_teste_vista.jpg`, O Paiz 05/04/1902). PORÉM o viewer só pede a resolução da janela (~517px, ilegível p/ transcrição); construir URL full-res no cache dá **404** (cache só serve o que o viewer mandou gerar). Formato do nome: `I{pag:07d}-1-0-{vistaW:06d}-{vistaH:06d}-{fullW:06d}-{fullH:06d}.JPG` (original ~7443×4994).
  9. **Deep-link de página descoberto:** `DocReader.aspx?bib={pasta}&pesq={termo}&pagfis={página_absoluta}` navega direto à página do hit — o downloader não precisa clicar em nada.
  10. **Rotas para resolução de trabalho (testar na F1):** (a) zoom programático no viewer → ele gera cache maior → fetch; (b) exportação oficial em PDF (`SaveAsFile.ashx`, mesma rota do download manual do piloto), com CAPTCHA human-in-the-loop já validado.
  11. Fallback (se thumbs quebrarem): navegação ocorrência a ocorrência (» + `#PastaTxt`), ~2 s/hit, funciona até sem imagem.

### DOWNLOAD legível: RESOLVIDO — host de PDF estático, HTTP puro (verificado 14/07/2026)

**O download NÃO usa o DocReader.** Existe um host de arquivos estáticos, aberto, com a edição inteira em PDF:

```
https://hemeroteca-pdf.bn.gov.br/{bib}/per{bib}_{ano}_{edição:05d}.pdf
# ex.: https://hemeroteca-pdf.bn.gov.br/178691/per178691_1906_07890.pdf
```

- **Sem Cloudflare, sem navegador.** `curl`/`requests.get` devolve HTTP 200 `application/pdf` direto (testado da máquina do Pedro E de IP externo). O bloqueio Cloudflare é exclusivo do app `memoria.bn.gov.br/DocReader`.
- **Resolução validada:** o PDF do host estático é **byte-idêntico** ao que o piloto baixou à mão (8 pág, 2016×2985 px). Mesma legibilidade do κ=0.712.
- **Numeração casa com a busca:** o `{edição:05d}` do nome = o número "Edição NNNNN" que o Match thumbs retorna. Global contínua desde 1884 (1884→00001, 1906→~07890). O `{ano}` também vem do thumb ("Ano 1906\Edição 07890").
- **Baixa a edição-dia inteira** (não "página ±1"): é a unidade de análise e o que o piloto usava. Decisão #5 (página ±1) fica obsoleta.
- **F1b = HTTP puro:** loop sobre a lista de hits da F1a, `GET` de cada URL, rate-limit educado (2-3 s), retry/backoff, resume (pula PDF já baixado), 404 → log de auditoria de recall. Nada de Selenium aqui.

**Beco sem saída (NÃO refazer):** exportação PDF do DocReader (`PDFExportAbre`→Create→`SaveAsFile.ashx`) barra no Cloudflare mesmo com stealth (`navigator.webdriver=undefined` não basta; é fingerprint TLS/IP). Export de década inteira ("All current folder matchs", 701 hits) não completa. Rota de imagem do viewer só dá 517px. Registro completo em `docs/decisoes.md` (14/07). Scripts `explora_export*.py`, `explora_fullres.py`, `explora_pdfpane.py` são histórico do diagnóstico, não a rota de produção.
