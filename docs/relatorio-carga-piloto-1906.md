# Relatório da carga piloto de 1906

Data da execução: 16/07/2026

## Resultado

O contrato SQLite v2 foi materializado e a carga das fontes canônicas autorizadas foi executada em `dados/base/caixa_conversao.db`.

O banco passou:

- `PRAGMA user_version = 1`;
- `PRAGMA integrity_check = ok`;
- `PRAGMA foreign_key_check` sem linhas;
- reexecução idempotente, sem duplicação de objetos, obtenções, páginas, avaliações, transcrições ou datas.

## Cobertura materializada

| Item | Total |
|---|---:|
| PDFs canônicos | 67 |
| Objetos digitais | 67 |
| Edições lógicas | 67 |
| Páginas físicas | 450 |
| Páginas com avaliação inicial `not_assessed` | 450 |
| Páginas transcritas | 102 |
| Datas observadas | 45 |
| Datas imputadas | 0 |
| Datas não resolvidas | 22 |
| Dias civis distintos entre as datas observadas | 43 |
| TXT sem PDF canônico no recorte autorizado | 474 |

Todos os 67 PDFs são de O Paiz, BIB `178691`. Portanto, esta execução valida o contrato sobre um subconjunto de O Paiz. Ela não constitui ainda o piloto completo dos quatro jornais.

## Análises legadas

As 102 páginas transcritas contêm 630 artigos demarcados. Há JSON associado a 621 artigos; nove estão sem JSON. Entre os JSON associados, 474 são listas vazias `[]`.

As avaliações substantivas vigentes em nível de página ficaram assim:

| Resultado | Páginas |
|---|---:|
| `relevant` | 45 |
| `not_relevant` | 26 |
| `uncertain` | 17 |

Quatorze páginas transcritas não possuem artigo demarcado e não receberam avaliação substantiva inventada. Todas permanecem com a avaliação inicial de triagem `not_assessed`.

## Divergências encontradas nas fontes

1. O manifesto estimava oito a doze páginas por PDF. A distribuição real é: três PDFs com quatro páginas, 41 com seis, 20 com oito, dois com dez e um com doze.
2. Os marcadores de página usam três formatos: `PAGE 1`, `arquivo.pdf-PAGE1` e número da edição no lugar do número de página, como `PAGE 7819`. O último formato foi tratado como página 1, preservando o literal original.
3. `per178691_1906_08099.txt` contém duas marcações da página 1. Os blocos foram fundidos, preservando texto e ordem dos artigos.
4. Há 45 datas observadas, mas somente 43 datas civis distintas. Dois pares exigem auditoria manual antes de serem interpretados como múltiplas edições:
   - `1906-07-10`: `per178691_1906_07950` e `per178691_1906_07959`;
   - `1906-09-20`: `per178691_1906_08022` e `per178691_1906_08028`.
5. O piloto não preserva o raster exato entregue ao produtor legado. `physical_pages.visual_sha256` e `transcriptions.input_visual_sha256` usam o hash do PDF contêiner, enquanto `page_id` e `#page=N` identificam a página. Essa granularidade deve ser substituída por hash do raster em novas execuções.
6. Os 474 TXT sem PDF canônico incluem edições de O Paiz fora do subconjunto de 67 e as transcrições dos demais jornais. Eles não foram materializados como páginas porque a carga exige objeto físico verificável.
7. A importação local não preserva a resposta HTTP original. As obtenções bem-sucedidas têm `http_status = NULL`; caminho, hashes, tamanho e número de páginas permanecem obrigatórios.
8. As transcrições preservam o bloco lógico `PAGE_METADATA`, mas não coordenadas visuais do masthead. `evidence_region_json` registra página, marcador e TXT de origem. Novas execuções devem acrescentar coordenadas do raster.
9. Alguns TXT da Gazeta concatenam números de edições distintas no mesmo arquivo. O parser interrompe a carga nesses casos, em vez de fundir edições silenciosamente. Eles deverão ser separados quando os PDFs correspondentes forem incorporados.

## Cardinalidades observadas

- 67 objetos digitais estão ligados a 67 edições lógicas.
- Todos os vínculos usam o papel `principal`.
- 45 edições estão `confirmed` por data observada.
- 22 edições permanecem `provisional`.
- Não foi possível identificar suplementos, extraordinárias, duplicatas de digitalização ou PDFs com mais de uma unidade lógica apenas com estas fontes.
- Os dois dias com duas datas normalizadas não podem ser classificados como múltiplas edições sem conferência visual.

## Tabelas sem dado real no piloto

- `circulation_assessments`: não há evidência independente de circulação por dia.
- `current_circulation_assessments`: não há avaliação de circulação selecionável.
- `search_campaigns`: as fontes não preservam a campanha de busca original.
- `search_runs`: não há resposta bruta, manifesto nem metadados completos das buscas.
- `current_search_runs`: não existe execução de busca importável.
- `search_hits`: os TXT não preservam cada hit bruto e sua identidade.
- `search_hit_resolutions`: não há vínculo auditável entre hit, objeto, edição e página.
- `current_search_hit_resolutions`: não existem resoluções importáveis.
- `date_record_sources`: a carga não realizou imputações nem usou fontes auxiliares.
- `phase_schemes`: o esquema de fases está fora das três fontes autorizadas.
- `phase_definitions`: não há definição versionada de fases nas fontes.
- `current_phase_schemes`: não há esquema de fases selecionável.
- `recall_audits`: o piloto não contém desenho probabilístico de recall.
- `recall_strata`: não há frame, estratos, sementes ou tamanhos amostrais preservados.
- `recall_sample_units`: não há sorteio reproduzível de edição-dias.
- `recall_reference_labels`: não há leitura integral de referência vinculada a amostra.
- `recall_gate_results`: não há estimativa e intervalo de confiança reproduzíveis.
- `classification_runs`: os JSON preservam resultados por artigo, sem execução válida em nível de edição.
- `edition_classifications`: a unidade dos JSON legados não satisfaz a classificação por edição.
- `classification_inputs`: não há classificação válida de edição a que vincular transcrições.
- `current_edition_classifications`: não há classificação de edição selecionável.
- `audit_cases`: as fontes autorizadas não identificam formalmente os casos P0.
- `audit_findings`: não há reavaliação auditável dos casos P0.
- `current_audit_findings`: não existem achados de auditoria selecionáveis.

## Próximo portão

Antes de expandir a coleta ou gastar com transcrição:

1. Revisar independentemente o schema, o módulo de acesso e o carregador.
2. Conferir visualmente os dois pares de datas duplicadas e uma amostra dos 45 mastheads resolvidos.
3. Completar os PDFs canônicos de O Paiz e incorporar PDFs dos outros três jornais.
4. Reexecutar a carga para medir cardinalidades de objeto, edição, suplemento e extraordinária no piloto completo.
5. Só então usar o piloto completo para decidir edição-dia estrita ou múltiplas manifestações editoriais.
