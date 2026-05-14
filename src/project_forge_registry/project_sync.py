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


@dataclass(frozen=True)
class LaneSpec:
    key: str
    title: str
    requested: bool
    command: list[str] | None


@dataclass
class LaneResult:
    key: str
    title: str
    requested: bool
    status: str
    command: list[str] | None
    return_code: int | None
    note: str


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
        description="Phase 8.1 dry-run-only single-slug orchestrator for Project Forge lanes.",
    )
    parser.add_argument("--slug", required=True, help="Project slug to orchestrate.")
    parser.add_argument("--passport-dir", default=DEFAULT_PASSPORT_DIR, help="Passport directory.")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode. Default behavior.")
    parser.add_argument("--apply", action="store_true", help="Not available in Phase 8.1.")
    parser.add_argument("--refresh-scan", action="store_true", help="Phase 8.1 placeholder lane.")
    parser.add_argument("--refresh-workspace", action="store_true", help="Run workspace lane.")
    parser.add_argument("--refresh-passport", action="store_true", help="Run passport lane.")
    parser.add_argument("--refresh-mirror", action="store_true", help="Run mirror lane.")
    parser.add_argument("--sync-obsidian", action="store_true", help="Run Obsidian sync lane in dry-run.")
    parser.add_argument("--export-docs", action="store_true", help="Run export sync lane in dry-run.")
    parser.add_argument("--remote-plan", action="store_true", help="Run remote plan lane in dry-run.")
    parser.add_argument("--remote-verify", action="store_true", help="Run remote verify lane in dry-run.")
    parser.add_argument("--push-ready", action="store_true", help="Run push-ready lane in dry-run.")
    parser.add_argument("--allow-remote-setup", action="store_true", help="Phase 8.1: ignored in dry-run-only mode.")
    parser.add_argument("--allow-push", action="store_true", help="Phase 8.1: ignored in dry-run-only mode.")
    parser.add_argument("--stop-on-warning", action="store_true", help="Stop at first failed lane.")
    parser.add_argument("--report-name", default=DEFAULT_REPORT_NAME, help="Combined report filename.")
    parser.add_argument("--include-category", action="append", default=[], help="Future multi-project filter placeholder.")
    parser.add_argument("--exclude-category", action="append", default=[], help="Future multi-project filter placeholder.")
    return parser


def parse_mode(args: argparse.Namespace, parser: argparse.ArgumentParser) -> str:
    if args.apply and args.dry_run:
        parser.error("Use either --apply or --dry-run, not both.")
    if args.apply:
        parser.error("--apply is intentionally disabled in Phase 8.1. Use dry-run only.")
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


def build_lane_specs(args: argparse.Namespace) -> list[LaneSpec]:
    explicit_flags = {
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
    run_all_default = not any(explicit_flags.values())

    def requested(key: str) -> bool:
        return run_all_default or explicit_flags[key]

    slug = args.slug

    def module_command(module_name: str, *module_args: str) -> list[str]:
        return [sys.executable, "-m", module_name, *module_args]

    return [
        LaneSpec("refresh_scan", "Refresh Classification", requested("refresh_scan"), None),
        LaneSpec(
            "refresh_workspace",
            "Refresh Workspace",
            requested("refresh_workspace"),
            module_command("project_forge_registry.workspace_generation", "--dry-run", "--include-slug", slug),
        ),
        LaneSpec(
            "refresh_passport",
            "Refresh Passport",
            requested("refresh_passport"),
            module_command("project_forge_registry.passport_generation", "--dry-run", "--include-slug", slug),
        ),
        LaneSpec(
            "refresh_mirror",
            "Refresh Obsidian Mirror",
            requested("refresh_mirror"),
            module_command("project_forge_registry.obsidian_mirror_generation", "--dry-run", "--include-slug", slug),
        ),
        LaneSpec(
            "sync_obsidian",
            "Obsidian Sync",
            requested("sync_obsidian"),
            module_command("project_forge_registry.obsidian_sync", "--dry-run", "--slug", slug),
        ),
        LaneSpec(
            "export_docs",
            "Export Docs",
            requested("export_docs"),
            module_command("project_forge_registry.export_sync", "--dry-run", "--slug", slug),
        ),
        LaneSpec(
            "remote_plan",
            "Remote Plan",
            requested("remote_plan"),
            module_command("project_forge_registry.remote_policy", "plan", "--dry-run", "--slug", slug),
        ),
        LaneSpec(
            "remote_verify",
            "Remote Verify",
            requested("remote_verify"),
            module_command("project_forge_registry.remote_policy", "verify", "--dry-run", "--slug", slug),
        ),
        LaneSpec(
            "push_ready",
            "Push Ready",
            requested("push_ready"),
            module_command("project_forge_registry.remote_policy", "push-ready", "--dry-run", "--slug", slug),
        ),
    ]


def run_lane(spec: LaneSpec) -> LaneResult:
    if not spec.requested:
        return LaneResult(spec.key, spec.title, spec.requested, "skipped", spec.command, None, "not requested")

    if spec.command is None:
        return LaneResult(
            spec.key,
            spec.title,
            spec.requested,
            "skipped",
            spec.command,
            None,
            "phase8_1_placeholder_no_runner",
        )

    try:
        proc = subprocess.run(spec.command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        return LaneResult(spec.key, spec.title, spec.requested, "failed", spec.command, None, str(exc))
    if proc.returncode == 0:
        return LaneResult(spec.key, spec.title, spec.requested, "passed", spec.command, 0, "ok")

    note = proc.stderr.strip() or proc.stdout.strip() or "lane_failed"
    return LaneResult(spec.key, spec.title, spec.requested, "failed", spec.command, proc.returncode, note)


def derive_final_status(global_blocked: bool, results: list[LaneResult]) -> str:
    if global_blocked:
        return "blocked"
    if any(item.status == "failed" for item in results):
        return "blocked"
    if any(item.status == "skipped" and item.requested for item in results):
        return "incomplete"
    if any(item.status == "skipped" for item in results):
        return "incomplete"
    return "ready_for_operator_review"


def write_report(
    report_path: Path,
    *,
    mode: str,
    slug: str,
    passport_path: Path,
    protected_reasons: list[str],
    results: list[LaneResult],
    final_status: str,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# Project Sync Report (Phase 8.1)",
        "",
        f"- mode: `{mode}`",
        f"- slug: `{slug}`",
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

    lines.extend(["## Lanes", ""])
    for item in results:
        command_text = " ".join(item.command) if item.command else "(none)"
        lines.extend(
            [
                f"### {item.title}",
                f"- key: `{item.key}`",
                f"- requested: `{str(item.requested).lower()}`",
                f"- status: `{item.status}`",
                f"- command: `{command_text}`",
                f"- return_code: `{item.return_code if item.return_code is not None else 'n/a'}`",
                f"- note: `{item.note}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Safety Statement",
            "",
            "- Phase 8.1 is dry-run only.",
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
    lane_specs = build_lane_specs(args)

    results: list[LaneResult] = []
    if protected_reasons:
        for spec in lane_specs:
            results.append(
                LaneResult(spec.key, spec.title, spec.requested, "blocked", spec.command, None, "global_gate_blocked")
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
                        )
                    )
                break

    final_status = derive_final_status(bool(protected_reasons), results)
    write_report(
        report_path,
        mode=mode,
        slug=args.slug,
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
