# Project Forge Obsidian Vault Apply

## Purpose

Phase 11C introduces guarded write-capable code for copying generated Project
Forge Obsidian artifact notes into a vault folder.

Default behavior remains dry-run.

## Command

Dry-run review:

```bash
PYTHONPATH=src python3 -m project_forge_registry.obsidian_vault_apply --dry-run
```

Console-script form:

```bash
project-forge-obsidian-vault-apply --dry-run
```

Guarded apply shape:

```bash
project-forge-obsidian-vault-apply \
  --apply \
  --yes-write-to-vault \
  --vault-root "<reviewed vault folder>"
```

Do not run guarded apply until the operator has inspected the dry-run output.

## Inputs

- `artifacts/obsidian_vault_apply_plan.json`
- generated source notes under `artifacts/obsidian_mirror/`

The command uses the canonical Phase 11B.1 fields:

- `vault_root`
- `entries`

## Dry-Run Outputs

- `artifacts/obsidian_vault_apply_dry_run_report.md`
- `artifacts/obsidian_vault_apply_dry_run.json`

Dry-run inspects source files and targets read-only, then reports:

- `would_create`
- `would_skip_identical`
- `blocked_existing_different`
- `blocked_missing_source`

## Apply Policy

Phase 11C apply is create-only.

- `--apply` is rejected unless `--yes-write-to-vault` is present.
- `--apply` requires an explicit `--vault-root`.
- no overwrite behavior is implemented
- no delete behavior is implemented
- all-or-nothing preflight runs before any write
- if any entry is blocked, no files are written
- identical existing targets are skipped
- missing targets are created only after preflight passes

## Safety Model

The command does not:

- write to the vault in dry-run
- overwrite target files
- delete target files
- modify external repos
- write marker files
- touch remotes
- push or fetch
- install packages
- make network calls
- launch VS Code
- run Codex
- perform Codex login or auth handling

Real apply should be run manually by the operator only after inspecting dry-run
output and confirming the target folder.
