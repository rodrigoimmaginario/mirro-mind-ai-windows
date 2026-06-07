"""CLI for explicit Mirror operating mode lifecycle."""

from __future__ import annotations

import argparse

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home
from memory.services.operating_mode import activate_mode, deactivate_mode, get_active_mode


def _client(mirror_home: str | None) -> MemoryClient:
    if mirror_home:
        db_path = db_path_from_mirror_home(mirror_home)
        return MemoryClient(db_path=db_path)
    return MemoryClient()


def cmd_activate(args: argparse.Namespace) -> None:
    with _client(args.mirror_home) as mem:
        state = activate_mode(
            mem.store,
            mode=args.mode,
            journey=args.journey,
            session_id=args.session_id,
        )
    if state.journey:
        print(f"Activated {state.mode} for {state.journey}")
    else:
        print(f"Activated {state.mode}")


def cmd_deactivate(args: argparse.Namespace) -> None:
    with _client(args.mirror_home) as mem:
        deactivate_mode(mem.store, session_id=args.session_id)
    print("Deactivated active mode")


def cmd_status(args: argparse.Namespace) -> None:
    with _client(args.mirror_home) as mem:
        state = get_active_mode(mem.store, session_id=args.session_id)
    if not state:
        print("Mirror Mode")
    elif state.journey:
        print(f"{state.mode} · {state.journey}")
    else:
        print(state.mode)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Mirror operating mode lifecycle")
    parser.add_argument("--mirror-home", default=None, help="Explicit Mirror home")
    parser.add_argument("--session-id", default=None, help="Runtime session id")
    sub = parser.add_subparsers(dest="command", required=True)

    p_activate = sub.add_parser("activate", help="Activate an operating mode")
    p_activate.add_argument("mode", help="Mode label, e.g. 'Builder Mode'")
    p_activate.add_argument("--journey", default=None, help="Active journey slug")
    p_activate.set_defaults(func=cmd_activate)

    p_deactivate = sub.add_parser("deactivate", help="Deactivate the active operating mode")
    p_deactivate.set_defaults(func=cmd_deactivate)

    p_status = sub.add_parser("status", help="Show the active operating mode")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
