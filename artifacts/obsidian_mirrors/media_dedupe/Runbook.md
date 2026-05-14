---
title: "media-dedupe - Runbook"
aliases:
  - "media-dedupe - Runbook"
---
# media-dedupe - Runbook

## Open Project

```bash
code "/home/cole/.config/Code/User/workspaces/media_dedupe.code-workspace"
code-media_dedupe
```

## Common Commands

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug media_dedupe
```

## Test Commands

- Run full tests before workflow or sync changes.
- Keep sync commands in dry-run mode during this phase.

## Recovery Notes

- Treat unknown behavior as `needs review`, not as operator truth.
- If docs are regenerated, re-apply verified enrichment only.
- Keep all changes scoped to repo mirror artifacts.
