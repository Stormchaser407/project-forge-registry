---
title: "project-forge-registry - Agent Handoff"
aliases:
  - "project-forge-registry - Agent Handoff"
---
# project-forge-registry - Agent Handoff

## Scope

- Project slug: `project_forge_registry`
- Local path: `/mnt/storage/Cole/Projects/project-forge-registry`
- Current lane: docs-oriented enrichment and controlled markdown-only sync planning

## Current State

- Status: `review`
- Category: `active_project`
- Phase coverage: scanner, workspace/launcher generation, passport generation, mirror generation, controlled docs-only sync

## Safe Commands

```bash
code "/home/cole/.config/Code/User/workspaces/project_forge_registry.code-workspace"
code-project_forge_registry
code-project-forge-command-center

PYTHONPATH=src python3 -m unittest discover -s tests
./scripts/project-scan
PYTHONPATH=src python3 -m project_forge_registry.workspace_generation --dry-run --input-json artifacts/project_scan_report.json
PYTHONPATH=src python3 -m project_forge_registry.passport_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug project_forge_registry
```

## Do Not Touch

- Do not write to the real Obsidian vault unless an explicit sync apply step is approved.
- Do not copy source code, secrets, env data, logs, or databases into mirror docs.
- Do not modify external project folders from this workflow.
- Do not enable GitHub/Codeberg sync implicitly.

## What The Next Agent Should Do

- Keep improving operator-facing docs quality for approved slugs.
- Verify tests remain side-effect free.
- Keep all automation steps dry-run-first until explicit apply approval is given.
