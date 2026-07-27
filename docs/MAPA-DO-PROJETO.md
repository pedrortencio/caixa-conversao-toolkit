# Mapa do projeto

**Escrito em:** 2026-07-27. **Para:** orientação rápida, sua ou de uma sessão
com contexto zero. Todos os números aqui foram medidos nesta data, não
lembrados.

Se você só tem dois minutos: o repositório é o **instrumento** (código,
manifestos, decisões); `C:\dados-caixa` é o **acervo** (123 GB de PDF e texto);
o banco costura os dois por ponteiro e hash. O gargalo do projeto não é técnico,
é o codebook das fases 2 a 4, que é redação sua.

---

## 1. No que consiste o repositório

Não é um repositório de código com dados anexos. É um **instrumento de medição
versionado**, e essa distinção governa o que entra e o que não entra no git.

Entra no git:

- o código do pipeline;
- os **manifestos**, que são o registro positivo de cada operação (o que foi
  baixado, o que deu 404, o que foi triado). Ausência nunca é inferida do
  silêncio: cada não-achado é uma linha gravada;
- as **decisões metodológicas** (`docs/decisoes.md`), append-only, incluindo os
  pré-registros feitos antes de olhar resultados;
- os **pareceres** e seus hashes de congelamento (`colaboracao/`), que provam
  que uma opinião foi emitida antes de conhecer a outra;
- as amostras tratadas, leves.

Não entra: PDF bruto, camada de texto, banco. São grandes, reprodutíveis a
partir dos manifestos, e vivem em `C:\dados-caixa`.

**Tamanho:** 58,3 MB rastreados em 7.536 arquivos; `.git` com 18 MB. É um repo
enxuto. Dos 7.536 arquivos, 7.153 (95%) são o piloto de 1906, que é herança e
domina a contagem sem pesar em bytes.

## 2. Estrutura das pastas

```
caixa-conversao-toolkit/
├── CLAUDE.md              instruções permanentes (sempre em contexto)
├── AGENTS.md              o equivalente para o Codex
├── docs/                  42 documentos
│   ├── MAPA-DO-PROJETO.md este arquivo
│   ├── decisoes.md        registro append-only, 68 KB, a fonte da verdade
│   ├── codebook-fases.md  ESQUELETO. o gargalo do projeto
│   ├── retomada-2026-07-26.md   estado da última sessão
│   ├── relatorio-*.md     8 relatórios de etapa
│   └── superpowers/       specs (8) e planos (6)
├── pipeline/              o instrumento
│   ├── scraper/           enumeração e download da Hemeroteca
│   ├── base/              banco, migrações, censo, portão de 1906
│   ├── triagem/           regra de nome, calibração, amostragem
│   ├── analise/           qualidade de OCR, Fightin' Words
│   ├── retrospecto/       Jornal do Commercio (exploratório)
│   └── prompts/           prompts versionados (são instrumento de medição)
├── dados/                 só o leve e versionado
│   ├── base/              caixa_conversao.db (127 MB, gitignored)
│   ├── censo/             manifestos de varredura e recuperação
│   ├── triagem/           manifestos de triagem + planilha de rotulagem
│   ├── piloto_1906/       herança do piloto (7.153 arquivos)
│   └── retrospecto_jc/    seções extraídas do JC
├── colaboracao/           protocolo Claude-Codex
│   ├── manifestos/        o que foi despachado
│   ├── pareceres/         as opiniões, congeladas e hasheadas
│   └── registros/         JSONL de cada invocação
├── tests/                 191 testes
├── artigo/                a escrita
└── .claude/               o toolkit (ver seção 4)
```

O acervo pesado está em `C:\dados-caixa`, com um `LEIAME.md` próprio na raiz.

## 3. Os dados que já coletamos

A cadeia é **PDF bruto → camada de texto → amostras tratadas**, e cada etapa
tem manifesto próprio.

### Etapa 1: PDFs originais (Fase A, completa)

