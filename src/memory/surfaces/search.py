"""Search and result-list read models for Mirror web surfaces."""

from __future__ import annotations

from memory.models import MemorySummary
from memory.services.memory import MemoryService
from memory.surfaces.models import SearchResultItem, SearchResults


class SearchSurface:
    """Shared search and result-list surface contract."""

    def __init__(self, memories: MemoryService | None = None) -> None:
        self.memories = memories

    def search(self, query: str, perspective: str | None = None) -> SearchResults:
        return SearchResults(
            query=query,
            perspective=perspective,
            empty_state="Search is not wired into the web surface yet.",
        )

    def memory_category(self, category_id: str, *, limit: int = 50) -> SearchResults:
        category = _category_from_id(category_id)
        if self.memories is None:
            return SearchResults(
                query=category,
                perspective="memories",
                empty_state="Memory categories are not wired into this surface yet.",
            )

        memories = [
            memory
            for memory in self.memories.list_recent(limit=1000)
            if _memory_category(memory.memory_type) == category
        ][:limit]
        return SearchResults(
            query=category,
            perspective="memories",
            results=tuple(_memory_result(memory) for memory in memories),
            empty_state=None
            if memories
            else f"No recent {category.lower()} memories are available yet.",
        )


def _memory_result(memory: MemorySummary) -> SearchResultItem:
    return SearchResultItem(
        id=memory.id,
        kind="memory",
        title=memory.title,
        description=memory.content,
        href=f"/objects/memory/{memory.id}",
        metadata={
            "memory_type": memory.memory_type,
            "layer": memory.layer,
            "journey": memory.journey,
            "persona": memory.persona,
            "created_at": memory.created_at,
        },
    )


def _category_from_id(category_id: str) -> str:
    normalized = (category_id or "").strip().lower().replace("_", "-")
    return {
        "decisions": "Decisions",
        "ideas": "Ideas",
        "insights": "Insights",
        "learning": "Learning",
        "reflections": "Reflections",
        "patterns": "Patterns",
        "tensions": "Tensions",
        "commitments": "Commitments",
        "info": "Info",
        "other": "Other",
    }.get(normalized, normalized.replace("-", " ").title() if normalized else "Other")


def _memory_category(raw_type: str) -> str:
    normalized = (raw_type or "").strip().lower()
    return {
        "decision": "Decisions",
        "decisao": "Decisions",
        "idea": "Ideas",
        "ideia": "Ideas",
        "insight": "Insights",
        "learning": "Learning",
        "reflection": "Reflections",
        "journal": "Reflections",
        "pattern": "Patterns",
        "padrao": "Patterns",
        "tension": "Tensions",
        "tensao": "Tensions",
        "commitment": "Commitments",
        "info": "Info",
    }.get(
        normalized,
        normalized.replace("_", " ").replace("-", " ").title() if normalized else "Other",
    )
