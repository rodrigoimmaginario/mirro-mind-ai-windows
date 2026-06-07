[< CV16](../index.md)

# CV16.DS1 — Mode Transition Surface

**Status:** ✅ Done  
**Placement:** CV16 cross-mode orientation story  
**User-visible outcome:** When Mirror changes operating mode, the user sees a compact surface that names the active lens, active journey, relevant context, and available mode affordances.

---

## Why This Exists

DS0 made mode lifecycle and the Pi status line explicit. The status line is
persistent orientation, but it is not enough as the only user-facing transition
signal. When the user enters Mirror Mode, Builder Mode, or Explorer Mode, Mirror
should acknowledge the lens change in the conversation itself.

This is especially important because Mirror now has three primary lenses:

```text
◌ Mirror Mode
■ Builder Mode
△ Explorer Mode
```

The user should not have to infer what changed from the footer alone.

---

## Scope

- Add a reusable Mode Transition Surface for mode changes.
- Render a Mirror Mode surface when `/mm-mirror` activates `◌ Mirror Mode`.
- Render a Builder Mode surface when `/mm-build` activates `■ Builder Mode`.
- Render an Explorer Mode transition surface when `/mm-explore` activates `△ Explorer Mode`, with current availability aligned to the durable Explorer release.
- Show persona-routing availability in Mirror Mode.
- Introduce a persona icon distinct from the Mirror identity symbol.
- Keep the status bar as persistent orientation and the transition surface as conversational confirmation.

---

## Surface Direction

### Mirror Mode

```text
Mirror
╭────────────────────────────────────────────────────────╮
│        ◌  MIRROR MODE ACTIVE                           │
│                                                        │
│  identity                                              │
│  alisson-vale                                          │
│                                                        │
│  active journey                                        │
│  explorer-mode                                         │
│                                                        │
│  what this mode is                                     │
│  Identity lens. Mirror reflects from memory, values,   │
│  journeys, tensions, and personas.                     │
│                                                        │
│  persona routing                                       │
│  when the topic asks: writer, strategist, therapist    │
│  and 8 more available                                  │
│                                                        │
│  available lenses                                      │
│  ◌ Mirror Mode     identity and integration            │
│  ■ Builder Mode    construction and validation         │
│  △ Explorer Mode   signals and story thickening        │
╰────────────────────────────────────────────────────────╯
```

### Builder Mode

Builder Mode should include the journey path and a compact synthesis or briefing
excerpt, because the user is entering a construction lens for a specific field of
work.

```text
Mirror
╭────────────────────────────────────────────────────────╮
│        ■  BUILDER MODE ACTIVE                          │
│                                                        │
│  active journey                                        │
│  explorer-mode                                         │
│                                                        │
│  journey path                                          │
│  Product architecture / exploratory mode design        │
│                                                        │
│  project path                                          │
│  /Users/alissonvale/Code/mirror-dev                    │
│                                                        │
│  briefing                                              │
│  Build Explorer Mode as a native Mirror lens for       │
│  exploration, sensemaking, signals, hypotheses, and    │
│  exploratory stories before Builder commitment.        │
│                                                        │
│  boundary                                              │
│  Builder executes commitment.                          │
╰────────────────────────────────────────────────────────╯
```

### Explorer Mode

Explorer Mode can begin with the minimal surface below. It should be refined when
Explorer behavior is built.

```text
Mirror
╭────────────────────────────────────────────────────────╮
│        △  EXPLORER MODE ACTIVE                         │
│                                                        │
│  active journey                                        │
│  explorer-mode                                         │
│                                                        │
│  what this mode is                                     │
│  Exploration lens. Mirror preserves uncertainty,       │
│  keeps signals, and thickens exploratory stories       │
│  before construction.                                  │
│                                                        │
│  boundary                                              │
│  Explorer preserves uncertainty.                       │
╰────────────────────────────────────────────────────────╯
```

---

## Persona Icon Direction

The Mirror identity symbol remains:

```text
◇ alisson-vale
```

Personas should receive a distinct icon so an activated persona no longer looks
like the Mirror itself. Candidate:

```text
✦ writer
✦ therapist
✦ engineer
```

Rationale: `✦` reads as a specialized lens or facet inside the Mirror without
competing with the three mode symbols. It is lighter than `◆`, avoids confusing
personas with Builder's solid square, and preserves `◇` for the integrated
Mirror identity.

---

## Non-goals

- No new mode lifecycle semantics beyond DS0.
- No Explorer state persistence.
- No full Explorer card grammar in this story.
- No web UI transition surface.
- No replacement of the Pi footer status line.

---

## Acceptance Behavior

Given Mirror Mode is activated, the response includes a compact transition
surface that names `◌ Mirror Mode`, the active identity, journey when present,
and a persona-routing line with a few persona examples plus a remaining count.

Given Builder Mode is activated, the response includes a compact transition
surface that names `■ Builder Mode`, active journey, journey path or stage,
project path when present, and a short briefing or synthesis.

Given Explorer Mode is activated, the response includes the minimal `△ Explorer
Mode` transition surface without claiming persistence or full exploratory story
behavior.

Given a persona is activated, persona rendering uses the persona icon rather than
reusing the Mirror identity symbol.

---

## References

- [Plan](plan.md)
- [Test Guide](test-guide.md)
- [CV16.DS0 Runtime Status Bar Foundation](../cv16-ds0-runtime-status-bar-foundation/index.md)
- [ES-003 Explorer Mode](../../../exploration/es-003-explorer-mode.md)