| Jornal | bib | Edições | 1906-1914 |
|---|---|---|---|
| O Paiz (RJ) | 178691 | 3.087 | completo |
| Correio da Manhã (RJ) | 089842 | 3.240 | completo |
| Correio Paulistano (SP) | 090972 | 3.128 | completo |
| Gazeta de Notícias (RJ) | 103730 | 2.505 | sem 1913 |
| Jornal do Commercio, Retrospecto | 180688 | 9 anuais | completo |

**11.969 arquivos, 119,2 GB.** O censo cobre 11.960 objetos digitais e 117.705
páginas. A Gazeta de 1913 não existe em acervo nenhum, o que está declarado na
cascata como ausência, sem imputação. Sobram 22 ausências terminais (404
confirmados em duas observações) e 1 PDF corrompido no host.

Isso **não** é o censo das edições publicadas. É o censo do acervo digital
identificável e recuperável segundo a fotografia datada das fontes da BN, feita
em 18/07/2026. A distinção está pré-registrada e precisa aparecer no texto.

### Etapa 2: camada de texto (completa)

Descoberta importante de 18/07: os PDFs da BN **já trazem OCR embutido**, então
a leitura do corpus inteiro custou zero token.

**117.703 páginas com texto, 4,25 GB, 4,32 bilhões de caracteres.** Zero erro
de extração no corpus inteiro (117.703 ok, 2 páginas vazias registradas
positivamente). Determinismo provado: o manifesto do piloto foi regenerado
byte-idêntico.

Ressalva medida: o OCR é sujo e o ruído **varia por célula**. O Paiz vai de
4,84% de ruído em 1909 a 14,33% em 1906, três vezes. Comparações entre anos ou
entre jornais estão confundidas pela digitalização, e isso já derrubou uma
justificativa de análise.

### Etapa 3: amostras tratadas

- **Triagem por nome:** 8.331 páginas do corpus mencionam "Caixa de Conversão",
  por regra tolerante a ruído de OCR, sem LLM e sem julgar posição.
- **Medida pivô:** o subcorpus substantivo é estimado entre **3.054 e 3.758**
  peças. É o número que decide se a codificação de posição pode ser humana ou
  precisa de LLM.
- **Rotulagem de registro:** 468 itens `keep`, 453 rotulados em três classes
  (substantivo, operacional_rotina, incidental). É o eixo que separa editorial
  de boletim de movimento.
- **Piloto de 1906:** 426 itens de gabarito, herança do trabalho manual.
- **Retrospecto do JC:** 136 páginas, 748 mil caracteres, das seções monetárias
  anuais. Estatuto no desenho ainda em aberto.

### Backup

`G:\My Drive\caixa-conversao`, por robocopy, conferido em 11.960 objetos.

## 4. As ferramentas de IA e como se usam

São três camadas, e a diferença entre elas é **o quanto você pode confiar que
vão agir**. Foi essa confusão que fez skill virar decoração.

| Camada | Confiabilidade | Onde vive |
|---|---|---|
| Hook e comando | Determinística. O harness executa. | `.claude/hooks/`, `.claude/commands/` |
| CLAUDE.md | Sempre em contexto. | raiz do repo |
| Skill | Discricionária. O modelo carrega se casar a descrição. | `.claude/skills/` e plugins |

**Regra que não pode falhar não pode morar em skill.**

### Claude Code (esta sessão)

Lidera código e arquitetura. Ferramentas próprias do projeto:

- **Skills:** `pipeline-hemeroteca` (rodar ou alterar o pipeline),
  `escrita-academica` (qualquer texto acadêmico, e é ela que proíbe travessão),
  `parecer-codex` (despachar trabalho ao Codex), `text-as-data` (trabalho
  estatístico sobre a base de classificações). Esta última **nunca disparou e
  não pode disparar**, porque a base de classificações ainda não existe.
- **Agente:** `revisor-metodologico`, para crítica de rascunho.
- **Comandos (novos):** `/regressao-1906` roda o portão; `/suite` roda os 191
  testes.
