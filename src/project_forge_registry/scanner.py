from __future__ import annotations

import re
from pathlib import Path

from .models import ProjectScanResult

README_NAMES = {"README", "README.md", "README.txt", "readme.md"}
ENV_FILE_PREFIXES = (".env",)
DB_SUFFIXES = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".db3",
    ".duckdb",
}

PATH_CLASSIFICATION_OVERRIDES = {
    "/home/cole/cerberus": {
        "recommended_category": "system_bound_project",
        "recommended_status": "active_special_case",
        "recommended_action": "document_only_for_now",
        "canonical_path": "/home/cole/cerberus",
        "do_not_move": True,
        "do_not_delete": False,
        "do_not_sync": True,
        "exclude_from_bulk_sync": True,
        "obsidian_note_policy": "high_level_notes_only",
        "extra_warnings": [
            "system_bound_path",
            "do_not_sync",
            "no_bulk_sync_automation",
            "obsidian_high_level_notes_only",
        ],
    },
    "/mnt/storage/Cole/cerberus": {
        "recommended_category": "reconciliation_required",
        "recommended_status": "old_copy_with_possible_operational_material",
        "recommended_action": "compare_only",
        "canonical_path": "/home/cole/cerberus",
        "do_not_move": False,
        "do_not_delete": True,
        "do_not_sync": True,
        "exclude_from_bulk_sync": True,
        "obsidian_note_policy": "reconciliation_note_only",
        "extra_warnings": [
            "reconciliation_required",
            "contains_possible_operational_material",
            "do_not_delete_automatically",
            "do_not_sync",
        ],
    },
}


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "project"


def is_cerberus_candidate(project_dir: Path) -> bool:
    slug = slugify(project_dir.name)
    return slug == "cerberus" or slug.startswith("cerberus_") or "_cerberus" in slug


def first_level_directories(root: Path) -> list[Path]:
    if not root.exists() or not root.is_dir():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir())


