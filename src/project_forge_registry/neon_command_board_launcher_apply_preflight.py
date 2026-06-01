"""Phase 11H.4 dry-run/preflight only for guarded launcher replacement.

Safety language for validation and operator review: Phase 11H.4,
dry-run/preflight only, no real apply, no replacement, no mutation, no backups
created, simulated backup manifest, simulated rollback plan, no autostart
changes, no systemd changes, no desktop entry changes, no --open, no launch
behavior, no vault writes, approval phrase inert in 11H.4, real apply remains
future phase only, all-or-nothing preflight.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PHASE = "Phase 11H.4"
MODE = "dry-run/preflight only"
APPROVAL_PHRASE = "APPROVE 11H.4 GUARDED LAUNCHER REPLACEMENT APPLY"
DEFAULT_REPORT_PATH = Path("artifacts/neon_command_board_launcher_apply_preflight.md")
DEFAULT_JSON_PATH = Path("artifacts/neon_command_board_launcher_apply_preflight.json")

DISCOVERY_PATH = Path("artifacts/neon_command_board_launcher_discovery.json")
REVIEW_PLAN_PATH = Path("artifacts/neon_command_board_replacement_review_plan.json")
DESIGN_PATH = Path("artifacts/neon_command_board_guarded_launcher_apply_design.json")

APPROVED_TARGET_CLASSES = (
    {
        "category": "user_desktop_entry",
        "label": "approved user-local desktop entries",
        "approved_directory": "~/.local/share/applications",
    },
    {
        "category": "user_autostart",
        "label": "approved user-local autostart entries",
        "approved_directory": "~/.config/autostart",
    },
    {
        "category": "user_systemd",
        "label": "approved user-local systemd user units",
        "approved_directory": "~/.config/systemd/user",
    },
)

SAFETY = {
    "dry-run/preflight only": True,
    "no real apply": True,
    "no replacement": True,
    "no mutation": True,
    "no backups created": True,
    "simulated backup manifest": True,
    "simulated rollback plan": True,
    "no autostart changes": True,
    "no systemd changes": True,
    "no desktop entry changes": True,
    "no --open": True,
    "no launch behavior": True,
    "no vault writes": True,
    "approval phrase inert in 11H.4": True,
    "real apply remains future phase only": True,
    "all-or-nothing preflight": True,
}


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


def checked_artifact_entry(label: str, path: Path, payload: dict[str, Any] | None, error: str | None) -> dict[str, Any]:
    return {
        "label": label,
        "path": str(path),
        "present": error is None,
        "phase": payload.get("phase") if payload else None,
        "status": "checked" if error is None else "refusal",
        "error": error,
    }


def candidate_targets(discovery: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not discovery:
        return []
    candidates = discovery.get("candidates", [])
    if not isinstance(candidates, list):
        return []
    approved_categories = {item["category"] for item in APPROVED_TARGET_CLASSES}
    output: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        category = str(candidate.get("category", ""))
        path = str(candidate.get("path", ""))
        output.append(
            {
                "path": path,
                "category": category,
                "target": candidate.get("target"),
                "source_status": candidate.get("status"),
                "matched_terms": candidate.get("matched_terms", []),
                "approved_target_class": category in approved_categories,
                "preflight_classification": classify_candidate(path=path, category=category),
            }
        )
    return output


def classify_candidate(*, path: str, category: str) -> str:
    if category == "user_desktop_entry" and path == "~/.local/share/applications/project-forge-command-board.desktop":
        return "primary operator-reviewed old launcher candidate"
    if category == "user_desktop_entry":
        return "related desktop entry candidate; review only"
    if category == "user_autostart":
        return "approved class candidate; no target selected"
    if category == "user_systemd":
        return "approved class candidate; no target selected"
    if category == "repo_launcher":
        return "repo-local command candidate; not a file target for apply"
    return "reference or unsupported class; not proposed for apply"


def proposed_targets(review_plan: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not review_plan:
        return []
    old_targets = review_plan.get("old_target_candidates", [])
    if not isinstance(old_targets, list):
        return []
    output: list[dict[str, Any]] = []
    for target in old_targets:
        if not isinstance(target, dict):
            continue
        path = str(target.get("path", ""))
        output.append(
            {
                "path": path,
                "category": "user_desktop_entry",
                "operator_review_required": bool(target.get("operator_review_required", True)),
                "proposed_action": "future guarded replacement candidate only",
                "preflight_status": "review_required_no_apply",
                "exact_target_path_confirmed": False,
            }
        )
    return output


def simulated_backup_manifest(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for target in targets:
        target_path = str(target.get("path", ""))
        manifest.append(
            {
                "target_path": target_path,
                "backup_path": f"{target_path}.bak.<timestamp>",
                "backup_created": False,
                "original_hash_recorded": False,
                "status": "simulated only; no backups created",
            }
        )
    return manifest


def simulated_diff_review(targets: list[dict[str, Any]], review_plan: dict[str, Any] | None) -> dict[str, Any]:
    neon_targets = []
    if review_plan and isinstance(review_plan.get("neon_target_candidates"), list):
        neon_targets = review_plan["neon_target_candidates"]
    return {
        "diff_generated": False,
        "status": "simulated review only; no replacement content generated",
        "changed_files": [target.get("path") for target in targets],
        "old_content_summary": "existing launcher content would be summarized in a future real apply phase",
        "new_content_summary": "future Neon launcher behavior must be operator-reviewed before real apply",
        "neon_target_candidates": neon_targets,
    }


def simulated_rollback_plan(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "target_path": target.get("path"),
            "restore_source": f"{target.get('path')}.bak.<timestamp>",
            "rollback_executed": False,
            "hash_verification": "future phase required",
            "status": "simulated rollback plan only",
        }
        for target in targets
    ]


def refusal_conditions(
    *,
    prior_artifacts: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    discovery: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    missing_artifacts = [item["path"] for item in prior_artifacts if not item["present"]]
    approved_categories = {item["category"] for item in APPROVED_TARGET_CLASSES}
    outside_approved = [
        target.get("path")
        for target in targets
        if target.get("category") not in approved_categories
    ]
    ambiguous = [
        target.get("path")
        for target in targets
        if not target.get("path") or target.get("exact_target_path_confirmed") is not True
    ]
    generated: list[dict[str, Any]] = [
        {
            "condition": "dirty repo",
            "triggered": False,
            "note": "operator still must run git status before any future phase",
        },
        {
            "condition": "missing prior artifact",
            "triggered": bool(missing_artifacts),
            "details": missing_artifacts,
        },
        {
            "condition": "missing approved target",
            "triggered": not targets,
            "details": [] if targets else ["no reviewed old target from replacement review plan"],
        },
        {
            "condition": "target path outside approved user-local directories",
            "triggered": bool(outside_approved),
            "details": outside_approved,
        },
        {
            "condition": "symlink ambiguity",
            "triggered": False,
            "note": "not inspected in Phase 11H.4 dry-run/preflight only",
        },
        {
            "condition": "unreadable target",
            "triggered": False,
            "note": "not inspected in Phase 11H.4 dry-run/preflight only",
        },
        {
            "condition": "missing backup path",
            "triggered": False,
            "note": "simulated backup manifest defines proposed backup paths only",
        },
        {
            "condition": "missing rollback plan",
            "triggered": False,
            "note": "simulated rollback plan generated",
        },
        {
            "condition": "missing exact approval phrase",
            "triggered": True,
            "note": "approval phrase inert in 11H.4; real apply remains future phase only",
        },
        {
            "condition": "generated plan older than latest discovery",
            "triggered": False,
            "note": "mtime comparison intentionally not used; artifacts are checked by presence and phase",
        },
        {
            "condition": "Obsidian conflict confused with launcher work",
            "triggered": False,
            "note": "recorded conflict remains out of scope and unresolved",
        },
        {
            "condition": "request to run --open or launch UI as part of apply",
            "triggered": False,
            "note": "no --open and no launch behavior",
        },
    ]
    if discovery is None:
        generated.append(
            {
                "condition": "candidate discovery unavailable",
                "triggered": True,
                "note": "preflight package generated as skipped/refusal report",
            }
        )
    if ambiguous:
        generated.append(
            {
                "condition": "exact target path not confirmed for real apply",
                "triggered": True,
                "details": ambiguous,
            }
        )
    return generated


def all_or_nothing_preflight(refusals: list[dict[str, Any]]) -> dict[str, Any]:
    triggered = [item for item in refusals if item.get("triggered")]
    return {
        "result": "blocked_for_real_apply_review_ready_for_dry_run",
        "passes_for_real_apply": False,
        "passes_for_dry_run_report": True,
        "triggered_refusal_count": len(triggered),
        "triggered_refusals": [item["condition"] for item in triggered],
        "summary": "all-or-nothing preflight report generated; no real apply is available in Phase 11H.4",
    }


def build_preflight(*, root: Path | None = None, approval_phrase: str | None = None) -> dict[str, Any]:
    root = (root or repo_root()).resolve()
    discovery_path = resolve_repo_path(DISCOVERY_PATH, root=root)
    review_path = resolve_repo_path(REVIEW_PLAN_PATH, root=root)
    design_path = resolve_repo_path(DESIGN_PATH, root=root)

    discovery, discovery_error = read_json_artifact(discovery_path)
    review_plan, review_error = read_json_artifact(review_path)
    design, design_error = read_json_artifact(design_path)
    prior = [
        checked_artifact_entry("Phase 11H.1 discovery", DISCOVERY_PATH, discovery, discovery_error),
        checked_artifact_entry("Phase 11H.2 replacement review plan", REVIEW_PLAN_PATH, review_plan, review_error),
        checked_artifact_entry("Phase 11H.3 guarded apply design", DESIGN_PATH, design, design_error),
    ]

    candidates = candidate_targets(discovery)
    targets = proposed_targets(review_plan)
    backups = simulated_backup_manifest(targets)
    rollbacks = simulated_rollback_plan(targets)
    diffs = simulated_diff_review(targets, review_plan)
    refusals = refusal_conditions(prior_artifacts=prior, targets=targets, discovery=discovery)
    preflight = all_or_nothing_preflight(refusals)

    return {
        "phase": PHASE,
        "mode": MODE,
        "dry_run": True,
        "preflight_only": True,
        "real_apply_available": False,
        "mutates_state": False,
        "approval_phrase": approval_phrase or APPROVAL_PHRASE,
        "approval_phrase_status": "inert_in_11h4",
        "prior_artifacts_checked": prior,
        "approved_target_classes": list(APPROVED_TARGET_CLASSES),
        "candidate_targets": candidates,
        "proposed_targets": targets,
        "simulated_backup_manifest": backups,
        "simulated_diff_review": diffs,
        "simulated_rollback_plan": rollbacks,
        "refusal_conditions": refusals,
        "all_or_nothing_preflight": preflight,
        "recommended_next_phase": (
            "Phase 11H.5 - guarded launcher replacement apply, only after explicit operator approval."
        ),
        "safety": SAFETY,
    }


def render_bool(value: bool) -> str:
    return "yes" if value else "no"


def render_artifacts(items: list[dict[str, Any]]) -> str:
    lines = []
    for item in items:
        status = "present" if item["present"] else f"missing/refusal: {item['error']}"
        phase = item.get("phase") or "unknown"
        lines.append(f"- `{item['path']}` - {status}; phase: `{phase}`")
    return "\n".join(lines)


def render_classes(items: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- {item['label']} - `{item['approved_directory']}` (`{item['category']}`)"
        for item in items
    )


def render_candidates(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- none found; preflight skipped for missing discovery evidence"
    lines = []
    for item in items:
        approved = "approved class" if item["approved_target_class"] else "not an apply target class"
        lines.append(
            f"- `{item['path']}` - `{item['category']}`; {approved}; "
            f"{item['preflight_classification']}"
        )
    return "\n".join(lines)


def render_proposed(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- none; no real apply target is approved"
    return "\n".join(
        f"- `{item['path']}` - {item['proposed_action']}; "
        f"status: `{item['preflight_status']}`"
        for item in items
    )


def render_backups(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- none; no backups created"
    return "\n".join(
        f"- `{item['target_path']}` -> `{item['backup_path']}`; "
        f"backup created: {render_bool(item['backup_created'])}; {item['status']}"
        for item in items
    )


def render_rollbacks(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- none; simulated rollback plan only"
    return "\n".join(
        f"- `{item['target_path']}` restore source `{item['restore_source']}`; "
        f"executed: {render_bool(item['rollback_executed'])}; {item['status']}"
        for item in items
    )


def render_refusals(items: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- {item['condition']}: triggered `{render_bool(bool(item.get('triggered')))}`"
        for item in items
    )


def render_report(preflight: dict[str, Any]) -> str:
    diff = preflight["simulated_diff_review"]
    summary = preflight["all_or_nothing_preflight"]
    return f"""# Neon Command Board Launcher Apply Preflight

