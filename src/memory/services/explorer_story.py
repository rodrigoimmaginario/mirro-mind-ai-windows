"""In-session Explorer Mode story state.

The Explorer Story is intentionally stored in runtime state for the first
behavior slice. It is a live conversational field, not durable Explorer archive.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from memory.storage.store import Store

EXPLORER_STORY_SESSION_PREFIX = "__explorer_story__:"
_UNSET = object()


@dataclass(frozen=True)
class ExplorerAttractor:
    label: str
    description: str | None = None
    status: str = "proposed"


@dataclass(frozen=True)
class ExplorerExperimentProposal:
    title: str
    description: str | None = None
    status: str = "proposed"


@dataclass(frozen=True)
class ExplorerBuilderHandoff:
    title: str
    summary: str | None = None
    readiness: str = "proposed"
    artifact_dir: str | None = None
    exploratory_story_path: str | None = None
    handoff_info_path: str | None = None
    product_design_proposal_path: str | None = None


@dataclass(frozen=True)
class ExplorerStory:
    journey: str
    current_exploratory_story: str | None = None
    narrative_field_summary: str | None = None
    last_story_card: str | None = None
    attractors: tuple[ExplorerAttractor, ...] = ()
    experiment_proposal: ExplorerExperimentProposal | None = None
    builder_handoff: ExplorerBuilderHandoff | None = None


def _session_id(journey: str) -> str:
    normalized = journey.strip()
    if not normalized:
        raise ValueError("journey must not be empty")
    return f"{EXPLORER_STORY_SESSION_PREFIX}{normalized}"


def _clean(value: str | None | object) -> str | None | object:
    if value is _UNSET:
        return _UNSET
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def get_explorer_story(store: Store, journey: str) -> ExplorerStory | None:
    """Return the current in-session Explorer Story for a journey."""
    normalized_journey = journey.strip()
    if not normalized_journey:
        raise ValueError("journey must not be empty")
    session = store.get_runtime_session(_session_id(normalized_journey))
    if not session or not session.active or not session.metadata:
        return None
    try:
        data = json.loads(session.metadata)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None

    return ExplorerStory(
        journey=normalized_journey,
        current_exploratory_story=_string_or_none(data.get("current_exploratory_story")),
        narrative_field_summary=_string_or_none(data.get("narrative_field_summary")),
        last_story_card=_string_or_none(data.get("last_story_card")),
        attractors=_parse_attractors(data.get("attractors")),
        experiment_proposal=_parse_experiment(data.get("experiment_proposal")),
        builder_handoff=_parse_handoff(data.get("builder_handoff")),
    )


def update_explorer_story(
    store: Store,
    journey: str,
    *,
    current_exploratory_story: str | None | object = _UNSET,
    narrative_field_summary: str | None | object = _UNSET,
    last_story_card: str | None | object = _UNSET,
) -> ExplorerStory:
    """Create or update the in-session Explorer Story for a journey.

    Omitted fields preserve existing values. Explicit empty strings or None clear
    the corresponding scalar.
    """
    normalized_journey = journey.strip()
    if not normalized_journey:
        raise ValueError("journey must not be empty")
    existing = get_explorer_story(store, normalized_journey)

    story_value = _clean(current_exploratory_story)
    summary_value = _clean(narrative_field_summary)
    last_card_value = _clean(last_story_card)

    updated = ExplorerStory(
        journey=normalized_journey,
        current_exploratory_story=(
            existing.current_exploratory_story
            if story_value is _UNSET and existing
            else (None if story_value is _UNSET else story_value)
        ),
        narrative_field_summary=(
            existing.narrative_field_summary
            if summary_value is _UNSET and existing
            else (None if summary_value is _UNSET else summary_value)
        ),
        last_story_card=(
            existing.last_story_card
            if last_card_value is _UNSET and existing
            else (None if last_card_value is _UNSET else last_card_value)
        ),
        attractors=existing.attractors if existing else (),
        experiment_proposal=existing.experiment_proposal if existing else None,
        builder_handoff=existing.builder_handoff if existing else None,
    )

    _store_story(store, updated)
    return updated


def set_explorer_attractors(
    store: Store,
    journey: str,
    attractors: list[ExplorerAttractor],
) -> ExplorerStory:
    """Replace the visible attractors for the current Explorer Story."""
    normalized_journey = journey.strip()
    if not normalized_journey:
        raise ValueError("journey must not be empty")
    existing = get_explorer_story(store, normalized_journey)
    updated = ExplorerStory(
        journey=normalized_journey,
        current_exploratory_story=existing.current_exploratory_story if existing else None,
        narrative_field_summary=existing.narrative_field_summary if existing else None,
        last_story_card=existing.last_story_card if existing else None,
        attractors=tuple(_normalize_attractor(attractor) for attractor in attractors),
        experiment_proposal=existing.experiment_proposal if existing else None,
        builder_handoff=existing.builder_handoff if existing else None,
    )
    _store_story(store, updated)
    return updated


def set_explorer_experiment_proposal(
    store: Store,
    journey: str,
    proposal: ExplorerExperimentProposal,
) -> ExplorerStory:
    """Replace the visible experiment proposal for the current Explorer Story."""
    normalized_journey = journey.strip()
    if not normalized_journey:
        raise ValueError("journey must not be empty")
    existing = get_explorer_story(store, normalized_journey)
    updated = ExplorerStory(
        journey=normalized_journey,
        current_exploratory_story=existing.current_exploratory_story if existing else None,
        narrative_field_summary=existing.narrative_field_summary if existing else None,
        last_story_card=existing.last_story_card if existing else None,
        attractors=existing.attractors if existing else (),
        experiment_proposal=_normalize_experiment(proposal),
        builder_handoff=existing.builder_handoff if existing else None,
    )
    _store_story(store, updated)
    return updated


def set_explorer_builder_handoff(
    store: Store,
    journey: str,
    handoff: ExplorerBuilderHandoff,
) -> ExplorerStory:
    """Replace the visible Builder handoff proposal for the current story."""
    normalized_journey = journey.strip()
    if not normalized_journey:
        raise ValueError("journey must not be empty")
    existing = get_explorer_story(store, normalized_journey)
    updated = ExplorerStory(
        journey=normalized_journey,
        current_exploratory_story=existing.current_exploratory_story if existing else None,
        narrative_field_summary=existing.narrative_field_summary if existing else None,
        last_story_card=existing.last_story_card if existing else None,
        attractors=existing.attractors if existing else (),
        experiment_proposal=existing.experiment_proposal if existing else None,
        builder_handoff=_normalize_handoff(handoff),
    )
    _store_story(store, updated)
    return updated


def clear_explorer_story(store: Store, journey: str) -> None:
    """Clear the current in-session Explorer Story for a journey."""
    normalized_journey = journey.strip()
    if not normalized_journey:
        raise ValueError("journey must not be empty")
    store.upsert_runtime_session(
        _session_id(normalized_journey),
        interface="explorer_story",
        journey=normalized_journey,
        active=False,
        metadata=None,
    )


def render_explorer_story_context(story: ExplorerStory) -> str:
    """Render Explorer Story context for prompt injection or CLI inspection."""
    lines = ["=== △ Exploratory Story ===", f"journey: {story.journey}"]
    if story.current_exploratory_story:
        lines.extend(["", "current exploratory story:", story.current_exploratory_story])
    if story.narrative_field_summary:
        lines.extend(["", "narrative field summary:", story.narrative_field_summary])
    if story.last_story_card:
        lines.extend(["", "last story card:", story.last_story_card])
    if story.attractors:
        lines.extend(["", "attractors:"])
        for attractor in story.attractors:
            lines.append(f"- {attractor.label} [{attractor.status}]")
            if attractor.description:
                lines.append(f"  {attractor.description}")
    if story.experiment_proposal:
        lines.extend(
            [
                "",
                "experiment proposal:",
                f"{story.experiment_proposal.title} [{story.experiment_proposal.status}]",
            ]
        )
        if story.experiment_proposal.description:
            lines.append(story.experiment_proposal.description)
    if story.builder_handoff:
        lines.extend(
            [
                "",
                "builder handoff:",
                f"{story.builder_handoff.title} [{story.builder_handoff.readiness}]",
            ]
        )
        if story.builder_handoff.artifact_dir:
            lines.append(f"artifact_dir: {story.builder_handoff.artifact_dir}")
    return "\n".join(lines)


def _store_story(store: Store, story: ExplorerStory) -> None:
    store.upsert_runtime_session(
        _session_id(story.journey),
        interface="explorer_story",
        journey=story.journey,
        active=True,
        metadata=json.dumps(
            {
                "current_exploratory_story": story.current_exploratory_story,
                "narrative_field_summary": story.narrative_field_summary,
                "last_story_card": story.last_story_card,
                "attractors": [
                    {
                        "label": attractor.label,
                        "description": attractor.description,
                        "status": attractor.status,
                    }
                    for attractor in story.attractors
                ],
                "experiment_proposal": (
                    {
                        "title": story.experiment_proposal.title,
                        "description": story.experiment_proposal.description,
                        "status": story.experiment_proposal.status,
                    }
                    if story.experiment_proposal
                    else None
                ),
                "builder_handoff": (
                    {
                        "title": story.builder_handoff.title,
                        "summary": story.builder_handoff.summary,
                        "readiness": story.builder_handoff.readiness,
                        "artifact_dir": story.builder_handoff.artifact_dir,
                        "exploratory_story_path": story.builder_handoff.exploratory_story_path,
                        "handoff_info_path": story.builder_handoff.handoff_info_path,
                        "product_design_proposal_path": story.builder_handoff.product_design_proposal_path,
                    }
                    if story.builder_handoff
                    else None
                ),
            },
            ensure_ascii=False,
        ),
    )


def _parse_attractors(value: object) -> tuple[ExplorerAttractor, ...]:
    if not isinstance(value, list):
        return ()
    attractors = []
    for item in value:
        if not isinstance(item, dict):
            continue
        label = _string_or_none(item.get("label"))
        if not label:
            continue
        attractors.append(
            ExplorerAttractor(
                label=label,
                description=_string_or_none(item.get("description")),
                status=_valid_status(item.get("status")),
            )
        )
    return tuple(attractors)


def _parse_experiment(value: object) -> ExplorerExperimentProposal | None:
    if not isinstance(value, dict):
        return None
    title = _string_or_none(value.get("title"))
    if not title:
        return None
    return ExplorerExperimentProposal(
        title=title,
        description=_string_or_none(value.get("description")),
        status=_valid_status(value.get("status")),
    )


def _parse_handoff(value: object) -> ExplorerBuilderHandoff | None:
    if not isinstance(value, dict):
        return None
    title = _string_or_none(value.get("title"))
    if not title:
        return None
    return ExplorerBuilderHandoff(
        title=title,
        summary=_string_or_none(value.get("summary")),
        readiness=_valid_handoff_readiness(value.get("readiness")),
        artifact_dir=_string_or_none(value.get("artifact_dir")),
        exploratory_story_path=_string_or_none(value.get("exploratory_story_path")),
        handoff_info_path=_string_or_none(value.get("handoff_info_path")),
        product_design_proposal_path=_string_or_none(
            value.get("product_design_proposal_path")
        ),
    )


def _normalize_attractor(attractor: ExplorerAttractor) -> ExplorerAttractor:
    label = _string_or_none(attractor.label)
    if not label:
        raise ValueError("attractor label must not be empty")
    return ExplorerAttractor(
        label=label,
        description=_string_or_none(attractor.description),
        status=_valid_status(attractor.status),
    )


def _normalize_experiment(proposal: ExplorerExperimentProposal) -> ExplorerExperimentProposal:
    title = _string_or_none(proposal.title)
    if not title:
        raise ValueError("experiment title must not be empty")
    return ExplorerExperimentProposal(
        title=title,
        description=_string_or_none(proposal.description),
        status=_valid_status(proposal.status),
    )


def _normalize_handoff(handoff: ExplorerBuilderHandoff) -> ExplorerBuilderHandoff:
    title = _string_or_none(handoff.title)
    if not title:
        raise ValueError("builder handoff title must not be empty")
    return ExplorerBuilderHandoff(
        title=title,
        summary=_string_or_none(handoff.summary),
        readiness=_valid_handoff_readiness(handoff.readiness),
        artifact_dir=_string_or_none(handoff.artifact_dir),
        exploratory_story_path=_string_or_none(handoff.exploratory_story_path),
        handoff_info_path=_string_or_none(handoff.handoff_info_path),
        product_design_proposal_path=_string_or_none(
            handoff.product_design_proposal_path
        ),
    )


def _valid_status(value: object) -> str:
    if value in {"proposed", "accepted"}:
        return str(value)
    return "proposed"


def _valid_handoff_readiness(value: object) -> str:
    if value in {"proposed", "confirmed"}:
        return str(value)
    return "proposed"


def _string_or_none(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None
