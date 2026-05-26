# Project Forge Neon Command Board Launcher Discovery

## Purpose

Phase 11H.1 adds a dry-run discovery command for launcher/autostart references
related to the old Recon Command Board and the new Neon command board.

The command is read-only. It produces markdown and JSON artifacts, performs no
mutation, executes no discovered commands, and requires operator approval before
replacement.

## Command

```bash
PYTHONPATH=src python3 -m project_forge_registry.neon_command_board_launcher_discovery
```

Wrapper form:

```bash
./scripts/project-forge-neon-command-board-launcher-discovery
```

## Outputs

- `artifacts/neon_command_board_launcher_discovery.md`
- `artifacts/neon_command_board_launcher_discovery.json`

## Approved Discovery Scope

Phase 11H.1 may inspect these locations in read-only mode:

- `scripts/`
- `pyproject.toml`
- `docs/`
- `artifacts/`
- `~/.config/autostart`
- `~/.config/systemd/user`
- `~/.local/share/applications`

Missing external directories are reported as skipped/missing, not as errors.

## Report Sections

- Purpose
- Scope
- Discovery targets inspected
- Repo-local launcher candidates
- User-local autostart candidates
- User-local systemd user service candidates
- User-local desktop entry candidates
- References found
- Risks / warnings
- Non-goals
- Recommended next phase

## Safety Model

- dry-run discovery
- read-only
- no mutation
- no autostart replacement
- no systemd changes
- no desktop entry changes
- no vault writes
- no --open
- no command execution
- no browser, file handler, or VS Code launch
- no push, fetch, or remote contact
- operator approval required before replacement

The discovery command reads text files only from approved targets. It records
matched paths, terms, and line numbers. It does not execute commands from
discovered files and does not call service managers or launchers.

## Recommended Next Phase

Phase 11H.2 should turn reviewed discovery output into an operator-reviewed
replacement plan. Any future replacement still needs exact old target
identification, exact Neon command board target identification, backup path,
rollback path, all-or-nothing preflight, and explicit operator approval.
