# Mirror Mind — Command Reference

Command reference, configuration, and legacy migration workflow.

- **Commands:** this document
- **System architecture, schema, and runtime model:** [docs/architecture.md](docs/architecture.md)
- **Python API:** [docs/api.md](docs/api.md)
- **Extensions:** [docs/product/extensions/](docs/product/extensions/index.md)

---

## Commands

Claude Code uses the `/mm:` prefix. Pi and Gemini CLI use the `/mm-` prefix.
Codex uses the `$mm-` prefix. All runtimes call the same Python core.

| Pi / Gemini CLI | Codex | Claude Code | Purpose | Main Arguments |
|---------|-------|-------------|---------|----------------|
| `/mm-mirror` | `$mm-mirror` | `/mm:mirror` | Loads identity, persona, journey, and attachments for Mirror Mode | `load [--persona P] [--journey J] [--query Q] [--org]`, `log "summary"`, `journeys` |
| `/mm-build` | `$mm-build` | `/mm:build` | Builder Mode for a journey — loads context and project docs | `<slug>` |
| `/mm-identity` | `$mm-identity` | `/mm:identity` | Read and update identity directly in the database | `list [--layer L]`, `get <layer> <key>`, `set <layer> <key>`, `edit <layer> <key>` |
| `/mm-consult` | `$mm-consult` | `/mm:consult` | Asks other LLMs through OpenRouter with Mirror context | `<family> [tier] "prompt"`, `credits` |
| `/mm-journeys` | `$mm-journeys` | `/mm:journeys` | Lists journeys with status | no arguments |
| `/mm-journey` | `$mm-journey` | `/mm:journey` | Shows detailed journey identity, journey path, memories, and conversations | `[journey]`, `update <journey> <content>` |
| `/mm-memories` | `$mm-memories` | `/mm:memories` | Lists or searches memories by type, layer, and journey | `--type T`, `--layer L`, `--journey J`, `--search "Q"`, `--limit N` |
| `/mm-tasks` | `$mm-tasks` | `/mm:tasks` | Manages tasks by journey | `list`, `add "title"`, `done <id>`, `doing <id>`, `block <id>`, `delete <id>`, `import`, `sync` |
| `/mm-week` | `$mm-week` | `/mm:week` | Weekly planning | `view`, `plan "text"`, `save` |
| `/mm-journal` | `$mm-journal` | `/mm:journal` | Records a personal journal entry | `[--journey J] "text"` |
| `/mm-recall` | `$mm-recall` | `/mm:recall` | Loads a previous conversation into context | `<conversation_id> [--limit N]` |
| `/mm-conversations` | `$mm-conversations` | `/mm:conversations` | Lists recent conversations | `--limit N`, `--journey J`, `--persona P` |
| `/mm-backup` | `$mm-backup` | `/mm:backup` | Backs up the memory database | no arguments |
| `/mm-seed` | `$mm-seed` | `/mm:seed` | Seeds identity files from the active user home into the database | no arguments |
| `/mm-mute` | `$mm-mute` | `/mm:mute` | Toggles conversation logging | no arguments |
| `/mm-new` | `$mm-new` | `/mm:new` | Starts a new conversation | no arguments |
| `/mm-consolidate` | `$mm-consolidate` | `/mm:consolidate` | Scan memories for patterns and propose consolidation | `scan`, `apply <id>`, `reject <id>`, `list` |
| `/mm-shadow` | `$mm-shadow` | `/mm:shadow` | Surface and promote shadow-layer observations | `scan`, `apply`, `reject`, `list`, `show` |
| `/mm-welcome` | `$mm-welcome` | `/mm:welcome` | Renders the state-aware welcome card on demand | no arguments |
| `/mm-help` | `$mm-help` | `/mm:help` | Lists available commands | no arguments |
| `python -m memory runtime` | — | — | Inspects Mirror runtime status, diagnoses drift, manages backups, and plans updates | `status [--mirror-home PATH]`, `diagnose [--mirror-home PATH]`, `backup [--mirror-home PATH]`, `backup --verify PATH`, `update --dry-run [--mirror-home PATH]` |
| `ext-review-copy` | — | `ext:review-copy` | External multi-LLM copy review skill; install and expose it before use | skill-driven workflow |

To inspect the local runtime state before an operational update:

```bash
uv run python -m memory runtime status
```

The command reports version, repository, git state, mirror home, database, core migration health, installed extensions, extension health, Python version, and environment. It exits with attention needed when the current state is not safe enough for update planning, for example when the git tree is dirty, the mirror home is not configured, core migrations are missing or unknown, or installed extension migrations have pending, drifted, or unknown files.

To classify attention-needed drift into repair routes without mutating files or the database:

```bash
uv run python -m memory runtime diagnose
```

The diagnosis command classifies repository drift, unknown or pending core migrations, extension migration drift, checksum drift, and invalid extension manifests. See [Runtime Repair Policy](docs/process/runtime-repair-policy.md) for the rules that govern safe repairs.

To create and structurally verify a runtime backup before an operational update:

```bash
uv run python -m memory runtime backup [--mirror-home PATH]
uv run python -m memory runtime backup --verify PATH_TO_BACKUP.zip
```

Runtime backup archives contain `memory.db` and SQLite sidecars (`memory.db-wal`, `memory.db-shm`) when present. Verification is structural: the zip must be readable, contain `memory.db`, and avoid unsafe archive paths. Recovery remains manual in this version: stop active runtime sessions, move current database files aside, extract the backup into the Mirror home, and rerun runtime status.

