"""Runtime status inspection for Mirror Mind."""

from __future__ import annotations

import argparse
import sqlite3
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path

from memory.cli.backup import backup as create_backup
from memory.cli.extensions import ExtensionValidationError, load_extension_manifest
from memory.config import (
    MEMORY_ENV,
    default_db_path_for_home,
    default_extensions_dir_for_home,
    resolve_mirror_home,
)
from memory.db.migrations import MIGRATIONS
from memory.extensions.migrations import ExtensionMigrationError, inspect_migration_files


@dataclass(frozen=True)
class BackupVerification:
    backup_path: Path
    valid: bool
    entries: tuple[str, ...]
    note: str | None = None


@dataclass(frozen=True)
class GitStatus:
    repository: Path | None
    branch: str | None
    commit: str | None
    dirty: bool | None
    error: str | None = None


@dataclass(frozen=True)
class CoreMigrationHealth:
    ready: bool
    applied_count: int | None
    known_count: int
    missing: tuple[str, ...]
    unknown: tuple[str, ...] = ()
    note: str | None = None


@dataclass(frozen=True)
class ExtensionHealth:
    extension_id: str
    ready: bool
    note: str | None = None
    pending_migrations: tuple[str, ...] = ()
    drifted_migrations: tuple[str, ...] = ()
    unknown_migrations: tuple[str, ...] = ()


@dataclass(frozen=True)
class GitWorktreeEntry:
    status: str
    path: str


@dataclass(frozen=True)
class DriftFinding:
    code: str
    severity: str
    subject: str
    detail: str
    recommendation: str
    repair_route: str


@dataclass(frozen=True)
class GitUpdatePlan:
    upstream: str | None
    ahead: int | None
    behind: int | None
    ready: bool
    action: str
    note: str | None = None


@dataclass(frozen=True)
class RuntimeUpdateDryRun:
    status_report: RuntimeStatusReport
    git_plan: GitUpdatePlan | None

    @property
    def ready(self) -> bool:
        return self.status_report.status == "ready" and bool(self.git_plan and self.git_plan.ready)


@dataclass(frozen=True)
class RuntimeStatusReport:
    version: str
    git: GitStatus
    mirror_home: Path | None
    mirror_home_error: str | None
    db_path: Path | None
    db_exists: bool | None
    core_migrations: CoreMigrationHealth
    extensions: tuple[str, ...]
    extension_health: tuple[ExtensionHealth, ...]
    python_version: str
    memory_env: str

    @property
    def status(self) -> str:
        if self.mirror_home_error:
            return "attention needed"
        if self.git.error:
            return "attention needed"
        if self.git.dirty:
            return "attention needed"
        if self.db_exists is False:
            return "attention needed"
        if not self.core_migrations.ready:
            return "attention needed"
        if any(not health.ready for health in self.extension_health):
            return "attention needed"
        return "ready"


def package_version() -> str:
    try:
        return metadata.version("mirror")
    except metadata.PackageNotFoundError:
        return _version_from_pyproject(Path.cwd()) or "unknown"


def _version_from_pyproject(start: Path) -> str | None:
    for parent in (start.resolve(), *start.resolve().parents):
        pyproject = parent / "pyproject.toml"
        if not pyproject.exists():
            continue
        for line in pyproject.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("version ="):
                return line.partition("=")[2].strip().strip('"')
    return None


