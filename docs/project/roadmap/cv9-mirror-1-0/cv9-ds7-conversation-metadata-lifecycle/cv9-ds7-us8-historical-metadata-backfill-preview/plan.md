# Plan — CV9.DS7.US8 Historical Metadata Backfill Preview

## Scope

- Add a non-mutating backfill preview route.
- Support modes:
  - `safe`: fill/repair only clear candidates;
  - `force`: show all selected conversations as regeneration candidates while preserving manual metadata by default.
- Support limit and journey filters.
- Expose CLI validation route.

## CLI Route

```bash
uv run python -m memory.cli.conversations \
  --metadata-backfill-preview \
  --metadata-backfill-mode safe \
  --limit 10
```

Force preview:

```bash
uv run python -m memory.cli.conversations \
  --metadata-backfill-preview \
  --metadata-backfill-mode force \
  --limit 10
```
