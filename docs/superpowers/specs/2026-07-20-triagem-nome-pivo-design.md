# Triagem por nome (medida pivô): design e contrato

Data: 2026-07-20. Autor: Claude (sessão Opus, brainstorming com Pedro), aprovação de
escopo por Pedro na mesma sessão.

## Estatuto metodológico e propósito

Esta é a **medida pivô** decidida em `docs/decisoes.md` (2026-07-19, "Detecção de
stance por LLM vira possibilidade contingente"): a primeira e mais barata medida da
rodada metodológica, custo zero de token. Ela não classifica posição, não faz stance
detection, não usa LLM. Mede uma coisa só: **onde, no censo inteiro, o nome "Caixa de
Conversão" aparece no texto embutido (OCR da BN)**, agregado a objeto digital e ano
(ver achado abaixo sobre por que não é edição-dia/fase no censo inteiro).

O número que ela produz, R (objetos relevantes, proxy de dias relevantes) por jornal
e ano, decide a próxima bifurcação estratégica: se R couber nas horas de codificação
humana de Pedro (15-20h/semana, ~2 meses), a posição é codificada à mão e a LLM para
stance vira opcional; se não couber, a LLM ou um classificador supervisionado ganha
lugar para cobertura, validado contra o padrão humano. A LLM segue em uso,
independente do resultado, em tarefas que não são stance (recuperação, transcrição
de páginas ilegíveis, extração de atores).

Não é a triagem definitiva de produção do corpus. Não implementa o gate de recall
pré-registrado (LCB unilateral 95% ≥ 0,90 por jornal-fase, `docs/decisoes.md`
2026-07-17 item 2), que exige a amostra de referência humana estratificada (artefato
4/5 da rodada, ainda não desenhada). Esta passada usa o único padrão-ouro disponível
hoje, o gabarito humano do piloto 1906, só para calibração diagnóstica.

**Achado que redefine a unidade de agregação (verificado no banco real nesta
sessão):** a camada de identidade de edição-dia (`edition_days`, `date_records`,
`v_current_edition_dates`) só foi construída para os 67 objetos do piloto 1906;
`phase_definitions` está vazia (0 linhas). O censo inteiro (11.960 objetos, 117.705
páginas) tem a camada de texto completa mas não tem data nem fase resolvidas.
Resolver isso para o censo inteiro é um projeto à parte (estender
`pipeline/base/extrai_texto.py`-equivalente para datas a todos os objetos), fora do
escopo desta medida pivô, cujo valor está em ser rápida e barata. Decisão de Pedro
nesta sessão: **agregar por `digital_object` e ano no censo inteiro** (proxy razoável
para edição-dia, validado 1:1 no piloto: 67 objetos = 67 edições-dia = 67 dias civis
distintos, `docs/relatorio-carga-piloto-1906.md`); a agregação fina por edição-dia
estrita e por fase roda só dentro do piloto 1906, onde a camada de identidade já
existe, e serve à calibração, não ao relatório do censo inteiro.

## Decisão de construto: ancorar no nome, não em lista de termos de debate

Discutida e fechada com Pedro nesta sessão. A regra de casamento é **o nome "caixa
de conversão"**, normalizado e tolerante a ruído de OCR na frase (acento e cedilha
caídos, hifenização de quebra de coluna, espaçamento irregular). "Caixa de
Amortização" é excluída explicitamente (instituição distinta, o fundo de
amortização).

**Não implementado nesta passada, gancho para depois:** uma lista de termos do
debate cambial mais amplo (câmbio ao par, estabilização do câmbio, conversibilidade
a tantos dinheiros) que ampliaria R para além do nome — Pedro considera muito
provável que todo o debate cambial/padrão-ouro seja substantivamente adjacente ao
tema, já que a Caixa é o mecanismo que o opera; um artigo que discute a política sem
citar o nome ainda é material que interessa. Essa camada 2 fica para uma sessão
futura, com dois cuidados já registrados para quando for desenhada:

1. **Split para evitar vazamento.** Minerar termos candidatos num subconjunto de
   trechos e medir precisão/recall noutro, nunca nos mesmos.
2. **Presumir adjacência, validar depois.** Ao contrário do costume de exigir
   precisão termo a termo antes de incluir, a orientação de Pedro é presumir que o
   debate cambial/padrão-ouro é adjacente e confirmar por amostragem, não excluir por
   suspeita de falso positivo a priori. Consequência a discutir na ocasião: isso move
   o denominador de "posição sobre a Caixa" para "participação no debate monetário",
   o que pode ganhar cobertura ou diluir o objeto: decisão de desenho, não desta
   spec.

As páginas que o nome pega nesta passada são o terreno natural para minerar os
termos candidatos da camada 2 (co-ocorrência com o nome); as edições relevantes do
gabarito 1906 que o nome não pega são o teste natural do que a lista recuperaria.
Este design deixa esse gancho registrado, não implementado.

