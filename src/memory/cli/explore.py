"""Explorer Mode context loader.

First slice: activate Explorer Mode for a journey and return the normal Mirror
context plus exploratory operating instructions. Explorer state and story
thickening persistence are later CV16 stories.
"""

from __future__ import annotations

import argparse
import sys

from memory.client import MemoryClient
from memory.services.operating_mode import activate_mode, deactivate_mode
from memory.skills.mirror import _persist_global_sticky_defaults
from memory.surfaces.mode_transition import render_explorer_mode_transition

EXPLORER_GUIDANCE = """=== Explorer Mode guidance ===
Explorer Mode is experimental. The full Explorer experience is being built and will be available soon.

Explorer preserves uncertainty. Builder executes commitment.

While Explorer Mode is active:
- Treat new substantive material as part of the exploratory field unless the user asks for a clear operational action.
- Preserve signals, tensions, hypotheses, corrections, and emerging story shape.
- Render Story Thickened when new material changes the accumulated story.
- Do not promote to Builder or Delivery without explicit user confirmation.
"""

EXPLORER_DEACTIVATED_SURFACE = """Mirror
╭────────────────────────────────────────────────────────╮
│        △  EXPLORER MODE DEACTIVATED                    │
│                                                        │
│  current lens                                          │
│  ◌ Mirror Mode                                         │
│                                                        │
│  context                                               │
│  Journey context remains available when it is sticky.  │
│                                                        │
│  boundary                                              │
│  Explorer lens ended. Uncertainty was not promoted.    │
╰────────────────────────────────────────────────────────╯
"""


def cmd_load(slug: str) -> None:
    mem = MemoryClient()
    journey_content = mem.get_identity("journey", slug)
    if not journey_content:
        print(f"Error: journey '{slug}' not found.", file=sys.stderr)
        sys.exit(1)

    activate_mode(mem.store, mode="Explorer Mode", journey=slug)
    _persist_global_sticky_defaults(mem, persona=None, journey=slug)

    print(f"\033[38;5;183m△ Explorer Mode active — journey: {slug}\033[0m", file=sys.stderr)
    print(render_explorer_mode_transition(journey=slug))
    print(mem.load_mirror_context(journey=slug))
    print("\n" + EXPLORER_GUIDANCE)


def cmd_deactivate() -> None:
    mem = MemoryClient()
    deactivate_mode(mem.store)
    print(EXPLORER_DEACTIVATED_SURFACE)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Explorer Mode context loader")
    sub = parser.add_subparsers(dest="command", required=True)

    p_load = sub.add_parser("load", help="Activate Explorer Mode for a journey")
    p_load.add_argument("slug", help="Journey ID")

    sub.add_parser("deactivate", help="Deactivate Explorer Mode and return to Mirror Mode")

    args = parser.parse_args(argv)
    if args.command == "load":
        cmd_load(args.slug)
    elif args.command == "deactivate":
        cmd_deactivate()


if __name__ == "__main__":
    main()
