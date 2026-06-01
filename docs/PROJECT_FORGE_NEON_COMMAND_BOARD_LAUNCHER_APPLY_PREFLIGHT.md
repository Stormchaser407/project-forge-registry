# Project Forge Neon Command Board Launcher Apply Preflight

## Purpose

Phase 11H.4 adds guarded launcher replacement apply dry-run/preflight only.
It reads the prior launcher discovery, replacement review plan, and guarded
apply design artifacts, then writes a repo-local preflight package.

This phase has no real apply, no replacement, no mutation, no backups created,
no autostart changes, no systemd changes, no desktop entry changes, no
--open, no launch behavior, and no vault writes.

## Command

```bash
PYTHONPATH=src python3 -m project_forge_registry.neon_command_board_launcher_apply_preflight
```

Console-script form:

```bash
project-forge-neon-command-board-launcher-apply-preflight
```

Wrapper form:

```bash
./scripts/project-forge-neon-command-board-launcher-apply-preflight
```

## Outputs

- `artifacts/neon_command_board_launcher_apply_preflight.md`
- `artifacts/neon_command_board_launcher_apply_preflight.json`

## Inputs

- `artifacts/neon_command_board_launcher_discovery.json`
- `artifacts/neon_command_board_replacement_review_plan.json`
- `artifacts/neon_command_board_guarded_launcher_apply_design.json`

Missing prior artifacts are recorded as refusal/skipped preflight conditions.
They do not trigger destructive behavior.

## Safety Model

Phase 11H.4 is dry-run/preflight only. There is no real apply mode.

The command rejects accidental `--apply` usage because no apply flag exists. The
approval phrase is recorded only as approval phrase inert in 11H.4:

```text
APPROVE 11H.4 GUARDED LAUNCHER REPLACEMENT APPLY
```

The phrase is not accepted as authorization. Real apply remains future phase
only.

## Report Contents

- Purpose
- Mode / Safety
- Current baseline
- Prior artifacts checked
- Approved target classes
- Candidate targets from discovery
- Proposed target review
- Simulated backup manifest
- Simulated diff/review summary
- Simulated rollback plan
- Refusal conditions
- All-or-nothing preflight result
- Operator approval phrase status
- Non-goals
- Recommended next phase

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

Phase 11H.5 - guarded launcher replacement apply, only after explicit operator
approval.
