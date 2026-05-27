[< CV13.E6](../index.md)

# CV13.E6.S5 — Approval checkpoint model

**Status:** ✅ Done
**Epic:** CV13.E6 — Async Operations and Agentic Web Console
**Release target:** v2.0

---

## User-visible outcome

Sensitive operation runs can pause before persistent writes, show that approval is required, and continue only after the user explicitly approves the run.

---

## Scope

- Add approval-required and approved lifecycle events.
- Add a guarded approval endpoint for operation runs.
- Route conversation repair apply runs through an approval checkpoint before mutation.
- Render approve action for approval-required runs.

---

## Non-goals

- No arbitrary write approval surface.
- No approval for raw SQL, shell, git, update, migration, or agent execution.
- No multi-approver workflow.

---

## Validation

Focused web/service tests plus ruff, node syntax, and diff checks.
