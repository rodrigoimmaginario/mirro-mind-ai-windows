[< Story](index.md)

# Plan — CV16.DS3 Explorer Activation Contract

## Boundary

This story makes the Explorer lens enterable and leaveable as an explicit operating contract. It does not implement exploratory memory, story thickening, signal radar, or promotion handoff.

The user-facing product interface is natural language. The CLI remains a contained operation Mirror can use to satisfy the user's declared intent.

## Current State

`python -m memory explore load <slug>` already:

- validates the journey exists;
- activates `Explorer Mode` in the operating-mode lifecycle;
- persists the journey as sticky context;
- renders the Explorer transition surface;
- loads Mirror identity and journey context;
- prints temporary Explorer guidance.

The missing pieces are:

- a deactivation operation scoped to Explorer semantics;
- stronger tests for the activation contract, especially that it does not create or switch conversations;
- skill instructions that make natural-language entry, exit, and promotion boundaries explicit;
- roadmap wiring for DS3.

## Implementation Direction

### Explorer CLI

Extend `src/memory/cli/explore.py` with a deactivation subcommand:

```bash
uv run python -m memory explore deactivate
```

or:

```bash
uv run python -m memory explore leave
```

The command should:

- call the existing operating-mode `deactivate_mode()` service;
- not clear sticky journey defaults;
- render a compact user-facing confirmation that the explicit Explorer lens ended;
- optionally show the resulting status line or Mirror Mode return copy.

Keep the generic `python -m memory mode deactivate` command intact. `explore deactivate` is a semantic wrapper for the user-facing skill contract.

### Pi skill contract

Update `.pi/skills/mm-explore/SKILL.md` so natural-language requests are the product surface:

```text
entrar em modo explorador nesta jornada
abrir exploração em explorer-mode
sair do modo explorador
voltar ao modo normal
promover essa exploração para construção
```

The skill should instruct Mirror to:

- run `uv run python -m memory explore load <slug>` for entry;
- render the transition surface copied from command output;
- run `uv run python -m memory explore deactivate` for exit;
- never promote to Builder without explicit confirmation.

### Activation contract tests

Extend `tests/unit/memory/cli/test_explore.py` to prove:

- `cmd_load()` activates Explorer Mode for a journey;
- `cmd_load()` persists sticky journey defaults;
- `cmd_load()` does not call Builder conversation switching and does not create a conversation row;
- `cmd_deactivate()` clears active mode but leaves sticky journey defaults intact;
- deactivation prints visible return/exit confirmation.

### Documentation wiring

Update `docs/project/roadmap/cv16-explorer-mode/index.md` so DS3 links to this story. Keep status planned until implementation and validation pass.

If behavior changes the public command reference, update `REFERENCE.md`. If the final deactivation command becomes part of user-visible CLI reference, mention it under `/mm-explore` or Operating Mode Lifecycle.

## Validation Route

Automated:

```bash
uv run pytest tests/unit/memory/cli/test_explore.py tests/unit/memory/services/test_operating_mode.py tests/unit/memory/cli/test_welcome.py
```

Lint:

```bash
uv run ruff check src/memory/cli/explore.py tests/unit/memory/cli/test_explore.py
```

Manual smoke:

```bash
uv run python -m memory explore load explorer-mode >/tmp/mirror-explore-load.txt
uv run python -m memory mode status
uv run python -m memory explore deactivate >/tmp/mirror-explore-deactivate.txt
uv run python -m memory mode status
uv run python -m memory welcome --status-line
```

Expected:

- activation output includes `△  EXPLORER MODE ACTIVE`;
- mode status after activation is `Explorer Mode · explorer-mode`;
- deactivation output visibly confirms Explorer Mode ended;
- mode status after deactivation falls back to `Mirror Mode`;
- welcome status still shows active journey on `◌ Mirror Mode` when sticky journey context remains.

## Risks

### Deactivation copy implies lost context

If the deactivation surface says the journey was cleared, it will be wrong. The command clears only the explicit lens. Sticky journey context remains.

### Accidental conversation mutation

Explorer activation should not behave like Builder activation if Builder switching creates or changes conversations. Add explicit tests so this boundary stays stable.

### Premature promotion behavior

The activation contract should mention promotion but not implement handoff. DS6 owns the Builder promotion brief.
