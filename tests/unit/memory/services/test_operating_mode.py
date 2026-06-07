"""Tests for explicit operating mode lifecycle state."""

from memory import MemoryClient
from memory.config import default_db_path_for_home
from memory.services.operating_mode import activate_mode, deactivate_mode, get_active_mode


def test_operating_mode_can_be_activated_and_deactivated(tmp_path):
    home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(home))

    activate_mode(mem.store, mode="Builder Mode", journey="explorer-mode")

    state = get_active_mode(mem.store)
    assert state is not None
    assert state.mode == "Builder Mode"
    assert state.label == "■ Builder Mode"
    assert state.journey == "explorer-mode"

    deactivate_mode(mem.store)

    assert get_active_mode(mem.store) is None


def test_operating_mode_can_be_scoped_by_session(tmp_path):
    home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(home))
    mem.store.upsert_runtime_session("sess-a", interface="pi", active=True)
    mem.store.upsert_runtime_session("sess-b", interface="pi", active=True)

    activate_mode(
        mem.store,
        mode="Builder Mode",
        journey="explorer-mode",
        session_id="sess-a",
    )
    activate_mode(
        mem.store,
        mode="Explorer Mode",
        journey="mirror-4-teams",
        session_id="sess-b",
    )

    state_a = get_active_mode(mem.store, session_id="sess-a")
    state_b = get_active_mode(mem.store, session_id="sess-b")
    assert state_a is not None
    assert state_a.mode == "Builder Mode"
    assert state_a.journey == "explorer-mode"
    assert state_b is not None
    assert state_b.mode == "Explorer Mode"
    assert state_b.journey == "mirror-4-teams"


def test_deactivate_mode_clears_only_session_scope(tmp_path):
    home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(home))
    mem.store.upsert_runtime_session("sess-a", interface="pi", active=True)
    mem.store.upsert_runtime_session("sess-b", interface="pi", active=True)
    activate_mode(mem.store, mode="Builder Mode", journey="explorer-mode", session_id="sess-a")
    activate_mode(mem.store, mode="Explorer Mode", journey="mirror-4-teams", session_id="sess-b")

    deactivate_mode(mem.store, session_id="sess-a")

    assert get_active_mode(mem.store, session_id="sess-a") is None
    assert get_active_mode(mem.store, session_id="sess-b") is not None


def test_operating_mode_does_not_pollute_sticky_journey_defaults(tmp_path):
    home = tmp_path / ".mirror" / "alisson-vale"
    mem = MemoryClient(db_path=default_db_path_for_home(home))

    activate_mode(mem.store, mode="Builder Mode", journey="explorer-mode")

    assert mem.store.get_latest_runtime_defaults() == (None, None)
