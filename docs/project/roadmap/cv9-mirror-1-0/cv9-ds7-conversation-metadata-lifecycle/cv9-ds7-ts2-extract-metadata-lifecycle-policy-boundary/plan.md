[< CV9.DS7.TS2](index.md)

# Plan — CV9.DS7.TS2 Extract Metadata Lifecycle Policy Boundary

## Roadmap Level

Technical Story inside [CV9.DS7 Conversation Metadata Lifecycle](../index.md).

## Verification Behavior

```text
Given the existing metadata lifecycle dry-run behavior
When the lifecycle decision policy is extracted from ConversationService
Then dry-run reports remain behaviorally equivalent
And ConversationService no longer owns the policy details that US2 apply behavior would grow
```

## Scope

- Extract metadata lifecycle decision helpers from `ConversationService` into a
  small internal module or service boundary.
- Preserve current dry-run report shape and behavior.
- Keep `ConversationService.dry_run_metadata_lifecycle()` as the public service
  method for callers.
- Keep CLI dry-run behavior unchanged.
- Update tests only as needed to preserve and clarify behavior.
- Update D-001 after validation.

## Out of Scope

- Implementing US2 apply/mutation behavior.
- Changing dry-run output semantics.
- Improving evidence term filtering/ranking beyond preserving current behavior.
- Introducing LLM-based semantic comparison.
- Changing manual title update or automatic title generation behavior.

## Implementation Approach

1. Create a small internal policy module, likely under `src/memory/services/` or
   `src/memory/intelligence/`, dedicated to conversation metadata lifecycle
   decisions.
2. Move pure decision helpers into that boundary:
   - title lifecycle dry-run;
   - summary lifecycle dry-run;
   - tags lifecycle dry-run;
   - title refinement evidence;
   - meaningful term extraction.
3. Keep storage reads and writes inside `ConversationService`.
4. Wire `ConversationService.dry_run_metadata_lifecycle()` to call the extracted
   policy boundary.
5. Run focused and full tests.

## Validation Route

- Focused tests for conversation service dry-run still pass.
- CLI dry-run test still passes.
- Full test suite passes.
- Optional Navigator validation: rerun dry-run on `0f8f0fc0` and confirm
  `refine_candidate`, `mutated=false`, and evidence fields remain.

## Debt Impact

This story should reduce D-001 by separating decision policy from the service
that will later own bounded apply orchestration. D-001 may remain partially
carried if evidence filtering/ranking stays noisy.

## Risks

- Over-extracting too early could create an unnecessary abstraction.
- Under-extracting would leave US2 mutation logic coupled to policy details.
- Behavior drift during refactor would undermine US1 validation.
