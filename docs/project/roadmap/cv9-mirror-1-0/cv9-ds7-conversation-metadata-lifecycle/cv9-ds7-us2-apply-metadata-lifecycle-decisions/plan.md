[< CV9.DS7.US2](index.md)

# Plan — CV9.DS7.US2 Apply Metadata Lifecycle Decisions Safely

## Roadmap Level

User Story inside [CV9.DS7 Conversation Metadata Lifecycle](../index.md).

## Acceptance Behavior

```text
Given a conversation with dry-run metadata lifecycle decisions and no manual title lock
When apply metadata lifecycle decisions is executed through an explicit bounded path
Then Mirror persists only safe lifecycle updates for eligible fields
And manual/user-edited title locks are preserved without overwrite
And weak or low-confidence candidate decisions are not applied automatically
```

## Debt Gate

D-001 is active for this story:

[Metadata lifecycle policy and evidence filtering live inside ConversationService](../../../../debt.md#d-001--metadata-lifecycle-policy-and-evidence-filtering-live-inside-conversationservice)

Before implementation, inspect whether apply/mutation behavior can remain small
and safe inside the current service boundary. If mutation paths require more
policy complexity, write orchestration, or confidence handling than expected,
split a TS2 debt-payment story before implementation.

Potential TS2:

```text
CV9.DS7.TS2 — Extract metadata lifecycle policy boundary
```

## Scope

- Add an explicit bounded apply path for metadata lifecycle decisions.
- Apply only safe, high-confidence lifecycle updates.
- Preserve manual/user-edited title locks.
- Preserve non-mutating dry-run behavior.
- Record metadata lifecycle provenance/update source when applying.
- Keep apply behavior opt-in; no autonomous per-turn updates.

## Out of Scope

- Applying low/medium-confidence `refine_candidate` title decisions automatically.
- Generating replacement titles from LLMs as part of apply.
- Journey inference after conversation start.
- Autonomous background metadata mutation.
- Broad evidence filtering/ranking refactor unless D-001 triggers TS2.

## Implementation Approach

1. Inspect current dry-run report shape and title update paths.
2. Decide whether current service boundary can safely host bounded apply.
3. If yes, add an explicit apply method that:
   - calls dry-run;
   - filters decisions to safe apply actions;
   - preserves manual locks;
   - updates only eligible fields;
   - records lifecycle metadata/provenance;
   - returns an operation report.
4. Expose apply through the smallest safe validation surface, likely service tests first.
5. Add tests for:
   - manual lock preservation;
   - low/medium-confidence `refine_candidate` not auto-applied;
   - safe title repair/create path where deterministic value already exists;
   - summary/tags apply only when values are provided or safely derivable;
   - dry-run remains non-mutating.

## Validation Route

- Focused automated tests for apply safety and lock preservation.
- Manual/Navigator validation should use a controlled test database or fixture, not production conversation rows, unless an explicit backup/recovery route exists.
- Confirm dry-run still reports `mutated: false`.
- Confirm apply report names exactly what changed and what was skipped.

## Documentation Impact

- Update US2 test guide with controlled apply validation route.
- Update DS7 status when US2 validates/closes.
- Update D-001 if debt is paid, grows, or remains carried.

## Risks

- Mutation behavior can corrupt user-facing metadata if confidence and lock rules are weak.
- Applying title refinement without generating an approved replacement title would be unsafe.
- ConversationService may become too large; D-001 may trigger TS2 before implementation.
