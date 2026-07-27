---
description: Roda o portão de 1906 e reporta o veredito (guardrail antes de lote pago)
---

Rode o portão de 1906:

```powershell
uv run python -m pipeline.base.portao_1906
```

Reporte o veredito ao Pedro **sem suavizar**, incluindo a saída literal do comando.

Contexto para interpretar o resultado:

- O critério é o pré-registro de 2026-07-18 (`docs/decisoes.md`, item 3), que
  substituiu o critério antigo de subconjunto simples. Todo item do gabarito do
  piloto precisa de exatamente uma classe: `unidade_canonica`,
  `manifestacao_coalescida` ou `excecao_terminal` documentada com fonte.
- **Lista de exceções sem `aprovado_por` preenchido não explica nada.** Se o
  veredito for REPROVADO só por isso, diga que a pendência é ratificação de
  Pedro, não defeito do censo, e mostre quais itens estão sem classe.
- Exit code 0 é aprovado, 1 é reprovado. O hook `PreToolUse` usa o mesmo
  comando para barrar chamadas às etapas pagas.

Se o veredito for REPROVADO, **não** proponha contornar o portão nem editar o
manifesto de exceções por conta própria: a ratificação é decisão de Pedro pelo
protocolo de nível crítico.
