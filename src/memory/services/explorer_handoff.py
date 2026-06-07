"""Explorer to Builder handoff artifact writer."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from memory.services.explorer_story import ExplorerBuilderHandoff, ExplorerStory


def write_builder_handoff_artifacts(
    project_path: Path,
    story: ExplorerStory,
    *,
    title: str,
    summary: str | None = None,
    now: datetime | None = None,
) -> ExplorerBuilderHandoff:
    """Write Explorer handoff docs under a project's exploration folder."""
    timestamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    es_id = f"{timestamp}-{_slugify(story.journey)}"
    base = project_path / "docs" / "project" / "explorations" / es_id
    suffix = 2
    while base.exists():
        base = project_path / "docs" / "project" / "explorations" / f"{es_id}-{suffix}"
        suffix += 1
    base.mkdir(parents=True, exist_ok=False)

    exploratory_story_path = base / "exploratory-story.md"
    handoff_info_path = base / "handoff-info.md"
    product_design_path = base / "product-design-proposal.md"

    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    exploratory_story_path.write_text(
        _render_exploratory_story_doc(story, title=title, generated_at=generated_at),
        encoding="utf-8",
    )
    handoff_info_path.write_text(
        _render_handoff_info_doc(story, title=title, summary=summary, generated_at=generated_at),
        encoding="utf-8",
    )
    product_design_path.write_text(
        _render_product_design_doc(story, title=title, summary=summary, generated_at=generated_at),
        encoding="utf-8",
    )

    return ExplorerBuilderHandoff(
        title=title,
        summary=summary,
        readiness="proposed",
        artifact_dir=str(base),
        exploratory_story_path=str(exploratory_story_path),
        handoff_info_path=str(handoff_info_path),
        product_design_proposal_path=str(product_design_path),
    )


def _render_exploratory_story_doc(
    story: ExplorerStory, *, title: str, generated_at: str
) -> str:
    return f"""# Exploratory Story: {title}

## Source

- Journey: `{story.journey}`
- Mode: Explorer Mode
- Generated at: {generated_at}

## Current Exploratory Story

{story.current_exploratory_story or '_No story text recorded._'}

## Narrative Summary

{story.narrative_field_summary or '_No narrative summary recorded._'}

## Last Story Card

{story.last_story_card or '_No last story card recorded._'}

## Attractors

{_render_attractors(story)}

## Experiment Proposal

{_render_experiment(story)}

## Evolution Narrative

This document preserves the discovery path that Explorer Mode surfaced before Builder commitment. It should be read as exploratory context, not as a delivery plan.
"""


def _render_handoff_info_doc(
    story: ExplorerStory, *, title: str, summary: str | None, generated_at: str
) -> str:
    return f"""# Handoff Info: {title}

## Source

- Journey: `{story.journey}`
- Generated at: {generated_at}

## Handoff Summary

{summary or story.narrative_field_summary or '_No handoff summary recorded._'}

## Risks

- Builder may over-treat exploratory material as settled delivery scope.
- The product design proposal still needs Builder review and Navigator validation.

## Open Questions

- Which parts of this exploration should become roadmap stories?
- What validation route proves the product behavior externally?
- What should remain outside the first delivery slice?

## Boundaries

- This handoff is not a delivery plan.
- Builder must still read the project, create or update roadmap/story docs, and validate with the Navigator.
- Explorer preserved uncertainty; Builder should not erase it prematurely.

## Non-Assumptions

- Do not assume implementation architecture from this handoff.
- Do not assume all open questions are in scope.
- Do not assume the experiment proposal has already been validated.

## Attractors

{_render_attractors(story)}

## Experiment Status

{_render_experiment(story)}

## Promotion Boundary

Builder executes only after explicit confirmation from the Navigator.
"""


def _render_product_design_doc(
    story: ExplorerStory, *, title: str, summary: str | None, generated_at: str
) -> str:
    return f"""# Product Design Proposal: {title}

## Source

- Journey: `{story.journey}`
- Generated at: {generated_at}

## Product Intent

{summary or story.narrative_field_summary or '_No product intent summary recorded._'}

## User-Facing Behavior

{story.current_exploratory_story or '_No current story recorded._'}

## Interaction Flow

- User works in Explorer Mode while uncertainty is still alive.
- Explorer surfaces story changes visibly.
- Explorer names attractors and proposes small experiments.
- Explorer proposes Builder handoff only when the user asks or confirms readiness.
- Builder begins only after explicit confirmation.

## Product-Level States

- Exploratory Story active.
- Attractor proposed or accepted.
- Experiment proposal proposed or accepted.
- Builder handoff proposed.

## Acceptance Behavior

- The user can understand what is being proposed without reading implementation details.
- The proposal preserves uncertainty and open questions.
- The proposal gives Builder enough product shape to create roadmap or story plans.

## Explicit Non-Goals

- This document does not define implementation architecture.
- This document does not create delivery tasks by itself.
- This document does not replace Builder planning.

## Open Product Questions

- Which behavior is necessary for the first delivery slice?
- What should remain exploratory after Builder starts?
- What user validation will prove the product behavior works?
"""


def _render_attractors(story: ExplorerStory) -> str:
    if not story.attractors:
        return "_No attractors recorded._"
    lines: list[str] = []
    for attractor in story.attractors:
        lines.append(f"- **{attractor.label}** (`{attractor.status}`)")
        if attractor.description:
            lines.append(f"  - {attractor.description}")
    return "\n".join(lines)


def _render_experiment(story: ExplorerStory) -> str:
    proposal = story.experiment_proposal
    if not proposal:
        return "_No experiment proposal recorded._"
    lines = [f"**{proposal.title}** (`{proposal.status}`)"]
    if proposal.description:
        lines.append("")
        lines.append(proposal.description)
    return "\n".join(lines)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "exploration"
