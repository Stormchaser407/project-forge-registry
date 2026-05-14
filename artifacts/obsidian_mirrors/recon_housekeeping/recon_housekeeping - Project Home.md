---
project_slug: "recon_housekeeping"
category: "active_project"
status: "review"
local_path: "/mnt/storage/Cole/Projects/recon_housekeeping"
launcher_command: "code-recon_housekeeping"
workspace_path: "/home/cole/.config/Code/User/workspaces/recon_housekeeping.code-workspace"
sync_policy: "docs_only / export_only"
---

# recon_housekeeping - Project Home

- [[Project Command Board]]
- [[recon_housekeeping - Demo Script]]
- [[recon_housekeeping - Architecture]]
- [[recon_housekeeping - Decisions]]
- [[recon_housekeeping - Roadmap]]
- [[recon_housekeeping - Agent Handoff]]
- [[recon_housekeeping - Runbook]]
- [[recon_housekeeping - Changelog]]

## Purpose

`recon_housekeeping` is the local-first housekeeping and consolidation workspace for repo-sprawl triage, SITREPs, archaeology, and cleanup decision tracking.

## Current Status

- Registry status: `review`
- Category: `active_project`
- Proposed mirror path: `/home/cole/main_vault/10 Projects/recon_housekeeping`
- Documentation lane: showroom/memory-layer docs with controlled markdown-only sync planning

## What This Project Does

- Supports safe consolidation planning across sprawling local project directories.
- Captures archaeology findings and operational SITREP context.
- Preserves cleanup decisions so future work does not repeat earlier mistakes.

## Why It Matters

- Reduces chaos during consolidation efforts.
- Improves continuity between operators and agents.
- Gives cleanup efforts an auditable, human-readable decision trail.

## Current Risks / Watch Items

- Classification and cleanup recommendations still require human validation before action.
- Consolidation work can unintentionally remove useful context if not tracked carefully.
- Mirror docs must stay docs-only with no source code, secrets, logs, or databases.

## Next Actions

1. Continue recording archaeology outcomes and cleanup decisions in structured notes.
2. Validate high-priority consolidation candidates before any destructive operations.
3. Keep Obsidian sync in dry-run mode until apply is explicitly approved.

## Demo Notes

- Start with the problem: many repos, uncertain overlap, and hidden cleanup risk.
- Show the safe command/report flow that creates confidence before changes.
- End with review checkpoints, not automation hype.

## Links and Commands

- Local path: `/mnt/storage/Cole/Projects/recon_housekeeping`
- Workspace path: `/home/cole/.config/Code/User/workspaces/recon_housekeeping.code-workspace`
- Launcher command: `code-recon_housekeeping`
- Sync policy: `docs_only / export_only`

```bash
code "/home/cole/.config/Code/User/workspaces/recon_housekeeping.code-workspace"
code-recon_housekeeping

PYTHONPATH=src python3 -m unittest discover -s tests
./scripts/project-scan
PYTHONPATH=src python3 -m project_forge_registry.workspace_generation --dry-run --input-json artifacts/project_scan_report.json
PYTHONPATH=src python3 -m project_forge_registry.passport_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug recon_housekeeping
```
