"""Guarded project review helpers for dashboard amber repos."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .path_policy import is_protected_filesystem_path

DEFAULT_INVENTORY_JSON = Path("artifacts/dashboard_inventory.json")
SENSITIVE_FRAGMENTS = (
    ".env",
    "secret",
    "secrets",
    "token",
    "credential",
    "credentials",
    ".pem",
    ".key",
    ".p12",
    ".sqlite",
    ".sqlite3",
    ".db",
)
PROJECT_ROOT_FALLBACK = Path("/run/media/cash/WD_BLACK_4TB/Cole/Projects")
PATH_PREFIX_FALLBACKS = (
    (Path("/mnt/storage/Cole/Projects"), PROJECT_ROOT_FALLBACK),
    (Path("/mnt/storage/Cole"), Path("/run/media/cash/WD_BLACK_4TB/Cole")),
)


@dataclass(frozen=True, slots=True)
class ReviewProject:
    slug: str
    path: Path
    category: str
    git_status: str
    recommended_action: str


def resolve_project_path(path: Path, slug: str) -> Path:
    if is_protected_filesystem_path(path):
        raise ValueError("Review is blocked for an exact protected filesystem path")
    if path.exists():
        return path

    for old_prefix, new_prefix in PATH_PREFIX_FALLBACKS:
        try:
            relative = path.relative_to(old_prefix)
        except ValueError:
            continue
        candidate = new_prefix / relative
        if candidate.exists():
            return candidate

    if PROJECT_ROOT_FALLBACK.exists():
        for name in (path.name, slug):
            candidate = PROJECT_ROOT_FALLBACK / name
            if candidate.exists():
                return candidate
    return path


def load_project(inventory_json: Path, slug: str) -> ReviewProject:
    if not inventory_json.exists():
        raise FileNotFoundError(f"Dashboard inventory JSON not found: {inventory_json}")

    payload = json.loads(inventory_json.read_text(encoding="utf-8"))
    projects = payload.get("projects")
    if not isinstance(projects, list):
        raise ValueError("Dashboard inventory JSON is missing a projects list")

    matches = [item for item in projects if isinstance(item, dict) and item.get("slug") == slug]
    if not matches:
        raise ValueError(f"Unknown project slug: {slug}")
    if len(matches) != 1:
        raise ValueError(f"Ambiguous project slug: {slug}")

    project = matches[0]
    raw_path = Path(str(project.get("path") or ""))
    return ReviewProject(
        slug=slug,
        path=resolve_project_path(raw_path, slug),
        category=str(project.get("category") or "unknown"),
        git_status=str(project.get("git_status") or "unknown"),
        recommended_action=str(project.get("recommended_action") or "unknown_review"),
    )


def git_text(repo: Path, args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def ensure_git_repo(project: ReviewProject) -> None:
    if not project.path.exists() or not project.path.is_dir():
        raise ValueError(f"Project path is not a directory: {project.path}")
    proc = git_text(project.path, ["rev-parse", "--is-inside-work-tree"])
    if proc.returncode != 0 or proc.stdout.strip() != "true":
        raise ValueError(f"Project path is not a git work tree: {project.path}")


def status_lines(project: ReviewProject) -> list[str]:
    proc = git_text(project.path, ["status", "--short", "--branch"], check=True)
    return proc.stdout.splitlines()


def changed_paths(project: ReviewProject) -> list[str]:
    proc = git_text(project.path, ["status", "--porcelain"], check=True)
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if not line:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        paths.append(path)
    return paths


def sensitive_paths(paths: list[str]) -> list[str]:
    flagged = []
    for path in paths:
        lowered = path.lower()
        if any(fragment in lowered for fragment in SENSITIVE_FRAGMENTS):
            flagged.append(path)
    return flagged


def render_header(project: ReviewProject, mode: str) -> list[str]:
    return [
        "============================================================",
        " PROJECT FORGE REVIEW PROJECT",
        "============================================================",
        f"Mode: {mode}",
        f"Slug: {project.slug}",
        f"Category: {project.category}",
        f"Git status: {project.git_status}",
        f"Recommended action: {project.recommended_action}",
        f"Project path: {project.path}",
        "",
    ]


def render_status(project: ReviewProject) -> str:
    lines = render_header(project, "status")
    lines.extend(["Git status:", ""])
    lines.extend(status_lines(project) or ["clean"])
    return "\n".join(lines) + "\n"


def render_diff(project: ReviewProject, full: bool = False) -> str:
    lines = render_header(project, "diff")
    stat = git_text(project.path, ["diff", "--stat"], check=True).stdout.strip()
    names = git_text(project.path, ["diff", "--name-status"], check=True).stdout.strip()
    staged_names = git_text(project.path, ["diff", "--cached", "--name-status"], check=True).stdout.strip()
    lines.extend(["Unstaged diff stat:", "", stat or "No unstaged diff.", ""])
    lines.extend(["Unstaged changed files:", "", names or "No unstaged changed files.", ""])
    lines.extend(["Staged changed files:", "", staged_names or "No staged changed files.", ""])
    if full:
        diff = git_text(project.path, ["diff"], check=True).stdout.strip()
        lines.extend(["Full unstaged diff:", "", diff or "No unstaged diff.", ""])
    return "\n".join(lines) + "\n"


def render_log(project: ReviewProject) -> str:
    lines = render_header(project, "log")
    proc = git_text(project.path, ["log", "-5", "--oneline", "--decorate"], check=True)
    lines.extend(["Recent commits:", "", proc.stdout.strip() or "No commits found."])
    return "\n".join(lines) + "\n"


def render_commit_preflight(project: ReviewProject) -> str:
    paths = changed_paths(project)
    flagged = sensitive_paths(paths)
    lines = render_header(project, "commit-dry-run")
    lines.extend(
        [
            "Commit preflight only. No files were staged and no commit was created.",
            "",
            "Changed paths:",
            "",
        ]
    )
    lines.extend([f"- {path}" for path in paths] or ["- none"])
    lines.extend(["", "Sensitive path flags:", ""])
    lines.extend([f"- {path}" for path in flagged] or ["- none"])
    lines.extend(
        [
            "",
            "Commit guard:",
            "",
            "- requires --commit",
            "- requires --message",
            "- requires --confirm-slug matching the selected slug",
            "- requires --yes-commit-reviewed",
            "- refuses untracked files unless --include-untracked and --yes-include-untracked are both present",
            "- refuses sensitive-looking paths unless --allow-sensitive-paths is present",
            "",
        ]
    )
    return "\n".join(lines)


def run_commit(
    project: ReviewProject,
    message: str,
    confirm_slug: str,
    yes_commit_reviewed: bool,
    include_untracked: bool,
    yes_include_untracked: bool,
    allow_sensitive_paths: bool,
) -> str:
    if project.category in {"protected_manual_review", "control_repo"}:
        raise ValueError(f"Commit automation is blocked for category: {project.category}")
    if project.recommended_action != "dirty_review_first":
        raise ValueError("Commit automation is available only for dirty-review projects")
    if confirm_slug != project.slug:
        raise ValueError("--confirm-slug must exactly match --slug")
    if not yes_commit_reviewed:
        raise ValueError("--yes-commit-reviewed is required for commit")
    if not message.strip():
        raise ValueError("--message is required for commit")

    paths = changed_paths(project)
    if not paths:
        raise ValueError("No changed paths to commit")

    untracked = [path for path in status_lines(project) if path.startswith("?? ")]
    if untracked and not (include_untracked and yes_include_untracked):
        raise ValueError(
            "Untracked files are present; rerun with --include-untracked and "
            "--yes-include-untracked only after reviewing them"
        )

    flagged = sensitive_paths(paths)
    if flagged and not allow_sensitive_paths:
        raise ValueError(
            "Sensitive-looking paths are present; rerun with --allow-sensitive-paths "
            "only after manual review"
        )

    add_args = ["add", "-A"] if include_untracked else ["add", "-u"]
    git_text(project.path, add_args, check=True)
    git_text(project.path, ["commit", "-m", message], check=True)

    lines = render_header(project, "commit")
    lines.extend(["Commit created.", "", "Post-commit status:", ""])
    lines.extend(status_lines(project) or ["clean"])
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-review-project")
    parser.add_argument("--inventory-json", default=str(DEFAULT_INVENTORY_JSON))
    parser.add_argument("--slug", required=True)
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--diff", action="store_true")
    parser.add_argument("--full-diff", action="store_true")
    parser.add_argument("--log", action="store_true")
    parser.add_argument("--commit-dry-run", action="store_true")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--message", default="")
    parser.add_argument("--confirm-slug", default="")
    parser.add_argument("--yes-commit-reviewed", action="store_true")
    parser.add_argument("--include-untracked", action="store_true")
    parser.add_argument("--yes-include-untracked", action="store_true")
    parser.add_argument("--allow-sensitive-paths", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    selected_modes = [
        bool(args.status),
        bool(args.diff),
        bool(args.log),
        bool(args.commit_dry_run),
        bool(args.commit),
    ]
    if sum(selected_modes) != 1:
        parser.error("select exactly one mode: --status, --diff, --log, --commit-dry-run, or --commit")

    try:
        project = load_project(Path(args.inventory_json), args.slug)
        ensure_git_repo(project)
        if args.status:
            print(render_status(project), end="")
        elif args.diff:
            print(render_diff(project, full=bool(args.full_diff)), end="")
        elif args.log:
            print(render_log(project), end="")
        elif args.commit_dry_run:
            print(render_commit_preflight(project))
        elif args.commit:
            print(
                run_commit(
                    project=project,
                    message=args.message,
                    confirm_slug=args.confirm_slug,
                    yes_commit_reviewed=bool(args.yes_commit_reviewed),
                    include_untracked=bool(args.include_untracked),
                    yes_include_untracked=bool(args.yes_include_untracked),
                    allow_sensitive_paths=bool(args.allow_sensitive_paths),
                ),
                end="",
            )
    except (FileNotFoundError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
