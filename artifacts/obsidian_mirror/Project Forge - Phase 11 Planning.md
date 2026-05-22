---
title: "Project Forge - Phase 11 Planning"
project: "Project Forge"
status: "dry-run artifact"
tags:
  - project-forge
  - phase-11
  - command-center
  - dry-run
---

# Project Forge - Phase 11 Planning

Back to [[Project Forge - Command Center]]. Review [[Project Forge - Deferred Items]] before expanding scope.

## Candidate Lanes

- Obsidian integration: keep artifact mirror deterministic before real vault sync.
- Repo action policies: define allowed, blocked, and review-only actions per category.
- Remote strategy: map local, GitHub, Codeberg, and mirror policy without contacting remotes by default.
- Codex/VS Code isolation research: test user-data, extension-dir, profile, and environment boundaries.

## Phase 11A Boundary

- Generate Markdown notes under `artifacts/obsidian_mirror/` only.
- Generate `artifacts/obsidian_mirror_report.md`.
- Generate `artifacts/obsidian_mirror_manifest.json`.
- Do not write to any real Obsidian vault.