## Purpose

Phase 11H.4 adds guarded launcher replacement apply dry-run/preflight only.
It reports what a future guarded launcher replacement would require.

## Mode / Safety

Mode: dry-run/preflight only.

This phase has no real apply, no replacement, no mutation, no backups created,
no autostart changes, no systemd changes, no desktop entry changes, no
--open, no launch behavior, and no vault writes.

The simulated backup manifest and simulated rollback plan are report-only.
The approval phrase inert in 11H.4 status means `{preflight['approval_phrase']}`
is recorded but not accepted as authorization. A real apply remains future phase only.

## Current Baseline

- Phase: Phase 11H.4
- Previous stable phase: Phase 11H.3 guarded launcher apply design
- Previous stable HEAD: `84eafe9 Add Phase 11H.3 guarded launcher apply design`
- Previous stable version tag: `v0.11.0h3-guarded-launcher-apply-design`
- Previous stable checkpoint: `checkpoint-20260601-162837-phase-11h3-guarded-launcher-apply-design`
- Obsidian no-clobber conflict remains recorded and unresolved.

## Prior Artifacts Checked

{render_artifacts(preflight['prior_artifacts_checked'])}

## Approved Target Classes

{render_classes(preflight['approved_target_classes'])}

## Candidate Targets From Discovery

