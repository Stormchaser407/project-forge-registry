---
title: "Project Forge - Command Center"
project: "Project Forge"
status: "dry-run artifact"
tags:
  - project-forge
  - phase-11
  - command-center
  - dry-run
---

# Project Forge - Command Center

Project Forge is a dry-run-first local command center. This Phase 11A mirror is generated under repository artifacts only.

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
