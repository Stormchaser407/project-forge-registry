# Project Forge Neon Command Board Launcher Plan

## Purpose

Phase 11H.0 defines the safe path from old Recon Command Board
launcher/autostart behavior toward the new Neon command board.

This phase is planning only. It does not inspect live launcher/autostart paths,
replace launchers, create services, create desktop entries, launch local file
handlers, or write outside this repository.

## Current Stable Baseline

- Phase: 11G.1 - Neon command board metadata hygiene
- Commit: `cf60a1f Add Phase 11G.1 Neon command board metadata hygiene`
- Version tag: `v0.11.0g1-neon-command-board-metadata-hygiene`
- Checkpoint: `checkpoint-20260524-234802-phase-11g1-neon-command-board-metadata-hygiene`
- Stale local checkpoint observation:
  `checkpoint-20260524-231148-phase-11g1-neon-command-board-metadata-hygiene`
  points at `4f1dc2f` and remains tag hygiene only.

The Neon command board is static display-only HTML/CSS. It has no JavaScript,
no command execution, and no vault writes. It displays copy-paste commands as
operator text only.

## Discovery Targets For Future Approval

Phase 11H.0 lists likely discovery targets only. It does not inspect these
external paths.

- `~/.config/autostart`
- `~/.config/systemd/user`
- `~/.local/share/applications`
- `scripts/`
- `pyproject.toml` project entrypoints
- Existing Project Forge dashboard scripts and docs inside this repository:
  - `scripts/project-forge-dashboard`
  - `scripts/project-forge-cold-start`
  - `scripts/project-forge-install-cold-start-desktop`
  - `scripts/project-forge-neon-command-board`
  - `docs/PROJECT_FORGE_DASHBOARD_LAUNCHER.md`
  - `docs/PROJECT_FORGE_COLD_START.md`
  - `docs/PROJECT_FORGE_COLD_START_DESKTOP.md`
  - `docs/PROJECT_FORGE_NEON_COMMAND_BOARD.md`

## Future Dry-Run Discovery Design

A future Phase 11H.1 dry-run discovery command may inspect approved local
launcher/autostart targets only after explicit operator approval.

The future command should:

- produce markdown and JSON artifacts under `artifacts/`
- record discovered files, candidate old Recon references, and candidate Neon
  replacement targets
- classify every candidate as `review_only`, `blocked`, or
  `ready_for_operator_review`
- avoid reading secrets, auth files, databases, caches, or unrelated personal
  data
- avoid mutating files
- avoid launching browsers, file handlers, VS Code, or other applications
- avoid enabling, disabling, starting, stopping, or reloading services
- avoid touching the real Obsidian vault

The future command should refuse to generate a replacement plan when the old
launcher target is ambiguous, the new Neon target is not exact, the working tree
is dirty, or rollback instructions cannot be stated clearly.

## Replacement Criteria

Any later replacement phase requires all of the following before implementation:

- exact old launcher/autostart target identified
- exact new Neon command board target identified
- backup path defined before any overwrite
- rollback path defined and reviewed
- operator approval phrase required
- all-or-nothing preflight
- no silent overwrite
- no delete behavior
- dirty repository review before proceeding
- protected or system-bound targets blocked for manual review

The expected new command target is one of:

```bash
./scripts/project-forge-neon-command-board
```

or:

```bash
PYTHONPATH=src python3 -m project_forge_registry.neon_command_board
```

## Proposed Future Operator Commands

These examples are copy-paste text only. They are not executable UI actions.

Generate the Neon command board:

```bash
./scripts/project-forge-neon-command-board
```

Module form:

```bash
PYTHONPATH=src python3 -m project_forge_registry.neon_command_board
```

Future dry-run discovery command, if approved and implemented:

```bash
./scripts/project-forge-neon-command-board-launcher-plan --dry-run
```

No real replacement command is listed as a normal action in Phase 11H.0.

## Explicit Non-Goals

- no autostart replacement in Phase 11H.0
- no service creation
- no desktop entry creation
- no system writes
- no vault writes
- no --open behavior
- no VS Code launch
- no tag deletion or movement
- no push, fetch, or remote contact
- no inspection of `~/.config/autostart` in this phase
- no inspection of `~/.config/systemd/user` in this phase
- no inspection of `~/.local/share/applications` in this phase

## Risk Register

| Risk | Planning Response |
| --- | --- |
| Existing launcher may live outside the repo. | Require explicit approval before future external-path discovery. |
| User services can have side effects. | Future discovery must not start, stop, enable, disable, or reload services. |
| Desktop entries can launch file handlers. | Future phases must treat desktop entries as inert text until operator-approved apply. |
| `--open` can surprise-launch a browser or file handler. | Keep no --open behavior in Phase 11H.0 and in default future commands. |
| Old dashboard, old Recon board, and new Neon board can be confused. | Future reports must name exact source and target commands before replacement. |
| Rollback can be unclear after launcher mutation. | Require backup path and rollback path before any replacement phase. |

## Recommended Next Phases

- Phase 11H.1: dry-run discovery/report command
- Phase 11H.2: operator-reviewed replacement plan
- Phase 11H.3: guarded apply only after explicit approval