def _run_git(args: list[str], *, cwd: Path) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def _parse_porcelain_line(line: str) -> GitWorktreeEntry | None:
    if not line:
        return None
    status = line[:2]
    path = line[2:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return GitWorktreeEntry(status=status, path=path)


def inspect_git_worktree(repository: Path | None) -> tuple[GitWorktreeEntry, ...]:
    if repository is None:
        return ()
    code, stdout, _stderr = _run_git(["status", "--porcelain"], cwd=repository)
    if code != 0 or not stdout:
        return ()
    entries = [_parse_porcelain_line(line) for line in stdout.splitlines()]
    return tuple(entry for entry in entries if entry is not None)


def inspect_git(start: Path) -> GitStatus:
    code, stdout, stderr = _run_git(["rev-parse", "--show-toplevel"], cwd=start)
    if code != 0 or not stdout:
        return GitStatus(
            repository=None,
            branch=None,
            commit=None,
            dirty=None,
            error=stderr or "not a git repository",
        )

    repository = Path(stdout).resolve()
    branch_code, branch, branch_err = _run_git(["branch", "--show-current"], cwd=repository)
    commit_code, commit, commit_err = _run_git(["rev-parse", "--short", "HEAD"], cwd=repository)
    dirty_code, dirty_out, dirty_err = _run_git(["status", "--porcelain"], cwd=repository)

    errors = [
        err
        for code, err in (
            (branch_code, branch_err),
            (commit_code, commit_err),
            (dirty_code, dirty_err),
        )
        if code != 0 and err
    ]

    return GitStatus(
        repository=repository,
        branch=branch if branch_code == 0 and branch else None,
        commit=commit if commit_code == 0 and commit else None,
        dirty=bool(dirty_out) if dirty_code == 0 else None,
        error="; ".join(errors) if errors else None,
    )


def list_installed_extensions(mirror_home: Path | None) -> tuple[str, ...]:
    if mirror_home is None:
        return ()
    extensions_dir = default_extensions_dir_for_home(mirror_home)
    if not extensions_dir.exists() or not extensions_dir.is_dir():
        return ()
    return tuple(
        sorted(
            child.name
            for child in extensions_dir.iterdir()
            if child.is_dir() and (child / "skill.yaml").exists()
        )
    )


def _connect_read_only(db_path: Path) -> sqlite3.Connection:
    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
    ).fetchone()
    return row is not None


def inspect_core_migrations(db_path: Path | None, db_exists: bool | None) -> CoreMigrationHealth:
    known_ids = tuple(migration_id for migration_id, _ in MIGRATIONS)
    if db_path is None:
        return CoreMigrationHealth(False, None, len(known_ids), (), note="database path unknown")
    if db_exists is not True:
        return CoreMigrationHealth(False, None, len(known_ids), (), note="database missing")
    try:
        with _connect_read_only(db_path) as conn:
            if not _table_exists(conn, "_migrations"):
                return CoreMigrationHealth(
                    False, 0, len(known_ids), known_ids, note="migration ledger missing"
                )
            rows = conn.execute("SELECT id FROM _migrations").fetchall()
    except sqlite3.Error as exc:
        return CoreMigrationHealth(False, None, len(known_ids), known_ids, note=str(exc))

    known_set = set(known_ids)
    applied = {row[0] for row in rows}
    missing = tuple(migration_id for migration_id in known_ids if migration_id not in applied)
    unknown = tuple(
        sorted(migration_id for migration_id in applied if migration_id not in known_set)
    )
    return CoreMigrationHealth(
        ready=not missing and not unknown,
        applied_count=len(applied.intersection(known_ids)),
        known_count=len(known_ids),
        missing=missing,
        unknown=unknown,
    )


