# Project Forge Registry Operational Checkpoint

Date: 2026-05-14 03:02:28

## Status

Project Forge Registry is now operational as a local, dry-run-first project command-board system.

Current HEAD:

    7a817cc Clean project-sync dry-run test output

Working tree at checkpoint creation:

    clean

## Stable Tags

    v0.8.3-project-sync-artifact-hygiene Stable milestone: Phase 8.3 project-sync artifact hygiene complete
    v0.8.5-project-sync-safe-wrapper Stable milestone: Phase 8.5 safe project-sync wrapper and operator runbook complete
    v0.8.7-project-sync-dry-run-operational Stable milestone: project-sync safe dry-run wrapper operational

## Operationally Safe Daily Command

    ./scripts/project-sync-safe

Equivalent module command:

    PYTHONPATH=src python3 -m project_forge_registry.project_sync --dry-run --slug project_forge_registry

## What The System Can Do Now

- Scan and classify local projects.
- Generate workspace and launcher plans.
- Generate project passport proposals.
- Generate Obsidian mirror proposals.
- Sync generated Markdown-only project docs to Obsidian under controlled rules.
- Export approved Obsidian _export/docs Markdown back into repo docs.
- Plan and verify remote posture without touching remotes.
- Run a push-ready preflight that never returns ready_to_push.
- Coordinate safe default dry-run lanes through project-sync.
- Run the safe wrapper from scripts/project-sync-safe.

## Safe Default project-sync Profile

When no lane flags are provided, project-sync runs the safe default dry-run profile:

- Obsidian sync dry-run
- Export docs dry-run
- Remote plan dry-run
- Remote verify dry-run
- Push-ready dry-run

It does not automatically run refresh/regeneration lanes:

- scanner refresh
- workspace refresh
- passport refresh
- mirror refresh

Those remain explicit because they regenerate artifacts.

## What ready_for_operator_review Means

ready_for_operator_review means the requested dry-run lanes completed successfully and the operator can review the reports.

It does not mean:

- safe to push
- remote setup is approved
- GitHub has been touched
- Codeberg has been touched
- apply is enabled
- external project folders were modified
- protected projects are approved

## Current Safety Boundaries

- dry-run-first
- single-slug-first
- no automatic remotes
- no automatic push/fetch
- no GitHub/Codeberg contact
- no Cerberus handling
- no hidden apply
- no repo-root README overwrite from export sync
- no code copied into Obsidian
- no destination deletes

## Primary Reports

Main orchestration report:

    artifacts/project_sync_report.md

Project-sync child lane reports:

    artifacts/project_sync_obsidian_sync_report.md
    artifacts/project_sync_export_sync_report.md
    artifacts/project_sync_remote_plan_report.md
    artifacts/project_sync_remote_verify_report.md
    artifacts/project_sync_push_ready_report.md

Canonical lane reports should remain clean during normal project-sync dry-runs:

    artifacts/obsidian_sync_report.md
    artifacts/export_sync_report.md
    artifacts/remote_plan_report.md
    artifacts/remote_verify_report.md
    artifacts/push_ready_report.md

## Important Commands

Run full tests:

    PYTHONPATH=src python3 -m unittest discover -s tests

Run safe project-sync wrapper:

    ./scripts/project-sync-safe

Run safe wrapper and capture output for ChatGPT:

    PROJECT_SYNC_SAFE_CAPTURE=1 ./scripts/project-sync-safe

Check canonical report dirt:

    git status --short artifacts/obsidian_sync_report.md artifacts/export_sync_report.md artifacts/remote_plan_report.md artifacts/remote_verify_report.md artifacts/push_ready_report.md

## Still Intentionally Blocked

- remote setup apply
- git push
- git fetch
- GitHub repository creation
- Codeberg repository creation
- multi-project apply waves
- Cerberus automation
- public release automation

## Recommended Optional Work

Optional Phase 9.1: run safe dry-run wrapper against approved slugs.

Optional Phase 9.2: build a friendly command-board/dashboard document for Obsidian.

## Operator Note

This is the first point where the system can be used as a real daily operational posture tool rather than a build project.

Do not confuse review-ready with push-ready.
