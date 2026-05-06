from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from .workspace_models import (
    PlannedFileAction,
    WorkspaceGenerationPlan,
    WorkspacePlanEntry,
    WorkspaceProjectRecord,
)
from .workspace_reporting import write_workspace_generation_report

DEFAULT_INPUT_JSON = "artifacts/project_scan_report.json"
DEFAULT_REPORT_NAME = "workspace_launcher_generation_report.md"
DEFAULT_PROTECTED_WORKSPACE = "project-forge-command-center.code-workspace"
FORCED_SKIP_CATEGORIES = {"system_bound_project", "reconciliation_required"}
DEFAULT_ELIGIBLE_CATEGORIES = {"active_project", "operated_tool"}
DEFAULT_SKIPPED_CATEGORIES = {"archive", "lab", "unknown", "vendor_clone"}
DEFAULT_ELIGIBLE_ACTIONS = {"register_full", "workspace_only"}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def repository_artifacts_root() -> Path:
    return repository_root() / "artifacts"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-forge-workspace-generate",
        description="Dry-run-first workspace and launcher generator for approved Project Forge entries.",
    )
    parser.add_argument(
        "--input-json",
        default=DEFAULT_INPUT_JSON,
        help="Path to the project scan JSON input.",
    )
    parser.add_argument(
        "--artifacts-dir",
        default="artifacts",
        help="Artifacts directory inside this repository.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan changes and write only the artifact report. This is the default mode.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write workspace and launcher files after planning and backup validation.",
    )
    parser.add_argument(
        "--include-slug",
        action="append",
        default=[],
        help="Restrict generation to this slug. Repeat to include multiple slugs.",
    )
    parser.add_argument(
        "--exclude-slug",
        action="append",
        default=[],
        help="Exclude this slug from generation. Repeat to exclude multiple slugs.",
    )
    parser.add_argument(
        "--include-category",
        action="append",
        default=[],
        help="Explicitly include a category that is skipped by default.",
    )
    parser.add_argument(
        "--exclude-category",
        action="append",
        default=[],
        help="Explicitly exclude an additional category.",
    )
    parser.add_argument(
        "--include-archive",
        action="store_true",
        help="Convenience flag equivalent to --include-category archive.",
    )
    parser.add_argument(
        "--workspace-dir",
        default="~/.config/Code/User/workspaces",
        help="Directory for generated VS Code workspace files.",
    )
    parser.add_argument(
        "--launcher-dir",
        default="~/.local/bin",
        help="Directory for generated code-<slug> launcher scripts.",
    )
    parser.add_argument(
        "--report-name",
        default=DEFAULT_REPORT_NAME,
        help="Filename for the generation report written inside the artifacts directory.",
    )
    parser.add_argument(
        "--backup-suffix",
        default=None,
        help="Suffix appended to backups. Defaults to a timestamp.",
    )
    parser.add_argument(
        "--preserve-workspace",
        action="append",
        default=[],
        help="Workspace filename to preserve and never overwrite. Repeat to add more.",
    )
    return parser


def parse_mode(args: argparse.Namespace, parser: argparse.ArgumentParser) -> str:
    if args.apply and args.dry_run:
        parser.error("Use either --apply or --dry-run, not both.")
    if args.apply:
        return "apply"
    return "dry-run"


def normalize_report_name(report_name: str) -> str:
    candidate = Path(report_name)
    if candidate.name != report_name or report_name in {"", ".", ".."}:
        raise ValueError("report name must be a simple filename inside the artifacts directory")
    return report_name


def resolve_artifacts_dir(artifacts_dir: str | Path) -> Path:
    candidate = Path(artifacts_dir).expanduser()
    if not candidate.is_absolute():
        candidate = repository_root() / candidate
    candidate = candidate.resolve()
    artifacts_root = repository_artifacts_root().resolve()
    if candidate != artifacts_root and artifacts_root not in candidate.parents:
        raise ValueError("artifacts directory must stay inside this repository's artifacts directory")
    return candidate


def ensure_allowed_target(target_path: Path, base_dir: Path, expected_name: str) -> None:
    resolved_base = base_dir.expanduser().resolve()
    resolved_target = target_path.expanduser().resolve()
    if resolved_target.name != expected_name:
        raise ValueError(f"target name must be exactly {expected_name}")
    if resolved_target.parent != resolved_base:
        raise ValueError(f"target must be written directly inside {resolved_base}")


def build_backup_path(target_path: Path, backup_suffix: str) -> Path:
    return target_path.with_name(f"{target_path.name}.bak.{backup_suffix}")