To plan a runtime update without mutating files, git refs, backups, migrations, or the database:

```bash
uv run python -m memory runtime update --dry-run
```

The dry-run reuses runtime status as its safety gate, inspects the local branch's configured upstream without fetching, and reports whether a real update would be a no-op, pull known remote commits, or require manual reconciliation because the branch is ahead, diverged, dirty, or missing an upstream.

To list the active personas for the current user:

```bash
uv run python -m memory list personas --verbose
```

The database is the source of truth for personas. There is no authoritative
static table; `list personas --verbose` reflects the current seeded state.

---

## Configuration

`.env` is loaded automatically by `memory.config` at import time; values
already present in the real environment take precedence.

Two starter files live at the repo root:

- `.env.example` — minimal template (identity + API keys)
- `.env.example.advanced` — canonical reference with every variable documented

### Identity (CV4 user home)

| Variable | Default | Role |
|----------|---------|------|
| `MIRROR_HOME` | (unset) | Explicit path to the user's mirror home. Takes precedence over `MIRROR_USER`. |
| `MIRROR_USER` | (unset) | Short user name; resolves to `~/.mirror-minds/<user>`. |

In production, one of the two must be set. Setting both is only valid when
they agree (`MIRROR_HOME` ends with the same user name).

**Legacy path compatibility.** The default container was renamed from
`~/.mirror` to `~/.mirror-minds` in 2026-05. When `MIRROR_USER` resolution
is used and `~/.mirror-minds/<user>` does not exist but `~/.mirror/<user>`
does, the legacy path is resolved and a one-time warning is emitted. This
is permanent supported behavior. To stop the warning, run
`mv ~/.mirror ~/.mirror-minds` once.

### API Keys

| Variable | Role |
|----------|------|
| `OPENROUTER_API_KEY` | Embeddings (`openai/text-embedding-3-small` via OpenRouter), extraction (Gemini Flash), and the multi-LLM `consult` command. |

### Environment Selection

| Variable | Default | Role |
|----------|---------|------|
| `MEMORY_ENV` | `production` | One of `production`, `development`, `test`. Controls DB file name and gates `MemoryClient.reset`. |

### Path Overrides

All of these derive from `MIRROR_HOME` in production. Set them only to
override the default layout.

| Variable | Default | Role |
|----------|---------|------|
| `MEMORY_DIR` | `MIRROR_HOME` (prod) or `~/.mirror-minds` | Runtime working dir for `mute` and `.bootstrap.lock`. |
| `MEMORY_PROD_DIR` | `MEMORY_DIR` | Production-only override. |
| `DB_PATH` | `<MIRROR_HOME>/memory.db` | Full SQLite path. |
| `DB_BACKUP_PATH` | `<DB_PATH parent>/backups` | Legacy alias for `BACKUP_DIR`. |
| `BACKUP_DIR` | `<MIRROR_HOME>/backups` | `memory backup` output. |
| `EXPORT_DIR` | `<MIRROR_HOME>/exports` | Markdown export root. |
| `TRANSCRIPT_EXPORT_DIR` | `<EXPORT_DIR>/transcripts` | Full-transcript export dir. |

### Runtime Integrations

| Variable | Default | Role |
|----------|---------|------|
| `PI_SESSIONS_DIR` | `~/.pi/agent/sessions` | Source directory for `backfill_pi_sessions`. Override for multi-user setups. |
| `MIRROR_SESSION_ID` | (unset) | Fallback session id for conversation-logger CLIs when neither `--session-id` nor a hook payload is present. Rarely set by humans. |
| `MIRROR_WELCOME` | (unset) | Set to `off`, `0`, `false`, or `no` to suppress the welcome card emitted by `python -m memory welcome`. See `docs/product/specs/welcome/index.md`. |

### Set by External Runtimes (do not set manually)

- `CLAUDE_PROJECT_DIR` — injected by Claude Code when it invokes hooks.
- Claude Code hook payloads carry `session_id` on stdin.
- Pi's extension passes the session file path to the logger CLI.

---

## Legacy Migration Workflow

> **Note:** This workflow exists for users migrating from Portuguese-era
> databases (pre-CV0). Most early users have already completed this migration.
> This section is a removal candidate for a future CV.

Use this when you have a Portuguese-era source database such as `memoria.db`
and want to migrate it into a user home.

### Supported Source Policy

Supported:
- clean Portuguese legacy databases

Rejected explicitly:
- already-English/current databases
- mixed Portuguese/English databases
- unsupported or ambiguous SQLite shapes

### Commands

```bash
uv run python -m memory migrate-legacy validate \
  --source ~/.espelho/memoria.db \
  --target-home ~/.mirror-minds/<user> \
  --report /tmp/mirror-migration-validate.json

uv run python -m memory migrate-legacy run \
  --source ~/.espelho/memoria.db \
  --target-home ~/.mirror-minds/<user> \
  --report /tmp/mirror-migration-run.json
```

### Safety Guarantees

- explicit source required
- explicit target home required
- source is never mutated
- target `memory.db` must not already exist
- no silent merge into an existing target
- `validate` performs no writes
- `run` copies first, migrates the copy, and verifies the result

Both commands support `--report PATH`. The JSON report includes: generation
timestamp, command mode, source and target paths, source classification,
source row counts, applied migrations, detected legacy columns/indexes/identity
layers, planned translations, and post-migration verification details.

---

**See also:** [Getting Started](docs/getting-started.md) ·
[Architecture](docs/architecture.md) · [Python API](docs/api.md)
