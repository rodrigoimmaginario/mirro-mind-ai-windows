[< Story](index.md)

# Test Guide — CV16.DS3 Explorer Activation Contract

## Automated Verification

```bash
uv run pytest \
  tests/unit/memory/cli/test_explore.py \
  tests/unit/memory/services/test_operating_mode.py \
  tests/unit/memory/cli/test_welcome.py
```

Expected: all tests pass.

Lint:

```bash
uv run ruff check \
  src/memory/cli/explore.py \
  tests/unit/memory/cli/test_explore.py
```

Expected: all checks pass.

## Manual Smoke

Activate Explorer Mode:

```bash
uv run python -m memory explore load explorer-mode >/tmp/mirror-explore-load.txt
uv run python -m memory mode status
uv run python -m memory welcome --status-line
```

Expected:

- `/tmp/mirror-explore-load.txt` includes `△  EXPLORER MODE ACTIVE`;
- mode status prints `Explorer Mode · explorer-mode`;
- status line includes `Active Journey explorer-mode on △ Explorer Mode`.

Leave Explorer Mode:

```bash
uv run python -m memory explore deactivate >/tmp/mirror-explore-deactivate.txt
uv run python -m memory mode status
uv run python -m memory welcome --status-line
```

Expected:

- `/tmp/mirror-explore-deactivate.txt` visibly confirms the Explorer lens ended;
- mode status prints `Mirror Mode`;
- status line falls back to `Active Journey explorer-mode on ◌ Mirror Mode` when sticky journey context remains.

## Skill-Level Validation

From Pi, enter Explorer Mode using either explicit skill syntax:

```text
/mm-explore explorer-mode
```

or natural language:

```text
abrir exploração em explorer-mode
```

Expected: Mirror runs the contained activation operation, renders the command's transition surface, and treats subsequent substantive material as exploratory.

Then leave using natural language:

```text
sair do modo explorador
```

Expected: Mirror runs the contained deactivation operation, confirms the explicit Explorer lens ended, and does not erase journey context.

## Pass Condition

Explorer Mode has an explicit entry and exit contract, activation is visible and non-constructional, deactivation is visible and context-preserving, and promotion to Builder remains explicitly out of scope for this story.