def load_project_records(input_json_path: Path) -> list[WorkspaceProjectRecord]:
    payload = json.loads(input_json_path.read_text(encoding="utf-8"))
    projects = payload.get("projects")
    if not isinstance(projects, list):
        raise ValueError("input JSON must contain a top-level 'projects' list")

    records: list[WorkspaceProjectRecord] = []
    for project in projects:
        if not isinstance(project, dict):
            raise ValueError("project entries must be objects")
        slug = str(project.get("safe_slug", "")).strip()
        name = str(project.get("folder_name", "")).strip()
        local_path = str(project.get("path", "")).strip()
        category = str(project.get("recommended_category", "")).strip()
        registry_action = str(project.get("recommended_action", "")).strip()
        do_not_sync = bool(project.get("do_not_sync", False))
        safety_warnings_raw = project.get("safety_warnings", [])
        if not all([slug, name, local_path, category, registry_action]):
            raise ValueError("each project entry must include safe_slug, folder_name, path, recommended_category, and recommended_action")
        if not isinstance(safety_warnings_raw, list):
            raise ValueError("project safety_warnings must be a list when present")
        records.append(
            WorkspaceProjectRecord(
                slug=slug,
                name=name,
                local_path=local_path,
                category=category,
                registry_action=registry_action,
                do_not_sync=do_not_sync,
                safety_warnings=tuple(str(item) for item in safety_warnings_raw),
            )
        )
    return records


def collect_duplicate_slugs(records: list[WorkspaceProjectRecord]) -> set[str]:
    counts: dict[str, int] = {}
    for record in records:
        counts[record.slug] = counts.get(record.slug, 0) + 1
    return {slug for slug, count in counts.items() if count > 1}


def build_workspace_file_content(record: WorkspaceProjectRecord) -> str:
    payload = {
        "folders": [{"path": record.local_path}],
        "settings": {
            "project_forge.generated_by": "project-forge-workspace-generate",
            "project_forge.slug": record.slug,
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def build_launcher_file_content(workspace_path: Path) -> str:
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            f'exec code "{workspace_path}" "$@"',
            "",
        ]
    )


def determine_reasons(
    record: WorkspaceProjectRecord,
    include_slugs: set[str],
    exclude_slugs: set[str],
    include_categories: set[str],
    exclude_categories: set[str],
    duplicate_slugs: set[str],
    preserved_workspaces: set[str],
    workspace_filename: str,
) -> list[str]:
    reasons: list[str] = []

    if include_slugs and record.slug not in include_slugs:
        reasons.append("not_selected_by_include_slug")
    if record.slug in exclude_slugs:
        reasons.append("excluded_by_slug")
    if record.slug in duplicate_slugs:
        reasons.append("duplicate_slug_collision")
    if record.do_not_sync:
        reasons.append("do_not_sync=true")
    if record.category in FORCED_SKIP_CATEGORIES:
        reasons.append(f"classification={record.category}")
    if record.category in exclude_categories:
        reasons.append(f"excluded_category={record.category}")
    if workspace_filename in preserved_workspaces:
        reasons.append(f"preserved_workspace={workspace_filename}")
    if record.registry_action not in DEFAULT_ELIGIBLE_ACTIONS:
        reasons.append(f"registry_action={record.registry_action}")
    if "cerberus_special_case_candidate" in record.safety_warnings:
        reasons.append("safety_warning=cerberus_special_case_candidate")

    if record.category in FORCED_SKIP_CATEGORIES:
        return reasons

    explicitly_included = record.category in include_categories
    if record.category in DEFAULT_ELIGIBLE_CATEGORIES:
        return reasons
    if record.category == "archive":
        if not explicitly_included:
            reasons.append("classification=archive_not_explicitly_included")
        return reasons
    if record.category == "vendor_clone":
        if not explicitly_included:
            reasons.append("classification=vendor_clone_requires_explicit_include")
        return reasons
    if record.category == "lab":
        if not explicitly_included:
            reasons.append("classification=lab_requires_explicit_include")
        return reasons
    if record.category in DEFAULT_SKIPPED_CATEGORIES and not explicitly_included:
        reasons.append(f"classification={record.category}")
        return reasons
    if record.category not in DEFAULT_ELIGIBLE_CATEGORIES and not explicitly_included:
        reasons.append(f"classification={record.category}_not_eligible_by_default")
    return reasons


