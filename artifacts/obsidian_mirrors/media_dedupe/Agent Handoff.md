---
title: "media-dedupe - Agent Handoff"
aliases:
  - "media-dedupe - Agent Handoff"
---
# media-dedupe - Agent Handoff

## Scope

- Project slug: `media_dedupe`
- Local path: `/mnt/storage/Cole/Projects/media-dedupe`
- Current lane: docs enrichment and dry-run sync planning

## Current State

- Status: `review`
- Category: `active_project`
- Core docs are enriched with explicit `needs review` safeguards.

## Safe Commands

```bash
code "/home/cole/.config/Code/User/workspaces/media_dedupe.code-workspace"
code-media_dedupe
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug media_dedupe
```

## Do Not Touch

- Do not write to real Obsidian vault without explicit apply approval.
- Do not modify external project folders from this workflow.
- Do not add code, secrets, logs, or databases to docs.
- Do not claim unverified capabilities as confirmed.

## Next Suggested Agent Task

Review the project directly and promote only verified behavior into these docs.
