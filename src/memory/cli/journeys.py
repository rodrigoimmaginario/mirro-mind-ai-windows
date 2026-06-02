"""CLI: list journeys with status, stage, and description."""

import argparse
import re

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home


def _journey_row(mem: MemoryClient, option: dict[str, str]) -> dict[str, str]:
    name = option["id"]
    ident = mem.store.get_identity("journey", name)
    content = ident.content if ident else ""
    status = option.get("status") or "?"

    desc = ""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith(("## Description", "## Descrição")):
            continue
        if line and not line.startswith("#") and not line.startswith("**"):
            desc = line[:80]
            break

    journey_path_raw = mem.get_identity("journey_path", name)
    journey_path = journey_path_raw if isinstance(journey_path_raw, str) else ""
    stage_match = re.search(r"\*\*(?:Current stage|Etapa atual):\*\*\s*(.+)", journey_path)
    stage = stage_match.group(1).strip() if stage_match else "—"
    return {
        "id": name,
        "status": status,
        "stage": stage,
        "description": desc,
        "parent_journey": option.get("parent_journey") or "",
    }


def _print_journey(row: dict[str, str], *, child: bool = False) -> None:
    status = row["status"]
    icon = {"active": "🚧", "completed": "✅", "paused": "⏸"}.get(status, "•")
    prefix = "  └─ " if child else ""
    detail_indent = "       " if child else "  "
    print(f"{prefix}{icon} **{row['id']}** ({status})")
    print(f"{detail_indent}Stage: {row['stage']}")
    if row["description"]:
        print(f"{detail_indent}{row['description']}")
    print()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="List journeys with status and stage")
    parser.add_argument(
        "--mirror-home",
        default=None,
        help="Explicit user home whose database should be read for this command",
    )
    args = parser.parse_args(argv)

    mem = MemoryClient(db_path=db_path_from_mirror_home(args.mirror_home))
    options = mem.journeys.list_journey_options()

    if not options:
        print("No journeys found.")
        return

    rows = [_journey_row(mem, option) for option in options]
    by_parent: dict[str, list[dict[str, str]]] = {}
    roots: list[dict[str, str]] = []
    known_ids = {row["id"] for row in rows}
    for row in rows:
        parent = row.get("parent_journey") or ""
        if parent and parent in known_ids:
            by_parent.setdefault(parent, []).append(row)
        else:
            roots.append(row)

    for row in roots:
        _print_journey(row)
        for child in by_parent.get(row["id"], []):
            _print_journey(child, child=True)


if __name__ == "__main__":
    main()
