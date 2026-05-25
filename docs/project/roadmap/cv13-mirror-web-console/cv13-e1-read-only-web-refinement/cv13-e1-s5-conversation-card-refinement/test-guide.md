[< Story](index.md)

# Test Guide — CV13.E1.S5 Conversation card refinement

## Automated validation

Run:

```bash
uv run pytest tests/unit/memory/surfaces/test_workspace.py tests/unit/memory/web/test_server.py
uv run ruff check src/memory/web src/memory/surfaces tests/unit/memory/surfaces/test_workspace.py tests/unit/memory/web/test_server.py
uv run ruff format --check src/memory/web src/memory/surfaces tests/unit/memory/surfaces/test_workspace.py tests/unit/memory/web/test_server.py
node --check src/memory/web/static/app.js
git diff --check
```

Expected result: all commands pass.

## Manual browser validation

Open Workspace and select a journey with conversations.

Expected observations:

- conversation cards are easier to scan than before;
- message count is prominent;
- persona, journey, and start date are visible when present;
- the card does not look like it links to an unavailable detail page.