def inspect_extension_health(
    mirror_home: Path | None, db_path: Path | None, db_exists: bool | None
) -> tuple[ExtensionHealth, ...]:
    if mirror_home is None:
        return ()
    extensions_dir = default_extensions_dir_for_home(mirror_home)
    if not extensions_dir.exists() or not extensions_dir.is_dir():
        return ()

    results: list[ExtensionHealth] = []
    conn: sqlite3.Connection | None = None
    if db_path is not None and db_exists is True:
        try:
            conn = _connect_read_only(db_path)
        except sqlite3.Error:
            conn = None

    try:
        for child in sorted(extensions_dir.iterdir()):
            if not child.is_dir() or not (child / "skill.yaml").exists():
                continue
            extension_id = child.name
            try:
                manifest = load_extension_manifest(child)
                extension_id = manifest["id"]
            except ExtensionValidationError as exc:
                results.append(ExtensionHealth(extension_id, False, str(exc)))
                continue

            if manifest["kind"] != "command-skill":
                results.append(ExtensionHealth(extension_id, True))
                continue

            if conn is None:
                results.append(ExtensionHealth(extension_id, False, "database unavailable"))
                continue
            if not _table_exists(conn, "_ext_migrations"):
                migrations_dir = child / "migrations"
                has_migrations = migrations_dir.exists() and any(migrations_dir.glob("*.sql"))
                results.append(
                    ExtensionHealth(
                        extension_id,
                        not has_migrations,
                        "extension migration ledger missing" if has_migrations else None,
                    )
                )
                continue

            try:
                migrations_dir = child / "migrations"
                pending, drifted = inspect_migration_files(
                    conn, extension_id=extension_id, migrations_dir=migrations_dir
                )
                known_files = {
                    path.name
                    for path in migrations_dir.glob("*.sql")
                    if path.is_file()
                }
                rows = conn.execute(
                    "SELECT filename FROM _ext_migrations WHERE extension_id = ?",
                    (extension_id,),
                ).fetchall()
                unknown = tuple(
                    sorted(str(row[0]) for row in rows if str(row[0]) not in known_files)
                )
            except (ExtensionMigrationError, sqlite3.Error) as exc:
                results.append(ExtensionHealth(extension_id, False, str(exc)))
                continue
            note = None
            if pending:
                note = "pending migrations"
            if drifted:
                note = "migration checksum drift" if note is None else f"{note}; checksum drift"
            if unknown:
                note = "unknown applied migrations" if note is None else f"{note}; unknown applied"
            results.append(
                ExtensionHealth(
                    extension_id,
                    not pending and not drifted and not unknown,
                    note,
                    pending_migrations=pending,
                    drifted_migrations=drifted,
                    unknown_migrations=unknown,
                )
            )
    finally:
        if conn is not None:
            conn.close()

    return tuple(results)


def build_runtime_status(
    *,
    start: Path | None = None,
    mirror_home_arg: str | Path | None = None,
) -> RuntimeStatusReport:
    start_path = (start or Path.cwd()).expanduser().resolve()
    git = inspect_git(start_path)

    mirror_home: Path | None = None
    mirror_home_error: str | None = None
    try:
        mirror_home = resolve_mirror_home(mirror_home=mirror_home_arg)
    except ValueError as exc:
        mirror_home_error = str(exc)

    db_path = default_db_path_for_home(mirror_home) if mirror_home else None
    db_exists = db_path.exists() if db_path else None

    return RuntimeStatusReport(
        version=package_version(),
        git=git,
        mirror_home=mirror_home,
        mirror_home_error=mirror_home_error,
        db_path=db_path,
        db_exists=db_exists,
        core_migrations=inspect_core_migrations(db_path, db_exists),
        extensions=list_installed_extensions(mirror_home),
        extension_health=inspect_extension_health(mirror_home, db_path, db_exists),
        python_version=sys.version.split()[0],
        memory_env=MEMORY_ENV,
    )


def verify_backup_archive(backup_path: Path) -> BackupVerification:
    if not backup_path.exists():
        return BackupVerification(backup_path, False, (), "backup file not found")
    try:
        with zipfile.ZipFile(backup_path) as zf:
            entries = tuple(sorted(zf.namelist()))
    except zipfile.BadZipFile:
        return BackupVerification(backup_path, False, (), "backup file is not a readable zip")

    for entry in entries:
        entry_path = Path(entry)
        if entry_path.is_absolute() or ".." in entry_path.parts:
            return BackupVerification(
                backup_path, False, entries, f"unsafe archive entry: {entry}"
            )
    if "memory.db" not in entries:
        return BackupVerification(backup_path, False, entries, "memory.db missing from backup")
    allowed = {"memory.db", "memory.db-wal", "memory.db-shm"}
    unexpected = tuple(entry for entry in entries if entry not in allowed)
    if unexpected:
        return BackupVerification(
            backup_path, False, entries, f"unexpected archive entries: {', '.join(unexpected)}"
        )
    return BackupVerification(backup_path, True, entries)


