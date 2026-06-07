[< Story](index.md)

# Plan — CV16.DS7 Promotion Handoff to Builder

## Boundary

This story implements the explicit crossing from Explorer to Builder through a transfer artifact set. It should make the proposed crossing visible, write the exploration output docs, store the proposed handoff and artifact paths in runtime story state, and activate Builder only when the user confirms.

DS7 does not create durable Exploratory Story database records. DS8 will persist status such as `active`, `promoted`, or `archived` when Exploratory Stories become durable database records. DS7 writes project documents because Builder needs something concrete to read and transform into roadmap or story plans.

## Transfer Document Set

Explorer handoff output is a group of documents under:

```text
<project_path>/docs/project/explorations/<es-id>/
```

For DS7, `<es-id>` can be generated deterministically from timestamp plus journey slug, for example:

```text
20260606-173000-explorer-mode
```

DS8 can later replace or augment this with durable Exploratory Story IDs once ES records exist in the database.

The document set is:

```text
exploratory-story.md
handoff-info.md
product-design-proposal.md
```

### exploratory-story.md

Purpose: tell the discovery story as a narrative of exploratory evolution.

Content:

- title;
- source journey;
- generated timestamp;
- current Exploratory Story;
- narrative summary;
- last story card;
- attractors;
- experiment proposal;
- evolution narrative describing how the exploration changed.

This document preserves the path of discovery. It is not a spec and not a Builder plan.

### handoff-info.md

Purpose: tell Builder what is important to know before turning exploration into construction.

Content:

- risks;
- open questions;
- boundaries;
- non-assumptions;
- relevant attractors;
- experiment status;
- what Builder should not assume;
- validation expectations;
- promotion boundary.

This document protects uncertainty from being flattened into premature delivery.

### product-design-proposal.md

Purpose: describe what the product should look like from the user's perspective, without implementation detail.

Content:

- product intent;
- user-facing behavior;
- surfaces or interaction flow;
- states and transitions at the product level;
- acceptance behavior;
- explicit non-goals;
- open product questions.

This is a design proposal, not an architecture or implementation plan. Builder may use it to create roadmap stories, but should still do its own project reading and planning.

## State Model

Extend `src/memory/services/explorer_story.py` with:

```python
@dataclass(frozen=True)
class ExplorerBuilderHandoff:
    title: str
    summary: str | None = None
    readiness: str = "proposed"
    artifact_dir: str | None = None
    exploratory_story_path: str | None = None
    handoff_info_path: str | None = None
    product_design_proposal_path: str | None = None
```

Extend `ExplorerStory`:

```python
builder_handoff: ExplorerBuilderHandoff | None = None
```

Status/readiness values for DS7:

```text
proposed
confirmed
```

Store it in the existing runtime payload for `__explorer_story__:<journey>`. DS8 can later migrate or copy this into durable Exploratory Story records.

## Service Operations

Add:

```python
set_explorer_builder_handoff(store, journey, handoff: ExplorerBuilderHandoff) -> ExplorerStory
```

Semantics:

- preserves story, summary, last card, attractors, and experiment proposal;
- replaces the current handoff proposal;
- validates non-empty title;
- stores readiness as `proposed` unless explicitly `confirmed`.

## Artifact Generation

Add a small artifact writer, likely in `src/memory/services/explorer_handoff.py`:

```python
write_builder_handoff_artifacts(project_path: Path, story: ExplorerStory, *, title: str, summary: str | None) -> ExplorerBuilderHandoff
```

Responsibilities:

- create `docs/project/explorations/<es-id>/` under the journey project path;
- write the three markdown documents;
- avoid overwriting an existing directory by generating a unique id;
- return a handoff object with artifact paths;
- use deterministic markdown, no LLM calls.

If a journey has no project path, DS7 should still render a handoff proposal but report that no artifact directory was written. DS8 can later decide a Mirror-home fallback for durable non-project explorations.

## Surfaces

Extend `src/memory/surfaces/explorer_story.py` with:

```python
render_builder_handoff_proposed(story: ExplorerStory) -> str
```

Surface fields:

- journey;
- handoff title;
- why this is ready or what is being handed off;
- artifact directory when available;
- three document paths when available;
- current story excerpt;
- attractor when present;
- experiment proposal when present;
- boundary: `Builder executes only after explicit confirmation.`

Missing story/handoff behavior should be explicit. Use the existing missing story surface or a dedicated `△ NO BUILDER HANDOFF` surface if clearer.

## CLI Operations

Extend `python -m memory explore story`:

```bash
uv run python -m memory explore story handoff explorer-mode \
  --title "Build Explorer persistence" \
  --summary "The exploration clarified the next Builder boundary."

uv run python -m memory explore story promote explorer-mode
```

