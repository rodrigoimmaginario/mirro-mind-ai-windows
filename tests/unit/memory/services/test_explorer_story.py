"""Tests for in-session Explorer Story state."""

from memory import MemoryClient
from memory.config import default_db_path_for_home
from memory.services.explorer_story import (
    ExplorerAttractor,
    ExplorerBuilderHandoff,
    ExplorerExperimentProposal,
    ExplorerSourceConversation,
    archive_explorer_story,
    clear_explorer_story,
    get_explorer_story,
    list_explorer_stories,
    mark_explorer_story_promoted,
    render_explorer_story_context,
    set_explorer_attractors,
    set_explorer_builder_handoff,
    set_explorer_experiment_proposal,
    set_explorer_source_conversations,
    update_explorer_story,
)


def _client(tmp_path):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    return MemoryClient(db_path=default_db_path_for_home(mirror_home))


def test_update_creates_explorer_story_for_journey(tmp_path):
    mem = _client(tmp_path)

    story = update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer is becoming observable.",
        narrative_field_summary="Runtime story state before persistence.",
        last_story_card="Story opened.",
    )

    assert story.journey == "explorer-mode"
    assert story.current_exploratory_story == "Explorer is becoming observable."
    assert story.narrative_field_summary == "Runtime story state before persistence."
    assert story.last_story_card == "Story opened."

    loaded = get_explorer_story(mem.store, "explorer-mode")
    assert loaded == story


def test_update_preserves_omitted_fields(tmp_path):
    mem = _client(tmp_path)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Initial story.",
        narrative_field_summary="Initial summary.",
        last_story_card="Initial card.",
    )

    updated = update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Thickened story.",
    )

    assert updated.current_exploratory_story == "Thickened story."
    assert updated.narrative_field_summary == "Initial summary."
    assert updated.last_story_card == "Initial card."


def test_update_can_clear_explicit_scalar(tmp_path):
    mem = _client(tmp_path)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Initial story.",
        narrative_field_summary="Initial summary.",
    )

    updated = update_explorer_story(
        mem.store,
        "explorer-mode",
        narrative_field_summary="",
    )

    assert updated.current_exploratory_story == "Initial story."
    assert updated.narrative_field_summary is None


def test_explorer_stories_are_isolated_by_journey(tmp_path):
    mem = _client(tmp_path)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer story.",
    )
    update_explorer_story(
        mem.store,
        "mirror-mind",
        current_exploratory_story="Mirror story.",
    )

    explorer = get_explorer_story(mem.store, "explorer-mode")
    mirror = get_explorer_story(mem.store, "mirror-mind")

    assert explorer is not None
    assert mirror is not None
    assert explorer.current_exploratory_story == "Explorer story."
    assert mirror.current_exploratory_story == "Mirror story."


def test_story_persists_across_clients(tmp_path):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(db_path=db_path)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer story survives a new client.",
    )
    mem.close()

    reopened = MemoryClient(db_path=db_path)

    loaded = get_explorer_story(reopened.store, "explorer-mode")
    assert loaded is not None
    assert loaded.id is not None
    assert loaded.status == "active"
    assert loaded.current_exploratory_story == "Explorer story survives a new client."


def test_clear_explorer_story_archives_active_story(tmp_path):
    mem = _client(tmp_path)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer story.",
    )

    clear_explorer_story(mem.store, "explorer-mode")

    assert get_explorer_story(mem.store, "explorer-mode") is None
    stories = list_explorer_stories(mem.store, "explorer-mode")
    assert len(stories) == 1
    assert stories[0].status == "archived"


def test_archive_active_story_allows_new_active_story(tmp_path):
    mem = _client(tmp_path)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="First story.",
    )

    archived = archive_explorer_story(mem.store, "explorer-mode")
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Second story.",
    )

    assert archived is not None
    assert archived.status == "archived"
    stories = list_explorer_stories(mem.store, "explorer-mode")
    assert [story.status for story in stories] == ["active", "archived"]
    assert stories[0].current_exploratory_story == "Second story."


def test_mark_promoted_removes_active_story_and_preserves_history(tmp_path):
    mem = _client(tmp_path)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Promoted story.",
    )

    promoted = mark_explorer_story_promoted(mem.store, "explorer-mode")

    assert promoted is not None
    assert promoted.status == "promoted"
    assert get_explorer_story(mem.store, "explorer-mode") is None
    assert list_explorer_stories(mem.store, "explorer-mode")[0].status == "promoted"


def test_invalid_metadata_returns_none(tmp_path):
    mem = _client(tmp_path)
    mem.store.upsert_runtime_session(
        "__explorer_story__:explorer-mode",
        interface="explorer_story",
        journey="explorer-mode",
        active=True,
        metadata="{invalid-json",
    )

    assert get_explorer_story(mem.store, "explorer-mode") is None