def render_backup_verification(verification: BackupVerification) -> str:
    lines: list[str] = []
    lines.append("Mirror runtime backup verification")
    lines.append("")
    lines.append(f"Backup: {verification.backup_path}")
    if verification.entries:
        lines.append(f"Entries: {', '.join(verification.entries)}")
    if verification.note:
        lines.append(f"Verification note: {verification.note}")
    lines.append(f"Verification result: {'valid' if verification.valid else 'invalid'}")
    return "\n".join(lines) + "\n"


def render_runtime_backup_created(
    *, backup_path: Path, mirror_home: Path, verification: BackupVerification
) -> str:
    lines: list[str] = []
    lines.append("Mirror runtime backup")
    lines.append("")
    lines.append(f"Mirror home: {mirror_home}")
    lines.append(f"Backup: {backup_path}")
    lines.append(f"Verification result: {'valid' if verification.valid else 'invalid'}")
    if verification.entries:
        lines.append(f"Entries: {', '.join(verification.entries)}")
    if verification.note:
        lines.append(f"Verification note: {verification.note}")
    lines.append("")
    lines.append("Manual recovery route:")
    lines.append("  1. Stop active runtime sessions that could write to the database.")
    lines.append("  2. Move current memory.db, memory.db-wal, and memory.db-shm aside.")
    lines.append("  3. Extract memory.db and sidecars from this backup into the Mirror home.")
    lines.append("  4. Run runtime status against the Mirror home.")
    lines.append("  5. Do not retry update execution until status is ready.")
    lines.append("")
    lines.append("Recovery is manual in this version; no files were restored.")
    return "\n".join(lines) + "\n"


def inspect_git_update_plan(git: GitStatus) -> GitUpdatePlan:
    if git.repository is None:
        return GitUpdatePlan(None, None, None, False, "blocked", "repository unavailable")
    code, upstream, stderr = _run_git(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=git.repository
    )
    if code != 0 or not upstream:
        return GitUpdatePlan(
            None, None, None, False, "blocked", stderr or "no upstream configured"
        )

    count_code, counts, count_err = _run_git(
        ["rev-list", "--left-right", "--count", "HEAD...@{u}"], cwd=git.repository
    )
    if count_code != 0 or not counts:
        return GitUpdatePlan(
            upstream, None, None, False, "blocked", count_err or "cannot compare upstream"
        )
    try:
        ahead_text, behind_text = counts.split()
        ahead = int(ahead_text)
        behind = int(behind_text)
    except ValueError:
        return GitUpdatePlan(
            upstream, None, None, False, "blocked", f"unexpected git count: {counts}"
        )

    if ahead == 0 and behind == 0:
        return GitUpdatePlan(upstream, ahead, behind, True, "none", "already up to date")
    if ahead == 0 and behind > 0:
        return GitUpdatePlan(
            upstream, ahead, behind, True, "pull", f"pull {behind} remote commit(s)"
        )
    if ahead > 0 and behind == 0:
        return GitUpdatePlan(upstream, ahead, behind, False, "blocked", "local commits present")
    return GitUpdatePlan(upstream, ahead, behind, False, "blocked", "branch diverged")


def build_runtime_update_dry_run(
    *,
    start: Path | None = None,
    mirror_home_arg: str | Path | None = None,
) -> RuntimeUpdateDryRun:
    status_report = build_runtime_status(start=start, mirror_home_arg=mirror_home_arg)
    git_plan = (
        inspect_git_update_plan(status_report.git) if status_report.status == "ready" else None
    )
    return RuntimeUpdateDryRun(status_report=status_report, git_plan=git_plan)


def _yes_no(value: bool | None) -> str:
    if value is None:
        return "unknown"
    return "yes" if value else "no"


def _render_core_migrations(health: CoreMigrationHealth) -> str:
    if health.ready:
        return f"Core migrations: current ({health.applied_count}/{health.known_count})"
    count = "unknown" if health.applied_count is None else str(health.applied_count)
    detail = f"{count}/{health.known_count} applied"
    if health.missing:
        detail = f"{detail}; missing {', '.join(health.missing)}"
    if health.unknown:
        detail = f"{detail}; unknown {', '.join(health.unknown)}"
    if health.note:
        detail = f"{detail}; {health.note}"
    return f"Core migrations: attention needed ({detail})"


