---
title: "media-dedupe - Demo Script"
aliases:
  - "media-dedupe - Demo Script"
---
# media-dedupe - Demo Script

## Thirty-Second Version

`media-dedupe` is treated as a likely duplicate-media utility project in the registry. This demo focuses on safe project framing and verified documentation boundaries.

## Why This Exists

- Media duplicates are a common operational pain point.
- Teams need clear understanding of tool intent before execution-level trust.

## Demo Flow

1. Open workspace and launcher.
2. Show registry status and mirror docs scope.
3. Call out verified facts vs `needs review` items.
4. Run dry-run sync command and show report output.

## Demo Commands

```bash
code "/home/cole/.config/Code/User/workspaces/media_dedupe.code-workspace"
code-media_dedupe
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug media_dedupe
```

## Known vs Needs Review

- Known: project is tracked, active, and present in controlled docs-sync lanes.
- Needs review: exact dedupe algorithms, safety behavior, and operational limits.

## Next Build Step

After project review, add a verified one-page capability map with safe usage boundaries.
