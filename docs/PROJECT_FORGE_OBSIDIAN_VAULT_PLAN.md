# Project Forge Obsidian Vault Apply Plan

## Purpose

Phase 11B adds a dry-run vault apply planner for the Project Forge Obsidian
operator memory layer.

The planner maps generated artifact mirror notes to proposed real Obsidian vault
targets, then writes only Project Forge artifact reports.

## Command

```bash
PYTHONPATH=src python3 -m project_forge_registry.obsidian_vault_plan
```

Console-script form:

```bash
project-forge-obsidian-vault-plan
```

## Inputs

The planner reads:

- `artifacts/obsidian_mirror_manifest.json`
- generated notes under `artifacts/obsidian_mirror/`

## Outputs

The planner writes only these Project Forge artifacts:

- `artifacts/obsidian_vault_apply_plan.md`
- `artifacts/obsidian_vault_apply_plan.json`

## Proposed Vault Folder

The default proposed vault folder is:

```text
/mnt/storage/Cole/main_vault/10 Projects/Project Forge/
```

This path is a proposed target only in Phase 11B. The planner does not create
the folder and does not copy notes there.

## Planned Actions

Each generated note receives a deterministic mapping with:

- source artifact path
- proposed vault target path
- action: `would_create`, `would_update`, `would_skip`, or `blocked`
- target existence, checked read-only
- reason

Current Phase 11B behavior uses `would_create`, `would_update`, or `blocked`.
`would_skip` is reserved for future policy rules.

## JSON Schema

The JSON plan uses these top-level fields:

- `mode`
- `vault_root`
- `vault_root_exists`
- `source_note_count`
- `proposed_target_count`
- `entries`
- `safety`

`entries` is the canonical per-note list. `vault_root_planned` is not emitted.

## Safety Model

Phase 11B is planning only.

The command does not:

- write to the real vault
- create vault directories
- copy files
- modify target files
- modify external repos
- apply changes
- write marker files
- add or modify remotes
- push or fetch
- install packages
- make network calls
- launch VS Code
- run Codex
- perform Codex login or auth handling

Phase 11C or later may implement an approved apply path after this plan is
reviewed.

## Validation

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m project_forge_registry.obsidian_vault_plan
python3 -m json.tool artifacts/obsidian_vault_apply_plan.json >/tmp/project-forge-obsidian-vault-plan-json-check.json
```
