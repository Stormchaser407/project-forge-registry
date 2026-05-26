"""Phase 11H.1 dry-run launcher/autostart discovery for Project Forge.

The command reads approved launcher/autostart text surfaces and writes
repository artifacts only. It never executes discovered commands or mutates
desktop entries, services, launchers, remotes, tags, or vault notes.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_REPORT_PATH = Path("artifacts/neon_command_board_launcher_discovery.md")
DEFAULT_JSON_PATH = Path("artifacts/neon_command_board_launcher_discovery.json")
PHASE = "Phase 11H.1"
MODE = "dry-run discovery"
MAX_TEXT_BYTES = 256_000
MAX_FILES_PER_DIRECTORY_TARGET = 500

SEARCH_TERMS = (
    "Project Forge",
    "project-forge",
    "Recon Command Board",
    "Recon",
    "Neon command board",
    "project-forge-dashboard",
    "project-forge-neon-command-board",
    "autostart",
    "systemd",
)

CANDIDATE_TERMS = (
    "Project Forge",
    "project-forge",
    "Recon Command Board",
    "Recon",
    "Neon command board",
    "project-forge-dashboard",
    "project-forge-neon-command-board",
)

SELF_ARTIFACT_NAMES = {
    DEFAULT_REPORT_PATH.name,
    DEFAULT_JSON_PATH.name,
}

REPO_DOC_EXTENSIONS = {".md", ".json", ".toml", ".txt", ".desktop", ".service", ".sh"}
USER_TEXT_EXTENSIONS = {
    ".desktop",
    ".service",
    ".timer",
    ".target",
    ".socket",
    ".path",
    ".conf",
    ".txt",
}


@dataclass(frozen=True, slots=True)
class DiscoveryTarget:
    key: str
    label: str
    path: Path
    kind: str
    category: str
    approved_scope: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_path(path: str | Path, *, root: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def display_path(path: Path, *, root: Path, home: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        pass
    try:
        return "~/" + str(path.relative_to(home))
    except ValueError:
        return str(path)


def safety_payload() -> dict[str, bool]:
    return {
        "dry_run_discovery": True,
        "read_only": True,
        "mutates_state": False,
        "command_execution": False,
        "autostart_replacement": False,
        "systemd_changes": False,
        "desktop_entry_changes": False,
        "vault_writes": False,
        "open_or_launch": False,
        "network_or_remotes": False,
        "tag_changes": False,
        "operator_approval_required_before_replacement": True,
    }


def default_targets(*, root: Path, home: Path) -> tuple[DiscoveryTarget, ...]:
    return (
        DiscoveryTarget(
            key="repo_scripts",
            label="repo scripts directory",
            path=root / "scripts",
            kind="directory",
            category="repo_launcher",
            approved_scope="repo-local launcher candidates",
        ),
        DiscoveryTarget(
            key="pyproject_entrypoints",
            label="pyproject.toml entrypoints",
            path=root / "pyproject.toml",
            kind="file",
            category="repo_launcher",
            approved_scope="repo-local entrypoints",
        ),
        DiscoveryTarget(
            key="repo_docs",
            label="repo docs",
            path=root / "docs",
            kind="directory",
            category="repo_reference",
            approved_scope="docs inside this repo",
        ),
        DiscoveryTarget(
            key="repo_artifacts",
            label="repo artifacts",
            path=root / "artifacts",
            kind="directory",
            category="repo_reference",
            approved_scope="artifacts inside this repo",
        ),
        DiscoveryTarget(
            key="user_autostart",
            label="user-local autostart",
            path=home / ".config" / "autostart",
            kind="directory",
            category="user_autostart",
            approved_scope="approved user-local autostart path",
        ),
        DiscoveryTarget(
            key="user_systemd",
            label="user-local systemd user services",
            path=home / ".config" / "systemd" / "user",
            kind="directory",
            category="user_systemd",
            approved_scope="approved user-local systemd path",
        ),
        DiscoveryTarget(
            key="user_applications",
            label="user-local desktop entries",
            path=home / ".local" / "share" / "applications",
            kind="directory",
            category="user_desktop_entry",
            approved_scope="approved user-local desktop application path",
        ),
    )


def is_text_candidate(path: Path, *, repo_local: bool) -> bool:
    if path.name.startswith(".") and path.suffix == "":
        return False
    if repo_local and path.parent.name == "scripts":
        return True
    extensions = REPO_DOC_EXTENSIONS if repo_local else USER_TEXT_EXTENSIONS
    return path.suffix in extensions or path.name == "pyproject.toml"


def discover_files(target: DiscoveryTarget, *, root: Path) -> tuple[list[Path], list[dict[str, Any]]]:
    skipped: list[dict[str, Any]] = []
    if not target.path.exists():
        return [], [
            {
                "target": target.key,
                "path": str(target.path),
                "reason": "missing",
            }
        ]
    if target.kind == "file":
        if not target.path.is_file():
            return [], [
                {
                    "target": target.key,
                    "path": str(target.path),
                    "reason": "not a file",
                }
            ]
        return [target.path], []
    if not target.path.is_dir():
        return [], [
            {
                "target": target.key,
                "path": str(target.path),
                "reason": "not a directory",
            }
        ]

    repo_local = target.path.resolve().is_relative_to(root.resolve())
    files: list[Path] = []
    seen: set[Path] = set()
    for path in sorted(target.path.rglob("*")):
        if len(files) >= MAX_FILES_PER_DIRECTORY_TARGET:
            skipped.append(
                {
                    "target": target.key,
                    "path": str(target.path),
                    "reason": f"file limit reached at {MAX_FILES_PER_DIRECTORY_TARGET}",
                }
            )
            break
        if not path.is_file():
            continue
        if target.key == "repo_artifacts" and path.name in SELF_ARTIFACT_NAMES:
            continue
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in seen:
            continue
        if is_text_candidate(path, repo_local=repo_local):
            files.append(path)
            seen.add(resolved)
    return files, skipped


def read_text_safely(path: Path) -> tuple[str | None, str | None]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        return None, f"stat failed: {exc}"
    if size > MAX_TEXT_BYTES:
        return None, f"larger than {MAX_TEXT_BYTES} bytes"
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, "not utf-8 text"
    except OSError as exc:
        return None, f"read failed: {exc}"


def matched_terms(text: str) -> list[str]:
    folded = text.lower()
    return [term for term in SEARCH_TERMS if term.lower() in folded]


def reference_matches(
    *,
    text: str,
    path: Path,
    target: DiscoveryTarget,
    root: Path,
    home: Path,
) -> list[dict[str, Any]]:
    references: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        folded = line.lower()
        for term in SEARCH_TERMS:
            if term.lower() in folded:
                references.append(
                    {
                        "target": target.key,
                        "category": target.category,
                        "path": display_path(path, root=root, home=home),
                        "term": term,
                        "line": line_number,
                    }
                )
    return references


def candidate_status(*, target: DiscoveryTarget, terms: list[str]) -> str:
    if target.category == "repo_reference":
        return "reference_only"
    if any(term.lower() == "recon command board" for term in terms):
        return "review_old_recon_candidate"
    if any(term.lower() == "project-forge-neon-command-board" for term in terms):
        return "review_neon_candidate"
    return "review_only"


def candidate_from_file(
    *,
    path: Path,
    text: str,
    target: DiscoveryTarget,
    root: Path,
    home: Path,
) -> dict[str, Any] | None:
    if target.category == "repo_reference":
        return None
    terms = matched_terms(text)
    candidate_terms = [term for term in terms if term in CANDIDATE_TERMS]
    if not candidate_terms:
        return None
    return {
        "category": target.category,
        "target": target.key,
        "path": display_path(path, root=root, home=home),
        "status": candidate_status(target=target, terms=candidate_terms),
        "matched_terms": candidate_terms,
    }


def warning_messages(
    *,
    skipped_targets: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> list[str]:
    warnings: list[str] = [
        "dry-run discovery only; operator approval required before replacement",
        "no mutation, no autostart replacement, no systemd changes, no desktop entry changes",
        "no vault writes, no --open, no command execution",
    ]
    for skipped in skipped_targets:
        warnings.append(f"skipped {skipped['target']}: {skipped['reason']}")
    if not candidates:
        warnings.append("no launcher/autostart candidates matched the discovery terms")
    return warnings


def collect_discovery(*, root: Path | None = None, home: Path | None = None) -> dict[str, Any]:
    root = (root or repo_root()).resolve()
    home = (home or Path.home()).resolve()
    inspected_targets: list[dict[str, Any]] = []
    skipped_targets: list[dict[str, Any]] = []
    skipped_files: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []

    for target in default_targets(root=root, home=home):
        files, skipped = discover_files(target, root=root)
        skipped_targets.extend(skipped)
        inspected_targets.append(
            {
                "key": target.key,
                "label": target.label,
                "path": display_path(target.path, root=root, home=home),
                "kind": target.kind,
                "category": target.category,
                "approved_scope": target.approved_scope,
                "exists": target.path.exists(),
                "files_read": 0,
            }
        )
        for path in files:
            text, skip_reason = read_text_safely(path)
            if skip_reason is not None:
                skipped_files.append(
                    {
                        "target": target.key,
                        "path": display_path(path, root=root, home=home),
                        "reason": skip_reason,
                    }
                )
                continue
            inspected_targets[-1]["files_read"] += 1
            assert text is not None
            candidate = candidate_from_file(path=path, text=text, target=target, root=root, home=home)
            if candidate is not None:
                candidates.append(candidate)
            references.extend(reference_matches(text=text, path=path, target=target, root=root, home=home))

    warnings = warning_messages(skipped_targets=skipped_targets, candidates=candidates)
    return {
        "phase": PHASE,
        "mode": MODE,
        "read_only": True,
        "mutates_state": False,
        "inspected_targets": inspected_targets,
        "skipped_targets": skipped_targets,
        "skipped_files": skipped_files,
        "candidates": candidates,
        "references_found": references,
        "warnings": warnings,
        "safety": safety_payload(),
    }


def candidates_by_category(discovery: dict[str, Any], category: str) -> list[dict[str, Any]]:
    return [
        candidate
        for candidate in discovery.get("candidates", [])
        if isinstance(candidate, dict) and candidate.get("category") == category
    ]


def render_candidate_list(candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return "- none found"
    lines = []
    for candidate in candidates:
        terms = ", ".join(candidate.get("matched_terms", []))
        lines.append(
            f"- `{candidate['path']}` - `{candidate['status']}`"
            f" - matched terms: {terms}"
        )
    return "\n".join(lines)


def render_references(discovery: dict[str, Any]) -> str:
    references = discovery.get("references_found", [])
    if not references:
        return "- none found"
    lines = []
    for reference in references[:80]:
        lines.append(
            f"- `{reference['path']}` line {reference['line']}: `{reference['term']}`"
        )
    remaining = len(references) - 80
    if remaining > 0:
        lines.append(f"- {remaining} additional references omitted from markdown; see JSON artifact")
    return "\n".join(lines)


def render_targets(discovery: dict[str, Any]) -> str:
    lines = []
    for target in discovery.get("inspected_targets", []):
        status = "present" if target["exists"] else "missing/skipped"
        lines.append(
            f"- `{target['path']}` - {status}; files read: `{target['files_read']}`; "
            f"scope: {target['approved_scope']}"
        )
    return "\n".join(lines)


def render_skipped(discovery: dict[str, Any]) -> str:
    skipped = list(discovery.get("skipped_targets", [])) + list(discovery.get("skipped_files", []))
    if not skipped:
        return "- none"
    return "\n".join(f"- `{item['path']}` - {item['reason']}" for item in skipped)


def render_report(discovery: dict[str, Any]) -> str:
    repo_candidates = candidates_by_category(discovery, "repo_launcher")
    autostart_candidates = candidates_by_category(discovery, "user_autostart")
    systemd_candidates = candidates_by_category(discovery, "user_systemd")
    desktop_candidates = candidates_by_category(discovery, "user_desktop_entry")
    warnings = "\n".join(f"- {warning}" for warning in discovery.get("warnings", []))

    return f"""# Neon Command Board Launcher Discovery Report

