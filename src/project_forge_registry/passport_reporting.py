from __future__ import annotations

from pathlib import Path

from .passport_models import PassportGenerationPlan


def write_passport_generation_report(path: Path, plan: PassportGenerationPlan) -> None:
    lines = [
        "# Project Passport Generation Report",
        "",
        "## Scope",
        "",
        f"- Mode: `{plan.mode}`",
        f"- Input JSON: `{plan.input_json_path}`",
        f"- Artifacts dir: `{plan.artifacts_dir}`",
        f"- Passport proposal dir: `{plan.passports_dir}`",
        "- External project folders modified: 0",
        "",
        "## Summary",
        "",
        f"- Eligible projects: {len(plan.eligible_entries)}",
        f"- Skipped projects: {len(plan.skipped_entries)}",
        f"- Planned proposal writes: {plan.planned_write_count}",
        f"- Planned backups: {plan.planned_backup_count}",
        f"- Completed proposal writes: {plan.written_count}",
        f"- Completed backups: {plan.backup_count}",
        "",
        "## Generated Passport Proposals",
        "",
    ]

    if not plan.eligible_entries:
        lines.append("- None")
    else:
        for entry in plan.eligible_entries:
            lines.extend(
                [
                    f"### {entry.record.slug}",
                    f"- Name: `{entry.record.name}`",
                    f"- Category: `{entry.record.category}`",
                    f"- Status: `{entry.record.status}`",
                    f"- Registry action: `{entry.record.registry_action}`",
                    f"- Local path: `{entry.record.local_path}`",
                    f"- Proposal path: `{entry.proposal_path}`",
                ]
            )
            if entry.file_action is not None:
                lines.append(
                    f"- file: exists_before={str(entry.file_action.existed_before).lower()}, "
                    f"backup={f'`{entry.file_action.backup_path}`' if entry.file_action.backup_path else '`none`'}, "
                    f"written={str(entry.file_action.wrote_file).lower()}, "
                    f"backup_created={str(entry.file_action.created_backup).lower()}"
                )
            lines.append("")

    lines.extend(
        [
            "## Skipped Projects",
            "",
        ]
    )
    if not plan.skipped_entries:
        lines.append("- None")
    else:
        for entry in plan.skipped_entries:
            reason_text = ", ".join(entry.reasons) if entry.reasons else "unspecified"
            lines.append(f"- `{entry.record.slug}`: {reason_text}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
