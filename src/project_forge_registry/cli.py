from __future__ import annotations

import argparse
from pathlib import Path

from .reporting import (
    ensure_artifact_dir,
    write_command_board,
    write_json_report,
    write_markdown_report,
    write_registry_yaml,
)
from .scanner import scan_roots as scan_projects

DEFAULT_SCAN_ROOTS = [
    Path("/mnt/storage/Cole/Projects"),
    Path("/home/cole/Projects"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-forge-registry",
        description="Dry-run scanner for local project discovery and registry proposals.",
    )
    parser.add_argument(
        "--scan-root",
        action="append",
        dest="scan_roots",
        help="Override or extend scan roots. Repeat to provide multiple roots.",
    )
    parser.add_argument(
        "--artifacts-dir",
        default="artifacts",
        help="Directory where reports will be written.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit for the number of first-level project folders to scan.",
    )
    return parser


def resolve_scan_roots(raw_roots: list[str] | None) -> list[Path]:
    if raw_roots:
        return [Path(item).expanduser() for item in raw_roots]
    return DEFAULT_SCAN_ROOTS.copy()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    scan_roots = resolve_scan_roots(args.scan_roots)
    results = scan_roots_and_limit(scan_roots, args.limit)

    artifacts_dir = Path(args.artifacts_dir)
    ensure_artifact_dir(artifacts_dir)

    scan_root_strings = [str(path) for path in scan_roots]
    write_markdown_report(artifacts_dir / "project_scan_report.md", results, scan_root_strings)
    write_json_report(artifacts_dir / "project_scan_report.json", results, scan_root_strings)
    write_registry_yaml(artifacts_dir / "projects_proposed.yml", results)
    write_command_board(artifacts_dir / "PROJECT_COMMAND_BOARD_DRAFT.md", results)

    print(f"Scanned {len(results)} project folders.")
    print(f"Artifacts written to {artifacts_dir.resolve()}")
    return 0


def scan_roots_and_limit(scan_root_paths: list[Path], limit: int | None) -> list:
    results = scan_projects(scan_root_paths)
    if limit is not None:
        return results[:limit]
    return results


if __name__ == "__main__":
    raise SystemExit(main())
