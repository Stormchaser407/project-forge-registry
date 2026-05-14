---
title: "project-forge-registry - Runbook"
aliases:
  - "project-forge-registry - Runbook"
---
# project-forge-registry - Runbook

## Open Project

```bash
code "/home/cole/.config/Code/User/workspaces/project_forge_registry.code-workspace"
code-project_forge_registry
code-project-forge-command-center
```

## Daily Safe Flow

1. Confirm repo state and branch.
2. Run tests.
3. Refresh scanner artifacts.
4. Run downstream generators in dry-run mode.
5. Review reports before any apply decision.

## Core Commands

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
./scripts/project-scan
PYTHONPATH=src python3 -m project_forge_registry.workspace_generation --dry-run --input-json artifacts/project_scan_report.json
PYTHONPATH=src python3 -m project_forge_registry.passport_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug project_forge_registry
```

## Report Checks

- `artifacts/project_scan_report.md`
- `artifacts/workspace_launcher_generation_report.md`
- `artifacts/project_passport_generation_report.md`
- `artifacts/obsidian_mirror_generation_report.md`
- `artifacts/obsidian_sync_report.md`

## Safety Checklist

- Dry-run remains the default.
- No external project-folder writes in registry workflow phases.
- No code or secrets moved into Obsidian-facing docs.
- Cerberus protections remain active.
- No force or destructive git operations.

## Recovery Notes

- If a report file was unintentionally overwritten by tests, restore it from git-tracked state and re-run tests.
- If classification outputs shift unexpectedly, inspect scan roots and re-run scanner before further apply planning.
