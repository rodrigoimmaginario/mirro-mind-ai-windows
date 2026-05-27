[< Story](index.md)

# Test Guide — CV13.E6.S5 Approval checkpoint model

```bash
uv run pytest tests/unit/memory/web tests/unit/memory/services/test_operation_runs.py tests/unit/memory/db/test_migrations.py -q
uv run ruff check .
node --check src/memory/web/static/app.js
git diff --check
```

Browser validation is included in the final E6 validation pass.
