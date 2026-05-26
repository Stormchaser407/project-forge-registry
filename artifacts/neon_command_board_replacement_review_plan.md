# Neon Command Board Replacement Review Plan

## Phase

Phase 11H.2 - operator-reviewed launcher replacement plan only.

## Purpose

Prepare a reviewed plan for a later, separately approved replacement of the old
Project Forge / Recon command board launcher with Neon command board behavior.

This artifact is not an apply artifact. It performs no mutation and approves no
replacement.

## Baseline Checked

- HEAD: `969fec4 Add Phase 11H.1 Neon launcher discovery dry-run`
- Tags at HEAD:
  - `v0.11.0h1-neon-launcher-discovery`
  - `checkpoint-20260526-170204-phase-11h1-neon-launcher-discovery`
- Command board checked from repo artifacts:
  - `artifacts/neon_command_board.html`
  - `artifacts/neon_command_board_report.md`
  - `artifacts/neon_command_board_manifest.json`
- Command board safety: static HTML/CSS, no JavaScript, no command execution,
  no launch controls, no mutation, no vault writes, no remotes, no network.
- Discovery source:
  - `artifacts/neon_command_board_launcher_discovery.md`
  - `artifacts/neon_command_board_launcher_discovery.json`

## Reviewed Discovery Summary

- Targets inspected by Phase 11H.1: `7`
- Candidates found: `21`
- Skipped targets: `0`
- Skipped files: `0`
- Safety result: dry-run/read-only; no mutation; no command execution; no
  autostart replacement; no systemd changes; no desktop entry changes; no vault
  writes; no open/launch behavior; no network/remotes; no tag changes.

## Operator-Review Targets

Primary old launcher candidate:

- `~/.local/share/applications/project-forge-command-board.desktop`
- source status: `review_only`
- required review: confirm this is the old command board launcher before any
  future replacement.

Primary Neon target candidate:

- `./scripts/project-forge-neon-command-board`
- `PYTHONPATH=src python3 -m project_forge_registry.neon_command_board`
- output: `artifacts/neon_command_board.html`
- required review: confirm future behavior before any launcher/autostart write.

Related candidates remain untouched in this phase:

- `~/.local/share/applications/project-forge-cold-start.desktop`
- `~/.local/share/applications/project-forge-operator-runbook.desktop`
- `~/.local/share/applications/project-forge-safe-sync.desktop`
- Recon desktop entries under `~/.local/share/applications`

No autostart or systemd user-service replacement target is selected.

## Future Apply Criteria

- exact old target confirmed
- exact Neon target behavior confirmed
- backup path defined
- rollback path defined
- diff/review report generated
- repository status reviewed
- all-or-nothing preflight passes
- existing different content blocks unless backup and exact approval are present
- no delete behavior
- no service enable/disable/start/stop/reload behavior
- no `--open` by default

## Future Backup Shape

Example only:

```text
~/.local/share/applications/project-forge-command-board.desktop.bak.<timestamp>
```

## Future Approval Phrase

Example only:

```text
APPROVE PHASE 11H.3 NEON LAUNCHER REPLACEMENT
```

## Explicit Non-Goals

- no apply
- no replacement
- no launch
- no enable or disable
- no autostart mutation
- no systemd mutation
- no desktop entry mutation
- no vault writes
- no remotes
- no tag movement

## Recommended Next Phase

Phase 11H.3: separately approved guarded apply design or implementation with
preflight, diff report, backup path, rollback path, and exact approval phrase.
