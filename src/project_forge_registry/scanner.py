from __future__ import annotations

import re
from pathlib import Path

from .models import ProjectScanResult
from .path_policy import is_protected_filesystem_path

README_NAMES = {"README", "README.md", "README.txt", "readme.md"}
ENV_FILE_PREFIXES = (".env",)
DB_SUFFIXES = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".db3",
    ".duckdb",
}


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "project"


def first_level_directories(root: Path) -> list[Path]:
    if is_protected_filesystem_path(root):
        return []
    if not root.exists() or not root.is_dir():
        return []
    return sorted(
        path
        for path in root.iterdir()
        if not is_protected_filesystem_path(path) and path.is_dir()
    )


def detect_stack(project_dir: Path) -> list[str]:
    stack: list[str] = []
    if (project_dir / "package.json").exists():
        stack.append("node")
    if (project_dir / "pyproject.toml").exists():
        stack.append("python")
    if (project_dir / "flake.nix").exists():
        stack.append("nix")
    if any(
        (project_dir / name).exists()
        for name in (
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml",
        )
    ):
        stack.append("docker")
    if not stack:
        stack.append("unknown")
    return stack


def detect_category(
    project_dir: Path,
    has_git: bool,
    has_node_modules: bool,
    has_readme: bool,
) -> str:
    name = project_dir.name.lower()
    path_text = str(project_dir).lower()

    if any(token in name for token in ("archive", "old", "backup", "deprecated")):
        return "archive"
    if any(token in name for token in ("vendor", "fork", "mirror", "clone")):
        return "vendor_clone"
    if any(token in path_text for token in ("/lab", "/labs")) or any(
        token in name for token in ("lab", "sandbox", "scratch", "playground")
    ):
        return "lab"
    if has_git and (has_readme or (project_dir / ".project").exists()):
        return "project_candidate"
    if has_node_modules and not has_git:
        return "operated_tool"
    return "unknown"


def detect_action(
    category: str,
    has_git: bool,
    has_project_yml: bool,
    has_code_workspace: bool,
    warnings: list[str],
) -> str:
    if category == "archive":
        return "ignore"
    if category == "system_bound_project":
        return "document_only_for_now"
    if category == "reconciliation_required":
        return "compare_only"
    if warnings:
        return "review_required"
    if category == "vendor_clone":
        return "workspace_only"
    if category == "operated_tool":
        return "workspace_only"
    if category == "lab":
        return "obsidian_notes_only"
    if category == "unknown":
        return "review_required"
    if has_git or has_project_yml or has_code_workspace:
        return "register_full"
    return "review_required"


def collect_safety_warnings(
    project_dir: Path,
    has_env_files: bool,
    has_sqlite_or_db_files: bool,
    has_node_modules: bool,
    has_git: bool,
) -> list[str]:
    """Return content- and state-based warnings without project-name exceptions.

    Project identity is not a security boundary. Cerberus-labeled repositories
    receive the same inspection and lifecycle treatment as every other personal
    project. Real env files, databases, dependency trees, and missing Git state
    still receive ordinary review warnings.
    """

    warnings: list[str] = []
    name = project_dir.name.lower()

    if has_env_files:
        warnings.append("contains_env_files")
    if has_sqlite_or_db_files:
        warnings.append("contains_database_files")
    if has_node_modules:
        warnings.append("contains_node_modules")
    if not has_git:
        warnings.append("not_a_git_repo")
    if any(token in name for token in ("backup", "archive", "copy", "old")):
        warnings.append("name_suggests_archive_or_duplicate")
    return warnings


def detect_status(category: str, warnings: list[str]) -> str:
    if category == "system_bound_project":
        return "active_special_case"
    if category == "reconciliation_required":
        return "reconciliation_required"
    if warnings:
        return "review"
    if category == "archive":
        return "archived_candidate"
    return "review"


def scan_project_dir(project_dir: Path) -> ProjectScanResult:
    if is_protected_filesystem_path(project_dir):
        raise ValueError(f"protected filesystem path is excluded: {project_dir}")

    entries = list(project_dir.iterdir())
    names = {entry.name for entry in entries}

    has_git = (project_dir / ".git").exists()
    has_readme = any(name in README_NAMES for name in names)
    has_code_workspace = any(entry.suffix == ".code-workspace" for entry in entries)
    has_project_yml = (
        (project_dir / ".project" / "project.yml").exists()
        or (project_dir / "project.yml").exists()
    )
    has_package_json = (project_dir / "package.json").exists()
    has_pyproject_toml = (project_dir / "pyproject.toml").exists()
    has_flake_nix = (project_dir / "flake.nix").exists()
    has_docker_compose = any(
        (project_dir / name).exists()
        for name in (
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml",
        )
    )
    has_env_files = any(name.startswith(ENV_FILE_PREFIXES) for name in names)
    has_sqlite_or_db_files = any(
        entry.is_file() and entry.suffix.lower() in DB_SUFFIXES for entry in entries
    )
    has_node_modules = (project_dir / "node_modules").exists()

    likely_stack = detect_stack(project_dir)
    safety_warnings = collect_safety_warnings(
        project_dir=project_dir,
        has_env_files=has_env_files,
        has_sqlite_or_db_files=has_sqlite_or_db_files,
        has_node_modules=has_node_modules,
        has_git=has_git,
    )
    recommended_category = detect_category(
        project_dir=project_dir,
        has_git=has_git,
        has_node_modules=has_node_modules,
        has_readme=has_readme,
    )
    recommended_status = detect_status(recommended_category, safety_warnings)
    recommended_action = detect_action(
        category=recommended_category,
        has_git=has_git,
        has_project_yml=has_project_yml,
        has_code_workspace=has_code_workspace,
        warnings=safety_warnings,
    )

    return ProjectScanResult(
        path=str(project_dir),
        folder_name=project_dir.name,
        safe_slug=slugify(project_dir.name),
        has_git=has_git,
        has_readme=has_readme,
        has_code_workspace=has_code_workspace,
        has_project_yml=has_project_yml,
        has_package_json=has_package_json,
        has_pyproject_toml=has_pyproject_toml,
        has_flake_nix=has_flake_nix,
        has_docker_compose=has_docker_compose,
        has_env_files=has_env_files,
        has_sqlite_or_db_files=has_sqlite_or_db_files,
        has_node_modules=has_node_modules,
        likely_stack=likely_stack,
        recommended_status=recommended_status,
        recommended_category=recommended_category,
        recommended_action=recommended_action,
        canonical_path=None,
        do_not_move=False,
        do_not_delete=False,
        do_not_sync=False,
        exclude_from_bulk_sync=False,
        obsidian_note_policy="docs_only",
        safety_warnings=safety_warnings,
    )


def scan_roots(roots: list[Path]) -> list[ProjectScanResult]:
    results: list[ProjectScanResult] = []
    seen_paths: set[str] = set()
    for root in roots:
        if is_protected_filesystem_path(root):
            continue
        for project_dir in first_level_directories(root):
            if is_protected_filesystem_path(project_dir):
                continue
            try:
                identity = str(project_dir.resolve())
            except OSError:
                identity = str(project_dir)
            if identity in seen_paths:
                continue
            seen_paths.add(identity)
            results.append(scan_project_dir(project_dir))
    return sorted(results, key=lambda item: item.path.lower())