## O que ela produz

1. **Manifesto por página**, registro positivo sempre (nunca ausência inferida):
   hit ou não-hit, span casado, versão da regra, referência à extração de texto.
2. **Relatório do censo inteiro**: R (objetos relevantes) e S (objetos triados) por
   jornal e ANO (não fase, ver achado acima); projeção de horas de codificação
   humana a partir de R.
3. **Relatório de calibração, restrito ao piloto 1906**: R/S por edição-dia estrita
   e por fase (onde data/fase já estão resolvidas), recall e amostra de precisão
   contra o gabarito humano.

## Componentes

Unidades pequenas, cada uma testável isoladamente:

- **`pipeline/triagem/regra_nome.py` — preditor de triagem** (função pura, sem I/O).
  Recebe uma string de texto de página, devolve lista de spans casados (offset,
  texto casado, contexto). Não sabe nada de banco, célula ou fase. Aqui moram os
  testes de corner case de OCR.
  - Normalização: casefold, remoção de acento/cedilha/til (NFKD + strip de
    combining marks), colapso de espaço múltiplo, rejunção de hifenização de quebra
    de linha (`conver-\nsão` → `conversão`) antes do casamento.
  - Casamento: regex tolerante sobre o texto normalizado, ancorada em
    `caixa\s+de\s+convers[aã]o` já sem diacríticos (a normalização já removeu),
    permitindo 0-2 caracteres de ruído entre tokens (erro comum de OCR: "caiva",
    "convcrsão"). Rejeita "caixa" ou "conversão" isolados. Rejeita "caixa de
    amortiza[çc][aã]o" mesmo com prefixo textual comum.
  - Versão da regra pinada como string de protocolo
    (`triagem/nome-caixa-conversao 1.0.0`), presente em todo registro de saída.

- **`pipeline/triagem/db_leitura.py` — leitor da camada de texto**. Consulta somente
  leitura sobre `v_current_page_texts` (migração 003) e `physical_pages.object_id →
  digital_objects` para resolver bib/jornal/ano (`digital_objects.source_year`),
  unidade padrão do censo inteiro. Só quando o escopo é o piloto 1906, resolve
  adicionalmente a cadeia `digital_objects → edition_object_links → edition_days` e
  `v_current_edition_phases` para a fase, usada apenas em `calibra_1906.py`. Cego à
  origem do objeto (varredura/somente_indice/recuperacao_manual): a flag de origem
  não entra na regra de casamento, só no relatório final, no espírito da flag cega de
  `docs/decisoes.md` (2026-07-18, item 4), embora o teste de margem de 5pp em si
  fique para a triagem de produção.

- **`pipeline/triagem/calibra_1906.py` — calibração no piloto**. Compara os hits do
  preditor, restritos às páginas de objetos do piloto 1906, contra o gabarito
  (`dados/piloto_1906/json*_1906/*_classificacao_holistica.json`). Aqui, e só aqui,
  a agregação é por edição-dia estrita e por fase, porque é o único recorte com data
  e fase resolvidas no banco. Duas métricas distintas, não uma:
  - **Recall contra os positivos do gabarito**: das edições que o piloto codificou
    com menção/posição (não "No Relevant Mentions"), quantas a regra por nome
    sinaliza como relevantes. Perda aqui é sinal concreto de quanto a camada 2
    (lista de termos) recuperaria.
  - **Precisão por amostra visual**, priorizando as ~280 edições que o piloto
    classificou "No Relevant Mentions": se a regra por nome achar menção real
    nessas edições, é evidência direta de que o método antigo (busca de hits da BN)
    subcontou, a falha de origem que o redesenho em camadas corrige. Os negativos
    do gabarito não são verdade limpa (vêm de busca, não de leitura de toda
    página), então não entram como denominador de precisão sem inspeção humana.

- **`pipeline/triagem/roda_censo.py` — runner do censo**. Aplica o preditor a todas
  as páginas com `result_status = 'ok'` (e conta `empty`/`error` à parte, nunca como
  não-hit) das ~117.705 da camada de texto. Agrega hit de página a hit de
  **objeto digital** (relevante se qualquer página do PDF bate; proxy para
  edição-dia, ver achado acima) e emite o manifesto.

- **`pipeline/triagem/relatorio_triagem.py`**. Agrega o manifesto a R/S por
  jornal-ANO (censo inteiro), no molde de `pipeline/base/relatorio_censo.py`, mais
  a seção de calibração fase-a-fase restrita ao piloto 1906 (saída de
  `calibra_1906.py`) e a projeção de horas de codificação (R × minutos/edição
  estimados, faixa, não ponto único).

## Fluxo de dados

