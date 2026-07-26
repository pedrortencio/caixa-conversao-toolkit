# Parecer do Claude: como medir posição no subcorpus substantivo

- task_id: 2026-07-25-escolha-instrumento-cobertura
- autor: Claude (Opus 5), parecer independente congelado ANTES do despacho ao Codex
- data: 2026-07-25
- escopo: instrumento e cobertura da medida de posição, nível crítico

## Fatos observados (verificados nesta sessão)

1. O subcorpus substantivo está entre **3.054 e 3.758 edições**, IC95 por
   bootstrap de 2.784 a 4.042. O número foi recalculado hoje depois da correção
   de dois bugs de limpeza e mal se moveu (era 3.043 e 3.750), o que o torna
   robusto aos defeitos conhecidos da amostra.
2. A calibração contra o gabarito de 1906 mantém erro de 1,6% (436 previsto
   contra 429). Ela valida a precisão da triagem por nome, **não** a proporção
   substantiva de 1907 em diante, que repousa em cerca de 50 peças por ano.
3. A 4 minutos por edição, o subcorpus exige de 204 a 251 horas. A 15 ou 20
   horas semanais, são 10 a 17 semanas só codificando, contra um cronograma de
   cerca de dois meses com leitura e escrita em paralelo.
4. A saliência não depende desta decisão: sai do censo, é determinística, já
   está decomposta em extensiva, intensidade e proeminência (D3, 19/07).
5. O estimando registrado é a distribuição de posições por edição-dia, e as
   afirmações centrais do trabalho são **por jornal e por fase**: quatro
   diários e quatro fases, ou seja, ao menos 16 células, com cinco categorias
   de posição mais Mixed/Ambiguous.
6. O piloto de 1906 tem validação humana com kappa 0,712 e rho 0,670, e a
   auditoria P0 dessa validação segue pendente.
7. Existe amostra rotulada de registro (487 peças, 453 decididas) com estratos
   de jornal e ano já construídos, que é moldura pronta para a estratificação.

## Inferências

**1. As três saídas não são alternativas mútuas. Duas delas contêm a
primeira.** Tanto a extensão por LLM quanto a por classificador supervisionado
exigem padrão-ouro humano em amostra, por dois motivos independentes: para
medir o erro e para calcular a correção do viés de classificação (a correção
tipo DSL que o próprio desenho prevê). A saída híbrida por fase exige o mesmo,
e ainda exige sobreposição entre os dois regimes para calibrar. Portanto a
amostra humana estratificada não é a saída 1: é **pré-requisito das três**.

**2. A decisão que Pedro precisa tomar hoje não é a que está posta.** Como as
três saídas convergem no mesmo primeiro passo, a escolha entre elas pode e deve
ser adiada até depois de haver padrão-ouro, quando ela deixa de ser uma aposta e
passa a ser leitura de números medidos: concordância entre codificadores,
precisão efetivamente alcançada por célula e custo real de lote pequeno. Decidir
agora é decidir sem a informação que a própria decisão requer.

**3. O ponto fraco da saída por amostra apenas é de resolução, não de honestidade.**
Uma amostra de 400 a 600 edições distribuída em 16 células dá 25 a 37 edições
por célula. Para uma proporção perto de 0,5, a meia-largura do IC95 por célula
fica na casa de 16 pontos percentuais, e cai ainda mais quando a categoria é uma
entre cinco. Isso sustenta contrastes grandes (um jornal claramente mais
expansionista que outro numa fase) e não sustenta o que o memorando chama de
essencial: variação temporal fina e identificação de viradas. A saída por
amostra não é inválida, é de baixa resolução exatamente onde mora o núcleo
interpretativo.

**4. A saída híbrida por fase tem objeção metodológica séria e específica.**
Trocar de instrumento ao longo do eixo temporal introduz variação de método
correlacionada com a variável de interesse, que é justamente a mudança ao longo
do tempo. Uma diferença observada entre 1906 e 1912 passaria a ser
inseparavelmente diferença de época e diferença de instrumento. O atrativo
retórico ("a fase decisiva foi lida inteira por humano") é real, mas o custo
inferencial é alto. Se for adotada, exige codificação humana também em amostra
das fases automatizadas, para estimar e reportar o degrau de instrumento. Feita
essa exigência, a híbrida se torna a saída 2 com censo humano adicional em 1906,
e não um desenho próprio.

**5. LLM e classificador supervisionado não deviam viajar na mesma frase.** São
diferentes em tudo que importa aqui: o classificador treinado na amostra humana
custa zero em token, é reprodutível bit a bit, audita-se por inspeção de
atributos e não depende de fornecedor; a LLM custa, varia com a versão do
modelo, e carrega o ônus da prova que 19/07 lhe atribuiu. Por outro lado o
classificador precisa de mais rótulos humanos para o mesmo desempenho e falha
justamente onde o construto é sutil (voz editorial contra discurso reproduzido,
que é o problema D4). A ordem barata é: treinar o classificador primeiro,
porque ele é grátis e mede o piso; recorrer à LLM apenas para o resíduo que ele
não resolve, com o custo então já dimensionado.

