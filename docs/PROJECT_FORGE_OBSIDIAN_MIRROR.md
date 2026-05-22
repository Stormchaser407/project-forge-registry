# Project Forge Obsidian Mirror

## Purpose

Phase 11A adds a dry-run artifact mirror that turns Project Forge state into
Obsidian-ready Markdown without writing to any real vault.

The generated notes are intended as an operator memory layer for the local
command center.

## Command

```bash
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror
```

Console-script form:

```bash
project-forge-obsidian-mirror
```

## Inputs

The mirror reads existing local Project Forge artifacts:

- `artifacts/dashboard_inventory.json`
- `artifacts/dashboard_inventory_report.md`
- `artifacts/repo_discovery_inventory.csv`
- `artifacts/phase_10_closeout_report.md`
- `docs/PROJECT_FORGE_PHASE_10_CLOSEOUT.md`
- `docs/PROJECT_FORGE_OPERATOR_RELEASE_NOTES.md`
- `CHANGELOG.md`

The dashboard inventory JSON is required. Other source artifacts are recorded
when present.

## Outputs

Generated artifact notes:

- `artifacts/obsidian_mirror/Project Forge - Command Center.md`
- `artifacts/obsidian_mirror/Project Forge - Dashboard Summary.md`
- `artifacts/obsidian_mirror/Project Forge - Known Embedded Repos.md`
- `artifacts/obsidian_mirror/Project Forge - Deferred Items.md`
- `artifacts/obsidian_mirror/Project Forge - Phase 11 Planning.md`

Generated support files:

- `artifacts/obsidian_mirror_report.md`
- `artifacts/obsidian_mirror_manifest.json`

## Note Format

Each note is deterministic Markdown with simple frontmatter, readable headings,
and tags:

- `project-forge`
- `phase-11`
- `command-center`
- `dry-run`

The notes use Obsidian wiki links such as:

- `[[Project Forge - Dashboard Summary]]`
- `[[Project Forge - Known Embedded Repos]]`
- `[[Project Forge - Deferred Items]]`
- `[[Project Forge - Phase 11 Planning]]`

No Obsidian plugin is required.

## Safety Model

This command writes only repository artifacts.

It does not:

- write to any real Obsidian vault
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

## Deferred Items

Phase 11A keeps these items deferred:

- Codex Personal/Business isolation
- real vault write/apply
- remote strategy
- repo action policy layer

## Validation

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror
python3 -m json.tool artifacts/obsidian_mirror_manifest.json >/tmp/project-forge-obsidian-mirror-manifest-check.json
find artifacts/obsidian_mirror -maxdepth 1 -type f -print | sort
```
