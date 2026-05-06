# SITREP 2026-05-06 Workspace Launcher Phase 2

This document records the proposed Phase 2 design for safe VS Code workspace and launcher generation in the federated Project Forge Command Center environment.

This is a design-only SITREP. It does not approve implementation, filesystem writes outside this repository, project mutation, git initialization, remote configuration, or Obsidian sync.

## Scope

- Repository in scope: `/mnt/storage/Cole/Projects/project-forge-registry`
- Context-only workspace members:
- `/mnt/storage/Cole/Projects/recon_housekeeping`
- `/mnt/storage/Cole/Projects`
- Proposed output types:
- `~/.config/Code/User/workspaces/<slug>.code-workspace`
- `~/.local/bin/code-<slug>`
- artifact report describing created and skipped items

## Goal

- Consume approved registry proposal data.
- Generate VS Code `.code-workspace` files for safe projects only.
- Generate `code-<slug>` launcher scripts for safe projects only.
- Keep all behavior dry-run-first, auditable, and reversible by backup.

## Proposed Command

- Command name: `project-forge-workspace-generate`

## Proposed CLI Surface

- `--input-json <path>`
- `--artifacts-dir <path>`
- `--dry-run`
- `--apply`
- `--include-slug <slug>`
- `--exclude-slug <slug>`
- `--include-category <category>`
- `--exclude-category <category>`
- `--include-archive`
- `--workspace-dir <path>`
- `--launcher-dir <path>`
- `--report-name <filename>`
- `--backup-suffix <suffix>`
- `--preserve-workspace <name>`

## Input Model

- Primary machine input should be `artifacts/project_scan_report.json`.
- The repository already emits JSON using only the standard library.
- JSON input avoids introducing YAML parsing dependencies during this phase.
- Registry proposal data should be filtered through classification, action, constraints, and slug safety checks before any write plan is produced.

## Write Boundaries

When implementation is approved, writes must be limited to:

- `~/.config/Code/User/workspaces/<slug>.code-workspace`
- `~/.local/bin/code-<slug>`
- report artifacts inside the chosen artifacts directory

The generator must not write:

- inside project folders
- inside `recon_housekeeping`
- inside any external project folder
- inside Obsidian
- inside git remotes or remote configuration

## Safety Behavior

- Default mode must be `--dry-run`.
- `--apply` must be required for any filesystem write outside repository artifacts.
- Existing workspace and launcher files must be backed up before overwrite.
- Existing files must be replaced only after backup succeeds.
- The command must refuse target paths outside the approved workspace, launcher, and artifacts directories.
- The command must not modify project contents.
- The command must not initialize git.
- The command must not create GitHub remotes.
- The command must not create Codeberg remotes.
- The command must not sync Obsidian.
- The command must produce a report describing eligible, skipped, planned, backed-up, and written items.

## Default Eligibility

Eligible by default:

- `active_project`
- `operated_tool`

Additional default gating:

- include only records whose `registry_action` is `register_full` or `workspace_only`
- exclude records with protected-name collisions
- exclude records with duplicate slug collisions until manually resolved

## Default Skips

Skipped by default:

- `system_bound_project`
- `reconciliation_required`
- `archive`
- `lab`
- `unknown`
- `vendor_clone`

Also skipped by default:

- `registry_action: review_required`
- `registry_action: compare_only`
- `registry_action: document_only_for_now`
- `registry_action: ignore`
- `registry_action: obsidian_notes_only`

## Special Handling

### `system_bound_project`

- Must be skipped.
- Must not receive automated workspace/launcher generation in this phase.
- Must remain excluded from bulk sync automation.

### `reconciliation_required`

- Must be skipped.
- Must remain compare-only.
- Must not receive automated launcher generation in this phase.

### `archive`

- Must be skipped by default.
- May only be considered if explicitly included by operator flag.

### `vendor_clone`

- Must be skipped by default.
- May only be considered if explicitly included with `--include-category vendor_clone`.

### `lab`

- Must be skipped by default.
- May only be considered if explicitly included with `--include-category lab`.

### Command Center Workspace

- Preserve `project-forge-command-center.code-workspace`.
- Treat it as an operator workspace, not a normal project workspace.
- Do not overwrite it accidentally.
- If a generated target collides with that filename, skip it and report the collision.

## Proposed Output Behavior

### Dry Run

- Build an in-memory plan from proposal data.
- Report what would be created, overwritten, backed up, or skipped.
- Perform no writes outside repository-local artifacts.

### Apply

- Recompute the same plan.
- Validate all target paths again before writing.
- Create backups for existing targets.
- Write workspace and launcher files only for eligible records.
- Emit a final report with applied actions and skips.

## Example Dry-Run Output

```text
$ project-forge-workspace-generate --dry-run

Mode: dry-run
Input: artifacts/project_scan_report.json
Workspace dir: /home/cole/.config/Code/User/workspaces
Launcher dir: /home/cole/.local/bin

Protected workspaces:
- project-forge-command-center.code-workspace

Eligible:
- project_forge_registry -> create workspace, create launcher
- recon_housekeeping -> create workspace, create launcher

Skipped:
- cerberus -> classification=system_bound_project
- cerberus_storage_copy -> classification=reconciliation_required
- archive -> classification=archive, not explicitly included
- sillytavern -> action=review_required
- andclaw_comms -> action=review_required

Planned writes: 4
Planned backups: 0
Project folders modified: 0
Report: artifacts/workspace_launcher_generation_report.md
```

## Example Apply Output

```text
$ project-forge-workspace-generate --apply --include-slug project_forge_registry

Mode: apply
Input: artifacts/project_scan_report.json

Applied:
- project_forge_registry
  workspace: wrote /home/cole/.config/Code/User/workspaces/project_forge_registry.code-workspace
  launcher: wrote /home/cole/.local/bin/code-project_forge_registry

Backups:
- /home/cole/.config/Code/User/workspaces/project_forge_registry.code-workspace.bak.20260506-153000
- /home/cole/.local/bin/code-project_forge_registry.bak.20260506-153000

Skipped:
- project-forge-command-center.code-workspace -> protected operator workspace

Project folders modified: 0
Report: artifacts/workspace_launcher_generation_report.md
```

## Files Proposed For Future Implementation

Add:

- `src/project_forge_registry/workspace_generation.py`
- `src/project_forge_registry/workspace_models.py`
- `src/project_forge_registry/workspace_reporting.py`
- `tests/test_workspace_generation.py`

Change:

- `src/project_forge_registry/cli.py`
- `pyproject.toml`
- `README.md`

## Test Plan

- Verify eligibility filtering by category and `registry_action`.
- Verify forced skips for `system_bound_project`.
- Verify forced skips for `reconciliation_required`.
- Verify `archive` is excluded unless explicitly included.
- Verify protected operator workspace preservation.
- Verify duplicate slug collision handling.
- Verify workspace content rendering.
- Verify launcher content rendering.
- Verify backup planning for existing targets.
- Verify target path guard rejects unapproved destinations.
- Verify dry-run performs no writes.
- Verify apply writes only approved target types and produces a report.

## Status

- Phase 2 design recorded.
- Implementation not approved.
- No external workspace, launcher, project, git, remote, or Obsidian changes authorized by this document.
