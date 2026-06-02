# Neon Command Board Launcher Apply Dry Run

## Purpose

Phase 11H.5 implements guarded launcher replacement apply command capability.
The command defaults to dry-run and writes repo-local reports.

## Mode / Safety

Mode: default dry-run.

This is a guarded launcher replacement apply command with default dry-run,
no real apply unless all guards pass, no mutation during dry-run, no launch
behavior, no --open, no systemd changes, no desktop entry changes unless
explicitly approved, no autostart changes unless explicitly approved, backup
before overwrite, rollback required, no delete, no vault writes, exact approval
phrase required, exact target path confirmation required, and clean git tree
required.

## Current Baseline

- Current phase: Phase 11H.5
- Previous stable phase: Phase 11H.4 launcher apply preflight dry-run
- Previous stable HEAD: `d35b601 Add Phase 11H.4 launcher apply preflight dry-run`
- Previous stable version tag: `v0.11.0h4-launcher-apply-preflight-dry-run`
- Previous stable checkpoint: `checkpoint-20260601-175501-phase-11h4-launcher-apply-preflight-dry-run`
- Obsidian no-clobber conflict remains recorded and unresolved.

## Prior Artifacts Checked

- `artifacts/neon_command_board_launcher_apply_preflight.json` - present; phase: `Phase 11H.4`

## Target Path Under Review

- Target path: `~/.local/share/applications/project-forge-command-board.desktop`
- Confirm target path: ``
- Exact target path confirmation required: `no`

## Guard Requirements

- --apply
- --yes-replace-launcher
- --approval-phrase "APPROVE 11H.5 GUARDED LAUNCHER REPLACEMENT APPLY"
- --target-path ~/.local/share/applications/project-forge-command-board.desktop
- --confirm-target-path exactly matching --target-path
- --clean-git-tree-confirmed after operator verifies clean git working tree
- --expected-head or --expected-tag
- Phase 11H.4 preflight artifact present
- proposed target included in preflight artifact
- backup path defined
- rollback plan defined
- no ambiguous target class
- no request to launch, open, enable, disable, or reload anything

## Guard Status

- --apply: `no` - real apply flag
- --yes-replace-launcher: `no` - explicit replacement approval flag
- exact approval phrase required: `no` - approval phrase must match exactly
- target path is approved target: `no` - target path must match proposed approved target
- exact target path confirmation required: `no` - confirm-target-path must exactly match target-path
- clean git tree required: `no` - operator must verify clean git tree first
- expected HEAD or expected tag confirmation: `no` - operator must provide expected HEAD or tag guard
- prior 11H.4 preflight artifact present: `yes` - checked
- proposed target included in preflight artifact: `no` - target must be present in Phase 11H.4 proposed_targets
- backup path defined: `yes` - backup before overwrite
- rollback plan defined: `yes` - rollback required
- no ambiguous target class: `no` - only the approved desktop entry target is supported
- no launch/open/enable/disable/reload request: `yes` - no launch behavior, no --open, no systemd changes

## Proposed File Content Summary

- Name: Project Forge Neon Command Board
- Line count: `7`
- Exec summary: `Exec=sh -lc 'cd /mnt/storage/Cole/Projects/project-forge-registry && PYTHONPATH=src python3 -m project_forge_registry.neon_command_board'`
- Launches now: `no`
- Notes: Proposed desktop entry content only; no launch behavior is performed by this command.

## Backup Plan

- Target path: `~/.local/share/applications/project-forge-command-board.desktop`
- Backup path: `~/.local/share/applications/project-forge-command-board.desktop.bak.<timestamp>`
- Backup before overwrite: `yes`
- Backup created: `no`
- Status: planned in dry-run; required before real apply

## Rollback Plan

- Target path: `~/.local/share/applications/project-forge-command-board.desktop`
- Restore from: `~/.local/share/applications/project-forge-command-board.desktop.bak.<timestamp>`
- Rollback required: `yes`
- Rollback executed: `no`
- Status: planned in dry-run; operator must review before real apply

## Refusal Conditions

- --apply: triggered `yes`
- --yes-replace-launcher: triggered `yes`
- exact approval phrase required: triggered `yes`
- target path is approved target: triggered `yes`
- exact target path confirmation required: triggered `yes`
- clean git tree required: triggered `yes`
- expected HEAD or expected tag confirmation: triggered `yes`
- prior 11H.4 preflight artifact present: triggered `no`
- proposed target included in preflight artifact: triggered `yes`
- backup path defined: triggered `no`
- rollback plan defined: triggered `no`
- no ambiguous target class: triggered `yes`
- no launch/open/enable/disable/reload request: triggered `no`

## Apply Availability

- Apply requested: `no`
- Real apply available: `no`
- Mutates state: `no`
- Dry-run: `yes`

## Non-Goals

- no launch behavior
- no --open
- no systemd changes
- no desktop entry changes unless explicitly approved
- no autostart changes unless explicitly approved
- no delete
- no vault writes
- no remotes
- no Obsidian conflict resolution

## Recommended Operator Next Step

Review this dry-run report. Run real apply only in a later operator-controlled terminal with every guard satisfied; do not launch or open anything as part of apply.
