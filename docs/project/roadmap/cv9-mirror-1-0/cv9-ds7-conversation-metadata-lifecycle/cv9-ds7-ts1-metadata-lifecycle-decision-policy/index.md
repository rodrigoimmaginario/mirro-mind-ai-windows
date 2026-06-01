[< CV9.DS7](../index.md)

# CV9.DS7.TS1 — Metadata Lifecycle Decision Policy

**Type:** Technical Story  
**Status:** Done  
**Parent:** [CV9.DS7 Conversation Metadata Lifecycle](../index.md)

---

## Intent

Define the internal metadata lifecycle decision policy for title, summary, tags,
readiness, provenance, confidence, lock state, and last update source.

---

## Verification Seed

Use fixtures or focused tests to verify lifecycle decisions for generic,
meaningful, and scope-changing conversation shapes while preserving manual title
locks.

---

## Pull State

Pulled after US1 Navigator validation revealed that the dry-run surface works but the title decision policy was too weak. TS1 is done: the policy now reports evidence-based `refine_candidate` decisions with confidence/evidence instead of hard-keeps for unlocked titles whose later summary is more specific.

## Plan and Validation

- [Plan](plan.md)
- [Test Guide](test-guide.md)
