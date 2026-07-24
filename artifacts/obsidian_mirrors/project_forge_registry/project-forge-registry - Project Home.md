---
project_slug: "project_forge_registry"
category: "active_project"
status: "active"
local_path: "/mnt/storage/Cole/Projects/project-forge-registry"
launcher_command: "code-project_forge_registry"
workspace_path: "/home/cole/.config/Code/User/workspaces/project_forge_registry.code-workspace"
sync_policy: "docs_only / export_only"
canonical_charter: "PROJECT_CHARTER.md"
canonical_status: "PROJECT_STATUS.md"
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

## Canonical Authority

- Mission and scope: repository `PROJECT_CHARTER.md`
- Lifecycle and current phase: repository `PROJECT_STATUS.md`
- Agent behavior: repository `AGENTS.md`
- Technical truth: repository state plus verified runtime evidence

## Purpose

Project Forge is the safety-first operational registry for technical projects,
repositories, deployment nodes, mirrors, workspaces, launchers, and machine
readiness.

It discovers and reports technical state. It does not own personal planning,
weekly prioritization, calendars, or the full roadmaps of other projects.

## Current Status

- Lifecycle: `active`
- Category: `active_project`
- Local path: `/mnt/storage/Cole/Projects/project-forge-registry`
- Canonical Obsidian mirror: `/home/cole/main_vault/10 Projects/Project Forge`
- Docs sync lane: controlled, markdown-only, dry-run-first
- Governance state: narrowed mission approved 2026-07-23

## Authority Boundaries

| System | Authority |
|---|---|
| Project Forge | Technical project, repository, mirror, deployment-node, and fleet condition |
| Individual repositories and verified runtime state | Technical roadmap and implementation truth |
| Todoist | Immediate actionable commitments |
| Google Calendar | Fixed time commitments |
| Sunday Outlook / C2 Review | Cross-system prioritization and reconciliation |
| Obsidian | Durable context, decisions, learning, and doctrine |

## Superseded Mission

The former concept of Project Forge as a universal planner, master personal
command system, or single source of truth for every project is retired.

The name **command center** may remain for technical dashboards, launchers,
workspaces, and operator surfaces. It does not grant Project Forge authority over
Todoist, Calendar, C2 planning, or another project's roadmap.

## What This Project Does

- Scans project roots and inventories candidate projects.
- Classifies projects into operational categories.
- Protects special cases such as Cerberus from normal automation.
- Reports repository, mirror, launcher, workspace, and readiness state.
- Generates VS Code workspaces and launchers for approved entries.
- Generates project passport proposals.
- Generates controlled Obsidian technical mirror files.
- Provides guarded, dry-run-first technical review and resume workflows.

## Why It Matters

Project Forge creates order before automation. It produces inspectable evidence,
clear guardrails, and reversible technical steps without pretending to own the
operator's entire life or every project's strategic roadmap.

## Current Risks / Watch Items

- Misclassification risk for unfamiliar folders still requires manual review.
- Cerberus paths must remain in protected handling modes.
- Obsidian sync must remain markdown-only and no-clobber.
- Scope expansion must follow the charter's explicit decision rule.
- Local Legion checkout and real Obsidian hub still need to pull and reflect the
  2026-07-23 governance update.

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

- Read `PROJECT_CHARTER.md` before changing scope.
- Dry-run first.
- Review artifacts before apply.
- Keep docs-only lanes separate from code and operations lanes.
- Avoid touching external project folders during registry workflows.
- Preserve historical phase records while keeping current-facing doctrine accurate.

## Links and Commands

- Local path: `/mnt/storage/Cole/Projects/project-forge-registry`
- Workspace path: `/home/cole/.config/Code/User/workspaces/project_forge_registry.code-workspace`
- Launcher command: `code-project_forge_registry`
- Sync policy: `docs_only / export_only`

```bash
code "/home/cole/.config/Code/User/workspaces/project_forge_registry.code-workspace"
code-project_forge_registry
```
