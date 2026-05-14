---
title: "recon_housekeeping - Runbook"
aliases:
  - "recon_housekeeping - Runbook"
---
# recon_housekeeping - Runbook

## Open Project

```bash
code "/home/cole/.config/Code/User/workspaces/recon_housekeeping.code-workspace"
code-recon_housekeeping
```

## Common Commands

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug recon_housekeeping
```

## Test Commands

- Run full tests before changing sync or generation behavior.
- Keep docs-sync checks in dry-run mode for this phase.

## Recovery Notes

- If notes drift from current cleanup reality, mark sections as `needs review` and re-validate.
- If generated docs are overwritten, regenerate then re-apply approved enrichment.
- Keep scope limited to this repo’s mirror artifact paths.
