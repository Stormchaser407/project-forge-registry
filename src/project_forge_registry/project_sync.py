from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .obsidian_mirror_generation import parse_simple_yaml

DEFAULT_PASSPORT_DIR = "artifacts/project_passports"
DEFAULT_REPORT_NAME = "project_sync_report.md"
PROTECTED_CATEGORIES = {"system_bound_project", "reconciliation_required", "unknown"}
PROTECTED_REGISTRY_ACTIONS = {"review_required"}
DEFAULT_PROFILE_LANES = {"sync_obsidian", "export_docs", "remote_plan", "remote_verify", "push_ready"}


@dataclass(frozen=True)
class LaneSpec:
    key: str
    title: str
    requested: bool
    command: list[str] | None
    report_name: str | None = None


@dataclass
class LaneResult:
    key: str
    title: str
    requested: bool
    status: str
    command: list[str] | None
    return_code: int | None
    note: str
    report_name: str | None = None


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_scoped_dir(raw_path: str | Path, description: str) -> Path:
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = repository_root() / candidate
    resolved = candidate.resolve()
    repo = repository_root().resolve()
    if resolved != repo and repo not in resolved.parents:
        raise ValueError(f"{description} must stay inside this repository")
    return resolved


def normalize_report_name(report_name: str) -> str:
    candidate = Path(report_name)
    if candidate.name != report_name or report_name in {"", ".", ".."}:
        raise ValueError("report name must be a simple filename inside artifacts directory")
    return report_name


def resolve_report_path(passport_dir: Path, report_name: str) -> Path:
    return passport_dir.resolve().parent / normalize_report_name(report_name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-sync",
        description="Phase 8.4 dry-run-only single-slug orchestrator for Project Forge lanes.",
    )
    parser.add_argument("--slug", required=True, help="Project slug to orchestrate.")
    parser.add_argument("--passport-dir", default=DEFAULT_PASSPORT_DIR, help="Passport directory.")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode. Default behavior.")
    parser.add_argument("--apply", action="store_true", help="Not available in Phase 8.4.")
    parser.add_argument("--refresh-scan", action="store_true", help="Phase 8.4 placeholder lane.")
    parser.add_argument("--refresh-workspace", action="store_true", help="Run workspace lane.")
    parser.add_argument("--refresh-passport", action="store_true", help="Run passport lane.")
    parser.add_argument("--refresh-mirror", action="store_true", help="Run mirror lane.")
    parser.add_argument("--sync-obsidian", action="store_true", help="Run Obsidian sync lane in dry-run.")
    parser.add_argument("--export-docs", action="store_true", help="Run export sync lane in dry-run.")
    parser.add_argument("--remote-plan", action="store_true", help="Run remote plan lane in dry-run.")
    parser.add_argument("--remote-verify", action="store_true", help="Run remote verify lane in dry-run.")
    parser.add_argument("--push-ready", action="store_true", help="Run push-ready lane in dry-run.")
    parser.add_argument("--allow-remote-setup", action="store_true", help="Phase 8.4: ignored in dry-run-only mode.")
    parser.add_argument("--allow-push", action="store_true", help="Phase 8.4: ignored in dry-run-only mode.")
    parser.add_argument("--stop-on-warning", action="store_true", help="Stop at first failed lane.")
    parser.add_argument("--report-name", default=DEFAULT_REPORT_NAME, help="Combined report filename.")
    parser.add_argument("--include-category", action="append", default=[], help="Future multi-project filter placeholder.")
    parser.add_argument("--exclude-category", action="append", default=[], help="Future multi-project filter placeholder.")
    return parser


def parse_mode(args: argparse.Namespace, parser: argparse.ArgumentParser) -> str:
    if args.apply and args.dry_run:
        parser.error("Use either --apply or --dry-run, not both.")
    if args.apply:
        parser.error("--apply is intentionally disabled in Phase 8.4. Use dry-run only.")
    return "dry-run"


def passport_path_for_slug(passport_dir: Path, slug: str) -> Path:
    return passport_dir / f"{slug}.project.yml"