def detect_stack(project_dir: Path) -> list[str]:
    stack: list[str] = []
    if (project_dir / "package.json").exists():
        stack.append("node")
    if (project_dir / "pyproject.toml").exists():
        stack.append("python")
    if (project_dir / "flake.nix").exists():
        stack.append("nix")
    if any((project_dir / name).exists() for name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")):
        stack.append("docker")
    if not stack:
        stack.append("unknown")
    return stack


def detect_category(project_dir: Path, has_git: bool, has_node_modules: bool, has_readme: bool) -> str:
    name = project_dir.name.lower()
    path_text = str(project_dir).lower()

    if any(token in name for token in ("archive", "old", "backup", "deprecated")):
        return "archive"
    if any(token in name for token in ("vendor", "fork", "mirror", "clone")):
        return "vendor_clone"
    if any(token in path_text for token in ("/lab", "/labs")) or any(token in name for token in ("lab", "sandbox", "scratch", "playground")):
        return "lab"
    if has_git and (has_readme or (project_dir / ".project").exists()):
        return "active_project"
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
    if is_cerberus_candidate(project_dir):
        warnings.append("cerberus_special_case_candidate")
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


def apply_path_override(project_dir: Path, result: dict[str, object], warnings: list[str]) -> None:
    try:
        resolved = str(project_dir.resolve())
    except OSError:
        resolved = str(project_dir)

    override = PATH_CLASSIFICATION_OVERRIDES.get(resolved)
    if not override:
        return

    result["recommended_category"] = override["recommended_category"]
    result["recommended_status"] = override["recommended_status"]
    result["recommended_action"] = override["recommended_action"]
    result["canonical_path"] = override["canonical_path"]
    result["do_not_move"] = override["do_not_move"]
    result["do_not_delete"] = override["do_not_delete"]
    result["do_not_sync"] = override["do_not_sync"]
    result["exclude_from_bulk_sync"] = override["exclude_from_bulk_sync"]
    result["obsidian_note_policy"] = override["obsidian_note_policy"]

    for warning in override["extra_warnings"]:
        if warning not in warnings:
            warnings.append(warning)


def apply_special_case_rules(project_dir: Path, result: dict[str, object], warnings: list[str]) -> None:
    try:
        resolved = str(project_dir.resolve())
    except OSError:
        resolved = str(project_dir)

    if resolved in PATH_CLASSIFICATION_OVERRIDES:
        return
    if not is_cerberus_candidate(project_dir):
        return

    result["do_not_sync"] = True
    result["exclude_from_bulk_sync"] = True
    if "do_not_sync" not in warnings:
        warnings.append("do_not_sync")

    if slugify(project_dir.name) == "cerberus":
        result["recommended_category"] = "reconciliation_required"
        result["recommended_status"] = "review"
        result["recommended_action"] = "review_required"
        if "cerberus_name_requires_manual_reconciliation_review" not in warnings:
            warnings.append("cerberus_name_requires_manual_reconciliation_review")
        return

    result["recommended_category"] = "unknown"
    result["recommended_status"] = "review"
    result["recommended_action"] = "review_required"
    if "cerberus_related_project_requires_manual_review" not in warnings:
        warnings.append("cerberus_related_project_requires_manual_review")


def scan_project_dir(project_dir: Path) -> ProjectScanResult:
    entries = list(project_dir.iterdir())
    names = {entry.name for entry in entries}

    has_git = (project_dir / ".git").exists()
    has_readme = any(name in README_NAMES for name in names)
    has_code_workspace = any(entry.suffix == ".code-workspace" for entry in entries)
    has_project_yml = (project_dir / ".project" / "project.yml").exists() or (project_dir / "project.yml").exists()
    has_package_json = (project_dir / "package.json").exists()
    has_pyproject_toml = (project_dir / "pyproject.toml").exists()
    has_flake_nix = (project_dir / "flake.nix").exists()
    has_docker_compose = any((project_dir / name).exists() for name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"))
    has_env_files = any(name.startswith(ENV_FILE_PREFIXES) for name in names)
    has_sqlite_or_db_files = any(entry.is_file() and entry.suffix.lower() in DB_SUFFIXES for entry in entries)
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
    canonical_path: str | None = None
    do_not_move = False
    do_not_delete = False
    do_not_sync = False
    exclude_from_bulk_sync = False
    obsidian_note_policy = "docs_only"

    result_data: dict[str, object] = {
        "recommended_category": recommended_category,
        "recommended_status": recommended_status,
        "recommended_action": recommended_action,
        "canonical_path": canonical_path,
        "do_not_move": do_not_move,
        "do_not_delete": do_not_delete,
        "do_not_sync": do_not_sync,
        "exclude_from_bulk_sync": exclude_from_bulk_sync,
        "obsidian_note_policy": obsidian_note_policy,
    }
    apply_path_override(project_dir, result_data, safety_warnings)
    apply_special_case_rules(project_dir, result_data, safety_warnings)

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
        recommended_status=str(result_data["recommended_status"]),
        recommended_category=str(result_data["recommended_category"]),
        recommended_action=str(result_data["recommended_action"]),
        canonical_path=result_data["canonical_path"] if isinstance(result_data["canonical_path"], str) else None,
        do_not_move=bool(result_data["do_not_move"]),
        do_not_delete=bool(result_data["do_not_delete"]),
        do_not_sync=bool(result_data["do_not_sync"]),
        exclude_from_bulk_sync=bool(result_data["exclude_from_bulk_sync"]),
        obsidian_note_policy=str(result_data["obsidian_note_policy"]),
        safety_warnings=safety_warnings,
    )


def scan_roots(roots: list[Path]) -> list[ProjectScanResult]:
    results: list[ProjectScanResult] = []
    seen_paths: set[str] = set()
    for root in roots:
        for project_dir in first_level_directories(root):
            try:
                identity = str(project_dir.resolve())
            except OSError:
                identity = str(project_dir)
            if identity in seen_paths:
                continue
            seen_paths.add(identity)
            results.append(scan_project_dir(project_dir))
    return sorted(results, key=lambda item: item.path.lower())
