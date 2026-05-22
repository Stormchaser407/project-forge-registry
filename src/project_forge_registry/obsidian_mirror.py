"""Phase 11A dry-run Obsidian artifact mirror for Project Forge.

This module converts existing Project Forge state into deterministic
Obsidian-ready Markdown under this repository's artifacts directory.

Safety policy:
- no real Obsidian vault writes
- no external repo writes
- no apply mode
- no remotes
- no push/fetch
- no package installs
- no network calls
- no VS Code launch
- no Codex login or auth handling
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_DASHBOARD_INVENTORY = Path("artifacts/dashboard_inventory.json")
DEFAULT_REPO_DISCOVERY_CSV = Path("artifacts/repo_discovery_inventory.csv")
DEFAULT_PHASE_10_REPORT = Path("artifacts/phase_10_closeout_report.md")
DEFAULT_PHASE_10_DOC = Path("docs/PROJECT_FORGE_PHASE_10_CLOSEOUT.md")
DEFAULT_OPERATOR_RELEASE_NOTES = Path("docs/PROJECT_FORGE_OPERATOR_RELEASE_NOTES.md")
DEFAULT_CHANGELOG = Path("CHANGELOG.md")
DEFAULT_OUTPUT_DIR = Path("artifacts/obsidian_mirror")
DEFAULT_REPORT_PATH = Path("artifacts/obsidian_mirror_report.md")
DEFAULT_MANIFEST_PATH = Path("artifacts/obsidian_mirror_manifest.json")

NOTE_FILENAMES = {
    "command_center": "Project Forge - Command Center.md",
    "dashboard_summary": "Project Forge - Dashboard Summary.md",
    "known_embedded": "Project Forge - Known Embedded Repos.md",
    "deferred_items": "Project Forge - Deferred Items.md",
    "phase_11_planning": "Project Forge - Phase 11 Planning.md",
}

COMMON_TAGS = ["project-forge", "phase-11", "command-center", "dry-run"]
DEFERRED_ITEMS = [
    "Codex Personal/Business isolation",
    "real vault write/apply",
    "remote strategy",
    "repo action policy layer",
]
SAFETY_STATEMENTS = [
    "no real Obsidian vault writes",
    "no external repo writes",
    "no apply",
    "no remotes",
    "no push/fetch",
    "no package installs",
    "no network calls",
    "no VS Code launch",
    "no Codex login/auth handling",
]
SOURCE_ARTIFACTS = [
    DEFAULT_DASHBOARD_INVENTORY,
    Path("artifacts/dashboard_inventory_report.md"),
    DEFAULT_REPO_DISCOVERY_CSV,
    DEFAULT_PHASE_10_REPORT,
    DEFAULT_PHASE_10_DOC,
    DEFAULT_OPERATOR_RELEASE_NOTES,
    DEFAULT_CHANGELOG,
]


@dataclass(frozen=True, slots=True)
class ProjectSummary:
    slug: str
    path: str
    category: str
    git_status: str
    recommended_action: str
    launch_policy_status: str


@dataclass(frozen=True, slots=True)
class MirrorState:
    total_projects: int
    known_embedded_count: int
    dirty_review_count: int
    protected_review_count: int
    candidate_review_count: int
    known_embedded_projects: tuple[ProjectSummary, ...]
    category_counts: dict[str, int]
    source_artifacts_used: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MirrorResult:
    output_dir: Path
    report_path: Path
    manifest_path: Path
    note_paths: tuple[Path, ...]
    state: MirrorState


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_path(path: str | Path, *, must_exist: bool = False) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = repository_root() / candidate
    candidate = candidate.resolve()
    repo_root = repository_root().resolve()
    if candidate != repo_root and repo_root not in candidate.parents:
        raise ValueError(f"path must stay inside Project Forge repository: {path}")
    if must_exist and not candidate.exists():
        raise FileNotFoundError(f"Required input not found: {candidate}")
    return candidate


def relative_to_repo(path: Path) -> str:
    return str(path.resolve().relative_to(repository_root().resolve()))


def load_dashboard_inventory(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required dashboard inventory not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("dashboard inventory must be a JSON object")
    if not isinstance(payload.get("summary"), dict):
        raise ValueError("dashboard inventory is missing summary object")
    if not isinstance(payload.get("projects"), list):
        raise ValueError("dashboard inventory is missing projects list")
    return payload


def available_sources(paths: list[Path]) -> tuple[str, ...]:
    found: list[str] = []
    for path in paths:
        resolved = resolve_repo_path(path)
        if resolved.exists():
            found.append(relative_to_repo(resolved))
    return tuple(found)


def build_state(inventory: dict[str, Any], source_paths: list[Path]) -> MirrorState:
    summary = inventory["summary"]
    projects = inventory["projects"]
    category_counts = dict(sorted((summary.get("count_by_category") or {}).items()))

    known_projects: list[ProjectSummary] = []
    for project in projects:
        if not isinstance(project, dict):
            continue
        if project.get("category") != "known_embedded":
            continue
        launch_policy = project.get("launch_policy") if isinstance(project.get("launch_policy"), dict) else {}
        known_projects.append(
            ProjectSummary(
                slug=str(project.get("slug", "")),
                path=str(project.get("path", "")),
                category=str(project.get("category", "")),
                git_status=str(project.get("git_status", "")),
                recommended_action=str(project.get("recommended_action", "")),
                launch_policy_status=str(launch_policy.get("status", "")),
            )
        )

    known_projects.sort(key=lambda item: item.slug)

    return MirrorState(
        total_projects=int(summary.get("total_projects", len(projects))),
        known_embedded_count=int(summary.get("known_embedded_count", len(known_projects))),
        dirty_review_count=int(summary.get("dirty_review_count", 0)),
        protected_review_count=int(summary.get("protected_review_count", 0)),
        candidate_review_count=int(category_counts.get("clean_candidate", 0)),
        known_embedded_projects=tuple(known_projects),
        category_counts=category_counts,
        source_artifacts_used=available_sources(source_paths),
    )


def frontmatter(title: str, tags: list[str] | None = None) -> str:
    note_tags = tags or COMMON_TAGS
    lines = [
        "---",
        f'title: "{title}"',
        'project: "Project Forge"',
        'status: "dry-run artifact"',
        "tags:",
        *(f"  - {tag}" for tag in note_tags),
        "---",
    ]
    return "\n".join(lines)


def render_command_center(state: MirrorState) -> str:
    return "\n".join(
        [
            frontmatter("Project Forge - Command Center"),
            "",
            "# Project Forge - Command Center",
            "",
            "Project Forge is a dry-run-first local command center. This Phase 11A mirror is generated under repository artifacts only.",
            "",
            "## Navigation",
            "",
            "- [[Project Forge - Dashboard Summary]]",
            "- [[Project Forge - Known Embedded Repos]]",
            "- [[Project Forge - Deferred Items]]",
            "- [[Project Forge - Phase 11 Planning]]",
            "",
            "## Operator Quick Start",
            "",
            "```bash",
            "./scripts/project-forge-cold-start",
            "./scripts/project-forge-dashboard --no-open",
            "./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --dry-run",
            "```",
            "",
            "## Dashboard",
            "",
            "- artifact: `artifacts/dashboard.html`",
            f"- total projects: `{state.total_projects}`",
            f"- known embedded repos: `{state.known_embedded_count}`",
            "",
            "## Safety",
            "",
            *[f"- {item}" for item in SAFETY_STATEMENTS],
            "",
        ]
    )


def render_dashboard_summary(state: MirrorState) -> str:
    lines = [
        frontmatter("Project Forge - Dashboard Summary"),
        "",
        "# Project Forge - Dashboard Summary",
        "",
        "Back to [[Project Forge - Command Center]].",
        "",
        "## Counts",
        "",
        f"- total projects: `{state.total_projects}`",
        f"- known embedded repos: `{state.known_embedded_count}`",
        f"- candidate review repos: `{state.candidate_review_count}`",
        f"- dirty review repos: `{state.dirty_review_count}`",
        f"- protected review repos: `{state.protected_review_count}`",
        "",
        "## Category Summary",
        "",
    ]
    if state.category_counts:
        lines.extend(f"- {category}: `{count}`" for category, count in state.category_counts.items())
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Related Notes",
            "",
            "- [[Project Forge - Known Embedded Repos]]",
            "- [[Project Forge - Deferred Items]]",
            "",
        ]
    )
    return "\n".join(lines)


def render_known_embedded(state: MirrorState) -> str:
    lines = [
        frontmatter("Project Forge - Known Embedded Repos"),
        "",
        "# Project Forge - Known Embedded Repos",
        "",
        "Back to [[Project Forge - Command Center]]. See also [[Project Forge - Dashboard Summary]].",
        "",
        "## Repos",
        "",
    ]
    if state.known_embedded_projects:
        for project in state.known_embedded_projects:
            lines.extend(
                [
                    f"### {project.slug}",
                    "",
                    f"- path: `{project.path}`",
                    f"- category: `{project.category}`",
                    f"- git status: `{project.git_status}`",
                    f"- recommended action: `{project.recommended_action}`",
                    f"- launch policy: `{project.launch_policy_status}`",
                    "",
                ]
            )
    else:
        lines.extend(["- none", ""])
    return "\n".join(lines)


def render_deferred_items(_: MirrorState) -> str:
    return "\n".join(
        [
            frontmatter("Project Forge - Deferred Items"),
            "",
            "# Project Forge - Deferred Items",
            "",
            "Back to [[Project Forge - Command Center]].",
            "",
            "## Deferred",
            "",
            *[f"- {item}" for item in DEFERRED_ITEMS],
            "",
            "## Notes",
            "",
            "- Codex Personal/Business isolation needs dedicated VS Code and extension behavior research.",
            "- Real vault writes remain deferred until an explicit apply/sync phase.",
            "- Remote strategy remains policy work until explicitly approved.",
            "- Repo action policy should be designed before any executable dashboard actions.",
            "",
            "Related: [[Project Forge - Phase 11 Planning]]",
            "",
        ]
    )


def render_phase_11_planning(_: MirrorState) -> str:
    return "\n".join(
        [
            frontmatter("Project Forge - Phase 11 Planning"),
            "",
            "# Project Forge - Phase 11 Planning",
            "",
            "Back to [[Project Forge - Command Center]]. Review [[Project Forge - Deferred Items]] before expanding scope.",
            "",
            "## Candidate Lanes",
            "",
            "- Obsidian integration: keep artifact mirror deterministic before real vault sync.",
            "- Repo action policies: define allowed, blocked, and review-only actions per category.",
            "- Remote strategy: map local, GitHub, Codeberg, and mirror policy without contacting remotes by default.",
            "- Codex/VS Code isolation research: test user-data, extension-dir, profile, and environment boundaries.",
            "",
            "## Phase 11A Boundary",
            "",
            "- Generate Markdown notes under `artifacts/obsidian_mirror/` only.",
            "- Generate `artifacts/obsidian_mirror_report.md`.",
            "- Generate `artifacts/obsidian_mirror_manifest.json`.",
            "- Do not write to any real Obsidian vault.",
            "",
        ]
    )


def render_notes(state: MirrorState) -> dict[str, str]:
    return {
        NOTE_FILENAMES["command_center"]: render_command_center(state),
        NOTE_FILENAMES["dashboard_summary"]: render_dashboard_summary(state),
        NOTE_FILENAMES["known_embedded"]: render_known_embedded(state),
        NOTE_FILENAMES["deferred_items"]: render_deferred_items(state),
        NOTE_FILENAMES["phase_11_planning"]: render_phase_11_planning(state),
    }


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_notes(output_dir: Path, notes: dict[str, str]) -> tuple[Path, ...]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename in sorted(notes):
        path = output_dir / filename
        path.write_text(notes[filename], encoding="utf-8")
        written.append(path)
    return tuple(written)


def write_report(report_path: Path, state: MirrorState, note_paths: tuple[Path, ...], output_dir: Path, manifest_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Project Forge Obsidian Mirror Report",
        "",
        "- mode: `dry-run artifact mirror`",
        f"- output directory: `{relative_to_repo(output_dir)}`",
        f"- report path: `{relative_to_repo(report_path)}`",
        f"- manifest path: `{relative_to_repo(manifest_path)}`",
        f"- total notes generated: `{len(note_paths)}`",
        f"- known embedded repo count: `{state.known_embedded_count}`",
        f"- protected review count: `{state.protected_review_count}`",
        f"- dirty review count: `{state.dirty_review_count}`",
        f"- candidate review count: `{state.candidate_review_count}`",
        "",
        "## Notes Generated",
        "",
        *[f"- `{relative_to_repo(path)}`" for path in note_paths],
        "",
        "## Source Artifacts Used",
        "",
        *[f"- `{source}`" for source in state.source_artifacts_used],
        "",
        "## Deferred Items",
        "",
        *[f"- {item}" for item in DEFERRED_ITEMS],
        "",
        "## Safety Statement",
        "",
        *[f"- {item}" for item in SAFETY_STATEMENTS],
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")


def write_manifest(manifest_path: Path, state: MirrorState, notes: dict[str, str], note_paths: tuple[Path, ...], report_path: Path) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    path_by_name = {path.name: path for path in note_paths}
    generated_files = [relative_to_repo(path_by_name[name]) for name in sorted(notes)]
    payload = {
        "generated_by": "project_forge_registry.obsidian_mirror",
        "mode": "dry-run artifact mirror",
        "generated_files": generated_files,
        "report_path": relative_to_repo(report_path),
        "source_artifacts_used": list(state.source_artifacts_used),
        "summary": {
            "total_notes_generated": len(note_paths),
            "total_projects": state.total_projects,
            "known_embedded_repo_count": state.known_embedded_count,
            "protected_review_count": state.protected_review_count,
            "dirty_review_count": state.dirty_review_count,
            "candidate_review_count": state.candidate_review_count,
        },
        "checksums": {
            relative_to_repo(path_by_name[name]): sha256_text(notes[name])
            for name in sorted(notes)
        },
        "safety": {
            "real_vault_writes": False,
            "external_repo_writes": False,
            "apply": False,
            "remotes": False,
            "push_fetch": False,
            "package_installs": False,
            "network_calls": False,
            "vs_code_launch": False,
            "codex_login_or_auth_handling": False,
        },
    }
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_obsidian_mirror(
    *,
    dashboard_inventory: Path,
    output_dir: Path,
    report_path: Path,
    manifest_path: Path,
    source_paths: list[Path] | None = None,
) -> MirrorResult:
    inventory_path = resolve_repo_path(dashboard_inventory, must_exist=True)
    output_dir = resolve_repo_path(output_dir)
    report_path = resolve_repo_path(report_path)
    manifest_path = resolve_repo_path(manifest_path)
    sources = source_paths or SOURCE_ARTIFACTS
    inventory = load_dashboard_inventory(inventory_path)
    state = build_state(inventory, sources)
    notes = render_notes(state)
    note_paths = write_notes(output_dir, notes)
    write_report(report_path, state, note_paths, output_dir, manifest_path)
    write_manifest(manifest_path, state, notes, note_paths, report_path)
    return MirrorResult(
        output_dir=output_dir,
        report_path=report_path,
        manifest_path=manifest_path,
        note_paths=note_paths,
        state=state,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-forge-obsidian-mirror",
        description="Generate dry-run Obsidian-ready Project Forge artifact notes.",
    )
    parser.add_argument(
        "--dashboard-inventory",
        default=str(DEFAULT_DASHBOARD_INVENTORY),
        help="Existing dashboard inventory JSON to read.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Artifact note directory inside this repository.",
    )
    parser.add_argument(
        "--report-path",
        default=str(DEFAULT_REPORT_PATH),
        help="Artifact report path inside this repository.",
    )
    parser.add_argument(
        "--manifest-path",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Artifact manifest JSON path inside this repository.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_obsidian_mirror(
            dashboard_inventory=Path(args.dashboard_inventory),
            output_dir=Path(args.output_dir),
            report_path=Path(args.report_path),
            manifest_path=Path(args.manifest_path),
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"project-forge-obsidian-mirror failed: {error}\n")

    print("project-forge-obsidian-mirror completed")
    print("mode: dry-run artifact mirror")
    print(f"notes written: {len(result.note_paths)}")
    print(f"output directory: {result.output_dir}")
    print(f"report path: {result.report_path}")
    print(f"manifest path: {result.manifest_path}")
    print("safety: no real Obsidian vault writes; no external repo writes; no apply; no remotes; no push/fetch; no package installs; no network calls; no VS Code launch; no Codex login/auth handling")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
