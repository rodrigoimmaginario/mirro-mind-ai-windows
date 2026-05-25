from memory.surfaces.search import SearchSurface


def test_search_surface_exposes_stable_empty_contract() -> None:
    results = SearchSurface().search("identity", perspective="atlas")

    assert results.query == "identity"
    assert results.perspective == "atlas"
    assert results.results == ()
    assert results.empty_state == "Search is not wired into the web surface yet."


def test_search_surface_lists_recent_memories_by_category(
    memory_service, mock_memory_embedding
) -> None:
    decision = memory_service.add_memory(
        title="Choose surface boundary",
        content="Web renders surfaces.",
        memory_type="decision",
    )
    memory_service.add_memory(title="Draft idea", content="Later.", memory_type="idea")

    results = SearchSurface(memories=memory_service).memory_category("decisions")

    assert results.query == "Decisions"
    assert results.perspective == "memories"
    assert results.empty_state is None
    assert len(results.results) == 1
    assert results.results[0].id == decision.id
    assert results.results[0].title == "Choose surface boundary"
    assert results.results[0].metadata["memory_type"] == "decision"


def test_search_surface_reports_empty_memory_category(memory_service) -> None:
    results = SearchSurface(memories=memory_service).memory_category("patterns")

    assert results.query == "Patterns"
    assert results.results == ()
    assert results.empty_state == "No recent patterns memories are available yet."
