from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class ProjectScanResult:
    path: str
    folder_name: str
    safe_slug: str
    has_git: bool
    has_readme: bool
    has_code_workspace: bool
    has_project_yml: bool
    has_package_json: bool
    has_pyproject_toml: bool
    has_flake_nix: bool
    has_docker_compose: bool
    has_env_files: bool
    has_sqlite_or_db_files: bool
    has_node_modules: bool
    likely_stack: list[str]
    recommended_status: str
    recommended_category: str
    recommended_action: str
    canonical_path: str | None
    do_not_move: bool
    do_not_delete: bool
    exclude_from_bulk_sync: bool
    obsidian_note_policy: str
    safety_warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
