[< Project](../briefing.md)

# ES-001 — Conversation Metadata Lifecycle

**Status:** Promoted to Delivery Story  
**Delivery handoff:** [CV9.DS7 Conversation Metadata Lifecycle](../roadmap/cv9-mirror-1-0/cv9-ds7-conversation-metadata-lifecycle/index.md)  
**Source:** Exploration simulation on 2026-05-29 using real Mirror conversation records

---

## Initial Signal

A web conversation could still show a generated GUID as its title. That made the
web experience feel unfinished and made later reorientation harder.

The first reading was that Mirror's automatic retitle trigger was too narrow:
it ran around first-message/session-close moments and did not cover forced-close
or early web visibility well enough.

---

## Thickened Story

The story widened from **conversation retitle timing** to **conversation metadata
lifecycle**.

Conversation titles can fail in several ways:

- GUIDs feel like implementation leaks or errors.
- First-turn command or project-opening titles are often too generic.
- A first prompt may already express real user intent.
- The first assistant response may add enough context for a better early title.
- A valid initial title may still need later coherence refinement when the
  conversation's purpose becomes clearer.

During the experiment we also noticed that summary, tags, and operational
metadata state need similar treatment. Title and summary share a lifecycle, but
readiness is per field: a title may be ready earlier than a summary, and tags may
need summary-level substance.

---

## Attractor Evolution

### Confirmed attractor: Conversation title lifecycle

The first center of gravity was that conversation titles need phases, not a
single automatic retitle trigger:

- placeholder or safe early title;
- repair once intent is clearer;
- later coherence refinement.

### Refined attractor: Conversation metadata lifecycle

The attractor was refined when summary entered the story. The previous attractor
was useful but too narrow.

**From:** Conversation title lifecycle  
**To:** Conversation metadata lifecycle

Title, summary, tags, and metadata JSON should be managed through one lifecycle,
with different readiness rules per field.

### Kept outside

Journey detection after conversation start is related but was intentionally kept
for later. A conversation may begin without a Journey and later reveal one, but
that is a separate thread.

---

## Experiment

### Method

Manual metadata-decision rubric over recalled Mirror conversations.

The experiment classified whether conversation metadata should be kept,
created, repaired, refined, or left alone. It also tested whether the observation
unit should be the first user prompt or the first exchange: user prompt plus
assistant response.

### Samples

#### `0f8f0fc0` — Antes de Mim editorial work

Current title: `vamos trabalhar no projeto antes de mim`

Finding: the title was project-related but too generic. It did not capture the
actual session intent, which later centered on explaining the book and preparing
a cover brief.

Better closure title: `Antes de Mim — sobre o livro e briefing de capa`

Decision: `repair_weak_title`

#### `c55b04ab` — Maestro checkpoint visibility work

Current title: `vamos trabalhar no maestro`

Finding: the title identified the project but not the actual work. The session
covered checkpoint visibility validation, commits/pushes, explaining Ariad and
Maestro, and cleanup of local artifacts.

Better closure title: `Maestro — structured checkpoint handoff and cleanup`

Decision: `repair_weak_title`

#### `e8b49667` — Delphi consulting inquiry

Current title: `você consegue trabalhar com codebase delphi?`

Finding: the opening title was meaningful and accurate for the first topic. By
the third turn, the purpose became clearer: a consulting/training package for a
possible client using Delphi.

Better refined title: `Delphi consulting — Mirror/Maestro/Ariad training`

Decision: `refine_for_coherence`

---

## Findings

- Title repair and coherence refinement are distinct.
- First prompt alone may be too thin.
- First exchange can often improve title generation.
- Placeholder may only be needed when the first exchange still lacks enough
  intent.
- Summary has a later readiness threshold than title.
- Tags likely depend on summary-level substance.
- Conversation metadata shares one lifecycle, but readiness is per field.
- Generic project-opening titles should be repaired.
- Valid initial titles may still need later refinement.
- Metadata JSON should track source, confidence, lock state, readiness, and last
  update.

---

## Carry Forward Notes

Preserve these for Delivery:

- The implementation intent should move from isolated title rename to
  conversation metadata update.
- Each metadata field should be evaluated independently.
- The first exchange should be considered as an early title input, not only the
  first user prompt.
- Summary should not be forced before enough substance exists.
- Tags should probably be derived after summary-level substance.
- Manual/user-edited title locks must continue to be respected.
- Journey inference after conversation start is related but out of scope for the
  promoted story.

---

## Candidate Rationale

The exploration produced enough shape for Delivery because the problem is now
bounded and verifiable: Mirror should manage conversation title, summary, tags,
and metadata state through a lifecycle rather than relying on a narrow retitle
trigger.

The first Delivery entry should avoid broad autonomous intelligence. It should
start by classifying the promoted candidate with the current Ariad taxonomy,
then choose the first implementable User Story or Technical Story around the
lifecycle policy, field readiness, provenance, and replayable validation over
known conversation shapes.

---

## Delivery Handoff

**Suggested placement:** CV9 Stabilization work  
**Delivery Story:** [CV9.DS7 Conversation Metadata Lifecycle](../roadmap/cv9-mirror-1-0/cv9-ds7-conversation-metadata-lifecycle/index.md)  
**Roadmap placement:** Created as a Delivery Story using the current Delivery Story / User Story / Technical Story taxonomy.

**Delivery Story seed:**

When a conversation begins and evolves, Mirror updates user-facing conversation
metadata through a lifecycle: title, summary, tags, and metadata state are
created, repaired, or refined according to per-field readiness rather than one
narrow retitle trigger.

**Validation seed:**

Replay sample conversations with generic, meaningful, and scope-changing
openings. Verify title, summary, tags, metadata readiness/provenance, and
refinement behavior while preserving manual title locks.
