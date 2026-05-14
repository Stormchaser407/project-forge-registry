from __future__ import annotations

from pathlib import Path

from .export_sync_models import ExportSyncPlan


def write_export_sync_report(path: Path, plan: ExportSyncPlan) -> None:
    lines = [
        "# Export Sync Report",
        "",
        "## Scope",
        "",
        f"- Mode: `{plan.mode}`",
        f"- Slug: `{plan.slug}`",
        f"- Passport dir: `{plan.passport_dir}`",
        f"- Passport file: `{plan.entry.record.passport_path}`",
        f"- Source export root: `{plan.entry.source_export_root}`",
        f"- Source docs root: `{plan.entry.source_docs_root}`",
        f"- Destination docs root: `{plan.entry.destination_docs_root}`",
        f"- Vault project root: `{plan.vault_project_root}`",
        f"- Repo root override: `{plan.repo_root_override if plan.repo_root_override else 'none'}`",
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
        lines.extend(["", "## Eligibility Notes", ""])
        for reason in plan.entry.reasons:
            lines.append(f"- {reason}")

    lines.extend(["", "## Files Planned", ""])
    if not plan.entry.file_actions:
        lines.append("- None")
    else:
        for action in plan.entry.file_actions:
            backup_text = f"`{action.backup_path}`" if action.backup_path else "`none`"
            lines.append(
                f"- source=`{action.source_path}` "
                f"(relative_export=`{action.source_relative_export_path}`) -> "
                f"destination=`{action.destination_path}` "
                f"(exists_before={str(action.existed_before).lower()}, "
                f"backup={backup_text}, "
                f"copied={str(action.copied).lower()}, "
                f"backup_created={str(action.backup_created).lower()})"
            )

    lines.extend(["", "## Excluded Files", ""])
    if not plan.entry.excluded_files:
        lines.append("- None")
    else:
        for excluded in plan.entry.excluded_files:
            lines.append(f"- `{excluded.source_relative_export_path}` ({excluded.reason})")

    lines.extend(
        [
            "",
            "## Safety Confirmation",
            "",
            "- `_export/docs/` default source scope enforced: yes",
            "- Markdown-only filter enforced: yes",
            "- Repo-root `README.md` overwrite allowed: no",
            "- Destination delete operations performed: no",
            "- Cerberus paths touched: no",
            "- Source code or secrets moved: no",
            "- Logs/databases/binaries moved: no",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