def test_setting_attractors_preserves_story_fields(tmp_path):
    mem = _client(tmp_path)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer is becoming observable.",
        narrative_field_summary="Runtime story state before persistence.",
    )

    updated = set_explorer_attractors(
        mem.store,
        "explorer-mode",
        [
            ExplorerAttractor(
                label="External validation",
                description="Validate behavior in Pi before internal modeling.",
            )
        ],
    )

    assert updated.current_exploratory_story == "Explorer is becoming observable."
    assert updated.narrative_field_summary == "Runtime story state before persistence."
    assert len(updated.attractors) == 1
    assert updated.attractors[0].label == "External validation"
    assert updated.attractors[0].status == "proposed"


def test_setting_attractors_replaces_existing_attractors(tmp_path):
    mem = _client(tmp_path)
    set_explorer_attractors(
        mem.store,
        "explorer-mode",
        [ExplorerAttractor(label="Old attractor")],
    )

    updated = set_explorer_attractors(
        mem.store,
        "explorer-mode",
        [ExplorerAttractor(label="Corrected attractor", status="accepted")],
    )

    assert [attractor.label for attractor in updated.attractors] == ["Corrected attractor"]
    assert updated.attractors[0].status == "accepted"


def test_setting_experiment_preserves_attractors_and_story(tmp_path):
    mem = _client(tmp_path)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer is becoming observable.",
    )
    set_explorer_attractors(
        mem.store,
        "explorer-mode",
        [ExplorerAttractor(label="External validation")],
    )

    updated = set_explorer_experiment_proposal(
        mem.store,
        "explorer-mode",
        ExplorerExperimentProposal(
            title="Validate in Pi",
            description="Ask through natural language and inspect surfaces.",
        ),
    )

    assert updated.current_exploratory_story == "Explorer is becoming observable."
    assert updated.attractors[0].label == "External validation"
    assert updated.experiment_proposal is not None
    assert updated.experiment_proposal.title == "Validate in Pi"


def test_setting_source_conversations_persists_evidence(tmp_path):
    mem = _client(tmp_path)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer is becoming observable.",
    )

    updated = set_explorer_source_conversations(
        mem.store,
        "explorer-mode",
        [
            ExplorerSourceConversation(
                conversation_id="conv-123",
                title="Explorer validation",
                role="origin conversation",
            )
        ],
    )

    assert updated.source_conversations[0].conversation_id == "conv-123"
    loaded = get_explorer_story(mem.store, "explorer-mode")
    assert loaded is not None
    assert loaded.source_conversations[0].title == "Explorer validation"


def test_setting_builder_handoff_preserves_story_directional_state(tmp_path):
    mem = _client(tmp_path)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer is becoming observable.",
    )
    set_explorer_attractors(
        mem.store,
        "explorer-mode",
        [ExplorerAttractor(label="External validation")],
    )
    set_explorer_experiment_proposal(
        mem.store,
        "explorer-mode",
        ExplorerExperimentProposal(title="Validate in Pi"),
    )

    updated = set_explorer_builder_handoff(
        mem.store,
        "explorer-mode",
        ExplorerBuilderHandoff(
            title="Build Explorer persistence",
            summary="The exploration clarified the Builder boundary.",
            artifact_dir="/tmp/handoff",
        ),
    )

    assert updated.current_exploratory_story == "Explorer is becoming observable."
    assert updated.attractors[0].label == "External validation"
    assert updated.experiment_proposal is not None
    assert updated.builder_handoff is not None
    assert updated.builder_handoff.title == "Build Explorer persistence"
    assert updated.builder_handoff.readiness == "proposed"


def test_setting_builder_handoff_rejects_empty_title(tmp_path):
    mem = _client(tmp_path)

    try:
        set_explorer_builder_handoff(
            mem.store,
            "explorer-mode",
            ExplorerBuilderHandoff(title=" "),
        )
    except ValueError as exc:
        assert "builder handoff title" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_render_explorer_story_context_includes_directional_state(tmp_path):
    mem = _client(tmp_path)
    story = update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer is becoming observable.",
        narrative_field_summary="Runtime story state before persistence.",
        last_story_card="Story opened.",
    )
    story = set_explorer_attractors(
        mem.store,
        "explorer-mode",
        [ExplorerAttractor(label="External validation")],
    )
    story = set_explorer_experiment_proposal(
        mem.store,
        "explorer-mode",
        ExplorerExperimentProposal(title="Validate in Pi"),
    )
    story = set_explorer_builder_handoff(
        mem.store,
        "explorer-mode",
        ExplorerBuilderHandoff(title="Build Explorer persistence", artifact_dir="/tmp/handoff"),
    )

    rendered = render_explorer_story_context(story)

    assert "=== △ Exploratory Story ===" in rendered
    assert "journey: explorer-mode" in rendered
    assert "Explorer is becoming observable." in rendered
    assert "External validation [proposed]" in rendered
    assert "Validate in Pi [proposed]" in rendered
    assert "Build Explorer persistence [proposed]" in rendered
    assert "artifact_dir: /tmp/handoff" in rendered
