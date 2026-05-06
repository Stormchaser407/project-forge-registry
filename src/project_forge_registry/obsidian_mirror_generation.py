from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from .obsidian_mirror_models import (
    ObsidianMirrorFileAction,
    ObsidianMirrorGenerationPlan,
    ObsidianMirrorPassportRecord,
    ObsidianMirrorPlanEntry,
)
from .obsidian_mirror_reporting import write_obsidian_mirror_generation_report

DEFAULT_PASSPORT_DIR = "artifacts/project_passports"
DEFAULT_REPORT_NAME = "obsidian_mirror_generation_report.md"
DEFAULT_MIRRORS_DIRNAME = "obsidian_mirrors"
DEFAULT_ELIGIBLE_CATEGORIES = {"active_project", "operated_tool"}
DEFAULT_SKIPPED_CATEGORIES = {
    "system_bound_project",
    "reconciliation_required",
    "archive",
    "lab",
    "unknown",
    "vendor_clone",
}
NOTE_FILENAMES = (
    "Demo Script.md",
    "Architecture.md",
    "Decisions.md",
    "Roadmap.md",
    "Agent Handoff.md",
    "Runbook.md",
    "Changelog.md",
    "_export/README.md",
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def repository_artifacts_root() -> Path:
    return repository_root() / "artifacts"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-forge-obsidian-mirror-generate",
        description="Dry-run-first Obsidian mirror proposal generator.",
    )
    parser.add_argument(
        "--passport-dir",
        default=DEFAULT_PASSPORT_DIR,
        help="Directory containing passport proposal files.",
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
        help="Write mirror proposal files inside artifacts/obsidian_mirrors after planning.",
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
        help="Suffix appended to backups for existing mirror proposal files. Defaults to a timestamp.",
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


def resolve_passport_dir(passport_dir: str | Path) -> Path:
    candidate = Path(passport_dir).expanduser()
    if not candidate.is_absolute():
        candidate = repository_root() / candidate
    return candidate.resolve()


def build_backup_path(target_path: Path, backup_suffix: str) -> Path:
    return target_path.with_name(f"{target_path.name}.bak.{backup_suffix}")


def ensure_allowed_target(target_path: Path, mirror_dir: Path) -> None:
    resolved_mirror_dir = mirror_dir.expanduser().resolve()
    resolved_target = target_path.expanduser().resolve()
    if resolved_mirror_dir not in resolved_target.parents:
        raise ValueError(f"target must stay inside mirror dir {resolved_mirror_dir}")


def parse_yaml_scalar(value: str) -> object:
    if value == "null":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "[]":
        return []
    if value == '""':
        return ""
    if value.startswith('"') and value.endswith('"'):
        inner = value[1:-1]
        return inner.replace('\\"', '"').replace("\\\\", "\\")
    return value


def parse_simple_yaml(text: str) -> dict[str, object]:
    lines = [line.rstrip("\n") for line in text.splitlines() if line.strip()]

    def parse_block(start_index: int, indent: int) -> tuple[object, int]:
        mapping: dict[str, object] = {}
        sequence: list[object] = []
        mode: str | None = None
        index = start_index

        while index < len(lines):
            raw_line = lines[index]
            current_indent = len(raw_line) - len(raw_line.lstrip(" "))
            if current_indent < indent:
                break
            if current_indent != indent:
                raise ValueError(f"unsupported indentation in YAML line: {raw_line}")

            line = raw_line[indent:]
            if line.startswith("- "):
                if mode is None:
                    mode = "list"
                if mode != "list":
                    raise ValueError("cannot mix mapping and list entries at the same indentation level")
                item_text = line[2:].strip()
                if item_text:
                    sequence.append(parse_yaml_scalar(item_text))
                    index += 1
                    continue
                child, index = parse_block(index + 1, indent + 2)
                sequence.append(child)
                continue

            if mode is None:
                mode = "dict"
            if mode != "dict":
                raise ValueError("cannot mix list and mapping entries at the same indentation level")

            key, separator, remainder = line.partition(":")
            if separator != ":":
                raise ValueError(f"invalid YAML mapping entry: {raw_line}")
            value_text = remainder.strip()
            if value_text:
                mapping[key] = parse_yaml_scalar(value_text)
                index += 1
                continue

            child, index = parse_block(index + 1, indent + 2)
            mapping[key] = child

        if mode == "list":
            return sequence, index
        return mapping, index

    parsed, next_index = parse_block(0, 0)
    if next_index != len(lines):
        raise ValueError("could not fully parse YAML input")
    if not isinstance(parsed, dict):
        raise ValueError("top-level YAML payload must be a mapping")
    return parsed


def load_passport_records(passport_dir: Path) -> list[ObsidianMirrorPassportRecord]:
    records: list[ObsidianMirrorPassportRecord] = []
    for passport_path in sorted(passport_dir.glob("*.project.yml")):
        payload = parse_simple_yaml(passport_path.read_text(encoding="utf-8"))
        project = payload.get("project")
        paths = payload.get("paths")
        launch = payload.get("launch")
        sync = payload.get("sync")
        safety = payload.get("safety")

        if not all(isinstance(section, dict) for section in (project, paths, launch, sync, safety)):
            raise ValueError(f"passport file is missing required sections: {passport_path}")

        warnings = safety.get("warnings", [])
        if not isinstance(warnings, list):
            raise ValueError(f"passport warnings must be a list: {passport_path}")

        required_values = {
            "slug": project.get("slug"),
            "name": project.get("name"),
            "category": project.get("category"),
            "status": project.get("status"),
            "local_path": project.get("local_path"),
            "workspace_path": paths.get("workspace"),
            "obsidian_path": paths.get("obsidian"),
            "launcher_command": launch.get("command"),
            "obsidian_to_repo": sync.get("obsidian_to_repo"),
            "repo_to_obsidian": sync.get("repo_to_obsidian"),
        }
        if any(not isinstance(value, str) or not value.strip() for value in required_values.values()):
            raise ValueError(f"passport file has missing required string fields: {passport_path}")

        records.append(
            ObsidianMirrorPassportRecord(
                slug=str(required_values["slug"]).strip(),
                name=str(required_values["name"]).strip(),
                category=str(required_values["category"]).strip(),
                status=str(required_values["status"]).strip(),
                local_path=str(required_values["local_path"]).strip(),
                workspace_path=str(required_values["workspace_path"]).strip(),
                obsidian_path=str(required_values["obsidian_path"]).strip(),
                launcher_command=str(required_values["launcher_command"]).strip(),
                obsidian_to_repo=str(required_values["obsidian_to_repo"]).strip(),
                repo_to_obsidian=str(required_values["repo_to_obsidian"]).strip(),
                allow_code_to_obsidian=bool(sync.get("allow_code_to_obsidian", False)),
                allow_secrets=bool(sync.get("allow_secrets", False)),
                do_not_move=bool(safety.get("do_not_move", False)),
                do_not_delete=bool(safety.get("do_not_delete", False)),
                do_not_sync=bool(safety.get("do_not_sync", False)),
                warnings=tuple(str(item) for item in warnings),
                passport_path=passport_path,
            )
        )
    return records


def collect_duplicate_slugs(records: list[ObsidianMirrorPassportRecord]) -> set[str]:
    counts: dict[str, int] = {}
    for record in records:
        counts[record.slug] = counts.get(record.slug, 0) + 1
    return {slug for slug, count in counts.items() if count > 1}


def slug_dir_name(record: ObsidianMirrorPassportRecord) -> str:
    return record.slug


def home_filename(record: ObsidianMirrorPassportRecord) -> str:
    return f"{record.name} - Project Home.md"


def safe_command_block(record: ObsidianMirrorPassportRecord) -> str:
    return "\n".join(
        [
            "```bash",
            f'code "{record.workspace_path}"',
            f"{record.launcher_command}",
            "```",
        ]
    )


def title_alias_frontmatter(title: str, alias: str) -> str:
    return "\n".join(
        [
            "---",
            f'title: "{title}"',
            "aliases:",
            f'  - "{alias}"',
            "---",
            "",
        ]
    )


def render_project_home(record: ObsidianMirrorPassportRecord) -> str:
    sync_policy = f"{record.repo_to_obsidian} / {record.obsidian_to_repo}"
    warnings = "\n".join(f"- {warning}" for warning in record.warnings) if record.warnings else "- None currently recorded."
    return "\n".join(
        [
            "---",
            f'project_slug: "{record.slug}"',
            f'category: "{record.category}"',
            f'status: "{record.status}"',
            f'local_path: "{record.local_path}"',
            f'launcher_command: "{record.launcher_command}"',
            f'workspace_path: "{record.workspace_path}"',
            f'sync_policy: "{sync_policy}"',
            "---",
            "",
            f"# {record.name} - Project Home",
            "",
            "- [[Project Command Board]]",
            f'- [[{record.name} - Demo Script]]',
            f'- [[{record.name} - Architecture]]',
            f'- [[{record.name} - Decisions]]',
            f'- [[{record.name} - Roadmap]]',
            f'- [[{record.name} - Agent Handoff]]',
            f'- [[{record.name} - Runbook]]',
            f'- [[{record.name} - Changelog]]',
            "",
            "## Purpose",
            "",
            f"Placeholder planning note for the `{record.slug}` mirror proposal.",
            "",
            "## Current Status",
            "",
            f"- Registry status: `{record.status}`",
            f"- Category: `{record.category}`",
            f"- Proposed mirror path: `{record.obsidian_path}`",
            "",
            "## What This Project Does",
            "",
            "Capture a safe documentation shell without copying source code into Obsidian.",
            "",
            "## Why It Matters",
            "",
            "Gives operators a clean project-facing surface for demos, status, handoff, and runbook material.",
            "",
            "## Current Risks / Watch Items",
            "",
            warnings,
            "",
            "## Next Actions",
            "",
            "- Review this proposal before any real vault sync is introduced.",
            "- Fill in purpose, risks, and roadmap details manually or through later approved automation.",
            "",
            "## Demo Notes",
            "",
            "- Start from the launcher or workspace path below.",
            "- Keep demo language high level until docs-only sync is approved.",
            "",
            "## Links and Commands",
            "",
            f"- Local path: `{record.local_path}`",
            f"- Workspace path: `{record.workspace_path}`",
            f"- Launcher command: `{record.launcher_command}`",
            f"- Sync policy: `{sync_policy}`",
            "",
            safe_command_block(record),
            "",
        ]
    )


def render_demo_script(record: ObsidianMirrorPassportRecord) -> str:
    title = f"{record.name} - Demo Script"
    return "\n".join(
        [
            title_alias_frontmatter(title, title).rstrip(),
            f"# {title}",
            "",
            "## Thirty-Second Version",
            "",
            "Describe the shortest useful story for the project.",
            "",
            "## Why I Built This",
            "",
            "Capture the user problem or workflow this project exists to serve.",
            "",
            "## What It Does Right Now",
            "",
            "List the current reliable capabilities only.",
            "",
            "## What Makes It Different",
            "",
            "Note the differentiator without copying implementation details.",
            "",
            "## Cool Part To Show First",
            "",
            "Call out the first moment that makes the project click.",
            "",
            "## Current Limitations",
            "",
            "Document the rough edges and what still needs operator care.",
            "",
            "## Next Build Step",
            "",
            "Record the next concrete improvement worth building.",
            "",
        ]
    )


def render_architecture(record: ObsidianMirrorPassportRecord) -> str:
    title = f"{record.name} - Architecture"
    return "\n".join(
        [
            title_alias_frontmatter(title, title).rstrip(),
            f"# {title}",
            "",
            "## Overview",
            "",
            "Summarize the major components at a high level without copying source code.",
            "",
            "## Boundaries",
            "",
            "- Local path is tracked in the passport.",
            "- Real Obsidian sync is not enabled in this phase.",
            "",
            "## Interfaces",
            "",
            "List the main entry points, services, or integrations to describe later.",
            "",
        ]
    )


def render_decisions(record: ObsidianMirrorPassportRecord) -> str:
    title = f"{record.name} - Decisions"
    return "\n".join(
        [
            title_alias_frontmatter(title, title).rstrip(),
            f"# {title}",
            "",
            "## Decision Log",
            "",
            "- Capture notable design choices here.",
            "- Add date, rationale, and follow-up when details are known.",
            "",
        ]
    )


def render_roadmap(record: ObsidianMirrorPassportRecord) -> str:
    title = f"{record.name} - Roadmap"
    return "\n".join(
        [
            title_alias_frontmatter(title, title).rstrip(),
            f"# {title}",
            "",
            "## Near Term",
            "",
            "- Next approved documentation or automation step.",
            "",
            "## Later",
            "",
            "- Future work once mirror sync is approved.",
            "",
        ]
    )


def render_agent_handoff(record: ObsidianMirrorPassportRecord) -> str:
    title = f"{record.name} - Agent Handoff"
    return "\n".join(
        [
            title_alias_frontmatter(title, title).rstrip(),
            f"# {title}",
            "",
            "## Scope",
            "",
            f"- Project slug: `{record.slug}`",
            f"- Local path: `{record.local_path}`",
            "",
            "## Current State",
            "",
            f"- Status: `{record.status}`",
            f"- Category: `{record.category}`",
            "",
            "## Safe Commands",
            "",
            safe_command_block(record),
            "",
            "## Do Not Touch",
            "",
            "- Do not write into the real Obsidian vault in this phase.",
            "- Do not copy source code, secrets, or operational databases into mirror docs.",
            "- Do not change external project folders from this workflow.",
            "",
            "## Next Suggested Agent Task",
            "",
            "- Review and enrich the proposed docs shell with approved high-level content only.",
            "",
        ]
    )


def render_runbook(record: ObsidianMirrorPassportRecord) -> str:
    title = f"{record.name} - Runbook"
    return "\n".join(
        [
            title_alias_frontmatter(title, title).rstrip(),
            f"# {title}",
            "",
            "## Open Project",
            "",
            safe_command_block(record),
            "",
            "## Common Commands",
            "",
            "- Add the safest daily commands here.",
            "",
            "## Test Commands",
            "",
            "- Add non-destructive verification commands here.",
            "",
            "## Recovery Notes",
            "",
            "- Record rollback or reset guidance that does not rely on destructive shortcuts.",
            "",
        ]
    )


def render_changelog(record: ObsidianMirrorPassportRecord) -> str:
    title = f"{record.name} - Changelog"
    return "\n".join(
        [
            title_alias_frontmatter(title, title).rstrip(),
            f"# {title}",
            "",
            "## Changes",
            "",
            "- Track operator-facing changes here.",
            "",
        ]
    )


def render_export_readme(record: ObsidianMirrorPassportRecord) -> str:
    return "\n".join(
        [
            f"# {record.name} Export Staging",
            "",
            "This folder is reserved for docs-only export material.",
            "",
            "- No source code copies.",
            "- No secrets or env files.",
            "- No operational database or log material.",
            "- `docs/` stays empty until a later approved export phase.",
            "",
        ]
    )


def build_file_contents(record: ObsidianMirrorPassportRecord) -> dict[str, str]:
    return {
        home_filename(record): render_project_home(record),
        "Demo Script.md": render_demo_script(record),
        "Architecture.md": render_architecture(record),
        "Decisions.md": render_decisions(record),
        "Roadmap.md": render_roadmap(record),
        "Agent Handoff.md": render_agent_handoff(record),
        "Runbook.md": render_runbook(record),
        "Changelog.md": render_changelog(record),
        "_export/README.md": render_export_readme(record),
    }


def determine_reasons(
    record: ObsidianMirrorPassportRecord,
    include_slugs: set[str],
    exclude_slugs: set[str],
    include_categories: set[str],
    exclude_categories: set[str],
    duplicate_slugs: set[str],
) -> list[str]:
    reasons: list[str] = []
    explicitly_included = record.category in include_categories

    if include_slugs and record.slug not in include_slugs:
        reasons.append("not_selected_by_include_slug")
    if record.slug in exclude_slugs:
        reasons.append("excluded_by_slug")
    if record.slug in duplicate_slugs:
        reasons.append("duplicate_slug_collision")
    if record.category in exclude_categories:
        reasons.append(f"excluded_category={record.category}")
    if record.do_not_sync:
        reasons.append("safety.do_not_sync=true")
    if record.allow_code_to_obsidian:
        reasons.append("sync.allow_code_to_obsidian=true")
    if record.allow_secrets:
        reasons.append("sync.allow_secrets=true")
    if record.slug == "cerberus" or "cerberus" in record.slug or "cerberus" in record.local_path.lower():
        reasons.append("cerberus_protected")
    if record.category in DEFAULT_SKIPPED_CATEGORIES and not explicitly_included:
        reasons.append(f"classification={record.category}")

    if record.category in DEFAULT_ELIGIBLE_CATEGORIES and not explicitly_included:
        return reasons
    if record.category in DEFAULT_SKIPPED_CATEGORIES and not explicitly_included:
        return reasons
    if record.category not in DEFAULT_ELIGIBLE_CATEGORIES and not explicitly_included:
        reasons.append(f"classification={record.category}_not_eligible_by_default")
    return reasons


def build_generation_plan(
    *,
    records: list[ObsidianMirrorPassportRecord],
    mode: str,
    passport_dir: Path,
    artifacts_dir: Path,
    report_name: str,
    include_slugs: set[str],
    exclude_slugs: set[str],
    include_categories: set[str],
    exclude_categories: set[str],
    backup_suffix: str,
) -> ObsidianMirrorGenerationPlan:
    normalized_report_name = normalize_report_name(report_name)
    mirrors_dir = artifacts_dir / DEFAULT_MIRRORS_DIRNAME
    report_path = artifacts_dir / normalized_report_name
    duplicate_slugs = collect_duplicate_slugs(records)

    entries: list[ObsidianMirrorPlanEntry] = []
    for record in records:
        mirror_dir = mirrors_dir / slug_dir_name(record)
        reasons = determine_reasons(
            record,
            include_slugs,
            exclude_slugs,
            include_categories,
            exclude_categories,
            duplicate_slugs,
        )
        eligible = not reasons
        entry = ObsidianMirrorPlanEntry(
            record=record,
            mirror_dir=mirror_dir,
            eligible=eligible,
            reasons=reasons,
        )
        if eligible:
            for relative_path in build_file_contents(record):
                target_path = mirror_dir / relative_path
                ensure_allowed_target(target_path, mirror_dir)
                existed_before = target_path.exists()
                entry.file_actions.append(
                    ObsidianMirrorFileAction(
                        target_path=target_path,
                        backup_path=build_backup_path(target_path, backup_suffix) if existed_before else None,
                        existed_before=existed_before,
                    )
                )
        entries.append(entry)

    return ObsidianMirrorGenerationPlan(
        mode=mode,
        passport_dir=passport_dir,
        artifacts_dir=artifacts_dir,
        mirrors_dir=mirrors_dir.resolve(),
        report_path=report_path,
        entries=entries,
    )


def apply_generation_plan(plan: ObsidianMirrorGenerationPlan) -> None:
    plan.artifacts_dir.mkdir(parents=True, exist_ok=True)
    plan.mirrors_dir.mkdir(parents=True, exist_ok=True)

    for entry in plan.eligible_entries:
        entry.mirror_dir.mkdir(parents=True, exist_ok=True)
        (entry.mirror_dir / "_export").mkdir(parents=True, exist_ok=True)
        (entry.mirror_dir / "_export" / "docs").mkdir(parents=True, exist_ok=True)
        contents = build_file_contents(entry.record)

        for action in entry.file_actions:
            action.target_path.parent.mkdir(parents=True, exist_ok=True)
            if action.backup_path is not None:
                action.backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(action.target_path, action.backup_path)
                action.created_backup = True
            relative_path = action.target_path.relative_to(entry.mirror_dir)
            action.target_path.write_text(contents[str(relative_path)], encoding="utf-8")
            action.wrote_file = True


def create_generation_plan_from_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> ObsidianMirrorGenerationPlan:
    mode = parse_mode(args, parser)
    backup_suffix = args.backup_suffix or datetime.now().strftime("%Y%m%d-%H%M%S")
    artifacts_dir = resolve_artifacts_dir(args.artifacts_dir)
    passport_dir = resolve_passport_dir(args.passport_dir)
    records = load_passport_records(passport_dir)

    return build_generation_plan(
        records=records,
        mode=mode,
        passport_dir=passport_dir,
        artifacts_dir=artifacts_dir,
        report_name=args.report_name,
        include_slugs=set(args.include_slug),
        exclude_slugs=set(args.exclude_slug),
        include_categories=set(args.include_category),
        exclude_categories=set(args.exclude_category),
        backup_suffix=backup_suffix,
    )


def format_console_summary(plan: ObsidianMirrorGenerationPlan) -> str:
    return "\n".join(
        [
            f"Mode: {plan.mode}",
            f"Passport dir: {plan.passport_dir}",
            f"Artifacts dir: {plan.artifacts_dir}",
            f"Mirror proposal dir: {plan.mirrors_dir}",
            f"Eligible projects: {len(plan.eligible_entries)}",
            f"Skipped projects: {len(plan.skipped_entries)}",
            f"Planned mirror writes: {plan.planned_write_count}",
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
    write_obsidian_mirror_generation_report(plan.report_path, plan)

    print(format_console_summary(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
