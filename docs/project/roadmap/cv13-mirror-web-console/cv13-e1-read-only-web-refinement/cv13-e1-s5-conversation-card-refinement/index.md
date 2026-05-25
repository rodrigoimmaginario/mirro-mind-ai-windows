[< CV13.E1](../index.md)

# CV13.E1.S5 — Conversation card refinement

**Status:** ✅ Done
**User-visible outcome:** Conversation cards in the selected journey tab are easier to scan, with clearer metadata for message count, persona, journey, and start date.

---

## Scope

- Improve rendering for `conversation` cards in Workspace.
- Make message count and date easier to see.
- Prefer persona context visually when a conversation has one.
- Keep the card read-only and non-clickable until a conversation detail/transcript page exists.

---

## Non-goals

- No transcript page.
- No conversation detail route.
- No retitle operation.
- No conversation editing.
- No LLM title generation.

---

## Acceptance Criteria

- Conversation cards visually differ from generic memory cards.
- Message count, persona, journey, and start date are visible when present.
- Cards do not imply a link to an unavailable detail page.
- Focused Workspace/web validation passes.

---

## See also

- [Plan](plan.md)
- [Test Guide](test-guide.md)
