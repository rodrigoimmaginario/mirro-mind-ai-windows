"""Allowlisted operation catalog for the local web console."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from memory.cli.runtime import RuntimeStatusReport, build_runtime_status

ParameterType = Literal["string", "integer", "boolean", "choice"]
RiskLevel = Literal["read_only", "writes_backup", "writes_database", "external_llm"]
DryRunMode = Literal["unsupported", "supported", "required"]
ExecutionState = Literal["catalog_only", "future", "runnable"]


@dataclass(frozen=True)
class OperationParameter:
    """Declarative metadata for a safe operation parameter."""

    name: str
    label: str
    kind: ParameterType
    description: str
    required: bool = False
    default: str | int | bool | None = None
    choices: tuple[str, ...] = ()
    minimum: int | None = None
    maximum: int | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "name": self.name,
            "label": self.label,
            "kind": self.kind,
            "description": self.description,
            "required": self.required,
        }
        if self.default is not None:
            payload["default"] = self.default
        if self.choices:
            payload["choices"] = list(self.choices)
        if self.minimum is not None:
            payload["minimum"] = self.minimum
        if self.maximum is not None:
            payload["maximum"] = self.maximum
        return payload


@dataclass(frozen=True)
class WebOperation:
    """Server-owned definition for one allowlisted web operation."""

    id: str
    title: str
    description: str
    category: str
    risk_level: RiskLevel
    dry_run: DryRunMode
    execution: ExecutionState = "catalog_only"
    parameters: tuple[OperationParameter, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "riskLevel": self.risk_level,
            "dryRun": self.dry_run,
            "execution": self.execution,
            "parameters": [parameter.to_dict() for parameter in self.parameters],
        }


OPERATION_CATALOG: tuple[WebOperation, ...] = (
    WebOperation(
        id="runtime-health",
        title="Runtime health diagnosis",
        description="Inspect runtime version, database path, migration state, extension health, and configuration warnings without changing local state.",
        category="runtime",
        risk_level="read_only",
        dry_run="unsupported",
        execution="runnable",
    ),
    WebOperation(
        id="database-backup",
        title="Database backup",
        description="Create and optionally verify a local backup archive for the active Mirror database before risky maintenance.",
        category="safety",
        risk_level="writes_backup",
        dry_run="unsupported",
        execution="future",
        parameters=(
            OperationParameter(
                name="verify",
                label="Verify backup",
                kind="boolean",
                description="Verify the created archive after backup completes.",
                default=True,
            ),
        ),
    ),
    WebOperation(
        id="conversation-journey-repair",
        title="Conversation journey repair",
        description="Find conversations missing journey association and repair them only after an explicit preview.",
        category="conversations",
        risk_level="writes_database",
        dry_run="required",
        execution="future",
        parameters=(
            OperationParameter(
                name="limit",
                label="Maximum conversations",
                kind="integer",
                description="Maximum number of conversations to inspect or repair in one run.",
                default=50,
                minimum=1,
                maximum=500,
            ),
        ),
    ),
    WebOperation(
        id="conversation-logger-health",
        title="Conversation logger health",
        description="Check recent logger warnings and errors so silent persistence failures become visible without blocking runtime sessions.",
        category="conversations",
        risk_level="read_only",
        dry_run="unsupported",
        execution="future",
    ),
    WebOperation(
        id="batch-conversation-retitle",
        title="Batch conversation retitle",
        description="Suggest improved titles for older conversations using an LLM, with limits, preview, and approval before database writes.",
        category="conversations",
        risk_level="external_llm",
        dry_run="required",
        execution="future",
        parameters=(
            OperationParameter(
                name="limit",
                label="Maximum conversations",
                kind="integer",
                description="Maximum number of conversations to consider in one batch.",
                default=10,
                minimum=1,
                maximum=100,
            ),
            OperationParameter(
                name="journey",
                label="Journey filter",
                kind="string",
                description="Optional journey id or slug used to limit the batch.",
                required=False,
            ),
        ),
    ),
)


def operation_catalog() -> list[dict[str, object]]:
    """Return the serialized server-owned operation catalog."""

    return [operation.to_dict() for operation in OPERATION_CATALOG]


def run_operation(
    operation_id: str, *, mirror_home: Path | None = None, start: Path | None = None
) -> dict[str, object]:
    """Run one implemented allowlisted operation and return web-safe results."""

    operation = _operation_by_id(operation_id)
    if operation is None:
        raise ValueError(f"Unknown operation: {operation_id}")
    if operation.execution != "runnable":
        raise ValueError(f"Operation is not runnable yet: {operation_id}")
    if operation.id != "runtime-health":
        raise ValueError(f"Operation is not implemented yet: {operation_id}")

    report = build_runtime_status(start=start, mirror_home_arg=mirror_home)
    return {
        "operationId": operation.id,
        "status": "completed",
        "outcome": report.status,
        "summary": _runtime_health_summary(report),
        "result": _runtime_status_payload(report),
    }


def _operation_by_id(operation_id: str) -> WebOperation | None:
    return next(
        (operation for operation in OPERATION_CATALOG if operation.id == operation_id), None
    )


def _runtime_health_summary(report: RuntimeStatusReport) -> list[str]:
    summary = [f"Runtime status: {report.status}", f"Version: {report.version}"]
    if report.git.branch:
        summary.append(f"Git branch: {report.git.branch}")
    if report.mirror_home:
        summary.append(f"Mirror home: {report.mirror_home}")
    if report.mirror_home_error:
        summary.append(f"Mirror home note: {report.mirror_home_error}")
    if report.db_exists is False:
        summary.append("Database: missing")
    elif report.db_exists is True:
        summary.append("Database: present")
    return summary


def _runtime_status_payload(report: RuntimeStatusReport) -> dict[str, object]:
    return {
        "status": report.status,
        "version": report.version,
        "repository": _path_or_none(report.git.repository),
        "git": {
            "branch": report.git.branch,
            "commit": report.git.commit,
            "dirty": report.git.dirty,
            "error": report.git.error,
        },
        "mirrorHome": _path_or_none(report.mirror_home),
        "mirrorHomeError": report.mirror_home_error,
        "database": {
            "path": _path_or_none(report.db_path),
            "exists": report.db_exists,
        },
        "coreMigrations": {
            "ready": report.core_migrations.ready,
            "appliedCount": report.core_migrations.applied_count,
            "knownCount": report.core_migrations.known_count,
            "missing": list(report.core_migrations.missing),
            "unknown": list(report.core_migrations.unknown),
            "note": report.core_migrations.note,
        },
        "extensions": list(report.extensions),
        "extensionHealth": [
            {
                "extensionId": health.extension_id,
                "ready": health.ready,
                "note": health.note,
                "pendingMigrations": list(health.pending_migrations),
                "driftedMigrations": list(health.drifted_migrations),
                "unknownMigrations": list(health.unknown_migrations),
            }
            for health in report.extension_health
        ],
        "cloneRole": {
            "value": report.clone_role.value,
            "source": _path_or_none(report.clone_role.source),
            "note": report.clone_role.note,
        },
        "pythonVersion": report.python_version,
        "memoryEnv": report.memory_env,
        "updateChannel": {
            "value": report.update_channel.value,
            "source": _path_or_none(report.update_channel.source),
            "note": report.update_channel.note,
        },
    }


def _path_or_none(path: Path | None) -> str | None:
    return str(path) if path is not None else None