**6. A camada de texto embutido muda a economia da decisão e ainda não foi
usada para isso.** O teste D5, protocolado com estimativa de poucos reais, nunca
rodou. Se classificar sobre o OCR da BN funcionar tão bem quanto sobre
transcrição por LLM, quase todo o orçamento de R$ 415 deixa de ser necessário, e
a saída 2 fica muito mais barata do que o relatório de 23/07 supõe. Decidir
cobertura antes de rodar D5 é decidir com o custo errado na mesa.

## Riscos, ranqueados

1. **Decidir o instrumento agora, sem padrão-ouro.** Compromete o desenho com
   uma aposta e gasta o capital de decisão de nível crítico numa escolha que
   ficará mais barata e mais informada em duas ou três semanas.
2. **Amostra dimensionada só para estimar, e não também para treinar.** Refazer
   amostragem depois custa o dobro de horas de Pedro, que é o recurso mais
   escasso do projeto.
3. **Proporção substantiva de 1907 em diante sem padrão-ouro.** Todo o número
   de 3.054 a 3.758 depende de cerca de 50 peças por ano, pooled entre quatro
   jornais. As células jornal-ano têm cerca de 13 peças e não sustentam leitura
   isolada. O risco correlato dos 300 descartes não medidos continua aberto e é
   barato de fechar.
4. **Codebook das fases 2 a 4 ainda esqueleto.** Bloqueia o protocolo humano,
   que bloqueia o padrão-ouro, que bloqueia tudo acima. É o gargalo real, e é
   redação de Pedro, não de modelo.
5. **Kappa de 0,712 do piloto pode não se reproduzir** sob o codebook novo e a
   unidade de codificação nova (peça relevante, não edição). Se a concordância
   humana cair, nenhuma extensão automatizada salva a medida, e o construto é
   que precisa de trabalho.

## Alternativas consideradas

- **Decidir agora pela saída 2** (automação com validação). Rejeitada: exige a
  amostra de qualquer modo, e antecipar a decisão não acelera nada.
- **Decidir agora pela saída 1** (amostra apenas). Rejeitada: descarta
  gratuitamente a opção de estender depois, e a resolução por célula é
  provavelmente insuficiente para o que o memorando chama de essencial.
- **Reduzir o estimando** (por exemplo, abandonar a leitura por fase e reportar
  só por jornal). É a saída honesta se o padrão-ouro mostrar que nada mais é
  sustentável, mas é decisão de Pedro sobre a pergunta histórica, não de
  desenho, e seria prematura antes de medir.

## Recomendação

**Não escolher entre as três saídas nesta rodada.** Executar o passo comum às
três e converter a escolha em leitura de números medidos. Concretamente, e em
ordem:

1. Pedro redige o codebook das fases 2 a 4. É o gargalo e não tem substituto.
2. Fechar o risco barato dos 300 descartes rotulando cerca de 40 sorteados,
   o que converte a projeção de "calibrada num ano" para "com viés medido".
3. Desenhar a amostra estratificada (artefato 4) **dimensionada para os dois
   usos**: estimar posição por célula com precisão declarada e servir de
   conjunto de treino e teste para extensão automatizada, com separação
   explícita entre as partições para o segundo uso não contaminar o primeiro.
4. Executar o protocolo humano (artefato 5): dupla codificação em subconjunto,
   adjudicação, conjunto dourado com classificação mascarada.
5. Rodar o teste D5 sobre o OCR embutido, que é barato e fixa o custo real da
   saída 2 antes de qualquer compromisso.
6. Só então decidir cobertura, com a concordância humana, a precisão por célula
   e o custo de lote pequeno na mesa.

Se for necessário registrar hoje uma direção, registre-a como **hipótese de
trabalho** e não como decisão: extensão automatizada sobre padrão-ouro humano,
com classificador supervisionado testado antes da LLM, e censo humano adicional
em 1906 apenas se sobrar tempo, tratado como validação e não como fonte de
comparabilidade entre fases.

## Teste que poderia refutar esta recomendação

Depois de codificado o padrão-ouro estratificado, calcular a precisão por célula
jornal-fase efetivamente obtida. **Se os intervalos por célula já sustentarem as
afirmações que Pedro quer fazer, a extensão automatizada é desnecessária e esta
recomendação estava errada ao tratá-la como provável.** O caminho seria a saída
1 pura, mais barata e mais defensável.

O teste simétrico também refuta: se a concordância entre codificadores humanos
ficar baixa no codebook novo, nenhuma cobertura automatizada resolve, porque não
haveria alvo estável a aprender, e o trabalho volta ao construto. Nesse caso a
recomendação de dimensionar a amostra para treino teria sido desperdício.
