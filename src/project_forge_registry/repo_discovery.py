"""Authorized Project Forge repo discovery.

This module performs explicit, read-only discovery of Git repositories under
operator-approved scan roots.

Safety policy:
- dry-run/report-only
- no external repo writes
- no content indexing
- no secret scanning
- no remotes
- no push/fetch
- no package installs
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


DEFAULT_REPORT_NAME = "repo_discovery_report.md"
DEFAULT_CSV_NAME = "repo_discovery_inventory.csv"

DEFAULT_EXCLUDED_PARTS = {
    ".cache",
    ".venv",
    "__pycache__",
    "node_modules",
    ".Trash",
    "Trash",
}

DEFAULT_EXCLUDED_ABSOLUTE_PREFIXES = (
    "/proc",
    "/sys",
    "/dev",
    "/run",
    "/nix/store",
)


@dataclass(frozen=True, slots=True)
class DiscoveredRepo:
    slug: str
    path: Path
    git_status: str
    has_readme: bool
    has_agents: bool
    has_code_workspace: bool
    has_project_forge_marker: bool
    remote_count: int
    category: str


@dataclass(frozen=True, slots=True)
class DiscoverySummary:
    scan_roots: list[Path]
    repos: list[DiscoveredRepo]
    report_path: Path
    csv_path: Path
    final_status: str


def normalize_slug(path: Path) -> str:
    return path.name.strip().replace(" ", "_").lower()


def should_exclude(path: Path, excluded_paths: list[Path] | None = None) -> bool:
    resolved = path.resolve()
    text = str(resolved)

    for prefix in DEFAULT_EXCLUDED_ABSOLUTE_PREFIXES:
        if text == prefix or text.startswith(prefix + os.sep):
            return True

    if any(part in DEFAULT_EXCLUDED_PARTS for part in resolved.parts):
        return True

    for excluded in excluded_paths or []:
        excluded_resolved = excluded.resolve()
        excluded_text = str(excluded_resolved)
        if text == excluded_text or text.startswith(excluded_text + os.sep):
            return True

    return False


def git_status(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "status", "--short"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return "unknown"
    return "dirty" if proc.stdout.strip() else "clean"


def remote_count(repo: Path) -> int:
    proc = subprocess.run(
        ["git", "-C", str(repo), "remote"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return 0
    return len([line for line in proc.stdout.splitlines() if line.strip()])


def has_readme(repo: Path) -> bool:
    return any(item.name.lower().startswith("readme") for item in repo.iterdir() if item.is_file())


def has_code_workspace(repo: Path) -> bool:
    return any(item.suffix == ".code-workspace" for item in repo.iterdir() if item.is_file())


def has_project_forge_marker(repo: Path) -> bool:
    return (repo / ".project-forge.yml").exists() or (repo / "docs" / "PROJECT_FORGE.md").exists()


def classify_repo(repo: Path, status: str, marker: bool) -> str:
    slug = normalize_slug(repo)
    lowered = str(repo).lower()

    if "cerberus" in lowered:
        return "protected_manual_review"

    if repo.name == "project-forge-registry" or slug == "project-forge-registry":
        return "control_repo"

    if marker:
        return "known_embedded"

    if status == "dirty":
        return "dirty_candidate_review_first"

    if status == "clean":
        return "clean_candidate"

    return "unknown_structure"


def inspect_repo(repo: Path) -> DiscoveredRepo:
    status = git_status(repo)
    marker = has_project_forge_marker(repo)

    return DiscoveredRepo(
        slug=normalize_slug(repo),
        path=repo.resolve(),
        git_status=status,
        has_readme=has_readme(repo),
        has_agents=(repo / "AGENTS.md").exists(),
        has_code_workspace=has_code_workspace(repo),
        has_project_forge_marker=marker,
        remote_count=remote_count(repo),
        category=classify_repo(repo, status, marker),
    )


def discover_repos(scan_roots: list[Path], excluded_paths: list[Path] | None = None) -> list[DiscoveredRepo]:
    repos: list[DiscoveredRepo] = []
    seen: set[Path] = set()

    for scan_root in scan_roots:
        root = scan_root.expanduser().resolve()
        if not root.exists() or not root.is_dir():
            continue

        for current, dirnames, _filenames in os.walk(root):
            current_path = Path(current)

            if should_exclude(current_path, excluded_paths):
                dirnames[:] = []
                continue

            if ".git" in dirnames:
                repo = current_path.resolve()
                if repo not in seen:
                    repos.append(inspect_repo(repo))
                    seen.add(repo)

                # Do not walk inside discovered repo internals.
                dirnames[:] = [name for name in dirnames if name != ".git"]
                continue

            dirnames[:] = [
                name for name in dirnames
                if not should_exclude(current_path / name, excluded_paths)
            ]

    return sorted(repos, key=lambda item: str(item.path))


def derive_final_status(repos: list[DiscoveredRepo]) -> str:
    if any(repo.category == "protected_manual_review" for repo in repos):
        return "ready_with_protected_reviews"
    if repos:
        return "ready_for_operator_review"
    return "no_repos_found"


def write_csv(csv_path: Path, repos: list[DiscoveredRepo]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "slug",
            "path",
            "git_status",
            "has_readme",
            "has_agents",
            "has_code_workspace",
            "has_project_forge_marker",
            "remote_count",
            "category",
        ])
        for repo in repos:
            writer.writerow([
                repo.slug,
                str(repo.path),
                repo.git_status,
                str(repo.has_readme).lower(),
                str(repo.has_agents).lower(),
                str(repo.has_code_workspace).lower(),
                str(repo.has_project_forge_marker).lower(),
                repo.remote_count,
                repo.category,
            ])


def write_report(report_path: Path, csv_path: Path, scan_roots: list[Path], repos: list[DiscoveredRepo]) -> str:
    final_status = derive_final_status(repos)
    categories = sorted(set(repo.category for repo in repos))

    lines: list[str] = [
        "# Project Forge Repo Discovery Report",
        "",
        "- mode: `dry-run`",
        "- authorization: `operator-provided scan roots`",
        f"- final_status: `{final_status}`",
        f"- repos_found: `{len(repos)}`",
        f"- csv: `{csv_path}`",
        "",
        "## Scan Roots",
        "",
    ]

    for scan_root in scan_roots:
        lines.append(f"- `{scan_root.expanduser().resolve()}`")

    lines.extend(["", "## Category Summary", ""])

    if categories:
        for category in categories:
            count = len([repo for repo in repos if repo.category == category])
            lines.append(f"- {category}: `{count}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Discovered Repos", ""])

    if not repos:
        lines.append("- none")
    else:
        for repo in repos:
            lines.extend([
                f"### {repo.slug}",
                "",
                f"- path: `{repo.path}`",
                f"- git_status: `{repo.git_status}`",
                f"- has_readme: `{str(repo.has_readme).lower()}`",
                f"- has_agents: `{str(repo.has_agents).lower()}`",
                f"- has_code_workspace: `{str(repo.has_code_workspace).lower()}`",
                f"- has_project_forge_marker: `{str(repo.has_project_forge_marker).lower()}`",
                f"- remote_count: `{repo.remote_count}`",
                f"- category: `{repo.category}`",
                "",
            ])

    lines.extend([
        "## Safety Statement",
        "",
        "- Discovery was dry-run/report-only.",
        "- No files were written to discovered repos.",
        "- No file content indexing was performed.",
        "- No secret scanning was performed.",
        "- No remotes were added or modified.",
        "- No push/fetch occurred.",
        "- No package installs were performed.",
        "",
    ])

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return final_status


def run_discovery(
    scan_roots: list[Path],
    excluded_paths: list[Path] | None,
    report_path: Path,
    csv_path: Path,
) -> DiscoverySummary:
    repos = discover_repos(scan_roots, excluded_paths)
    write_csv(csv_path, repos)
    final_status = write_report(report_path, csv_path, scan_roots, repos)
    return DiscoverySummary(scan_roots, repos, report_path, csv_path, final_status)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-discover-repos")
    parser.add_argument(
        "--scan-root",
        action="append",
        required=True,
        help="Operator-approved root to scan. May be provided multiple times.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Path to exclude from discovery. May be provided multiple times.",
    )
    parser.add_argument(
        "--report-name",
        default=DEFAULT_REPORT_NAME,
        help="Report filename under artifacts/.",
    )
    parser.add_argument(
        "--csv-name",
        default=DEFAULT_CSV_NAME,
        help="CSV filename under artifacts/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Discovery is always dry-run/report-only.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    scan_roots = [Path(item) for item in args.scan_root]
    excluded_paths = [Path(item) for item in args.exclude]
    report_path = Path("artifacts") / args.report_name
    csv_path = Path("artifacts") / args.csv_name

    summary = run_discovery(scan_roots, excluded_paths, report_path, csv_path)

    print("project-forge-discover-repos completed")
    print("mode: dry-run")
    print(f"repos found: {len(summary.repos)}")
    print(f"final status: {summary.final_status}")
    print(f"report written: {summary.report_path.resolve()}")
    print(f"csv written: {summary.csv_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
