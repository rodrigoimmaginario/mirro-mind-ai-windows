[< Story](index.md)

# Test Guide — CV13.E1.S3 Memory category drilldown

## Automated validation

Run:

```bash
uv run pytest tests/unit/memory/surfaces/test_search.py tests/unit/memory/web/test_server.py
uv run ruff check src/memory/surfaces src/memory/web tests/unit/memory/surfaces/test_search.py tests/unit/memory/web/test_server.py
uv run ruff format --check src/memory/surfaces src/memory/web tests/unit/memory/surfaces/test_search.py tests/unit/memory/web/test_server.py
node --check src/memory/web/static/app.js
git diff --check
```

Expected result: all commands pass.

## Manual browser validation

Start the web app:

```bash
uv run python -m memory web
```

Open Identity and click a memory category card.

Expected observations:

- a memory category page opens;
- the contextual bar names the category;
- recent memory cards appear when the category has data;
- empty category state is honest;
- Back to Identity returns to the Identity map.
