[< CV9.DS7](index.md)

# Exploration Summary — Conversation Metadata Lifecycle

Full exploration document: [ES-001 Conversation Metadata Lifecycle](../../../exploration/es-001-conversation-metadata-lifecycle.md)

---

## Signal

A web conversation could still show a generated GUID as its title. That made the
web experience feel unfinished and made later reorientation harder.

The initial hypothesis was narrow: automatic retitle timing was too limited.
Exploration widened the problem into a conversation metadata lifecycle.

---

## Thickened Story

Conversation metadata needs phases rather than a single title trigger:

- placeholder or safe early title;
- repair once intent is clearer;
- later coherence refinement;
- summary readiness after enough substance exists;
- tag readiness after summary-level substance;
- metadata state that records source, confidence, lock state, readiness, and
  last update.

Title, summary, tags, and metadata JSON share one lifecycle, but readiness is
per field.

---

## Experiment Result

Manual metadata-decision rubric over recalled Mirror conversations:

- `0f8f0fc0` — generic project title should be repaired;
- `c55b04ab` — generic Maestro project title should be repaired;
- `e8b49667` — meaningful opening title can later be refined for coherence.

The experiment showed that first prompt alone may be too thin and that first
exchange can often improve early title generation.

---

## Carry Forward Notes

- Move from isolated title rename to conversation metadata update.
- Evaluate each metadata field independently.
- Consider the first exchange as early title input, not only the first user
  prompt.
- Do not force summary before enough substance exists.
- Derive tags only after summary-level substance exists.
- Preserve manual/user-edited title locks.
- Keep journey inference after conversation start out of scope.

---

## Delivery Handoff

Suggested Delivery Story:

```text
CV9.DS7 — Conversation Metadata Lifecycle
```

Validation seed:

Replay sample conversations with generic, meaningful, and scope-changing
openings. Verify title, summary, tags, metadata readiness/provenance, and
refinement behavior while preserving manual title locks.
