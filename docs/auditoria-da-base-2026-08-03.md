# Auditoria da base tratada

**Feita em:** 2026-08-03. **Escopo:** verificar se as camadas de dados estão
consumíveis, com número medido nesta data e não lembrado. **Custo:** zero token
de API.

Comandos que sustentam cada número estão no fim do documento.

## 1. Veredito por camada

| camada | estado | número medido |
|---|---|---|
| Censo e PDF bruto | pronta | 11.960 objetos digitais, 117.705 páginas, backup conferido |
| Texto embutido | pronta | 117.705 registros vigentes, zero erro de extração |
| Triagem por nome | pronta | 8.331 páginas com menção, zero arquivo de texto faltando no disco |
| Banco | pronta | `integrity_check` ok, `user_version` 3, 47 tabelas |
| Rotulagem de registro | pronta | 468 `keep`, 453 rotulados em três classes |
| Banqueiros externos | pronta nesta sessão | 1.709 achados, e os 10 exemplares curados voltaram para arquivo |
| Catálogo de debates | pronta, é piloto | 48 janelas, 98 registros do Claude e 83 do Codex, citação conferida |
| Documentos Parlamentares | dados prontos, instrumento ausente | 1.152 páginas, 660 menções do nome, zero erro |
| Fichas de leitura | vazias | 185 linhas, zero campo de leitura preenchido |
| Suíte de testes | verde | 256 testes, mais 47 subtestes |
| Portão de 1906 | reprovado | 422 de 426, quatro itens sem classe ratificada |

## 2. O que impede consumo, em ordem de gravidade

### 2.1 A camada corrigida dos Documentos Parlamentares não é reprodutível

`dados/texto_corrigido/fontes_parlamentares/` tem 1.152 páginas corrigidas, com
hash de entrada e de saída, contagem de operações e relatório de qualidade. O
código que produziu esses arquivos não existe no repositório. O plano de
2026-08-01 prevê `pipeline/base/correcao_texto_parlamentar.py` e
`pipeline/base/gera_texto_corrigido.py`, e os dois estão com todos os passos em
aberto. A extração bruta também não tem script versionado, apenas o registro de
que usou `pypdf 6.10.0` com `extract_text` padrão.

Isso contraria a regra que governa o repositório, que é ser o instrumento. Hoje
existe produto sem instrumento: ninguém consegue regerar a camada, conferir o
replay determinístico que a especificação exige, nem saber que regra produziu
uma correção específica.

Consequência prática imediata: a camada serve para ler e para pesquisar, mas
nenhum número tirado dela deve entrar em texto antes de a rotina existir e o
replay passar.

### 2.2 A validação de busca da camada corrigida tem um termo vazio

O relatório de qualidade compara contagens antes e depois da correção para sete
termos. Um deles, `câmbio`, dá 0 nos dois lados. A grafia da época é `cambio`,
sem acento, então essa linha passou sem medir nada. O termo mais central do
corpus ficou de fora da verificação.

Na mesma tabela, `Caixa de Conversão` sobe de 520 para 606 ocorrências depois da
correção, porque a correção rejunta palavras partidas na quebra de linha. O
número é plausível e até desejável, mas confirma que a camada bruta e a corrigida
não são intercambiáveis para contagem. Qualquer série tem de declarar de qual
das duas saiu.

### 2.3 O portão de 1906 continua reprovado

```
itens do gabarito      : 426
reproduzidos no censo  : 422
exceções aceitas       : 0
inexplicados           : 4
lista de exceções      : NÃO RATIFICADA
```

Os quatro são Correio da Manhã 1869 e 1870, Correio Paulistano 15276 e Gazeta de
Notícias 78. A lista existe em
`pipeline/base/manifests/excecoes_portao_1906.json` com `aprovado_por: null`.
Enquanto estiver assim, o hook barra qualquer etapa paga. A decisão é sua, e um
modelo não pode se auto-aprovar exceção.

### 2.4 As fichas de leitura estão vazias

`dados/leitura/fichas_leitura.csv` tem 185 peças sorteadas, com identificação e
`forma` e `registro` pré-preenchidos. Os quinze campos que dependem da leitura
estão zerados nas 185 linhas: `voz`, `objeto_politica`, `posicao_declarada`,
`argumento`, `atores_nomeados`, `citacao_ancora`, `confianca`, `minutos`.

Isso confirma o gargalo já registrado. O codebook das fases 2 a 4 depende dessa
leitura, e nenhuma medida de posição avança sem ele.

### 2.5 Três dias de trabalho existem só nesta máquina

`git status` traz 119 itens fora do commit, entre eles o piloto de catalogação
inteiro (48 manifestos, 48 registros de invocação, quatro JSONL de anotação), a
camada dos Documentos Parlamentares, a nota sobre o referente argentino e o
relatório do piloto. O último commit é de 2026-08-01 e só traz documentos.

Não commitei nada, conforme a regra de que o git anda ao seu comando. Registro
aqui porque o volume acumulado já é de perda relevante se o disco falhar.

### 2.6 O mapa do projeto está desatualizado

`docs/MAPA-DO-PROJETO.md` tem data de 2026-07-27 e não conhece o catálogo de
debates, os Documentos Parlamentares nem a sondagem de banqueiros. Também diz
que a skill `text-as-data` "nunca disparou e não pode disparar", o que continua
verdadeiro para o objeto 2 mas já não descreve o estado do objeto 1. Atualizei o
cabeçalho e as seções 3, 4 e 6.

## 3. O que corrigi nesta sessão

**Exemplares de banqueiros externos.** O LEIAME dizia que os trechos curados em
26/07 "não estão em arquivo: foram entregues no chat". Chat não é manifesto.
Reconstruí a tabela a partir de `achados.csv`, que guardou localizador, termo,
variante de OCR e contexto de 280 caracteres. Saiu
`dados/banqueiros_externos/exemplares_curados.csv`, com 11 linhas para os 10
trechos, porque uma das páginas casa dois termos distintos. O exemplar do
Retrospecto do Jornal do Commercio não entra, porque o JC não está no censo.

## 4. O que depende de você

1. Ratificar ou recusar as quatro exceções do portão de 1906, por escrito no
   manifesto. Enquanto não, nenhum lote pago roda.
2. Decidir se a camada corrigida dos Documentos Parlamentares vira rotina
   versionada agora ou se fica declarada como derivada não reprodutível até lá.
3. Decidir o que entra no git, e quando.
4. A leitura das 185 fichas, que nenhum modelo faz por você.

## 5. Comandos

```bash
uv run python -m pytest -q
```

```bash
uv run python -m pipeline.base.portao_1906
```

```bash
uv run python -m pipeline.analise.nomes_no_debate
```

```bash
uv run python -m pipeline.analise.nomes_parlamentares
```

O `PYTHONPATH` precisa incluir a raiz do repositório para os módulos de
`pipeline`, e a suíte roda com `uv run python -m pytest`, nunca `uv run pytest`,
por causa da política de Application Control do Windows.
