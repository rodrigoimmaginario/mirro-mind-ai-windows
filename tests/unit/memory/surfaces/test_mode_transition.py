"""Tests for mode transition surfaces."""

from memory.surfaces.mode_transition import (
    render_builder_mode_transition,
    render_explorer_mode_transition,
    render_mirror_mode_transition,
)


def test_mirror_mode_transition_shows_persona_examples_and_count():
    rendered = render_mirror_mode_transition(
        identity="alisson-vale",
        journey="explorer-mode",
        personas=["writer", "therapist", "engineer", "mentor"],
    )

    assert "◌  MIRROR MODE ACTIVE" in rendered
    assert "alisson-vale" in rendered
    assert "explorer-mode" in rendered
    assert "when the topic asks: engineer, mentor, therapist and 1" in rendered
    assert "more available" in rendered


def test_builder_mode_transition_shows_project_path_stage_and_briefing():
    rendered = render_builder_mode_transition(
        journey="explorer-mode",
        project_path="/tmp/mirror-dev",
        journey_content="""# Explorer Mode
**Status:** active
**Stage:** Product architecture

## Briefing
Build Explorer Mode as a native Mirror lens before construction.
""",
    )

    assert "■  BUILDER MODE ACTIVE" in rendered
    assert "explorer-mode" in rendered
    assert "/tmp/mirror-dev" in rendered
    assert "Product architecture" in rendered
    assert "Build Explorer Mode as a native Mirror lens" in rendered


def test_explorer_mode_transition_is_minimal():
    rendered = render_explorer_mode_transition(journey="explorer-mode")

    assert "△  EXPLORER MODE ACTIVE" in rendered
    assert "explorer-mode" in rendered
    assert "ready for durable" in rendered
    assert "exploration" in rendered
    assert "Explorer preserves uncertainty" in rendered
