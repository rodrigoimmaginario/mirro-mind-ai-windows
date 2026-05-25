[< Story](index.md)

# Plan — CV13.E1.S3 Memory category drilldown

## Design

Use the existing `SearchResults` and `SearchResultItem` DTOs as the smallest coherent read model for a category result page.

Implementation:

- extend `SearchSurface` to receive `MemoryService`;
- add `memory_category(category_id: str, limit: int = 50) -> SearchResults`;
- classify memory summaries into the same public categories used by Atlas memory cards;
- add `SurfaceService.memory_category(...)`;
- add `GET /api/surface/memories?category=<id>`;
- make `renderMemoryCategory()` emit a clickable target;
- add `loadMemoryCategory()` and render a read-only result page.

The page should be local and deterministic. It must use recent persisted memory summaries only, not semantic search or live LLM calls.

## Tests

- focused `SearchSurface` test for category filtering and empty state;
- web server route serialization test;
- `node --check` for the new browser handler.

## Risk

Low to medium. The only product risk is naming: this is category drilldown, not the final full Memory page. Keep copy honest.
