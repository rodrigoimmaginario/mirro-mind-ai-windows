[< CV13.E5](../index.md)

# CV13.E5.S2 — Runtime health operation

**Status:** ✅ Done
**Epic:** CV13.E5 — Web Operations Runner
**Release target:** v0.15.0

---

## User-visible outcome

The web app can run a read-only runtime health operation for the active local Mirror and receive structured status results without opening a terminal.

---

## Scope

- Mark the `runtime-health` catalog entry as runnable.
- Add a bounded operation execution endpoint for allowlisted operations.
- Implement only the `runtime-health` operation in this story.
- Reuse existing runtime status inspection logic instead of shelling out to the CLI command.
- Return structured status fields suitable for a future UI: overall status, version, repository, git state, mirror home, database state, migrations, extensions, clone role, Python version, environment, and update channel.
- Reject unknown operation ids and future operations.
- Keep the operation read-only.

---

## Non-goals

- No generic command execution.
- No subprocess execution for web operations.
- No audit persistence or operation history.
- No streaming.
- No backup creation.
- No repair, retitle, migration, update, extension install, or git mutation.
- No full Operations UI yet.

---

## Validation

See [test guide](test-guide.md).