## Purpose

Phase 11H.1 adds dry-run discovery for launcher/autostart references related to
the old Recon Command Board and the new Neon command board.

## Scope

Mode: dry-run discovery. This report is read-only, performs no mutation, does
not execute discovered commands, and requires operator approval before
replacement.

## Discovery Targets Inspected

{render_targets(discovery)}

## Repo-Local Launcher Candidates

{render_candidate_list(repo_candidates)}

## User-Local Autostart Candidates

{render_candidate_list(autostart_candidates)}

## User-Local Systemd User Service Candidates

{render_candidate_list(systemd_candidates)}

## User-Local Desktop Entry Candidates

{render_candidate_list(desktop_candidates)}

## References Found

{render_references(discovery)}

## Skipped / Missing

{render_skipped(discovery)}

## Risks / Warnings

{warnings}

## Non-Goals

- no autostart replacement
- no systemd changes
- no desktop entry changes
- no vault writes
- no --open
- no command execution
- no browser, file handler, or VS Code launch
- no push, fetch, or remote contact
- no tag deletion or movement

## Safety Confirmation

This is dry-run discovery only. It is read-only, has no mutation path, performs
no autostart replacement, makes no systemd changes, makes no desktop entry
changes, performs no vault writes, runs no --open behavior, performs no command
execution, and requires operator approval before replacement.

