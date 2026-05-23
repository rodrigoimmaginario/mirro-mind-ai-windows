[< CV9.E3 Distribution & Tooling](../index.md)

# CV9.E3.S11 — Release Channel Operations Docs

**Epic:** CV9.E3 Distribution & Tooling
**Status:** ✅ Done
**User-visible outcome:** Users and operators can see how to switch between `stable` and `main`, understand branch/channel differences, and recover from common update-channel problems.

---

## What Changed

- `REFERENCE.md` now includes practical update-channel commands:
  - switch to `stable`;
  - switch to `main`;
  - remove the marker to return to the default;
  - verify the current channel.
- `REFERENCE.md` explains that local git branch and update channel are distinct.
- `docs/process/troubleshooting.md` now covers:
  - stable channel not fetched or unavailable;
  - `.mirror-update-channel` making older versions dirty;
  - welcome showing `main` unexpectedly;
  - missing release notes before the first prospective release.
- `origin/stable` was bootstrapped at the validated `6c58e9c` baseline.
- The production clone was switched to `.mirror-update-channel = stable` and validated with `runtime update --check`.

---

## Verification

```bash
uv run --extra dev ruff check src/ tests/
uv run --extra dev ruff format --check src/ tests/
git diff --check
```

Manual production validation:

```bash
uv run python -m memory runtime version
uv run python -m memory runtime update --check
uv run python -m memory welcome
```

Expected: `Update channel: stable`, `origin/stable`, `Availability: up_to_date`, and welcome line `Version ... · channel stable`.

---

## See also

- [Runtime Self-Update Reference](../../../../../../REFERENCE.md#runtime-self-update)
- [Troubleshooting](../../../../../process/troubleshooting.md)
