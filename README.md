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

## Phase 4 Command

`project-forge-obsidian-mirror-generate` consumes `artifacts/project_passports/*.project.yml` and plans or generates mirror proposal files at:

- `artifacts/obsidian_mirrors/<slug>/`
- `artifacts/obsidian_mirror_generation_report.md`

Default behavior is dry-run. In dry-run mode, only the artifact report is written.

Example dry-run:

```bash
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror_generation --dry-run
```

Example apply:

```bash
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror_generation --apply
```

### Phase 4 Defaults

- Eligible by default: `active_project`, `operated_tool`
- Skipped by default: `system_bound_project`, `reconciliation_required`, `archive`, `lab`, `unknown`, `vendor_clone`
- Additional safety skips: `safety.do_not_sync=true`, `sync.allow_code_to_obsidian=true`, `sync.allow_secrets=true`, and Cerberus-related entries

### Phase 4 Safety Rules

- Dry-run first.
- `--apply` writes proposed mirror files only inside this repository's `artifacts/obsidian_mirrors/` directory in this phase.
- No writes to `/home/cole/main_vault`.
- No project folder modifications.
- No source code copy into mirror proposal files.
- No git initialization.
- No GitHub or Codeberg remote creation.
- No Obsidian sync.
- Existing mirror proposal files are backed up before overwrite.

### Capture For Chat

The Phase 4 Python command prints the mirror proposal directory and report path clearly so terminal wrappers can capture verification output without any clipboard dependency inside Python.

Suggested dry-run verification capture:

```bash
{
  PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror_generation --dry-run
  sed -n '1,220p' artifacts/obsidian_mirror_generation_report.md
} | capture-for-chat phase4-obsidian-mirror-check
```

Suggested apply verification capture:

```bash
{
  PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror_generation --apply
  rg --files artifacts/obsidian_mirrors
  sed -n '1,220p' artifacts/obsidian_mirror_generation_report.md
} | capture-for-chat phase4-obsidian-mirror-check
```

## Phase 4b Command

`project-forge-obsidian-sync` consumes:

- `artifacts/project_passports/<slug>.project.yml`
- `artifacts/obsidian_mirrors/<slug>/`

and plans or performs a docs-only markdown sync to:

- `/home/cole/main_vault/10 Projects/<project-folder>/`

The project folder name is derived from `paths.obsidian` in the passport.

Default behavior is dry-run. In dry-run mode, only the artifact report is written:

- `artifacts/obsidian_sync_report.md`

Example dry-run:

```bash
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync \
  --slug project_forge_registry \
  --dry-run
```

Example apply:

```bash
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync \
  --slug project_forge_registry \
  --apply
```

### Phase 4b CLI

- `--slug <slug>`: required slug to sync.
- `--passport-dir <path>`: defaults to `artifacts/project_passports`.
- `--mirror-dir <path>`: defaults to `artifacts/obsidian_mirrors`.
- `--vault-project-root <path>`: defaults to `/home/cole/main_vault/10 Projects`.
- `--dry-run`: plan only (default mode).
- `--apply`: perform copy.
- `--report-name <filename>`: defaults to `obsidian_sync_report.md`.
- `--backup-suffix <suffix>`: optional backup suffix, otherwise timestamp-based.

### Phase 4b Safety Rules

- Dry-run first.
- Markdown only (`*.md`) from mirror source.
- Excludes include `*.bak*`, `.env*`, `.py`, `.js`, `.ts`, `.nix`, `.json`, `.yml`, `.yaml`, `.db`, `.sqlite`, `.log`.
- Excludes directories: `node_modules/`, `.venv/`, `__pycache__/`, `.git/`.
- No destination deletes.
- Existing destination markdown files are backed up before overwrite.
- Destination must stay under `--vault-project-root`.
- Source paths for passports and mirrors must stay inside this repository.
- Cerberus-protected entries are skipped.
- No GitHub/Codeberg sync and no external project-folder writes.

### Phase 4b Capture For Chat

Suggested dry-run verification capture:

```bash
{
  PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync \
    --slug project_forge_registry \
    --dry-run
  sed -n '1,260p' artifacts/obsidian_sync_report.md
} | capture-for-chat phase4b-obsidian-sync-dry-run
```

Suggested apply verification capture:

```bash
{
  PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync \
    --slug project_forge_registry \
    --apply
  sed -n '1,260p' artifacts/obsidian_sync_report.md
  find "/home/cole/main_vault/10 Projects/project-forge-registry" -maxdepth 3 -type f | sort
} | capture-for-chat phase4b-obsidian-sync-apply
```

## Phase 5 Command

`project-forge-export-sync` plans or performs a controlled reverse docs lane from Obsidian export staging to repository docs:

