# Project Sync Operator Runbook

## Purpose

`project-sync` is the safe Project Forge command-board runner. It coordinates proven dry-run lanes for one project slug and produces a combined report.

Repo-local wrapper:

    ./scripts/project-sync-safe

Default slug:

    project_forge_registry

Equivalent module command:

    PYTHONPATH=src python3 -m project_forge_registry.project_sync --dry-run --slug project_forge_registry

## Safe Default Command

    ./scripts/project-sync-safe

For a specific approved slug:

    ./scripts/project-sync-safe project_forge_registry

## What `ready_for_operator_review` Means

`ready_for_operator_review` means the requested dry-run lanes completed successfully and the operator can review the reports.

It does not mean:

- safe to push
- remote setup is approved
- GitHub or Codeberg has been touched
- apply is enabled
- external folders were modified
- protected projects are approved

## What The Safe Wrapper Does

The wrapper runs:

    PYTHONPATH=src python3 -m project_forge_registry.project_sync --dry-run --slug <slug>

It remains dry-run only.

## What The Safe Wrapper Does Not Do

It does not:

- pass `--apply`
- add remotes
- push or fetch
- contact GitHub or Codeberg
- touch Cerberus
- write to external project folders

## Reports

Main report:

    artifacts/project_sync_report.md

Project-sync child reports:

    artifacts/project_sync_obsidian_sync_report.md
    artifacts/project_sync_export_sync_report.md
    artifacts/project_sync_remote_plan_report.md
    artifacts/project_sync_remote_verify_report.md
    artifacts/project_sync_push_ready_report.md

Canonical child-lane reports should remain clean during normal project-sync dry-runs:

    artifacts/obsidian_sync_report.md
    artifacts/export_sync_report.md
    artifacts/remote_plan_report.md
    artifacts/remote_verify_report.md
    artifacts/push_ready_report.md

## What To Paste Back Into ChatGPT

Paste:

1. wrapper output
2. final `git status --short`
3. any failing lane section from `artifacts/project_sync_report.md`

Useful command:

    PROJECT_SYNC_SAFE_CAPTURE=1 ./scripts/project-sync-safe

## Common Troubleshooting

### Console command not on PATH

Use the module form:

    PYTHONPATH=src python3 -m project_forge_registry.project_sync --dry-run --slug project_forge_registry

### `--apply is intentionally disabled`

This is expected in current tests. It proves apply remains blocked.

### Report dirt

Project-sync-specific reports may update. Canonical child reports should not be dirtied by normal `project-sync` dry-runs.

Check:

    git status --short artifacts/obsidian_sync_report.md artifacts/export_sync_report.md artifacts/remote_plan_report.md artifacts/remote_verify_report.md artifacts/push_ready_report.md

### Final status is not `ready_for_operator_review`

Open:

    artifacts/project_sync_report.md

Look at:

- Requested Lanes
- Failed Or Incomplete Lanes
- Lane Details
