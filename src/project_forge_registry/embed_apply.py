"""Project Forge approved marker apply.

Reads embed_plan_inventory.csv and writes Project Forge marker files only for
explicitly selected, eligible plan_marker_write rows.

Safety policy:
- requires explicit --apply and --confirm-apply
- selected plan_marker_write rows only
- no dirty/protected/control repos
- no deletes
- no remotes
- no push/fetch
- no external commits
"""

from __future__ import annotations

import argparse
import csv
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_INPUT_CSV = Path("artifacts/embed_plan_inventory.csv")
DEFAULT_REPORT_NAME = "embed_apply_report.md"


@dataclass(frozen=True, slots=True)
class EmbedApplyRow:
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


@dataclass(frozen=True, slots=True)
class ApplyResult:
    slug: str
    path: Path
    status: str
    marker_yaml: Path
    marker_doc: Path
    note: str


def parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def load_plan(csv_path: Path) -> list[EmbedApplyRow]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Embed plan inventory not found: {csv_path}")

    rows: list[EmbedApplyRow] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                EmbedApplyRow(
                    slug=row["slug"],
                    path=Path(row["path"]),
                    selected=parse_bool(row["selected"]),
                    eligible=parse_bool(row["eligible"]),
                    decision=row["decision"],
                    reason=row["reason"],
                    marker_yaml=Path(row["marker_yaml"]),
                    marker_doc=Path(row["marker_doc"]),
                    category=row["category"],
                    git_status=row["git_status"],
                )
            )
    return rows


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


def marker_yaml_text(row: EmbedApplyRow) -> str:
    return "\n".join(
        [
            "# Project Forge marker",
            f"slug: {row.slug}",
            f"project_name: {row.slug}",
            "managed_by: project-forge-registry",
            "embed_status: approved",
            "safe_default_profile: true",
            "allow_apply: false",
            "allow_push: false",
            "notes: Marker created by approved Project Forge embed apply pilot.",
            "",
        ]
    )


def marker_doc_text(row: EmbedApplyRow) -> str:
    return "\n".join(
        [
            "# Project Forge",
            "",
            "This repository is tracked by Project Forge.",
            "",
            "## Status",
            "",
            f"- slug: `{row.slug}`",
            "- embed_status: `approved`",
            "- safe_default_profile: `true`",
            "- allow_apply: `false`",
            "- allow_push: `false`",
            "",
            "## Operator Notes",
            "",
            "Project Forge markers identify this repo for local dashboard and review workflows.",
            "",
            "This marker does not mean:",
            "",
            "- automatic push is approved",
            "- remote setup is approved",
            "- apply operations are enabled",
            "- external sync has occurred",
            "",
            "Use the Project Forge control repo for dry-run checks and dashboard review.",
            "",
        ]
    )


def is_safe_apply_row(row: EmbedApplyRow) -> tuple[bool, str]:
    if not row.selected:
        return False, "not selected"
    if not row.eligible:
        return False, "not eligible"
    if row.decision != "plan_marker_write":
        return False, f"decision is {row.decision}"
    if row.category != "clean_candidate":
        return False, f"category is {row.category}"
    if row.git_status != "clean":
        return False, f"planned git_status is {row.git_status}"
    if "cerberus" in str(row.path).lower():
        return False, "protected cerberus-like path"
    if row.path.name == "project-forge-registry":
        return False, "control repo"
    return True, "ok"


def apply_marker(row: EmbedApplyRow) -> ApplyResult:
    safe, reason = is_safe_apply_row(row)
    if not safe:
        return ApplyResult(row.slug, row.path, "skipped", row.marker_yaml, row.marker_doc, reason)

    if not row.path.exists() or not (row.path / ".git").exists():
        return ApplyResult(row.slug, row.path, "blocked", row.marker_yaml, row.marker_doc, "repo path missing or not git repo")

    current_status = git_status(row.path)
    if current_status != "clean":
        return ApplyResult(row.slug, row.path, "blocked", row.marker_yaml, row.marker_doc, f"current git status is {current_status}")

    if row.marker_yaml.exists() or row.marker_doc.exists():
        return ApplyResult(row.slug, row.path, "blocked", row.marker_yaml, row.marker_doc, "marker already exists; refusing overwrite")

    row.marker_doc.parent.mkdir(parents=True, exist_ok=True)
    row.marker_yaml.write_text(marker_yaml_text(row), encoding="utf-8")
    row.marker_doc.write_text(marker_doc_text(row), encoding="utf-8")

    return ApplyResult(row.slug, row.path, "written", row.marker_yaml, row.marker_doc, "marker files written")


def derive_final_status(results: list[ApplyResult]) -> str:
    if any(result.status == "blocked" for result in results):
        return "blocked"
    if any(result.status == "written" for result in results):
        return "applied_for_operator_review"
    return "incomplete"


def write_report(report_path: Path, results: list[ApplyResult]) -> str:
    final_status = derive_final_status(results)
    written = [item for item in results if item.status == "written"]
    blocked = [item for item in results if item.status == "blocked"]

    lines = [
        "# Project Forge Embed Apply Report",
        "",
        f"- date: `{datetime.now().isoformat(timespec='seconds')}`",
        "- mode: `approved-apply`",
        f"- final_status: `{final_status}`",
        f"- marker_writes: `{len(written)}`",
        f"- blocked: `{len(blocked)}`",
        "",
        "## Results",
        "",
    ]

    for result in results:
        if result.status in {"written", "blocked"}:
            lines.extend(
                [
                    f"### {result.slug}",
                    "",
                    f"- path: `{result.path}`",
                    f"- status: `{result.status}`",
                    f"- marker_yaml: `{result.marker_yaml}`",
                    f"- marker_doc: `{result.marker_doc}`",
                    f"- note: {result.note}",
                    "",
                ]
            )

    lines.extend(
        [
            "## Safety Statement",
            "",
            "- Only selected plan_marker_write rows were eligible.",
            "- No protected, dirty, or control repos were applied.",
            "- No remotes were added or modified.",
            "- No push/fetch occurred.",
            "- No package installs were performed.",
            "- No external commits were created.",
            "- Marker files were the only intended external writes.",
            "",
        ]
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return final_status


def run_apply(input_csv: Path, report_path: Path) -> str:
    rows = load_plan(input_csv)
    results = [apply_marker(row) for row in rows]
    return write_report(report_path, results)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-embed-apply")
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--report-name", default=DEFAULT_REPORT_NAME)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-apply", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.apply or not args.confirm_apply:
        parser.error("embed apply requires both --apply and --confirm-apply")

    report_path = Path("artifacts") / args.report_name
    final_status = run_apply(Path(args.input_csv), report_path)

    print("project-forge-embed-apply completed")
    print("mode: approved-apply")
    print(f"final status: {final_status}")
    print(f"report written: {report_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
