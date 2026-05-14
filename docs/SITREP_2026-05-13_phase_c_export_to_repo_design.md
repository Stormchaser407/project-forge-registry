# SITREP 2026-05-13 Phase C Export To Repo Design

This document records the Phase C design for a controlled reverse lane that exports approved Obsidian `_export` markdown into repository documentation locations.

This is design-only. It does not approve implementation, external writes, remote sync, or apply execution.

## Purpose

- Define a safe, dry-run-first pathway for moving approved docs from:
- `/home/cole/main_vault/10 Projects/<slug>/_export/`
- into repository doc locations for the same project.
- Keep this lane narrow, auditable, and explicitly gated by passport metadata.

## Non-Goals

- Not a general Obsidian sync engine.
- Not bidirectional content reconciliation.
- Not code sync.
- Not GitHub or Codeberg sync.
- Not external project-folder mutation beyond explicitly approved repo-doc destinations.
- Not Cerberus handling.

## Scope

- Repository in scope: `/mnt/storage/Cole/Projects/project-forge-registry`
- Initial operation mode: single slug required
- Initial destination model: `<project local_path>/docs/` only
- `README.md` mapping is an open decision (see Open Questions)

## Proposed Command

- `project-forge-export-sync`

## Proposed CLI Surface

- `--slug <slug>` (required)
- `--passport-dir <path>`
- `--vault-project-root <path>`
- `--repo-root-override <path>`
- `--dry-run`
- `--apply`
- `--include-file <relative path>` (repeatable)
- `--exclude-file <relative path>` (repeatable)
- `--report-name <filename>`
- `--backup-suffix <suffix>`

## Mode Rules

- Default mode: dry-run
- `--apply` required for writes
- `--dry-run` and `--apply` are mutually exclusive
- Single slug required for initial implementation phase

## Source Path Model

For slug `X`:

- Source root is exactly:
- `/home/cole/main_vault/10 Projects/X/_export/`

Path guards:

- Resolve and canonicalize source root before planning.
- Refuse source paths outside `--vault-project-root`.
- Refuse symlink/path traversal escape attempts.
- Refuse if slug path is Cerberus-related.

## Destination Path Model

Primary destination root (initial default):

- `<passport.project.local_path>/docs/`

Derived from passport metadata:

- Use `<passport-dir>/<slug>.project.yml`.
- Read project local path and safety policy fields.
- Enforce safety-based eligibility before planning.

Destination guards:

- Destination must be within project local path for slug.
- Destination must be docs-scoped by default (`docs/` subtree).
- No destination deletes.
- No writes to external project folders other than the resolved target for the slug.

`--repo-root-override` behavior (for testing/controlled scenarios):

- Optional.
- Must still remain within the resolved project local path unless explicitly relaxed in a future phase.
- If provided outside local path in Phase C initial implementation, command should error.

## Passport Dependency Rules

The command must fail closed unless passport data is valid.

Required checks:

- slug matches requested slug
- `project.local_path` exists and is non-empty
- `sync.allow_code_to_obsidian` is false
- `sync.allow_secrets` is false
- `safety.do_not_sync` is false
- project is not Cerberus-related
- classification/status is eligible for this lane

Eligibility baseline:

- allow only explicitly approved categories initially (e.g., `active_project`, `operated_tool`)
- skip unknown/review_required projects unless explicitly included by future policy extension

## Safety Rules

1. Dry-run-first
2. Markdown-only
3. `_export` subtree only
4. No source code
5. No secrets
6. No logs
7. No databases
8. No binaries
9. No deletion from destination
10. Back up existing destination docs before overwrite
11. Never touch Cerberus paths
12. Skip unknown/review_required unless explicitly approved later
13. Plan derived from passport metadata
14. Single-slug operation first
15. Report required before apply

## Eligible File Rules

- Source files must be under `_export/` for the selected slug
- Allowed extension: `.md` only
- Optional initial sub-scope recommendation: `_export/docs/**/*.md`
- If `--include-file` is provided:
- treat includes as allowlist relative to `_export/`
- includes must resolve inside source root

## Excluded File Rules

Always exclude:

- `*.bak*`
- non-markdown files
- hidden operational artifacts not ending in `.md`
- known disallowed extensions (`.py`, `.js`, `.ts`, `.json`, `.yml`, `.yaml`, `.env`, `.db`, `.sqlite`, `.log`, binaries)
- directories such as `.git/`, `node_modules/`, `.venv/`, `__pycache__/`

`--exclude-file` behavior:

- apply after allowlist resolution
- relative to `_export/`
- no path traversal

## Conflict and Backup Behavior

For each planned destination markdown path:

- If destination does not exist: plan copy
- If destination exists:
- plan backup to `<filename>.bak.<suffix>` in same directory
- on apply, create backup before overwrite
- if backup fails, do not overwrite target

No destructive behavior:

- never delete files from destination
- never prune destination directories

## Proposed Report Contents

Artifact path (default):

- `artifacts/export_sync_report.md`

Report must include:

- mode
- slug
- passport path used
- source root
- destination root
- eligibility result and skip reasons
- included files planned
- excluded files and reason
- backups planned
- writes planned
- backups created (apply)
- writes completed (apply)
- explicit safety confirmations:
- markdown-only enforced
- no delete operations
- no Cerberus access
- no source code/secrets/logs/databases moved

## Proposed Test Plan

Core tests:

- parser defaults to dry-run
- single slug required
- passport load and slug mismatch failure
- skip on `do_not_sync=true`
- skip on `allow_code_to_obsidian=true`
- skip on `allow_secrets=true`
- skip Cerberus slug/path
- source root guard under vault root
- destination guard under local project docs root
- markdown-only filtering
- `.bak` exclusion
- include/exclude relative path filtering
- dry-run writes only report
- apply creates destination dirs as needed
- apply creates backups before overwrite
- apply does not delete files
- report contains planned/copied/backup/exclusion counts
- full test suite leaves tracked repo files clean

## Open Questions

1. `_export/README.md` mapping policy:
- Candidate A: map to repo `README.md`
- Candidate B: map to repo `docs/README.md`
- Candidate C: map to neither by default; require explicit include

Safest recommendation:

- Default to Candidate C (no automatic mapping).
- Allow `_export/README.md` only when explicitly included via `--include-file README.md`.
- If included, safest first target is `docs/README.md` (not repo-root `README.md`) to avoid accidental replacement of project identity docs.

2. Should initial Phase C require `_export/docs/` only, or allow full `_export/` root markdown?
- Safer default: `_export/docs/` only in initial apply-capable phase.

3. Should unknown/review_required projects be hard-blocked or soft-skipped?
- Safer default: hard-block apply with explicit reason unless future explicit override flag is approved.

4. Should `--repo-root-override` be enabled in production mode initially?
- Safer default: allow only when override still resolves inside `<local_path>/docs` and log override usage prominently.

## Recommended Implementation Phases

### Phase C1: Planner + Report Only

- Build command parser and planning engine.
- Validate passport and path guards.
- Produce report only.
- No apply path yet.

### Phase C2: Controlled Apply For Single Slug

- Enable markdown-only copy with backup-before-overwrite.
- Keep destination limited to `<local_path>/docs/`.
- No README root mapping.

### Phase C3: Include/Exclude Refinement

- Add strict include/exclude relative path behavior.
- Improve reporting detail and conflict diagnostics.

### Phase C4: Policy Extensions (Optional)

- Evaluate explicit overrides for broader destinations.
- Evaluate controlled support for additional categories.
- Keep Cerberus protection permanent unless separately redesigned.

## Status

- Phase C design recorded.
- No implementation performed.
- No external sync authorized by this document.
