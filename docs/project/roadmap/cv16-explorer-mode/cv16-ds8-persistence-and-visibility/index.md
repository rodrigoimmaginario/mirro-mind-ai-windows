[< CV16](../index.md)

# CV16.DS8 — Persistence and Visibility

**Status:** ✅ Done

**Placement:** CV16 durable Explorer release story, split into DS8.1 and DS8.2

**User-visible outcome:** Exploratory Stories first survive beyond fragile runtime state as durable, resumable, visible records. Then Builder handoff packages become provenance-rich editorial artifacts with source evidence, completeness review, and optional privacy-safe full conversation material.

---

## Why This Exists

DS7 proved the Explorer-to-Builder handoff mechanism, but real Soul Mode validation showed the generated handoff is only useful when it becomes an editorial transfer of discovery. The first generated documents captured final state but missed the continuous thickening, source conversations, simulations, phases, decisions, and product details that made the exploration ready for Builder.

DS8 turns Explorer output from temporary runtime state into a durable, reviewable exploration artifact. The work is intentionally split because persistence and evidence are different kinds of trust: DS8.1 asks whether Explorer remembers; DS8.2 asks whether Builder can trust the handoff.

---

## Delivery Split

### CV16.DS8.1 — Durable Explorer Stories

**Status:** ✅ Done

**Outcome:** Exploratory Stories stop living only in runtime state. They become durable, resumable, visible records per journey.

Scope:

- Persist Exploratory Stories as durable records, while keeping at most one active story per journey.
- Store the current story fields: title, current story, narrative summary, last story card, attractors, experiment proposal, and Builder handoff state.
- Support lifecycle status: `active`, `archived`, and `promoted`.
- Make `story open`, `story thicken`, `story snapshot`, `story attractors`, and `story experiment` read and write durable state.
- Support resuming the active Exploratory Story when entering Explorer Mode, with `△ EXPLORATORY STORY RESUMED`.
- Add minimal story visibility for a journey: active story plus archived or promoted historical stories.
- Support archiving the active story.
- Mark the durable story as `promoted` when `story promote` crosses into Builder.

Out of scope:

- Source conversations.
- Source evidence lists.
- `full-conversation.md`.
- Privacy obfuscation.
- Handoff completeness checklist.

### CV16.DS8.2 — Editorial Handoff Evidence

**Status:** ✅ Done

**Outcome:** Builder handoff becomes a trustworthy editorial transfer artifact, with provenance and privacy boundaries.

Scope:

- Connect handoff artifacts to the durable Exploratory Story id.
- Register source conversations that contributed to the exploration.
- Ask for or confirm which conversations should be included as handoff evidence.
- List source evidence in `index.md`, including conversation ids, titles, and role in the exploration.
- Add a handoff completeness checklist covering continuous thickening, source evidence, surfaces, phases, examples or simulations, product decisions, user flows, transition rules, risks, boundaries, open questions, preservation guidance, and non-assumptions.
- Generate or attach `full-conversation.md` only when the user explicitly confirms raw source material inclusion.
- Obfuscate sensitive Navigator information before writing conversation evidence into handoff artifacts.
- Ask before writing raw excerpts when sensitivity is uncertain.

---

## Non-goals

- No multiple simultaneously active Exploratory Stories for one journey.
- No broad web UI unless needed for minimal visibility.
- No automatic publication of raw conversations without user confirmation.
- No irreversible deletion of source evidence.
- No source evidence or raw conversation export in DS8.1.
- No durable storage redesign in DS8.2 beyond the fields needed to attach evidence to the story.

---

## Acceptance Behavior

### DS8.1

Given a journey has an active Exploratory Story, when the user enters Explorer Mode, Mirror resumes it visibly.

Given an Exploratory Story is opened, thickened, receives attractors, or receives an experiment proposal, the durable record is updated.

Given the user asks for explorations in a journey, Mirror shows the active story and historical archived or promoted stories.

Given the exploration is promoted to Builder, the durable story status becomes `promoted`.

Given the user archives an exploration, it remains visible as historical evidence but is no longer the active story.

### DS8.2

Given a handoff is prepared, Mirror identifies or asks for source conversations that contributed to the exploration.

Given a handoff is generated, its artifacts link back to the durable Exploratory Story id.

Given full conversation evidence is included, Mirror obfuscates personal or sensitive Navigator information before writing it to `full-conversation.md`.

Given the handoff is incomplete, Mirror names missing evidence or sections before treating it as ready for Builder.

---

## References

- [CV16 Explorer Mode](../index.md)
- [DS7 Promotion Handoff to Builder](../cv16-ds7-promotion-handoff-to-builder/index.md)
