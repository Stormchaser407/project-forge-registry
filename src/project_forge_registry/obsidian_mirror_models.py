from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ObsidianMirrorPassportRecord:
    slug: str
    name: str
    category: str
    status: str
    local_path: str
    workspace_path: str
    obsidian_path: str
    launcher_command: str
    obsidian_to_repo: str
    repo_to_obsidian: str
    allow_code_to_obsidian: bool
    allow_secrets: bool
    do_not_move: bool
    do_not_delete: bool
    do_not_sync: bool
    warnings: tuple[str, ...]
    passport_path: Path


@dataclass(slots=True)
class ObsidianMirrorFileAction:
    target_path: Path
    backup_path: Path | None = None
    existed_before: bool = False
    wrote_file: bool = False
    created_backup: bool = False


@dataclass(slots=True)
class ObsidianMirrorPlanEntry:
    record: ObsidianMirrorPassportRecord
    mirror_dir: Path
    eligible: bool
    reasons: list[str] = field(default_factory=list)
    file_actions: list[ObsidianMirrorFileAction] = field(default_factory=list)

    @property
    def planned_write_count(self) -> int:
        return len(self.file_actions)

    @property
    def planned_backup_count(self) -> int:
        return sum(1 for action in self.file_actions if action.backup_path is not None)


@dataclass(slots=True)
class ObsidianMirrorGenerationPlan:
    mode: str
    passport_dir: Path
    artifacts_dir: Path
    mirrors_dir: Path
    report_path: Path
    entries: list[ObsidianMirrorPlanEntry]

    @property
    def eligible_entries(self) -> list[ObsidianMirrorPlanEntry]:
        return [entry for entry in self.entries if entry.eligible]

    @property
    def skipped_entries(self) -> list[ObsidianMirrorPlanEntry]:
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
