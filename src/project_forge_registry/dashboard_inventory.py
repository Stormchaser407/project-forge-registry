"""Project Forge dashboard inventory feed.

This module converts existing Project Forge artifacts into a read-only JSON
feed and Markdown status report for a future dashboard.

Safety policy:
- read-only against discovered repos
- no external repo writes
- no apply
- no marker writes
- no remotes
- no push/fetch
- no package installs
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_REPO_DISCOVERY_CSV = Path("artifacts/repo_discovery_inventory.csv")
DEFAULT_EMBED_PLAN_CSV = Path("artifacts/embed_plan_inventory.csv")
DEFAULT_JSON_PATH = Path("artifacts/dashboard_inventory.json")
DEFAULT_REPORT_PATH = Path("artifacts/dashboard_inventory_report.md")

REPORT_LINKS = [
    "artifacts/repo_discovery_report.md",
    "artifacts/repo_discovery_inventory.csv",
    "artifacts/embed_plan_report.md",
    "artifacts/embed_plan_inventory.csv",
    "artifacts/tool_readiness_report.md",
    "artifacts/project_sync_report.md",
]


@dataclass(frozen=True, slots=True)
class RepoDiscoveryRow:
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
class EmbedPlanRow:
    slug: str
    decision: str
    marker_yaml: Path
    marker_doc: Path


@dataclass(frozen=True, slots=True)
class DashboardProject:
    slug: str
    path: Path
    category: str
    git_status: str
    has_readme: bool
    has_agents: bool
    has_code_workspace: bool
    has_project_forge_marker: bool
    remote_count: int
    embed_decision: str | None
    repo_light: str
    docs_light: str
    risk_light: str
    overall_status: str
    recommended_action: str
    vscode_target: Path
    marker_yaml_path: Path
    marker_doc_path: Path
    report_links: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "path": str(self.path),
            "category": self.category,
            "git_status": self.git_status,
            "has_readme": self.has_readme,
            "has_agents": self.has_agents,
            "has_code_workspace": self.has_code_workspace,
            "has_project_forge_marker": self.has_project_forge_marker,
            "remote_count": self.remote_count,
            "embed_decision": self.embed_decision,
            "repo_light": self.repo_light,
            "docs_light": self.docs_light,
            "risk_light": self.risk_light,
            "overall_status": self.overall_status,
            "recommended_action": self.recommended_action,
            "vscode_target": str(self.vscode_target),
            "marker_yaml_path": str(self.marker_yaml_path),
            "marker_doc_path": str(self.marker_doc_path),
            "report_links": self.report_links,
        }


def parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def load_repo_discovery_inventory(csv_path: Path) -> list[RepoDiscoveryRow]:
    """Load the required repo discovery inventory."""
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Required repo discovery inventory not found: {csv_path}"
        )

    rows: list[RepoDiscoveryRow] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                RepoDiscoveryRow(
                    slug=row["slug"],
                    path=Path(row["path"]),
                    git_status=row["git_status"],
                    has_readme=parse_bool(row["has_readme"]),
                    has_agents=parse_bool(row["has_agents"]),
                    has_code_workspace=parse_bool(row["has_code_workspace"]),
                    has_project_forge_marker=parse_bool(
                        row["has_project_forge_marker"]
                    ),
                    remote_count=int(row["remote_count"]),
                    category=row["category"],
                )
            )
    return sorted(rows, key=lambda item: (str(item.path), item.slug))


def load_embed_plan_inventory(csv_path: Path) -> dict[str, EmbedPlanRow]:
    """Load optional embed-plan inventory rows keyed by slug."""
    if not csv_path.exists():
        return {}

    rows: dict[str, EmbedPlanRow] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows[row["slug"]] = EmbedPlanRow(
                slug=row["slug"],
                decision=row["decision"],
                marker_yaml=Path(row["marker_yaml"]),
                marker_doc=Path(row["marker_doc"]),
            )
    return rows


def derive_repo_light(row: RepoDiscoveryRow) -> str:
    if row.category in {"known_embedded", "clean_candidate"} and row.git_status == "clean":
        return "green"
    if row.category == "dirty_candidate_review_first" or row.git_status == "dirty":
        return "amber"
    if row.category == "control_repo":
        return "blue"
    return "red"


def derive_docs_light(row: RepoDiscoveryRow) -> str:
    if row.has_project_forge_marker:
        return "green"
    if row.has_readme:
        return "amber"
    return "gray"


def derive_risk_light(row: RepoDiscoveryRow) -> str:
    if row.category == "control_repo":
        return "blue"
    if row.category == "protected_manual_review":
        return "red"
    if row.category == "dirty_candidate_review_first" or row.git_status == "dirty":
        return "amber"
    if row.category == "clean_candidate" and row.remote_count > 0:
        return "amber"
    if row.category in {"known_embedded", "clean_candidate"} and row.git_status == "clean":
        return "green"
    return "red"


def derive_recommended_action(row: RepoDiscoveryRow) -> str:
    if row.category == "known_embedded":
        return "embedded_ready"
    if row.category == "clean_candidate":
        return "candidate_review"
    if row.category == "dirty_candidate_review_first" or row.git_status == "dirty":
        return "dirty_review_first"
    if row.category == "protected_manual_review":
        return "protected_manual_review"
    if row.category == "control_repo":
        return "control_repo_no_embed"
    return "unknown_review"


def derive_overall_status(row: RepoDiscoveryRow) -> str:
    return derive_recommended_action(row)


def find_vscode_target(repo_path: Path) -> Path:
    """Prefer a repo-root .code-workspace file when present."""
    if repo_path.exists() and repo_path.is_dir():
        workspaces = sorted(repo_path.glob("*.code-workspace"), key=lambda item: item.name)
        if workspaces:
            return workspaces[0]
    return repo_path


def build_project_record(
    row: RepoDiscoveryRow,
    embed_rows: dict[str, EmbedPlanRow],
) -> DashboardProject:
    embed = embed_rows.get(row.slug)
    marker_yaml = embed.marker_yaml if embed else row.path / ".project-forge.yml"
    marker_doc = embed.marker_doc if embed else row.path / "docs" / "PROJECT_FORGE.md"

    return DashboardProject(
        slug=row.slug,
        path=row.path,
        category=row.category,
        git_status=row.git_status,
        has_readme=row.has_readme,
        has_agents=row.has_agents,
        has_code_workspace=row.has_code_workspace,
        has_project_forge_marker=row.has_project_forge_marker,
        remote_count=row.remote_count,
        embed_decision=embed.decision if embed else None,
        repo_light=derive_repo_light(row),
        docs_light=derive_docs_light(row),
        risk_light=derive_risk_light(row),
        overall_status=derive_overall_status(row),
        recommended_action=derive_recommended_action(row),
        vscode_target=find_vscode_target(row.path),
        marker_yaml_path=marker_yaml,
        marker_doc_path=marker_doc,
        report_links=list(REPORT_LINKS),
    )


def build_dashboard_inventory(
    discovery_rows: list[RepoDiscoveryRow],
    embed_rows: dict[str, EmbedPlanRow] | None = None,
) -> list[DashboardProject]:
    embed_lookup = embed_rows or {}
    return [
        build_project_record(row, embed_lookup)
        for row in sorted(discovery_rows, key=lambda item: (str(item.path), item.slug))
    ]


def count_by(projects: list[DashboardProject], field_name: str) -> dict[str, int]:
    counts = Counter(getattr(project, field_name) for project in projects)
    return dict(sorted(counts.items()))


def build_summary(projects: list[DashboardProject]) -> dict[str, Any]:
    return {
        "total_projects": len(projects),
        "count_by_category": count_by(projects, "category"),
        "count_by_repo_light": count_by(projects, "repo_light"),
        "count_by_docs_light": count_by(projects, "docs_light"),
        "count_by_risk_light": count_by(projects, "risk_light"),
        "known_embedded_count": len(
            [project for project in projects if project.category == "known_embedded"]
        ),
        "dirty_review_count": len(
            [
                project
                for project in projects
                if project.recommended_action == "dirty_review_first"
            ]
        ),
        "protected_review_count": len(
            [
                project
                for project in projects
                if project.recommended_action == "protected_manual_review"
            ]
        ),
    }


def write_json(json_path: Path, projects: list[DashboardProject]) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_by": "project_forge_registry.dashboard_inventory",
        "mode": "read-only",
        "summary": build_summary(projects),
        "report_links": list(REPORT_LINKS),
        "projects": [project.to_dict() for project in projects],
    }
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _format_count_lines(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- none"]
    return [f"- {key}: `{value}`" for key, value in sorted(counts.items())]


def write_report(report_path: Path, json_path: Path, projects: list[DashboardProject]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    summary = build_summary(projects)
    known_embedded = [
        project for project in projects if project.category == "known_embedded"
    ]
    dirty_review = [
        project
        for project in projects
        if project.recommended_action == "dirty_review_first"
    ]
    protected_review = [
        project
        for project in projects
        if project.recommended_action == "protected_manual_review"
    ]

    lines: list[str] = [
        "# Project Forge Dashboard Inventory Report",
        "",
        "- mode: `read-only`",
        f"- total_projects: `{summary['total_projects']}`",
        f"- json: `{json_path}`",
        "",
        "## Category Summary",
        "",
        *_format_count_lines(summary["count_by_category"]),
        "",
        "## Repo Light Summary",
        "",
        *_format_count_lines(summary["count_by_repo_light"]),
        "",
        "## Docs Light Summary",
        "",
        *_format_count_lines(summary["count_by_docs_light"]),
        "",
        "## Risk Light Summary",
        "",
        *_format_count_lines(summary["count_by_risk_light"]),
        "",
        "## Known Embedded Projects",
        "",
    ]

    if known_embedded:
        for project in known_embedded:
            lines.append(f"- `{project.slug}` - `{project.path}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Dirty Review Projects", ""])
    if dirty_review:
        for project in dirty_review:
            lines.append(f"- `{project.slug}` - `{project.path}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Protected Review Projects", ""])
    if protected_review:
        for project in protected_review:
            lines.append(f"- `{project.slug}` - `{project.path}`")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety Statement",
            "",
            "- Dashboard inventory is built from existing Project Forge artifacts.",
            "- No external repos were modified.",
            "- No apply operation was performed.",
            "- No marker files were written.",
            "- No remotes were added or modified.",
            "- No push/fetch occurred.",
            "- No package installs were performed.",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_dashboard_inventory(
    discovery_csv: Path,
    embed_plan_csv: Path,
    json_path: Path,
    report_path: Path,
) -> list[DashboardProject]:
    discovery_rows = load_repo_discovery_inventory(discovery_csv)
    embed_rows = load_embed_plan_inventory(embed_plan_csv)
    projects = build_dashboard_inventory(discovery_rows, embed_rows)
    write_json(json_path, projects)
    write_report(report_path, json_path, projects)
    return projects


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-dashboard-inventory")
    parser.add_argument(
        "--repo-discovery-csv",
        default=str(DEFAULT_REPO_DISCOVERY_CSV),
        help="Required repo discovery inventory CSV.",
    )
    parser.add_argument(
        "--embed-plan-csv",
        default=str(DEFAULT_EMBED_PLAN_CSV),
        help="Optional embed plan inventory CSV.",
    )
    parser.add_argument(
        "--json-path",
        default=str(DEFAULT_JSON_PATH),
        help="Dashboard JSON output path.",
    )
    parser.add_argument(
        "--report-path",
        default=str(DEFAULT_REPORT_PATH),
        help="Dashboard Markdown report output path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    projects = run_dashboard_inventory(
        discovery_csv=Path(args.repo_discovery_csv),
        embed_plan_csv=Path(args.embed_plan_csv),
        json_path=Path(args.json_path),
        report_path=Path(args.report_path),
    )
    summary = build_summary(projects)

    print("project-forge-dashboard-inventory completed")
    print("mode: read-only")
    print(f"projects: {summary['total_projects']}")
    print(f"known embedded: {summary['known_embedded_count']}")
    print(f"json written: {Path(args.json_path).resolve()}")
    print(f"report written: {Path(args.report_path).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
