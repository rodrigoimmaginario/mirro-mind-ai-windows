[< CV9.DS7](../index.md)

# CV9.DS7.US1 — Dry-run Metadata Lifecycle Decision Path

**Type:** User Story  
**Status:** Done  
**Parent:** [CV9.DS7 Conversation Metadata Lifecycle](../index.md)

---

## Intent

Expose a non-mutating dry-run path that reports conversation metadata lifecycle
decisions over known conversation shapes.

The report should make the lifecycle observable before any apply/mutation path
exists.

---

## Observable Behavior Seed

Given sample conversations with generic, meaningful, and scope-changing openings,
the dry-run reports decisions such as keep, create, repair, refine, or defer for
title, summary, tags, and metadata readiness/provenance.

Manual/user-edited title locks must be reported as preserved.

---

## Pull State

Pulled as the first child story of CV9.DS7. Automated validation passed, and [CV9.DS7.TS1](../cv9-ds7-ts1-metadata-lifecycle-decision-policy/index.md) resolved the semantic false-keep found during Navigator validation. Navigator validation accepted the dry-run across representative samples. US1 is done.

## Plan and Validation

- [Plan](plan.md)
- [Test Guide](test-guide.md)
