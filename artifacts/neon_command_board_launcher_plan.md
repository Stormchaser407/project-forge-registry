# Neon Command Board Launcher Plan

## Phase

Phase 11H.0 - launcher/autostart replacement planning only.

## Purpose

Define the documentation-first path from the old Recon Command Board
launcher/autostart behavior toward the new Neon command board. This artifact is
a plan, not an implementation.

## Current Stable Baseline

- Phase: 11G.1 - Neon command board metadata hygiene
- Commit: `cf60a1f`
- Version tag: `v0.11.0g1-neon-command-board-metadata-hygiene`
- Checkpoint: `checkpoint-20260524-234802-phase-11g1-neon-command-board-metadata-hygiene`
- Neon board safety model: static display-only HTML/CSS, no JavaScript, no
  command execution, no vault writes

## Discovery Targets For Future Approval

Likely future discovery targets, listed only and not inspected in Phase 11H.0:

- `~/.config/autostart`
- `~/.config/systemd/user`
- `~/.local/share/applications`
- `scripts/`
- `pyproject.toml`
- Existing Project Forge dashboard scripts/docs inside the repo

## Future Dry-Run Discovery Design

A future dry-run discovery command may inspect approved local targets after
operator approval. It must produce markdown and JSON artifacts, avoid mutation,
avoid launching anything, avoid service enable/disable behavior, and avoid the
real Obsidian vault.

Expected artifact names for a future command:

- `artifacts/neon_command_board_launcher_discovery.md`
- `artifacts/neon_command_board_launcher_discovery.json`

## Replacement Criteria

- exact old launcher/autostart target identified
- exact new Neon command board target identified
- backup path defined
- rollback path defined
- operator approval phrase required
- all-or-nothing preflight
- no silent overwrite
- no delete behavior

## Proposed Future Operator Commands

Copy-paste text only:

```bash
./scripts/project-forge-neon-command-board
```

```bash
PYTHONPATH=src python3 -m project_forge_registry.neon_command_board
```

Future dry-run discovery command, if approved and implemented:

```bash
./scripts/project-forge-neon-command-board-launcher-plan --dry-run
```

No real replacement command is included as a normal action.

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
- no external launcher/autostart path inspection in this phase

## Risk Register

- Existing launcher may live outside the repo.
- User services can have side effects.
- Desktop entries can launch file handlers.
- `--open` can surprise-launch browser/file handler behavior.
- Old dashboard, old Recon board, and new Neon board can be confused.
- Rollback must be explicit before any replacement.

## Recommended Next Phases

- Phase 11H.1 dry-run discovery/report command
- Phase 11H.2 operator-reviewed replacement plan
- Phase 11H.3 guarded apply only after explicit approval
