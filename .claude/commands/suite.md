---
description: Roda a suíte de testes do repo e reporta o resultado real
---

Rode a suíte completa:

```powershell
uv run --with pytest pytest tests/ -q
```

Reporte o número de testes que passaram e falharam, com a saída literal.

Regras:

- Python puro não está no PATH desta máquina. Sempre `uv run`.
- Se algum teste falhar, mostre o traceback e **não** declare a suíte verde.
  Nenhuma afirmação de "está funcionando" sem esta saída na mão, conforme a
  disciplina de verificação antes de conclusão.
- Não conserte o teste para fazê-lo passar sem antes entender a causa. Se a
  falha for real, o caminho é a disciplina de depuração sistemática.
