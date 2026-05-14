from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from .obsidian_mirror_generation import parse_simple_yaml
from .obsidian_sync_models import (
    ObsidianSyncExcludedFile,
    ObsidianSyncFileAction,
    ObsidianSyncPassportRecord,
    ObsidianSyncPlan,
    ObsidianSyncPlanEntry,
)
from .obsidian_sync_reporting import write_obsidian_sync_report

DEFAULT_PASSPORT_DIR = "artifacts/project_passports"
DEFAULT_MIRROR_DIR = "artifacts/obsidian_mirrors"
DEFAULT_VAULT_PROJECT_ROOT = "/home/cole/main_vault/10 Projects"
DEFAULT_REPORT_NAME = "obsidian_sync_report.md"
EXCLUDED_DIR_NAMES = {"node_modules", ".venv", "__pycache__", ".git"}
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
        prog="project-forge-obsidian-sync",
        description="Dry-run-first docs-only sync from mirror proposals to the real Obsidian vault project folder.",
    )
    parser.add_argument(
        "--slug",
        required=True,
        help="Project slug to sync.",
    )
    parser.add_argument(
        "--passport-dir",
        default=DEFAULT_PASSPORT_DIR,
        help="Directory containing passport proposal files.",
    )
    parser.add_argument(
        "--mirror-dir",
        default=DEFAULT_MIRROR_DIR,
        help="Directory containing generated mirror proposal folders.",
    )
    parser.add_argument(
        "--vault-project-root",
        default=DEFAULT_VAULT_PROJECT_ROOT,
        help="Destination vault project root directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan sync only and write the artifact report. This is the default mode.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Copy markdown files into the destination vault project folder.",
    )
    parser.add_argument(
        "--report-name",
        default=DEFAULT_REPORT_NAME,
        help="Filename for the sync report written inside artifacts/.",
    )
    parser.add_argument(
        "--backup-suffix",
        default=None,
        help="Suffix appended to backups for existing destination markdown files. Defaults to a timestamp.",
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
        raise ValueError("report name must be a simple filename inside this repository's artifacts directory")
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


def resolve_report_path(report_name: str, mirror_dir: Path) -> Path:
    return mirror_dir.resolve().parent / normalize_report_name(report_name)


def ensure_destination_within_vault_root(destination: Path, vault_project_root: Path) -> None:
    resolved_root = vault_project_root.expanduser().resolve()
    resolved_destination = destination.expanduser().resolve()
    if resolved_destination != resolved_root and resolved_root not in resolved_destination.parents:
        raise ValueError(f"destination path must stay inside vault project root {resolved_root}")


def build_backup_path(target_path: Path, backup_suffix: str) -> Path:
    return target_path.with_name(f"{target_path.name}.bak.{backup_suffix}")


def load_passport_record(passport_dir: Path, slug: str) -> ObsidianSyncPassportRecord:
    passport_path = passport_dir / f"{slug}.project.yml"
    if not passport_path.exists():
        raise ValueError(f"passport file not found for slug '{slug}': {passport_path}")

    payload = parse_simple_yaml(passport_path.read_text(encoding="utf-8"))
    project = payload.get("project")
    paths = payload.get("paths")
    sync = payload.get("sync")
    safety = payload.get("safety")

    if not all(isinstance(section, dict) for section in (project, paths, sync, safety)):
        raise ValueError(f"passport file is missing required sections: {passport_path}")

    record_slug = str(project.get("slug", "")).strip()
    if record_slug != slug:
        raise ValueError(f"passport slug mismatch: expected '{slug}', found '{record_slug}'")

    warnings = safety.get("warnings", [])
    if not isinstance(warnings, list):
        raise ValueError(f"passport warnings must be a list: {passport_path}")

    required_values = {
        "name": project.get("name"),
        "local_path": project.get("local_path"),
        "category": project.get("category"),
        "status": project.get("status"),
        "obsidian_path": paths.get("obsidian"),
    }
    if any(not isinstance(value, str) or not value.strip() for value in required_values.values()):
        raise ValueError(f"passport file has missing required string fields: {passport_path}")

    return ObsidianSyncPassportRecord(
        slug=slug,
        name=str(required_values["name"]).strip(),
        local_path=str(required_values["local_path"]).strip(),
        category=str(required_values["category"]).strip(),
        status=str(required_values["status"]).strip(),
        obsidian_path=str(required_values["obsidian_path"]).strip(),
        allow_code_to_obsidian=bool(sync.get("allow_code_to_obsidian", False)),
        allow_secrets=bool(sync.get("allow_secrets", False)),
        do_not_sync=bool(safety.get("do_not_sync", False)),
        warnings=tuple(str(item) for item in warnings),
        passport_path=passport_path,
    )


def destination_folder_name(record: ObsidianSyncPassportRecord) -> str:
    obsidian_path = Path(record.obsidian_path.rstrip("/"))
    folder_name = obsidian_path.name.strip()
    if not folder_name:
        raise ValueError("passport obsidian path must include a final project folder name")
    if folder_name in {".", ".."}:
        raise ValueError("passport obsidian project folder name is invalid")
    return folder_name


def gather_candidate_files(source_mirror_dir: Path) -> tuple[list[Path], list[ObsidianSyncExcludedFile]]:
    allowed: list[Path] = []
    excluded: list[ObsidianSyncExcludedFile] = []

    for candidate in sorted(source_mirror_dir.rglob("*")):
        if candidate.is_dir():
            continue

        relative_path = candidate.relative_to(source_mirror_dir)
        path_parts = set(relative_path.parts[:-1])
        if path_parts.intersection(EXCLUDED_DIR_NAMES):
            excluded.append(
                ObsidianSyncExcludedFile(
                    source_path=candidate,
                    reason="excluded_directory",
                )
            )
            continue

        name_lower = candidate.name.lower()
        suffix_lower = candidate.suffix.lower()

        if ".bak" in name_lower:
            excluded.append(ObsidianSyncExcludedFile(source_path=candidate, reason="excluded_bak_file"))
            continue
        if candidate.name.startswith(".env") or suffix_lower == ".env":
            excluded.append(ObsidianSyncExcludedFile(source_path=candidate, reason="excluded_env_file"))
            continue
        if suffix_lower in EXCLUDED_SUFFIXES:
            excluded.append(ObsidianSyncExcludedFile(source_path=candidate, reason=f"excluded_suffix={suffix_lower}"))
            continue
        if suffix_lower != ".md":
            excluded.append(ObsidianSyncExcludedFile(source_path=candidate, reason="non_markdown_file"))
            continue

        allowed.append(candidate)

    return allowed, excluded


def determine_skip_reasons(record: ObsidianSyncPassportRecord) -> list[str]:
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

    return reasons


def build_sync_plan(
    *,
    mode: str,
    slug: str,
    passport_dir: Path,
    mirror_dir: Path,
    vault_project_root: Path,
    report_name: str,
    backup_suffix: str,
) -> ObsidianSyncPlan:
    record = load_passport_record(passport_dir, slug)
    source_mirror_dir = (mirror_dir / slug).resolve()
    if not source_mirror_dir.exists() or not source_mirror_dir.is_dir():
        raise ValueError(f"source mirror directory not found for slug '{slug}': {source_mirror_dir}")

    target_folder_name = destination_folder_name(record)
    destination_vault_dir = (vault_project_root / target_folder_name).resolve()
    ensure_destination_within_vault_root(destination_vault_dir, vault_project_root)

    reasons = determine_skip_reasons(record)
    allowed_files, excluded_files = gather_candidate_files(source_mirror_dir)
    eligible = not reasons

    file_actions: list[ObsidianSyncFileAction] = []
    if eligible:
        for source_file in allowed_files:
            relative_path = source_file.relative_to(source_mirror_dir)
            destination_path = destination_vault_dir / relative_path
            ensure_destination_within_vault_root(destination_path, vault_project_root)
            existed_before = destination_path.exists()
            file_actions.append(
                ObsidianSyncFileAction(
                    source_path=source_file,
                    destination_path=destination_path,
                    backup_path=build_backup_path(destination_path, backup_suffix) if existed_before else None,
                    existed_before=existed_before,
                )
            )

    entry = ObsidianSyncPlanEntry(
        record=record,
        source_mirror_dir=source_mirror_dir,
        destination_vault_dir=destination_vault_dir,
        eligible=eligible,
        reasons=reasons,
        file_actions=file_actions,
        excluded_files=excluded_files,
    )

    report_path = resolve_report_path(report_name, mirror_dir)
    ensure_destination_within_vault_root(vault_project_root, vault_project_root)
    return ObsidianSyncPlan(
        mode=mode,
        slug=slug,
        passport_dir=passport_dir,
        mirror_dir=mirror_dir,
        source_mirror_path=source_mirror_dir,
        vault_project_root=vault_project_root.resolve(),
        destination_vault_path=destination_vault_dir,
        report_path=report_path,
        entry=entry,
    )


def apply_sync_plan(plan: ObsidianSyncPlan) -> None:
    if not plan.entry.eligible:
        return

    plan.destination_vault_path.mkdir(parents=True, exist_ok=True)
    for action in plan.entry.file_actions:
        action.destination_path.parent.mkdir(parents=True, exist_ok=True)
        if action.backup_path is not None:
            action.backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(action.destination_path, action.backup_path)
            action.backup_created = True
        shutil.copy2(action.source_path, action.destination_path)
        action.copied = True


def create_sync_plan_from_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> ObsidianSyncPlan:
    mode = parse_mode(args, parser)
    backup_suffix = args.backup_suffix or datetime.now().strftime("%Y%m%d-%H%M%S")
    passport_dir = resolve_repo_scoped_dir(args.passport_dir, "passport dir")
    mirror_dir = resolve_repo_scoped_dir(args.mirror_dir, "mirror dir")
    vault_project_root = resolve_vault_project_root(args.vault_project_root)

    return build_sync_plan(
        mode=mode,
        slug=args.slug,
        passport_dir=passport_dir,
        mirror_dir=mirror_dir,
        vault_project_root=vault_project_root,
        report_name=args.report_name,
        backup_suffix=backup_suffix,
    )


def format_console_summary(plan: ObsidianSyncPlan) -> str:
    return "\n".join(
        [
            f"Mode: {plan.mode}",
            f"Slug: {plan.slug}",
            f"Source mirror path: {plan.source_mirror_path}",
            f"Destination vault path: {plan.destination_vault_path}",
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
    write_obsidian_sync_report(plan.report_path, plan)

    print(format_console_summary(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
