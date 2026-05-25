[< CV13.E1](../index.md)

# CV13.E1.S3 — Memory category drilldown

**Status:** ✅ Done
**User-visible outcome:** Memory category cards in the Identity map open a read-only page with recent memories from that category.

---

## Scope

- Make Identity memory category cards clickable.
- Add a read-only web surface for recent memories by category.
- Render the result with the same contextual-bar rhythm as Workspace, Identity, and Docs.
- Keep the first slice lexical and local: no semantic search and no LLM calls during page load.

---

## Non-goals

- No full memories browser.
- No global search page.
- No memory editing.
- No memory detail page.
- No live synthesis.

---

## Acceptance Criteria

- Clicking a memory category card in Identity opens a memory category page.
- The page shows recent memory cards for the selected category.
- Empty categories show an honest empty state.
- The implementation uses surface DTOs and does not query SQLite from web handlers.
- Focused search/surface and web tests pass.

---

## See also

- [Plan](plan.md)
- [Test Guide](test-guide.md)