- **Hook (novo):** `gate_lote_pago.py` barra as etapas pagas enquanto o portão
  de 1906 não passar.
- **Plugins:** superpowers, humblepowers, engineering-discipline,
  session-workflow, skill-creator, github.

### Codex (via wrapper)

Lidera auditoria metodológica e acadêmica. **Nunca é invocado à mão**: sempre
por `scripts/invoca-codex.ps1`, que garante encoding, isolamento, registro em
JSONL e proveniência. Quem implementa um artefato não o audita. Em decisão de
nível crítico o parecer do Claude é **congelado e hasheado antes** do despacho,
para que a concordância entre os dois não seja contaminada.

### Gemini (planejado, não implementado)

Seria a camada de anotadores em lote (`pipeline/anotadores/`), com orçamento de
cerca de R$415. **Nunca rodou, custo até hoje é zero.** E está em questão: a
decisão de 19/07 rebaixou o uso de LLM para detecção de posição a uma pergunta
empírica, com o ônus da prova do lado da LLM. A saliência e a exposição já são
respondíveis sem nenhuma LLM.

## 5. As exceções do portão de 1906, explicadas

Você disse que não entendeu. É o seguinte.

O piloto de 1906 codificou 426 edições à mão. Elas são o **gabarito**: se o
pipeline novo não reencontra o que a mão achou, alguma coisa está errada. O
guardrail do CLAUDE.md diz que nenhum lote pago roda antes de passar essa
conferência.

Hoje o pipeline reencontra **422 das 426**. Faltam quatro:

| Jornal | Edição |
|---|---|
| Correio da Manhã | 1869 e 1870 |
| Correio Paulistano | 15276 |
| Gazeta de Notícias | 78 |

Essas quatro **não são bug**. São edições que o servidor de PDF da BN devolve
404 de verdade, confirmado em duas observações separadas. O piloto as obteve à
mão pelo DocReader, que é uma rota que o pipeline não tem.

Aí está o problema que o pré-registro de 18/07 resolveu: um portão que exige
426 de 426 **nunca abriria**, e você acabaria desligando o portão. Então o
critério virou outro: cada item do gabarito precisa de uma explicação
registrada, e "ausência terminal documentada com fonte" é uma explicação
válida. O que não vale é item sem explicação nenhuma.

E tem a trava: **a lista de exceções só conta se você aprovar por escrito.**
Sem isso, um modelo apressado poderia declarar exceção qualquer ausência
inconveniente e abrir o portão sozinho.

Deixei a lista pronta em `pipeline/base/manifests/excecoes_portao_1906.json`
com `aprovado_por: null`. Enquanto estiver assim, o portão reprova e o hook
barra lote pago. Para fechar, você precisa de duas coisas:

1. **Conferir a classe de cada item.** As duas do Correio da Manhã podem não
   ser "ausência terminal": no DocReader elas existem como B01869 e B01870, sem
   variante A. Se forem duas manifestações do mesmo dia, a classe correta é
   `manifestacao_coalescida`, que é uma afirmação diferente sobre o corpus.
2. **Preencher `aprovado_por` e `aprovado_em`.**

Não preenchi por você de propósito. Um modelo se auto-aprovando é exatamente a
falha que o portão existe para impedir.

## 6. O que falta decidir

1. **Codebook das fases 2 a 4.** Redação sua. Bloqueia protocolo humano, que
   bloqueia padrão-ouro, que bloqueia benchmark e a escolha do instrumento.
   Nenhum modelo faz por você.
2. **As quatro exceções do portão**, acima.
3. **Manifesto de 25/07** sobre a escolha do instrumento de cobertura,
   aguardando sua autorização de despacho, com o parecer do Claude já congelado
   (sha256 `4113ffd8...`).
4. **Rotular cerca de 40 descartes sorteados**, uma tarde de trabalho, que
   converte a medida pivô de "calibrada num ano só" para "com viés medido".
