---
title: "SteelSeries_RGB - Agent Handoff"
aliases:
  - "SteelSeries_RGB - Agent Handoff"
---
# SteelSeries_RGB - Agent Handoff

## Scope

- Project slug: `steelseries_rgb`
- Local path: `/mnt/storage/Cole/Projects/SteelSeries_RGB`
- Current lane: docs enrichment and dry-run sync planning

## Current State

- Status: `review`
- Category: `active_project`
- Mirror docs upgraded with explicit `needs review` boundaries.

## Safe Commands

```bash
code "/home/cole/.config/Code/User/workspaces/steelseries_rgb.code-workspace"
code-steelseries_rgb
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug steelseries_rgb
```

## Do Not Touch

- Do not write to real Obsidian vault without explicit apply approval.
- Do not modify external project folders from this workflow.
- Do not include code, secrets, logs, or databases in mirror docs.
- Do not claim unverified hardware capabilities as confirmed.

## Next Suggested Agent Task

Use approved qualification notes to replace `needs review` sections with verified operator guidance.
