"""Fast status refresh for known Project Forge repos.

This refreshes git status for repos already present in the discovery inventory.
It intentionally avoids a broad filesystem walk so dashboard refreshes stay
usable even when large source trees live under the Projects root.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path

from .repo_discovery import (
    DEFAULT_CSV_NAME,
    DEFAULT_REPORT_NAME,
    GIT_COMMAND_TIMEOUT_SECONDS,
    DiscoveredRepo,
    classify_repo,
    inspect_repo,
    write_csv,
    write_report,
)


DEFAULT_INPUT_CSV = Path("artifacts") / DEFAULT_CSV_NAME
PROJECT_ROOT_FALLBACK = Path("/run/media/cash/WD_BLACK_4TB/Cole/Projects")
PATH_PREFIX_FALLBACKS = (
    (Path("/mnt/storage/Cole/Projects"), PROJECT_ROOT_FALLBACK),
    (Path("/mnt/storage/Cole"), Path("/run/media/cash/WD_BLACK_4TB/Cole")),
)


def resolve_known_repo_path(path: Path, slug: str) -> Path:
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


def is_git_work_tree(path: Path) -> bool:
    try:
        proc = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
            timeout=GIT_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return False
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def load_known_rows(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Known repo inventory not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def missing_repo(row: dict[str, str], resolved_path: Path) -> DiscoveredRepo:
    status = "unknown"
    marker = False
    return DiscoveredRepo(
        slug=row["slug"],
        path=resolved_path,
        git_status=status,
        has_readme=False,
        has_agents=False,
        has_code_workspace=False,
        has_project_forge_marker=marker,
        remote_count=0,
        category=classify_repo(resolved_path, status, marker),
    )


def refresh_known_rows(rows: list[dict[str, str]]) -> list[DiscoveredRepo]:
    refreshed: list[DiscoveredRepo] = []
    seen: set[Path] = set()
    for row in rows:
        raw_path = Path(row["path"])
        resolved_path = resolve_known_repo_path(raw_path, row["slug"]).resolve()
        if resolved_path in seen:
            continue
        seen.add(resolved_path)

        if resolved_path.exists() and resolved_path.is_dir() and is_git_work_tree(resolved_path):
            refreshed.append(inspect_repo(resolved_path))
        else:
            refreshed.append(missing_repo(row, resolved_path))
    return sorted(refreshed, key=lambda item: str(item.path))


def run_refresh(input_csv: Path, output_csv: Path, report_path: Path) -> list[DiscoveredRepo]:
    rows = load_known_rows(input_csv)
    repos = refresh_known_rows(rows)
    write_csv(output_csv, repos)
    write_report(report_path, output_csv, [PROJECT_ROOT_FALLBACK], repos)
    return repos


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-refresh-known-repos")
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--csv-name", default=DEFAULT_CSV_NAME)
    parser.add_argument("--report-name", default=DEFAULT_REPORT_NAME)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output_csv = Path("artifacts") / args.csv_name
    report_path = Path("artifacts") / args.report_name
    repos = run_refresh(Path(args.input_csv), output_csv, report_path)
    dirty = len([repo for repo in repos if repo.git_status == "dirty"])

    print("project-forge-refresh-known-repos completed")
    print("mode: read-only known repo status refresh")
    print(f"repos refreshed: {len(repos)}")
    print(f"dirty repos: {dirty}")
    print(f"report written: {report_path.resolve()}")
    print(f"csv written: {output_csv.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
