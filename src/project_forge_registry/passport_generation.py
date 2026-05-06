from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from .passport_models import (
    PassportFileAction,
    PassportGenerationPlan,
    PassportPlanEntry,
    PassportProjectRecord,
)
from .passport_reporting import write_passport_generation_report
from .reporting import OBSIDIAN_PROJECT_ROOT, _write_yaml_lines

DEFAULT_INPUT_JSON = "artifacts/project_scan_report.json"
DEFAULT_REPORT_NAME = "project_passport_generation_report.md"
DEFAULT_PASSPORTS_DIRNAME = "project_passports"
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
        prog="project-forge-passport-generate",
        description="Dry-run-first project passport proposal generator.",
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
        help="Write passport proposal files inside artifacts/project_passports after planning.",
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
        "--report-name",
        default=DEFAULT_REPORT_NAME,
        help="Filename for the generation report written inside the artifacts directory.",
    )
    parser.add_argument(
        "--backup-suffix",
        default=None,
        help="Suffix appended to backups for existing proposal files. Defaults to a timestamp.",
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


def ensure_allowed_target(target_path: Path, passports_dir: Path, expected_name: str) -> None:
    resolved_base = passports_dir.expanduser().resolve()
    resolved_target = target_path.expanduser().resolve()
    if resolved_target.name != expected_name:
        raise ValueError(f"target name must be exactly {expected_name}")
    if resolved_target.parent != resolved_base:
        raise ValueError(f"target must be written directly inside {resolved_base}")


def build_backup_path(target_path: Path, backup_suffix: str) -> Path:
    return target_path.with_name(f"{target_path.name}.bak.{backup_suffix}")


def load_project_records(input_json_path: Path) -> list[PassportProjectRecord]:
    payload = json.loads(input_json_path.read_text(encoding="utf-8"))
    projects = payload.get("projects")
    if not isinstance(projects, list):
        raise ValueError("input JSON must contain a top-level 'projects' list")

    records: list[PassportProjectRecord] = []
    for project in projects:
        if not isinstance(project, dict):
            raise ValueError("project entries must be objects")

        required = {
            "safe_slug": "slug",
            "folder_name": "name",
            "path": "local_path",
            "recommended_category": "category",
            "recommended_status": "status",
            "recommended_action": "registry_action",
        }
        values: dict[str, str] = {}
        for source_key, label in required.items():
            raw_value = str(project.get(source_key, "")).strip()
            if not raw_value:
                raise ValueError(f"each project entry must include {source_key} for {label}")
            values[source_key] = raw_value

        safety_warnings_raw = project.get("safety_warnings", [])
        if not isinstance(safety_warnings_raw, list):
            raise ValueError("project safety_warnings must be a list when present")

        records.append(
            PassportProjectRecord(
                slug=values["safe_slug"],
                name=values["folder_name"],
                local_path=values["path"],
                category=values["recommended_category"],
                status=values["recommended_status"],
                registry_action=values["recommended_action"],
                canonical_path=str(project.get("canonical_path")).strip() if project.get("canonical_path") else None,
                has_git=bool(project.get("has_git", False)),
                do_not_move=bool(project.get("do_not_move", False)),
                do_not_delete=bool(project.get("do_not_delete", False)),
                do_not_sync=bool(project.get("do_not_sync", False)),
                exclude_from_bulk_sync=bool(project.get("exclude_from_bulk_sync", False)),
                obsidian_note_policy=str(project.get("obsidian_note_policy", "docs_only")).strip() or "docs_only",
                safety_warnings=tuple(str(item) for item in safety_warnings_raw),
            )
        )
    return records


def collect_duplicate_slugs(records: list[PassportProjectRecord]) -> set[str]:
    counts: dict[str, int] = {}
    for record in records:
        counts[record.slug] = counts.get(record.slug, 0) + 1
    return {slug for slug, count in counts.items() if count > 1}


def build_passport_payload(record: PassportProjectRecord) -> dict[str, object]:
    local_path = record.canonical_path or record.local_path
    warnings = list(record.safety_warnings)
    notes = [
        f"generated_from_registry_category={record.category}",
        f"generated_from_registry_action={record.registry_action}",
        f"obsidian_note_policy={record.obsidian_note_policy}",
    ]
    if record.exclude_from_bulk_sync:
        notes.append("exclude_from_bulk_sync=true")

    return {
        "project": {
            "slug": record.slug,
            "name": record.name,
            "category": record.category,
            "status": record.status,
            "registry_action": record.registry_action,
            "local_path": local_path,
            "created_by": "project-forge-registry",
            "schema_version": "0.1",
        },
        "paths": {
            "local": local_path,
            "workspace": f"/home/cole/.config/Code/User/workspaces/{record.slug}.code-workspace",
            "obsidian": f"{OBSIDIAN_PROJECT_ROOT}/{record.slug}",
        },
        "launch": {
            "command": f"code-{record.slug}",
        },
        "git": {
            "default_branch": "main" if record.has_git else None,
            "github": None,
            "codeberg": None,
            "mirror_mode": "disabled_for_now",
        },
        "sync": {
            "obsidian_to_repo": "export_only",
            "repo_to_obsidian": "docs_only",
            "allow_code_to_obsidian": False,
            "allow_secrets": False,
        },
        "visibility": {
            "github": "private",
            "codeberg": "private",
            "public_ready": False,
        },
        "automation": {
            "auto_doc_sync": False,
            "auto_git_sync": False,
            "require_safety_check_before_push": True,
        },
        "safety": {
            "warnings": warnings,
            "do_not_move": record.do_not_move,
            "do_not_delete": record.do_not_delete,
            "do_not_sync": record.do_not_sync,
            "notes": notes,
        },
    }


def render_passport_yaml(record: PassportProjectRecord) -> str:
    return "\n".join(_write_yaml_lines(build_passport_payload(record))) + "\n"


def determine_reasons(
    record: PassportProjectRecord,
    include_slugs: set[str],
    exclude_slugs: set[str],
    include_categories: set[str],
    exclude_categories: set[str],
    duplicate_slugs: set[str],
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
    if record.registry_action not in DEFAULT_ELIGIBLE_ACTIONS:
        reasons.append(f"registry_action={record.registry_action}")
    if "cerberus_special_case_candidate" in record.safety_warnings:
        reasons.append("safety_warning=cerberus_special_case_candidate")
    if record.slug == "cerberus" or "cerberus" in record.local_path.lower():
        reasons.append("cerberus_protected")

    if record.category in FORCED_SKIP_CATEGORIES:
        return reasons

    explicitly_included = record.category in include_categories
    if record.category in DEFAULT_ELIGIBLE_CATEGORIES:
        return reasons
    if record.category in DEFAULT_SKIPPED_CATEGORIES and not explicitly_included:
        reasons.append(f"classification={record.category}")
        return reasons
    if record.category not in DEFAULT_ELIGIBLE_CATEGORIES and not explicitly_included:
        reasons.append(f"classification={record.category}_not_eligible_by_default")
    return reasons


def build_generation_plan(
    *,
    records: list[PassportProjectRecord],
    mode: str,
    input_json_path: Path,
    artifacts_dir: Path,
    report_name: str,
    include_slugs: set[str],
    exclude_slugs: set[str],
    include_categories: set[str],
    exclude_categories: set[str],
    backup_suffix: str,
) -> PassportGenerationPlan:
    normalized_report_name = normalize_report_name(report_name)
    passports_dir = artifacts_dir / DEFAULT_PASSPORTS_DIRNAME
    report_path = artifacts_dir / normalized_report_name
    duplicate_slugs = collect_duplicate_slugs(records)

    entries: list[PassportPlanEntry] = []
    for record in records:
        proposal_path = passports_dir / f"{record.slug}.project.yml"
        reasons = determine_reasons(
            record,
            include_slugs,
            exclude_slugs,
            include_categories,
            exclude_categories,
            duplicate_slugs,
        )
        eligible = not reasons
        entry = PassportPlanEntry(
            record=record,
            proposal_path=proposal_path,
            eligible=eligible,
            reasons=reasons,
        )
        if eligible:
            ensure_allowed_target(proposal_path, passports_dir, f"{record.slug}.project.yml")
            existed_before = proposal_path.exists()
            entry.file_action = PassportFileAction(
                target_path=proposal_path,
                backup_path=build_backup_path(proposal_path, backup_suffix) if existed_before else None,
                existed_before=existed_before,
            )
        entries.append(entry)

    return PassportGenerationPlan(
        mode=mode,
        input_json_path=input_json_path,
        artifacts_dir=artifacts_dir,
        passports_dir=passports_dir.resolve(),
        report_path=report_path,
        entries=entries,
    )


def apply_generation_plan(plan: PassportGenerationPlan) -> None:
    plan.artifacts_dir.mkdir(parents=True, exist_ok=True)
    plan.passports_dir.mkdir(parents=True, exist_ok=True)

    for entry in plan.eligible_entries:
        if entry.file_action is None:
            continue
        if entry.file_action.backup_path is not None:
            entry.file_action.backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(entry.file_action.target_path, entry.file_action.backup_path)
            entry.file_action.created_backup = True

        entry.file_action.target_path.write_text(
            render_passport_yaml(entry.record),
            encoding="utf-8",
        )
        entry.file_action.wrote_file = True


def create_generation_plan_from_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> PassportGenerationPlan:
    mode = parse_mode(args, parser)
    backup_suffix = args.backup_suffix or datetime.now().strftime("%Y%m%d-%H%M%S")
    artifacts_dir = resolve_artifacts_dir(args.artifacts_dir)
    input_json_path = Path(args.input_json).expanduser()
    if not input_json_path.is_absolute():
        input_json_path = repository_root() / input_json_path
    input_json_path = input_json_path.resolve()

    records = load_project_records(input_json_path)
    return build_generation_plan(
        records=records,
        mode=mode,
        input_json_path=input_json_path,
        artifacts_dir=artifacts_dir,
        report_name=args.report_name,
        include_slugs=set(args.include_slug),
        exclude_slugs=set(args.exclude_slug),
        include_categories=set(args.include_category),
        exclude_categories=set(args.exclude_category),
        backup_suffix=backup_suffix,
    )


def format_console_summary(plan: PassportGenerationPlan) -> str:
    return "\n".join(
        [
            f"Mode: {plan.mode}",
            f"Input: {plan.input_json_path}",
            f"Artifacts dir: {plan.artifacts_dir}",
            f"Passport proposal dir: {plan.passports_dir}",
            f"Eligible projects: {len(plan.eligible_entries)}",
            f"Skipped projects: {len(plan.skipped_entries)}",
            f"Planned proposal writes: {plan.planned_write_count}",
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
    write_passport_generation_report(plan.report_path, plan)

    print(format_console_summary(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
