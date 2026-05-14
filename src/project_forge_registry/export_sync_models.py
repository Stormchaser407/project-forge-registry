from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ExportSyncPassportRecord:
    slug: str
    name: str
    category: str
    status: str
    registry_action: str
    local_path: str
    allow_code_to_obsidian: bool
    allow_secrets: bool
    do_not_sync: bool
    warnings: tuple[str, ...]
    passport_path: Path


@dataclass(slots=True)
class ExportSyncFileAction:
    source_path: Path
    source_relative_export_path: Path
    destination_path: Path
    backup_path: Path | None
    existed_before: bool
    copied: bool = False
    backup_created: bool = False


@dataclass(slots=True)
class ExportSyncExcludedFile:
    source_relative_export_path: str
    reason: str


@dataclass(slots=True)
class ExportSyncPlanEntry:
    record: ExportSyncPassportRecord
    source_export_root: Path
    source_docs_root: Path
    destination_docs_root: Path
    eligible: bool
    reasons: list[str] = field(default_factory=list)
    file_actions: list[ExportSyncFileAction] = field(default_factory=list)
    excluded_files: list[ExportSyncExcludedFile] = field(default_factory=list)

    @property
    def planned_file_count(self) -> int:
        return len(self.file_actions)

    @property
    def planned_backup_count(self) -> int:
        return sum(1 for action in self.file_actions if action.backup_path is not None)


@dataclass(slots=True)
class ExportSyncPlan:
    mode: str
    slug: str
    passport_dir: Path
    vault_project_root: Path
    repo_root_override: Path | None
    report_path: Path
    entry: ExportSyncPlanEntry

    @property
    def files_planned(self) -> int:
        return self.entry.planned_file_count

    @property
    def backups_planned(self) -> int:
        return self.entry.planned_backup_count

    @property
    def files_copied(self) -> int:
        return sum(1 for action in self.entry.file_actions if action.copied)

    @property
    def backups_created(self) -> int:
        return sum(1 for action in self.entry.file_actions if action.backup_created)
