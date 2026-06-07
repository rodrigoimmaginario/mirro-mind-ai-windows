[< CV16](../index.md)

# CV16.DS7 — Promotion Handoff to Builder

**Status:** ✅ Done

**Placement:** CV16 Explorer to Builder boundary story

**User-visible outcome:** A confirmed Exploratory Story can produce a transfer document set under `docs/project/explorations/<es-id>/`, giving Builder the discovery narrative, handoff cautions, and product design proposal before switching to Builder only after explicit user confirmation.

---

## Why This Exists

DS6 made Explorer directional: it can name attractors and propose experiments. The next boundary is commitment. Explorer should be able to say “this exploration may be ready for construction” without silently becoming Builder.

The handoff is not a delivery plan. It is a compact translation from uncertainty into a Builder starting point. Builder still owns project reading, planning, validation, and implementation.

```text
Explorer proposes commitment.
Builder executes commitment.
The user confirms the crossing.
```

---

## Scope

- Add a Builder handoff proposal surface for the current Exploratory Story.
- Generate a transfer document set under `docs/project/explorations/<es-id>/` when the active journey has a project path.
- The document set contains `exploratory-story.md`, `handoff-info.md`, and `product-design-proposal.md`.
- Persist the proposed handoff and artifact paths inside the current in-session story state for DS7.
- Add a contained confirmation operation that activates Builder Mode only after explicit user confirmation.
- Keep Builder activation equivalent to normal Builder Mode activation, including transition surface and project path output.
- Update the Explorer skill contract so promotion is a two-step interaction: proposal, then confirmation.

---

## Non-goals

- No automatic Builder activation.
- No full delivery plan generation.
- No roadmap mutation.
- No story status persistence beyond runtime state. DS8 owns durable status such as promoted or archived.
- No multiple Exploratory Stories.
- No web console surface.

---

## Acceptance Behavior

Given an Exploratory Story exists, when the user asks to promote it or asks whether it is ready for Builder, Mirror renders `△ BUILDER HANDOFF PROPOSED`, writes the transfer document set, shows the artifact paths, and does not switch modes.

Given the user explicitly confirms promotion, Mirror activates Builder Mode for the same journey and renders the normal Builder Mode transition surface.

Given the user does not confirm promotion, active mode remains Explorer Mode and the transfer documents remain available for review.

Given no Exploratory Story exists, promotion proposal returns a clear “no story to promote” surface.

Given the story has attractor and experiment proposal, the transfer document set includes both.

---

## References

- [Plan](plan.md)
- [Test Guide](test-guide.md)
- [CV16 Explorer Mode](../index.md)
