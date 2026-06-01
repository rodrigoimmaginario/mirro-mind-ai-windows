[< CV9.DS7.TS2](index.md)

# Test Guide — CV9.DS7.TS2 Extract Metadata Lifecycle Policy Boundary

## Verification Behavior

```text
Given the existing metadata lifecycle dry-run behavior
When the lifecycle decision policy is extracted from ConversationService
Then dry-run reports remain behaviorally equivalent
And ConversationService no longer owns the policy details that US2 apply behavior would grow
```

## Automated Validation

Run:

```bash
uv run pytest tests/unit/memory/services/test_conversation.py tests/unit/memory/cli/test_conversations.py -q
uv run pytest tests -q
```

Expected coverage:

- manual title lock still returns `preserve`;
- provisional/weak title still returns `repair`;
- later-specific summary evidence still returns `refine_candidate`;
- summary/tag readiness decisions remain unchanged;
- CLI dry-run still prints JSON report;
- dry-run still returns `mutated: false`.

## Navigator Validation Route

Optional after automated validation:

```bash
uv run python -m memory.cli.conversations --metadata-lifecycle-dry-run 0f8f0fc0
```

Expected observation:

- `fields.title.decision` remains `refine_candidate`;
- `mutated` remains `false`;
- evidence fields remain present.

Pass condition:

Dry-run behavior is unchanged and policy details are no longer embedded directly
inside `ConversationService`.

Fail condition:

Dry-run output changes unexpectedly, CLI breaks, or policy details remain coupled
to the service enough to make US2 apply behavior risky.
