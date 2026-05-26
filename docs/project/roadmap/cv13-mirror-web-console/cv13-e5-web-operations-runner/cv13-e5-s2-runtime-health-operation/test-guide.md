[< Story](index.md)

# Test Guide — CV13.E5.S2 Runtime health operation

## Automated checks

```bash
uv run pytest tests/unit/memory/web/test_operations.py tests/unit/memory/web/test_server.py
uv run ruff check src/memory/web tests/unit/memory/web/test_operations.py tests/unit/memory/web/test_server.py
uv run ruff format --check src/memory/web tests/unit/memory/web/test_operations.py tests/unit/memory/web/test_server.py
node --check src/memory/web/static/app.js
git diff --check
```

## Manual validation

1. Start the local web server against a disposable or non-production Mirror home:

   ```bash
   uv run python -m memory.web.server --mirror-home ~/.mirror-minds/alisson-vale
   ```

2. Confirm `runtime-health` is marked runnable:

   ```bash
   curl http://127.0.0.1:8765/api/operations/catalog | python -m json.tool
   ```

3. Run the runtime health operation:

   ```bash
   curl -X POST http://127.0.0.1:8765/api/operations/run \
     -H 'Content-Type: application/json' \
     -d '{"operationId":"runtime-health"}' | python -m json.tool
   ```

4. Confirm the response includes operation id, completed status, runtime outcome, version, git/repository fields, mirror home, database state, migration state, extension state, Python version, environment, and update channel.
5. Confirm an `attention needed` runtime outcome is displayed as operation data, not as an HTTP failure.
6. Confirm unknown operations are rejected:

   ```bash
   curl -X POST http://127.0.0.1:8765/api/operations/run \
     -H 'Content-Type: application/json' \
     -d '{"operationId":"unsafe-shell","command":"echo unsafe"}' | python -m json.tool
   ```

7. Confirm future operations such as `database-backup` are rejected until their own stories implement them.

## Expected result

The web API can run only the read-only runtime health operation. No generic command execution, mutation, backup, repair, update, or streaming exists yet.
