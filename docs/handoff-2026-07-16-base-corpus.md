# Handoff, sessao 2026-07-16: esquema da base do corpus

## Atualização, 18/07/2026 (noite): PR do debate de mensuração mergeado, camada de texto embutido

Sessão pós-Fase A. Backup da recuperação CONFERIDO (11.960 PDFs no destino == 11.960 locais).

1. **PR #1 mergeado** (`docs/contexto-debate-metodologico-mensuracao.md` agora canônico,
   ponteiros em CLAUDE.md/AGENTS.md; main até cc18860 com push). A rodada
   científico-metodológica ANTECEDE a Fase B substantiva; escala -2/+2, stance, LLM e
   Gemini viram hipóteses de trabalho a comparar.
2. **DESCOBERTA: os PDFs da BN têm camada de texto embutida** (OCR da Hemeroteca), em
   todos os objetos amostrados, 28-44k chars/página. Texto integral do corpus a custo
   ZERO de token.
3. **Camada de texto embutido implementada** (TDD, migração 003 aditiva, suíte 95 verde;
   commits f2baf2d/ebf022c): extração determinística pypdf pinada em protocolo
   `text_extraction/texto-embutido-pypdf 1.0.0`; statuses positivos ok/empty/error;
   texto em `C:\dados-caixa\texto_embutido\`; manifestos `dados/texto_embutido/`;
   modo `--verificar` de replay. Spec:
   `docs/superpowers/specs/2026-07-18-camada-texto-embutido-design.md`. Migração 003
   aplicada ao banco real SEM alterar contagens (user_version 3, integrity ok).
4. **Piloto O Paiz 1906 APROVADO**: 2.472 páginas, 100% ok, 0 empty, 0 error,
   5,85 pág/s; replay determinístico com 0 divergências; checagem cruzada com as
   transcrições LLM do piloto confirma páginas certas (~50% de tokens exatos em comum,
   OCR sujo esperado).
5. **Corrida completa DISPARADA destacada** (~115k páginas restantes, ~5,5h; PID 14932;
   log `dados/texto_embutido/log_extracao.txt` + `_err.txt`, gitignored). Resume por
   banco: re-rodar o mesmo comando continua de onde parou.
6. **Esqueleto do memorando de quantidades históricas** (artefato 1 da rodada) em
   `docs/memorando-quantidades-historicas.md`, aguardando preenchimento de Pedro.

### Retomada (próxima sessão, em ordem)

CORRIDA COMPLETA na madrugada de 19/07 (feito na própria sessão): 117.705/117.705
páginas com registro vigente (117.703 ok + 2 empty), ZERO error no corpus inteiro;
35 células reais (grid de 36 menos Gazeta 1913, sem acervo em fonte alguma);
`--verificar` amostral em 1 célula por jornal (8.692 páginas): 0 divergências;
manifesto da célula piloto regenerado byte-idêntico (determinismo confirmado em
dados reais). Manifestos commitados. Backup robocopy de texto_embutido para
`G:\My Drive\caixa-conversao\texto_embutido` disparado offline (Google Drive
sincroniza quando a internet voltar; conferir log
`C:\dados-caixa\backup_texto_embutido.log`, exit < 8).

1. **Push da main** (f2baf2d..HEAD): a internet da máquina caiu ~00h30 de 19/07 e
   não voltou até o fim da sessão (perfil de rede só LocalNetwork; vigias de
   30min/2h/4h expiraram). Conferir depois se o vigia final conseguiu ou fazer
   `git push origin main` à mão.
2. Conferir a sincronização do Google Drive (backup de texto_embutido + manifestos).
3. Rodada metodológica: Pedro preenche `docs/memorando-quantidades-historicas.md`;
   pendentes de ratificação o time-box (2-3 semanas) e o reposicionamento do P0
   (diagnóstico como insumo da rodada; reparo de codebook absorvido pelo protocolo
   humano do desenho vencedor). Em paralelo (Claude+Codex, pareceres independentes):
   matriz de literatura enxuta.

## Atualização, 18/07/2026 (tarde/noite): Fase A COMPLETA, pré-registros, merge do Codex

Sessão que executou os passos 2 a 5 da retomada da manhã e fechou a Fase A.

Feito e commitado (main até 519ce89, com push; branch feature/integracao-codex mergeada em 18ecbda):

1. **Segunda passagem do índice** (recomendação 2 do Codex): reextração das 4 páginas bndigital
   pelo Chrome do Pedro (Cloudflare barra requests), snapshots do DOM em
   `dados/censo/snapshots_bndigital/` com SHA-256 conferido navegador vs disco. Verificador novo
   `pipeline/scraper/indice_bndigital.py` (TDD): conjuntos de links IDÊNTICOS à primeira passagem
   nas 4 páginas, 0 divergências em 11.981 edições. `.gitattributes -text` protege os snapshots.
2. **Recuperação por lista de alvos** (`pipeline/base/recupera_indice.py`, TDD): baixou o diff
   índice-menos-censo. Rodada CONCLUÍDA: 3.070 ok, 0 erro, 22 ausências terminais (404 em 2
   observações), 1 pdf_invalido (Paiz 1913_10408, corrompido no host). 404 só terminal com 2
   observações; 403/429/5xx/rede = transitório.
3. **Fase A COMPLETA.** Banco: 11.960 objetos, 11.959 fetch ok, 1 invalid_pdf; integrity_check ok;
   user_version 2. O **CM de 1907-14, perdido pela varredura no salto 2099->2255, está inteiro**
   (362/365/362/362/363/363/363/340, batendo com o índice). Cobertura contra o índice: zero
   pendentes em quase toda célula; sobram só ausências de acervo reais (GN 1910 com 20, GN 1914
   com 1) e o Paiz 10408. Relatório regenerado em `docs/relatorio-cobertura-censo.md`.
4. **Pré-registros antes da Fase B** (`docs/decisoes.md`, ratificados por Pedro): agregação de
   manifestações; cascata K/E/D/S/R/C por jornal-mês; novo portão 1906 por 3 classes sem item
   inexplicado; flag cega varredura/somente_indice margem 5pp.
5. **Merge do Codex**: wrapper `invoca-codex.ps1` + protocolo + skill parecer-codex agora na main
   (aprovado no smoke test real de 18/07). Instrumento intacto.
6. **Backup**: robocopy incremental dos 3.070 PDFs novos para `G:\My Drive\caixa-conversao\raw_pdf`
   disparado no fim da sessão (log `C:\dados-caixa\backup_robocopy_recuperacao.log`; conferir exit
   code < 8 na retomada; local tinha 11.960 PDFs, backup partia de 8.890).

Sobre a **recuperação manual das 5 órfãs** (CM 1869/1870, CP 15276, GN 78 do piloto + Paiz 10408
corrompido): confirmado que NENHUM PDF do piloto existe no disco (0 em `dados/piloto_1906`, só
JSON+xlsx; as 4 órfãs não aparecem em lugar nenhum do C:). O export PDF do DocReader não completa
sob automação (POSTs com pagfis vazio; mesmo beco do 14/07) e, segundo Pedro, o máximo do DocReader
talvez seja captura de tela em baixa resolução. Pedro classificou as 5 como "detalhe do detalhe".
RECOMENDAÇÃO em aberto: documentar as 5 como exceção terminal do novo portão 1906 (decisão expressa
de Pedro) em vez de gastar tempo no DocReader.

### Retomada (próxima sessão, em ordem) — cronograma ~2 meses

Caminho crítico: NÃO é o censo (fechado) nem as 5 órfãs. São dois blocos.

1. **P0 do piloto de 1906** (gate antes de qualquer token pago). A auditoria do Codex
   (`docs/avaliacao-independente-2026-07-15.md`) achou: 280 "sem menção relevante" de 537 (porque o
   piloto buscava só os hits da BN; o novo desenho corrige com triagem barata de TODA página), 169
   sem data, κ=0,712 não reproduzível, decompor por item. Auditar/reparar o piloto e fechar o
   codebook das fases 2-4 (Pedro redige). Custo de token baixo.
2. **Plano de implementação da Fase B.** A spec existe (`docs/plano-batch-anotadores.md`, com
   apêndice técnico), o plano executável NÃO. Fase B = camada `pipeline/anotadores/` (backend
   `gemini_api` primário via Batch Mode + `claude_cli` segundo anotador), triagem, transcrição
   (gemini-2.5-flash), classificação (gemini-2.5-pro). Orçamento ~R$415, só roda após passar a
   regressão 1906 e medir o custo de um lote pequeno (guardrail).
3. **Decisão pendente de Pedro**: documentar as 5 órfãs como exceção terminal (fecha o portão 1906
   sem pendência) e escolher por qual dos dois blocos acima começar.

## Atualização, 18/07/2026 (manhã): índice bndigital descoberto, pareceres duplos, retomada da próxima sessão

Depois do fechamento da varredura (seção abaixo), a sessão descobriu que as páginas públicas
`bndigital.bn.gov.br/acervo-digital/{correio|correio-paulistano|gazeta-de-noticias|paiz}/{bib}`
trazem a ENUMERAÇÃO OFICIAL ano a ano do acervo, com links diretos ao host estático. Fatos
validados e manifestos em `dados/censo/indice_bndigital_*.csv` + LEIAME (commit 47c2045):
censo da varredura é subconjunto do índice nas 36 células; diff de 3.092 edições recuperáveis
(CM 2.781 em 1907-14; GN 306, incluindo 1914 inteiro); host ⊆ índice; GN 1913 inexistente nas
duas fontes; sobreposições de rótulo de ano no CM (masthead decide). Cloudflare barra requests:
extração só via navegador (claude-in-chrome + captcha resolvido pelo Pedro no DocReader).

Pareceres duplos de nível crítico executados conforme o protocolo (worktree, commit 90bb449):
parecer do Claude congelado com hash ANTES do despacho; Codex invocado pelo wrapper com pacote
isolado (PRIMEIRA execução real, smoke test aprovado; registro run 20260718T093603843-5b165538).
Codex favorável à incorporação sob condições; síntese apresentada ao Pedro na sessão. Pontos que
o Codex acrescenta e que valem adotar: quadro K/E/D/S/R/C por jornal-mês; segunda passagem de
extração do índice com snapshot e hash; 404 terminal só com duas observações; regra de agregação
de manifestações (dedupe exato; dia = 1 unidade analítica; opostas = Mixed/Ambiguous; OR/max);
flag cega varredura/somente_indice com margem de 5 p.p. pré-registrada; descrever o corpus como
censo do acervo digital em fotografia datada.

Backup robocopy DISPARADO em 18/07 09h49 (destacado, log em C:\dados-caixa\backup_robocopy.log,
destino G:\My Drive\caixa-conversao\raw_pdf); conferir conclusão e código de saída na retomada.

### Retomada (próxima sessão, em ordem)

1. Conferir backup (log do robocopy; exit code < 8) e estado do banco/manifests (`git status`).
2. SEGUNDA passagem de extração do índice via navegador (recomendação 2 do parecer do Codex):
   repetir a extração das 4 páginas, comparar com `indice_bndigital_*.csv`, registrar
   divergências; guardar snapshot com hash conforme a recomendação 1.
3. Implementar via TDD o modo lista de alvos da recuperação (novo `pipeline/base/recupera_indice.py`
   ou extensão do `carrega_censo`): fonte `inventory/indice_bndigital/1.0.0`, alvos = diff
   índice menos censo, registro positivo por item, 403/429/5xx = transitório, 404 terminal
   exige 2 observações; re-tentativa do Paiz 1913_10408 na mesma rodada.
3. Disparar a rodada destacada (~3.092 alvos, ~25-30 GB, ~4h com pausa 4s) e, ao concluir,
   re-rodar `relatorio_censo.py` + checagens de banco e atualizar este handoff.
4. Pré-registros em docs/decisoes.md ANTES da Fase B (base: recomendações 5-9 do parecer do
   Codex + parecer do Claude): agregação de manifestações; cascata K/E/D/S/R/C; novo portão
   1906 (nenhum item do piloto inexplicado; lista de exceções aprovada por Pedro); flag cega
   varredura/somente_indice com margem 5 p.p.
5. Pendentes de decisão do Pedro: resgate manual das 4 edições do piloto no DocReader;
   merge da branch feature/integracao-codex (wrapper aprovado no uso real).

## Atualização, 18/07/2026 (madrugada): varredura ENCERRADA, relatório de cobertura e regressão 1906

A varredura completou sozinha às ~04h05 de 18/07 (processo destacado encerrou limpo).
Resultado: 8.889 edições ok (84,4 GB, 84.771 páginas materializadas) + 1 `pdf_invalido`
(`per178691_1913_10408.pdf`, HTTP 200, 21 MB, ilegível pelo pypdf; candidato a
re-download manual). Relatório completo: `docs/relatorio-cobertura-censo.md`, gerado por
`pipeline/base/relatorio_censo.py` (novo, com testes; lê só manifestos, nunca o banco).

Portão da Fase A verificado nesta sessão:

- Banco == manifesto == disco nas 27 células (bib, ano) com sucesso; zero divergências.
- `PRAGMA integrity_check` ok; migração 002 APLICADA ao banco real (user_version 2),
  na primeira conexão após a varredura soltar o arquivo, como previsto.
- `physical_pages` == `page_count` do fetch vigente em todos os objetos.
- Regressão do gabarito 1906: O Paiz APROVADO 79/79. Correio da Manhã 106/108
  (faltam 1869 e 1870), Correio Paulistano 92/93 (falta 15276), Gazeta 145/146
  (falta 78). Os 4 faltantes foram sondados ao vivo e são 404 REAIS no host
  estático: são edições que o piloto baixou à mão pelo DocReader (três delas são as
  edições duplas com prefixo A/B). Não é bug do scraper, é limite de cobertura do host.

Lacunas de acervo DO HOST descobertas (decisão metodológica pendente de Pedro):

- Correio da Manhã: host para no número 2099 (~jul/1907). 1908 varrido 2100-2299 sem
  sucesso; 1909-1914 sem varredura efetiva (sem âncora). Sondagens extra (extrapolações
  ~3010/3740/4470 para 1910/12/14 e sondas anuais n=1..6 de cada ano) todas 404.
- Gazeta: host para no número 278 de 1912 (~out/1912); 1913 concluída com zero
  sucessos, 1914 pulada. Buracos grandes internos em 1910-1912 (75/60/68 edições).
- O Paiz tem o mesmo fenômeno em miniatura: ~122 números ausentes no fim de 1907
  (8368-8489); a janela de 200 atravessou e 1908 retomou em 8490.
- Sem listagem de diretório no host (403). Próximo passo proposto: verificar NO
  DOCREADER (navegador; Cloudflare bloqueia requests) se CM 1907-14 e Gazeta 1912-14
  existem digitalizados. Se sim, desenhar rota de recuperação (export SaveAsFile com
  captcha human-in-the-loop, receita validada em 13/07); se não, registrar como
  ausência de acervo no denominador (cascata do censo).

Pendências operacionais: backup robocopy para `G:\My Drive\caixa-conversao\raw_pdf`
decidido e AINDA NÃO executado; Gazeta 1914 e CM 1909-14 sem manifesto de varredura
efetiva (registrados no relatório como anos sem varredura/sem sucesso).

## Atualização, 18/07/2026: Fase A em execução

A Fase A (censo 1906-1914) foi implementada e a varredura completa está RODANDO em
processo destacado. Plano: `docs/superpowers/plans/2026-07-18-fase-a-censo-download.md`.
Fatos de desenho descobertos por sondagem real: os 4 bibs servem PDF no host estático;
o par (ano, número) é validado pelo servidor; O Paiz, Correio da Manhã e Correio
Paulistano têm numeração contínua entre anos; a Gazeta tem numeração anual COM buracos
reais no meio do ano (1907: números 100 e 200 ausentes, 320 existe). Por isso o censo é
varredura número a número com registro positivo de ausência, nunca busca binária pura.

Operação:

- Raiz local dos PDFs: `C:\dados-caixa\raw_pdf` (fora do OneDrive). Backup decidido por
  Pedro: local + Google Drive (`robocopy C:\dados-caixa\raw_pdf "G:\My Drive\caixa-conversao\raw_pdf" /E /XO`).
- Pausa automática: 4,0 s de dia, 2,5 s de madrugada (23h-7h). Decisão de Pedro em 18/07:
  rodar de dia também, prevalecendo sobre o "lotes grandes de madrugada" do CLAUDE.md.
- Volume estimado: ~13 mil edições, ~90 GB (PDFs de ~5-7 MB), ~30 h de rede no total.
- Estado por (bib, ano) em `dados/censo/`: `varredura_{bib}_{ano}.csv` (manifesto
  versionado, positivo para presença E ausência), `inicio_{bib}_{ano}.txt` (sidecar de
  retomada), `concluido_{bib}_{ano}.txt` (marcador de varredura terminada por regra).
- Log: `dados/censo/log_varredura.txt` (gitignored). Interromper é seguro: o resume lê
  manifesto e cache de PDFs válidos sem tocar a rede.
- Para retomar após interrupção: `uv run python pipeline/base/carrega_censo.py --raw-root C:\dados-caixa\raw_pdf`.
- Status rápido: contar linhas ok/ausente dos CSVs de `dados/censo/` + tail do log.

Ao concluir os 36 (bib, ano): relatório de cobertura do censo (contagens por bib/ano,
buracos, estados de ausência), verificação do gabarito 1906 (79/94/146/110 hits do
piloto devem ser subconjunto do censo), commit dos manifestos, e só então Fase B.

## Atualização, 17/07/2026

O manifesto visual resolveu as 22 lacunas e corrigiu cinco candidatos do OCR.
A carga limpa agora produz 72 registros históricos, 67 datas vigentes observadas,
67 dias civis distintos, zero datas imputadas e zero datas não resolvidas.
A próxima revisão recomendada é humana e independente, por amostra ou pelos 27 casos.

A revisão independente da implementação (Claude, 17/07) está em
`docs/revisao-independente-claude-2026-07-17.md`: aprovada com ressalvas. O achado
principal foi corrigido no mesmo dia (`code_commit` fora da identidade do protocolo,
permitindo reexecutar a carga sob commits novos). Os achados B, D e E do parecer
ficam para uma migração 002 e ajustes de spec antes da Fase B.

## Atualização após a carga, 16/07/2026

A etapa de implementação foi concluída no repositório principal. Foram criados `pipeline/base/schema.sql`, `pipeline/base/migrations/001_init.sql`, `pipeline/base/db.py`, `pipeline/base/carrega_piloto.py` e a suíte em `tests/`.

O banco operacional local `dados/base/caixa_conversao.db` foi criado e carregado com os 67 PDFs canônicos disponíveis, todos de O Paiz. A carga produziu 450 páginas físicas, 102 transcrições, 45 datas observadas e 22 datas não resolvidas. Os contract checks passaram e a segunda execução foi idempotente.

O relatório completo está em `docs/relatorio-carga-piloto-1906.md`. A pendência imediata deixou de ser o disparo do Codex. Agora é a revisão independente da implementação e a auditoria visual dos dois pares de datas duplicadas encontrados.

Documento para uma sessao futura (tokens frescos) retomar sem perder o fio. O Codex tem orcamento e esta tocando etapas enquanto o Claude encerra.

## Onde estamos

Desenhamos e validamos a base de dados do corpus (SQLite, fonte da verdade operacional que torna as edicoes da Hemeroteca legiveis por maquina). A v1 do spec passou por um painel de 3 lentes (subagentes frescos) e por uma auditoria do Codex. Veredito unanime: a v1 nao esta segura para comecar a coleta seletiva e a transcricao paga. Esta em curso um redesenho em camadas (v2), que o Codex esta redigindo.

## Consenso da validacao (o que a v2 tem que resolver)

- O corpus nao e agnostico a medicao como a v1 dizia. A identificacao de pagina relevante e definicao de corpus, nao medicao, e nao pode ser deferida como a decisao de postura pode.
- Negativo tem que ser registro positivo (resultado explicito por pagina: relevante, nao_relevante, incerta, erro, nao_avaliada), nunca inferido de ausencia de linha. Sem isso nao ha auditoria de recall.
- Censo e denominador da saliencia estao indefinidos e o fluxo so alimenta hits. Publicar a cascata: inventariadas, disponiveis, avaliadas, recuperadas, substantivamente relevantes, transcritas, classificadas. Denominador sobre edicao-dias avaliadas, nao hits.
- Data desacoplada da relevancia e do texto do modelo: masthead transcrito para TODA edicao; guardar data_literal, regiao, parser, versao; observada vs imputada; vizinhanca e imputada.
- Ligacoes explicitas busca -> hit -> objeto/edicao -> pagina.
- Append-only: busca, identificacao e transcricao versionadas, nunca sobrescritas.
- Recall com gancho no esquema e amostra estatisticamente valida (os ~15/jornal do plano sao insuficientes; limite superior perto de 20%).
- Gate de economia da identificacao: triagem barata em todas as paginas, transcricao de qualidade so nos candidatos, amostra estratificada lida por inteiro para medir o que a triagem perde. Medir o custo real da triagem antes de comprometer a arquitetura.
- Objeto digital da BN separado da unidade analitica edicao-dia (suplementos, edicoes extras, numero do arquivo vs impresso). Nao assumir 1 PDF = 1 edicao-dia.
- Nomear com honestidade: se a transcricao for seletiva, o corpus textual e um subcorpus recuperado por protocolo; a camada bruta (PDFs) deve ser completa, duravel e reprocessavel.

## Faseamento acordado

- Fase A, gate-free, pode comecar apos o contrato minimo de inventario: enumerar o censo e baixar os PDFs inteiros. Barato, necessario de todo jeito.
- Fase B, antes de gastar token de transcricao: fechar identificacao, denominador, recall dimensionado, validacao de data, e os gates do P0 de 1906 (auditar os 280 sem mencao localizando a pagina-hit).

## Plano em etapas (Codex redige, Claude revisa; Codex nao audita o que implementa)

1. v2 do spec (modelo em camadas). DESPACHADA ao Codex em 16/07.
2. schema.sql (DDL das tabelas v2). Depende da v2 aprovada.
3. pipeline/base/db.py + migrador + migrations.
4. Carga do piloto 1906 no esquema + contract check (teste com dado real; entrega o substrato do P0).

## Artefatos e caminhos

- v1 do spec: docs/superpowers/specs/2026-07-16-esquema-base-corpus-design.md (repo principal, untracked).
- Parecer do Codex sobre a v1: C:\Users\pedro\worktrees\caixa-conversao-integracao-codex\colaboracao\pareceres\2026-07-16-auditoria-esquema-base-corpus--20260716T195701784-20a144da.md
- v2 redigida pelo Codex (Etapa 1 CONCLUIDA em 16/07): colocada em docs/superpowers/specs/2026-07-16-esquema-base-corpus-design-v2.md (repo principal). Original do Codex em colaboracao/pareceres/2026-07-16-redesenho-esquema-base-v2--20260716T201513216-26049755.md no worktree. NOTA: 1656 linhas, 12 secoes, 44 CREATE TABLE, decisoes reservadas a Pedro na secao 10. FALTA a revisao independente da v2 (Claude + Pedro; Codex nao audita o que escreveu); ponto a calibrar: 44 tabelas pode estar super-normalizado (cobertura completa vs simplicidade operacional).
- Manifestos: mesmo worktree, colaboracao/manifestos/.

## Passos de retomada (proxima sessao Claude)

1. Ler este handoff, o parecer do Codex sobre a v1, e a v2 que o Codex redigiu.
2. Revisar a v2 de forma independente; salvar como docs/superpowers/specs/2026-07-16-esquema-base-corpus-design-v2.md; apresentar a Pedro os pontos de decisao (subcorpus vs censo textual completo; unidade edicao-dia).
3. Com a v2 aprovada, despachar a Etapa 2 (schema.sql) ao Codex via o wrapper (invoca-codex.ps1, com -Workdir no repo principal).
4. So iniciar a Fase A (coleta) depois do contrato minimo de inventario fechado na v2.

## Pendente imediato: Etapa de implementacao (manifesto pronto, disparo bloqueado por outage)

Em 16/07 o manifesto de implementacao foi escrito (colaboracao/manifestos/2026-07-16-impl-fase-a-e-carga-piloto.md), mas o disparo do wrapper ficou bloqueado por uma indisponibilidade temporaria do classificador de seguranca do harness. O manifesto pede ao Codex: schema.sql + migrations/001_init.sql + pipeline/base/db.py + pipeline/base/carrega_piloto.py (carrega o piloto 1906 real e roda contract checks), com blocos delimitados `===ARQUIVO: <caminho>===` / `===FIM===`, mais uma lista de "tabelas sem dado real no piloto" para calibrar as 44 tabelas.

Para disparar (rode com o prefixo ! no prompt, ou quando o classificador voltar):

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\pedro\worktrees\caixa-conversao-integracao-codex\scripts\invoca-codex.ps1" -Manifesto "C:\Users\pedro\worktrees\caixa-conversao-integracao-codex\colaboracao\manifestos\2026-07-16-impl-fase-a-e-carga-piloto.md" -TaskId "2026-07-16-impl-fase-a-e-carga-piloto" -Workdir "C:\Users\pedro\OneDrive\Documentos\Acadêmico\Dissertação Mestrado\Dados\caixa-conversao-toolkit"

Depois: a saida cai em colaboracao/pareceres/2026-07-16-impl-fase-a-e-carga-piloto--*.md. Separar os blocos em arquivos (um script curto le a saida e escreve os arquivos, sem carregar o conteudo no contexto), rodar o migrador e o carrega_piloto.py com uv, ler o relatorio de contract check e a lista de tabelas sem dado real (sinal de calibracao das 44 tabelas).

## Infra

- Integracao do Codex commitada na branch feature/integracao-codex (commit 2a00600), aguardando decisao de merge do Pedro. Nao mergeada.
- O wrapper invoca-codex.ps1 funciona para tarefas do repo principal usando -Workdir apontado para a pasta do OneDrive; o registro captura o estado do worktree (proveniencia registrada no proprio manifesto).
