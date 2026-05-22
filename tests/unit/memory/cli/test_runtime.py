"""Tests for runtime status CLI."""

import sqlite3
import zipfile
from pathlib import Path

from memory.cli.runtime import (
    BackupVerification,
    CoreMigrationHealth,
    ExtensionHealth,
    GitStatus,
    GitUpdatePlan,
    GitWorktreeEntry,
    RuntimeStatusReport,
    RuntimeUpdateDryRun,
    cmd_runtime,
    diagnose_runtime,
    inspect_core_migrations,
    inspect_extension_health,
    inspect_git_update_plan,
    render_runtime_backup_created,
    render_runtime_diagnosis,
    render_runtime_status,
    render_runtime_update_dry_run,
    verify_backup_archive,
)
from memory.db.migrations import MIGRATIONS
from memory.extensions.migrations import run_migrations


def _report(**overrides) -> RuntimeStatusReport:
    base = {
        "version": "0.7.0",
        "git": GitStatus(
            repository=Path("/repo"),
            branch="main",
            commit="abc1234",
            dirty=False,
        ),
        "mirror_home": Path("/home/.mirror-minds/alisson"),
        "mirror_home_error": None,
        "db_path": Path("/home/.mirror-minds/alisson/memory.db"),
        "db_exists": True,
        "core_migrations": CoreMigrationHealth(True, len(MIGRATIONS), len(MIGRATIONS), ()),
        "extensions": ("maestro",),
        "extension_health": (ExtensionHealth("maestro", True),),
        "python_version": "3.12.0",
        "memory_env": "production",
    }
    base.update(overrides)
    return RuntimeStatusReport(**base)


