[< CV9.DS7.US1](index.md)

# Test Guide — CV9.DS7.US1 Dry-run Metadata Lifecycle Decision Path

## Acceptance Behavior

```text
Given sample conversations with generic, meaningful, and scope-changing openings
When the metadata lifecycle dry-run is executed
Then Mirror reports lifecycle decisions for title, summary, tags, readiness, and provenance without mutating stored conversations
And manual/user-edited title locks are reported as preserved
```

## Automated Validation

Run the focused tests added for the dry-run decision matrix.

Expected coverage:

- generic or low-specificity metadata is reported for repair/refinement;
- meaningful opening metadata can be kept;
- later summary evidence can produce `refine_candidate` with confidence/evidence;
- summary and tags can defer until enough substance exists;
- manual/user-edited title locks are preserved;
- dry-run execution does not write to storage.

## Manual / Operation Validation

Run the dry-run against representative conversation samples and inspect the JSON report:

```bash
uv run python -m memory.cli.conversations --metadata-lifecycle-dry-run <conversation-id>
```

Use `--mirror-home <path>` when validating against a non-default Mirror home.

Expected observations:

- each metadata field has a decision or deferral reason;
- readiness/provenance/confidence are visible where applicable;
- manual locks are explicitly preserved;
- no conversation row is mutated after the dry-run.

## Non-Goals

Do not validate apply/mutation behavior in this story. Apply behavior belongs to
CV9.DS7.US2.
