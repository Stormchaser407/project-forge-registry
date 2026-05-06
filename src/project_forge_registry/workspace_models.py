from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class WorkspaceProjectRecord:
    slug: str
    name: str
    local_path: str
    category: str
    registry_action: str
    do_not_sync: bool
    safety_warnings: tuple[str, ...]


@dataclass(slots=True)
class PlannedFileAction:
    kind: str
    target_path: Path
    backup_path: Path | None = None
    existed_before: bool = False
    wrote_file: bool = False
    created_backup: bool = False


@dataclass(slots=True)
class WorkspacePlanEntry:
    record: WorkspaceProjectRecord
    workspace_path: Path
    launcher_path: Path
    eligible: bool
    reasons: list[str] = field(default_factory=list)
    file_actions: list[PlannedFileAction] = field(default_factory=list)

    @property
    def planned_write_count(self) -> int:
        return len(self.file_actions)

    @property
    def planned_backup_count(self) -> int:
        return sum(1 for action in self.file_actions if action.backup_path is not None)


@dataclass(slots=True)
class WorkspaceGenerationPlan:
    mode: str
    input_json_path: Path
    artifacts_dir: Path
    report_path: Path
    workspace_dir: Path
    launcher_dir: Path
    preserved_workspaces: tuple[str, ...]
    entries: list[WorkspacePlanEntry]

    @property
    def eligible_entries(self) -> list[WorkspacePlanEntry]:
        return [entry for entry in self.entries if entry.eligible]

    @property
    def skipped_entries(self) -> list[WorkspacePlanEntry]:
        return [entry for entry in self.entries if not entry.eligible]

    @property
    def planned_write_count(self) -> int:
        return sum(entry.planned_write_count for entry in self.eligible_entries)

    @property
    def planned_backup_count(self) -> int:
        return sum(entry.planned_backup_count for entry in self.eligible_entries)

    @property
    def written_count(self) -> int:
        return sum(
            1
            for entry in self.eligible_entries
            for action in entry.file_actions
            if action.wrote_file
        )

    @property
    def backup_count(self) -> int:
        return sum(
            1
            for entry in self.eligible_entries
            for action in entry.file_actions
            if action.created_backup
        )
