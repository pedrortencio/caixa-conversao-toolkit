# dados/

- `piloto_1906/` — resultados do piloto (transcrições txt, classificações json, consolidados xlsx). Histórico, não sobrescrever.
- `scraping/` — hits_{jornal}.csv e registros de busca (termo, data) produzidos pela F1.
- `raw_pdf/` — páginas baixadas da BN (FORA do git; backup via OneDrive). `piloto_1906/` aqui dentro = PDFs originais do piloto.
- `transcricoes/`, `classificacoes/` — outputs das F3/F4 por jornal (versionados: texto leve, domínio público).
- `base/` — caixa_conversao.db (SQLite), parquet e exports xlsx da F5.
