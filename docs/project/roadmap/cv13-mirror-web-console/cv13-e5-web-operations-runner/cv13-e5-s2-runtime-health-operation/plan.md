[< Story](index.md)

# Plan — CV13.E5.S2 Runtime health operation

## Implementation plan

1. Extend the web operations module with a small execution result model and a dispatcher that only knows implemented operation ids.
2. Change `runtime-health` from `execution: future` to `execution: runnable` in the catalog.
3. Add `POST /api/operations/run` with a JSON body containing `operationId` and optional `parameters`.
4. Validate the requested operation against the server-owned catalog.
5. Implement only `runtime-health` by calling `build_runtime_status()` directly from `memory.cli.runtime` with the active web `mirror_home` and repository start path.
6. Serialize the runtime status report into a web-safe structured payload rather than returning raw CLI text.
7. Return `400` for unknown operation ids, malformed requests, and operations that remain catalog-only/future.
8. Add tests for successful runtime health execution, unknown operation rejection, future operation rejection, and absence of command-like execution inputs.

## Design boundaries

- The endpoint name should describe operation execution without implying arbitrary command execution.
- Execution is allowlist-only. The request may select an operation id; it may not supply code, command strings, executable paths, raw SQL, or scripts.
- S2 remains synchronous because runtime health is fast and read-only. Job model and streaming remain later stories.
- The operation calls Python functions directly, not `subprocess` and not `python -m memory runtime status`.
- Runtime status may report `attention needed` when the development tree is dirty or a temporary Mirror lacks a database. That is valid health information, not a web error.
- Secret-bearing environment values must not be included in the response.

## Result shape

The successful response should include:

- operation id and status,
- high-level outcome such as `ready` or `attention needed`,
- structured result data,
- human-readable summary lines for lightweight display,
- errors only when the operation request itself fails.

## Risks and mitigations

- Risk: execution endpoint becomes a foothold for arbitrary commands. Mitigation: dispatch only from hardcoded implemented operations and reject command-like request fields.
- Risk: reusing CLI rendering leaks too much or returns brittle text. Mitigation: serialize selected fields from the existing report dataclasses.
- Risk: health state is confused with HTTP failure. Mitigation: operation succeeds with `status: completed` even when runtime health says `attention needed`; request validation failures use `400`.

## Verification approach

- Focused unit tests cover operation dispatcher and web endpoint behavior.
- Existing web server tests continue to pass.
- Static checks cover the new operation code.
- Manual validation runs the web server and posts the runtime-health operation request.