Semantics:

- `handoff` writes the transfer document set when `project_path` exists, stores a `proposed` handoff, and renders `△ BUILDER HANDOFF PROPOSED`.
- `promote` confirms the stored handoff and activates Builder Mode for the same journey.
- `promote` should reuse existing Builder load behavior where possible so the normal Builder transition surface, context, and `project_path=...` output remain consistent.
- If no handoff exists, `promote` should not activate Builder and should explain that a handoff proposal is needed first.

Implementation option:

- Keep `cmd_story_promote()` in `memory.cli.explore` as a thin wrapper around `memory.cli.build.cmd_load(slug)` after marking the handoff `confirmed` in runtime state.
- Avoid duplicating Builder context loading logic.

## Skill Contract

Update `.pi/skills/mm-explore/SKILL.md`:

- when the user asks “isso está pronto para Builder?” or “promover para Builder?”, first call `story handoff` and render the returned surface;
- show the three generated artifact paths;
- ask for explicit confirmation in the answer;
- only after the user confirms, call `story promote`;
- never call Builder directly from an unconfirmed exploratory turn.

## Tests

Service tests:

- setting builder handoff preserves story, attractor, and experiment fields;
- invalid empty handoff title raises;
- unknown readiness normalizes to `proposed`;
- artifact writer creates the three docs under `docs/project/explorations/<es-id>/`;
- artifact docs include story, handoff info, and product design proposal sections.

Surface tests:

- handoff surface includes title, summary, current story, attractor, experiment, artifact paths, and confirmation boundary;
- missing handoff/story behavior is clear.

CLI tests:

- `cmd_story_handoff` stores and renders handoff proposal;
- `cmd_story_handoff` writes the three docs when the journey has project path;
- `cmd_story_promote` does not activate Builder when no handoff exists;
- `cmd_story_promote` marks handoff confirmed and invokes Builder load when handoff exists;
- proposal command leaves active mode as Explorer.

## Validation Route

Automated:

```bash
uv run pytest \
  tests/unit/memory/services/test_explorer_story.py \
  tests/unit/memory/services/test_explorer_handoff.py \
  tests/unit/memory/surfaces/test_explorer_story.py \
  tests/unit/memory/cli/test_explore.py
```

Lint:

```bash
uv run ruff check \
  src/memory/services/explorer_story.py \
  src/memory/services/explorer_handoff.py \
  src/memory/surfaces/explorer_story.py \
  src/memory/cli/explore.py \
  tests/unit/memory/services/test_explorer_story.py \
  tests/unit/memory/services/test_explorer_handoff.py \
  tests/unit/memory/surfaces/test_explorer_story.py \
  tests/unit/memory/cli/test_explore.py
```

## User Validation in Pi

The Navigator validates DS7 as a user in Pi, without running internal commands.

Activate Explorer Mode:

```text
/mm-explore explorer-mode
```

Create or reuse an Exploratory Story with attractor and experiment proposal.

Ask for promotion:

```text
isso já está pronto para virar Builder?
```

Expected:

- assistant renders `△ BUILDER HANDOFF PROPOSED`;
- handoff includes story, attractor, and experiment proposal when available;
- surface shows generated paths for:
  - `exploratory-story.md`;
  - `handoff-info.md`;
  - `product-design-proposal.md`;
- assistant asks for explicit confirmation;
- footer/status remains on `△ Explorer Mode`.

Review the generated docs through the normal editor or file browser. Expected:

- `exploratory-story.md` tells the discovery narrative;
- `handoff-info.md` lists risks, open questions, boundaries, and non-assumptions;
- `product-design-proposal.md` describes product behavior without implementation detail.

Withhold confirmation:

```text
ainda não, vamos continuar explorando
```

Expected:

- active mode remains Explorer;
- the story can still be thickened;
- the transfer docs remain available for review.

Confirm promotion:

```text
sim, promover para Builder
```

Expected:

- assistant activates Builder Mode;
- response renders the normal `■ BUILDER MODE ACTIVE` transition surface;
- footer/status changes to Builder Mode for the same journey;
- Builder can read the generated transfer docs and use them to create roadmap or story docs.

If this was only validation, discard the test conversation before quitting:

```text
/mm-discard
```

## Risks

### Handoff becomes a delivery plan

The handoff should be enough for Builder to start reading and planning. It should not pretend to solve Builder planning inside Explorer.

### Product Design Proposal leaks implementation

The product design proposal must describe behavior and product shape, not architecture or implementation tasks.

### Silent promotion

Promotion must remain a two-step interaction. Proposal and confirmation are separate.

### Builder loading duplication

Reusing Builder load avoids drift. If direct reuse is awkward, keep the duplicated logic minimal and test the transition surface and mode state.
