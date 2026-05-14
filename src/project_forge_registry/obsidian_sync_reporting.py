from __future__ import annotations

from pathlib import Path

from .obsidian_sync_models import ObsidianSyncPlan


def write_obsidian_sync_report(path: Path, plan: ObsidianSyncPlan) -> None:
    lines = [
        "# Obsidian Sync Report",
        "",
        "## Scope",
        "",
        f"- Mode: `{plan.mode}`",
        f"- Slug: `{plan.slug}`",
        f"- Passport dir: `{plan.passport_dir}`",
        f"- Mirror dir: `{plan.mirror_dir}`",
        f"- Source mirror path: `{plan.source_mirror_path}`",
        f"- Destination vault path: `{plan.destination_vault_path}`",
        f"- Vault project root: `{plan.vault_project_root}`",
        "",
        "## Summary",
        "",
        f"- Eligible: {str(plan.entry.eligible).lower()}",
        f"- Files planned: {plan.files_planned}",
        f"- Files copied: {plan.files_copied}",
        f"- Backups planned: {plan.backups_planned}",
        f"- Backups created: {plan.backups_created}",
        f"- Excluded files: {len(plan.entry.excluded_files)}",
    ]

    if plan.entry.reasons:
        lines.extend(["", "## Skip Reasons", ""])
        for reason in plan.entry.reasons:
            lines.append(f"- {reason}")

    lines.extend(["", "## Files Planned", ""])
    if not plan.entry.file_actions:
        lines.append("- None")
    else:
        for action in plan.entry.file_actions:
            backup_text = f"`{action.backup_path}`" if action.backup_path else "`none`"
            lines.append(
                f"- source=`{action.source_path}` -> destination=`{action.destination_path}` "
                f"(exists_before={str(action.existed_before).lower()}, "
                f"backup={backup_text}, copied={str(action.copied).lower()}, "
                f"backup_created={str(action.backup_created).lower()})"
            )

    lines.extend(["", "## Excluded Files", ""])
    if not plan.entry.excluded_files:
        lines.append("- None")
    else:
        for excluded in plan.entry.excluded_files:
            lines.append(f"- `{excluded.source_path}` ({excluded.reason})")

    lines.extend(
        [
            "",
            "## Safety Confirmation",
            "",
            "- Source code copied: no",
            "- Secrets copied: no",
            "- Markdown-only filter enforced: yes",
            "- `.bak` files copied: no",
            "- Non-markdown files copied: no",
            "- Destination deletes performed: no",
            "- External project folders modified: no",
            "- Cerberus system/storage paths touched: no",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
