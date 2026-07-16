# Fontes de estudo contínuo

Comunidades, blogs e newsletters para acompanhar as quatro frentes do projeto: métodos quantitativos e text-as-data, IA para pesquisa, escrita acadêmica e código em ciências sociais aplicadas. Curadoria feita em 2026-07-14 a partir do estado do repo (stance detection com LLM validado por κ/ρ, DSL, bootstrap; anotadores Gemini Batch + claude_cli + futuro modelo aberto via OpenRouter; artigo em LaTeX/ABNT; scraping da Hemeroteca).

## As cinco assinaturas essenciais

Se for acompanhar só cinco, são estas:

1. **r/CompSocial** (reddit.com/r/CompSocial): ciência social computacional mantida por pesquisadores; discussão frequente da literatura LLM-como-anotador (Gilardi, Ziems, Egami).
2. **r/LocalLLaMA** (reddit.com/r/LocalLLaMA): modelos abertos, benchmarks reais, custo; diretamente relevante para o terceiro anotador via OpenRouter.
3. **Blog do Andrew Gelman** (statmodeling.stat.columbia.edu): medição, erro e interpretação em ciências sociais; o enquadramento "erro medido, não assumido" do projeto é gelmaniano.
4. **Simon Willison** (simonwillison.net): o melhor blog prático sobre ferramental de LLM (structured output, custo por token, avaliação, pipelines).
5. **NEP-HIS** (nep.repec.org): alerta semanal de working papers em história econômica, por e-mail.

## Métodos quantitativos e text-as-data

- r/AskStatistics e r/statistics: dúvidas pontuais (kappa, concordância entre anotadores, bootstrap) e discussão de métodos.
- r/econometrics: inferência, erros-padrão, desenho amostral (útil na análise final).
- r/AskSocialScience e r/AskEconomics: moderação rigorosa, respostas com fonte.
- r/EconomicHistory: atividade moderada, mas é a área de conteúdo da dissertação.
- SICSS (sicss.io): material aberto dos Summer Institutes in Computational Social Science, incluindo os tutoriais de text-as-data do Chris Bail. Currículo padrão da área.
- Cross Validated (stats.stackexchange.com): dúvidas técnicas de validação estatística.
- Quantitude (podcast): medição, confiabilidade, validade, por dois professores de métodos.
- Broadstreet (broadstreet.blog): economia política histórica, métodos quantitativos + história.
- Materiais de curso de Arthur Spirling e Justin Grimmer (GitHub): versão em sala de aula do Grimmer, Roberts & Stewart (2022), já referência canônica do projeto.

## IA para pesquisa (ferramentas e arquiteturas)

- r/ClaudeAI e r/ClaudeCode: relevantes para o anotador claude_cli e o toolkit .claude/ do repo.
- r/MachineLearning: papers, com filtro (muito ruído para pesquisa aplicada).
- One Useful Thing (Ethan Mollick, Substack): IA aplicada a trabalho acadêmico, sem hype.
- AI Snake Oil (Narayanan e Kapoor, Substack): perspectiva cética sobre validade de LLM em classificação; alimenta a seção de limitações.
- Latent Space (newsletter e podcast): arquiteturas de sistemas com LLM (batch, avaliação, agentes).
- Alertas do Google Scholar: um para "LLM annotation social science", outro para "stance detection LLM". A literatura da ponte metodológica cresce mês a mês.

## Escrita acadêmica

- Raul Pacheco-Vega (raulpacheco.org): fluxo de trabalho de leitura e escrita acadêmica (fichamento, memorandos, escrita diária); cientista político latino-americano. A recomendação mais forte desta seção.
- Explorations of Style (Rachael Cayley): o ato de escrever texto acadêmico, revisão e clareza; combina com o padrão de prosa do projeto.
- The Thesis Whisperer (Inger Mewburn): processo de dissertação e doutorado.
- r/AskAcademia e r/PhD: vida acadêmica (publicação, banca, orientação).
- r/LaTeX e TeX Stack Exchange (tex.stackexchange.com): ABNT em LaTeX (abntex2/biblatex-abnt) sempre gera dúvida.
- r/Zotero: gestão do referencias.bib.

## Código e reprodutibilidade em ciências sociais

- r/Python e r/rstats: o pipeline é Python, o pacote dsl de referência é R; r/rstats tem cultura forte de pesquisa reprodutível.
- r/dataengineering: os padrões de idempotência, retry e resume discutidos lá se aplicam direto ao F1-F4.
- The Turing Way (the-turing-way.netlify.app): handbook aberto de ciência de dados reprodutível para pesquisa; referência de boas práticas para a seção de método.
- The Carpentries (carpentries.org): lições abertas de software e dados para pesquisadores; nível introdutório, mas bom material de organização de projeto.
- Programming Historian em português (programminghistorian.org/pt): ecossistema natural do scraper da Hemeroteca; as lições do Eric Brasil saíram lá.
- LABHD-UFBA e comunidade brasileira de humanidades digitais: eventos e YouTube; interlocutores nacionais do pipeline.
- ABPHE: associação brasileira de história econômica; eventos e rede da área.