- source root: `/home/cole/main_vault/10 Projects/<slug>/_export/`
- default source sub-scope: `_export/docs/` only
- destination root: `<project local_path>/docs/`

Default behavior is dry-run. In dry-run mode, only the artifact report is written:

- `artifacts/export_sync_report.md`

Example dry-run:

```bash
PYTHONPATH=src python3 -m project_forge_registry.export_sync \
  --slug project_forge_registry \
  --dry-run
```

### Phase 5 CLI

- `--slug <slug>`: required slug to sync.
- `--passport-dir <path>`: defaults to `artifacts/project_passports`.
- `--vault-project-root <path>`: defaults to `/home/cole/main_vault/10 Projects`.
- `--repo-root-override <path>`: optional destination override; must stay inside `<local_path>/docs/`.
- `--dry-run`: plan/report only (default mode).
- `--apply`: perform copy (not required for planning workflows).
- `--include-file <relative path>`: include specific `_export`-relative files.
- `--exclude-file <relative path>`: exclude specific `_export`-relative files.
- `--report-name <filename>`: defaults to `export_sync_report.md`.
- `--backup-suffix <suffix>`: optional backup suffix, otherwise timestamp-based.

### Phase 5 Safety Rules

- Dry-run first.
- Markdown-only lane (`*.md`).
- Default source scope is `_export/docs/` only.
- `_export/README.md` is not mapped automatically.
- If explicitly included (`--include-file README.md`), it maps only to `docs/README.md`, never repo-root `README.md`.
- No destination deletes.
- Existing destination markdown files are backed up before overwrite.
- Destination must stay inside `<project local_path>/docs/`.
- Passport safety flags gate eligibility (`do_not_sync`, `allow_code_to_obsidian`, `allow_secrets`).
- Cerberus-related slugs/paths are protected and skipped.
- No GitHub/Codeberg sync actions in this lane.

## Phase 7 Commands

Phase 7 introduces local-only remote policy tooling:

- `project-forge-remote-plan`
- `project-forge-remote-verify`
- `project-forge-push-ready`

Both commands are dry-run/read-only in this phase. They do not add remotes, push, fetch, or contact remote services.

Module equivalent (subcommands):

- `PYTHONPATH=src python3 -m project_forge_registry.remote_policy plan ...`
- `PYTHONPATH=src python3 -m project_forge_registry.remote_policy verify ...`
- `PYTHONPATH=src python3 -m project_forge_registry.remote_policy push-ready ...`

### Phase 7 CLI

`project-forge-remote-plan`:

- `--slug <slug>` (required)
- `--passport-dir <path>` (default `artifacts/project_passports`)
- `--report-name <filename>` (default `remote_plan_report.md`)
- `--dry-run`

`project-forge-remote-verify`:

- `--slug <slug>` (required)
- `--passport-dir <path>` (default `artifacts/project_passports`)
- `--require-clean-tree`
- `--require-tests-pass` (reported as pending Phase 7b/8 in this phase)
- `--require-doc-reports-current` (reported as pending Phase 7b/8 in this phase)
- `--report-name <filename>` (default `remote_verify_report.md`)
- `--dry-run`

`project-forge-push-ready`:

- `--slug <slug>` (required)
- `--passport-dir <path>` (default `artifacts/project_passports`)
- `--require-clean-tree`
- `--require-tests-pass`
- `--require-doc-reports-current`
- `--require-export-report-current`
- `--report-name <filename>` (default `push_ready_report.md`)
- `--dry-run`

### Phase 7 Safety Rules

- Read-only policy/report tooling only.
- No remote add/modify actions.
- No push, fetch, or external remote contact.
- Protected projects (Cerberus-related, reconciliation/system-bound/unknown/review_required) are blocked by policy.
- Push-ready is not granted in this phase.

### Phase 7b Push-Ready Notes

- `project-forge-push-ready` is a read-only preflight gate.
- Final aggregate statuses are:
- `blocked`
- `incomplete`
- `ready_for_operator_review`
- `ready_to_push` is intentionally not returned in this phase.
- Secret/sensitive scanning is filename-based for tracked/staged files and reports findings without reading secret contents.


## Phase 8.5: Safe project-sync wrapper

Safe default operator command:

    ./scripts/project-sync-safe

Specific slug:

    ./scripts/project-sync-safe project_forge_registry

The wrapper runs `project-sync` in dry-run mode only. It does not pass `--apply`, does not add remotes, does not push/fetch, and does not contact GitHub or Codeberg.

See:

    docs/PROJECT_SYNC_OPERATOR_RUNBOOK.md

## Phase 10.6B: Dashboard launcher wrapper

Refresh the dashboard inventory and static HTML without opening a browser:

    ./scripts/project-forge-dashboard

