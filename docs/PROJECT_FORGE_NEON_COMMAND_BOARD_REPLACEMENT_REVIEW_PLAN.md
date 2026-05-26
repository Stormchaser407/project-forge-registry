# Project Forge Neon Command Board Replacement Review Plan

## Purpose

Phase 11H.2 turns the reviewed Phase 11H.1 dry-run discovery output into an
operator-reviewed replacement plan for moving the old Project Forge / Recon
command board launcher toward the Neon command board.

This phase is planning only. It does not apply, replace, launch, enable,
disable, reload, or mutate autostart entries, systemd user services, desktop
entries, remotes, tags, vault files, or project folders.

## Baseline Checked

- Current checkpoint: `969fec4 Add Phase 11H.1 Neon launcher discovery dry-run`
- Current tags at `HEAD`:
  - `v0.11.0h1-neon-launcher-discovery`
  - `checkpoint-20260526-170204-phase-11h1-neon-launcher-discovery`
- Command board artifact checked:
  - `artifacts/neon_command_board.html`
  - `artifacts/neon_command_board_report.md`
  - `artifacts/neon_command_board_manifest.json`
- Command board safety model: static HTML/CSS, no JavaScript, no command
  execution, no executable buttons, no URL launch controls, no state mutation,
  no real vault writes, no remotes, and no network calls.
- Phase 11H.1 discovery artifact checked:
  - `artifacts/neon_command_board_launcher_discovery.md`
  - `artifacts/neon_command_board_launcher_discovery.json`

## Reviewed Discovery Summary

Phase 11H.1 inspected approved text surfaces in dry-run/read-only mode:

- `scripts/`
- `pyproject.toml`
- `docs/`
- `artifacts/`
- `~/.config/autostart`
- `~/.config/systemd/user`
- `~/.local/share/applications`

Discovery found `21` candidates, `0` skipped targets, and `0` skipped files.
The discovery safety payload confirms no mutation, no command execution, no
autostart replacement, no systemd changes, no desktop entry changes, no vault
writes, no open/launch behavior, no network/remotes, and no tag changes.

## Operator-Review Targets

Primary old launcher candidate:

- Path: `~/.local/share/applications/project-forge-command-board.desktop`
- Source: Phase 11H.1 discovery JSON
- Current status: `review_only`
- Review decision required: confirm whether this is the old command board
  launcher that should eventually be replaced or whether it should remain.

Primary Neon target candidate:

- Wrapper command: `./scripts/project-forge-neon-command-board`
- Module command: `PYTHONPATH=src python3 -m project_forge_registry.neon_command_board`
- Output artifact: `artifacts/neon_command_board.html`
- Current status: planning target only
- Review decision required: confirm whether future desktop/autostart behavior
  should generate the Neon board, open the generated HTML, or both. Opening is
  not approved in Phase 11H.2.

Related candidates to leave untouched in this phase:

- `~/.local/share/applications/project-forge-cold-start.desktop`
- `~/.local/share/applications/project-forge-operator-runbook.desktop`
- `~/.local/share/applications/project-forge-safe-sync.desktop`
- Recon desktop entries discovered under `~/.local/share/applications`

No autostart or systemd user-service replacement target is selected in this
phase.

## Replacement Criteria

A later apply phase must not proceed unless all of these are true:

- operator confirms the exact old target path
- operator confirms the exact Neon target behavior
- backup path is defined before any write
- rollback path is defined before any write
- generated diff/review report exists
- repository status is reviewed
- all writes are all-or-nothing
- existing different file content blocks unless a backup and explicit approval
  phrase are both present
- no delete behavior is included
- no service enable, disable, start, stop, or reload behavior is included
- no `--open` or browser/file-handler launch is included by default

## Proposed Future Backup And Rollback Shape

If a later phase is approved, the backup should be adjacent to the old target
and timestamped. Example shape only:

```text
~/.local/share/applications/project-forge-command-board.desktop.bak.<timestamp>
```

Rollback must be stated before any write. Example shape only:

```text
restore backup over target after exact operator confirmation
```

These are review shapes, not Phase 11H.2 actions.

## Required Approval Phrase For Future Apply

A later apply phase should require an exact phrase similar to:

```text
APPROVE PHASE 11H.3 NEON LAUNCHER REPLACEMENT
```

Phase 11H.2 does not accept that phrase and does not perform replacement.

## Explicit Non-Goals

- no apply
- no replacement
- no launcher execution
- no browser, file-handler, or VS Code launch
- no autostart entry creation, edit, removal, enable, or disable
- no systemd user service creation, edit, removal, enable, disable, start,
  stop, or reload
- no desktop entry creation, edit, removal, or installation
- no writes outside this repository
- no real Obsidian vault writes
- no remote contact
- no tag movement or deletion

## Recommended Next Phase

Phase 11H.3 should be a separately approved guarded apply design or guarded
apply implementation. It should start from this reviewed plan, re-check the
working tree, re-check the exact target paths, write a preflight/diff report,
and stop before mutation unless Cash gives the explicit approval phrase for
that future phase.
