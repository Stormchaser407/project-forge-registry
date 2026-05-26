# Neon Command Board Launcher Discovery Report

## Purpose

Phase 11H.1 adds dry-run discovery for launcher/autostart references related to
the old Recon Command Board and the new Neon command board.

## Scope

Mode: dry-run discovery. This report is read-only, performs no mutation, does
not execute discovered commands, and requires operator approval before
replacement.

## Discovery Targets Inspected

- `scripts` - present; files read: `11`; scope: repo-local launcher candidates
- `pyproject.toml` - present; files read: `1`; scope: repo-local entrypoints
- `docs` - present; files read: `36`; scope: docs inside this repo
- `artifacts` - present; files read: `111`; scope: artifacts inside this repo
- `~/.config/autostart` - present; files read: `2`; scope: approved user-local autostart path
- `~/.config/systemd/user` - present; files read: `9`; scope: approved user-local systemd path
- `~/.local/share/applications` - present; files read: `82`; scope: approved user-local desktop application path

## Repo-Local Launcher Candidates

- `scripts/project-forge-checkpoint` - `review_only` - matched terms: Project Forge, project-forge
- `scripts/project-forge-codex-profile-bootstrap` - `review_only` - matched terms: Project Forge, project-forge
- `scripts/project-forge-codex-profile-probe` - `review_only` - matched terms: Project Forge, project-forge
- `scripts/project-forge-cold-start` - `review_only` - matched terms: Project Forge, project-forge, project-forge-dashboard
- `scripts/project-forge-dashboard` - `review_only` - matched terms: Project Forge, project-forge, project-forge-dashboard
- `scripts/project-forge-install-cold-start-desktop` - `review_only` - matched terms: Project Forge, project-forge
- `scripts/project-forge-open-project` - `review_only` - matched terms: Project Forge, project-forge
- `scripts/project-sync-safe` - `review_only` - matched terms: Project Forge
- `pyproject.toml` - `review_neon_candidate` - matched terms: project-forge, project-forge-dashboard, project-forge-neon-command-board

## User-Local Autostart Candidates

- none found

## User-Local Systemd User Service Candidates

- none found

## User-Local Desktop Entry Candidates

- `~/.local/share/applications/project-forge-cold-start.desktop` - `review_only` - matched terms: Project Forge, project-forge
- `~/.local/share/applications/project-forge-command-board.desktop` - `review_only` - matched terms: Project Forge, project-forge
- `~/.local/share/applications/project-forge-operator-runbook.desktop` - `review_only` - matched terms: Project Forge, project-forge
- `~/.local/share/applications/project-forge-safe-sync.desktop` - `review_only` - matched terms: Project Forge, project-forge
- `~/.local/share/applications/recon-container-restart.desktop` - `review_only` - matched terms: Recon
- `~/.local/share/applications/recon-container-status.desktop` - `review_only` - matched terms: Recon
- `~/.local/share/applications/recon-flake-build.desktop` - `review_only` - matched terms: Recon
- `~/.local/share/applications/recon-flake-switch.desktop` - `review_only` - matched terms: Recon
- `~/.local/share/applications/recon-flake-test.desktop` - `review_only` - matched terms: Recon
- `~/.local/share/applications/recon-ops-dashboard.desktop` - `review_only` - matched terms: Recon
- `~/.local/share/applications/recon-span-screensaver.desktop` - `review_only` - matched terms: Recon
- `~/.local/share/applications/recon-update-all.desktop` - `review_only` - matched terms: Recon

## References Found

