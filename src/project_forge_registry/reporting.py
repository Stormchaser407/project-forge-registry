from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .models import ProjectScanResult

OBSIDIAN_PROJECT_ROOT = "/home/cole/main_vault/10 Projects"


def ensure_artifact_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_registry_record(result: ProjectScanResult) -> dict[str, object]:
    slug = result.safe_slug
    return {
        "slug": slug,
        "name": result.folder_name,
        "status": result.recommended_status,
        "classification": result.recommended_category,
        "category": result.recommended_category,
        "local_path": result.path,
        "canonical_path": result.canonical_path,
        "paths": {
            "workspace": f"/home/cole/.config/Code/User/workspaces/{slug}.code-workspace",
            "obsidian": f"{OBSIDIAN_PROJECT_ROOT}/{slug}",
        },
        "registry_action": result.recommended_action,
        "launch": {
            "command": f"code-{slug}",
        },
        "git": {
            "default_branch": "main" if result.has_git else None,
            "github": None,
            "codeberg": None,
            "mirror_mode": "dual_push",
        },
        "sync": {
            "obsidian_to_repo": "export_only",
            "repo_to_obsidian": "docs_only",
            "allow_code_to_obsidian": False,
            "allow_secrets": False,
        },
        "visibility": {
            "github": "private",
            "codeberg": "private",
            "public_ready": False,
        },
        "automation": {
            "auto_doc_sync": False,
            "auto_git_sync": False,
            "require_safety_check_before_push": True,
        },
        "constraints": {
            "do_not_move": result.do_not_move,
            "do_not_delete": result.do_not_delete,
            "exclude_from_bulk_sync": result.exclude_from_bulk_sync,
            "obsidian_note_policy": result.obsidian_note_policy,
        },
        "safety_warnings": result.safety_warnings,
    }


def _yaml_scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        if value == "":
            return '""'
        if any(char in value for char in ":#[]{}&*!|>'\"%@`") or value.strip() != value:
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return value
    raise TypeError(f"Unsupported YAML scalar: {type(value)!r}")


def _write_yaml_lines(value: object, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                if isinstance(item, list) and not item:
                    lines.append(f"{prefix}{key}: []")
                    continue
                lines.append(f"{prefix}{key}:")
                lines.extend(_write_yaml_lines(item, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {_yaml_scalar(item)}")
        return lines
    if isinstance(value, list):
        lines = []
        if not value:
            return [f"{prefix}[]"]
        for item in value:
            if isinstance(item, (dict, list)):
                child_lines = _write_yaml_lines(item, indent + 2)
                first, *rest = child_lines
                lines.append(f"{prefix}- {first.strip()}")
                lines.extend(rest)
            else:
                lines.append(f"{prefix}- {_yaml_scalar(item)}")
        return lines
    return [f"{prefix}{_yaml_scalar(value)}"]


def write_json_report(path: Path, results: list[ProjectScanResult], scan_roots: list[str]) -> None:
    payload = {
        "scan_roots": scan_roots,
        "project_count": len(results),
        "projects": [result.to_dict() for result in results],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_registry_yaml(path: Path, results: list[ProjectScanResult]) -> None:
    payload = {"projects": [build_registry_record(result) for result in results]}
    path.write_text("\n".join(_write_yaml_lines(payload)) + "\n", encoding="utf-8")


def write_markdown_report(path: Path, results: list[ProjectScanResult], scan_roots: list[str]) -> None:
    category_counts = Counter(result.recommended_category for result in results)
    action_counts = Counter(result.recommended_action for result in results)
    risky = [result for result in results if result.safety_warnings]

    lines = [
        "# Project Scan Report",
        "",
        "## Scope",
        "",
        f"- Scan roots: {', '.join(scan_roots)}",
        f"- Projects scanned: {len(results)}",
        "- Mode: dry-run only",
        "- Project folders modified: none",
        "",
        "## Summary",
        "",
    ]
    lines.extend(f"- Category `{key}`: {value}" for key, value in sorted(category_counts.items()))
    lines.extend(f"- Action `{key}`: {value}" for key, value in sorted(action_counts.items()))
    lines.extend(
        [
            "",
            "## Manual Review Needed",
            "",
        ]
    )
    if risky:
        lines.extend(
            f"- `{item.folder_name}`: {', '.join(item.safety_warnings)}"
            for item in risky
        )
    else:
        lines.append("- No high-risk folders were flagged by current heuristics.")

    lines.extend(
        [
            "",
            "## Projects",
            "",
            "| Folder | Slug | Stack | Status | Category | Action | Warnings |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for result in results:
        lines.append(
            "| "
            + " | ".join(
                [
                    result.folder_name,
                    result.safe_slug,
                    ", ".join(result.likely_stack),
                    result.recommended_status,
                    result.recommended_category,
                    result.recommended_action,
                    ", ".join(result.safety_warnings) if result.safety_warnings else "none",
                ]
            )
            + " |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_command_board(path: Path, results: list[ProjectScanResult]) -> None:
    lines = [
        "# Project Command Board Draft",
        "",
        "Dry-run planning board generated from project scan results.",
        "",
        "## Queue",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"### {result.folder_name}",
                f"- Slug: `{result.safe_slug}`",
                f"- Path: `{result.path}`",
                f"- Category: `{result.recommended_category}`",
                f"- Status: `{result.recommended_status}`",
                f"- Recommended action: `{result.recommended_action}`",
                f"- Suggested launcher: `code-{result.safe_slug}`",
                f"- Workspace target: `/home/cole/.config/Code/User/workspaces/{result.safe_slug}.code-workspace`",
                f"- Obsidian target: `{OBSIDIAN_PROJECT_ROOT}/{result.safe_slug}`",
                f"- Canonical path: `{result.canonical_path or result.path}`",
                f"- Constraints: do_not_move={str(result.do_not_move).lower()}, do_not_delete={str(result.do_not_delete).lower()}, exclude_from_bulk_sync={str(result.exclude_from_bulk_sync).lower()}, obsidian_note_policy={result.obsidian_note_policy}",
                f"- Warnings: {', '.join(result.safety_warnings) if result.safety_warnings else 'none'}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
