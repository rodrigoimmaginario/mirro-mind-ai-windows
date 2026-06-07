"""Tests for Explorer Mode CLI context loader."""

from memory import MemoryClient
from memory.cli import explore
from memory.config import default_db_path_for_home
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


def test_explore_deactivate_clears_mode_but_preserves_sticky_journey(
    mocker, tmp_path, capsys
):
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
