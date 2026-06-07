[< CV16](../index.md)

# CV16.DS3 — Explorer Activation Contract

**Status:** ✅ Done

**Placement:** CV16 first Explorer behavior story

**User-visible outcome:** The user can explicitly enter and leave Explorer Mode for a journey through natural language or the runtime skill surface, with Mirror treating CLI commands as internal operating resources rather than the product interface.

---

## Why This Exists

DS0 and DS1 created the operating-mode lifecycle, status line, and transition surfaces. DS2 added runtime hygiene for testing. Explorer Mode now needs its first behavior contract: activation and deactivation should be explicit, visible, and safe before story thickening or exploratory state exists.

The important boundary is not a new storage model. The important boundary is obedience to the declared lens:

```text
Explorer preserves uncertainty.
Builder executes commitment.
```

Entering Explorer Mode should set the active journey and lens without starting construction. Leaving Explorer Mode should return to the normal Mirror lens while preserving journey context when it remains sticky.

---

## Scope

- Document the Explorer activation and deactivation contract in the Pi skill instructions.
- Keep natural language as the user-facing interface.
- Keep `/mm-explore <journey>` and `python -m memory explore load <slug>` as contained activation resources.
- Add a contained Explorer deactivation command that returns the runtime to Mirror Mode semantics while preserving sticky journey context.
- Render a visible deactivation confirmation instead of leaving the user to infer the transition from status alone.
- Add tests proving activation does not start a new conversation and deactivation clears only the explicit Explorer lens.

---

## Non-goals

- No story thickening state.
- No Signal Radar persistence.
- No Narrative Field Snapshot.
- No promotion handoff to Builder.
- No hidden hook-based intent interception.
- No automatic detection of exploratory intent outside an explicitly active Explorer lens.
- No web console surface.

---

## Acceptance Behavior

Given the user asks to enter Explorer Mode for a journey, Mirror runs the contained activation operation, renders `△ EXPLORER MODE ACTIVE`, sets the active mode to Explorer Mode, and sets the journey as sticky context.

Given Explorer Mode activation runs, it does not start or switch a conversation by itself.

Given the user asks to leave Explorer Mode, Mirror runs the contained deactivation operation, clears the explicit active mode, preserves sticky journey context, and renders a visible return-to-Mirror confirmation.

Given Explorer Mode is active, the skill instructions tell Mirror to treat substantive new material as exploratory unless the user asks for a clear operational action.

Given the user asks to promote the exploration to Builder, Mirror does not switch modes silently. It asks for explicit confirmation or uses the later promotion handoff story when available.

---

## References

- [Plan](plan.md)
- [Test Guide](test-guide.md)
- [CV16 Explorer Mode](../index.md)
- [ES-003 Explorer Mode](../../../exploration/es-003-explorer-mode.md)
