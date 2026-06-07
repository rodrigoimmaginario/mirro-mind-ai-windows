"""Tests for Explorer Mode CLI context loader."""

from pathlib import Path

from memory import MemoryClient
from memory.cli import explore
from memory.config import default_db_path_for_home
from memory.models import Conversation, Message
from memory.services.explorer_story import get_explorer_story, update_explorer_story
from memory.services.operating_mode import activate_mode, get_active_mode

JOURNEY_CONTENT = """# Explorer Mode
**Status:** active

## Description
A journey for exploratory behavior.
"""


def test_explore_load_activates_explorer_mode_for_journey(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    mem.set_identity("journey", "explorer-mode", JOURNEY_CONTENT)
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)
    mocker.patch.object(mem, "load_mirror_context", return_value="context")

    explore.cmd_load("explorer-mode")

    state = get_active_mode(mem.store)
    assert state is not None
    assert state.mode == "Explorer Mode"
    assert state.journey == "explorer-mode"
    persona, journey = mem.store.get_global_sticky_defaults()
    assert persona is None
    assert journey == "explorer-mode"
    assert mem.store.list_recent_conversation_summaries(limit=10) == []
    out = capsys.readouterr().out
    assert "context" in out
    assert "Explorer preserves uncertainty" in out


def test_explore_deactivate_clears_mode_but_preserves_sticky_journey(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    mem.set_identity("journey", "explorer-mode", JOURNEY_CONTENT)
    activate_mode(mem.store, mode="Explorer Mode", journey="explorer-mode")
    mem.store.upsert_runtime_session(
        "__global_sticky_defaults__",
        interface="global_defaults",
        mirror_active=False,
        journey="explorer-mode",
        hook_injected=True,
        active=False,
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_deactivate()

    assert get_active_mode(mem.store) is None
    persona, journey = mem.store.get_global_sticky_defaults()
    assert persona is None
    assert journey == "explorer-mode"
    out = capsys.readouterr().out
    assert "EXPLORER MODE DEACTIVATED" in out
    assert "◌ Mirror Mode" in out


def test_story_update_command_stores_exploratory_story(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_update(
        "explorer-mode",
        story="Explorer is becoming observable.",
        summary="Runtime story state before persistence.",
        last_card="Story opened.",
    )

    stored = get_explorer_story(mem.store, "explorer-mode")
    assert stored is not None
    assert stored.current_exploratory_story == "Explorer is becoming observable."
    assert stored.narrative_field_summary == "Runtime story state before persistence."
    assert stored.last_story_card == "Story opened."
    out = capsys.readouterr().out
    assert "=== △ Exploratory Story ===" in out
    assert "Explorer is becoming observable." in out


def test_story_show_command_renders_stored_story(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer is becoming observable.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_show("explorer-mode")

    out = capsys.readouterr().out
    assert "=== △ Exploratory Story ===" in out
    assert "Explorer is becoming observable." in out


def test_story_clear_command_removes_stored_story(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer is becoming observable.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_clear("explorer-mode")

    assert get_explorer_story(mem.store, "explorer-mode") is None
    assert "Exploratory Story cleared" in capsys.readouterr().out


def test_explore_load_resumes_existing_exploratory_story(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    mem.set_identity("journey", "explorer-mode", JOURNEY_CONTENT)
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer is becoming observable.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)
    mocker.patch.object(mem, "load_mirror_context", return_value="context")

    explore.cmd_load("explorer-mode")

    out = capsys.readouterr().out
    assert "△  EXPLORATORY STORY RESUMED" in out
    assert "=== △ Exploratory Story ===" in out
    assert "Explorer is becoming observable." in out


def test_story_list_command_renders_durable_stories(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer is becoming observable.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_list("explorer-mode")

    out = capsys.readouterr().out
    assert "△  EXPLORATORY STORIES" in out
    assert "Explorer is becoming observable." in out
    assert "active" in out


def test_story_archive_command_archives_active_story(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Explorer is becoming observable.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_archive("explorer-mode")

    assert get_explorer_story(mem.store, "explorer-mode") is None
    out = capsys.readouterr().out
    assert "△  EXPLORATORY STORY ARCHIVED" in out
    assert "archived" in out


def test_story_open_command_stores_story_and_renders_surface(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_open(
        "explorer-mode",
        story="Explorer opens a visible story.",
        summary="Visible state, not only storage.",
        last_card="Opened.",
    )

    stored = get_explorer_story(mem.store, "explorer-mode")
    assert stored is not None
    assert stored.current_exploratory_story == "Explorer opens a visible story."
    out = capsys.readouterr().out
    assert "△  EXPLORATORY STORY OPENED" in out
    assert "Explorer opens a visible story." in out


def test_story_thicken_command_updates_story_and_renders_surface(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Initial story.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_thicken(
        "explorer-mode",
        story="Thickened story.",
        summary="A correction changed the shape.",
        last_card="Thickened.",
        changed="External behavior became required.",
    )

    stored = get_explorer_story(mem.store, "explorer-mode")
    assert stored is not None
    assert stored.current_exploratory_story == "Thickened story."
    out = capsys.readouterr().out
    assert "[[MIRROR_REQUIRED_SURFACE_BEGIN:story_thickened]]" in out
    assert "△  STORY THICKENED" in out
    assert "[[MIRROR_REQUIRED_SURFACE_END:story_thickened]]" in out
    assert "External behavior became required." in out
    assert "Thickened story." in out


def test_story_snapshot_command_renders_stored_story(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Current story.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_snapshot("explorer-mode")

    out = capsys.readouterr().out
    assert "△  NARRATIVE FIELD SNAPSHOT" in out
    assert "Current story." in out


def test_story_snapshot_command_handles_missing_story(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_snapshot("explorer-mode")

    out = capsys.readouterr().out
    assert "△  NO EXPLORATORY STORY" in out
    assert "No current Exploratory Story" in out


def test_story_attractors_command_stores_and_renders_surface(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Current story.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_attractors(
        "explorer-mode",
        attractor="External validation",
        description="Validate behavior in Pi before internal modeling.",
        status="proposed",
    )

    stored = get_explorer_story(mem.store, "explorer-mode")
    assert stored is not None
    assert stored.attractors[0].label == "External validation"
    out = capsys.readouterr().out
    assert "△  ATTRACTORS EMERGING" in out
    assert "External validation" in out


def test_story_experiment_command_stores_and_renders_surface(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    activate_mode(mem.store, mode="Explorer Mode", journey="explorer-mode")
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Current story.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_experiment(
        "explorer-mode",
        title="Validate in Pi",
        description="Ask through natural language and inspect surfaces.",
        status="proposed",
    )

    stored = get_explorer_story(mem.store, "explorer-mode")
    assert stored is not None
    assert stored.experiment_proposal is not None
    assert stored.experiment_proposal.title == "Validate in Pi"
    active_mode = get_active_mode(mem.store)
    assert active_mode is not None
    assert active_mode.mode == "Explorer Mode"
    out = capsys.readouterr().out
    assert "△  EXPERIMENT PROPOSAL" in out
    assert "This is not Builder delivery" in out


def test_story_snapshot_includes_attractor_and_experiment(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Current story.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)
    explore.cmd_story_attractors(
        "explorer-mode",
        attractor="External validation",
        description="Validate behavior in Pi before internal modeling.",
        status="proposed",
    )
    explore.cmd_story_experiment(
        "explorer-mode",
        title="Validate in Pi",
        description="Ask through natural language and inspect surfaces.",
        status="proposed",
    )
    capsys.readouterr()

    explore.cmd_story_snapshot("explorer-mode")

    out = capsys.readouterr().out
    assert "△  NARRATIVE FIELD SNAPSHOT" in out
    assert "External validation [proposed]" in out
    assert "Validate in Pi [proposed]" in out


def test_story_handoff_writes_source_evidence_and_full_conversation(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    project_path = tmp_path / "project"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    mem.set_identity("journey", "explorer-mode", JOURNEY_CONTENT)
    mem.journeys.set_project_path("explorer-mode", str(project_path))
    mem.store.create_conversation(
        Conversation(
            id="convsource1",
            title="Explorer source",
            interface="pi",
            journey="explorer-mode",
        )
    )
    mem.store.add_message(
        Message(
            conversation_id="convsource1",
            role="user",
            content="Source path /Users/alissonvale/Code/mirror and token=sk-secretvalue123456",
        )
    )
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Current story.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_handoff(
        "explorer-mode",
        title="Evidence handoff",
        summary="The exploration clarified evidence.",
        editorial_synthesis="The exploration continuously thickened around evidence.",
        source_conversation_ids=["convsource1:origin conversation"],
        include_full_conversation=True,
    )

    stored = get_explorer_story(mem.store, "explorer-mode")
    assert stored is not None
    assert stored.source_conversations[0].conversation_id == "convsource1"
    assert stored.builder_handoff is not None
    assert stored.builder_handoff.full_conversation_path is not None
    full_text = Path(stored.builder_handoff.full_conversation_path).read_text()
    assert "[LOCAL_PATH]" in full_text
    assert "token=[SECRET]" in full_text
    out = capsys.readouterr().out
    assert "[[MIRROR_REQUIRED_SURFACE_BEGIN:builder_handoff_proposed]]" in out
    assert "△  BUILDER HANDOFF PROPOSED" in out
    assert "[[MIRROR_REQUIRED_SURFACE_END:builder_handoff_proposed]]" in out
    assert "full-conversation.md" in out
    assert "source evidence" in out


def test_story_handoff_writes_docs_stores_and_renders_surface(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    project_path = tmp_path / "project"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    mem.set_identity("journey", "explorer-mode", JOURNEY_CONTENT)
    mem.journeys.set_project_path("explorer-mode", str(project_path))
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Current story.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)

    explore.cmd_story_handoff(
        "explorer-mode",
        title="Build Explorer persistence",
        summary="The exploration clarified the Builder boundary.",
        editorial_synthesis="The exploration continuously thickened around transfer docs.",
    )

    stored = get_explorer_story(mem.store, "explorer-mode")
    assert stored is not None
    assert stored.builder_handoff is not None
    assert stored.builder_handoff.title == "Build Explorer persistence"
    assert stored.builder_handoff.index_path is not None
    assert stored.builder_handoff.exploratory_story_path is not None
    assert "docs/project/explorations" in stored.builder_handoff.exploratory_story_path
    assert (project_path / "docs" / "project" / "explorations").is_dir()
    out = capsys.readouterr().out
    assert "△  BUILDER HANDOFF PROPOSED" in out
    assert "index.md" in out
    assert "exploratory-story.md" in out


def test_story_promote_requires_existing_handoff(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)
    build = mocker.patch("memory.cli.explore.build_cli.cmd_load")

    explore.cmd_story_promote("explorer-mode")

    build.assert_not_called()
    out = capsys.readouterr().out
    assert "△  NO BUILDER HANDOFF" in out


def test_story_promote_confirms_handoff_and_invokes_builder(mocker, tmp_path):
    mirror_home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(mirror_home))
    update_explorer_story(
        mem.store,
        "explorer-mode",
        current_exploratory_story="Current story.",
    )
    mocker.patch("memory.cli.explore.MemoryClient", return_value=mem)
    explore.cmd_story_handoff(
        "explorer-mode",
        title="Build Explorer persistence",
        summary="The exploration clarified the Builder boundary.",
        editorial_synthesis=None,
    )
    build = mocker.patch("memory.cli.explore.build_cli.cmd_load")

    explore.cmd_story_promote("explorer-mode")

    build.assert_called_once_with("explorer-mode")
    stored = get_explorer_story(mem.store, "explorer-mode")
    assert stored is None
    stories = mem.store.list_explorer_story_records("explorer-mode")
    assert stories[0]["status"] == "promoted"
    assert "confirmed" in stories[0]["builder_handoff_json"]
