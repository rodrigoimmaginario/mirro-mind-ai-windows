# Test Guide — CV9.DS7.US8 Historical Metadata Backfill Preview

## Automated

```bash
uv run pytest tests/unit/memory/services/test_conversation.py tests/unit/memory/cli/test_conversations.py -q
```

## Navigator Validation

Run safe preview:

```bash
uv run python -m memory.cli.conversations \
  --metadata-backfill-preview \
  --metadata-backfill-mode safe \
  --limit 10
```

Run force preview:

```bash
uv run python -m memory.cli.conversations \
  --metadata-backfill-preview \
  --metadata-backfill-mode force \
  --limit 10
```

Pass conditions:

- `mode` is `metadata_backfill_preview`;
- `mutated` is false;
- candidates contain per-field `actions`;
- safe mode only includes conversations with apply/regenerate-ready actions;
- force mode shows selected conversations as regeneration candidates while preserving manual locks.