def detect_protected_project(passport_path: Path, slug: str) -> list[str]:
    reasons: list[str] = []
    slug_lower = slug.lower()
    if slug_lower == "cerberus" or "cerberus" in slug_lower:
        reasons.append("cerberus_protected")

    if not passport_path.exists():
        reasons.append("passport_missing")
        return reasons

    payload = parse_simple_yaml(passport_path.read_text(encoding="utf-8"))
    project = payload.get("project") if isinstance(payload, dict) else None
    safety = payload.get("safety") if isinstance(payload, dict) else None
    if isinstance(safety, dict) and bool(safety.get("do_not_sync", False)):
        reasons.append("safety.do_not_sync=true")
    if isinstance(project, dict):
        category = str(project.get("category", "")).strip()
        registry_action = str(project.get("registry_action", "")).strip()
        local_path = str(project.get("local_path", "")).lower()
        if category in PROTECTED_CATEGORIES:
            reasons.append(f"classification={category}")
        if registry_action in PROTECTED_REGISTRY_ACTIONS:
            reasons.append(f"registry_action={registry_action}")
        if "cerberus" in local_path:
            reasons.append("cerberus_protected")
    return reasons


def collect_lane_flags(args: argparse.Namespace) -> dict[str, bool]:
    return {
        "refresh_scan": args.refresh_scan,
        "refresh_workspace": args.refresh_workspace,
        "refresh_passport": args.refresh_passport,
        "refresh_mirror": args.refresh_mirror,
        "sync_obsidian": args.sync_obsidian,
        "export_docs": args.export_docs,
        "remote_plan": args.remote_plan,
        "remote_verify": args.remote_verify,
        "push_ready": args.push_ready,
    }


def determine_lane_selection_mode(args: argparse.Namespace) -> str:
    if any(collect_lane_flags(args).values()):
        return "explicit"
    return "default_profile"


def build_lane_specs(args: argparse.Namespace) -> list[LaneSpec]:
    explicit_flags = collect_lane_flags(args)
    use_default_profile = determine_lane_selection_mode(args) == "default_profile"

    def requested(key: str) -> bool:
        if use_default_profile:
            return key in DEFAULT_PROFILE_LANES
        return explicit_flags[key]

    slug = args.slug

    def module_command(module_name: str, *module_args: str) -> list[str]:
        return [sys.executable, "-m", module_name, *module_args]

    def report_command(module_name: str, report_name: str, *module_args: str) -> list[str]:
        return module_command(module_name, *module_args, "--report-name", report_name)

    return [
        LaneSpec("refresh_scan", "Refresh Classification", requested("refresh_scan"), None),
        LaneSpec(
            "refresh_workspace",
            "Refresh Workspace",
            requested("refresh_workspace"),
            report_command(
                "project_forge_registry.workspace_generation",
                "project_sync_workspace_generation_report.md",
                "--dry-run",
                "--include-slug",
                slug,
            ),
            "project_sync_workspace_generation_report.md",
        ),
        LaneSpec(
            "refresh_passport",
            "Refresh Passport",
            requested("refresh_passport"),
            report_command(
                "project_forge_registry.passport_generation",
                "project_sync_passport_generation_report.md",
                "--dry-run",
                "--include-slug",
                slug,
            ),
            "project_sync_passport_generation_report.md",
        ),
        LaneSpec(
            "refresh_mirror",
            "Refresh Obsidian Mirror",
            requested("refresh_mirror"),
            report_command(
                "project_forge_registry.obsidian_mirror_generation",
                "project_sync_obsidian_mirror_generation_report.md",
                "--dry-run",
                "--include-slug",
                slug,
            ),
            "project_sync_obsidian_mirror_generation_report.md",
        ),
        LaneSpec(
            "sync_obsidian",
            "Obsidian Sync",
            requested("sync_obsidian"),
            report_command(
                "project_forge_registry.obsidian_sync",
                "project_sync_obsidian_sync_report.md",
                "--dry-run",
                "--slug",
                slug,
            ),
            "project_sync_obsidian_sync_report.md",
        ),
        LaneSpec(
            "export_docs",
            "Export Docs",
            requested("export_docs"),
            report_command(
                "project_forge_registry.export_sync",
                "project_sync_export_sync_report.md",
                "--dry-run",
                "--slug",
                slug,
            ),
            "project_sync_export_sync_report.md",
        ),
        LaneSpec(
            "remote_plan",
            "Remote Plan",
            requested("remote_plan"),
            report_command(
                "project_forge_registry.remote_policy",
                "project_sync_remote_plan_report.md",
                "plan",
                "--dry-run",
                "--slug",
                slug,
            ),
            "project_sync_remote_plan_report.md",
        ),
        LaneSpec(
            "remote_verify",
            "Remote Verify",
            requested("remote_verify"),
            report_command(
                "project_forge_registry.remote_policy",
                "project_sync_remote_verify_report.md",
                "verify",
                "--dry-run",
                "--slug",
                slug,
            ),
            "project_sync_remote_verify_report.md",
        ),
        LaneSpec(
            "push_ready",
            "Push Ready",
            requested("push_ready"),
            report_command(
                "project_forge_registry.remote_policy",
                "project_sync_push_ready_report.md",
                "push-ready",
                "--dry-run",
                "--slug",
                slug,
            ),
            "project_sync_push_ready_report.md",
        ),
    ]


