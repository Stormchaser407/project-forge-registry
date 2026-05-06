from __future__ import annotations

from pathlib import Path

from .obsidian_mirror_models import ObsidianMirrorGenerationPlan


def write_obsidian_mirror_generation_report(path: Path, plan: ObsidianMirrorGenerationPlan) -> None:
    lines = [
        "# Obsidian Mirror Generation Report",
        "",
        "## Scope",
        "",
        f"- Mode: `{plan.mode}`",
        f"- Passport dir: `{plan.passport_dir}`",
        f"- Artifacts dir: `{plan.artifacts_dir}`",
        f"- Mirror proposal dir: `{plan.mirrors_dir}`",
        "- Real Obsidian vault modified: 0",
        "- External project folders modified: 0",
        "",
        "## Summary",
        "",
        f"- Eligible projects: {len(plan.eligible_entries)}",
        f"- Skipped projects: {len(plan.skipped_entries)}",
        f"- Planned mirror writes: {plan.planned_write_count}",
        f"- Planned backups: {plan.planned_backup_count}",
        f"- Completed mirror writes: {plan.written_count}",
        f"- Completed backups: {plan.backup_count}",
        "",
        "## Generated Mirror Proposals",
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
                    f"- Passport: `{entry.record.passport_path}`",
                    f"- Mirror path: `{entry.mirror_dir}`",
                ]
            )
            for action in entry.file_actions:
                lines.append(
                    f"- file: `{action.target_path}` "
                    f"(exists_before={str(action.existed_before).lower()}, "
                    f"backup={f'`{action.backup_path}`' if action.backup_path else '`none`'}, "
                    f"written={str(action.wrote_file).lower()}, "
                    f"backup_created={str(action.created_backup).lower()})"
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
