"""Project Forge embed plan dry-run.

This module reads a repo discovery inventory CSV and builds a dry-run plan for
adding Project Forge marker files to approved repositories.

Safety policy:
- dry-run/report-only
- no external repo writes
- no marker files created
- no apply
- no remotes
- no push/fetch
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


DEFAULT_INPUT_CSV = Path("artifacts/repo_discovery_inventory.csv")
DEFAULT_REPORT_NAME = "embed_plan_report.md"
DEFAULT_CSV_NAME = "embed_plan_inventory.csv"


@dataclass(frozen=True, slots=True)
class RepoInventoryRow:
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
class EmbedPlanItem:
    slug: str
    path: Path
    selected: bool
    eligible: bool
    decision: str
    reason: str
    marker_yaml: Path
    marker_doc: Path
    category: str
    git_status: str


def parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def load_inventory(csv_path: Path) -> list[RepoInventoryRow]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Discovery inventory not found: {csv_path}")

    rows: list[RepoInventoryRow] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                RepoInventoryRow(
                    slug=row["slug"],
                    path=Path(row["path"]),
                    git_status=row["git_status"],
                    has_readme=parse_bool(row["has_readme"]),
                    has_agents=parse_bool(row["has_agents"]),
                    has_code_workspace=parse_bool(row["has_code_workspace"]),
                    has_project_forge_marker=parse_bool(row["has_project_forge_marker"]),
                    remote_count=int(row["remote_count"]),
                    category=row["category"],
                )
            )
    return rows


def build_plan_item(row: RepoInventoryRow, selected_slugs: set[str]) -> EmbedPlanItem:
    selected = row.slug in selected_slugs

    eligible = row.category == "clean_candidate" and row.git_status == "clean"

    if row.has_project_forge_marker:
        decision = "already_embedded"
        reason = "Project Forge marker already present."
    elif row.category == "control_repo":
        decision = "skip_control_repo"
        reason = "Project Forge control repo should not embed into itself automatically."
    elif row.category == "protected_manual_review":
        decision = "blocked_protected"
        reason = "Protected/Cerberus-related repo requires manual review."
    elif row.git_status != "clean":
        decision = "blocked_dirty"
        reason = "Repo is dirty; clean or review before embedding."
    elif not selected:
        decision = "candidate_not_selected"
        reason = "Clean candidate, but not selected for this embed plan."
    elif eligible:
        decision = "plan_marker_write"
        reason = "Selected clean candidate; marker write may be approved in later apply phase."
    else:
        decision = "blocked_unknown"
        reason = "Repo does not meet safe embed criteria."

    return EmbedPlanItem(
        slug=row.slug,
        path=row.path,
        selected=selected,
        eligible=eligible,
        decision=decision,
        reason=reason,
        marker_yaml=row.path / ".project-forge.yml",
        marker_doc=row.path / "docs" / "PROJECT_FORGE.md",
        category=row.category,
        git_status=row.git_status,
    )


def build_plan(rows: list[RepoInventoryRow], selected_slugs: set[str]) -> list[EmbedPlanItem]:
    return [build_plan_item(row, selected_slugs) for row in rows]


def derive_final_status(items: list[EmbedPlanItem]) -> str:
    selected = [item for item in items if item.selected]

    if not selected:
        return "incomplete"

    if any(item.decision.startswith("blocked") for item in selected):
        return "blocked"

    if any(item.decision == "plan_marker_write" for item in selected):
        return "ready_for_operator_review"

    if all(item.decision == "already_embedded" for item in selected):
        return "ready_for_operator_review"

    return "incomplete"


def write_csv(csv_path: Path, items: list[EmbedPlanItem]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "slug",
            "path",
            "selected",
            "eligible",
            "decision",
            "reason",
            "marker_yaml",
            "marker_doc",
            "category",
            "git_status",
        ])
        for item in items:
            writer.writerow([
                item.slug,
                str(item.path),
                str(item.selected).lower(),
                str(item.eligible).lower(),
                item.decision,
                item.reason,
                str(item.marker_yaml),
                str(item.marker_doc),
                item.category,
                item.git_status,
            ])


def write_report(report_path: Path, csv_path: Path, items: list[EmbedPlanItem], selected_slugs: set[str]) -> str:
    final_status = derive_final_status(items)
    selected_items = [item for item in items if item.selected]
    plan_items = [item for item in items if item.decision == "plan_marker_write"]
    blocked_selected = [item for item in selected_items if item.decision.startswith("blocked")]

    lines: list[str] = [
        "# Project Forge Embed Plan Report",
        "",
        "- mode: `dry-run`",
        "- apply_performed: `false`",
        f"- final_status: `{final_status}`",
        f"- selected_slugs: `{len(selected_slugs)}`",
        f"- planned_marker_writes: `{len(plan_items)}`",
        f"- blocked_selected: `{len(blocked_selected)}`",
        f"- csv: `{csv_path}`",
        "",
        "## Selected Slugs",
        "",
    ]

    if selected_slugs:
        for slug in sorted(selected_slugs):
            lines.append(f"- `{slug}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Planned Marker Writes", ""])

    if plan_items:
        for item in plan_items:
            lines.extend([
                f"### {item.slug}",
                "",
                f"- path: `{item.path}`",
                f"- marker_yaml: `{item.marker_yaml}`",
                f"- marker_doc: `{item.marker_doc}`",
                f"- decision: `{item.decision}`",
                f"- reason: {item.reason}",
                "",
            ])
    else:
        lines.append("- none")

    lines.extend(["", "## Selected Repo Decisions", ""])

    if selected_items:
        for item in selected_items:
            lines.extend([
                f"### {item.slug}",
                "",
                f"- path: `{item.path}`",
                f"- category: `{item.category}`",
                f"- git_status: `{item.git_status}`",
                f"- eligible: `{str(item.eligible).lower()}`",
                f"- decision: `{item.decision}`",
                f"- reason: {item.reason}",
                "",
            ])
    else:
        lines.append("- none")

    lines.extend(["", "## All Repo Decision Summary", ""])

    decision_counts: dict[str, int] = {}
    for item in items:
        decision_counts[item.decision] = decision_counts.get(item.decision, 0) + 1

    for decision in sorted(decision_counts):
        lines.append(f"- {decision}: `{decision_counts[decision]}`")

    lines.extend([
        "",
        "## Safety Statement",
        "",
        "- This is a dry-run embed plan only.",
        "- No marker files were written.",
        "- No external repos were modified.",
        "- No apply operation was performed.",
        "- No remotes were added or modified.",
        "- No push/fetch occurred.",
        "- Embedding requires a separate approved apply phase.",
        "",
    ])

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return final_status


def run_embed_plan(
    input_csv: Path,
    selected_slugs: set[str],
    report_path: Path,
    output_csv: Path,
) -> str:
    rows = load_inventory(input_csv)
    items = build_plan(rows, selected_slugs)
    write_csv(output_csv, items)
    return write_report(report_path, output_csv, items, selected_slugs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-embed-plan")
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--include-slug", action="append", default=[])
    parser.add_argument("--report-name", default=DEFAULT_REPORT_NAME)
    parser.add_argument("--csv-name", default=DEFAULT_CSV_NAME)
    parser.add_argument("--dry-run", action="store_true", default=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    selected_slugs = set(args.include_slug)
    report_path = Path("artifacts") / args.report_name
    csv_path = Path("artifacts") / args.csv_name

    final_status = run_embed_plan(
        input_csv=Path(args.input_csv),
        selected_slugs=selected_slugs,
        report_path=report_path,
        output_csv=csv_path,
    )

    print("project-forge-embed-plan completed")
    print("mode: dry-run")
    print(f"selected slugs: {len(selected_slugs)}")
    print(f"final status: {final_status}")
    print(f"report written: {report_path.resolve()}")
    print(f"csv written: {csv_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
