---
title: "Project Forge - Command Center"
project: "Project Forge"
status: "historical dry-run artifact"
tags:
  - project-forge
  - phase-11
  - command-center
  - dry-run
  - superseded-scope-qualified
---

# Project Forge - Command Center

> **Governance note:** This is a preserved Phase 11A dry-run artifact. The
> canonical current mission and authority boundary are defined by repository
> `PROJECT_CHARTER.md` and `PROJECT_STATUS.md`.

Project Forge is a dry-run-first local **technical** command center. It inventories
and reports technical project, repository, mirror, launcher, workspace, and
readiness state. It does not own personal planning, weekly prioritization,
calendars, or the complete roadmaps of other projects.

The older universal-planner interpretation of “command center” is superseded.
The term here refers only to a technical operator surface.

## Navigation

- [[Project Forge - Dashboard Summary]]
- [[Project Forge - Known Embedded Repos]]
- [[Project Forge - Deferred Items]]
- [[Project Forge - Phase 11 Planning]]

## Operator Quick Start

```bash
./scripts/project-forge-cold-start
./scripts/project-forge-dashboard --no-open
./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --dry-run
```

## Dashboard

- artifact: `artifacts/dashboard.html`
- total projects: `74`
- known embedded repos: `4`

## Safety

- no real Obsidian vault writes
- no external repo writes
- no apply
- no remotes
- no push/fetch
- no package installs
- no network calls
- no VS Code launch
- no Codex login/auth handling
