[< CV13.E6](../index.md)

# CV13.E6.S2 — Operation event log and timeline

**Status:** ✅ Done
**Epic:** CV13.E6 — Async Operations and Agentic Web Console
**Release target:** v2.0

---

## User-visible outcome

The user can inspect an operation run as a timeline of durable events instead of only seeing a final status and result. The browser shows when a run was queued, started, completed, or failed, and preserves concise event details as evidence.

---

## Scope

- Add durable event storage for operation runs.
- Record lifecycle events for queued, running, completed, and failed transitions.
- Expose run events in the one-run inspection API.
- Render a compact event timeline in the Operations detail surface.
- Keep polling as the delivery mechanism for this story.
- Preserve the existing run history and final result cards.

---

## Non-goals

- No SSE or WebSocket streaming yet.
- No cancellation semantics.
- No approval checkpoints.
- No controlled command executor.
- No Pi/headless agent integration.
- No arbitrary shell command, SQL, git, or runtime update surface.

---

## Validation

See [test guide](test-guide.md).
