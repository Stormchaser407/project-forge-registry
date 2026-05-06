from __future__ import annotations

from pathlib import Path

from .workspace_models import WorkspaceGenerationPlan


def write_workspace_generation_report(path: Path, plan: WorkspaceGenerationPlan) -> None:
    lines = [
        "# Workspace Launcher Generation Report",
        "",
        "## Scope",
        "",
        f"- Mode: `{plan.mode}`",
        f"- Input JSON: `{plan.input_json_path}`",
        f"- Workspace dir: `{plan.workspace_dir}`",
        f"- Launcher dir: `{plan.launcher_dir}`",
        f"- Preserved workspaces: {', '.join(f'`{name}`' for name in plan.preserved_workspaces)}",
        "- Project folders modified: 0",
        "",
        "## Summary",
        "",
        f"- Eligible projects: {len(plan.eligible_entries)}",
        f"- Skipped projects: {len(plan.skipped_entries)}",
        f"- Planned writes: {plan.planned_write_count}",
        f"- Planned backups: {plan.planned_backup_count}",
        f"- Completed writes: {plan.written_count}",
        f"- Completed backups: {plan.backup_count}",
        "",
        "## Eligible Projects",
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
                    f"- Registry action: `{entry.record.registry_action}`",
                    f"- Local path: `{entry.record.local_path}`",
                ]
            )
            for action in entry.file_actions:
                lines.append(
                    f"- {action.kind}: `{action.target_path}` "
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
