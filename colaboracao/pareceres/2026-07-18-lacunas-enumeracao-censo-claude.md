# Parecer do Claude: lacunas de enumeração do censo e recuperação pelo índice bndigital

- task_id: 2026-07-18-lacunas-enumeracao-censo
- autor: Claude (Fable 5), parecer independente congelado ANTES do despacho ao Codex
- data: 2026-07-18 (madrugada)
- escopo: decisão de corpus, nível crítico

## Fatos observados (verificados nesta sessão)

1. A varredura da Fase A encerrou limpa: 8.889 edições ok (84,4 GB, 84.771
   páginas) e 1 pdf_invalido (Paiz 1913_10408). Portão técnico: banco ==
   manifesto == disco nas 27 células com sucesso; integrity_check ok;
   migração 002 aplicada.
2. Regressão 1906: Paiz 79/79 aprovado; CM 106/108 (faltam 1869, 1870), CP
   92/93 (falta 15276), GN 145/146 (falta 78). Os 4 faltantes respondem 404
   no host estático e NÃO constam do índice bndigital; 3 deles são as
   edições duplas com prefixo A/B que o piloto baixou à mão no DocReader.
3. O índice bndigital (páginas acervo-digital da BN) enumera, por ano, cada
   edição digitalizada com link direto ao MESMO host estático da varredura.
   Extração via navegador em 18/07 (Cloudflare devolve 403 a requests).
   Manifesto versionado: dados/censo/indice_bndigital_{bib}.csv + LEIAME.
4. O censo da varredura é SUBCONJUNTO ESTRITO do índice nas 36 células.
   Diff: 3.092 edições no índice ausentes do censo (CM 2.781 em 1907-14;
   GN 306, sendo 21 em 1910 e 285 em 1914; Paiz 2; CP 2).
5. Amostras vivas do host: per089842_1908_02400.pdf 200 (8,4 MB) e
   per103730_1914_00100.pdf 200 (8,2 MB); per103730_1910_00121.pdf 404.
   Logo host ⊆ índice: o índice também lista arquivos ausentes do host.
6. Lacunas REAIS de digitalização (ausentes também do índice): GN 1913
   inteiro; Paiz fim de 1907 (~122 números, 8368-8489); CP 1908 (~105
   números); GN 1910-1912 (buracos internos de 75/60/68); CM 1697, 1869 e
   1870 em 1906.
7. O índice do CM tem sobreposições de número entre rótulos de ano
   (3000-3089 sob 1907 E 1909; 4000-4070 sob 1907 E 1912) e espúrios
   isolados (135 em 1910, 9394 em 1913 etc.). A varredura do CM morreu por
   um salto de numeração (2099 para 2255, maior que a parada de 90) e pelo
   encadeamento de âncora entre anos.
8. A base v2 resolve identidade edição-dia por data de masthead observada
   (protocolo auditado no piloto), nunca pelo rótulo do nome de arquivo.

## Inferências

- A enumeração pelo índice DOMINA a varredura como fonte de censo: é
  superconjunto verificado, oficial e barata. A varredura por vizinhança
  fica como validação, não como descoberta.
- A recuperação dos 3.092 é pequena em termos operacionais (~25-30 GB,
  ~4h com pausa de 4 s) e reutiliza a máquina existente (persistência,
  manifesto, resume, cache); muda só o gerador de alvos: lista explícita
  (ano, número) em vez de varredura incremental.
- As lacunas que sobram são de acervo da BN, não de método; o desenho da
  cascata do censo já prevê registrá-las como ausência documentada.
- Duplas A/B e sobreposições de rótulo de ano são problemas de IDENTIDADE,
  não de coleta; o masthead + sha256 já dão o mecanismo de resolução, mas a
  regra de agregação por dia com mais de uma edição precisa ser
  pré-registrada antes da Fase B (pendência já aberta em decisoes.md).

## Riscos, ranqueados

1. Viés de cobertura entre jornais e no tempo: CM ganha 2.781 edições
   (1907-14) e GN perde 1913 inteiro; comparações entre jornais e meses com
   cobertura desigual podem confundir composição com posição. Mitigação:
   publicar taxa de cobertura por jornal-mês na cascata do denominador e
   rodar análise de sensibilidade nos meses de baixa cobertura.
2. Índice parcialmente aspiracional (lista 404s): tratá-lo como fonte de
   ENUMERAÇÃO com sondagem positiva por item, nunca como prova de
   existência.
3. Duplicatas/mislabels do CM inflarem o denominador se a contagem for por
   (ano, número): a des-duplicação por masthead (e sha para byte-idênticos)
   tem de preceder qualquer contagem de edição-dia.
4. Proveniência da extração manual (navegador): mitigada por manifesto
   versionado + LEIAME; risco residual de o Cloudflare endurecer e travar
   reextrações futuras.
5. As 4 edições do piloto fora do host: só recuperáveis por DocReader
   manual (captcha); só temos PDFs locais do piloto para O Paiz, então
   CM/CP/GN exigiriam re-download manual. Ganho: 4 edições-dia.

## Alternativas

- A (recomendada): rodada de recuperação guiada pelo índice, com protocolo
  novo de inventário (fonte indice_bndigital) e registro positivo de cada
  alvo (ok, ausente, erro); depois re-rodar cobertura + regressão.
- B: congelar o corpus como está e tratar todo o diff como ausência.
  Rejeitada: deixaria 2.781 edições EXISTENTES fora por artefato do método
  de varredura, viés grave e evitável contra o CM em 1907-14.
- C: A + resgate manual das 4 edições do piloto via DocReader. Não bloqueia
  A; decisão à parte de Pedro (custo manual por edição, captcha).

## Recomendação

Executar A agora, antes da Fase B e sem gate pago (é coleta, não medição):

1. Nova fonte de inventário `indice_bndigital/1.0.0` (parâmetros: URLs das
   páginas, data de extração, método navegador) e carga dos alvos do diff
   com a máquina existente; GN 1910 índice-only sondado e registrado.
2. Re-rodar relatório de cobertura e regressão 1906. Atualizar o critério
   do portão: gabarito ⊆ (censo ∪ ausências documentadas com fonte); hoje a
   regressão reprova sem essa categoria e os 4 faltantes ficam sem estado
   formal.
3. Pré-registrar antes da Fase B: regra de agregação para dia com mais de
   uma edição; tratamento de duplicatas de rótulo de ano do CM (masthead
   decide, sha detecta byte-idênticos); publicação da cobertura por
   jornal-mês; política explícita para GN 1913 (ausência total de acervo).
4. Nova tentativa de download do Paiz 1913_10408 (pdf_invalido) na mesma
   rodada. DocReader NÃO vira rota de produção.

## Teste que poderia refutar esta recomendação

Sondar amostra aleatória de ~30 alvos do diff antes da rodada: se a taxa de
404 for alta (acima de ~20%), o índice não sustenta a recuperação como
planejado e a alternativa B ganha peso nos trechos afetados. Na carga, se a
auditoria de masthead mostrar que os blocos 3000/4000 rotulados 1907 no CM
são edições DISTINTAS das homônimas de 1909/1912 (e não duplicatas), a
cronologia da numeração do CM exige revisão antes de contar edição-dia.
