---
title: "SteelSeries_RGB - Runbook"
aliases:
  - "SteelSeries_RGB - Runbook"
---
# SteelSeries_RGB - Runbook

## Open Project

```bash
code "/home/cole/.config/Code/User/workspaces/steelseries_rgb.code-workspace"
code-steelseries_rgb
```

## Common Commands

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug steelseries_rgb
```

## Test Commands

- Run full test suite before any sync-related changes.
- Keep docs sync in dry-run mode during this phase.

## Recovery Notes

- If a capability statement is uncertain, mark it `needs review` immediately.
- If generated docs are replaced, regenerate then re-apply verified enrichment.
- Keep scope constrained to repository mirror artifacts only.
