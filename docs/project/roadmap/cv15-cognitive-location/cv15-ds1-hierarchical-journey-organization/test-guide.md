[< Story](index.md)

# Test Guide — CV15.DS1 Hierarchical Journey Organization

## Automated Checks

Run the focused tests while developing:

```bash
uv run pytest tests/unit/memory/services/test_journey.py tests/unit/memory/web/test_server.py tests/unit/memory/surfaces/test_workspace.py tests/unit/memory/cli/test_journeys.py -q
uv run ruff check src/memory/services/journey.py src/memory/web/server.py src/memory/surfaces/workspace.py src/memory/cli/journeys.py tests/unit/memory/services/test_journey.py tests/unit/memory/web/test_server.py tests/unit/memory/surfaces/test_workspace.py tests/unit/memory/cli/test_journeys.py
uv run ruff format --check src/ tests/
node --check src/memory/web/static/app.js
```

Before release packaging, run:

```bash
uv run pytest -q
uv run ruff check .
uv run ruff format --check src/ tests/
node --check src/memory/web/static/app.js
uv run python -m memory runtime release-notes latest
uv run python -m memory runtime release-doctor --target v0.20.0 --stable origin/stable
```

## Manual Browser Validation

Start or restart the local web console after web changes:

```bash
~/restart-mirror-web.sh
```

Then validate:

1. Open Workspace.
2. Create or use three test journeys:
   - one parent journey;
   - two child journeys with that parent.
3. Confirm the Workspace journey sidebar renders children under the parent.
4. Open the parent journey and confirm only the parent journey's own content is shown.
5. Open a child journey and confirm it remains independently selectable.
6. Open Journey Settings and change a journey parent.
7. Open New journey and confirm the parent selector can set a parent at creation.
8. Open Unassigned conversations and conversation detail journey selectors and confirm child journeys appear indented/grouped.

## Manual CLI Validation

Run:

```bash
uv run python -m memory journeys
```

Expected result:

- parent journeys render at the top level;
- child journeys render nested underneath their parent;
- status, stage, and description remain visible;
- journeys without a parent remain top-level.

## Safety Checks

Validate rejected parent assignments:

- unknown parent journey;
- parent set to self;
- deeper nesting attempt in the first one-level slice.

Expected result: the operation fails with a clear error and no partial metadata
mutation.