def _render_extension_health(items: tuple[ExtensionHealth, ...]) -> list[str]:
    if not items:
        return ["Extension health: ready (0 checked)"]
    issue_count = sum(1 for item in items if not item.ready)
    if issue_count == 0:
        return [f"Extension health: ready ({len(items)} checked)"]

    lines = [f"Extension health: attention needed ({len(items)} checked, {issue_count} issue(s))"]
    for item in items:
        if item.ready:
            continue
        details: list[str] = []
        if item.note:
            details.append(item.note)
        if item.pending_migrations:
            details.append(f"pending {', '.join(item.pending_migrations)}")
        if item.drifted_migrations:
            details.append(f"drifted {', '.join(item.drifted_migrations)}")
        if item.unknown_migrations:
            details.append(f"unknown {', '.join(item.unknown_migrations)}")
        lines.append(
            f"  - {item.extension_id}: {'; '.join(details) if details else 'attention needed'}"
        )
    return lines


def _runtime_status_blockers(report: RuntimeStatusReport) -> list[str]:
    blockers: list[str] = []
    if report.mirror_home_error:
        blockers.append("mirror home is not configured")
    if report.git.error:
        blockers.append(f"git status error: {report.git.error}")
    if report.git.dirty:
        blockers.append("git tree is dirty")
    if report.db_exists is False:
        blockers.append("database is missing")
    if not report.core_migrations.ready:
        blockers.append("core migrations are not current")
    for health in report.extension_health:
        if not health.ready:
            blockers.append(f"extension {health.extension_id} needs attention")
    return blockers


def _git_dirty_finding(entry: GitWorktreeEntry) -> DriftFinding:
    is_session_html = entry.path.startswith("pi-session-") and entry.path.endswith(".html")
    if entry.status == "??" and is_session_html:
        recommendation = "archive or ignore generated session HTML before update planning"
        repair_route = "manual review"
    elif entry.status == "??":
        recommendation = "review untracked file before update planning"
        repair_route = "manual review"
    else:
        recommendation = "commit, stash, or discard intentional work before update planning"
        repair_route = "commit or manual review"
    return DriftFinding(
        code="git_dirty",
        severity="attention",
        subject="repository",
        detail=f"{entry.status} {entry.path}",
        recommendation=recommendation,
        repair_route=repair_route,
    )


def diagnose_runtime(
    report: RuntimeStatusReport,
    worktree_entries: tuple[GitWorktreeEntry, ...] = (),
) -> tuple[DriftFinding, ...]:
    findings: list[DriftFinding] = []
    if report.mirror_home_error:
        findings.append(
            DriftFinding(
                "mirror_home_missing",
                "blocker",
                "mirror home",
                report.mirror_home_error,
                "configure MIRROR_HOME or MIRROR_USER before update planning",
                "configuration",
            )
        )
    if report.db_exists is False:
        findings.append(
            DriftFinding(
                "database_missing",
                "blocker",
                "database",
                str(report.db_path) if report.db_path else "unknown",
                "restore or initialize the memory database before update planning",
                "restore or initialize",
            )
        )

    findings.extend(_git_dirty_finding(entry) for entry in worktree_entries)

    for migration_id in report.core_migrations.missing:
        findings.append(
            DriftFinding(
                "core_migration_pending",
                "blocker",
                "database _migrations",
                migration_id,
                "run pending core migrations only after backup",
                "backup then migrate",
            )
        )
    for migration_id in report.core_migrations.unknown:
        findings.append(
            DriftFinding(
                "core_migration_unknown",
                "attention",
                "database _migrations",
                migration_id,
                "classify as legacy core row, extension-owned row, or experimental drift",
                "manual review",
            )
        )
    if report.core_migrations.note:
        findings.append(
            DriftFinding(
                "core_migration_unreadable",
                "blocker",
                "database _migrations",
                report.core_migrations.note,
                "restore readable migration tracking before update planning",
                "database repair",
            )
        )

    for extension in report.extension_health:
        if extension.note and "missing required field" in extension.note:
            findings.append(
                DriftFinding(
                    "extension_manifest_invalid",
                    "blocker",
                    f"extension/{extension.extension_id}",
                    extension.note,
                    "repair or reinstall the extension manifest before update planning",
                    "extension repair",
                )
            )
        for filename in extension.pending_migrations:
            findings.append(
                DriftFinding(
                    "extension_migration_pending",
                    "blocker",
                    f"extension/{extension.extension_id}",
                    filename,
                    "run pending extension migrations only after backup",
                    "backup then extension migrate",
                )
            )
        for filename in extension.drifted_migrations:
            findings.append(
                DriftFinding(
                    "extension_migration_checksum_drift",
                    "blocker",
                    f"extension/{extension.extension_id}",
                    filename,
                    "restore the original migration file or create a new migration",
                    "extension repair",
                )
            )
        for filename in extension.unknown_migrations:
            findings.append(
                DriftFinding(
                    "extension_migration_unknown",
                    "attention",
                    f"extension/{extension.extension_id}",
                    filename,
                    "compare installed extension with canonical source and classify history",
                    "manual review or reinstall",
                )
            )
    return tuple(findings)


