---
description: Run linting, typecheck, and tests
---

```bash
ruff check . && mypy debian relay --ignore-missing-imports && pytest -v
```
