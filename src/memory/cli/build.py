"""Build skill: DB-only context loader for Builder Mode."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from memory.cli.conversation_logger import switch_conversation
from memory.cli.runtime import inspect_clone_role
from memory.client import MemoryClient
from memory.services.operating_mode import activate_mode, resolve_operating_session_id
from memory.skills.mirror import _persist_global_sticky_defaults
from memory.surfaces.mode_transition import render_builder_mode_transition


def _print_builder_banner(slug: str, project_path: str | None = None) -> None:
    print(f"\033[38;5;117m⚙ Builder Mode active — journey: {slug}\033[0m", file=sys.stderr)
    if project_path:
        print(f"\033[38;5;117m  📁 {project_path}\033[0m", file=sys.stderr)


def _extract_query(journey_content: str, slug: str) -> str:
    lines = journey_content.splitlines()
    sections = ["description", "briefing", "context", "descrição", "contexto"]
    result = []
    capturing = False
    for line in lines:
        header = line.lstrip("#").strip().lower()
        if any(s in header for s in sections):
            capturing = True
            continue
        if capturing:
            if line.startswith("#"):
                break
            result.append(line)
    text = " ".join(result).strip()
    return text[:500] if text else slug


def _is_mirror_mind_checkout(start: Path | None = None) -> bool:
    """Return True when ``start`` is inside a Mirror Mind source checkout."""
    start_path = (start or Path.cwd()).expanduser().resolve()
    candidates = (start_path, *start_path.parents)
    for candidate in candidates:
        pyproject = candidate / "pyproject.toml"
        memory_package = candidate / "src" / "memory"
        if not pyproject.is_file() or not memory_package.is_dir():
            continue
        try:
            pyproject_text = pyproject.read_text(encoding="utf-8")
        except OSError:
            return False
        return 'name = "mirror"' in pyproject_text
    return False


def _check_clone_role_guard(
    *, ignore_production_role: bool, project_path: str | None = None
) -> None:
    role_start = Path(project_path) if project_path else None
    if not _is_mirror_mind_checkout(role_start):
        return
    role = inspect_clone_role(role_start)
    if not role.is_production:
        return
    if ignore_production_role:
        print(
            "\033[38;5;208m⚠️  Production clone override: --ignore-production-role passed.\033[0m",
            file=sys.stderr,
        )
        return
    source = role.source if role.source is not None else "<default: missing marker>"
    print(
        "Builder Mode refused: the journey project clone is marked 'production'.\n"
        f"  Project path: {project_path or '<current directory>'}\n"
        f"  Clone role source: {source}\n"
        "  Development should happen in a clone marked 'dev'.\n"
        "  To proceed here anyway, pass --ignore-production-role.",
        file=sys.stderr,
    )
    sys.exit(2)


def cmd_load(
    slug: str,
    *,
    ignore_production_role: bool = False,
    session_id: str | None = None,
) -> None:
    mem = MemoryClient()

    journey_content = mem.get_identity("journey", slug)
    if not journey_content:
        print(f"Error: journey '{slug}' not found.", file=sys.stderr)
        sys.exit(1)

    project_path = mem.journeys.get_project_path(slug)
    _check_clone_role_guard(
        ignore_production_role=ignore_production_role,
        project_path=project_path,
    )
    _print_builder_banner(slug, project_path)
    print(
        render_builder_mode_transition(
            journey=slug,
            journey_content=journey_content,
            project_path=project_path,
        )
    )

    context = mem.load_mirror_context(persona="engineer", journey=slug)
    print(context)

    raw_content = journey_content if isinstance(journey_content, str) else slug
    query_text = _extract_query(raw_content, slug)
    scoped = mem.search(query_text, limit=5, journey=slug)
    global_ = mem.search(query_text, limit=5)
    seen_ids: set[str] = set()
    merged: list = []
    for memory, score in scoped + global_:
        if memory.id not in seen_ids:
            seen_ids.add(memory.id)
            merged.append((memory, score))
    merged.sort(key=lambda x: x[1], reverse=True)
    relevant_memories = merged[:6]
    if relevant_memories:
        print("\n=== recent memories ===")
        for memory, _ in relevant_memories:
            print(f"\n[{memory.layer}] {memory.title}")
            print(memory.content)

    _persist_global_sticky_defaults(mem, persona="engineer", journey=slug)
    resolved_session_id = resolve_operating_session_id(mem.store, session_id)
    activate_mode(
        mem.store,
        mode="Builder Mode",
        journey=slug,
        session_id=resolved_session_id,
    )
    switch_conversation(session_id=resolved_session_id, persona="engineer", journey=slug)

    if project_path:
        print(f"\nproject_path={project_path}")
    else:
        print(
            f"\n[Journey '{slug}' has no project_path configured. "
            f"Run: python -m memory journey set-path {slug} /path/to/project]"
        )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build skill — DB context loader")
    sub = parser.add_subparsers(dest="command", required=True)

    p_load = sub.add_parser("load", help="Load journey context from DB (emits project_path)")
    p_load.add_argument("slug", help="Journey ID")
    p_load.add_argument(
        "--ignore-production-role",
        action="store_true",
        dest="ignore_production_role",
        help="Override the production clone role guard for this invocation",
    )
    p_load.add_argument(
        "--session-id",
        default=None,
        help="Runtime session id for session-scoped operating mode state",
    )

    args = parser.parse_args(argv)

    if args.command == "load":
        cmd_load(
            args.slug,
            ignore_production_role=args.ignore_production_role,
            session_id=args.session_id,
        )
