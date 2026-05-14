from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .obsidian_mirror_generation import parse_simple_yaml
from .remote_models import (
    RemotePassportRecord,
    RemotePlan,
    RemotePolicyDefaults,
    RemoteState,
    RemoteVerify,
    VerificationCheck,
)
from .remote_reporting import write_remote_plan_report, write_remote_verify_report

DEFAULT_PASSPORT_DIR = "artifacts/project_passports"
DEFAULT_PLAN_REPORT_NAME = "remote_plan_report.md"
DEFAULT_VERIFY_REPORT_NAME = "remote_verify_report.md"
ELIGIBLE_CATEGORIES = {"active_project", "operated_tool"}
PROTECTED_CATEGORIES = {"system_bound_project", "reconciliation_required", "unknown"}
PROTECTED_REGISTRY_ACTIONS = {"review_required"}


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
        prog="project-forge-remote-policy",
        description="Local-only remote policy planner/verifier for Project Forge.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="Plan remote policy defaults and eligibility.")
    plan.add_argument("--slug", required=True, help="Project slug to inspect.")
    plan.add_argument("--passport-dir", default=DEFAULT_PASSPORT_DIR, help="Passport directory.")
    plan.add_argument("--report-name", default=DEFAULT_PLAN_REPORT_NAME, help="Plan report filename.")
    plan.add_argument("--dry-run", action="store_true", help="Dry-run mode (default behavior).")

    verify = subparsers.add_parser("verify", help="Verify local repo state and remote readiness.")
    verify.add_argument("--slug", required=True, help="Project slug to inspect.")
    verify.add_argument("--passport-dir", default=DEFAULT_PASSPORT_DIR, help="Passport directory.")
    verify.add_argument("--require-clean-tree", action="store_true", help="Require clean working tree.")
    verify.add_argument("--require-tests-pass", action="store_true", help="Require tests-pass check (Phase 7: not yet implemented).")
    verify.add_argument(
        "--require-doc-reports-current",
        action="store_true",
        help="Require docs-report freshness check (Phase 7: not yet implemented).",
    )
    verify.add_argument("--report-name", default=DEFAULT_VERIFY_REPORT_NAME, help="Verify report filename.")
    verify.add_argument("--dry-run", action="store_true", help="Dry-run mode (default behavior).")
    return parser


def load_passport_record(passport_dir: Path, slug: str) -> RemotePassportRecord:
    passport_path = passport_dir / f"{slug}.project.yml"
    if not passport_path.exists():
        raise ValueError(f"passport file not found for slug '{slug}': {passport_path}")

    payload = parse_simple_yaml(passport_path.read_text(encoding="utf-8"))
    project = payload.get("project")
    sync = payload.get("sync")
    safety = payload.get("safety")
    git_block = payload.get("git")
    visibility = payload.get("visibility")
    if not all(isinstance(section, dict) for section in (project, sync, safety, git_block, visibility)):
        raise ValueError(f"passport file is missing required sections: {passport_path}")

    record_slug = str(project.get("slug", "")).strip()
    if record_slug != slug:
        raise ValueError(f"passport slug mismatch: expected '{slug}', found '{record_slug}'")

    required_values = {
        "name": project.get("name"),
        "category": project.get("category"),
        "status": project.get("status"),
        "local_path": project.get("local_path"),
    }
    if any(not isinstance(value, str) or not value.strip() for value in required_values.values()):
        raise ValueError(f"passport file has missing required string fields: {passport_path}")

    return RemotePassportRecord(
        slug=slug,
        name=str(required_values["name"]).strip(),
        category=str(required_values["category"]).strip(),
        status=str(required_values["status"]).strip(),
        registry_action=str(project.get("registry_action", "")).strip(),
        local_path=Path(str(required_values["local_path"]).strip()).expanduser().resolve(),
        default_branch=str(git_block.get("default_branch", "main")).strip() or "main",
        visibility_github=str(visibility.get("github", "private")).strip() or "private",
        visibility_codeberg=str(visibility.get("codeberg", "private")).strip() or "private",
        allow_code_to_obsidian=bool(sync.get("allow_code_to_obsidian", False)),
        allow_secrets=bool(sync.get("allow_secrets", False)),
        do_not_sync=bool(safety.get("do_not_sync", False)),
        passport_path=passport_path,
    )


