# Plan — CV9.DS7.US10 Web Historical Metadata Backfill Operation

## Implementation Plan

1. Add operation catalog entry `historical-metadata-backfill`.
2. Parameters:
   - `dryRun` boolean, default true;
   - `mode` choice: `safe` or `force`;
   - `scope` choice: `all`, `not_backfilled`, or `no_change_latest_run`;
   - `allConversations` boolean;
   - `limit` integer, bounded;
   - optional `journey` string.
3. Wire operation runner:
   - dry-run calls `preview_metadata_backfill`;
   - apply creates backup and applies one candidate at a time with progress events.
4. Require approval for apply (`dryRun=false`).
5. Add no-change/result details UI and approval clarity.
6. Add approval-gated orphan cleanup with dry-run, backup, and progress.
7. Add tests for catalog, dry-run, apply with backup, orphan cleanup, and approval requirement.
8. Validate with focused/full tests and web manual route.
