"""Phase 11H.5 guarded launcher replacement apply command.

Safety language for validation and operator review: Phase 11H.5, guarded
launcher replacement apply, default dry-run, no real apply unless all guards
pass, no mutation during dry-run, no launch behavior, no --open, no systemd
changes, no desktop entry changes unless explicitly approved, no autostart
changes unless explicitly approved, backup before overwrite, rollback required,
no delete, no vault writes, exact approval phrase required, exact target path
confirmation required, clean git tree required.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PHASE = "Phase 11H.5"
MODE_DRY_RUN = "default dry-run"
MODE_APPLY = "guarded real apply"
APPROVAL_PHRASE = "APPROVE 11H.5 GUARDED LAUNCHER REPLACEMENT APPLY"
APPROVED_TARGET = "~/.local/share/applications/project-forge-command-board.desktop"
DEFAULT_REPORT_PATH = Path("artifacts/neon_command_board_launcher_apply_dry_run.md")
DEFAULT_JSON_PATH = Path("artifacts/neon_command_board_launcher_apply_dry_run.json")
PREFLIGHT_PATH = Path("artifacts/neon_command_board_launcher_apply_preflight.json")

SAFETY = {
    "guarded launcher replacement apply": True,
    "default dry-run": True,
    "no real apply unless all guards pass": True,
    "no mutation during dry-run": True,
    "no launch behavior": True,
    "no --open": True,
    "no systemd changes": True,
    "no desktop entry changes unless explicitly approved": True,
    "no autostart changes unless explicitly approved": True,
    "backup before overwrite": True,
    "rollback required": True,
    "no delete": True,
    "no vault writes": True,
    "exact approval phrase required": True,
    "exact target path confirmation required": True,
    "clean git tree required": True,
}


@dataclass(frozen=True, slots=True)
class ApplyOptions:
    apply_requested: bool = False
    yes_replace_launcher: bool = False
    approval_phrase: str | None = None
    target_path: str | None = None
    confirm_target_path: str | None = None
    expected_head: str | None = None
    expected_tag: str | None = None
    clean_git_tree_confirmed: bool = False
    launch_requested: bool = False
    open_requested: bool = False
    enable_requested: bool = False
    disable_requested: bool = False
    reload_requested: bool = False
    real_target_path: Path | None = None
    backup_path: Path | None = None
    replacement_content: str | None = None


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_path(path: str | Path, *, root: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def read_json_artifact(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "missing"
    if not path.is_file():
        return None, "not a file"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"invalid json: {exc}"
    except OSError as exc:
        return None, f"read failed: {exc}"
    if not isinstance(payload, dict):
        return None, "json root is not an object"
    return payload, None


def checked_artifact(path: Path, payload: dict[str, Any] | None, error: str | None) -> dict[str, Any]:
    return {
        "path": str(path),
        "present": error is None,
        "phase": payload.get("phase") if payload else None,
        "status": "checked" if error is None else "refusal",
        "error": error,
    }


def target_in_preflight(preflight: dict[str, Any] | None, target_path: str | None) -> bool:
    if not preflight or not target_path:
        return False
    for target in preflight.get("proposed_targets", []):
        if isinstance(target, dict) and target.get("path") == target_path:
            return True
    return False


def generated_content() -> str:
    return "\n".join(
        [
            "[Desktop Entry]",
            "Type=Application",
            "Name=Project Forge Neon Command Board",
            "Comment=Generate the Project Forge Neon command board artifact",
            "Exec=sh -lc 'cd /mnt/storage/Cole/Projects/project-forge-registry && PYTHONPATH=src python3 -m project_forge_registry.neon_command_board'",
            "Terminal=false",
            "Categories=Utility;",
            "",
        ]
    )


def summarize_content(content: str) -> dict[str, Any]:
    lines = content.splitlines()
    exec_lines = [line for line in lines if line.startswith("Exec=")]
    return {
        "line_count": len(lines),
        "name": "Project Forge Neon Command Board",
        "exec_summary": exec_lines[0] if exec_lines else "missing Exec line",
        "launches_now": False,
        "notes": "Proposed desktop entry content only; no launch behavior is performed by this command.",
    }


def build_backup_plan(target_path: str | None, backup_path: str | None = None) -> dict[str, Any]:
    target = target_path or APPROVED_TARGET
    planned = backup_path or f"{target}.bak.<timestamp>"
    return {
        "target_path": target,
        "backup_path": planned,
        "backup_before_overwrite": True,
        "backup_created": False,
        "status": "planned in dry-run; required before real apply",
    }


def build_rollback_plan(target_path: str | None, backup_path: str | None = None) -> dict[str, Any]:
    target = target_path or APPROVED_TARGET
    planned = backup_path or f"{target}.bak.<timestamp>"
    return {
        "target_path": target,
        "restore_from": planned,
        "rollback_required": True,
        "rollback_executed": False,
        "status": "planned in dry-run; operator must review before real apply",
    }


def required_guards() -> list[str]:
    return [
        "--apply",
        "--yes-replace-launcher",
        f'--approval-phrase "{APPROVAL_PHRASE}"',
        f"--target-path {APPROVED_TARGET}",
        "--confirm-target-path exactly matching --target-path",
        "--clean-git-tree-confirmed after operator verifies clean git working tree",
        "--expected-head or --expected-tag",
        "Phase 11H.4 preflight artifact present",
        "proposed target included in preflight artifact",
        "backup path defined",
        "rollback plan defined",
        "no ambiguous target class",
        "no request to launch, open, enable, disable, or reload anything",
    ]


def guard_status(options: ApplyOptions, preflight: dict[str, Any] | None, preflight_error: str | None) -> list[dict[str, Any]]:
    target = options.target_path
    backup_plan = build_backup_plan(target, str(options.backup_path) if options.backup_path else None)
    rollback_plan = build_rollback_plan(target, str(options.backup_path) if options.backup_path else None)
    statuses = [
        ("--apply", options.apply_requested, "real apply flag"),
        ("--yes-replace-launcher", options.yes_replace_launcher, "explicit replacement approval flag"),
        ("exact approval phrase required", options.approval_phrase == APPROVAL_PHRASE, "approval phrase must match exactly"),
        ("target path is approved target", target == APPROVED_TARGET, "target path must match proposed approved target"),
        (
            "exact target path confirmation required",
            bool(target) and options.confirm_target_path == target,
            "confirm-target-path must exactly match target-path",
        ),
        ("clean git tree required", options.clean_git_tree_confirmed, "operator must verify clean git tree first"),
        (
            "expected HEAD or expected tag confirmation",
            bool(options.expected_head or options.expected_tag),
            "operator must provide expected HEAD or tag guard",
        ),
        ("prior 11H.4 preflight artifact present", preflight_error is None, preflight_error or "checked"),
        (
            "proposed target included in preflight artifact",
            target_in_preflight(preflight, target),
            "target must be present in Phase 11H.4 proposed_targets",
        ),
        ("backup path defined", bool(backup_plan["backup_path"]), "backup before overwrite"),
        ("rollback plan defined", bool(rollback_plan["restore_from"]), "rollback required"),
        ("no ambiguous target class", target == APPROVED_TARGET, "only the approved desktop entry target is supported"),
        (
            "no launch/open/enable/disable/reload request",
            not (
                options.launch_requested
                or options.open_requested
                or options.enable_requested
                or options.disable_requested
                or options.reload_requested
            ),
            "no launch behavior, no --open, no systemd changes",
        ),
    ]
    return [
        {
            "guard": guard,
            "passed": bool(passed),
            "note": note,
        }
        for guard, passed, note in statuses
    ]


def refusal_conditions(statuses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "condition": item["guard"],
            "triggered": not item["passed"],
            "note": item["note"],
        }
        for item in statuses
    ]


def real_apply_available(statuses: list[dict[str, Any]]) -> bool:
    return all(item["passed"] for item in statuses)


def build_payload(*, options: ApplyOptions, root: Path | None = None) -> dict[str, Any]:
    root = (root or repo_root()).resolve()
    preflight_path = resolve_repo_path(PREFLIGHT_PATH, root=root)
    preflight, preflight_error = read_json_artifact(preflight_path)
    artifact = checked_artifact(PREFLIGHT_PATH, preflight, preflight_error)
    content = options.replacement_content if options.replacement_content is not None else generated_content()
    backup = build_backup_plan(options.target_path, str(options.backup_path) if options.backup_path else None)
    rollback = build_rollback_plan(options.target_path, str(options.backup_path) if options.backup_path else None)
    statuses = guard_status(options, preflight, preflight_error)
    available = real_apply_available(statuses)
    mutates = bool(options.apply_requested and available)
    approval_status = "accepted_for_guarded_apply" if available else "missing_or_incomplete"
    return {
        "phase": PHASE,
        "mode": MODE_APPLY if options.apply_requested else MODE_DRY_RUN,
        "dry_run": not mutates,
        "apply_requested": options.apply_requested,
        "real_apply_available": available,
        "mutates_state": mutates,
        "target_path": options.target_path or APPROVED_TARGET,
        "confirm_target_path": options.confirm_target_path,
        "approval_phrase_required": APPROVAL_PHRASE,
        "approval_phrase_status": approval_status,
        "required_guards": required_guards(),
        "guard_status": statuses,
        "prior_artifacts_checked": [artifact],
        "proposed_file_content_summary": summarize_content(content),
        "backup_plan": backup,
        "rollback_plan": rollback,
        "refusal_conditions": refusal_conditions(statuses),
        "safety": SAFETY,
        "recommended_next_step": (
            "Review this dry-run report. Run real apply only in a later operator-controlled terminal "
            "with every guard satisfied; do not launch or open anything as part of apply."
        ),
    }


def render_bool(value: bool) -> str:
    return "yes" if value else "no"


def render_guard_status(items: list[dict[str, Any]]) -> str:
    return "\n".join(f"- {item['guard']}: `{render_bool(item['passed'])}` - {item['note']}" for item in items)


def render_refusals(items: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- {item['condition']}: triggered `{render_bool(bool(item['triggered']))}`"
        for item in items
    )


def render_artifacts(items: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{item['path']}` - {'present' if item['present'] else 'missing/refusal'}; phase: `{item.get('phase') or 'unknown'}`"
        for item in items
    )


def render_report(payload: dict[str, Any]) -> str:
    backup = payload["backup_plan"]
    rollback = payload["rollback_plan"]
    content = payload["proposed_file_content_summary"]
    return f"""# Neon Command Board Launcher Apply Dry Run