Explicit no-open mode:

    ./scripts/project-forge-dashboard --no-open

Open the local dashboard with `xdg-open` when available:

    ./scripts/project-forge-dashboard --open

The wrapper regenerates `artifacts/dashboard_inventory.json`,
`artifacts/dashboard_inventory_report.md`, and `artifacts/dashboard.html`.
It does not apply changes, write marker files, touch remotes, push/fetch,
install packages, contact GitHub or Codeberg, or launch VS Code.

See:

    docs/PROJECT_FORGE_DASHBOARD_LAUNCHER.md

## Phase 10.8A: Cold Start wrapper

Resume Project Forge with the standard local status, test, sync, and dashboard
refresh sequence:

    ./scripts/project-forge-cold-start

Open the local dashboard after refresh when `xdg-open` is available:

    ./scripts/project-forge-cold-start --open-dashboard

The Cold Start wrapper is a status/resume/check script. It does not apply
changes, write marker files, touch remotes, push/fetch, install packages,
contact GitHub or Codeberg, launch VS Code, create commits, or create tags.

See:

    docs/PROJECT_FORGE_COLD_START.md

## Phase 10.8B: Cold Start desktop launcher

Preview the user-local desktop launcher/icon install without writing files:

    ./scripts/project-forge-install-cold-start-desktop --dry-run

Install the user-local launcher and Neon District SVG icon only after explicit
operator approval:

    ./scripts/project-forge-install-cold-start-desktop

The installer writes only the expected user-local desktop/icon files. It does
not run Cold Start, open the dashboard, apply changes, write marker files, touch
remotes, push/fetch, install packages, make network calls, launch VS Code,
create commits, or create tags.

See:

    docs/PROJECT_FORGE_COLD_START_DESKTOP.md

## Phase 10.7A: Codex profile probe

Probe a proposed local Codex workspace/profile selection without logging in,
reading tokens, launching VS Code, or running Codex:

    ./scripts/project-forge-codex-profile-probe --profile personal
    ./scripts/project-forge-codex-profile-probe --profile business
    ./scripts/project-forge-codex-profile-probe --profile plain

The probe is for the one-account, multiple-workspace operator model where the
operator may choose Personal or Business context after login. It checks proposed
`CODEX_HOME` paths and whether `codex` is on `PATH`, but it does not read or
print auth contents.

Future local overrides belong in ignored file:

    config/codex_profiles.local.yml

See:

    docs/PROJECT_FORGE_CODEX_PROFILES.md

## Phase 10.7B: Codex profile bootstrap

Preview local Codex profile home setup:

    ./scripts/project-forge-codex-profile-bootstrap --dry-run

Create the local profile homes and ignored local config skeleton:

    ./scripts/project-forge-codex-profile-bootstrap --write

The bootstrap prepares `~/.codex-personal`, `~/.codex-business`, and `config/codex_profiles.local.yml`.
It does not read tokens, print auth contents, copy auth files, execute Codex, launch VS Code, contact remotes, install packages, create commits, or create tags.

See:

    docs/PROJECT_FORGE_CODEX_PROFILE_BOOTSTRAP.md

## Phase 10.7C: Controlled project open wrapper

Preview a project launch from the dashboard inventory with an explicit profile:

    ./scripts/project-forge-open-project --slug lifesaver-ledger --profile personal --dry-run
    ./scripts/project-forge-open-project --slug lifesaver-ledger --profile business --dry-run
    ./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --dry-run

Explicit editor launch is available only with `--open` after reviewing dry-run
output. Personal launches set `CODEX_HOME=~/.codex-personal`, Business launches
set `CODEX_HOME=~/.codex-business`, and Plain launches do not set `CODEX_HOME`.

The wrapper reads `artifacts/dashboard_inventory.json`, resolves the selected
slug to its `vscode_target` or workspace target, and applies the Phase 10.7C
eligibility policy. `known_embedded` and `clean_candidate` projects are allowed.
`dirty_candidate_review_first`, `protected_manual_review`, and unknown
categories are blocked. The control repo remains dry-run/profile-restricted.

It does not run Codex, attempt login, read or print auth contents, copy auth
files, modify dashboard inventory, touch remotes, contact GitHub or Codeberg,
install packages, mutate external repos, create commits, or create tags.

See:

    docs/PROJECT_FORGE_OPEN_PROJECT.md

## Phase 10.7D: Dashboard launch command display

The static dashboard now shows copy-paste dry-run launch commands for eligible
projects and policy-blocked text for ineligible ones.

Eligible cards display:

    ./scripts/project-forge-open-project --slug <slug> --profile personal --dry-run
    ./scripts/project-forge-open-project --slug <slug> --profile business --dry-run
    ./scripts/project-forge-open-project --slug <slug> --profile plain --dry-run

