---
project_slug: "media_dedupe"
category: "active_project"
status: "review"
local_path: "/mnt/storage/Cole/Projects/media-dedupe"
launcher_command: "code-media_dedupe"
workspace_path: "/home/cole/.config/Code/User/workspaces/media_dedupe.code-workspace"
sync_policy: "docs_only / export_only"
---

# media-dedupe - Project Home

- [[Project Command Board]]
- [[media-dedupe - Demo Script]]
- [[media-dedupe - Architecture]]
- [[media-dedupe - Decisions]]
- [[media-dedupe - Roadmap]]
- [[media-dedupe - Agent Handoff]]
- [[media-dedupe - Runbook]]
- [[media-dedupe - Changelog]]

## Purpose

`media-dedupe` is tracked as a likely duplicate-media utility project. This mirror focuses on safe, high-level context while deeper capabilities are verified.

## Current Status

- Registry status: `review`
- Category: `active_project`
- Proposed mirror path: `/home/cole/main_vault/10 Projects/media_dedupe`
- Documentation lane: showroom/memory-layer docs with controlled markdown-only sync planning

## What This Project Does

- Likely supports duplicate-media detection or organization workflows.
- Provides a candidate utility lane for media cleanup efficiency.
- Detailed feature claims remain `needs review` until confirmed directly in the project.

## Why It Matters

- Duplicate media can consume storage and complicate content management.
- A clear operator-facing summary helps avoid risky assumptions.
- Keeping documentation honest prevents overpromising unknown behavior.

## Current Risks / Watch Items

- Exact matching methods and data handling are not yet verified in this note.
- Any operation that might remove/relocate media requires explicit validation.
- Docs must remain free of sensitive paths, logs, and operational datasets.

## Next Actions

1. Review the project directly and verify supported dedupe workflow boundaries.
2. Update docs from verified behavior only.
3. Keep sync actions in dry-run mode until apply is explicitly approved.

## Demo Notes

- Lead with “what is known” and “what still needs review.”
- Show safe workflow commands rather than hypothetical media operations.

## Links and Commands

- Local path: `/mnt/storage/Cole/Projects/media-dedupe`
- Workspace path: `/home/cole/.config/Code/User/workspaces/media_dedupe.code-workspace`
- Launcher command: `code-media_dedupe`
- Sync policy: `docs_only / export_only`

```bash
code "/home/cole/.config/Code/User/workspaces/media_dedupe.code-workspace"
code-media_dedupe

PYTHONPATH=src python3 -m unittest discover -s tests
./scripts/project-scan
PYTHONPATH=src python3 -m project_forge_registry.workspace_generation --dry-run --input-json artifacts/project_scan_report.json
PYTHONPATH=src python3 -m project_forge_registry.passport_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug media_dedupe
```