def determine_policy_status(record: RemotePassportRecord) -> tuple[bool, str, list[str]]:
    reasons: list[str] = []
    slug_lower = record.slug.lower()
    local_lower = str(record.local_path).lower()

    if record.do_not_sync:
        reasons.append("safety.do_not_sync=true")
    if record.allow_code_to_obsidian:
        reasons.append("sync.allow_code_to_obsidian=true")
    if record.allow_secrets:
        reasons.append("sync.allow_secrets=true")
    if slug_lower == "cerberus" or "cerberus" in slug_lower or "cerberus" in local_lower:
        reasons.append("cerberus_protected")
    if record.category in PROTECTED_CATEGORIES:
        reasons.append(f"classification={record.category}")
    if record.registry_action in PROTECTED_REGISTRY_ACTIONS:
        reasons.append(f"registry_action={record.registry_action}")
    if record.category not in ELIGIBLE_CATEGORIES:
        reasons.append(f"classification={record.category}_not_eligible_by_default")

    hard_blockers = [
        item
        for item in reasons
        if item.startswith("safety.")
        or item.startswith("sync.")
        or item == "cerberus_protected"
        or item.startswith("classification=")
        or item.startswith("registry_action=")
    ]
    if hard_blockers:
        return False, "blocked", reasons

    if record.status == "review":
        reasons.append("operator_approval_required")
        return True, "needs_approval", reasons

    return True, "eligible", reasons


