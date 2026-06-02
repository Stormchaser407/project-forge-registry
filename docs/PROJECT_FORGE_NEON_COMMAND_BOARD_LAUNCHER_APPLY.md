# Project Forge Neon Command Board Launcher Apply

## Purpose

Phase 11H.5 adds guarded launcher replacement apply command capability for the
Project Forge Neon command board transition.

The command is default dry-run. It produces repo-local reports unless a future
operator runs it with every real apply guard satisfied.

## Command

```bash
PYTHONPATH=src python3 -m project_forge_registry.neon_command_board_launcher_apply
```

Console-script form:

```bash
project-forge-neon-command-board-launcher-apply
```

Wrapper form:

```bash
./scripts/project-forge-neon-command-board-launcher-apply
```

## Outputs

- `artifacts/neon_command_board_launcher_apply_dry_run.md`
- `artifacts/neon_command_board_launcher_apply_dry_run.json`

## Safety

Phase 11H.5 is a guarded launcher replacement apply command with default
dry-run, no real apply unless all guards pass, no mutation during dry-run, no
launch behavior, no --open, no systemd changes, no desktop entry changes unless
explicitly approved, no autostart changes unless explicitly approved, backup
before overwrite, rollback required, no delete, no vault writes, exact approval
phrase required, exact target path confirmation required, and clean git tree
required.

## Required Real Apply Guards

A future real apply requires all guards:

- `--apply`
- `--yes-replace-launcher`
- `--approval-phrase "APPROVE 11H.5 GUARDED LAUNCHER REPLACEMENT APPLY"`
- `--target-path ~/.local/share/applications/project-forge-command-board.desktop`
- `--confirm-target-path` exactly matching `--target-path`
- `--clean-git-tree-confirmed` after operator verification
- `--expected-head` or `--expected-tag`
- Phase 11H.4 preflight artifact present
- proposed target included in the Phase 11H.4 preflight artifact
- backup path defined
- rollback plan defined
- no ambiguous target class
- no request to launch, open, enable, disable, or reload anything

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

## Operator Note

Do not run real apply until the dry-run report, target path, backup plan,
rollback plan, and expected HEAD or tag have been reviewed. This Codex phase
implements the capability but does not run live apply.
