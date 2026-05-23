"""Phase 11B dry-run real-vault apply planner for Project Forge.

This module maps Phase 11A artifact mirror notes to proposed Obsidian vault
targets without writing to the vault.

Safety policy:
- real vault writes are blocked
- no directories are created outside this repository
- no files are copied
- no target files are modified
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
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST_PATH = Path("artifacts/obsidian_mirror_manifest.json")
DEFAULT_REPORT_PATH = Path("artifacts/obsidian_vault_apply_plan.md")
DEFAULT_JSON_PATH = Path("artifacts/obsidian_vault_apply_plan.json")
DEFAULT_VAULT_ROOT = Path("/mnt/storage/Cole/main_vault/10 Projects/Project Forge")

SAFETY_STATEMENTS = [
    "no real vault writes",
    "no external repo writes",
    "no apply",
    "no directory creation",
    "no file copy",
    "no target modification",
    "no remotes",
    "no push/fetch",
    "no package installs",
    "no network calls",
    "no VS Code launch",
    "no Codex login/auth handling",
]


@dataclass(frozen=True, slots=True)
class VaultPlanEntry:
    source_artifact_path: Path
    proposed_vault_target_path: Path
    action: str
    target_exists: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_artifact_path": relative_to_repo(self.source_artifact_path),
            "proposed_vault_target_path": str(self.proposed_vault_target_path),
            "action": self.action,
            "target_exists": self.target_exists,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class VaultPlan:
    mode: str
    source_manifest_path: Path
    vault_root: Path
    vault_root_exists: bool
    entries: tuple[VaultPlanEntry, ...]
    report_path: Path
    json_path: Path

    @property
    def source_note_count(self) -> int:
        return len(self.entries)

    @property
    def proposed_target_count(self) -> int:
        return len([entry for entry in self.entries if entry.action != "blocked"])


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


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        raise FileNotFoundError(f"Required mirror manifest not found: {manifest_path}")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("mirror manifest must be a JSON object")
    generated_files = payload.get("generated_files")
    if not isinstance(generated_files, list):
        raise ValueError("mirror manifest is missing generated_files list")
    return payload


def validate_generated_files(generated_files: list[Any]) -> tuple[Path, ...]:
    source_paths: list[Path] = []
    for raw_path in generated_files:
        if not isinstance(raw_path, str) or not raw_path.endswith(".md"):
            raise ValueError("generated_files entries must be Markdown path strings")
        source_paths.append(resolve_repo_path(raw_path))
    return tuple(sorted(source_paths, key=lambda item: item.name))


def build_entry(source_path: Path, vault_root: Path, vault_root_exists: bool) -> VaultPlanEntry:
    target_path = vault_root / source_path.name
    source_exists = source_path.exists()
    target_exists = target_path.exists()
    if not source_exists:
        return VaultPlanEntry(
            source_artifact_path=source_path,
            proposed_vault_target_path=target_path,
            action="blocked",
            target_exists=target_exists,
            reason="source_artifact_missing",
        )
    if target_exists:
        return VaultPlanEntry(
            source_artifact_path=source_path,
            proposed_vault_target_path=target_path,
            action="would_update",
            target_exists=True,
            reason="target_exists_plan_only",
        )
    reason = "vault_root_missing_plan_only" if not vault_root_exists else "target_missing_plan_only"
    return VaultPlanEntry(
        source_artifact_path=source_path,
        proposed_vault_target_path=target_path,
        action="would_create",
        target_exists=False,
        reason=reason,
    )


def build_vault_plan(
    *,
    manifest_path: Path,
    vault_root: Path,
    report_path: Path,
    json_path: Path,
) -> VaultPlan:
    manifest_path = resolve_repo_path(manifest_path, must_exist=True)
    report_path = resolve_repo_path(report_path)
    json_path = resolve_repo_path(json_path)
    manifest = load_manifest(manifest_path)
    source_paths = validate_generated_files(manifest["generated_files"])
    planned_vault_root = Path(vault_root).expanduser()
    vault_root_exists = planned_vault_root.exists()
    entries = tuple(
        build_entry(source_path, planned_vault_root, vault_root_exists)
        for source_path in source_paths
    )
    return VaultPlan(
        mode="dry-run vault apply plan",
        source_manifest_path=manifest_path,
        vault_root=planned_vault_root,
        vault_root_exists=vault_root_exists,
        entries=entries,
        report_path=report_path,
        json_path=json_path,
    )


def write_report(plan: VaultPlan) -> None:
    plan.report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Project Forge Obsidian Vault Apply Plan",
        "",
        f"- mode: `{plan.mode}`",
        f"- source note count: `{plan.source_note_count}`",
        f"- proposed target count: `{plan.proposed_target_count}`",
        f"- vault_root: `{plan.vault_root}`",
        f"- vault root exists: `{str(plan.vault_root_exists).lower()}`",
        f"- source manifest: `{relative_to_repo(plan.source_manifest_path)}`",
        f"- json path: `{relative_to_repo(plan.json_path)}`",
        "",
        "## Planned Note Mappings",
        "",
        "| Source artifact | Proposed vault target | Action | Target exists | Reason |",
        "|---|---|---|---|---|",
    ]
    for entry in plan.entries:
        lines.append(
            "| "
            f"`{relative_to_repo(entry.source_artifact_path)}` | "
            f"`{entry.proposed_vault_target_path}` | "
            f"`{entry.action}` | "
            f"`{str(entry.target_exists).lower()}` | "
            f"`{entry.reason}` |"
        )
    lines.extend(
        [
            "",
            "## Safety Statement",
            "",
            *[f"- {statement}" for statement in SAFETY_STATEMENTS],
            "",
            "## Phase Boundary",
            "",
            "Phase 11B is planning only. Phase 11C or later may implement an approved apply path.",
            "This command does not write to the planned vault folder.",
            "",
        ]
    )
    plan.report_path.write_text("\n".join(lines), encoding="utf-8")


def write_json_plan(plan: VaultPlan) -> None:
    plan.json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_by": "project_forge_registry.obsidian_vault_plan",
        "mode": plan.mode,
        "source_manifest_path": relative_to_repo(plan.source_manifest_path),
        "vault_root": str(plan.vault_root),
        "vault_root_exists": plan.vault_root_exists,
        "source_note_count": plan.source_note_count,
        "proposed_target_count": plan.proposed_target_count,
        "report_path": relative_to_repo(plan.report_path),
        "entries": [entry.to_dict() for entry in plan.entries],
        "safety": {
            "real_vault_writes": False,
            "external_repo_writes": False,
            "apply": False,
            "directory_creation": False,
            "file_copy": False,
            "target_modification": False,
            "remotes": False,
            "push_fetch": False,
            "package_installs": False,
            "network_calls": False,
            "vs_code_launch": False,
            "codex_login_or_auth_handling": False,
        },
    }
    plan.json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_vault_plan(
    *,
    manifest_path: Path,
    vault_root: Path,
    report_path: Path,
    json_path: Path,
) -> VaultPlan:
    plan = build_vault_plan(
        manifest_path=manifest_path,
        vault_root=vault_root,
        report_path=report_path,
        json_path=json_path,
    )
    write_report(plan)
    write_json_plan(plan)
    return plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-forge-obsidian-vault-plan",
        description="Plan a dry-run Obsidian vault apply from artifact mirror notes.",
    )
    parser.add_argument(
        "--manifest-path",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Phase 11A artifact mirror manifest.",
    )
    parser.add_argument(
        "--vault-root",
        default=str(DEFAULT_VAULT_ROOT),
        help="Proposed vault folder for planning only.",
    )
    parser.add_argument(
        "--report-path",
        default=str(DEFAULT_REPORT_PATH),
        help="Markdown plan report path inside this repository.",
    )
    parser.add_argument(
        "--json-path",
        default=str(DEFAULT_JSON_PATH),
        help="JSON plan path inside this repository.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        plan = run_vault_plan(
            manifest_path=Path(args.manifest_path),
            vault_root=Path(args.vault_root),
            report_path=Path(args.report_path),
            json_path=Path(args.json_path),
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"project-forge-obsidian-vault-plan failed: {error}\n")

    print("project-forge-obsidian-vault-plan completed")
    print(f"mode: {plan.mode}")
    print(f"source note count: {plan.source_note_count}")
    print(f"proposed target count: {plan.proposed_target_count}")
    print(f"vault_root: {plan.vault_root}")
    print(f"report path: {plan.report_path}")
    print(f"json path: {plan.json_path}")
    print("safety: no real vault writes; no external repo writes; no apply; no remotes; no push/fetch; no package installs; no network calls; no VS Code launch; no Codex login/auth handling")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
