from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class PassportProjectRecord:
    slug: str
    name: str
    local_path: str
    category: str
    status: str
    registry_action: str
    canonical_path: str | None
    has_git: bool
    do_not_move: bool
    do_not_delete: bool
    do_not_sync: bool
    exclude_from_bulk_sync: bool
    obsidian_note_policy: str
    safety_warnings: tuple[str, ...]


@dataclass(slots=True)
class PassportFileAction:
    target_path: Path
    backup_path: Path | None = None
    existed_before: bool = False
    wrote_file: bool = False
    created_backup: bool = False


@dataclass(slots=True)
class PassportPlanEntry:
    record: PassportProjectRecord
    proposal_path: Path
    eligible: bool
    reasons: list[str] = field(default_factory=list)
    file_action: PassportFileAction | None = None

    @property
    def planned_write_count(self) -> int:
        return 1 if self.file_action is not None else 0

    @property
    def planned_backup_count(self) -> int:
        if self.file_action is None or self.file_action.backup_path is None:
            return 0
        return 1


@dataclass(slots=True)
class PassportGenerationPlan:
    mode: str
    input_json_path: Path
    artifacts_dir: Path
    passports_dir: Path
    report_path: Path
    entries: list[PassportPlanEntry]

    @property
    def eligible_entries(self) -> list[PassportPlanEntry]:
        return [entry for entry in self.entries if entry.eligible]

    @property
    def skipped_entries(self) -> list[PassportPlanEntry]:
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
            if entry.file_action is not None and entry.file_action.wrote_file
        )

    @property
    def backup_count(self) -> int:
        return sum(
            1
            for entry in self.eligible_entries
            if entry.file_action is not None and entry.file_action.created_backup
        )
