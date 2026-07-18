# Handoff, sessao 2026-07-16: esquema da base do corpus

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
