# Later Phase Roadmap

This repository intentionally starts with discovery and proposal generation only.

## Planned Phases

### 1. Workspace and Launcher Generation

- Generate VS Code workspace files from approved registry entries.
- Generate `code-[project]` launchers only after paths and naming are reviewed.

### 2. `.project/project.yml` Generation

- Create a consistent local project metadata file for approved projects.
- Keep generation additive and template-driven.

### 3. Obsidian Mirror Folder Generation

- Create project note folders in Obsidian after explicit approval.
- Use `/home/cole/main_vault/10 Projects/<project-slug>` as the canonical mirror root.
- Keep notes, metadata, and exported docs separate from source code.
- Respect special-case note policies such as Cerberus high-level notes only.

### 4. Doc Sync Using Obsidian `_export` Folders

- Support docs-only sync paths.
- Preserve a one-way or constrained two-way policy depending on project safety settings.
- Never permit code copy into Obsidian by default.

### 5. GitHub and Codeberg Remote Configuration

- Add support for GitHub primary remotes and Codeberg mirrors after review.
- Require explicit opt-in before creating or updating remote configuration.
- Exclude `system_bound_project` entries like Cerberus from normal sync automation unless the user explicitly defines a narrower safe workflow later.

### 6. Safety and Secrets Checking

- Add checks for env files, credentials, generated artifacts, and large databases.
- Gate any future write or push action on safety review.
- Preserve `reconciliation_required` entries as compare-only until a manual reconciliation plan is approved.

## Constraint-Aware Handling

- `system_bound_project` defaults to `document_only_for_now`.
- `reconciliation_required` defaults to `compare_only`.
- Special-case constraints should be sourced from formal project notes such as [docs/SITREP_2026-05-06_housekeeping.md](/mnt/storage/Cole/Projects/project-forge-registry/docs/SITREP_2026-05-06_housekeeping.md:1).

### 7. Optional Watcher or Timer Automation

- Add periodic scans or watcher-based refreshes only after the core model is trusted.
- Keep automation dry-run capable and fully auditable.
