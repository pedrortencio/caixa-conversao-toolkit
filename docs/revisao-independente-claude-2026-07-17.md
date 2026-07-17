# Revisão independente da base do corpus (spec v2, schema, db.py, carrega_piloto)

Data: 17/07/2026
Revisor: Claude (Fable 5), conforme protocolo de colaboração (o Codex não audita o que implementa)
Escopo: `docs/superpowers/specs/2026-07-16-esquema-base-corpus-design-v2.md`, `pipeline/base/schema.sql`, `pipeline/base/migrations/001_init.sql`, `pipeline/base/db.py`, `pipeline/base/carrega_piloto.py`, `pipeline/base/date_audit.py`, `pipeline/base/manifests/datas_masthead_1906.json`, banco `dados/base/caixa_conversao.db`

## Método

Leitura integral da spec e do código, seguida de verificação empírica contra o banco materializado e as fontes. Todos os testes abaixo foram executados nesta revisão, não herdados do relatório:

1. Reprodução de todas as contagens do `docs/relatorio-carga-piloto-1906.md` por consulta direta ao banco.
2. Teste de re-execução da carga sobre cópia do banco operacional (idempotência).
3. Carga do zero em banco novo e comparação linha a linha com o banco operacional, excluídas apenas colunas de timestamp e `code_commit` (replay determinístico).
4. Teste de alinhamento ordinal artigo para JSON legado: busca de cada `relevant_quote` no texto da página atribuída, com matching exato e aproximado, e varredura de todas as demais páginas do banco.
5. Verificação do manifesto de datas contra o banco (hashes, páginas, decisões) e projeção do estado pós-aplicação, incluindo monotonicidade número de arquivo por data.
6. Suíte de testes do repo: 32 testes, todos verdes.

## Veredito

Implementação aprovada com ressalvas pontuais. Nenhum achado invalida o contrato v2 nem os dados carregados. Um achado (A) precisa de decisão de design antes das Tasks 2 a 5 da auditoria de datas, porque a integração do manifesto vai esbarrar nele na primeira execução.

## Verificações que passaram (com evidência)

- Todas as contagens do relatório foram reproduzidas exatamente: 67 objetos, 67 edições, 450 páginas, 102 transcrições, 45 datas observadas vigentes, 0 imputadas, 43 dias civis distintos, avaliações substantivas 45 relevant / 26 not_relevant / 17 uncertain, 450 screening not_assessed.
- Replay determinístico: a carga do zero produz banco idêntico ao operacional em todas as colunas estáveis de todas as 44 tabelas.
- Idempotência real no mesmo commit: re-execução sobre cópia não cria nem altera nenhuma linha estável.
- Alinhamento ordinal artigo para JSON: as 74 quotes relevantes com 20+ caracteres foram localizadas na página exata a que o carregador as atribuiu (53 por substring exata, 21 por similaridade acima de 0,75 explicada por ruído de OCR, 0 em outra página, 0 ausentes). A suposição semântica mais arriscada do carregador está empiricamente confirmada.
- Manifesto de datas: os 27 registros são coerentes com o banco (pdf_sha256 idêntico, page_number dentro do PDF, os 5 `correct_ocr` apontam exatamente a data vigente errada, os 22 `fill_missing_ocr` apontam edições sem data). Projeção pós-aplicação: 67 datas observadas, 67 dias civis distintos, 0 imputadas, exatamente a meta do design.
- Corroboração independente da auditoria visual: ordenando as 67 edições pelo número de arquivo da BN, a data projetada cresce estritamente e a diferença de números é igual à diferença de dias em todos os 66 pares consecutivos. Essa progressão perfeita sustenta tanto as 27 datas visuais quanto as 40 datas de OCR não tocadas. Registro: a sequência continua sendo verificação de consistência, nunca fonte de data, como o design manda.
- `schema.sql` e `001_init.sql` são idênticos (a migração só acrescenta `PRAGMA user_version = 1`). As 44 tabelas correspondem à spec; o DDL ainda corrigiu duas omissões da spec (FK de `edition_identifiers.evidence_page_id` e unicidade parcial de `population_memberships`).
- `upsert_protocol` compara a identidade completa do protocolo e aborta em divergência, proteção correta do instrumento de medição.

## Achados

### A. Importante: a idempotência quebra entre commits

`db.py upsert_protocol` inclui `code_commit` (HEAD do repo) na comparação de identidade. A carga original rodou no commit `2c37d2b`; re-executar hoje aborta com `ValueError: conflito de protocolo`. Qualquer commit novo, mesmo só de docs, torna a carga não re-executável sem bump de versão de todos os 6 protocolos. Confirmado empiricamente: o re-run falhou com HEAD atual e passou com o commit original fixado.

Consequência imediata: as Tasks 2 a 5 da auditoria de datas (que exigem novo commit e nova carga) falham na primeira execução.

Opções, em ordem de preferência desta revisão:

1. Tirar `code_commit` da comparação de identidade (mantê-lo como registro da primeira materialização) e, para protocolos determinísticos, incluir em `parameters_json` um hash do conteúdo do código do parser. Assim a identidade semântica é (stage, name, version, executor, modelo, prompt, parâmetros incluindo hash do código relevante), e mudanças reais de código continuam forçando versão nova, sem falso conflito por commit de docs.
2. Manter a regra e bumpar versões de protocolo a cada carga em commit novo. Rígido e barulhento; infla versões sem mudança de instrumento.

