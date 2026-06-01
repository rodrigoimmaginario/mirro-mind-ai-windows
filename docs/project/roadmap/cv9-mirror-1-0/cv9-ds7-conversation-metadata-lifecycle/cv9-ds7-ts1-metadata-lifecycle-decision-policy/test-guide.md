[< CV9.DS7.TS1](index.md)

# Test Guide — CV9.DS7.TS1 Metadata Lifecycle Decision Policy

## Verification Behavior

```text
Given conversation metadata with title provenance, lock state, messages, and optional summary evidence
When the metadata lifecycle policy evaluates title, summary, and tags
Then it reports evidence-based decisions without relying on user-specific phrase matching
And it distinguishes hard decisions from low/medium-confidence refinement candidates
```

## Automated Validation

Run focused conversation service tests for the metadata lifecycle policy.

Expected coverage:

- manual title lock returns `preserve`;
- missing/provisional/known weak title returns `create` or `repair`;
- meaningful unlocked title can remain `keep`;
- unlocked title with later, more specific summary evidence returns
  `refine_candidate` with confidence/evidence;
- summary/tag decisions remain non-mutating;
- dry-run report still returns `mutated: false`.

## Navigator Validation Route

Use the US1 dry-run command after TS1 is implemented:

```bash
uv run python -m memory.cli.conversations --metadata-lifecycle-dry-run 0f8f0fc0
```

Expected observation:

- `mode` is `dry_run`;
- `mutated` is `false`;
- `fields.title.decision` is no longer a hard `keep` for the `0f8f0fc0` sample;
- the title decision explains that later evidence is more specific than the
  current unlocked title;
- the report does not rely on the literal phrase "vamos trabalhar no projeto".

Pass condition:

The Navigator can see an evidence-based refinement candidate without stored
conversation metadata changing.

Fail condition:

The result remains an unexplained hard `keep`, mutates data, or depends on a
user-specific phrase heuristic.
