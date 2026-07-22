# Decomposição de registro dos matches (medida de substância): design e contrato

Data: 2026-07-21. Autor: Claude (sessão Opus, brainstorming com Pedro),
aprovação de escopo e das refinações por Pedro na mesma sessão.

## Estatuto metodológico e propósito

Segunda medida da rodada metodológica, na sequência da triagem por nome
(`docs/superpowers/specs/2026-07-20-triagem-nome-pivo-design.md`, já
implementada e rodada). É **piloto metodológico**, não produção: separa, de
forma barata e determinística sobre o OCR embutido que já temos, o
engajamento editorial com a Caixa da menção mecânica de rotina. Custo zero de
token, sem LLM, sem julgamento de posição/stance.

Enquadramento obrigatório (`docs/contexto-debate-metodologico-mensuracao.md`):
esta etapa incorpora seleção substantiva de relevância, então NÃO é neutra e
é piloto até aprovação de Pedro. A **definição do construto é de Pedro**; o
Claude propõe operacionalizações testáveis e testes de refutação. Nada de
texto é descartado: a camada completa de OCR permanece intacta, o registro é
uma etiqueta reversível e versionada, uma VISTA sobre os matches.

## O que motivou (achado da triagem por nome)

A triagem por nome (`docs/relatorio-triagem-nome.md`) achou R = 6.354
edições-dia que nomeiam a Caixa, saliência global 0,53, com recall 0,948
contra o gabarito humano de 1906. Mas **R conta presença do nome, não
discussão**. A inspeção de ~32 edições mostrou que, nos anos de operação
(1907+), boa parte dos matches é o nome como dado de rotina: boletim diário
de movimento de ouro, escala de guarda militar ao prédio, telegrama. Em 1906
(Caixa ainda não operava) presença ≈ discussão, e a saliência é a mais baixa
(0,23-0,41); a subida para 0,79-0,84 em 1909-11 é em parte relevante artefato
de gênero textual, não intensificação de debate. Esta medida existe para
separar essas camadas e produzir denominadores defensáveis.

## Decisão de construto: três denominadores (Pedro)

Hierarquia oficial, decidida por Pedro:

1. **edições totais** (~11.960): a população de objetos digitais.
2. **edições que mencionam a Caixa, excluídos os incidentes** (dado limpo):
   a Caixa aparece como assunto reportado, não como endereço/prédio/pessoal.
3. **edições em que a Caixa é discutida de forma substantiva**: engajamento
   com a Caixa como questão, fora do reporte mecânico de rotina.

Ressalva de construto de Pedro, incorporada: o **tom geral do conteúdo
publicado sobre a Caixa, não só a voz editorial própria, compõe a reportagem
que o jornal fez da Caixa**. Por isso o denominador 2 (menção limpa) mantém o
reporte operacional de rotina como cobertura, e NÃO se tenta separar voz
própria de discurso reproduzido nesta medida (isso é a opção 3, adiada, exige
amostra humana). O reporte operacional só sai no denominador 3 (substantivo),
por ser mecânico e não-discursivo, não por ser reproduzido.

O R bruto de nome (6.354, ainda com incidentes) é reportado apenas como
diagnóstico do "antes da limpeza", para quantificar quanto era incidental.

## A taxonomia de registro (três etiquetas)

Cada match do nome recebe uma etiqueta pelo seu contexto local:

- **incidental**: a Caixa é local, prédio ou pessoal, não é o assunto da
  informação. Escala de guarda ("alferes Roque na caixa de conversão"),
  lista de repartições, nome próprio + cargo em nota administrativa
  ("ex-diretor da caixa de conversão completa anniversario"). Sai do
  denominador 2.
