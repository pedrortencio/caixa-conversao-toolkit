# Manifestos do índice bndigital (indice_bndigital_{bib}.csv)

Enumeração oficial de edições digitalizadas por jornal, extraída das páginas
de acervo da BN em 18/07/2026 (~04h40-05h05, horário local):

- https://bndigital.bn.gov.br/acervo-digital/correio/089842
- https://bndigital.bn.gov.br/acervo-digital/correio-paulistano/090972
- https://bndigital.bn.gov.br/acervo-digital/gazeta-de-noticias/103730
- https://bndigital.bn.gov.br/acervo-digital/paiz/178691

Cada link numérico dessas páginas aponta um PDF do host estático
(`https://hemeroteca-pdf.bn.gov.br/{bib}/per{bib}_{ano}_{numero:05d}.pdf`),
o mesmo host e nomenclatura usados pela varredura da Fase A.

## Método e limitação de acesso

Extração via navegador (Chrome, sessão do Pedro), lendo os `href` dos links
com regex `per{bib}_(\d{4})_(\d{5})\.pdf` e comprimindo em faixas; expansão
determinística para estes CSVs (colunas `ano,numero`, recorte 1906-1914).
O acesso fora de navegador é bloqueado pelo Cloudflare (GET simples devolve
403), então a extração NÃO é automatizável por requests; repetições exigem
navegador ou Selenium headed.

## Fatos de validação (18/07/2026)

- O censo por varredura é SUBCONJUNTO do índice em todas as 36 células
  (bib, ano); nenhum arquivo do censo está fora do índice.
- Diff índice menos censo: 3.092 edições (CM 2.781 em 1907-14; Gazeta 306,
  sendo 21 em 1910 e 285 em 1914; O Paiz 2; CP 2).
- Sondagens ao vivo no host: per089842_1908_02400.pdf e
  per103730_1914_00100.pdf respondem 200 (recuperação viável);
  per103730_1910_00121.pdf responde 404 (o índice também lista arquivos
  ausentes do host; recuperação deve sondar e registrar ausência positiva).
- Gazeta 1913 NÃO existe no índice (lacuna real de digitalização).

## Segunda passagem de extração (18/07/2026, ~14h)

Repetição independente da extração (recomendação 2 do parecer do Codex de
18/07), na sessão de Chrome do Pedro, com snapshot do DOM guardado em
`snapshots_bndigital/` e hash SHA-256 conferido entre o navegador e o disco:

| bib | arquivo | bytes | sha256 |
|---|---|---|---|
| 089842 | snapshot_bndigital_089842_20260718_passagem2.html | 1.445.078 | 7b4687fd5164bd38757d6f278f11bd8683ffbe2853b0a37a4221171843ba1879 |
| 090972 | snapshot_bndigital_090972_20260718_passagem2.html | 1.522.933 | d4b396bba7a05a987531a3ee317b3a927ba8d9976c61d4238edf4a9c1792d593 |
| 103730 | snapshot_bndigital_103730_20260718_passagem2.html | 1.491.530 | fc7a2971a18a0a7b8fc2bfa7e795ea652304757bdf3404e1eca2a0629be35d8a |
| 178691 | snapshot_bndigital_178691_20260718_passagem2.html | 1.018.251 | fdde83f82e79f463d9b02927735aeb49ffbe8cd6356eb561a4129e7a817efa98 |

Verificação reproduzível: `uv run python pipeline/scraper/indice_bndigital.py
--snapshots dados/censo/snapshots_bndigital --censo dados/censo` (com testes
em `tests/test_indice_bndigital.py`). Resultado: **IDÊNTICOS nas 4 páginas**,
zero divergências item a item no recorte 1906-1914 (089842: 3.240; 090972:
3.128; 103730: 2.526; 178691: 3.087; total 11.981 edições). As anomalias da
seção abaixo reapareceram todas na segunda passagem.

Nota de método: o HTML serializado do DOM varia ~1-2 KB entre carregamentos
(conteúdo dinâmico da página), então o hash identifica a fotografia exata
salva, não um invariante da página; o invariante verificado é o CONJUNTO de
links, idêntico entre as passagens.

## Anomalias conhecidas do índice

- Sobreposição de números entre rótulos de ano no CM (ex.: 3000-3089
  aparecem sob 1907 e sob 1909; 4000-4070 sob 1907 e 1912): candidatos a
  duplicata/mislabel da BN; a identidade edição-dia é resolvida pela data do
  masthead na carga, nunca pelo rótulo do nome de arquivo.
- Números espúrios isolados: Paiz 1907_5254, CM 1910_135, CM 1913_9394,
  GN 1906_783, GN 1910_994, GN 1914_801, CP 1908_17171-17172.
- O índice lista Paiz 1913_10408, cujo download da varredura veio corrompido
  (pdf_invalido); candidato a nova tentativa de download.
