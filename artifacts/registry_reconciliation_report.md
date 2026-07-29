# Project Forge Registry Reconciliation Report

**Date:** 2026-07-29
**Mode:** report-first reconciliation; no scanned project directory was modified

## Current Inventory

- Top-level project folders scanned: `78`
- Owned repository roots discovered: `82`
- Repository categories: `68 clean_candidate`, `6 dirty_candidate_review_first`,
  `4 known_embedded`, `1 control_repo`, `3 unknown_structure`
- Cerberus-branded repository roots visible: `12`
- Name-derived protected rows: `0`
- Current customized passports: `7`

Android `.repo` checkout farms and repositories nested beneath an already-owned
Git repository are excluded from independent project ownership. This reduced the
unbounded baseline discovery result from `1269` to `82` repository roots.

## Passport Decisions

### Added

- `pixel_dual_esim_diagnostics`: active private project; current GitHub origin
  recorded; raw device evidence remains outside Git.
- `proton_pass_vault_janitor`: active local project; no remote is configured;
  raw vault material remains outside Git.
- `agent_zero`: replaces the stale `agentzero` identity and is classified as a
  `vendor_clone` with lifecycle `reference`, not as an active personal project.

### Reconciled

- `media_dedupe`
- `project_forge_registry`
- `spiderfoot_peoplesearch`
- `steelseries_rgb`

Their canonical local paths now use the live Legion mount. Verified GitHub and
Codeberg URLs were recorded where configured, and review-only lifecycle values
were replaced with evidence-backed active status.

### Retired From Current Derived State

- `extension_blip`: no matching current local folder or GitHub owner repository.
- `recon_housekeeping`: no matching current local folder or GitHub owner
  repository.
- `agentzero`: superseded by the current `agent_zero` identity.

The retired files remain recoverable from Git history,
`/tmp/project-forge-artifacts-precloseout`, and `stash@{0}`.

## Candidate Evidence Reconciliation

- The preserved Proton Pass passport was accepted as legitimate project evidence
  but updated to current lifecycle, mount, remote, and restricted-data facts.
- Project Forge PR #2's Pixel passport remains legitimate. Current closeout
  output preserves its focused intent while recording that the scanner first
  classified it as a candidate and the operator evidence promoted it to active.
- The old stash's name-derived Cerberus protection rows were rejected.
- The old stash was not applied.

## External Estate Signals

GitHub/local presence gaps, stale branches, missing remotes, Codeberg divergence,
the unavailable canonical Obsidian root, and the separate homelab fleet-panel
worktree are recorded in `artifacts/technical_followup_signals.json`. Project
Forge reports those technical conditions; it does not convert them into tasks.

## Safety

- Protected paths `/home/cole/cerberus` and `/mnt/storage/Cole/cerberus` were
  excluded lexically before discovery or downstream processing.
- No protected-path contents were inspected.
- No scanned project folder was modified.
- No external marker apply was performed.
- No external remote was created, changed, or pushed during reconciliation.
