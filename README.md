# project-forge-registry

`project-forge-registry` is a dry-run-first registry and discovery tool for local projects. Its first milestone is to scan likely project directories, summarize what is present, and generate proposal artifacts for later workspace, launcher, documentation, and remote-management phases.

## Purpose

- Build a safe inventory of local projects before automation exists.
- Propose normalized slugs, categories, launch commands, workspace targets, and Obsidian note targets.
- Create human-readable and machine-readable artifacts that can be reviewed before any write actions are introduced in later phases.
- Use `/home/cole/main_vault/10 Projects/<project-slug>` as the canonical Obsidian project mirror target.

## Non-Goals

- No GitHub or Codeberg pushes.
- No remote creation or mirror configuration.
- No git initialization in existing folders.
- No writes inside scanned project directories.
- No code copy into Obsidian.
- No destructive or bulk-mutating operations.

## Safety Rules

- Dry-run only.
- Read existing project folders without modifying them.
- Write outputs only to this repository's `artifacts/` directory during phase one.
- Treat env files, database files, and `node_modules` as safety signals that require review.
- Prefer additive follow-up automation with explicit approval gates.
- `system_bound_project` means an active or important project that may intentionally live outside `/mnt/storage/Cole/Projects`, may be referenced by NixOS, Home Manager, systemd, launchers, services, or scripts, must not be moved automatically, must not be bulk-registered into normal sync automation, and should default to `document_only_for_now`.
- `reconciliation_required` means a duplicate, old copy, or partially overlapping folder that may contain storage-only operational material, must not be deleted automatically, must not be merged automatically, and should default to `compare_only`.
- Cerberus is a special-case project family: do not move `/home/cole/cerberus`, do not delete `/mnt/storage/Cole/cerberus`, do not create GitHub or Codeberg sync automation for Cerberus, and do not copy `recon/raw`, `recon/cases`, `exports`, `logs`, `databases`, or operational files into Obsidian.
- Cerberus Obsidian output is limited to high-level notes only: `project home`, `workspace map`, `runbook index`, and `reconciliation note`.

## Usage

Run the scanner with the default roots:

```bash
./scripts/project-scan
```

Run with custom roots:

```bash
./scripts/project-scan \
  --scan-root /mnt/storage/Cole/Projects \
  --scan-root /home/cole/Projects
```

Limit output while iterating on heuristics:

```bash
./scripts/project-scan --limit 5
```

## Generated Artifacts

- `artifacts/project_scan_report.md`
- `artifacts/project_scan_report.json`
- `artifacts/projects_proposed.yml`
- `artifacts/PROJECT_COMMAND_BOARD_DRAFT.md`

## Detection Model

For each first-level folder in each scan root, the scanner records:

- path
- folder name
- safe slug
- git/readme/workspace/project metadata markers
- package and build markers
- env/database/node_modules safety markers
- likely stack
- recommended status
- recommended category
- recommended action
- canonical path and constraint flags when special handling applies
- safety warnings

## Examples

An active git-backed repo with a readme will often be proposed as `active_project`.

A folder with `node_modules` but no git metadata may be proposed as `operated_tool` or flagged for review.

A folder with env files or local databases will be marked with safety warnings and will default to `review_required`.

All proposed Obsidian mirrors use `/home/cole/main_vault/10 Projects/<project-slug>`.

`system_bound_project` entries default to `document_only_for_now`.

`reconciliation_required` entries default to `compare_only`.

## Next Milestones

1. Workspace and launcher generation.
2. `.project/project.yml` generation.
3. Obsidian mirror folder generation.
4. Docs-only sync using Obsidian `_export` folders.
5. GitHub and Codeberg remote configuration.
6. Safety and secrets checking.
7. Optional watcher or timer automation.

See [docs/later_phase_roadmap.md](/mnt/storage/Cole/Projects/project-forge-registry/docs/later_phase_roadmap.md:1) for the phase outline.
See [docs/SITREP_2026-05-06_housekeeping.md](/mnt/storage/Cole/Projects/project-forge-registry/docs/SITREP_2026-05-06_housekeeping.md:1) for the formal housekeeping constraints.
See [docs/SITREP_2026-05-06_workspace_launcher_phase2.md](/mnt/storage/Cole/Projects/project-forge-registry/docs/SITREP_2026-05-06_workspace_launcher_phase2.md:1) for the Phase 2 workspace and launcher design record.

## Phase 2 Command

`project-forge-workspace-generate` consumes `artifacts/project_scan_report.json` and plans or generates:

- `~/.config/Code/User/workspaces/<slug>.code-workspace`
- `~/.local/bin/code-<slug>`
- a report inside this repository's `artifacts/` directory

Default behavior is dry-run. In dry-run mode, only the artifact report is written.

Example dry-run:

```bash
PYTHONPATH=src python3 -m project_forge_registry.workspace_generation --dry-run
```

Example apply:

```bash
PYTHONPATH=src python3 -m project_forge_registry.workspace_generation --apply
```

### Phase 2 Defaults

- Eligible by default: `active_project`, `operated_tool`
- Skipped by default: `system_bound_project`, `reconciliation_required`, `archive`, `lab`, `unknown`, `vendor_clone`
- `vendor_clone` requires `--include-category vendor_clone`
- `lab` requires `--include-category lab`
- `archive` requires `--include-archive` or `--include-category archive`
- `project-forge-command-center.code-workspace` is preserved as an operator workspace

### Phase 2 Safety Rules

- Dry-run first.
- No writes outside approved target types unless `--apply` is explicitly used.
- No project folder modifications.
- No git initialization.
- No GitHub or Codeberg remote creation.
- No Obsidian sync.
- Existing workspace and launcher files are backed up before overwrite.

## Phase 3 Command

`project-forge-passport-generate` consumes `artifacts/project_scan_report.json` and plans or generates passport proposal files at:

- `artifacts/project_passports/<slug>.project.yml`
- `artifacts/project_passport_generation_report.md`

Default behavior is dry-run. In dry-run mode, only the artifact report is written.

Example dry-run:

```bash
PYTHONPATH=src python3 -m project_forge_registry.passport_generation --dry-run
```

Example apply:

```bash
PYTHONPATH=src python3 -m project_forge_registry.passport_generation --apply
```

### Phase 3 Defaults

- Eligible by default: `active_project`, `operated_tool`
- Skipped by default: `system_bound_project`, `reconciliation_required`, `archive`, `lab`, `unknown`, `vendor_clone`
- Cerberus-related entries remain protected and skipped

### Phase 3 Safety Rules

- Dry-run first.
- `--apply` writes only inside this repository's `artifacts/project_passports/` directory in this phase.
- No project folder modifications.
- No git initialization.
- No GitHub or Codeberg remote creation.
- No Obsidian sync.
- Existing passport proposal files are backed up before overwrite.
