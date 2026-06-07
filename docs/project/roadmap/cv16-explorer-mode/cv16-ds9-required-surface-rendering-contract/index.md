[< CV16](../index.md)

# CV16.DS9 — Required Surface Rendering and Operational Boundary Contract

**Status:** ✅ Done

**Placement:** CV16 release hardening story

**User-visible outcome:** Required Explorer surfaces such as `△ STORY THICKENED` and `△ BUILDER HANDOFF PROPOSED` cannot disappear into assistant interpretation, clear operational requests such as editing files, applying procedures, or creating code are routed out of Explorer before mutation, and Pi's status bar reflects the current session's mode instead of another open session's mode.

---

## Why This Exists

During external validation, `explore story thicken` correctly returned the `△ STORY THICKENED` surface, but the assistant summarized the concept instead of showing the card. The failure was not state or CLI behavior. It was the presentation contract between contained command output and the final assistant response.

Explorer surfaces are product output, not internal evidence. Explorer is also not the right lens for mutating project files. When the user asks for a clear operational action, Mirror must not force that request into story thickening or exploration.

DS9 also hardens a multisession leak discovered during validation: the Pi footer could show `Active Journey mirror-4-teams on △ Explorer Mode` in one session while another session was working in Builder Mode for `explorer-mode`. Operating mode display must be session-scoped when Pi supplies a session id.

---

## Scope

- Mark required Mirror surfaces in CLI output with an explicit contract marker.
- Update runtime skill instructions to require first-block rendering while stripping marker lines from user-facing copy.
- Preserve the narrative/substantive versus local/refinement boundary before `story thicken` is called.
- Add an operational boundary rule for clear file, code, doc, command, and mutation requests while Explorer Mode is active.
- Require a visible mode-boundary response before mutating files or creating code from Explorer Mode.
- Add tests or smoke validation proving Explorer surfaces are distinguishable from ordinary command output.
- Make Pi status-line rendering pass the current runtime session id so the footer reads session-scoped mode state.
- Remove stale Explorer experimental availability copy now that durable Explorer behavior exists.
- Investigate whether Pi can enforce or preserve required surface blocks automatically.

---

## Non-goals

- No broad runtime rendering framework.
- No changes to Explorer story semantics.
- No Builder handoff behavior changes beyond surface preservation.

---

## Acceptance Behavior

Given an Explorer command returns a required surface, the assistant renders that surface before commentary.

Given a required surface is present in CLI output, it is machine-identifiable by stable `[[MIRROR_REQUIRED_SURFACE_BEGIN:<surface-id>]]` and `[[MIRROR_REQUIRED_SURFACE_END:<surface-id>]]` markers.

Given external validation runs in Pi, `△ STORY THICKENED` appears immediately after a substantive story change.

Given two Pi sessions are open with different operating modes, each footer shows its own session's active journey and mode.

Given the user makes a local refinement, such as icon, microcopy, visual label, or wording polish, Explorer does not call `story thicken` unless the user explicitly asks to preserve it in the Exploratory Story.

Given the user asks Explorer Mode to edit files, apply a procedure to a document, create code, run implementation commands, or otherwise mutate project state, Mirror does not treat the request as exploratory thickening. It names the request as operational work and asks to switch to Builder Mode, using the `△ EXPLORER → BUILDER BOUNDARY` response shape.

---

## References

- [CV16 Explorer Mode](../index.md)
