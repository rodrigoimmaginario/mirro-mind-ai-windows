[< Roadmap](../index.md)

# CV16 — Explorer Mode

**Status:** 🟢 DS0–DS3 Done

**Source exploration:** [ES-003 Explorer Mode](../../exploration/es-003-explorer-mode.md)

**Release intent:** future minor release after roadmap confirmation

---

## What This Is

CV16 gives Mirror a native exploratory lens for the uncertain middle between
reflection and construction.

Mirror Mode reflects identity, memory, tensions, and sensemaking. Builder Mode
turns a journey into project construction, implementation, validation, and
history. Explorer Mode sits beside Builder Mode as an explicit operating lens for
a journey, but its purpose is different: it preserves uncertainty before the user
is ready to commit to delivery.

Explorer Mode lets the user open an exploration in natural language, stay inside
that exploratory field across turns, visibly thicken one current Exploratory
Story, keep nearby signals in a radar, request a Narrative Field Snapshot, and
explicitly promote the exploration into Builder only when ready.

---

## Product Boundary

```text
Explorer preserves uncertainty.
Builder executes commitment.
```

Explorer may name signals, open or thicken an Exploratory Story, preserve a
radar item, formulate a candidate, or propose promotion. It does not edit code,
create delivery plans, mutate roadmap state, or begin construction unless the
user explicitly confirms promotion into Builder.

Explorer is not hidden intent detection. The user activates the lens explicitly,
and while it is active Mirror assumes new material belongs to the exploratory
field unless the user asks for a clear operational action.

---

## Community Promise

Mirror is not only a place to reflect or build. It can also hold the field where
something is becoming clear but is not ready to become work.

Explorer Mode gives that field a shape. It listens for signals, opens an
Exploratory Story, shows when the story thickens, keeps nearby signals without
forcing them into the roadmap, and proposes a promotion brief when construction
becomes possible. It does not silently convert exploration into delivery.

---

## Delivery Arc

| Code | Delivery Story | Outcome | Status |
|------|----------------|---------|--------|
| [CV16.DS0](cv16-ds0-runtime-status-bar-foundation/index.md) | Runtime status bar foundation | Pi footer shows active Mirror identity, active journey, active mode, and health marker as a cross-mode orientation foundation | ✅ Done |
| [CV16.DS1](cv16-ds1-mode-transition-surface/index.md) | Mode transition surface | Mode changes render a compact conversational surface for Mirror, Builder, and Explorer lenses, including persona routing and Builder journey context | ✅ Done |
| [CV16.DS2](cv16-ds2-discard-current-conversation-skill/index.md) | Discard current conversation skill | Test sessions can be quit without preserving the current conversation in Mirror history | ✅ Done |
| [CV16.DS3](cv16-ds3-explorer-activation-contract/index.md) | Explorer activation contract | A user can explicitly enter and leave Explorer Mode for a journey through natural language, with Mirror using contained commands only as internal behavioral resources | ✅ Done |
| CV16.DS4 | In-session exploratory field | Explorer Mode maintains one current Exploratory Story per journey session, with current signal, radar excerpt, narrative summary, and last card context available for the next turn | 🟡 Planned |
| CV16.DS5 | Story thickening surfaces | Mirror renders Explorer Mode Active, Possible Signal, Exploratory Story Opened, Story Thickened, Signal Radar, Narrative Field Snapshot, and Promotion Proposal at the right moments | 🟡 Planned |
| CV16.DS6 | Promotion handoff to Builder | A thickened exploration can produce an explicit promotion proposal and a minimal Builder handoff without pretending to be a complete delivery plan | 🟡 Planned |
| CV16.DS7 | Persistence and visibility | Exploratory state survives beyond one fragile session and becomes visible in appropriate Mirror surfaces after the conversational behavior is proven | ⚪ Later |

The first enabling slice is the runtime status bar foundation because Explorer
adds a new operating lens and Mirror should make the active lens visible before
adding another mode. After that, the roadmap should move to the behavior
contract, not storage or web UI. Persistence is intentionally delayed until
Explorer proves that it can hold uncertainty and thicken stories coherently in
conversation.

---

## First Slice Principles

- Natural language is the user interface. Formal commands are resources Mirror
  can use internally when contained behavior is useful.
- `/mm-explore <journey>` should only set mode context. It should not start a
  new conversation session by itself.
- Explorer Mode is of the same nature as Builder Mode: an explicit journey lens,
  not a hidden specialization inside Mirror Mode.
- The first implementation supports one current Exploratory Story per journey
  session.
- Story Thickened is the core user-visible behavior.
- Promotion to Builder requires explicit confirmation.

---

## Conscious Non-Goals for the First Slice

- No hidden hook-based intent interception.
- No automatic conversion from Mirror Mode to Explorer Mode.
- No automatic promotion to Builder.
- No complex database schema before behavior is validated.
- No web console dependency for the first conversational behavior.
- No broad signal classifier that tries to detect every possible exploratory
  moment.
- No requirement that Ariad or Maestro become the runtime substrate.

---

## Open Design Questions

- Where should the first non-persistent state live: runtime state, journey
  identity, local context file, or session-scoped database state?
- How should `last_story_card` be represented so the next turn can thicken the
  story rather than replace it?
- What is the smallest promotion brief Builder can consume while preserving the
  distinction between exploratory candidate and delivery plan?

---

## Done Condition

CV16 is done when a user can explicitly enter Explorer Mode for a journey,
explore across multiple turns with visible story thickening, keep signals in a
radar, request a Narrative Field Snapshot, receive a promotion proposal, and
explicitly promote the exploration into Builder without hidden mode switching or
premature construction.

---

## References

- [ES-003 Explorer Mode](../../exploration/es-003-explorer-mode.md)
- Ariad Exploration: `/Users/alissonvale/Code/ariad/docs/exploration/`
- Passagem evidence conversation: `/Users/alissonvale/Desktop/passagem-conversa.md`
