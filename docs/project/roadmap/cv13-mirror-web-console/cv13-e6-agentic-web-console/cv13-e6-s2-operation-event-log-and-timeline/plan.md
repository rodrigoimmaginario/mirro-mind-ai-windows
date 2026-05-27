[< Story](index.md)

# Plan — CV13.E6.S2 Operation event log and timeline

## Intent

Make asynchronous operation runs observable through durable lifecycle events. S1 introduced queued/running/completed states; S2 gives those transitions a visible timeline that later streaming, cancellation, approvals, command execution, and agent runs can reuse.

## Implementation outline

- Add an `operation_run_events` table with run id, sequence/order, kind, message, details JSON, and timestamp.
- Extend the operation run service with event recording and event listing.
- Emit events when a run is queued, starts running, completes, or fails.
- Include events in `OperationRun.to_dict()` or the single-run API payload.
- Update tests for migrations, service behavior, server responses, and guarded validation failures.
- Update the Operations UI to render the active/last run timeline without removing final result cards.

## Design notes

The event model should remain small and typed. It is evidence, not chatty logs. A useful initial event vocabulary is `queued`, `running`, `completed`, and `failed`.

Polling remains acceptable in this story. The API shape should make a future SSE stream an implementation detail rather than a new product concept.

## Risks

- Event details can become a dumping ground for raw output. Keep them concise.
- If event recording is tied too tightly to one execution path, later command/agent runs will need to duplicate it.
- UI timeline should not imply real streaming yet; it is a polled timeline.

## Documentation impact

- Mark S2 done after validation.
- Update the E6 epic story table.
- Add a worklog entry after validation.
