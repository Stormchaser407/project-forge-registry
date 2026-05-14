---
title: "project-forge-registry - Demo Script"
aliases:
  - "project-forge-registry - Demo Script"
---
# project-forge-registry - Demo Script

## Thirty-Second Version

Project Forge Registry is a safety-first workflow system that maps local projects, classifies risk, and generates reviewable outputs before any wide automation is allowed.

## Why This Exists

Local project ecosystems grow faster than manual tracking. This system creates a dependable registry so workspace setup, documentation sync, and future remote sync can happen with clear safety gates.

## Demo Flow (Operator-Friendly)

1. Show scanner output as the trusted inventory baseline.
2. Show category/action proposals and highlight manual-review entries.
3. Show generated workspace and launcher planning for approved slugs.
4. Show passport proposals as durable project records.
5. Show Obsidian mirror proposal files as the showroom layer.
6. Show markdown-only sync dry-run for a single approved slug.

## Commands To Run During Demo

```bash
code-project_forge_registry
code-project-forge-command-center

./scripts/project-scan
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m project_forge_registry.workspace_generation --dry-run --input-json artifacts/project_scan_report.json
PYTHONPATH=src python3 -m project_forge_registry.passport_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug project_forge_registry
```

## What Makes It Different

- Registry before automation.
- Dry-run-first as default behavior.
- Explicit protections for sensitive/special-case paths.
- Documentation treated as a controlled product surface, not an afterthought.

## Cool Part To Show First

Show the same slug flowing through phases: scan -> classify -> workspace/passport/mirror generation -> docs-only sync dry-run. It demonstrates an end-to-end system without risky writes.

## Current Limitations

- Final classifications still require human judgment for edge cases.
- Remote sync policies remain intentionally deferred.
- Cross-project docs enrichment is not complete yet.

## Next Build Step

Expand this polished showroom layer to additional approved project slugs and keep sync operations in a controlled markdown-only lane.
