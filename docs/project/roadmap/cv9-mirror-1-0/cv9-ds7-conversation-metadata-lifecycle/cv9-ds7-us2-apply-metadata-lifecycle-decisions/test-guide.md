[< CV9.DS7.US2](index.md)

# Test Guide — CV9.DS7.US2 Apply Metadata Lifecycle Decisions Safely

## Acceptance Behavior

```text
Given a conversation with dry-run metadata lifecycle decisions and no manual title lock
When apply metadata lifecycle decisions is executed through an explicit bounded path
Then Mirror persists only safe lifecycle updates for eligible fields
And manual/user-edited title locks are preserved without overwrite
And weak or low-confidence candidate decisions are not applied automatically
```

## Automated Validation

Expected focused test coverage:

- manual title locks are preserved;
- `refine_candidate` decisions are reported/skipped, not automatically applied;
- eligible safe updates record lifecycle metadata/provenance;
- apply report shows changed and skipped fields;
- dry-run remains non-mutating after apply path exists;
- no autonomous background mutation is introduced.

## Navigator Validation Route

Use a controlled test database or fixture conversation. Do not validate apply
against production conversation rows unless a backup/recovery route has been
explicitly named and accepted.

Expected route after implementation:

1. Create or select a fixture conversation in a controlled test database.
2. Run `ConversationService.dry_run_metadata_lifecycle(conversation_id)` and inspect decisions.
3. Run `ConversationService.apply_metadata_lifecycle(...)` with explicit metadata values.
4. Inspect the apply report's `changed` and `skipped` fields.
5. Re-read the conversation and confirm only eligible fields changed.
6. Confirm manual locks are preserved in a locked-title fixture.
7. Confirm `refine_candidate` title decisions are skipped rather than applied automatically.

Pass condition:

Apply behavior is explicit, bounded, explainable, and preserves manual locks.

Fail condition:

Apply mutates low-confidence candidates, overwrites manual titles, hides what it
changed, or introduces autonomous mutation outside the explicit apply path.

## Debt Gate

If implementation requires substantial policy extraction or write orchestration,
stop and split CV9.DS7.TS2 before applying mutation behavior.
