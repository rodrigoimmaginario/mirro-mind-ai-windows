"""Tests for Explorer Story user-facing surfaces."""

from memory.services.explorer_story import (
    ExplorerAttractor,
    ExplorerBuilderHandoff,
    ExplorerExperimentProposal,
    ExplorerStory,
)
from memory.surfaces.explorer_story import (
    render_attractors_emerging,
    render_builder_handoff_proposed,
    render_experiment_proposal,
    render_exploratory_story_opened,
    render_missing_exploratory_story,
    render_narrative_field_snapshot,
    render_no_builder_handoff,
    render_story_thickened,
)


def _story() -> ExplorerStory:
    return ExplorerStory(
        journey="explorer-mode",
        current_exploratory_story="Explorer centers on one accumulated story.",
        narrative_field_summary="Signals were removed from the first behavior slice.",
        last_story_card="The story became the observable unit.",
        attractors=(
            ExplorerAttractor(
                label="External validation",
                description="Validate behavior in Pi before internal modeling.",
            ),
        ),
        experiment_proposal=ExplorerExperimentProposal(
            title="Validate in Pi",
            description="Ask through natural language and inspect surfaces.",
        ),
        builder_handoff=ExplorerBuilderHandoff(
            title="Build Explorer persistence",
            summary="The exploration clarified the Builder boundary.",
            artifact_dir="/tmp/exploration",
            exploratory_story_path="/tmp/exploration/exploratory-story.md",
            handoff_info_path="/tmp/exploration/handoff-info.md",
            product_design_proposal_path="/tmp/exploration/product-design-proposal.md",
        ),
    )


def test_opened_surface_renders_story():
    rendered = render_exploratory_story_opened(_story())

    assert "△  EXPLORATORY STORY OPENED" in rendered
    assert "explorer-mode" in rendered
    assert "Explorer centers on one accumulated story." in rendered


def test_thickened_surface_renders_change_and_story():
    rendered = render_story_thickened(_story(), changed="External behavior became required.")

    assert "△  STORY THICKENED" in rendered
    assert "External behavior became required." in rendered
    assert "Explorer centers on one accumulated story." in rendered
    assert "Signals were removed" in rendered


def test_snapshot_surface_renders_current_field_with_directional_state():
    rendered = render_narrative_field_snapshot(_story())

    assert "△  NARRATIVE FIELD SNAPSHOT" in rendered
    assert "Explorer centers on one accumulated story." in rendered
    assert "The story became the observable unit." in rendered
    assert "External validation [proposed]" in rendered
    assert "Validate in Pi [proposed]" in rendered


def test_attractors_surface_renders_visible_direction():
    rendered = render_attractors_emerging(_story())

    assert "△  ATTRACTORS EMERGING" in rendered
    assert "External validation" in rendered
    assert "Validate behavior in Pi" in rendered
    assert "proposed" in rendered


def test_experiment_proposal_surface_renders_boundary():
    rendered = render_experiment_proposal(_story())

    assert "△  EXPERIMENT PROPOSAL" in rendered
    assert "Validate in Pi" in rendered
    assert "This is not Builder delivery" in rendered


def test_builder_handoff_surface_renders_artifacts_and_boundary():
    rendered = render_builder_handoff_proposed(_story())

    assert "△  BUILDER HANDOFF PROPOSED" in rendered
    assert "Build Explorer persistence" in rendered
    assert "exploratory-story.md" in rendered
    assert "handoff-info.md" in rendered
    assert "product-design-proposal.md" in rendered
    assert "Builder executes only after explicit confirmation" in rendered


def test_no_builder_handoff_surface_is_clear():
    rendered = render_no_builder_handoff(journey="explorer-mode")

    assert "△  NO BUILDER HANDOFF" in rendered
    assert "No Builder handoff proposal" in rendered


def test_missing_story_surface_is_clear():
    rendered = render_missing_exploratory_story(journey="explorer-mode")

    assert "△  NO EXPLORATORY STORY" in rendered
    assert "No current Exploratory Story" in rendered
