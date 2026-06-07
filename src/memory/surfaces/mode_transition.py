"""Plain-text mode transition surfaces."""

from __future__ import annotations

import re
from collections.abc import Iterable

WIDTH = 56


def render_mirror_mode_transition(
    *,
    identity: str,
    journey: str | None = None,
    personas: Iterable[str] = (),
) -> str:
    persona_line = _persona_routing_line(sorted(personas))
    rows = [
        ("identity", identity),
    ]
    if journey:
        rows.append(("active journey", journey))
    rows.extend(
        [
            (
                "what this mode is",
                "Identity lens. Mirror reflects from memory, values, journeys, tensions, and personas.",
            ),
            ("persona routing", persona_line),
            ("available lenses", "◌ Mirror Mode · ■ Builder Mode · △ Explorer Mode"),
        ]
    )
    return _box("◌  MIRROR MODE ACTIVE", rows)


def render_builder_mode_transition(
    *,
    journey: str,
    journey_content: str,
    project_path: str | None = None,
) -> str:
    rows = [("active journey", journey)]
    stage = _extract_stage(journey_content)
    if stage:
        rows.append(("journey path", stage))
    if project_path:
        rows.append(("project path", project_path))
    briefing = _extract_section(journey_content, ["briefing", "description", "context"])
    if briefing:
        rows.append(("briefing", _truncate_words(briefing, 32)))
    rows.append(("boundary", "Builder executes commitment."))
    return _box("■  BUILDER MODE ACTIVE", rows)


def render_explorer_mode_transition(*, journey: str) -> str:
    return _box(
        "△  EXPLORER MODE ACTIVE",
        [
            ("active journey", journey),
            (
                "availability",
                "Explorer Mode is active and ready for durable exploration, story thickening, attractors, experiments, and Builder handoff.",
            ),
            (
                "what this mode is",
                "Exploration lens. Mirror preserves uncertainty, keeps signals, and thickens exploratory stories before construction.",
            ),
            ("boundary", "Explorer preserves uncertainty."),
        ],
    )


def _persona_routing_line(personas: list[str]) -> str:
    if not personas:
        return "when the topic asks: personas route naturally"
    shown = personas[:3]
    suffix = ""
    remaining = len(personas) - len(shown)
    if remaining > 0:
        suffix = f" and {remaining} more available"
    return f"when the topic asks: {', '.join(shown)}{suffix}"


def _box(title: str, rows: list[tuple[str, str]]) -> str:
    lines = ["Mirror", "╭" + "─" * WIDTH + "╮", _line(f"        {title}")]
    for label, value in rows:
        lines.append(_line(""))
        lines.append(_line(f"  {label}"))
        for wrapped in _wrap(value):
            lines.append(_line(f"  {wrapped}"))
    lines.append("╰" + "─" * WIDTH + "╯")
    return "\n".join(lines)


def _line(text: str) -> str:
    content = text[:WIDTH]
    return "│" + content.ljust(WIDTH) + "│"


def _wrap(text: str) -> list[str]:
    max_width = WIDTH - 2
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= max_width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _extract_stage(content: str) -> str | None:
    match = re.search(r"^\*\*Stage:\*\*\s*(.+)$", content, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def _extract_section(content: str, names: list[str]) -> str | None:
    lines = content.splitlines()
    capturing = False
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        header = stripped.lstrip("#").strip().lower()
        if stripped.startswith("#"):
            if capturing:
                break
            if any(name in header for name in names):
                capturing = True
                continue
        elif capturing:
            result.append(stripped)
    text = " ".join(line for line in result if line).strip()
    if text:
        return text
    fallback = " ".join(line.strip() for line in lines if line.strip() and not line.startswith("#"))
    return fallback[:240].strip() or None


def _truncate_words(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]).rstrip(".,;") + "…"