```
v_current_page_texts (texto por página, camada 003)
        │
        ▼
regra_nome.py (função pura: texto → spans)
        │
        ▼
roda_censo.py: decisão positiva por página
        │  (agrega: relevante se qualquer página do OBJETO bate — proxy p/ edição-dia)
        ▼
objeto relevante / não-relevante, por bib-ano
        │
        ├──► manifesto (dados/triagem/triagem_nome_{bib}_{ano}.csv)
        │
        └──► relatorio_triagem.py ──► docs/relatorio-triagem-nome.md
                                       (R/S por jornal-ano no censo inteiro,
                                        + seção de calibração do piloto 1906,
                                        faixa de horas projetadas)

calibra_1906.py roda à parte, mesmo preditor, escopo restrito ao piloto 1906
(único recorte com edição-dia e fase resolvidas), agrega por edição-dia/fase,
compara contra o gabarito humano.
```

## Saída e proveniência

- **Manifesto**: `dados/triagem/triagem_nome_{bib}_{ano}.csv`, uma linha por
  página, colunas: `bib`, `source_identifier`, `page_number`, `hit` (0/1),
  `n_matches`, `primeiro_span_texto`, `primeiro_span_offset`, `regra_versao`,
  `extraction_run_id` (rastreia a extração de texto de origem), `result_status`
  (herdado da camada de texto: `ok`/`empty`/`error`, para nunca confundir
  "sem hit" com "sem texto para triar"). Texto leve, domínio público: entra no git,
  como os manifestos de censo e texto embutido.
- **Relatório**: `docs/relatorio-triagem-nome.md`.
- Regra pinada como protocolo determinístico (`triagem/nome-caixa-conversao
  1.0.0`), re-rodável byte-idêntico. Não persiste em banco nesta passada (sem
  migração de schema): o manifesto versionado no git é a proveniência. Promoção a
  tabelas no banco (`triage_runs`, `page_triage_decisions`, no padrão de
  `text_extraction_runs`/`page_text_extractions`) fica para quando esta virar a
  triagem de produção, decisão futura de Pedro.

## Tratamento de erro e cobertura

Página com `result_status` `empty` ou `error` na camada de texto entra no manifesto
com `hit = 0` mas **não conta como triada negativa**: é registro positivo de
"sem texto disponível para triar", nunca inferida como ausência de menção. O
relatório expõe, por célula, a fração de páginas sem texto (`empty` + `error`)
separada da fração triada com sucesso, para que R/S nunca seja silenciosamente
enviesado por buraco de OCR. Isso ecoa o espírito do S da cascata K/E/D/S/R/C
(`docs/decisoes.md`, 2026-07-18 item 2), agora em termos de objeto: S = objetos
completamente triados, ou seja, com todas as páginas em `result_status = 'ok'`.
Dentro do piloto 1906, `calibra_1906.py` reporta o S homólogo em edição-dia, o
grão que a cascata original define.

Objeto sem obtenção vigente `ok` (o único hoje: `per178691_1913_10408`,
`invalid_pdf`) fica fora do universo, como já documentado na camada de texto.

## Testes (TDD)

`regra_nome.py` isolado, sem banco:
- Casamento direto ("Caixa de Conversão", maiúsculas/minúsculas variadas).
- Ruído de OCR: acento caído ("Caixa de Conversao"), cedilha/til perdidos,
  1-2 caracteres trocados por erro de OCR plausível.
- Hifenização de quebra de linha/coluna ("conver-\nsão").
- Espaçamento interno irregular (espaço duplo, tab).
- Rejeição: "Caixa de Amortização", "conversão" isolada, "caixa" isolada,
  "Caixa Econômica".
- Múltiplos matches na mesma página (conta `n_matches` corretamente).

`roda_censo.py`, com banco de teste:
- Agregação página→objeto (uma página basta para marcar o objeto relevante).
- `empty`/`error` não vira falso não-hit nem falso hit.
- Determinismo: mesma célula, duas execuções, manifesto byte-idêntico.

`calibra_1906.py`, com banco de teste restrito ao piloto:
- Agregação página→edição-dia via `edition_object_links`, distinta da agregação
  por objeto usada no censo inteiro (teste que prova que os dois caminhos não se
  confundem, já que 1906 tem os dois disponíveis).
- Fixture pequena com gabarito sintético (2-3 casos conhecidos positivos e
  "No Relevant Mentions"), confirma que a métrica de recall e a de precisão são
  calculadas sobre conjuntos distintos (não confundir denominador).

## Não-objetivos

Sem lista de termos de debate cambial (camada 2, gancho registrado acima, não
implementada). Sem gate de recall formal (LCB 0,90, exige amostra de referência
estratificada). Sem persistência em banco/migração de schema. Sem qualquer
julgamento de posição, stance ou extração de afirmações. Sem uso de LLM em
qualquer etapa.
