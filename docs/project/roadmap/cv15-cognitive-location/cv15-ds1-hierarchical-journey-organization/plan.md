[< Story](index.md)

# Plan — CV15.DS1 Hierarchical Journey Organization

## Boundary

This story introduces one-level hierarchical organization for journeys. It is a
structural foundation for CV15, not the Scene experience itself.

The implementation must preserve existing journey semantics. Parent-child
relationships organize display and selection only. They do not merge memories,
conversations, tasks, attachments, Builder context, routing, extraction, or
search behavior.

## Design

### Metadata model

Use the existing journey identity metadata JSON:

```json
{
  "parent_journey": "mirror-mind"
}
```

This avoids schema migration and keeps parent assignment beside existing journey
configuration fields such as `project_path`, `sync_file`, `icon`, and `color`.

### Service layer

Extend `JourneyService` with helpers for parent validation and hierarchical
rendering data:

- `parent_journey` becomes an allowed journey metadata field.
- parent validation rejects unknown parent ids.
- parent validation rejects self-parenting.
- parent validation rejects parent journeys that already have a parent in this
  first one-level slice.
- creation and metadata update paths both use the same validation.
- journey option/read models include `parent_journey` so web and CLI rendering do
  not parse metadata independently.

### Web API

Extend existing web journey endpoints:

- `POST /api/journeys` accepts `parentJourney`.
- `POST /api/journeys/metadata` accepts `parentJourney`.
- conversation detail and unassigned payloads include journey options with parent
  metadata.

### Web UI

Add parent selection to:

- New journey review form.
- Journey Settings.

Render hierarchy consistently:

- Workspace journey sidebar groups children under parents.
- Journey dropdowns indent children and keep parent names visible.
- Existing selection behavior remains unchanged: selecting a child opens the
  child journey; selecting a parent opens the parent journey.

### Textual journey list

Update `python -m memory journeys` and therefore `mm-journeys` to render a
hierarchical tree, while preserving the existing status, stage, and description
information.

Example:

```text
🚧 **mirror-mind** (active)
  Stage: —
  Local-first memory and identity framework...
  └─ 🚧 **mirror-web-console** (active)
       Stage: —
       Web surface work...
```

## Risks

### Semantic bleed

Parent-child display could be misread as context inheritance. Mitigation: keep
code paths explicitly display-only and document non-goals in release notes.

### One-level constraint friction

Some users may want deeper nesting immediately. Mitigation: reject deeper nesting
with a clear error and preserve the simpler model until Scene exists.

### UI clutter

Hierarchical dropdowns can become harder to scan. Mitigation: indent children
lightly and keep existing alphabetical/status ordering inside each group.

## Implementation Slices

1. Service validation and read model support for `parent_journey`.
2. Web API and tests for create/update parent assignment.
3. Web UI parent selectors and hierarchical rendering.
4. CLI/textual hierarchical journey list.
5. Release note/version packaging for v0.20.0 after validation.

## Validation Route

See [Test Guide](test-guide.md).
