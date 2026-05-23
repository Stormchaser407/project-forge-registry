"""Phase 11C guarded Obsidian vault apply command for Project Forge.

Default mode is dry-run. Real vault writes require both --apply and
--yes-write-to-vault, and apply is create-only and all-or-nothing.
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_PLAN_PATH = Path("artifacts/obsidian_vault_apply_plan.json")
DEFAULT_SOURCE_ROOT = Path("artifacts/obsidian_mirror")
DEFAULT_DRY_RUN_REPORT_PATH = Path("artifacts/obsidian_vault_apply_dry_run_report.md")
DEFAULT_DRY_RUN_JSON_PATH = Path("artifacts/obsidian_vault_apply_dry_run.json")
EXPECTED_PLAN_MODE = "dry-run vault apply plan"

SAFETY_STATEMENTS = [
    "no real vault writes in dry-run",
    "apply requires --apply and --yes-write-to-vault",
    "create-only first implementation",
    "no overwrite",
    "no delete",
    "all-or-nothing preflight before apply writes",
    "no external repo writes",
    "no marker writes",
    "no remotes",
    "no push/fetch",
    "no package installs",
    "no network calls",
    "no VS Code launch",
    "no Codex login/auth handling",
]


@dataclass(frozen=True, slots=True)
class ApplyEntry:
    source_path: Path
    target_path: Path
    action: str
    target_exists: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": relative_to_repo(self.source_path),
            "target_path": str(self.target_path),
            "action": self.action,
            "target_exists": self.target_exists,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class ApplyPlan:
    mode: str
    apply_requested: bool
    vault_root: Path
    plan_path: Path
    source_root: Path
    report_path: Path
    json_path: Path
    entries: tuple[ApplyEntry, ...]

    @property
    def entries_reviewed(self) -> int:
        return len(self.entries)

    @property
    def would_create_count(self) -> int:
        return len([entry for entry in self.entries if entry.action in {"would_create", "created"}])

    @property
    def would_skip_count(self) -> int:
        return len([entry for entry in self.entries if entry.action in {"would_skip_identical", "skipped_identical"}])

    @property
    def blocked_count(self) -> int:
        return len([entry for entry in self.entries if entry.action.startswith("blocked")])

    @property
    def blocked_entries(self) -> tuple[ApplyEntry, ...]:
        return tuple(entry for entry in self.entries if entry.action.startswith("blocked"))


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


def load_json_plan(plan_path: Path) -> dict[str, Any]:
    if not plan_path.exists():
        raise FileNotFoundError(f"Required vault apply plan not found: {plan_path}")
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("vault apply plan must be a JSON object")
    if payload.get("mode") != EXPECTED_PLAN_MODE:
        raise ValueError(f"vault apply plan mode must be {EXPECTED_PLAN_MODE!r}")
    if not isinstance(payload.get("entries"), list) or not payload["entries"]:
        raise ValueError("vault apply plan must contain non-empty entries list")
    if not isinstance(payload.get("vault_root"), str) or not payload["vault_root"]:
        raise ValueError("vault apply plan must contain vault_root")
    return payload


def resolve_source_path(raw_source_path: str, source_root: Path) -> Path:
    source_path = resolve_repo_path(raw_source_path)
    source_root = resolve_repo_path(source_root)
    if source_root != source_path and source_root not in source_path.parents:
        raise ValueError(f"source path must stay inside source root: {raw_source_path}")
    return source_path


def compare_files(left: Path, right: Path) -> bool:
    return left.read_bytes() == right.read_bytes()


def preflight_entry(raw_entry: dict[str, Any], source_root: Path, vault_root: Path) -> ApplyEntry:
    raw_source = raw_entry.get("source_artifact_path") or raw_entry.get("source_path")
    if not isinstance(raw_source, str) or not raw_source:
        raise ValueError("vault apply plan entry is missing source artifact path")
    source_path = resolve_source_path(raw_source, source_root)
    target_path = vault_root / source_path.name

    if not source_path.exists():
        return ApplyEntry(
            source_path=source_path,
            target_path=target_path,
            action="blocked_missing_source",
            target_exists=target_path.exists(),
            reason="source file is missing",
        )

    if target_path.exists():
        if target_path.is_file() and compare_files(source_path, target_path):
            return ApplyEntry(
                source_path=source_path,
                target_path=target_path,
                action="would_skip_identical",
                target_exists=True,
                reason="target exists with identical content",
            )
        return ApplyEntry(
            source_path=source_path,
            target_path=target_path,
            action="blocked_existing_different",
            target_exists=True,
            reason="target exists and differs; create-only apply does not overwrite",
        )

    return ApplyEntry(
        source_path=source_path,
        target_path=target_path,
        action="would_create",
        target_exists=False,
        reason="target missing and source exists",
    )


def build_apply_plan(
    *,
    plan_path: Path,
    source_root: Path,
    vault_root_override: Path | None,
    apply_requested: bool,
    report_path: Path,
    json_path: Path,
) -> ApplyPlan:
    plan_path = resolve_repo_path(plan_path, must_exist=True)
    source_root = resolve_repo_path(source_root, must_exist=True)
    report_path = resolve_repo_path(report_path)
    json_path = resolve_repo_path(json_path)
    payload = load_json_plan(plan_path)
    if apply_requested and vault_root_override is None:
        raise ValueError("--apply requires explicit --vault-root")
    vault_root = Path(vault_root_override or payload["vault_root"]).expanduser()
    raw_entries = payload["entries"]
    entries = tuple(
        preflight_entry(raw_entry, source_root, vault_root)
        for raw_entry in raw_entries
    )
    mode = "apply" if apply_requested else "dry-run"
    return ApplyPlan(
        mode=mode,
        apply_requested=apply_requested,
        vault_root=vault_root,
        plan_path=plan_path,
        source_root=source_root,
        report_path=report_path,
        json_path=json_path,
        entries=entries,
    )


def apply_create_only(plan: ApplyPlan) -> ApplyPlan:
    if plan.blocked_entries:
        raise ValueError("apply preflight blocked; no files were written")
    plan.vault_root.mkdir(parents=True, exist_ok=True)
    applied_entries: list[ApplyEntry] = []
    for entry in plan.entries:
        if entry.action == "would_skip_identical":
            applied_entries.append(
                ApplyEntry(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    action="skipped_identical",
                    target_exists=True,
                    reason=entry.reason,
                )
            )
            continue
        if entry.action == "would_create":
            if entry.target_path.exists():
                raise ValueError(f"target appeared during apply; refusing overwrite: {entry.target_path}")
            shutil.copyfile(entry.source_path, entry.target_path)
            applied_entries.append(
                ApplyEntry(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    action="created",
                    target_exists=True,
                    reason="created by guarded create-only apply",
                )
            )
            continue
        raise ValueError(f"unsupported apply action: {entry.action}")
    return ApplyPlan(
        mode=plan.mode,
        apply_requested=plan.apply_requested,
        vault_root=plan.vault_root,
        plan_path=plan.plan_path,
        source_root=plan.source_root,
        report_path=plan.report_path,
        json_path=plan.json_path,
        entries=tuple(applied_entries),
    )


def write_report(plan: ApplyPlan) -> None:
    plan.report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Project Forge Obsidian Vault Apply Dry-Run Report" if not plan.apply_requested else "# Project Forge Obsidian Vault Apply Report",
        "",
        f"- mode: `{plan.mode}`",
        f"- apply requested: `{str(plan.apply_requested).lower()}`",
        f"- vault_root: `{plan.vault_root}`",
        f"- entries reviewed: `{plan.entries_reviewed}`",
        f"- would create: `{plan.would_create_count}`",
        f"- would skip: `{plan.would_skip_count}`",
        f"- blocked: `{plan.blocked_count}`",
        f"- plan path: `{relative_to_repo(plan.plan_path)}`",
        f"- source root: `{relative_to_repo(plan.source_root)}`",
        f"- json path: `{relative_to_repo(plan.json_path)}`",
        "",
        "## Entry Review",
        "",
        "| Source | Target | Action | Target exists | Reason |",
        "|---|---|---|---|---|",
    ]
    for entry in plan.entries:
        lines.append(
            "| "
            f"`{relative_to_repo(entry.source_path)}` | "
            f"`{entry.target_path}` | "
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
            "## Policy",
            "",
            "- default command is dry-run",
            "- --apply is rejected unless --yes-write-to-vault is also present",
            "- apply is create-only",
            "- no overwrite behavior is implemented",
            "- no delete behavior is implemented",
            "- all-or-nothing preflight blocks every write if any entry is blocked",
            "",
        ]
    )
    plan.report_path.write_text("\n".join(lines), encoding="utf-8")


def write_json(plan: ApplyPlan) -> None:
    plan.json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_by": "project_forge_registry.obsidian_vault_apply",
        "mode": plan.mode,
        "apply_requested": plan.apply_requested,
        "vault_root": str(plan.vault_root),
        "plan_path": relative_to_repo(plan.plan_path),
        "source_root": relative_to_repo(plan.source_root),
        "report_path": relative_to_repo(plan.report_path),
        "entries_reviewed": plan.entries_reviewed,
        "would_create": plan.would_create_count,
        "would_skip": plan.would_skip_count,
        "blocked": plan.blocked_count,
        "entries": [entry.to_dict() for entry in plan.entries],
        "safety": {
            "real_vault_writes_in_dry_run": False,
            "external_repo_writes": False,
            "overwrite": False,
            "delete": False,
            "all_or_nothing": True,
            "requires_yes_write_to_vault": True,
            "remotes": False,
            "push_fetch": False,
            "package_installs": False,
            "network_calls": False,
            "vs_code_launch": False,
            "codex_login_or_auth_handling": False,
        },
    }
    plan.json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_apply_command(
    *,
    plan_path: Path,
    source_root: Path,
    vault_root: Path | None,
    apply_requested: bool,
    yes_write_to_vault: bool,
    report_path: Path,
    json_path: Path,
) -> ApplyPlan:
    if apply_requested and not yes_write_to_vault:
        raise ValueError("--apply requires --yes-write-to-vault")
    plan = build_apply_plan(
        plan_path=plan_path,
        source_root=source_root,
        vault_root_override=vault_root,
        apply_requested=apply_requested,
        report_path=report_path,
        json_path=json_path,
    )
    if apply_requested:
        if plan.blocked_entries:
            write_report(plan)
            write_json(plan)
            raise ValueError("apply preflight blocked; no files were written")
        plan = apply_create_only(plan)
    write_report(plan)
    write_json(plan)
    return plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-forge-obsidian-vault-apply",
        description="Guarded create-only Obsidian vault apply command.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Review only. This is the default.")
    mode.add_argument("--apply", action="store_true", help="Create missing vault notes after full preflight.")
    parser.add_argument("--vault-root", default=None, help="Target vault folder. Required with --apply.")
    parser.add_argument("--plan", default=str(DEFAULT_PLAN_PATH), help="Vault apply plan JSON.")
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT), help="Artifact note source directory.")
    parser.add_argument("--require-clean-git", action="store_true", help="Reserved policy flag; not enforced in Phase 11C.")
    parser.add_argument("--yes-write-to-vault", action="store_true", help="Required with --apply.")
    parser.add_argument("--report-path", default=str(DEFAULT_DRY_RUN_REPORT_PATH), help="Repo-local report path.")
    parser.add_argument("--json-path", default=str(DEFAULT_DRY_RUN_JSON_PATH), help="Repo-local JSON report path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    apply_requested = bool(args.apply)
    try:
        plan = run_apply_command(
            plan_path=Path(args.plan),
            source_root=Path(args.source_root),
            vault_root=Path(args.vault_root) if args.vault_root else None,
            apply_requested=apply_requested,
            yes_write_to_vault=bool(args.yes_write_to_vault),
            report_path=Path(args.report_path),
            json_path=Path(args.json_path),
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"project-forge-obsidian-vault-apply failed: {error}\n")

    print("project-forge-obsidian-vault-apply completed")
    print(f"mode: {plan.mode}")
    print(f"apply requested: {str(plan.apply_requested).lower()}")
    print(f"entries reviewed: {plan.entries_reviewed}")
    print(f"would create: {plan.would_create_count}")
    print(f"would skip: {plan.would_skip_count}")
    print(f"blocked: {plan.blocked_count}")
    print(f"report path: {plan.report_path}")
    print(f"json path: {plan.json_path}")
    print("safety: create-only; no overwrite; no delete; all-or-nothing; no real vault writes in dry-run")
    if plan.apply_requested:
        created = [entry for entry in plan.entries if entry.action == "created"]
        for entry in created:
            print(f"created: {entry.target_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