## Purpose

Phase 11H.5 implements guarded launcher replacement apply command capability.
The command defaults to dry-run and writes repo-local reports.

## Mode / Safety

Mode: {payload['mode']}.

This is a guarded launcher replacement apply command with default dry-run,
no real apply unless all guards pass, no mutation during dry-run, no launch
behavior, no --open, no systemd changes, no desktop entry changes unless
explicitly approved, no autostart changes unless explicitly approved, backup
before overwrite, rollback required, no delete, no vault writes, exact approval
phrase required, exact target path confirmation required, and clean git tree
required.

## Current Baseline

- Current phase: Phase 11H.5
- Previous stable phase: Phase 11H.4 launcher apply preflight dry-run
- Previous stable HEAD: `d35b601 Add Phase 11H.4 launcher apply preflight dry-run`
- Previous stable version tag: `v0.11.0h4-launcher-apply-preflight-dry-run`
- Previous stable checkpoint: `checkpoint-20260601-175501-phase-11h4-launcher-apply-preflight-dry-run`
- Obsidian no-clobber conflict remains recorded and unresolved.

## Prior Artifacts Checked

{render_artifacts(payload['prior_artifacts_checked'])}

## Target Path Under Review

- Target path: `{payload['target_path'] or APPROVED_TARGET}`
- Confirm target path: `{payload['confirm_target_path'] or ''}`
- Exact target path confirmation required: `{render_bool(bool(payload['confirm_target_path'] and payload['confirm_target_path'] == payload['target_path']))}`

