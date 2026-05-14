from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class RemotePassportRecord:
    slug: str
    name: str
    category: str
    status: str
    registry_action: str
    local_path: Path
    default_branch: str
    visibility_github: str
    visibility_codeberg: str
    allow_code_to_obsidian: bool
    allow_secrets: bool
    do_not_sync: bool
    passport_path: Path


@dataclass(slots=True)
class RemotePolicyDefaults:
    github_remote_name: str = "origin"
    codeberg_remote_name: str = "codeberg"
    github_visibility: str = "private"
    codeberg_visibility: str = "private"
    default_branch: str = "main"
    push_behavior: str = "manual_only"


@dataclass(slots=True)
class RemotePlan:
    mode: str
    slug: str
    passport_dir: Path
    report_path: Path
    record: RemotePassportRecord
    defaults: RemotePolicyDefaults
    eligible: bool
    policy_status: str
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RemoteState:
    inside_git_repo: bool
    current_branch: str | None
    remotes: list[tuple[str, str, str]]
    clean_working_tree: bool | None
    clean_working_tree_lines: list[str] = field(default_factory=list)


@dataclass(slots=True)
class VerificationCheck:
    name: str
    required: bool
    passed: bool
    detail: str


@dataclass(slots=True)
class RemoteVerify:
    mode: str
    slug: str
    passport_dir: Path
    report_path: Path
    record: RemotePassportRecord
    defaults: RemotePolicyDefaults
    eligible: bool
    policy_status: str
    reasons: list[str]
    remote_state: RemoteState
    checks: list[VerificationCheck]