def render_runtime_diagnosis(findings: tuple[DriftFinding, ...]) -> str:
    lines: list[str] = ["Mirror runtime drift diagnosis", ""]
    if not findings:
        lines.append("Findings: 0")
        lines.append("")
        lines.append("Status: ready")
        return "\n".join(lines) + "\n"

    lines.append(f"Findings: {len(findings)} attention needed")
    for finding in findings:
        lines.append("")
        lines.append(f"[{finding.severity}] {finding.code}: {finding.detail}")
        lines.append(f"Subject: {finding.subject}")
        lines.append(f"Recommendation: {finding.recommendation}")
        lines.append(f"Repair route: {finding.repair_route}")
    lines.append("")
    lines.append("Status: attention needed")
    return "\n".join(lines) + "\n"


def render_runtime_update_dry_run(dry_run: RuntimeUpdateDryRun) -> str:
    report = dry_run.status_report
    lines: list[str] = []
    lines.append("Mirror runtime update dry-run")
    lines.append("")
    lines.append(f"Current status: {report.status}")
    lines.append(f"Repository: {report.git.repository if report.git.repository else 'unknown'}")
    lines.append(f"Git branch: {report.git.branch or 'unknown'}")

    blockers = _runtime_status_blockers(report)
    if blockers:
        lines.append("Blocked:")
        for blocker in blockers:
            lines.append(f"  - {blocker}")
        lines.append("")
        lines.append("Dry-run result: blocked")
        return "\n".join(lines) + "\n"

    git_plan = dry_run.git_plan
    if git_plan is None:
        lines.append("Blocked:")
        lines.append("  - git update plan unavailable")
        lines.append("")
        lines.append("Dry-run result: blocked")
        return "\n".join(lines) + "\n"

    lines.append(f"Upstream: {git_plan.upstream or 'not configured'}")
    if git_plan.ahead is not None and git_plan.behind is not None:
        lines.append(f"Git relation: ahead {git_plan.ahead}, behind {git_plan.behind}")

    if not git_plan.ready:
        lines.append("Blocked:")
        lines.append(f"  - {git_plan.note or 'git update is not safe to plan'}")
        lines.append("")
        lines.append("Dry-run result: blocked")
        return "\n".join(lines) + "\n"

    lines.append(f"Update plan: {git_plan.note or git_plan.action}")
    if report.mirror_home:
        lines.append(f"Backup: required before real update ({report.mirror_home / 'backups'})")
    else:
        lines.append("Backup: required before real update")
    lines.append("Validation after update:")
    lines.append('  - uv run pytest tests/unit/ tests/integration/ -m "not live"')
    lines.append("  - uv run ruff check src/ tests/")
    lines.append("  - uv run ruff format --check src/ tests/")
    lines.append("Note: dry-run does not fetch, pull, back up, migrate, or modify files.")
    lines.append("")
    lines.append("Dry-run result: ready")
    return "\n".join(lines) + "\n"


