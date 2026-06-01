# Neon Command Board Launcher Apply Preflight

## Purpose

Phase 11H.4 adds guarded launcher replacement apply dry-run/preflight only.
It reports what a future guarded launcher replacement would require.

## Mode / Safety

Mode: dry-run/preflight only.

This phase has no real apply, no replacement, no mutation, no backups created,
no autostart changes, no systemd changes, no desktop entry changes, no
--open, no launch behavior, and no vault writes.

The simulated backup manifest and simulated rollback plan are report-only.
The approval phrase inert in 11H.4 status means `APPROVE 11H.4 GUARDED LAUNCHER REPLACEMENT APPLY`
is recorded but not accepted as authorization. A real apply remains future phase only.

## Current Baseline

- Phase: Phase 11H.4
- Previous stable phase: Phase 11H.3 guarded launcher apply design
- Previous stable HEAD: `84eafe9 Add Phase 11H.3 guarded launcher apply design`
- Previous stable version tag: `v0.11.0h3-guarded-launcher-apply-design`
- Previous stable checkpoint: `checkpoint-20260601-162837-phase-11h3-guarded-launcher-apply-design`
- Obsidian no-clobber conflict remains recorded and unresolved.

## Prior Artifacts Checked

- `artifacts/neon_command_board_launcher_discovery.json` - present; phase: `Phase 11H.1`
- `artifacts/neon_command_board_replacement_review_plan.json` - present; phase: `Phase 11H.2`
- `artifacts/neon_command_board_guarded_launcher_apply_design.json` - present; phase: `Phase 11H.3`

## Approved Target Classes

- approved user-local desktop entries - `~/.local/share/applications` (`user_desktop_entry`)
- approved user-local autostart entries - `~/.config/autostart` (`user_autostart`)
- approved user-local systemd user units - `~/.config/systemd/user` (`user_systemd`)

## Candidate Targets From Discovery

- `scripts/project-forge-checkpoint` - `repo_launcher`; not an apply target class; repo-local command candidate; not a file target for apply
- `scripts/project-forge-codex-profile-bootstrap` - `repo_launcher`; not an apply target class; repo-local command candidate; not a file target for apply
- `scripts/project-forge-codex-profile-probe` - `repo_launcher`; not an apply target class; repo-local command candidate; not a file target for apply
- `scripts/project-forge-cold-start` - `repo_launcher`; not an apply target class; repo-local command candidate; not a file target for apply
- `scripts/project-forge-dashboard` - `repo_launcher`; not an apply target class; repo-local command candidate; not a file target for apply
- `scripts/project-forge-install-cold-start-desktop` - `repo_launcher`; not an apply target class; repo-local command candidate; not a file target for apply
- `scripts/project-forge-open-project` - `repo_launcher`; not an apply target class; repo-local command candidate; not a file target for apply
- `scripts/project-sync-safe` - `repo_launcher`; not an apply target class; repo-local command candidate; not a file target for apply
- `pyproject.toml` - `repo_launcher`; not an apply target class; repo-local command candidate; not a file target for apply
- `~/.local/share/applications/project-forge-cold-start.desktop` - `user_desktop_entry`; approved class; related desktop entry candidate; review only
- `~/.local/share/applications/project-forge-command-board.desktop` - `user_desktop_entry`; approved class; primary operator-reviewed old launcher candidate
- `~/.local/share/applications/project-forge-operator-runbook.desktop` - `user_desktop_entry`; approved class; related desktop entry candidate; review only
- `~/.local/share/applications/project-forge-safe-sync.desktop` - `user_desktop_entry`; approved class; related desktop entry candidate; review only
- `~/.local/share/applications/recon-container-restart.desktop` - `user_desktop_entry`; approved class; related desktop entry candidate; review only
- `~/.local/share/applications/recon-container-status.desktop` - `user_desktop_entry`; approved class; related desktop entry candidate; review only
- `~/.local/share/applications/recon-flake-build.desktop` - `user_desktop_entry`; approved class; related desktop entry candidate; review only
- `~/.local/share/applications/recon-flake-switch.desktop` - `user_desktop_entry`; approved class; related desktop entry candidate; review only
- `~/.local/share/applications/recon-flake-test.desktop` - `user_desktop_entry`; approved class; related desktop entry candidate; review only
- `~/.local/share/applications/recon-ops-dashboard.desktop` - `user_desktop_entry`; approved class; related desktop entry candidate; review only
- `~/.local/share/applications/recon-span-screensaver.desktop` - `user_desktop_entry`; approved class; related desktop entry candidate; review only
- `~/.local/share/applications/recon-update-all.desktop` - `user_desktop_entry`; approved class; related desktop entry candidate; review only

## Proposed Target Review

- `~/.local/share/applications/project-forge-command-board.desktop` - future guarded replacement candidate only; status: `review_required_no_apply`

## Simulated Backup Manifest

- `~/.local/share/applications/project-forge-command-board.desktop` -> `~/.local/share/applications/project-forge-command-board.desktop.bak.<timestamp>`; backup created: no; simulated only; no backups created

No backups created. This is a simulated backup manifest only.

## Simulated Diff/Review Summary

- Diff generated: `no`
- Status: simulated review only; no replacement content generated
- Changed files list: `~/.local/share/applications/project-forge-command-board.desktop`
- Old content summary: existing launcher content would be summarized in a future real apply phase
- New content summary: future Neon launcher behavior must be operator-reviewed before real apply

## Simulated Rollback Plan

- `~/.local/share/applications/project-forge-command-board.desktop` restore source `~/.local/share/applications/project-forge-command-board.desktop.bak.<timestamp>`; executed: no; simulated rollback plan only

This is a simulated rollback plan only; no rollback commands executed.

## Refusal Conditions

- dirty repo: triggered `no`
- missing prior artifact: triggered `no`
- missing approved target: triggered `no`
- target path outside approved user-local directories: triggered `no`
- symlink ambiguity: triggered `no`
- unreadable target: triggered `no`
- missing backup path: triggered `no`
- missing rollback plan: triggered `no`
- missing exact approval phrase: triggered `yes`
- generated plan older than latest discovery: triggered `no`
- Obsidian conflict confused with launcher work: triggered `no`
- request to run --open or launch UI as part of apply: triggered `no`
- exact target path not confirmed for real apply: triggered `yes`

## All-Or-Nothing Preflight Result

- Result: `blocked_for_real_apply_review_ready_for_dry_run`
- Passes for real apply: `no`
- Passes for dry-run report: `yes`
- Triggered refusal count: `2`
- Summary: all-or-nothing preflight report generated; no real apply is available in Phase 11H.4

## Operator Approval Phrase Status

- Approval phrase: `APPROVE 11H.4 GUARDED LAUNCHER REPLACEMENT APPLY`
- Approval phrase status: approval phrase inert in 11H.4
- The phrase is not accepted as authorization in this phase.

## Non-Goals

- no real apply
- no replacement
- no mutation
- no backups created
- no autostart changes
- no systemd changes
- no desktop entry changes
- no --open
- no launch behavior
- no vault writes
- no remotes
- no Obsidian conflict resolution

## Recommended Next Phase

Phase 11H.5 - guarded launcher replacement apply, only after explicit operator approval.