{render_candidates(preflight['candidate_targets'])}

## Proposed Target Review

{render_proposed(preflight['proposed_targets'])}

## Simulated Backup Manifest

{render_backups(preflight['simulated_backup_manifest'])}

No backups created. This is a simulated backup manifest only.

## Simulated Diff/Review Summary

- Diff generated: `{render_bool(diff['diff_generated'])}`
- Status: {diff['status']}
- Changed files list: {', '.join(f"`{item}`" for item in diff['changed_files']) if diff['changed_files'] else 'none'}
- Old content summary: {diff['old_content_summary']}
- New content summary: {diff['new_content_summary']}

## Simulated Rollback Plan

{render_rollbacks(preflight['simulated_rollback_plan'])}

This is a simulated rollback plan only; no rollback commands executed.

## Refusal Conditions

{render_refusals(preflight['refusal_conditions'])}

## All-Or-Nothing Preflight Result

- Result: `{summary['result']}`
- Passes for real apply: `{render_bool(summary['passes_for_real_apply'])}`
- Passes for dry-run report: `{render_bool(summary['passes_for_dry_run_report'])}`
- Triggered refusal count: `{summary['triggered_refusal_count']}`
- Summary: {summary['summary']}

## Operator Approval Phrase Status

- Approval phrase: `{preflight['approval_phrase']}`
- Approval phrase status: approval phrase inert in 11H.4
- The phrase is not accepted as authorization in this phase.