## Guard Requirements

{chr(10).join(f"- {guard}" for guard in payload['required_guards'])}

## Guard Status

{render_guard_status(payload['guard_status'])}

## Proposed File Content Summary

- Name: {content['name']}
- Line count: `{content['line_count']}`
- Exec summary: `{content['exec_summary']}`
- Launches now: `{render_bool(content['launches_now'])}`
- Notes: {content['notes']}

## Backup Plan

- Target path: `{backup['target_path']}`
- Backup path: `{backup['backup_path']}`
- Backup before overwrite: `{render_bool(backup['backup_before_overwrite'])}`
- Backup created: `{render_bool(backup['backup_created'])}`
- Status: {backup['status']}

## Rollback Plan

- Target path: `{rollback['target_path']}`
- Restore from: `{rollback['restore_from']}`
- Rollback required: `{render_bool(rollback['rollback_required'])}`
- Rollback executed: `{render_bool(rollback['rollback_executed'])}`
- Status: {rollback['status']}

## Refusal Conditions

{render_refusals(payload['refusal_conditions'])}

## Apply Availability

- Apply requested: `{render_bool(payload['apply_requested'])}`
- Real apply available: `{render_bool(payload['real_apply_available'])}`
- Mutates state: `{render_bool(payload['mutates_state'])}`
- Dry-run: `{render_bool(payload['dry_run'])}`