This phase is display-only. The HTML does not run commands, does not expose
`--open`, and does not generate `file://`, `vscode://`, or JavaScript launcher
actions.

See:

    docs/PROJECT_FORGE_DASHBOARD_UI.md

## Phase 10.7E: Dashboard copy-helper polish

The static dashboard keeps the same non-executing safety model, but the launch
area is now easier to copy from:

- `Copy-Paste Launch Commands` heading
- explicit Personal, Business, and Plain context labels
- a dry-run-only safety note
- separate monospace command blocks for each eligible launch command

The HTML still does not execute commands, render `--open`, or generate
`file://`, `vscode://`, JavaScript, or executable launcher links.

See:

    docs/PROJECT_FORGE_DASHBOARD_UI.md

## Phase 10.7F: Plain open test findings

The first controlled local editor open test used:

```bash
./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --open
```

The wrapper resolved the known embedded project and launched VS Code without setting `CODEX_HOME`.

A normal VS Code session may already have OpenAI/Codex extension app-server processes running. This is a finding for later Personal/Business profile testing, not evidence that Project Forge itself executed Codex.

See:

```text
docs/PROJECT_FORGE_PLAIN_OPEN_TEST.md
```

## Phase 10.7G: Codex profile isolation deferred

Deeper Personal/Business Codex profile isolation research is deferred until after the stable Phase 10 closeout.

Project Forge currently supports safe dry-run launch planning, profile homes, dashboard launch command display, and plain editor open testing. It does not yet guarantee that VS Code or the OpenAI/Codex extension honors `CODEX_HOME` as a complete Personal/Business isolation boundary.

See:

```text
docs/PROJECT_FORGE_CODEX_PROFILE_ISOLATION_DEFERRAL.md
```

## Phase 10.9: Local command center closeout

Phase 10.9 packages the stable local command center boundary for operator use.

Quick start:

```bash
./scripts/project-forge-cold-start
./scripts/project-forge-dashboard --no-open
./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --dry-run
```

Dashboard:

```text
artifacts/dashboard.html
```

The closeout confirms that Cold Start, the dashboard refresh, display-only launch
commands, known embedded pilot repos, and plain open findings are stable enough
for a local release. Codex Personal/Business isolation remains deferred.

See:

```text
docs/PROJECT_FORGE_PHASE_10_CLOSEOUT.md
docs/PROJECT_FORGE_OPERATOR_RELEASE_NOTES.md
artifacts/phase_10_closeout_report.md
```

## Phase 11A: Obsidian artifact mirror

Generate Obsidian-ready Markdown notes under repository artifacts only:

```bash
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror
```

Outputs:

```text
artifacts/obsidian_mirror/
artifacts/obsidian_mirror_report.md
artifacts/obsidian_mirror_manifest.json
```

This phase is a dry-run operator memory layer. It does not write to any real
Obsidian vault, modify external repos, apply changes, touch remotes, push/fetch,
install packages, make network calls, launch VS Code, or perform Codex
login/auth handling.

See:

```text
docs/PROJECT_FORGE_OBSIDIAN_MIRROR.md
```

## Phase 11B: Obsidian vault apply plan

Plan a real-vault apply without writing to the vault:

```bash
PYTHONPATH=src python3 -m project_forge_registry.obsidian_vault_plan
```

Outputs:

```text
artifacts/obsidian_vault_apply_plan.md
artifacts/obsidian_vault_apply_plan.json
```

The default proposed vault folder is:

```text
/mnt/storage/Cole/main_vault/10 Projects/Project Forge/
```

This phase is dry-run planning only. It does not create directories, copy files,
modify target files, apply changes, touch remotes, push/fetch, install packages,
make network calls, launch VS Code, or perform Codex login/auth handling.

The JSON plan uses `vault_root` as the canonical proposed target root field and
`entries` as the canonical per-note mapping list.

See:

```text
docs/PROJECT_FORGE_OBSIDIAN_VAULT_PLAN.md
```

## Phase 11C: Guarded Obsidian vault apply

Review the create-only vault apply preflight without writing to the vault:

```bash
PYTHONPATH=src python3 -m project_forge_registry.obsidian_vault_apply --dry-run
```

Outputs:

```text
artifacts/obsidian_vault_apply_dry_run_report.md
artifacts/obsidian_vault_apply_dry_run.json
```

Real apply is implemented but guarded. It requires `--apply`,
`--yes-write-to-vault`, and an explicit `--vault-root`. Phase 11C is
create-only: no overwrite, no delete, and all-or-nothing preflight before any
write.

See:

```text
docs/PROJECT_FORGE_OBSIDIAN_VAULT_APPLY.md
```