- **operacional_rotina**: reporte mecânico dos números de rotina da Caixa.
  Boletim de movimento, entradas/saídas de ouro, saldo do dia ("o movimento
  de hontem da caixa de conversão foi... entraram 50.238 libras"). Conta como
  cobertura (denominador 2), sai do denominador 3.
- **substantivo**: o balde residual, por padrão. Discussão, argumento,
  política, evento, avaliação, crítica, história. Não precisa ser definido
  positivamente; é o que sobra depois de reconhecer os dois gêneros
  estereotipados acima.

O telegrama NÃO é um registro; é um veículo. Um telegrama classifica-se pelo
conteúdo como qualquer outra menção: telegrama de números de movimento é
`operacional_rotina`, telegrama que reporta debate ou evento de política é
`substantivo`. Coerente com a ressalva de Pedro (cobertura reproduzida conta):
a forma de telegrama não subtrai nada por si.

**Base observacional atual: ~32 edições olhadas a olho** (7 positivos-
recuperados + 15 de O Paiz 1911 + 10 de Correio Paulistano 1913). É hipótese
semeada, não taxonomia validada. Daí o passo 1 abaixo.

## Componentes

Unidades pequenas, cada uma testável isoladamente.

- **Passo 1 — `pipeline/triagem/amostra_registro.py` (caracterização
  primeiro).** Antes de fixar detectores: amostra estratificada aleatória de
  matches (por jornal × ano, semente fixa), dumpa o contexto de cada um para
  CSV rotulável. Serve para (a) Pedro conferir se as três etiquetas são
  exaustivas e suficientes, (b) medir a distribuição real dos registros, (c)
  virar o conjunto de referência contra o qual os detectores são medidos.
  Tamanho fixado (2026-07-21): amostra estratificada por jornal × ano, ~12
  matches por célula, ~400 contextos no total (~35 células, Gazeta 1913 fora).
  Ajustável se a distribuição pedir. Sem esta amostra os detectores ficariam
  ancorados só nas ~32 edições.

- **`pipeline/triagem/classificador_registro.py` — classificador de registro
  (função pura, sem I/O).** Recebe o contexto normalizado de um match, devolve
  a etiqueta (`incidental` | `operacional_rotina` | `substantivo`) e qual
  detector disparou. Aqui moram os detectores determinísticos (regex de
  patente militar/repartições para `incidental`, template de boletim de
  movimento para `operacional_rotina`; o resto cai em `substantivo`) e os
  testes de corner case. Versão de protocolo pinada
  (`triagem/registro-caixa 0.1.0`), presente em todo registro de saída.

- **Integração ao manifesto da triagem.** A etiqueta de registro entra como
  coluna nova no manifesto por página (ou manifesto paralelo por match), sem
  quebrar o contrato existente. Reversível: o texto e o hit continuam
  intactos; a etiqueta é uma vista.

- **`pipeline/triagem/relatorio_registro.py`.** Os três denominadores por
  jornal-ano (totais, menção-limpa, substantivo) mais a decomposição da
  saliência em registros (empilhado por ano), no molde de
  `relatorio_triagem.py`. Mostra preto no branco quanto da subida de 1907+ é
  operacional e quanto é substantivo.

- **Calibração.** Estende `calibra_1906.py` (ou módulo irmão): os positivos do
  gabarito 1906 devem cair quase todos em `substantivo` (recall ~0,90+);
  reporta a mistura de registros por ano (incidental/operacional devem
  concentrar em 1907+).

## Fluxo de dados

```
matches da triagem por nome (spans + contexto, já existentes)
        │
        ├──► amostra_registro.py (passo 1): amostra estratificada → CSV
        │      rotulável → Pedro confere exaustividade e distribuição
        │
        ▼
classificador_registro.py (função pura: contexto → etiqueta + detector)
        │
        ▼
etiqueta por match ──► manifesto (coluna de registro)
        │
        ├──► relatorio_registro.py: 3 denominadores + decomposição por ano
        │
        └──► calibra: recall dos positivos 1906 em `substantivo`,
                       mistura de registros por ano
```

## Validação e refutação (pré-registrada)

- **Preservação de recall**: os positivos do gabarito 1906 devem cair quase
  todos em `substantivo`. Alvo: recall ~0,90+. Se caírem em rotina/incidental,
  o detector exagerou e afrouxa.
- **Teste do artefato de gênero**: `incidental` e `operacional_rotina` devem
  concentrar em 1907+ e ser raros em 1906. Se dispararem muito em 1906, estão
  errados (em 1906 a Caixa não operava, então não há boletim de movimento).
- **Checagem humana estratificada**: amostra de cada etiqueta, Pedro confere a
  acurácia. **Margem fixada por Pedro (2026-07-21): 5% no nível da EDIÇÃO**
  (não do match), avaliada nos dois registros mecânicos (incidental e
  operacional_rotina, que empurram o denominador substantivo). O nível da
  edição importa porque é o dos denominadores: a edição conta se qualquer
  menção sua é substantiva, então erro num match isolado raramente vira a
  edição; o risco concentra nas edições de menção única. **Cláusula de
  calibração**: 5% é alvo com calibração pela amostra do passo 1, não promessa
  cega. Se um registro não alcançar 5% barato, reporta-se a margem alcançada e
  decide-se por registro (aceitar a margem declarada, ou escalar só aquela
  fatia para instrumento mais caro). O gate mais informativo é o VIÉS LÍQUIDO
  no denominador (erros equilibrados se cancelam), não a acurácia crua por
  match. É o "vamos ver se vão ser acuradas e suficientes" operacionalizado.
- **Margem de suficiência**: se a amostra do passo 1 revelar um quarto gênero
  frequente não coberto pelas três etiquetas, a taxonomia se estende antes de
  qualquer contagem em escala.

## Saídas e proveniência

- **Manifesto**: coluna de registro adicionada por match/página, com o
  detector que disparou, em `dados/triagem/` (texto leve, domínio público,
  entra no git como os demais manifestos).
- **Amostra de caracterização**: `dados/triagem/amostra_registro_*.csv`
  (contextos sorteados, semente registrada) para rotulagem e auditoria.
- **Relatório**: `docs/relatorio-registro-substancia.md`.
- Regra pinada como protocolo determinístico (`triagem/registro-caixa
  0.1.0`), re-rodável byte-idêntico. Versão 0.x porque a taxonomia é hipótese
  até a validação da amostra; bump consciente quando estabilizar. Sem
  persistência em banco nesta passada.

## Testes (TDD)

`classificador_registro.py` isolado, sem banco:
- Boletim: os templates reais de movimento ("movimento de hontem da caixa de
  conversão... entraram X libras") → `operacional_rotina`.
- Escala de guarda: patente + repartições ("na caixa de conversão, alferes
  Servulo") → `incidental`.
- Telegrama classificado pelo conteúdo, não pela forma: telegrama de números
  de movimento → `operacional_rotina`; telegrama de debate/evento →
  `substantivo`. A dateline sozinha não subtrai.
- Discussão substantiva real (os exemplos recuperados: "crear a caixa de
  conversão e resgatar moeda fiduciaria") → `substantivo`.
- Menção que mistura palavra de boletim mas é discussão ("o movimento da
  Caixa foi criticado") → não pode virar `operacional_rotina` cegamente
  (corner case da falha registrada abaixo).
- Determinismo: mesmo contexto, mesma etiqueta.

Agregação e relatório, com banco/manifesto de teste:
- Objeto com um match incidental e um substantivo → conta no denominador 2 e
  no 3 (OR no nível do objeto, o registro mais forte manda).
- Os três denominadores por jornal-ano batem com contagens manuais numa
  fixture pequena.

## Não-objetivos

Sem detecção de voz própria vs reproduzida (opção 3, adiada, exige amostra
humana). Sem dicionário de vocabulário de debate como definição de substância
(opção 2, fica como vista estrita opcional DENTRO de `substantivo`, decisão
futura). Sem LLM. Sem descarte de texto. Sem julgamento de posição/stance.
Sem classificação de produção nem gate de recall formal. A escolha final do
denominador-estimando e a liberação em escala são de Pedro, com registro em
`docs/decisoes.md`.
