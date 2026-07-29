---
description: Roda a suíte de testes do repo e reporta o resultado real
---

Rode a suíte completa:

```powershell
uv run python -m pytest tests/ -q
```

Reporte o número de testes que passaram e falharam, com a saída literal.

Regras:

- Python puro não está no PATH desta máquina. Sempre `uv run`.
- **Use `uv run python -m pytest`, nunca `uv run pytest`.** O `.venv` é uma
  junction para `C:\dados-caixa\envs\`, e a política de Application Control do
  Windows bloqueia o `pytest.exe`, que falha com `os error 4551`. Invocar pelo
  módulo passa pelo `python.exe` e funciona.
- Se algum teste falhar, mostre o traceback e **não** declare a suíte verde.
  Nenhuma afirmação de "está funcionando" sem esta saída na mão, conforme a
  disciplina de verificação antes de conclusão.
- Não conserte o teste para fazê-lo passar sem antes entender a causa. Se a
  falha for real, o caminho é a disciplina de depuração sistemática.
