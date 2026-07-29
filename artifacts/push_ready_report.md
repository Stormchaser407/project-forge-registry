# Push Ready Report

## Scope

- Mode: `dry-run`
- Slug: `project_forge_registry`
- Passport dir: `/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/artifacts/project_passports`
- Passport file: `/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/artifacts/project_passports/project_forge_registry.project.yml`
- Local repo path: `/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry`

## Eligibility

- Eligible: true
- Policy status: `eligible`
- Final aggregate status: `ready_for_operator_review`
- Operator approval still required: true

## Local Git State

- Inside git repo: true
- Current branch: `main`
- Working tree clean (if checked): `not_checked`

## Remote Snapshot

- `codeberg` `fetch` -> `git@codeberg.org:stormchaser/project-forge-registry.git`
- `codeberg` `push` -> `git@codeberg.org:stormchaser/project-forge-registry.git`
- `origin` `fetch` -> `git@github.com:Stormchaser407/project-forge-registry.git`
- `origin` `push` -> `git@github.com:Stormchaser407/project-forge-registry.git`

## Gate Checks

- `local_git_repository_detected` required=true passed=true detail=local path is a git repository
- `working_tree_clean` required=false passed=true detail=dirty or not checked
- `tests_pass_evidence` required=false passed=true detail=not independently verified; pending explicit test evidence
- `docs_reports_current` required=false passed=true detail=present_with_slug_mention
- `export_report_current` required=false passed=true detail=present_with_slug_mention
- `secret_scan_clear` required=true passed=true detail=git tracked/staged filename denylist scan completed

## Docs Report Evidence

- Obsidian sync report: `/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/artifacts/obsidian_sync_report.md` exists=true slug_mentioned=true detail=present_with_slug_mention
- Export sync report: `/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/artifacts/export_sync_report.md` exists=true slug_mentioned=true detail=present_with_slug_mention

## Secret Scan Summary

- Implemented: true (git-scoped=true)
- Detail: git tracked/staged filename denylist scan completed
- Suspicious tracked/staged file names: none detected

## Safety Confirmation

- Read-only preflight mode: yes
- Remotes added/modified: no
- Push/fetch performed: no
- GitHub/Codeberg network contact: no
- Ready to push returned in this phase: no
