# Project Sync Report (Phase 8.3)

- mode: `dry-run`
- slug: `project_forge_registry`
- passport: `/mnt/storage/Cole/Projects/project-forge-registry/artifacts/project_passports/project_forge_registry.project.yml`
- final_status: `ready_for_operator_review`

## Lane Summary

- requested_lanes: `5`
- unrequested_skipped_lanes: `4`
- passed_lanes: `5`
- failed_or_incomplete_lanes: `0`

## Requested Lanes

- sync_obsidian: `passed`
- export_docs: `passed`
- remote_plan: `passed`
- remote_verify: `passed`
- push_ready: `passed`

## Unrequested Skipped Lanes

- refresh_scan
- refresh_workspace
- refresh_passport
- refresh_mirror

## Passed Lanes

- sync_obsidian
- export_docs
- remote_plan
- remote_verify
- push_ready

## Failed Or Incomplete Lanes

- none

## Child Lane Reports

- refresh_workspace: `artifacts/project_sync_workspace_generation_report.md`
- refresh_passport: `artifacts/project_sync_passport_generation_report.md`
- refresh_mirror: `artifacts/project_sync_obsidian_mirror_generation_report.md`
- sync_obsidian: `artifacts/project_sync_obsidian_sync_report.md`
- export_docs: `artifacts/project_sync_export_sync_report.md`
- remote_plan: `artifacts/project_sync_remote_plan_report.md`
- remote_verify: `artifacts/project_sync_remote_verify_report.md`
- push_ready: `artifacts/project_sync_push_ready_report.md`

## Lane Details

### Refresh Classification
- key: `refresh_scan`
- requested: `false`
- status: `skipped`
- command: `(none)`
- child_report: `n/a`
- return_code: `n/a`
- note: `not requested`

### Refresh Workspace
- key: `refresh_workspace`
- requested: `false`
- status: `skipped`
- command: `/etc/profiles/per-user/cole/bin/python3 -m project_forge_registry.workspace_generation --dry-run --include-slug project_forge_registry --report-name project_sync_workspace_generation_report.md`
- child_report: `artifacts/project_sync_workspace_generation_report.md`
- return_code: `n/a`
- note: `not requested`

### Refresh Passport
- key: `refresh_passport`
- requested: `false`
- status: `skipped`
- command: `/etc/profiles/per-user/cole/bin/python3 -m project_forge_registry.passport_generation --dry-run --include-slug project_forge_registry --report-name project_sync_passport_generation_report.md`
- child_report: `artifacts/project_sync_passport_generation_report.md`
- return_code: `n/a`
- note: `not requested`

### Refresh Obsidian Mirror
- key: `refresh_mirror`
- requested: `false`
- status: `skipped`
- command: `/etc/profiles/per-user/cole/bin/python3 -m project_forge_registry.obsidian_mirror_generation --dry-run --include-slug project_forge_registry --report-name project_sync_obsidian_mirror_generation_report.md`
- child_report: `artifacts/project_sync_obsidian_mirror_generation_report.md`
- return_code: `n/a`
- note: `not requested`

### Obsidian Sync
- key: `sync_obsidian`
- requested: `true`
- status: `passed`
- command: `/etc/profiles/per-user/cole/bin/python3 -m project_forge_registry.obsidian_sync --dry-run --slug project_forge_registry --report-name project_sync_obsidian_sync_report.md`
- child_report: `artifacts/project_sync_obsidian_sync_report.md`
- return_code: `0`
- note: `ok`

### Export Docs
- key: `export_docs`
- requested: `true`
- status: `passed`
- command: `/etc/profiles/per-user/cole/bin/python3 -m project_forge_registry.export_sync --dry-run --slug project_forge_registry --report-name project_sync_export_sync_report.md`
- child_report: `artifacts/project_sync_export_sync_report.md`
- return_code: `0`
- note: `ok`

### Remote Plan
- key: `remote_plan`
- requested: `true`
- status: `passed`
- command: `/etc/profiles/per-user/cole/bin/python3 -m project_forge_registry.remote_policy plan --dry-run --slug project_forge_registry --report-name project_sync_remote_plan_report.md`
- child_report: `artifacts/project_sync_remote_plan_report.md`
- return_code: `0`
- note: `ok`

### Remote Verify
- key: `remote_verify`
- requested: `true`
- status: `passed`
- command: `/etc/profiles/per-user/cole/bin/python3 -m project_forge_registry.remote_policy verify --dry-run --slug project_forge_registry --report-name project_sync_remote_verify_report.md`
- child_report: `artifacts/project_sync_remote_verify_report.md`
- return_code: `0`
- note: `ok`

### Push Ready
- key: `push_ready`
- requested: `true`
- status: `passed`
- command: `/etc/profiles/per-user/cole/bin/python3 -m project_forge_registry.remote_policy push-ready --dry-run --slug project_forge_registry --report-name project_sync_push_ready_report.md`
- child_report: `artifacts/project_sync_push_ready_report.md`
- return_code: `0`
- note: `ok`

## Safety Statement

- Phase 8.3 is dry-run only.
- No push or remote mutation actions are performed by this command.