- `scripts/project-forge-checkpoint` line 14: `Project Forge`
- `scripts/project-forge-checkpoint` line 49: `project-forge`
- `scripts/project-forge-checkpoint` line 60: `Project Forge`
- `scripts/project-forge-codex-profile-bootstrap` line 13: `project-forge`
- `scripts/project-forge-codex-profile-bootstrap` line 14: `project-forge`
- `scripts/project-forge-codex-profile-bootstrap` line 52: `Project Forge`
- `scripts/project-forge-codex-profile-bootstrap` line 89: `Project Forge`
- `scripts/project-forge-codex-profile-probe` line 7: `project-forge`
- `scripts/project-forge-codex-profile-probe` line 8: `project-forge`
- `scripts/project-forge-codex-profile-probe` line 9: `project-forge`
- `scripts/project-forge-codex-profile-probe` line 10: `project-forge`
- `scripts/project-forge-codex-profile-probe` line 71: `project-forge`
- `scripts/project-forge-codex-profile-probe` line 106: `Project Forge`
- `scripts/project-forge-cold-start` line 7: `project-forge`
- `scripts/project-forge-cold-start` line 10: `Project Forge`
- `scripts/project-forge-cold-start` line 46: `project-forge`
- `scripts/project-forge-cold-start` line 59: `Project Forge`
- `scripts/project-forge-cold-start` line 92: `project-forge`
- `scripts/project-forge-cold-start` line 92: `project-forge-dashboard`
- `scripts/project-forge-cold-start` line 94: `project-forge`
- `scripts/project-forge-cold-start` line 94: `project-forge-dashboard`
- `scripts/project-forge-dashboard` line 7: `project-forge`
- `scripts/project-forge-dashboard` line 7: `project-forge-dashboard`
- `scripts/project-forge-dashboard` line 10: `Project Forge`
- `scripts/project-forge-dashboard` line 21: `Project Forge`
- `scripts/project-forge-dashboard` line 50: `project-forge`
- `scripts/project-forge-dashboard` line 50: `project-forge-dashboard`
- `scripts/project-forge-dashboard` line 63: `Project Forge`
- `scripts/project-forge-install-cold-start-desktop` line 7: `project-forge`
- `scripts/project-forge-install-cold-start-desktop` line 10: `Project Forge`
- `scripts/project-forge-install-cold-start-desktop` line 45: `project-forge`
- `scripts/project-forge-install-cold-start-desktop` line 55: `project-forge`
- `scripts/project-forge-install-cold-start-desktop` line 58: `project-forge`
- `scripts/project-forge-install-cold-start-desktop` line 59: `project-forge`
- `scripts/project-forge-install-cold-start-desktop` line 60: `project-forge`
- `scripts/project-forge-install-cold-start-desktop` line 62: `project-forge`
- `scripts/project-forge-install-cold-start-desktop` line 67: `Project Forge`
- `scripts/project-forge-install-cold-start-desktop` line 105: `Project Forge`
- `scripts/project-forge-install-cold-start-desktop` line 106: `Project Forge`
- `scripts/project-forge-install-cold-start-desktop` line 116: `Project Forge`
- `scripts/project-forge-open-project` line 16: `project-forge`
- `scripts/project-forge-open-project` line 17: `project-forge`
- `scripts/project-forge-open-project` line 18: `project-forge`
- `scripts/project-forge-open-project` line 19: `project-forge`
- `scripts/project-forge-open-project` line 230: `Project Forge`
- `scripts/project-sync-safe` line 13: `Project Forge`
- `pyproject.toml` line 6: `project-forge`
- `pyproject.toml` line 14: `project-forge`
- `pyproject.toml` line 15: `project-forge`
- `pyproject.toml` line 16: `project-forge`
- `pyproject.toml` line 17: `project-forge`
- `pyproject.toml` line 18: `project-forge`
- `pyproject.toml` line 19: `project-forge`
- `pyproject.toml` line 20: `project-forge`
- `pyproject.toml` line 21: `project-forge`
- `pyproject.toml` line 22: `project-forge`
- `pyproject.toml` line 24: `project-forge`
- `pyproject.toml` line 24: `project-forge-dashboard`
- `pyproject.toml` line 25: `project-forge`
- `pyproject.toml` line 25: `project-forge-dashboard`
- `pyproject.toml` line 26: `project-forge`
- `pyproject.toml` line 27: `project-forge`
- `pyproject.toml` line 28: `project-forge`
- `pyproject.toml` line 29: `project-forge`
- `pyproject.toml` line 29: `project-forge-neon-command-board`
- `pyproject.toml` line 30: `project-forge`
- `pyproject.toml` line 30: `project-forge-neon-command-board`
- `docs/PROJECT_FORGE_CHECKPOINTS.md` line 1: `Project Forge`
- `docs/PROJECT_FORGE_CHECKPOINTS.md` line 19: `project-forge`
- `docs/PROJECT_FORGE_CHECKPOINTS.md` line 23: `project-forge`
- `docs/PROJECT_FORGE_CHECKPOINTS.md` line 65: `project-forge`
- `docs/PROJECT_FORGE_CODEX_PROFILES.md` line 1: `Project Forge`
- `docs/PROJECT_FORGE_CODEX_PROFILES.md` line 5: `Project Forge`
- `docs/PROJECT_FORGE_CODEX_PROFILES.md` line 16: `project-forge`
- `docs/PROJECT_FORGE_CODEX_PROFILES.md` line 20: `project-forge`
- `docs/PROJECT_FORGE_CODEX_PROFILES.md` line 24: `project-forge`
- `docs/PROJECT_FORGE_CODEX_PROFILES.md` line 28: `project-forge`
- `docs/PROJECT_FORGE_CODEX_PROFILES.md` line 32: `project-forge`
- `docs/PROJECT_FORGE_CODEX_PROFILE_BOOTSTRAP.md` line 1: `Project Forge`
- `docs/PROJECT_FORGE_CODEX_PROFILE_BOOTSTRAP.md` line 15: `project-forge`
- 1247 additional references omitted from markdown; see JSON artifact

## Skipped / Missing

- none

## Risks / Warnings

- dry-run discovery only; operator approval required before replacement
- no mutation, no autostart replacement, no systemd changes, no desktop entry changes
- no vault writes, no --open, no command execution

## Non-Goals

- no autostart replacement
- no systemd changes
- no desktop entry changes
- no vault writes
- no --open
- no command execution
- no browser, file handler, or VS Code launch
- no push, fetch, or remote contact
- no tag deletion or movement

## Safety Confirmation

This is dry-run discovery only. It is read-only, has no mutation path, performs
no autostart replacement, makes no systemd changes, makes no desktop entry
changes, performs no vault writes, runs no --open behavior, performs no command
execution, and requires operator approval before replacement.

## Recommended Next Phase

Phase 11H.2: operator-reviewed replacement plan after the exact old target and
exact Neon command board target are confirmed.
