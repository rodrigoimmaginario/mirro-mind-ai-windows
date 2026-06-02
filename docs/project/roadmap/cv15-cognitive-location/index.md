[< Roadmap](../index.md)

# CV15 — Cognitive Location

**Status:** 🟢 Planned  
**Source exploration:** [ES-002 Hierarchical Journeys](../../exploration/es-002-hierarchical-journeys.md)  
**Release intent:** two minor releases after v0.19.x

---

## What This Is

CV15 turns the Workspace from a flat journey browser into a surface that returns
cognitive location: where the user is situated now, which broader field contains
that movement, and which horizons are currently alive.

The capability starts pragmatically with one-level hierarchical journeys. Journey
remains the operational primitive for conversations, memories, tasks, Builder
context, routing, and extraction. The parent-child relationship organizes the
field without automatically merging semantic context.

Once the hierarchy is stable, Workspace gains **Scene**: a composed surface that
interprets the journey field and answers “where am I now?” through a journey map,
recent movement, horizons, and grounded LLM synthesis.

---

## Core Distinction

```text
Data primitive: Journey
Relationship: parent_journey
Surface: Scene
Meaning: cognitive location
Synthesis: grounded orientation
```

Hierarchical journeys organize the field. Scene interprets the field.

---

## Release Path

| Target | Story | Outcome | Status |
|--------|-------|---------|--------|
| v0.20.0 | [Hierarchical Journey Organization](cv15-ds1-hierarchical-journey-organization/index.md) | Users can set parent journeys and see journeys rendered hierarchically across web and Mirror textual surfaces | ✅ Done |
| v0.21.0 | Scene Workspace Home | Workspace opens as Scene, using the hierarchical journey map, movement signals, horizons, and bounded LLM synthesis to return cognitive location | 🟡 Planned |

Version numbers are release intents. They may shift if urgent patches land first,
but the stories should remain separate: the hierarchy foundation must exist
before Scene synthesis depends on it.

---

## Story 1 — Hierarchical Journey Organization

**Status:** ✅ Done
**Release:** [v0.20.0](../../../releases/v0.20.0.md)

### Outcome

The user can organize journeys under one parent level and see that organization
wherever journeys are listed.

### Scope

- Add `parent_journey` support to journey metadata.
- Allow setting parent journey during **New journey** creation.
- Allow editing parent journey in Journey Settings.
- Validate parent assignment:
  - parent exists;
  - journey cannot parent itself;
  - first slice supports only one level;
  - no cycles.
- Render journeys hierarchically across web surfaces:
  - Workspace journey navigation;
  - journey selection dropdowns;
  - conversation assignment dropdowns;
  - any other web journey lists.
- Render journeys hierarchically in textual Mirror surfaces:
  - `mm-journeys` / `python -m memory journeys`;
  - natural-language journey-list responses should prefer hierarchical rendering.

### Non-goals

- No Scene surface yet.
- No LLM synthesis yet.
- No automatic context inheritance from parent to child.
- No conversation, memory, task, attachment, Builder, routing, or extraction merging.
- No journey slug rename or deletion cascade.

---

## Story 2 — Scene Workspace Home

**Release intent:** v0.21.0

### Outcome

Workspace returns cognitive location instead of only listing and drilling into
journeys.

### Scope

- Make **Scene** the default Workspace home.
- Use Scene as the home shown when the user clicks a specific journey.
- Compose a deterministic Scene read model from:
  - journey tree;
  - selected journey, when present;
  - parent and sibling relationships;
  - stage, current focus, and description;
  - recent conversations;
  - recent memories and decisions;
  - open tasks where available.
- Add bounded LLM synthesis from the deterministic Scene read model.
- Show the signals used for synthesis.
- Provide fallback behavior when synthesis fails or is unavailable.

### Non-goals

- No automatic memory/routing/Builder context mixing across parent and child.
- No hidden semantic inference that changes journey assignment.
- No user-managed Scene entity.
- No recursive hierarchy beyond the foundation delivered in Story 1.

---

## Done Condition

CV15 is done when:

- Journey hierarchy can be created and maintained through safe service and web paths.
- Journey hierarchy is rendered consistently in web and textual Mirror surfaces.
- Workspace has a Scene home that answers “where am I now?” from existing Mirror data.
- Scene synthesis is grounded in a bounded read model and clearly distinguishes interpretation from source signals.
- Parent-child relationships do not silently merge memories, conversations, tasks, Builder context, routing, or extraction semantics.
