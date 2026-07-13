---
name: pipeline-hemeroteca
description: Use ao rodar, implementar ou modificar qualquer etapa do pipeline de dados (scraper da Hemeroteca, transcrição, classificação, consolidação, análise) e ao estimar custos de API.
---

# Pipeline Hemeroteca → base Caixa de Conversão

## Mapa e estado (atualizar este bloco quando uma fase for concluída)

| Etapa | Pasta | Estado |
|---|---|---|
| F1 Scraper (busca + download) | `pipeline/scraper/` | a implementar (Selenium, base pyHDB) |
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
8. `GOOGLE_API_KEY` em `.env` na raiz (nunca commitado).

## Fatos técnicos da Hemeroteca (verificados 13/07/2026)

- Viewer: `https://memoria.bn.gov.br/DocReader/DocReader.aspx?bib={bib}_{pasta}` (pastas por década; `178691_02` = O Paiz 1890-99).
- Busca por frase exata com aspas, dentro do periódico.
- Sem API limpa; handler de download `SaveAsFile.ashx?id=...` com id de sessão (sondar para download em lote dentro da sessão Selenium).
- Ferramenta de referência: pyHDB (Eric Brasil) — Selenium, citável na metodologia.