def run_git(repo_path: Path, args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(repo_path), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def read_remote_state(record: RemotePassportRecord, require_clean_tree: bool) -> RemoteState:
    if not record.local_path.exists():
        return RemoteState(
            inside_git_repo=False,
            current_branch=None,
            remotes=[],
            clean_working_tree=None,
            clean_working_tree_lines=[],
        )

    code, out, _err = run_git(record.local_path, ["rev-parse", "--is-inside-work-tree"])
    inside = code == 0 and out == "true"
    if not inside:
        return RemoteState(
            inside_git_repo=False,
            current_branch=None,
            remotes=[],
            clean_working_tree=None,
            clean_working_tree_lines=[],
        )

    _, branch, _ = run_git(record.local_path, ["branch", "--show-current"])
    _, remotes_raw, _ = run_git(record.local_path, ["remote", "-v"])
    remotes: list[tuple[str, str, str]] = []
    for line in remotes_raw.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            name = parts[0]
            url = parts[1]
            direction = parts[2].strip("()")
            remotes.append((name, url, direction))

    clean_state: bool | None = None
    clean_lines: list[str] = []
    if require_clean_tree:
        _, status_out, _ = run_git(record.local_path, ["status", "--short"])
        clean_lines = [line for line in status_out.splitlines() if line.strip()]
        clean_state = len(clean_lines) == 0

    return RemoteState(
        inside_git_repo=True,
        current_branch=branch if branch else None,
        remotes=remotes,
        clean_working_tree=clean_state,
        clean_working_tree_lines=clean_lines,
    )


def build_plan(args: argparse.Namespace) -> RemotePlan:
    passport_dir = resolve_repo_scoped_dir(args.passport_dir, "passport dir")
    record = load_passport_record(passport_dir, args.slug)
    eligible, policy_status, reasons = determine_policy_status(record)
    defaults = RemotePolicyDefaults()

    if record.default_branch != defaults.default_branch:
        reasons.append(f"passport_default_branch={record.default_branch}")
    if record.visibility_github != defaults.github_visibility:
        reasons.append(f"passport_github_visibility={record.visibility_github}")
    if record.visibility_codeberg != defaults.codeberg_visibility:
        reasons.append(f"passport_codeberg_visibility={record.visibility_codeberg}")

    return RemotePlan(
        mode="dry-run",
        slug=args.slug,
        passport_dir=passport_dir,
        report_path=resolve_report_path(passport_dir, args.report_name),
        record=record,
        defaults=defaults,
        eligible=eligible,
        policy_status=policy_status,
        reasons=reasons,
    )


def build_verify(args: argparse.Namespace) -> RemoteVerify:
    passport_dir = resolve_repo_scoped_dir(args.passport_dir, "passport dir")
    record = load_passport_record(passport_dir, args.slug)
    eligible, policy_status, reasons = determine_policy_status(record)
    defaults = RemotePolicyDefaults()
    remote_state = read_remote_state(record, args.require_clean_tree)

    checks: list[VerificationCheck] = []
    checks.append(
        VerificationCheck(
            name="local_git_repository_detected",
            required=True,
            passed=remote_state.inside_git_repo,
            detail="local path is a git repository" if remote_state.inside_git_repo else "local path is not a git repository",
        )
    )
    checks.append(
        VerificationCheck(
            name="working_tree_clean",
            required=args.require_clean_tree,
            passed=(remote_state.clean_working_tree is True) if args.require_clean_tree else True,
            detail=(
                "clean"
                if remote_state.clean_working_tree is True
                else "dirty or not checked"
            ),
        )
    )
    checks.append(
        VerificationCheck(
            name="tests_pass_check",
            required=args.require_tests_pass,
            passed=not args.require_tests_pass,
            detail="pending Phase 7b/8 implementation",
        )
    )
    checks.append(
        VerificationCheck(
            name="docs_reports_current_check",
            required=args.require_doc_reports_current,
            passed=not args.require_doc_reports_current,
            detail="pending Phase 7b/8 implementation",
        )
    )

    if record.default_branch != defaults.default_branch:
        reasons.append(f"passport_default_branch={record.default_branch}")

    return RemoteVerify(
        mode="dry-run",
        slug=args.slug,
        passport_dir=passport_dir,
        report_path=resolve_report_path(passport_dir, args.report_name),
        record=record,
        defaults=defaults,
        eligible=eligible,
        policy_status=policy_status,
        reasons=reasons,
        remote_state=remote_state,
        checks=checks,
    )


def run_plan(args: argparse.Namespace) -> int:
    plan = build_plan(args)
    plan.report_path.parent.mkdir(parents=True, exist_ok=True)
    write_remote_plan_report(plan.report_path, plan)
    print(
        "\n".join(
            [
                f"Mode: {plan.mode}",
                f"Slug: {plan.slug}",
                f"Eligible: {str(plan.eligible).lower()}",
                f"Policy status: {plan.policy_status}",
                f"Default branch policy: {plan.defaults.default_branch}",
                f"GitHub remote policy name: {plan.defaults.github_remote_name}",
                f"Codeberg remote policy name: {plan.defaults.codeberg_remote_name}",
                f"Report: {plan.report_path}",
            ]
        )
    )
    return 0


def run_verify(args: argparse.Namespace) -> int:
    verify = build_verify(args)
    verify.report_path.parent.mkdir(parents=True, exist_ok=True)
    write_remote_verify_report(verify.report_path, verify)
    print(
        "\n".join(
            [
                f"Mode: {verify.mode}",
                f"Slug: {verify.slug}",
                f"Eligible: {str(verify.eligible).lower()}",
                f"Policy status: {verify.policy_status}",
                f"Inside git repo: {str(verify.remote_state.inside_git_repo).lower()}",
                f"Current branch: {verify.remote_state.current_branch or 'unknown'}",
                f"Remotes found: {len(verify.remote_state.remotes)}",
                f"Report: {verify.report_path}",
            ]
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "plan":
        return run_plan(args)
    if args.command == "verify":
        return run_verify(args)
    parser.error(f"unknown command: {args.command}")
    return 2


def main_plan() -> int:
    return main(["plan", *sys.argv[1:]])


def main_verify() -> int:
    return main(["verify", *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
