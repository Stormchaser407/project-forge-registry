# Project Forge Neon Command Board

## Purpose

Phase 11G adds a local static frontend command board in the Neon District /
Punk Union aesthetic. It is an operator cockpit for Project Forge status,
Obsidian memory state, safety doctrine, and copy-paste commands.

This phase does not replace the old Recon Command Board and does not create
autostart entries.

## Command

```bash
PYTHONPATH=src python3 -m project_forge_registry.neon_command_board
```

Console-script form:

```bash
project-forge-neon-command-board
```

## Outputs

- `artifacts/neon_command_board.html`
- `artifacts/neon_command_board_report.md`
- `artifacts/neon_command_board_manifest.json`

## Panels

- System State
- Project Inventory
- Obsidian Memory Layer
- Safety Doctrine
- Actions / Command Copy Cards
- Warnings / Blockers
- Phase Roadmap

## Safety Model

The board is static HTML/CSS with no JavaScript. Commands are displayed as
copy-paste text only; the UI does not execute commands, launch URLs, write
files, mutate state, contact remotes, install packages, launch VS Code, or
touch the real Obsidian vault.

The real guarded vault write command is not shown as a normal action. Operator
approval is required for any real vault write workflow.

Safety doctrine shown on the board:

- dry-run first
- create-only
- skip identical
- block different
- human-edited vault notes win
- no silent overwrite
- no delete

## Inputs

The generator reads repo-local artifacts only:

- `artifacts/dashboard_inventory.json`
- `artifacts/obsidian_vault_apply_plan.json`
- `artifacts/obsidian_vault_apply_dry_run.json`
- `artifacts/obsidian_vault_real_apply_report.md`
- `artifacts/obsidian_vault_maintenance_policy_report.md`

## Roadmap

- Phase 11G: Neon command board
- Phase 11H: launcher/autostart replacement for old Recon Command Board
- Future: backup-before-update, manual merge workflow, no-clobber update tooling
