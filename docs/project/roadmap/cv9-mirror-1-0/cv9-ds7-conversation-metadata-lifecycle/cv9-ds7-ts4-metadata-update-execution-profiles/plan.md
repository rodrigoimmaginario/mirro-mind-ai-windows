# Plan — CV9.DS7.TS4 Metadata Update Execution Profiles

## Scope

- Add explicit execution profile definitions.
- Support profile action derivation per field.
- Keep manual maintenance on `manual_safe`.
- Prepare backfill preview for `backfill_safe` and `backfill_force`.
- Preserve manual locks by default.

## Validation

```bash
uv run pytest tests/unit/memory/services/test_conversation.py tests/unit/memory/cli/test_conversations.py -q
```
