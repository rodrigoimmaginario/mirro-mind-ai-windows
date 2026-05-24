[< CV9.E6 Web Visibility](../index.md)

# CV9.E6.S3 — Atlas Identity and Persona Map

**Status:** 🟢 Planned — Plan checkpoint ready
**User-visible outcome:** Atlas opens as an editorial psyche map with real identity and persona regions.

## Scope

Implement the first Atlas vertical slice:

- editorial psyche map layout;
- Identity region backed by real identity data;
- Personas region backed by real persona data;
- honest empty or partial states for other map regions;
- links from map regions to supported detail routes.

## Acceptance Criteria

- Atlas does not present itself as a sidebar-first admin menu.
- Identity and personas are real data from Mirror Core.
- Unsupported or partial regions are visibly honest.
- The Atlas surface is read-only.
- The page can be manually validated against the personal Mirror.

## Plan and Validation

- [Plan](plan.md)
- [Test Guide](test-guide.md)

## Notes

The map may be visually simple in the first slice. A static map-card layout is
preferred over a complex graph engine.
