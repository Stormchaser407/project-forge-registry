from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from .export_sync_models import (
    ExportSyncExcludedFile,
    ExportSyncFileAction,
    ExportSyncPassportRecord,
    ExportSyncPlan,
    ExportSyncPlanEntry,
)
from .export_sync_reporting import write_export_sync_report
from .obsidian_mirror_generation import parse_simple_yaml

DEFAULT_PASSPORT_DIR = "artifacts/project_passports"
DEFAULT_VAULT_PROJECT_ROOT = "/home/cole/main_vault/10 Projects"
DEFAULT_REPORT_NAME = "export_sync_report.md"
DEFAULT_ELIGIBLE_CATEGORIES = {"active_project", "operated_tool"}
FORCED_SKIP_REGISTRY_ACTIONS = {"review_required"}
EXCLUDED_DIR_NAMES = {".git", "node_modules", ".venv", "__pycache__"}
EXCLUDED_SUFFIXES = {
    ".py",
    ".js",
    ".ts",
    ".nix",
    ".json",
    ".yml",
    ".yaml",
    ".env",
    ".db",
    ".sqlite",
    ".log",
}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def repository_artifacts_root() -> Path:
    return repository_root() / "artifacts"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-forge-export-sync",
        description="Dry-run-first planner/reporter for controlled Obsidian _export to repo docs sync.",
    )
    parser.add_argument("--slug", required=True, help="Project slug to sync.")
    parser.add_argument(
        "--passport-dir",
        default=DEFAULT_PASSPORT_DIR,
        help="Directory containing passport proposal files.",
    )
    parser.add_argument(
        "--vault-project-root",
        default=DEFAULT_VAULT_PROJECT_ROOT,
        help="Root Obsidian Projects folder containing <slug>/_export paths.",
    )
    parser.add_argument(
        "--repo-root-override",
        default=None,
        help="Optional destination docs root override. Must remain within <local_path>/docs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan/report only. This is the default mode.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Copy approved markdown files from _export into destination docs root.",
    )
    parser.add_argument(
        "--include-file",
        action="append",
        default=[],
        help="Include this _export-relative file path. Repeat to include multiple files.",
    )
    parser.add_argument(
        "--exclude-file",
        action="append",
        default=[],
        help="Exclude this _export-relative file path. Repeat to exclude multiple files.",
    )
    parser.add_argument(
        "--report-name",
        default=DEFAULT_REPORT_NAME,
        help="Filename for the report written inside the artifacts directory.",
    )
    parser.add_argument(
        "--backup-suffix",
        default=None,
        help="Suffix appended to backups for destination files. Defaults to a timestamp.",
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


def resolve_repo_scoped_dir(raw_path: str | Path, description: str) -> Path:
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = repository_root() / candidate
    resolved = candidate.resolve()
    repo = repository_root().resolve()
    if resolved != repo and repo not in resolved.parents:
        raise ValueError(f"{description} must stay inside this repository")
    return resolved


def resolve_vault_project_root(raw_path: str | Path) -> Path:
    root = Path(raw_path).expanduser()
    if not root.is_absolute():
        raise ValueError("vault project root must be an absolute path")
    return root.resolve()


def ensure_path_within(base: Path, target: Path, description: str) -> None:
    resolved_base = base.expanduser().resolve()
    resolved_target = target.expanduser().resolve()
    if resolved_target != resolved_base and resolved_base not in resolved_target.parents:
        raise ValueError(f"{description} must stay inside {resolved_base}")


def parse_relative_export_path(raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        raise ValueError(f"relative export path must not be absolute: {raw_path}")

    normalized_parts: list[str] = []
    for part in candidate.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            raise ValueError(f"relative export path must not traverse parent directories: {raw_path}")
        normalized_parts.append(part)

    if not normalized_parts:
        raise ValueError(f"relative export path must not be empty: {raw_path}")
    return Path(*normalized_parts)


def build_backup_path(target_path: Path, backup_suffix: str) -> Path:
    return target_path.with_name(f"{target_path.name}.bak.{backup_suffix}")


def load_passport_record(passport_dir: Path, slug: str) -> ExportSyncPassportRecord:
    passport_path = passport_dir / f"{slug}.project.yml"
    if not passport_path.exists():
        raise ValueError(f"passport file not found for slug '{slug}': {passport_path}")

    payload = parse_simple_yaml(passport_path.read_text(encoding="utf-8"))
    project = payload.get("project")
    sync = payload.get("sync")
    safety = payload.get("safety")

    if not all(isinstance(section, dict) for section in (project, sync, safety)):
        raise ValueError(f"passport file is missing required sections: {passport_path}")

    record_slug = str(project.get("slug", "")).strip()
    if record_slug != slug:
        raise ValueError(f"passport slug mismatch: expected '{slug}', found '{record_slug}'")

    warnings = safety.get("warnings", [])
    if not isinstance(warnings, list):
        raise ValueError(f"passport warnings must be a list: {passport_path}")

    required_values = {
        "name": project.get("name"),
        "category": project.get("category"),
        "status": project.get("status"),
        "local_path": project.get("local_path"),
    }
    if any(not isinstance(value, str) or not value.strip() for value in required_values.values()):
        raise ValueError(f"passport file has missing required string fields: {passport_path}")

    return ExportSyncPassportRecord(
        slug=slug,
        name=str(required_values["name"]).strip(),
        category=str(required_values["category"]).strip(),
        status=str(required_values["status"]).strip(),
        registry_action=str(project.get("registry_action", "")).strip(),
        local_path=str(required_values["local_path"]).strip(),
        allow_code_to_obsidian=bool(sync.get("allow_code_to_obsidian", False)),
        allow_secrets=bool(sync.get("allow_secrets", False)),
        do_not_sync=bool(safety.get("do_not_sync", False)),
        warnings=tuple(str(item) for item in warnings),
        passport_path=passport_path,
    )


def determine_skip_reasons(record: ExportSyncPassportRecord) -> list[str]:
    reasons: list[str] = []
    slug_lower = record.slug.lower()
    local_path_lower = record.local_path.lower()

    if record.do_not_sync:
        reasons.append("safety.do_not_sync=true")
    if record.allow_code_to_obsidian:
        reasons.append("sync.allow_code_to_obsidian=true")
    if record.allow_secrets:
        reasons.append("sync.allow_secrets=true")
    if slug_lower == "cerberus" or "cerberus" in slug_lower or "cerberus" in local_path_lower:
        reasons.append("cerberus_protected")
    if record.category not in DEFAULT_ELIGIBLE_CATEGORIES:
        reasons.append(f"classification={record.category}")
    if record.registry_action in FORCED_SKIP_REGISTRY_ACTIONS:
        reasons.append(f"registry_action={record.registry_action}")

    return reasons


def determine_destination_docs_root(record: ExportSyncPassportRecord, repo_root_override: str | None) -> Path:
    local_root = Path(record.local_path).expanduser().resolve()
    destination_docs_root = (local_root / "docs").resolve()
    ensure_path_within(local_root, destination_docs_root, "destination docs root")

    if repo_root_override:
        override = Path(repo_root_override).expanduser()
        if not override.is_absolute():
            override = local_root / override
        override = override.resolve()
        ensure_path_within(destination_docs_root, override, "repo root override")
        return override

    return destination_docs_root


def evaluate_candidate_file(source_path: Path, rel_export_path: Path) -> str | None:
    if any(part in EXCLUDED_DIR_NAMES for part in rel_export_path.parts[:-1]):
        return "excluded_directory"

    name_lower = source_path.name.lower()
    suffix_lower = source_path.suffix.lower()

    if ".bak" in name_lower:
        return "excluded_bak_file"
    if source_path.name.startswith(".env") or suffix_lower == ".env":
        return "excluded_env_file"
    if suffix_lower in EXCLUDED_SUFFIXES:
        return f"excluded_suffix={suffix_lower}"
    if suffix_lower != ".md":
        return "non_markdown_file"

    return None


def determine_candidates(
    *,
    source_export_root: Path,
    source_docs_root: Path,
    include_files: set[Path],
    exclude_files: set[Path],
) -> tuple[list[tuple[Path, Path]], list[ExportSyncExcludedFile], list[str]]:
    selected: list[tuple[Path, Path]] = []
    excluded: list[ExportSyncExcludedFile] = []
    notes: list[str] = []

    if include_files:
        for rel_export_path in sorted(include_files, key=lambda p: p.as_posix()):
            if rel_export_path == Path("README.md"):
                source_path = (source_export_root / rel_export_path).resolve()
                ensure_path_within(source_export_root, source_path, "included source file")
                if not source_path.exists() or not source_path.is_file():
                    excluded.append(
                        ExportSyncExcludedFile(
                            source_relative_export_path=rel_export_path.as_posix(),
                            reason="include_missing",
                        )
                    )
                    continue

                exclude_reason = evaluate_candidate_file(source_path, rel_export_path)
                if exclude_reason:
                    excluded.append(
                        ExportSyncExcludedFile(
                            source_relative_export_path=rel_export_path.as_posix(),
                            reason=exclude_reason,
                        )
                    )
                    continue

                selected.append((source_path, rel_export_path))
                continue

            if not rel_export_path.parts or rel_export_path.parts[0] != "docs":
                excluded.append(
                    ExportSyncExcludedFile(
                        source_relative_export_path=rel_export_path.as_posix(),
                        reason="include_outside_allowed_scope",
                    )
                )
                continue

            source_path = (source_export_root / rel_export_path).resolve()
            ensure_path_within(source_export_root, source_path, "included source file")
            if not source_path.exists() or not source_path.is_file():
                excluded.append(
                    ExportSyncExcludedFile(
                        source_relative_export_path=rel_export_path.as_posix(),
                        reason="include_missing",
                    )
                )
                continue

            exclude_reason = evaluate_candidate_file(source_path, rel_export_path)
            if exclude_reason:
                excluded.append(
                    ExportSyncExcludedFile(
                        source_relative_export_path=rel_export_path.as_posix(),
                        reason=exclude_reason,
                    )
                )
                continue

            selected.append((source_path, rel_export_path))
    else:
        if not source_docs_root.exists() or not source_docs_root.is_dir():
            notes.append("source_export_docs_missing")
            return selected, excluded, notes

        for source_path in sorted(source_docs_root.rglob("*")):
            if not source_path.is_file():
                continue
            rel_docs_path = source_path.relative_to(source_docs_root)
            rel_export_path = Path("docs") / rel_docs_path
            exclude_reason = evaluate_candidate_file(source_path, rel_export_path)
            if exclude_reason:
                excluded.append(
                    ExportSyncExcludedFile(
                        source_relative_export_path=rel_export_path.as_posix(),
                        reason=exclude_reason,
                    )
                )
                continue
            selected.append((source_path, rel_export_path))

    filtered: list[tuple[Path, Path]] = []
    for source_path, rel_export_path in selected:
        if rel_export_path in exclude_files:
            excluded.append(
                ExportSyncExcludedFile(
                    source_relative_export_path=rel_export_path.as_posix(),
                    reason="excluded_by_flag",
                )
            )
            continue
        filtered.append((source_path, rel_export_path))

    deduped: dict[str, tuple[Path, Path]] = {}
    for source_path, rel_export_path in filtered:
        deduped[rel_export_path.as_posix()] = (source_path, rel_export_path)
    return [deduped[key] for key in sorted(deduped)], excluded, notes


def build_destination_path(destination_docs_root: Path, rel_export_path: Path) -> Path:
    if rel_export_path == Path("README.md"):
        return (destination_docs_root / "README.md").resolve()

    if not rel_export_path.parts or rel_export_path.parts[0] != "docs":
        raise ValueError(f"unexpected export-relative path outside docs mapping: {rel_export_path}")

    rel_docs_path = Path(*rel_export_path.parts[1:])
    if str(rel_docs_path) in {"", "."}:
        raise ValueError("docs relative path must not be empty")
    return (destination_docs_root / rel_docs_path).resolve()


def build_sync_plan(
    *,
    mode: str,
    slug: str,
    passport_dir: Path,
    vault_project_root: Path,
    repo_root_override: str | None,
    include_files: set[Path],
    exclude_files: set[Path],
    report_name: str,
    backup_suffix: str,
) -> ExportSyncPlan:
    record = load_passport_record(passport_dir, slug)
    source_export_root = (vault_project_root / slug / "_export").resolve()
    ensure_path_within(vault_project_root, source_export_root, "source export root")
    source_docs_root = (source_export_root / "docs").resolve()
    ensure_path_within(source_export_root, source_docs_root, "source docs root")

    destination_docs_root = determine_destination_docs_root(record, repo_root_override)
    local_root = Path(record.local_path).expanduser().resolve()
    ensure_path_within(local_root, destination_docs_root, "destination docs root")

    reasons = determine_skip_reasons(record)
    selected, excluded, notes = determine_candidates(
        source_export_root=source_export_root,
        source_docs_root=source_docs_root,
        include_files=include_files,
        exclude_files=exclude_files,
    )
    reasons.extend(notes)

    eligible = not any(
        reason.startswith("safety.")
        or reason.startswith("sync.")
        or reason.startswith("classification=")
        or reason.startswith("registry_action=")
        or reason == "cerberus_protected"
        for reason in reasons
    )

    file_actions: list[ExportSyncFileAction] = []
    if eligible:
        for source_path, rel_export_path in selected:
            destination_path = build_destination_path(destination_docs_root, rel_export_path)
            ensure_path_within(destination_docs_root, destination_path, "destination file path")
            existed_before = destination_path.exists()
            file_actions.append(
                ExportSyncFileAction(
                    source_path=source_path,
                    source_relative_export_path=rel_export_path,
                    destination_path=destination_path,
                    backup_path=build_backup_path(destination_path, backup_suffix) if existed_before else None,
                    existed_before=existed_before,
                )
            )

    entry = ExportSyncPlanEntry(
        record=record,
        source_export_root=source_export_root,
        source_docs_root=source_docs_root,
        destination_docs_root=destination_docs_root,
        eligible=eligible,
        reasons=reasons,
        file_actions=file_actions,
        excluded_files=sorted(excluded, key=lambda item: (item.source_relative_export_path, item.reason)),
    )

    report_path = passport_dir.resolve().parent / normalize_report_name(report_name)
    return ExportSyncPlan(
        mode=mode,
        slug=slug,
        passport_dir=passport_dir,
        vault_project_root=vault_project_root,
        repo_root_override=destination_docs_root if repo_root_override else None,
        report_path=report_path,
        entry=entry,
    )


def apply_sync_plan(plan: ExportSyncPlan) -> None:
    if not plan.entry.eligible:
        return

    plan.entry.destination_docs_root.mkdir(parents=True, exist_ok=True)
    for action in plan.entry.file_actions:
        action.destination_path.parent.mkdir(parents=True, exist_ok=True)
        if action.backup_path is not None:
            action.backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(action.destination_path, action.backup_path)
            action.backup_created = True
        shutil.copy2(action.source_path, action.destination_path)
        action.copied = True


def create_sync_plan_from_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> ExportSyncPlan:
    mode = parse_mode(args, parser)
    passport_dir = resolve_repo_scoped_dir(args.passport_dir, "passport dir")
    vault_project_root = resolve_vault_project_root(args.vault_project_root)
    backup_suffix = args.backup_suffix or datetime.now().strftime("%Y%m%d-%H%M%S")
    include_files = {parse_relative_export_path(item) for item in args.include_file}
    exclude_files = {parse_relative_export_path(item) for item in args.exclude_file}

    return build_sync_plan(
        mode=mode,
        slug=args.slug,
        passport_dir=passport_dir,
        vault_project_root=vault_project_root,
        repo_root_override=args.repo_root_override,
        include_files=include_files,
        exclude_files=exclude_files,
        report_name=args.report_name,
        backup_suffix=backup_suffix,
    )


def format_console_summary(plan: ExportSyncPlan) -> str:
    return "\n".join(
        [
            f"Mode: {plan.mode}",
            f"Slug: {plan.slug}",
            f"Source export root: {plan.entry.source_export_root}",
            f"Source docs root: {plan.entry.source_docs_root}",
            f"Destination docs root: {plan.entry.destination_docs_root}",
            f"Eligible: {str(plan.entry.eligible).lower()}",
            f"Files planned: {plan.files_planned}",
            f"Files copied: {plan.files_copied}",
            f"Backups planned: {plan.backups_planned}",
            f"Backups created: {plan.backups_created}",
            f"Excluded files: {len(plan.entry.excluded_files)}",
            f"Report: {plan.report_path}",
        ]
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    plan = create_sync_plan_from_args(args, parser)

    plan.report_path.parent.mkdir(parents=True, exist_ok=True)
    if plan.mode == "apply":
        apply_sync_plan(plan)
    write_export_sync_report(plan.report_path, plan)

    print(format_console_summary(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
