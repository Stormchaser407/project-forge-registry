---
title: "recon_housekeeping - Demo Script"
aliases:
  - "recon_housekeeping - Demo Script"
---
# recon_housekeeping - Demo Script

## Thirty-Second Version

`recon_housekeeping` is the safe operating layer for untangling project sprawl. It emphasizes evidence, review checkpoints, and clean handoff notes before any risky cleanup steps.

## Why This Exists

- Consolidation work fails when context is fragmented.
- This project preserves context and rationale while cleanup work is planned.

## Demo Flow

1. Open workspace and launcher.
2. Show how reports and notes frame cleanup decisions.
3. Show dry-run command path for docs sync and explain why apply is gated.
4. Close with explicit “needs human review” checkpoints.

## Demo Commands

```bash
code "/home/cole/.config/Code/User/workspaces/recon_housekeeping.code-workspace"
code-recon_housekeeping
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug recon_housekeeping
```

## Known vs Needs Review

- Known: this is a consolidation and archaeology support lane.
- Needs review: any project-specific cleanup action plans that would alter source folders.

## Next Build Step

Add short, verified before/after housekeeping examples once they are approved for publication.
