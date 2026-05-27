[< Story](index.md)

# Test Guide — CV13.E6.S2 Operation event log and timeline

## Automated validation

```bash
uv run pytest tests/unit/memory/web tests/unit/memory/services/test_operation_runs.py tests/unit/memory/db/test_migrations.py -q
uv run ruff check .
node --check src/memory/web/static/app.js
git diff --check
```

## Behavioral checks

- Migration creates `operation_run_events` with run id, sequence, kind, message, details JSON, and timestamp fields.
- Queueing a run records a queued event.
- Marking a run as running records a running event.
- Completing a run records a completed event with outcome evidence.
- Failing a run records a failed event with error evidence.
- Fetching one run by id returns its events in chronological order.
- Recent-run listing remains compatible with the Operations page.
- Invalid requests are rejected before a run or event is created.
- The Operations UI can render a compact timeline for the selected run.

## Manual validation

If browser validation is requested:

- Open Operations.
- Run `runtime-health`.
- Confirm the operation result shows a run id, final evidence, and a lifecycle timeline.
- Reload the page and confirm recent runs still show durable evidence.

## Acceptance evidence

Record automated results, any browser observations, and any known limitations around polling versus streaming.