### B. Médio: falha de parse de data não é registrável positivamente

`date_records` só admite `observed` e `imputed`, com `normalized_date NOT NULL`. Uma tentativa de parse que falha não deixa registro; as 22 datas não resolvidas do piloto existiam apenas como ausência de ponteiro. O consenso da validação ("negativo é registro positivo") foi aplicado às páginas mas não às datas. As Tasks 2 a 5 zeram os 22 casos de 1906, mas o problema volta nos outros jornais e anos, onde haverá masthead ilegível de verdade. Recomendação: migração futura com tabela de tentativas de parse (ou status `unresolved` com `normalized_date` anulável e CHECK condicional), decidir antes da Fase B.

### C. Médio: população só materializa positivos

`population_memberships` recebeu apenas as 45 linhas `eligible`. As 22 edições sem data não têm linha nenhuma, ausência de novo, sendo que o esquema suporta `unknown` com `reason`. A carga deveria registrar explicitamente as não elegíveis. Corrigir junto com as Tasks 2 a 5 (após a aplicação do manifesto, a população piloto passa a ter as 67).

### D. Médio: divergência spec x DDL não retroalimentada

O CHECK de obtenção `ok` na spec exige `http_status BETWEEN 200 AND 299`; o schema.sql implementado aceita também `http_status IS NULL` (necessário para a importação local do piloto). A relaxação é legítima mas ficou só no DDL. Recomendação: atualizar a spec e considerar uma coluna `fetch_mode` (`http`, `local_import`) na Fase A, para que um download HTTP real com `http_status` nulo não passe despercebido.

### E. Menores

1. `response_sha256 = pdf_sha256` nas 67 obtenções importadas: não houve resposta HTTP, o valor é fabricado; deveria ser NULL (confirmado no banco: 67 de 67).
2. O contract check de contagem de páginas é circular: `physical_pages` é materializado a partir do mesmo `count_pdf_pages` heurístico que o check confere. Na Fase A, contar páginas com biblioteca de PDF real (pypdf) e manter o heurístico como cross-check.
3. `upsert_newspaper` e `upsert_digital_object` fazem `DO UPDATE` silencioso em campos de identidade (`bn_bib`, `source_url`, `source_year`). Aplicar o padrão do `upsert_protocol`: comparar e abortar em divergência.
4. `git_commit()` não detecta working tree sujo; a proveniência pode apontar para um commit que não contém o código executado. Abortar com árvore suja ou registrar sufixo explícito.
5. Append-only é convenção sem enforcement mecânico. Uma migração futura pode acrescentar triggers `RAISE(ABORT)` para UPDATE e DELETE nas tabelas históricas, barato e mecânico.
6. `pytest` não está declarado no `pyproject.toml` (a suíte só roda com `uv run --with pytest`). Declarar em dependency-group `dev`.
7. Spec cita migrações `001_initial_v2.sql` e `002_views_v2.sql`; o real é `001_init.sql` com as views dentro. Cosmético, atualizar a spec.
8. Heurística de relevância: duas quotes curtas viraram `relevant` ("25 o|o ouro, a 12 d", plausivelmente relevante de verdade, e "Fechos & Factos", título de seção, suspeita real). São casos para o P0 do piloto, não motivo para reescrever a heurística agora.

## Sobre as 44 tabelas (pergunta do handoff)

Não considero super-normalizado. Treze das 44 são ponteiros `current_*` de um padrão uniforme e mecânico; as demais mapeiam um para um artefatos metodológicos com identidade e ciclo de vida próprios (execução, resultado, evidência, gate). O custo cognitivo é baixo porque o padrão se repete; o ganho é exatamente o que o consenso da validação exigiu (append-only, negativo positivo, proveniência completa). Recomendo manter.

## Decisões que continuam reservadas a Pedro (spec, seções 10 e 12)

1. Gate de recall: limite inferior de confiança de 95% maior ou igual a 0,90 (29 unidades relevantes por estrato com zero perda) ou 0,95 (59 unidades, custo aproximadamente o dobro). A spec recomenda 0,90.
2. Censo textual completo ou subcorpus recuperado por protocolo. A spec recomenda subcorpus, com PDFs completos e mastheads universais, condicionado aos gates de economia e recall.
3. Edição-dia estrita ou múltiplas manifestações como unidade principal. A spec recomenda modelar múltiplas na coleta e analisar em edição-dia estrita com regra pré-registrada.

Nenhuma das três bloqueia a Fase A (censo e download) nem as Tasks 2 a 5 da auditoria de datas. As três bloqueiam transcrição substantiva e classificação em lote.

## Ordem recomendada dos próximos passos

1. Resolver o achado A (decisão de design pequena, mexe só em `db.py` e num teste).
2. Executar as Tasks 2 a 5 do plano da auditoria de datas, incorporando o achado C na mesma passada; meta verificável: 67 observadas, 67 dias, 0 imputadas, e as duas "datas duplicadas" do relatório desaparecem (eram erro de OCR, confirmado pelo manifesto).
3. Fase A gate-free (enumeração do censo 1907 a 1914 + download noturno), incorporando D.2 (contagem real de páginas) e E.1.
4. Achados B, D e E restantes entram como migração 002 e ajustes de spec antes da Fase B.
