# Project Forge Command Board

> Local-first. Dry-run-first. Review before action.

Updated: 2026-05-14 03:07:24

## Current State

Project Forge Registry is operational as a local dry-run command-board system.

Current HEAD:

    d60dc0e Correct safe project-sync dry-run wave summary

Stable operational tags:

    v0.9.0-project-forge-local-operational Operational milestone: Project Forge local dry-run command-board system complete
    v0.9.1-safe-dry-run-wave Optional milestone: corrected safe multi-project dry-run wave complete

## Big Green Button

Safe daily command:

    ./scripts/project-sync-safe

Safe daily command with capture for ChatGPT:

    PROJECT_SYNC_SAFE_CAPTURE=1 ./scripts/project-sync-safe

Specific approved slug:

    ./scripts/project-sync-safe project_forge_registry

## Approved Dry-Run Slugs

- project_forge_registry
- recon_housekeeping
- media_dedupe
- steelseries_rgb

These slugs passed the Phase 9.1 safe dry-run wave with `ready_for_operator_review`.

## Status Meanings

| Status | Meaning | Action |
|---|---|---|
| ready_for_operator_review | Requested dry-run lanes passed. | Review reports; do not assume push approval. |
| incomplete | One or more required dry-run signals are missing or not proven. | Inspect failed/incomplete lanes. |
| blocked | A safety/protection gate stopped the run. | Do not bypass without explicit redesign. |

Important: Project Forge intentionally does not return `ready_to_push` in the current local operational phase.

## Reports To Check

Main report:

    artifacts/project_sync_report.md

Project-sync child reports:

    artifacts/project_sync_obsidian_sync_report.md
    artifacts/project_sync_export_sync_report.md
    artifacts/project_sync_remote_plan_report.md
    artifacts/project_sync_remote_verify_report.md
    artifacts/project_sync_push_ready_report.md

Wave summary:

    artifacts/project_sync_wave_summary.md

Operational checkpoint:

    docs/PROJECT_FORGE_OPERATIONAL_CHECKPOINT.md

Operator runbook:

    docs/PROJECT_SYNC_OPERATOR_RUNBOOK.md

## Safe Commands

Run tests:

    PYTHONPATH=src python3 -m unittest discover -s tests

Run safe wrapper:

    ./scripts/project-sync-safe

Run safe wrapper for approved slug:

    ./scripts/project-sync-safe recon_housekeeping

Check canonical report dirt:

    git status --short artifacts/obsidian_sync_report.md artifacts/export_sync_report.md artifacts/remote_plan_report.md artifacts/remote_verify_report.md artifacts/push_ready_report.md

## Hard Boundaries

Still blocked unless separately designed and approved:

- `--apply` orchestration
- remote setup apply
- GitHub push/fetch
- Codeberg push/fetch
- repo creation
- public release automation
- Cerberus automation
- multi-project apply waves

## Next Session Resume

Start here:

    cd /mnt/storage/Cole/Projects/project-forge-registry
    git status --short
    ./scripts/project-sync-safe

Then paste the wrapper output into ChatGPT.

## Operator Motto

Review-ready is not push-ready. The machine tells you what it sees; the operator decides what it means.
