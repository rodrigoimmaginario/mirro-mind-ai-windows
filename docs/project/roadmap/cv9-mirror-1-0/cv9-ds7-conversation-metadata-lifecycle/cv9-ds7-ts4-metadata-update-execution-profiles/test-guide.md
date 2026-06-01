# Test Guide — CV9.DS7.TS4 Metadata Update Execution Profiles

## Automated

```bash
uv run pytest tests/unit/memory/services/test_conversation.py tests/unit/memory/cli/test_conversations.py -q
```

Expected:

- profiles resolve by name;
- manual safe applies only create/repair/create decisions;
- backfill force marks eligible generated fields for regeneration;
- manual locks remain preserved by default.
