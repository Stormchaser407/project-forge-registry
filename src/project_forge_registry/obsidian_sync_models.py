from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ObsidianSyncPassportRecord:
    slug: str
    name: str
    local_path: str
    category: str
    status: str
    obsidian_path: str
    allow_code_to_obsidian: bool
    allow_secrets: bool
    do_not_sync: bool
    warnings: tuple[str, ...]
    passport_path: Path


@dataclass(slots=True)
class ObsidianSyncFileAction:
    source_path: Path
    destination_path: Path
    backup_path: Path | None
    existed_before: bool
    copied: bool = False
    backup_created: bool = False


@dataclass(slots=True)
class ObsidianSyncExcludedFile:
    source_path: Path
    reason: str


@dataclass(slots=True)
class ObsidianSyncPlanEntry:
    record: ObsidianSyncPassportRecord
    source_mirror_dir: Path
    destination_vault_dir: Path
    eligible: bool
    reasons: list[str] = field(default_factory=list)
    file_actions: list[ObsidianSyncFileAction] = field(default_factory=list)
    excluded_files: list[ObsidianSyncExcludedFile] = field(default_factory=list)

    @property
    def planned_file_count(self) -> int:
        return len(self.file_actions)

    @property
    def planned_backup_count(self) -> int:
        return sum(1 for action in self.file_actions if action.backup_path is not None)


@dataclass(slots=True)
class ObsidianSyncPlan:
    mode: str
    slug: str
    passport_dir: Path
    mirror_dir: Path
    source_mirror_path: Path
    vault_project_root: Path
    destination_vault_path: Path
    report_path: Path
    entry: ObsidianSyncPlanEntry

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
