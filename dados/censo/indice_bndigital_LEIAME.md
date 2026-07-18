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

## Anomalias conhecidas do índice

- Sobreposição de números entre rótulos de ano no CM (ex.: 3000-3089
  aparecem sob 1907 e sob 1909; 4000-4070 sob 1907 e 1912): candidatos a
  duplicata/mislabel da BN; a identidade edição-dia é resolvida pela data do
  masthead na carga, nunca pelo rótulo do nome de arquivo.
- Números espúrios isolados: Paiz 1907_5254, CM 1910_135, CM 1913_9394,
  GN 1906_783, GN 1910_994, GN 1914_801, CP 1908_17171-17172.
- O índice lista Paiz 1913_10408, cujo download da varredura veio corrompido
  (pdf_invalido); candidato a nova tentativa de download.
