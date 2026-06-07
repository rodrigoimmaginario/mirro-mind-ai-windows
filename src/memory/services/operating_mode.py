"""Operating mode lifecycle state.

Operating modes are explicit Mirror lenses such as Builder Mode and Explorer
Mode. The state is session-scoped when a runtime session id is available, with a
legacy global fallback for CLI calls that do not know their session.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from memory.storage.store import Store

MODE_ICONS = {
    "Mirror Mode": "◌",
    "Builder Mode": "■",
    "Explorer Mode": "△",
}

MODE_STATE_SESSION_ID = "__global_operating_mode__"
MODE_METADATA_KEY = "operating_mode"


@dataclass(frozen=True)
class OperatingModeState:
    mode: str
    journey: str | None = None

    @property
    def label(self) -> str:
        icon = MODE_ICONS.get(self.mode)
        return f"{icon} {self.mode}" if icon else self.mode


def resolve_operating_session_id(
    store: Store, explicit_session_id: str | None = None
) -> str | None:
    """Resolve a runtime session id for session-scoped operating mode state."""
    if explicit_session_id:
        return explicit_session_id
    env_session = os.environ.get("MIRROR_SESSION_ID", "").strip()
    if env_session:
        return env_session
    row = store.conn.execute(
        """SELECT session_id FROM runtime_sessions
           WHERE active = 1
             AND session_id NOT IN (?, ?)
             AND interface IS NOT NULL
             AND interface != 'global_defaults'
           ORDER BY updated_at DESC
           LIMIT 1""",
        (MODE_STATE_SESSION_ID, "__global_sticky_defaults__"),
    ).fetchone()
    return row["session_id"] if row else None


def activate_mode(
    store: Store,
    *,
    mode: str,
    journey: str | None = None,
    session_id: str | None = None,
) -> OperatingModeState:
    """Activate an operating mode and return the stored state."""
    normalized_mode = mode.strip()
    if not normalized_mode:
        raise ValueError("mode must not be empty")
    normalized_journey = journey.strip() if isinstance(journey, str) and journey.strip() else None
    state = OperatingModeState(mode=normalized_mode, journey=normalized_journey)
    if session_id:
        _write_session_mode(store, session_id=session_id, state=state)
    else:
        _write_global_mode(store, state)
    return state


def deactivate_mode(store: Store, *, session_id: str | None = None) -> None:
    """Deactivate the current operating mode.

    With a session id, clears only that runtime session's operating lens. Without
    one, clears the legacy global operating-mode row. It does not mutate Mirror
    sticky persona/journey defaults or conversation routing.
    """
    if session_id:
        _clear_session_mode(store, session_id=session_id)
        return
    store.upsert_runtime_session(
        MODE_STATE_SESSION_ID,
        metadata=None,
        active=False,
    )


def get_active_mode(store: Store, *, session_id: str | None = None) -> OperatingModeState | None:
    """Return active operating mode state, if one exists."""
    if session_id:
        session_state = _read_session_mode(store, session_id=session_id)
        if session_state is not None:
            return session_state
    session = store.get_runtime_session(MODE_STATE_SESSION_ID)
    if not session or not session.active or not session.metadata:
        return None
    return _state_from_payload(_decode_metadata(session.metadata))


def _write_global_mode(store: Store, state: OperatingModeState) -> None:
    store.upsert_runtime_session(
        MODE_STATE_SESSION_ID,
        metadata=json.dumps(
            {
                "active_mode": state.mode,
                "active_journey": state.journey,
            },
            ensure_ascii=False,
        ),
        active=True,
    )


def _write_session_mode(store: Store, *, session_id: str, state: OperatingModeState) -> None:
    session = store.get_runtime_session(session_id)
    metadata = _decode_metadata(session.metadata if session else None)
    metadata[MODE_METADATA_KEY] = {
        "active_mode": state.mode,
        "active_journey": state.journey,
    }
    store.upsert_runtime_session(
        session_id,
        metadata=json.dumps(metadata, ensure_ascii=False),
        active=True,
    )


def _clear_session_mode(store: Store, *, session_id: str) -> None:
    session = store.get_runtime_session(session_id)
    if not session:
        return
    metadata = _decode_metadata(session.metadata)
    metadata.pop(MODE_METADATA_KEY, None)
    store.upsert_runtime_session(
        session_id,
        metadata=json.dumps(metadata, ensure_ascii=False) if metadata else None,
    )


def _read_session_mode(store: Store, *, session_id: str) -> OperatingModeState | None:
    session = store.get_runtime_session(session_id)
    if not session or not session.metadata:
        return None
    metadata = _decode_metadata(session.metadata)
    payload = metadata.get(MODE_METADATA_KEY)
    if not isinstance(payload, dict):
        return None
    return _state_from_payload(payload)


def _decode_metadata(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _state_from_payload(payload: dict[str, Any]) -> OperatingModeState | None:
    mode = payload.get("active_mode")
    if not isinstance(mode, str) or not mode.strip():
        return None
    journey = payload.get("active_journey")
    return OperatingModeState(
        mode=mode.strip(),
        journey=journey.strip() if isinstance(journey, str) and journey.strip() else None,
    )
