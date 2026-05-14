---
title: "recon_housekeeping - Agent Handoff"
aliases:
  - "recon_housekeeping - Agent Handoff"
---
# recon_housekeeping - Agent Handoff

## Scope

- Project slug: `recon_housekeeping`
- Local path: `/mnt/storage/Cole/Projects/recon_housekeeping`
- Active lane: docs enrichment and safe sync planning only

## Current State

- Status: `review`
- Category: `active_project`
- Mirror docs upgraded from templates to operator-ready showroom content.

## Safe Commands

```bash
code "/home/cole/.config/Code/User/workspaces/recon_housekeeping.code-workspace"
code-recon_housekeeping
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug recon_housekeeping
```

## Do Not Touch

- Do not write to real Obsidian vault without explicit apply approval.
- Do not modify external project folders from this workflow.
- Do not include code, secrets, logs, or databases in mirror docs.
- Do not attempt GitHub/Codeberg sync here.

## Next Suggested Agent Task

Validate and enrich any section still marked as “needs review” using approved non-sensitive project context.