## Non-Goals

- no real apply
- no replacement
- no mutation
- no backups created
- no autostart changes
- no systemd changes
- no desktop entry changes
- no --open
- no launch behavior
- no vault writes
- no remotes
- no Obsidian conflict resolution

## Recommended Next Phase

{preflight['recommended_next_phase']}
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_preflight(
    *,
    root: Path | None = None,
    report_path: Path = DEFAULT_REPORT_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
    approval_phrase: str | None = None,
) -> dict[str, Any]:
    root = (root or repo_root()).resolve()
    payload = build_preflight(root=root, approval_phrase=approval_phrase)
    report_output = resolve_repo_path(report_path, root=root)
    json_output = resolve_repo_path(json_path, root=root)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(render_report(payload), encoding="utf-8")
    write_json(json_output, payload)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-neon-command-board-launcher-apply-preflight")
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--json-path", default=str(DEFAULT_JSON_PATH))
    parser.add_argument(
        "--approval-phrase",
        default=None,
        help="Recorded as inert/not accepted in Phase 11H.4; never authorizes real apply.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    if argv is not None and "--apply" in argv:
        print("error: --apply is rejected; Phase 11H.4 is dry-run/preflight only")
        return 2
    args = parser.parse_args(argv)
    payload = run_preflight(
        report_path=Path(args.report_path),
        json_path=Path(args.json_path),
        approval_phrase=args.approval_phrase,
    )
    print("project-forge-neon-command-board-launcher-apply-preflight completed")
    print("mode: dry-run/preflight only")
    print("safety confirmation: no real apply; no replacement; no mutation; no backups created")
    print("approval phrase status: approval phrase inert in 11H.4")
    print(f"report path: {resolve_repo_path(args.report_path, root=repo_root())}")
    print(f"json path: {resolve_repo_path(args.json_path, root=repo_root())}")
    print(f"candidate targets: {len(payload['candidate_targets'])}")
    print(f"proposed targets: {len(payload['proposed_targets'])}")
    print(f"all-or-nothing preflight: {payload['all_or_nothing_preflight']['result']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
