[< CV9.DS7.TS1](index.md)

# Plan — CV9.DS7.TS1 Metadata Lifecycle Decision Policy

## Roadmap Level

Technical Story inside [CV9.DS7 Conversation Metadata Lifecycle](../index.md).

## Verification Behavior

```text
Given conversation metadata with title provenance, lock state, messages, and optional summary evidence
When the metadata lifecycle policy evaluates title, summary, and tags
Then it reports evidence-based decisions without relying on user-specific phrase matching
And it distinguishes hard decisions from low/medium-confidence refinement candidates
```

## Problem Found During US1 Validation

US1 exposed the non-mutating dry-run successfully, but Navigator validation on
sample `0f8f0fc0` produced a semantic false-keep:

```text
title: vamos trabalhar no projeto antes de mim
decision: keep
```

The human reading was that this title is usable but weak: later summary evidence
contains more specific work intent than the unlocked title. We should not fix
this with a brittle phrase rule such as matching "vamos trabalhar no projeto X",
because that overfits one user's phrasing.

## Scope

- Define evidence-based metadata lifecycle policy for dry-run decisions.
- Add a title refinement candidate state for unlocked titles whose later evidence
  is more specific than the current title.
- Keep phrase-specific/personalized heuristics out of the core policy.
- Use structural signals such as:
  - title source/provenance;
  - manual lock state;
  - whether title is missing/provisional/generated/unknown;
  - whether first exchange and later summary exist;
  - whether later summary contains more specific work objects than the title;
  - confidence for candidate decisions.
- Update US1 dry-run output to use the policy.

## Out of Scope

- Generating replacement titles.
- Applying metadata decisions.
- LLM-based semantic comparison in this story.
- User-specific phrase dictionaries.
- Journey inference after conversation start.

## Implementation Approach

1. Extract or isolate policy helpers from the current dry-run implementation.
2. Represent title decisions with evidence and confidence where useful.
3. Add a non-personal structural check for later specificity:
   - compare normalized meaningful terms in title vs summary;
   - ignore common stop words and very short tokens;
   - report `refine_candidate` when summary has enough extra concrete terms and
     title is unlocked/non-manual.
4. Keep existing hard decisions:
   - `preserve` for manual locks;
   - `create` for missing ready title;
   - `repair` for provisional/known weak titles;
   - `defer` when insufficient conversation evidence exists.
5. Add focused tests for:
   - `0f8f0fc0`-like false-keep becomes `refine_candidate`;
   - meaningful opening title remains `keep`;
   - manual lock remains `preserve`;
   - no phrase-specific rule is required for the generic-title case.

## Validation Route

- Focused service tests for the policy matrix.
- Re-run US1 dry-run validation on sample `0f8f0fc0`.
- Confirm the result is evidence-based and non-mutating.

## Documentation Impact

- Update US1 test guide if the dry-run report now includes `refine_candidate`,
  `confidence`, or evidence fields.
- Update DS7 status after TS1 is implemented/validated.

## Risks

- Token-overlap specificity is still a heuristic; it must be humble and report
  candidate status rather than pretending certainty.
- Too much policy work may want an LLM or richer semantic model, which is out of
  scope for this technical story.