## Non-Goals

- no launch behavior
- no --open
- no systemd changes
- no desktop entry changes unless explicitly approved
- no autostart changes unless explicitly approved
- no delete
- no vault writes
- no remotes
- no Obsidian conflict resolution

## Recommended Operator Next Step

{payload['recommended_next_step']}
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report(payload), encoding="utf-8")


def timestamped_backup_path(target: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return target.with_name(f"{target.name}.bak.{timestamp}")


def perform_guarded_apply(target: Path, backup: Path, content: str) -> dict[str, Any]:
    existing = target.read_text(encoding="utf-8")
    backup.write_text(existing, encoding="utf-8")
    target.write_text(content, encoding="utf-8")
    return {
        "backup_created": True,
        "target_written": True,
        "backup_path": str(backup),
        "target_path": str(target),
    }


def run_apply(
    *,
    options: ApplyOptions,
    root: Path | None = None,
    report_path: Path = DEFAULT_REPORT_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> tuple[dict[str, Any], int]:
    root = (root or repo_root()).resolve()
    payload = build_payload(options=options, root=root)
    exit_code = 0
    if options.apply_requested:
        if not payload["real_apply_available"]:
            exit_code = 2
        else:
            target = options.real_target_path or Path(options.target_path or "").expanduser()
            backup = options.backup_path or timestamped_backup_path(target)
            content = options.replacement_content if options.replacement_content is not None else generated_content()
            result = perform_guarded_apply(target, backup, content)
            payload["apply_result"] = result
            payload["mutates_state"] = True
            payload["dry_run"] = False
            payload["backup_plan"]["backup_path"] = result["backup_path"]
            payload["backup_plan"]["backup_created"] = True
    report_output = resolve_repo_path(report_path, root=root)
    json_output = resolve_repo_path(json_path, root=root)
    write_report(report_output, payload)
    write_json(json_output, payload)
    return payload, exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-neon-command-board-launcher-apply")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--yes-replace-launcher", action="store_true")
    parser.add_argument("--approval-phrase", default=None)
    parser.add_argument("--target-path", default=None)
    parser.add_argument("--confirm-target-path", default=None)
    parser.add_argument("--expected-head", default=None)
    parser.add_argument("--expected-tag", default=None)
    parser.add_argument("--clean-git-tree-confirmed", action="store_true")
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--json-path", default=str(DEFAULT_JSON_PATH))
    parser.add_argument("--launch", action="store_true")
    parser.add_argument("--open", dest="open_requested", action="store_true")
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--disable", action="store_true")
    parser.add_argument("--reload", action="store_true")
    return parser


def options_from_args(args: argparse.Namespace) -> ApplyOptions:
    return ApplyOptions(
        apply_requested=bool(args.apply),
        yes_replace_launcher=bool(args.yes_replace_launcher),
        approval_phrase=args.approval_phrase,
        target_path=args.target_path,
        confirm_target_path=args.confirm_target_path,
        expected_head=args.expected_head,
        expected_tag=args.expected_tag,
        clean_git_tree_confirmed=bool(args.clean_git_tree_confirmed),
        launch_requested=bool(args.launch),
        open_requested=bool(args.open_requested),
        enable_requested=bool(args.enable),
        disable_requested=bool(args.disable),
        reload_requested=bool(args.reload),
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload, exit_code = run_apply(
        options=options_from_args(args),
        report_path=Path(args.report_path),
        json_path=Path(args.json_path),
    )
    print("project-forge-neon-command-board-launcher-apply completed")
    print(f"mode: {payload['mode']}")
    print("safety confirmation: default dry-run; no real apply unless all guards pass")
    print(f"apply requested: {render_bool(payload['apply_requested'])}")
    print(f"real apply available: {render_bool(payload['real_apply_available'])}")
    print(f"mutates state: {render_bool(payload['mutates_state'])}")
    print(f"report path: {resolve_repo_path(args.report_path, root=repo_root())}")
    print(f"json path: {resolve_repo_path(args.json_path, root=repo_root())}")
    if exit_code:
        print("result: refusal report generated")
    else:
        print("result: dry-run report generated" if payload["dry_run"] else "result: guarded apply completed")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
