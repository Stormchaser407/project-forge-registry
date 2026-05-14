---
project_slug: "project_forge_registry"
category: "active_project"
status: "review"
local_path: "/mnt/storage/Cole/Projects/project-forge-registry"
launcher_command: "code-project_forge_registry"
workspace_path: "/home/cole/.config/Code/User/workspaces/project_forge_registry.code-workspace"
sync_policy: "docs_only / export_only"
---

# project-forge-registry - Project Home

- [[Project Command Board]]
- [[project-forge-registry - Demo Script]]
- [[project-forge-registry - Architecture]]
- [[project-forge-registry - Decisions]]
- [[project-forge-registry - Roadmap]]
- [[project-forge-registry - Agent Handoff]]
- [[project-forge-registry - Runbook]]
- [[project-forge-registry - Changelog]]

## Purpose

Project Forge Registry is the safety-first control plane for organizing local projects before higher-risk automation is introduced.

## Current Status

- Registry status: `review`
- Category: `active_project`
- Proposed mirror path: `/home/cole/main_vault/10 Projects/project_forge_registry`
- Docs sync lane: controlled, markdown-only, dry-run-first

## What This Project Does

- Scans project roots and inventories candidate projects.
- Classifies projects into operational categories.
- Protects special cases such as Cerberus from normal automation.
- Generates VS Code workspaces and launchers for approved entries.
- Generates project passport proposals.
- Generates Obsidian mirror proposal files.
- Performs controlled markdown-only sync planning to Obsidian.
- Prepares future GitHub/Codeberg policy work without enabling remote sync by default.

## Why It Matters

This project creates order before automation. Instead of pushing changes across many folders and systems immediately, it produces inspectable artifacts, clear guardrails, and reversible steps.

## Current Risks / Watch Items

- Misclassification risk for unfamiliar folders still requires manual review.
- Cerberus paths must remain in protected handling modes.
- Obsidian sync must stay markdown-only until broader policies are approved.
- Remote sync (GitHub/Codeberg) remains intentionally deferred until safety gates are explicit.

## Operator Quickstart

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

## Working Style

- Dry-run first.
- Review artifacts before apply.
- Keep docs-only lanes separate from code and operations lanes.
- Avoid touching external project folders during registry workflows.

## Links and Commands

- Local path: `/mnt/storage/Cole/Projects/project-forge-registry`
- Workspace path: `/home/cole/.config/Code/User/workspaces/project_forge_registry.code-workspace`
- Launcher command: `code-project_forge_registry`
- Sync policy: `docs_only / export_only`

```bash
code "/home/cole/.config/Code/User/workspaces/project_forge_registry.code-workspace"
code-project_forge_registry
```