def render_runtime_status(report: RuntimeStatusReport) -> str:
    lines: list[str] = []
    lines.append("Mirror runtime status")
    lines.append("")
    lines.append(f"Version: {report.version}")
    lines.append(f"Repository: {report.git.repository if report.git.repository else 'unknown'}")
    lines.append(f"Git branch: {report.git.branch or 'unknown'}")
    lines.append(f"Git commit: {report.git.commit or 'unknown'}")
    lines.append(f"Git dirty: {_yes_no(report.git.dirty)}")
    if report.git.error:
        lines.append(f"Git status note: {report.git.error}")
    lines.append(f"Mirror home: {report.mirror_home if report.mirror_home else 'not configured'}")
    if report.mirror_home_error:
        lines.append(f"Mirror home note: {report.mirror_home_error}")
    lines.append(f"Database: {report.db_path if report.db_path else 'unknown'}")
    lines.append(f"Database exists: {_yes_no(report.db_exists)}")
    lines.append(_render_core_migrations(report.core_migrations))
    if report.extensions:
        lines.append(
            f"Installed extensions: {len(report.extensions)} ({', '.join(report.extensions)})"
        )
    else:
        lines.append("Installed extensions: 0")
    lines.extend(_render_extension_health(report.extension_health))
    lines.append(f"Python: {report.python_version}")
    lines.append(f"MEMORY_ENV: {report.memory_env}")
    lines.append("")
    lines.append(f"Status: {report.status}")
    return "\n".join(lines) + "\n"


def cmd_runtime(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Inspect Mirror runtime state")
    subparsers = parser.add_subparsers(dest="command", required=True)
    status_parser = subparsers.add_parser("status", help="Inspect runtime status")
    status_parser.add_argument("--mirror-home", dest="mirror_home")
    diagnose_parser = subparsers.add_parser("diagnose", help="Diagnose runtime drift")
    diagnose_parser.add_argument("--mirror-home", dest="mirror_home")
    update_parser = subparsers.add_parser("update", help="Plan a runtime update")
    update_parser.add_argument("--dry-run", action="store_true", dest="dry_run")
    update_parser.add_argument("--mirror-home", dest="mirror_home")
    backup_parser = subparsers.add_parser("backup", help="Create or verify a runtime backup")
    backup_parser.add_argument("--mirror-home", dest="mirror_home")
    backup_parser.add_argument("--verify", dest="verify")
    args = parser.parse_args(argv)

    if args.command == "status":
        report = build_runtime_status(mirror_home_arg=args.mirror_home)
        sys.stdout.write(render_runtime_status(report))
        return 0 if report.status == "ready" else 1

    if args.command == "diagnose":
        report = build_runtime_status(mirror_home_arg=args.mirror_home)
        entries = inspect_git_worktree(report.git.repository)
        findings = diagnose_runtime(report, entries)
        sys.stdout.write(render_runtime_diagnosis(findings))
        return 0 if not findings else 1

    if args.command == "update":
        if not args.dry_run:
            sys.stderr.write("runtime update currently supports --dry-run only\n")
            return 1
        dry_run = build_runtime_update_dry_run(mirror_home_arg=args.mirror_home)
        sys.stdout.write(render_runtime_update_dry_run(dry_run))
        return 0 if dry_run.ready else 1

    if args.command == "backup":
        if args.verify:
            verification = verify_backup_archive(Path(args.verify).expanduser())
            sys.stdout.write(render_backup_verification(verification))
            return 0 if verification.valid else 1
        try:
            mirror_home = (
                Path(args.mirror_home).expanduser() if args.mirror_home else resolve_mirror_home()
            )
        except ValueError as exc:
            sys.stderr.write(f"{exc}\n")
            return 1
        backup_path = create_backup(silent=True, mirror_home=mirror_home)
        if backup_path is None:
            sys.stderr.write(f"Database not found: {default_db_path_for_home(mirror_home)}\n")
            return 1
        verification = verify_backup_archive(backup_path)
        sys.stdout.write(
            render_runtime_backup_created(
                backup_path=backup_path, mirror_home=mirror_home, verification=verification
            )
        )
        return 0 if verification.valid else 1

    parser.print_help()
    return 1


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(cmd_runtime(sys.argv[1:] if argv is None else argv))