## Recommended Next Phase

Phase 11H.2: operator-reviewed replacement plan after the exact old target and
exact Neon command board target are confirmed.
"""


def write_json(path: Path, discovery: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(discovery, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_discovery(
    *,
    root: Path | None = None,
    home: Path | None = None,
    report_path: Path = DEFAULT_REPORT_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> dict[str, Any]:
    root = (root or repo_root()).resolve()
    discovery = collect_discovery(root=root, home=home)
    report_output = resolve_repo_path(report_path, root=root)
    json_output = resolve_repo_path(json_path, root=root)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(render_report(discovery), encoding="utf-8")
    write_json(json_output, discovery)
    return discovery


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-neon-command-board-launcher-discovery")
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--json-path", default=str(DEFAULT_JSON_PATH))
    parser.add_argument(
        "--home",
        default=None,
        help="Home directory to inspect for approved user-local launcher/autostart paths.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    home = Path(args.home).expanduser().resolve() if args.home else None
    discovery = run_discovery(
        home=home,
        report_path=Path(args.report_path),
        json_path=Path(args.json_path),
    )
    print("project-forge-neon-command-board-launcher-discovery completed")
    print("mode: dry-run discovery")
    print("safety confirmation: read-only; no mutation; no command execution; no vault writes")
    print(f"report path: {resolve_repo_path(args.report_path, root=repo_root())}")
    print(f"json path: {resolve_repo_path(args.json_path, root=repo_root())}")
    print(f"targets inspected: {len(discovery['inspected_targets'])}")
    print(f"candidates found: {len(discovery['candidates'])}")
    print(f"skipped/missing targets: {len(discovery['skipped_targets'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