def _write_command_extension(root: Path, extension_id: str = "hello") -> Path:
    ext_dir = root / "extensions" / extension_id
    (ext_dir / "migrations").mkdir(parents=True)
    (ext_dir / "extension.py").write_text(
        "def register(api):\n    return None\n",
        encoding="utf-8",
    )
    (ext_dir / "skill.yaml").write_text(
        f"""
id: {extension_id}
name: Hello
category: extension
kind: command-skill
summary: Hello extension
entrypoint:
  module: extension
runtimes:
  pi:
    command_name: ext-{extension_id}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return ext_dir


def test_render_runtime_status_ready():
    rendered = render_runtime_status(_report())

    assert "Mirror runtime status" in rendered
    assert "Version: 0.7.0" in rendered
    assert "Repository: /repo" in rendered
    assert "Git dirty: no" in rendered
    assert f"Core migrations: current ({len(MIGRATIONS)}/{len(MIGRATIONS)})" in rendered
    assert "Installed extensions: 1 (maestro)" in rendered
    assert "Extension health: ready (1 checked)" in rendered
    assert "Status: ready" in rendered


def test_render_runtime_status_attention_needed_when_git_dirty():
    report = _report(git=GitStatus(Path("/repo"), "main", "abc1234", True))

    rendered = render_runtime_status(report)

    assert "Git dirty: yes" in rendered
    assert "Status: attention needed" in rendered


def test_render_runtime_status_attention_needed_when_mirror_home_missing():
    report = _report(
        mirror_home=None,
        mirror_home_error="Mirror home is not configured. Set MIRROR_HOME or MIRROR_USER.",
        db_path=None,
        db_exists=None,
        core_migrations=CoreMigrationHealth(False, None, len(MIGRATIONS), ()),
        extensions=(),
        extension_health=(),
    )

    rendered = render_runtime_status(report)

    assert "Mirror home: not configured" in rendered
    assert "Mirror home note: Mirror home is not configured" in rendered
    assert "Database exists: unknown" in rendered
    assert "Status: attention needed" in rendered


def test_render_runtime_status_attention_needed_when_core_migrations_missing():
    report = _report(
        core_migrations=CoreMigrationHealth(
            False, len(MIGRATIONS) - 1, len(MIGRATIONS), (MIGRATIONS[-1][0],)
        )
    )

    rendered = render_runtime_status(report)

    assert "Core migrations: attention needed" in rendered
    assert MIGRATIONS[-1][0] in rendered
    assert "Status: attention needed" in rendered


def test_render_runtime_status_attention_needed_when_extension_health_fails():
    report = _report(
        extension_health=(
            ExtensionHealth(
                "hello", False, "pending migrations", pending_migrations=("001_init.sql",)
            ),
        )
    )

    rendered = render_runtime_status(report)

    assert "Extension health: attention needed (1 checked, 1 issue(s))" in rendered
    assert "hello: pending migrations; pending 001_init.sql" in rendered
    assert "Status: attention needed" in rendered


def test_inspect_core_migrations_reports_current(tmp_path):
    db_path = tmp_path / "memory.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE _migrations (id TEXT PRIMARY KEY, applied_at TEXT NOT NULL)")
        conn.executemany(
            "INSERT INTO _migrations (id, applied_at) VALUES (?, 'now')",
            [(migration_id,) for migration_id, _ in MIGRATIONS],
        )

    health = inspect_core_migrations(db_path, True)

    assert health.ready is True
    assert health.applied_count == len(MIGRATIONS)
    assert health.missing == ()


def test_inspect_core_migrations_reports_missing_without_mutating(tmp_path):
    db_path = tmp_path / "memory.db"

    health = inspect_core_migrations(db_path, False)

    assert health.ready is False
    assert health.note == "database missing"
    assert not db_path.exists()


def test_inspect_core_migrations_reports_missing_ids(tmp_path):
    db_path = tmp_path / "memory.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE _migrations (id TEXT PRIMARY KEY, applied_at TEXT NOT NULL)")
        conn.executemany(
            "INSERT INTO _migrations (id, applied_at) VALUES (?, 'now')",
            [(migration_id,) for migration_id, _ in MIGRATIONS[:-1]],
        )

    health = inspect_core_migrations(db_path, True)

    assert health.ready is False
    assert health.missing == (MIGRATIONS[-1][0],)


def test_inspect_core_migrations_reports_unknown_ids(tmp_path):
    db_path = tmp_path / "memory.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE _migrations (id TEXT PRIMARY KEY, applied_at TEXT NOT NULL)")
        conn.executemany(
            "INSERT INTO _migrations (id, applied_at) VALUES (?, 'now')",
            [(migration_id,) for migration_id, _ in MIGRATIONS],
        )
        conn.execute("INSERT INTO _migrations (id, applied_at) VALUES ('999_local', 'now')")

    health = inspect_core_migrations(db_path, True)

    assert health.ready is False
    assert health.missing == ()
    assert health.unknown == ("999_local",)


def test_inspect_extension_health_reports_prompt_skill_ready(tmp_path):
    ext_dir = tmp_path / "extensions" / "prompt"
    ext_dir.mkdir(parents=True)
    (ext_dir / "SKILL.md").write_text("# Prompt\n", encoding="utf-8")
    (ext_dir / "skill.yaml").write_text(
        """
id: prompt
name: Prompt
category: extension
kind: prompt-skill
summary: Prompt extension
runtimes:
  pi:
    command_name: ext-prompt
    skill_file: SKILL.md
""".strip()
        + "\n",
        encoding="utf-8",
    )
    db_path = tmp_path / "memory.db"
    db_path.touch()

    health = inspect_extension_health(tmp_path, db_path, True)

    assert health == (ExtensionHealth("prompt", True),)


def test_inspect_extension_health_reports_invalid_manifest(tmp_path):
    ext_dir = tmp_path / "extensions" / "broken"
    ext_dir.mkdir(parents=True)
    (ext_dir / "skill.yaml").write_text("id: broken\n", encoding="utf-8")
    db_path = tmp_path / "memory.db"
    db_path.touch()

    health = inspect_extension_health(tmp_path, db_path, True)

    assert len(health) == 1
    assert health[0].extension_id == "broken"
    assert health[0].ready is False
    assert "missing required field" in (health[0].note or "")


def test_inspect_extension_health_reports_pending_command_migration(tmp_path):
    ext_dir = _write_command_extension(tmp_path)
    (ext_dir / "migrations" / "001_init.sql").write_text(
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);\n", encoding="utf-8"
    )
    db_path = tmp_path / "memory.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE _ext_migrations (extension_id TEXT, filename TEXT, "
            "checksum TEXT, applied_at TEXT, PRIMARY KEY (extension_id, filename))"
        )

    health = inspect_extension_health(tmp_path, db_path, True)

    assert health == (
        ExtensionHealth(
            "hello", False, "pending migrations", pending_migrations=("001_init.sql",)
        ),
    )


def test_inspect_extension_health_reports_checksum_drift(tmp_path):
    ext_dir = _write_command_extension(tmp_path)
    migration = ext_dir / "migrations" / "001_init.sql"
    migration.write_text(
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);\n", encoding="utf-8"
    )
    db_path = tmp_path / "memory.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE _ext_migrations (extension_id TEXT, filename TEXT, "
            "checksum TEXT, applied_at TEXT, PRIMARY KEY (extension_id, filename))"
        )
        run_migrations(conn, extension_id="hello", migrations_dir=ext_dir / "migrations")
    migration.write_text(
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY, title TEXT);\n",
        encoding="utf-8",
    )

    health = inspect_extension_health(tmp_path, db_path, True)

    assert health == (
        ExtensionHealth(
            "hello", False, "migration checksum drift", drifted_migrations=("001_init.sql",)
        ),
    )


def test_inspect_extension_health_reports_unknown_migration(tmp_path):
    ext_dir = _write_command_extension(tmp_path)
    (ext_dir / "migrations" / "002_current.sql").write_text(
        "CREATE TABLE ext_hello_current (id INTEGER PRIMARY KEY);\n",
        encoding="utf-8",
    )
    db_path = tmp_path / "memory.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE _ext_migrations (extension_id TEXT, filename TEXT, "
            "checksum TEXT, applied_at TEXT, PRIMARY KEY (extension_id, filename))"
        )
        conn.execute(
            "INSERT INTO _ext_migrations (extension_id, filename, checksum, applied_at) "
            "VALUES ('hello', '001_legacy.sql', 'abc', 'now')"
        )

    health = inspect_extension_health(tmp_path, db_path, True)

    assert health[0].ready is False
    assert health[0].unknown_migrations == ("001_legacy.sql",)


def test_diagnose_runtime_reports_drift_findings():
    report = _report(
        core_migrations=CoreMigrationHealth(
            False,
            len(MIGRATIONS),
            len(MIGRATIONS),
            (),
            unknown=("999_local",),
        ),
        extension_health=(
            ExtensionHealth(
                "maestro",
                False,
                "unknown applied migrations",
                unknown_migrations=("001_init.sql",),
            ),
        ),
    )

    findings = diagnose_runtime(report, (GitWorktreeEntry("??", "pi-session-x.html"),))

    assert [finding.code for finding in findings] == [
        "git_dirty",
        "core_migration_unknown",
        "extension_migration_unknown",
    ]
    assert "archive or ignore" in findings[0].recommendation


def test_render_runtime_diagnosis_ready():
    rendered = render_runtime_diagnosis(())

    assert "Mirror runtime drift diagnosis" in rendered
    assert "Findings: 0" in rendered
    assert "Status: ready" in rendered


def test_cmd_runtime_status_dispatches(monkeypatch, capsys):
    monkeypatch.setattr(
        "memory.cli.runtime.build_runtime_status", lambda mirror_home_arg=None: _report()
    )

    rc = cmd_runtime(["status"])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Mirror runtime status" in out
    assert "Status: ready" in out


def test_cmd_runtime_status_returns_nonzero_when_attention_needed(monkeypatch, capsys):
    monkeypatch.setattr(
        "memory.cli.runtime.build_runtime_status",
        lambda mirror_home_arg=None: _report(
            git=GitStatus(Path("/repo"), "main", "abc1234", True)
        ),
    )

    rc = cmd_runtime(["status"])

    out = capsys.readouterr().out
    assert rc == 1
    assert "Status: attention needed" in out


def test_inspect_git_update_plan_reports_missing_upstream(monkeypatch):
    def fake_run_git(args, *, cwd):
        if args[:2] == ["rev-parse", "--abbrev-ref"]:
            return 128, "", "no upstream configured"
        raise AssertionError(args)

    monkeypatch.setattr("memory.cli.runtime._run_git", fake_run_git)

    plan = inspect_git_update_plan(GitStatus(Path("/repo"), "main", "abc1234", False))

    assert plan == GitUpdatePlan(None, None, None, False, "blocked", "no upstream configured")


def test_inspect_git_update_plan_reports_equal_branch(monkeypatch):
    def fake_run_git(args, *, cwd):
        if args[:2] == ["rev-parse", "--abbrev-ref"]:
            return 0, "origin/main", ""
        if args[:2] == ["rev-list", "--left-right"]:
            return 0, "0 0", ""
        raise AssertionError(args)

    monkeypatch.setattr("memory.cli.runtime._run_git", fake_run_git)

    plan = inspect_git_update_plan(GitStatus(Path("/repo"), "main", "abc1234", False))

    assert plan == GitUpdatePlan("origin/main", 0, 0, True, "none", "already up to date")


def test_inspect_git_update_plan_reports_behind_branch(monkeypatch):
    def fake_run_git(args, *, cwd):
        if args[:2] == ["rev-parse", "--abbrev-ref"]:
            return 0, "origin/main", ""
        if args[:2] == ["rev-list", "--left-right"]:
            return 0, "0 3", ""
        raise AssertionError(args)

    monkeypatch.setattr("memory.cli.runtime._run_git", fake_run_git)

    plan = inspect_git_update_plan(GitStatus(Path("/repo"), "main", "abc1234", False))

    assert plan == GitUpdatePlan("origin/main", 0, 3, True, "pull", "pull 3 remote commit(s)")


def test_inspect_git_update_plan_blocks_ahead_branch(monkeypatch):
    def fake_run_git(args, *, cwd):
        if args[:2] == ["rev-parse", "--abbrev-ref"]:
            return 0, "origin/main", ""
        if args[:2] == ["rev-list", "--left-right"]:
            return 0, "2 0", ""
        raise AssertionError(args)

    monkeypatch.setattr("memory.cli.runtime._run_git", fake_run_git)

    plan = inspect_git_update_plan(GitStatus(Path("/repo"), "main", "abc1234", False))

    assert plan == GitUpdatePlan("origin/main", 2, 0, False, "blocked", "local commits present")


def test_inspect_git_update_plan_blocks_diverged_branch(monkeypatch):
    def fake_run_git(args, *, cwd):
        if args[:2] == ["rev-parse", "--abbrev-ref"]:
            return 0, "origin/main", ""
        if args[:2] == ["rev-list", "--left-right"]:
            return 0, "2 4", ""
        raise AssertionError(args)

    monkeypatch.setattr("memory.cli.runtime._run_git", fake_run_git)

    plan = inspect_git_update_plan(GitStatus(Path("/repo"), "main", "abc1234", False))

    assert plan == GitUpdatePlan("origin/main", 2, 4, False, "blocked", "branch diverged")


def test_render_runtime_update_dry_run_blocks_dirty_status():
    dry_run = RuntimeUpdateDryRun(
        _report(git=GitStatus(Path("/repo"), "main", "abc1234", True)), None
    )

    rendered = render_runtime_update_dry_run(dry_run)

    assert "Mirror runtime update dry-run" in rendered
    assert "Current status: attention needed" in rendered
    assert "git tree is dirty" in rendered
    assert "Dry-run result: blocked" in rendered


def test_render_runtime_update_dry_run_ready_plan_includes_backup_and_validation():
    dry_run = RuntimeUpdateDryRun(
        _report(), GitUpdatePlan("origin/main", 0, 3, True, "pull", "pull 3 remote commit(s)")
    )

    rendered = render_runtime_update_dry_run(dry_run)

    assert "Current status: ready" in rendered
    assert "Upstream: origin/main" in rendered
    assert "Update plan: pull 3 remote commit(s)" in rendered
    assert "Backup: required before real update" in rendered
    assert 'uv run pytest tests/unit/ tests/integration/ -m "not live"' in rendered
    assert "Dry-run result: ready" in rendered


def test_cmd_runtime_diagnose_dispatches(monkeypatch, capsys):
    monkeypatch.setattr(
        "memory.cli.runtime.build_runtime_status",
        lambda mirror_home_arg=None: _report(
            core_migrations=CoreMigrationHealth(
                False,
                len(MIGRATIONS),
                len(MIGRATIONS),
                (),
                unknown=("999_local",),
            )
        ),
    )
    monkeypatch.setattr("memory.cli.runtime.inspect_git_worktree", lambda repository: ())

    rc = cmd_runtime(["diagnose"])

    out = capsys.readouterr().out
    assert rc == 1
    assert "core_migration_unknown" in out
    assert "Status: attention needed" in out


def test_cmd_runtime_update_requires_dry_run(capsys):
    rc = cmd_runtime(["update"])

    captured = capsys.readouterr()
    assert rc == 1
    assert "runtime update currently supports --dry-run only" in captured.err


def test_cmd_runtime_update_dry_run_dispatches(monkeypatch, capsys):
    monkeypatch.setattr(
        "memory.cli.runtime.build_runtime_update_dry_run",
        lambda mirror_home_arg=None: RuntimeUpdateDryRun(
            _report(),
            GitUpdatePlan("origin/main", 0, 0, True, "none", "already up to date"),
        ),
    )

    rc = cmd_runtime(["update", "--dry-run"])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Mirror runtime update dry-run" in out
    assert "Dry-run result: ready" in out


def test_cmd_runtime_update_dry_run_returns_nonzero_when_blocked(monkeypatch, capsys):
    monkeypatch.setattr(
        "memory.cli.runtime.build_runtime_update_dry_run",
        lambda mirror_home_arg=None: RuntimeUpdateDryRun(
            _report(git=GitStatus(Path("/repo"), "main", "abc1234", True)), None
        ),
    )

    rc = cmd_runtime(["update", "--dry-run"])

    out = capsys.readouterr().out
    assert rc == 1
    assert "Dry-run result: blocked" in out


def test_verify_backup_archive_accepts_memory_db_zip(tmp_path):
    backup_path = tmp_path / "memory.zip"
    with zipfile.ZipFile(backup_path, "w") as zf:
        zf.writestr("memory.db", "db")
        zf.writestr("memory.db-wal", "wal")

    verification = verify_backup_archive(backup_path)

    assert verification == BackupVerification(backup_path, True, ("memory.db", "memory.db-wal"))


def test_verify_backup_archive_rejects_missing_file(tmp_path):
    backup_path = tmp_path / "missing.zip"

    verification = verify_backup_archive(backup_path)

    assert verification == BackupVerification(backup_path, False, (), "backup file not found")


def test_verify_backup_archive_rejects_non_zip(tmp_path):
    backup_path = tmp_path / "not.zip"
    backup_path.write_text("not a zip", encoding="utf-8")

    verification = verify_backup_archive(backup_path)

    assert verification == BackupVerification(
        backup_path, False, (), "backup file is not a readable zip"
    )


def test_verify_backup_archive_rejects_zip_without_memory_db(tmp_path):
    backup_path = tmp_path / "memory.zip"
    with zipfile.ZipFile(backup_path, "w") as zf:
        zf.writestr("notes.txt", "no")

    verification = verify_backup_archive(backup_path)

    assert verification.valid is False
    assert verification.note == "memory.db missing from backup"


def test_verify_backup_archive_rejects_unsafe_entries(tmp_path):
    backup_path = tmp_path / "memory.zip"
    with zipfile.ZipFile(backup_path, "w") as zf:
        zf.writestr("memory.db", "db")
        zf.writestr("../escape", "bad")

    verification = verify_backup_archive(backup_path)

    assert verification.valid is False
    assert verification.note == "unsafe archive entry: ../escape"


def test_render_runtime_backup_created_includes_recovery_route(tmp_path):
    backup_path = tmp_path / "backups" / "memory.zip"
    verification = BackupVerification(backup_path, True, ("memory.db",))

    rendered = render_runtime_backup_created(
        backup_path=backup_path, mirror_home=tmp_path, verification=verification
    )

    assert "Mirror runtime backup" in rendered
    assert "Verification result: valid" in rendered
    assert "Manual recovery route:" in rendered
    assert "Recovery is manual" in rendered


def test_cmd_runtime_backup_creates_and_verifies_archive(tmp_path, capsys):
    db_path = tmp_path / "memory.db"
    db_path.write_text("db content", encoding="utf-8")

    rc = cmd_runtime(["backup", "--mirror-home", str(tmp_path)])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Mirror runtime backup" in out
    assert "Verification result: valid" in out
    assert list((tmp_path / "backups").glob("memory_*.zip"))


def test_cmd_runtime_backup_missing_database_returns_nonzero(tmp_path, capsys):
    rc = cmd_runtime(["backup", "--mirror-home", str(tmp_path)])

    captured = capsys.readouterr()
    assert rc == 1
    assert "Database not found" in captured.err
    assert not (tmp_path / "backups").exists()


def test_cmd_runtime_backup_verify_dispatches(tmp_path, capsys):
    backup_path = tmp_path / "memory.zip"
    with zipfile.ZipFile(backup_path, "w") as zf:
        zf.writestr("memory.db", "db")

    rc = cmd_runtime(["backup", "--verify", str(backup_path)])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Mirror runtime backup verification" in out
    assert "Verification result: valid" in out


def test_cmd_runtime_backup_verify_returns_nonzero_for_invalid_archive(tmp_path, capsys):
    backup_path = tmp_path / "bad.zip"
    backup_path.write_text("bad", encoding="utf-8")

    rc = cmd_runtime(["backup", "--verify", str(backup_path)])

    out = capsys.readouterr().out
    assert rc == 1
    assert "Verification result: invalid" in out
