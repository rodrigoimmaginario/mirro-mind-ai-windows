[< Story](index.md)

# Plan — CV13.E1.S5 Conversation card refinement

## Design

The current Workspace card renderer treats conversations like any other card. This story adds a specialized renderer for `kind === "conversation"` while keeping the same Workspace surface DTO.

Implementation:

- add `renderConversationCard(card)` in `app.js`;
- route conversation cards from `renderWorkspaceCard()` to the specialized renderer;
- format `started_at` with a compact local date;
- show message count as a prominent stat;
- show persona and journey as chips when available;
- use a persona-style icon when `metadata.persona` exists.

No backend change is required because the Workspace surface already carries `message_count`, `journey`, `persona`, and `started_at`.

## Tests

This is mostly presentational. Run existing focused Workspace/web tests and `node --check`.

## Risk

Low. The main product risk is implying the card is clickable. Avoid link affordances until a conversation detail or transcript page exists.