def run_lane(spec: LaneSpec) -> LaneResult:
    if not spec.requested:
        return LaneResult(
            spec.key,
            spec.title,
            spec.requested,
            "skipped",
            spec.command,
            None,
            "not requested",
            spec.report_name,
        )

    if spec.command is None:
        return LaneResult(
            spec.key,
            spec.title,
            spec.requested,
            "skipped",
            spec.command,
            None,
            "phase8_4_placeholder_no_runner",
            spec.report_name,
        )

    try:
        proc = subprocess.run(spec.command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        return LaneResult(spec.key, spec.title, spec.requested, "failed", spec.command, None, str(exc), spec.report_name)
    if proc.returncode == 0:
        return LaneResult(spec.key, spec.title, spec.requested, "passed", spec.command, 0, "ok", spec.report_name)

    note = proc.stderr.strip() or proc.stdout.strip() or "lane_failed"
    return LaneResult(spec.key, spec.title, spec.requested, "failed", spec.command, proc.returncode, note, spec.report_name)


def derive_final_status(global_blocked: bool, results: list[LaneResult]) -> str:
    if global_blocked:
        return "blocked"

    requested_results = [item for item in results if item.requested]
    if any(item.status in {"failed", "blocked"} for item in requested_results):
        return "blocked"
    if any(item.status in {"skipped", "incomplete"} for item in requested_results):
        return "incomplete"
    return "ready_for_operator_review"


def write_report(
    report_path: Path,
    *,
    mode: str,
    slug: str,
    lane_selection_mode: str,
    passport_path: Path,
    protected_reasons: list[str],
    results: list[LaneResult],
    final_status: str,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# Project Sync Report (Phase 8.4)",
        "",
        f"- mode: `{mode}`",
        f"- slug: `{slug}`",
        f"- lane_selection: `{lane_selection_mode}`",
        f"- passport: `{passport_path}`",
        f"- final_status: `{final_status}`",
        "",
    ]

    if protected_reasons:
        lines.extend(
            [
                "## Global Gates",
                "",
                "Project is blocked by protection/safety gates:",
                *[f"- {reason}" for reason in protected_reasons],
                "",
            ]
        )

    requested_results = [item for item in results if item.requested]
    unrequested_results = [item for item in results if not item.requested]
    passed_results = [item for item in requested_results if item.status == "passed"]
    problem_results = [
        item for item in requested_results if item.status in {"failed", "blocked", "skipped", "incomplete"}
    ]

    lines.extend(
        [
            "## Lane Summary",
            "",
            f"- selection_note: `{'safe default dry-run profile' if lane_selection_mode == 'default_profile' else 'explicit lane flags'}`",
            f"- requested_lanes: `{len(requested_results)}`",
            f"- unrequested_skipped_lanes: `{len([item for item in unrequested_results if item.status == 'skipped'])}`",
            f"- passed_lanes: `{len(passed_results)}`",
            f"- failed_or_incomplete_lanes: `{len(problem_results)}`",
            "",
            "## Requested Lanes",
            "",
        ]
    )

    if requested_results:
        lines.extend([f"- {item.key}: `{item.status}`" for item in requested_results])
    else:
        lines.append("- none")
    lines.append("")

    lines.extend(["## Unrequested Skipped Lanes", ""])
    skipped_unrequested = [item for item in unrequested_results if item.status == "skipped"]
    if skipped_unrequested:
        lines.extend([f"- {item.key}" for item in skipped_unrequested])
    else:
        lines.append("- none")
    lines.append("")

    lines.extend(["## Passed Lanes", ""])
    if passed_results:
        lines.extend([f"- {item.key}" for item in passed_results])
    else:
        lines.append("- none")
    lines.append("")

    lines.extend(["## Failed Or Incomplete Lanes", ""])
    if problem_results:
        lines.extend([f"- {item.key}: `{item.status}` ({item.note})" for item in problem_results])
    else:
        lines.append("- none")
    lines.append("")

    lines.extend(["## Child Lane Reports", ""])
    report_results = [item for item in results if item.requested and item.report_name]
    if report_results:
        lines.extend([f"- {item.key}: `artifacts/{item.report_name}`" for item in report_results])
    else:
        lines.append("- none")
    lines.append("")

    lines.extend(["## Lane Details", ""])
    for item in results:
        command_text = " ".join(item.command) if item.command else "(none)"
        report_text = f"artifacts/{item.report_name}" if item.requested and item.report_name else "n/a"
        lines.extend(
            [
                f"### {item.title}",
                f"- key: `{item.key}`",
                f"- requested: `{str(item.requested).lower()}`",
                f"- status: `{item.status}`",
                f"- command: `{command_text}`",
                f"- child_report: `{report_text}`",
                f"- return_code: `{item.return_code if item.return_code is not None else 'n/a'}`",
                f"- note: `{item.note}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Safety Statement",
            "",
            "- Phase 8.4 is dry-run only.",
            "- No push or remote mutation actions are performed by this command.",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    mode = parse_mode(args, parser)

    passport_dir = resolve_repo_scoped_dir(args.passport_dir, "passport dir")
    report_path = resolve_report_path(passport_dir, args.report_name)
    passport_path = passport_path_for_slug(passport_dir, args.slug)

    protected_reasons = detect_protected_project(passport_path, args.slug)
    lane_selection_mode = determine_lane_selection_mode(args)
    lane_specs = build_lane_specs(args)

    results: list[LaneResult] = []
    if protected_reasons:
        for spec in lane_specs:
            results.append(
                LaneResult(
                    spec.key,
                    spec.title,
                    spec.requested,
                    "blocked",
                    spec.command,
                    None,
                    "global_gate_blocked",
                    spec.report_name,
                )
            )
    else:
        for spec in lane_specs:
            result = run_lane(spec)
            results.append(result)
            if args.stop_on_warning and result.status == "failed":
                for pending in lane_specs[len(results) :]:
                    results.append(
                        LaneResult(
                            pending.key,
                            pending.title,
                            pending.requested,
                            "blocked",
                            pending.command,
                            None,
                            "stopped_on_warning",
                            pending.report_name,
                        )
                    )
                break

    final_status = derive_final_status(bool(protected_reasons), results)
    write_report(
        report_path,
        mode=mode,
        slug=args.slug,
        lane_selection_mode=lane_selection_mode,
        passport_path=passport_path,
        protected_reasons=protected_reasons,
        results=results,
        final_status=final_status,
    )

    print(f"project-sync completed in {mode} mode for slug '{args.slug}'")
    print(f"report written: {report_path}")
    print(f"final status: {final_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