def build_generation_plan(
    *,
    records: list[WorkspaceProjectRecord],
    mode: str,
    input_json_path: Path,
    artifacts_dir: Path,
    report_name: str,
    workspace_dir: Path,
    launcher_dir: Path,
    include_slugs: set[str],
    exclude_slugs: set[str],
    include_categories: set[str],
    exclude_categories: set[str],
    preserved_workspaces: set[str],
    backup_suffix: str,
) -> WorkspaceGenerationPlan:
    normalized_report_name = normalize_report_name(report_name)
    report_path = artifacts_dir / normalized_report_name
    duplicate_slugs = collect_duplicate_slugs(records)

    entries: list[WorkspacePlanEntry] = []
    for record in records:
        workspace_path = workspace_dir.expanduser() / f"{record.slug}.code-workspace"
        launcher_path = launcher_dir.expanduser() / f"code-{record.slug}"
        reasons = determine_reasons(
            record,
            include_slugs,
            exclude_slugs,
            include_categories,
            exclude_categories,
            duplicate_slugs,
            preserved_workspaces,
            workspace_path.name,
        )
        eligible = not reasons
        entry = WorkspacePlanEntry(
            record=record,
            workspace_path=workspace_path,
            launcher_path=launcher_path,
            eligible=eligible,
            reasons=reasons,
        )
        if eligible:
            ensure_allowed_target(workspace_path, workspace_dir, f"{record.slug}.code-workspace")
            ensure_allowed_target(launcher_path, launcher_dir, f"code-{record.slug}")
            workspace_exists = workspace_path.exists()
            launcher_exists = launcher_path.exists()
            entry.file_actions = [
                PlannedFileAction(
                    kind="workspace",
                    target_path=workspace_path,
                    backup_path=build_backup_path(workspace_path, backup_suffix) if workspace_exists else None,
                    existed_before=workspace_exists,
                ),
                PlannedFileAction(
                    kind="launcher",
                    target_path=launcher_path,
                    backup_path=build_backup_path(launcher_path, backup_suffix) if launcher_exists else None,
                    existed_before=launcher_exists,
                ),
            ]
        entries.append(entry)

    return WorkspaceGenerationPlan(
        mode=mode,
        input_json_path=input_json_path,
        artifacts_dir=artifacts_dir,
        report_path=report_path,
        workspace_dir=workspace_dir.expanduser().resolve(),
        launcher_dir=launcher_dir.expanduser().resolve(),
        preserved_workspaces=tuple(sorted(preserved_workspaces)),
        entries=entries,
    )


def apply_generation_plan(plan: WorkspaceGenerationPlan) -> None:
    plan.artifacts_dir.mkdir(parents=True, exist_ok=True)
    plan.workspace_dir.mkdir(parents=True, exist_ok=True)
    plan.launcher_dir.mkdir(parents=True, exist_ok=True)

    for entry in plan.eligible_entries:
        for action in entry.file_actions:
            if action.backup_path is not None:
                action.backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(action.target_path, action.backup_path)
                action.created_backup = True

        entry.workspace_path.write_text(
            build_workspace_file_content(entry.record),
            encoding="utf-8",
        )
        entry.file_actions[0].wrote_file = True

        entry.launcher_path.write_text(
            build_launcher_file_content(entry.workspace_path),
            encoding="utf-8",
        )
        entry.launcher_path.chmod(0o755)
        entry.file_actions[1].wrote_file = True


def create_generation_plan_from_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> WorkspaceGenerationPlan:
    mode = parse_mode(args, parser)
    backup_suffix = args.backup_suffix or datetime.now().strftime("%Y%m%d-%H%M%S")
    artifacts_dir = resolve_artifacts_dir(args.artifacts_dir)
    input_json_path = Path(args.input_json).expanduser()
    if not input_json_path.is_absolute():
        input_json_path = repository_root() / input_json_path
    input_json_path = input_json_path.resolve()

    include_categories = set(args.include_category)
    if args.include_archive:
        include_categories.add("archive")
    preserved_workspaces = {DEFAULT_PROTECTED_WORKSPACE, *args.preserve_workspace}
    records = load_project_records(input_json_path)

    return build_generation_plan(
        records=records,
        mode=mode,
        input_json_path=input_json_path,
        artifacts_dir=artifacts_dir,
        report_name=args.report_name,
        workspace_dir=Path(args.workspace_dir),
        launcher_dir=Path(args.launcher_dir),
        include_slugs=set(args.include_slug),
        exclude_slugs=set(args.exclude_slug),
        include_categories=include_categories,
        exclude_categories=set(args.exclude_category),
        preserved_workspaces=preserved_workspaces,
        backup_suffix=backup_suffix,
    )


def format_console_summary(plan: WorkspaceGenerationPlan) -> str:
    return "\n".join(
        [
            f"Mode: {plan.mode}",
            f"Input: {plan.input_json_path}",
            f"Workspace dir: {plan.workspace_dir}",
            f"Launcher dir: {plan.launcher_dir}",
            f"Eligible projects: {len(plan.eligible_entries)}",
            f"Skipped projects: {len(plan.skipped_entries)}",
            f"Planned writes: {plan.planned_write_count}",
            f"Planned backups: {plan.planned_backup_count}",
            f"Report: {plan.report_path}",
        ]
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    plan = create_generation_plan_from_args(args, parser)

    plan.artifacts_dir.mkdir(parents=True, exist_ok=True)
    if plan.mode == "apply":
        apply_generation_plan(plan)
    write_workspace_generation_report(plan.report_path, plan)

    print(format_console_summary(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
