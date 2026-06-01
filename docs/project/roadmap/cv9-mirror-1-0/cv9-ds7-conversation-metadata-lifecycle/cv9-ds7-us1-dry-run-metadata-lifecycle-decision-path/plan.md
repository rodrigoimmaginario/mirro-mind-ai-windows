[< CV9.DS7.US1](index.md)

# Plan — CV9.DS7.US1 Dry-run Metadata Lifecycle Decision Path

## Roadmap Level

User Story inside [CV9.DS7 Conversation Metadata Lifecycle](../index.md).

## Acceptance Behavior

```text
Given sample conversations with generic, meaningful, and scope-changing openings
When the metadata lifecycle dry-run is executed
Then Mirror reports lifecycle decisions for title, summary, tags, readiness, and provenance without mutating stored conversations
And manual/user-edited title locks are reported as preserved
```

## Scope

- Add a non-mutating dry-run path for conversation metadata lifecycle decisions.
- Report decisions such as keep, create, repair, refine, or defer for title,
  summary, tags, readiness, and provenance.
- Include the minimal lifecycle policy needed to produce the dry-run report.
- Cover known sample shapes from the Exploration handoff:
  - generic project-opening title;
  - meaningful first prompt;
  - scope-changing conversation that later needs refinement.
- Preserve manual/user-edited title locks in the dry-run result.

## Out of Scope

- Applying or mutating metadata lifecycle decisions.
- Autonomous per-turn metadata updates.
- Journey inference after conversation start.
- Full policy generalization beyond what the dry-run needs.
- Replacing all existing title generation behavior.

## Implementation Approach

1. Inspect existing conversation metadata/title lifecycle code and tests.
2. Define a small decision report shape for dry-run output.
3. Implement decision logic in a service-layer path that does not write to storage.
4. Expose the dry-run through the smallest appropriate callable surface for validation
   (service, CLI, or operation surface depending on existing project patterns).
5. Add tests/fixtures for generic, meaningful, scope-changing, and manual-lock cases.
6. Document the validation route in `test-guide.md`.

## Validation Route

- Automated tests for the dry-run decision matrix.
- Manual or command-level dry-run over representative conversation samples, if an
  appropriate command/operation surface exists.
- Confirm no stored conversation metadata is mutated by the dry-run.

## Documentation Impact

- Update this story's `test-guide.md` with the dry-run validation route.
- Update the parent DS7 status when US1 is implemented/validated.
- Capture any discovered policy split as follow-up for TS1 if the minimal policy
  becomes too large for US1.

## Risks

- Existing title-generation code may not expose enough metadata context for a clean
  dry-run without refactoring.
- Summary/tag readiness may require a minimal policy that wants to become TS1.
- A dry-run surface could accidentally become an apply path if mutation boundaries
  are not explicit.
