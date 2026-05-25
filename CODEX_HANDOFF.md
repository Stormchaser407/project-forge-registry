# Codex Handoff

## Mission

Preserve the Phase 11G Neon District / Punk Union command board state.

## Current State

Project Forge has stable support for repo discovery, tool readiness reporting,
embed planning and the approved embedded pilot, dashboard inventory JSON, the
static Neon District dashboard, dashboard launcher, Cold Start wrapper, Cold
Start desktop launcher installer, profile probing, profile home bootstrap,
controlled project open planning, dashboard launch-command display, copy-helper
polish, and the first plain editor open test.

Phase 10.7G intentionally defers deeper Codex profile isolation work because VS Code and the OpenAI/Codex extension may rely on process reuse, VS Code user-data, OS credential storage, or extension-specific behavior beyond `CODEX_HOME`.

Phase 10.9 adds closeout/release documentation only:

- `docs/PROJECT_FORGE_PHASE_10_CLOSEOUT.md`
- `docs/PROJECT_FORGE_OPERATOR_RELEASE_NOTES.md`
- `artifacts/phase_10_closeout_report.md`
- `CHANGELOG.md`

Phase 11A adds a dry-run/report-only Obsidian-ready operator memory layer under
repository artifacts only:

- `src/project_forge_registry/obsidian_mirror.py`
- `tests/test_obsidian_mirror.py`
- `docs/PROJECT_FORGE_OBSIDIAN_MIRROR.md`
- `artifacts/obsidian_mirror/`
- `artifacts/obsidian_mirror_report.md`
- `artifacts/obsidian_mirror_manifest.json`

Phase 11B adds a dry-run real-vault apply planner. It maps artifact mirror notes
to proposed vault targets, but writes only Project Forge plan artifacts:

- `src/project_forge_registry/obsidian_vault_plan.py`
- `tests/test_obsidian_vault_plan.py`
- `docs/PROJECT_FORGE_OBSIDIAN_VAULT_PLAN.md`
- `artifacts/obsidian_vault_apply_plan.md`
- `artifacts/obsidian_vault_apply_plan.json`

Phase 11B.1 normalizes the JSON schema: `vault_root` is canonical,
`vault_root_planned` is not emitted, and `entries` remains the canonical
per-note list.

Phase 11C adds guarded create-only apply code, but the real-vault apply path has
not been run in validation:

- `src/project_forge_registry/obsidian_vault_apply.py`
- `tests/test_obsidian_vault_apply.py`
- `docs/PROJECT_FORGE_OBSIDIAN_VAULT_APPLY.md`
- `artifacts/obsidian_vault_apply_dry_run_report.md`
- `artifacts/obsidian_vault_apply_dry_run.json`

Phase 11C.1 hardens the guarded apply UX before the first real vault write:

- dry-run output includes a clear preflight summary and review reminder
- real apply refusal messaging names every required guard
- real apply requires `--confirm-vault-root` to exactly match `--vault-root`
- create-only, no-overwrite, no-delete, and all-or-nothing behavior remains unchanged

Phase 11D performed the first approved real-vault apply and Phase 11D.4
verified the vault files and committed repo-local evidence:

- `artifacts/obsidian_vault_real_apply_report.md`
- current vault root: `/mnt/storage/Cole/main_vault/10 Projects/Project Forge`
- managed vault note count: 5

Phase 11E defines the maintenance policy after real vault files exist:

- `docs/PROJECT_FORGE_OBSIDIAN_MAINTENANCE_POLICY.md`
- `artifacts/obsidian_vault_maintenance_policy_report.md`

The doctrine is no-clobber: human-edited vault notes win by default; generated
artifact notes are machine output; vault notes are operator-facing memory and
may become human-edited. The safe maintenance posture is create-only, skip
identical, and block existing different. Silent overwrite, no delete behavior,
unguarded update, and apply without exact vault root confirmation remain
prohibited.

Any future update mode requires explicit operator approval, backup before
update, a diff/review report, exact vault root confirmation, and all-or-nothing
preflight. Future update mode, if ever added, should be a separate phase and
separate command/flag path, not implicit apply behavior.

Phase 11G adds a local static Neon District / Punk Union command board:

- `src/project_forge_registry/neon_command_board.py`
- `tests/test_neon_command_board.py`
- `docs/PROJECT_FORGE_NEON_COMMAND_BOARD.md`
- `artifacts/neon_command_board.html`
- `artifacts/neon_command_board_report.md`
- `artifacts/neon_command_board_manifest.json`
- `scripts/project-forge-neon-command-board`

The board is static HTML/CSS with no JavaScript. It reads repo-local artifacts
and displays System State, Project Inventory, Obsidian Memory Layer, Safety
Doctrine, Actions / Command Copy Cards, Warnings / Blockers, and Phase Roadmap
panels. Commands are copy-paste text only; the UI does not execute commands,
launch URLs, mutate state, write to the vault, create autostart entries, or
replace the old Recon Command Board.

Phase 11G.1 metadata hygiene:

- checkpoint detection prefers checkpoint tags pointing at `HEAD`
- if no checkpoint tag points at `HEAD`, it falls back to the latest checkpoint
- Neon board commit metadata is the commit observed at generation time
- committed generated artifacts may not equal the final containing commit hash
  after amend
- tags/checkpoints are operator checkpoint indicators, not executable actions

## Product Boundary

Do not block Phase 10 closeout on Personal/Business Codex account separation.

Stable claims:

- dry-run launch planning is safe
- plain editor open works
- dirty and protected projects remain blocked
- Personal/Business profile homes are prepared for later research
- Personal/Business Codex isolation is deferred and not guaranteed
- dashboard path is `artifacts/dashboard.html`
- known embedded pilot repos are `lifesaver-ledger`, `media-dedupe`, `neon-district`, and `recon_housekeeping`

## Operator Quick Start

```bash
./scripts/project-forge-cold-start
./scripts/project-forge-dashboard --no-open
./scripts/project-forge-neon-command-board
./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror
PYTHONPATH=src python3 -m project_forge_registry.obsidian_vault_plan
PYTHONPATH=src python3 -m project_forge_registry.obsidian_vault_apply --dry-run
```

## Safety

This phase does not run Codex, launch VS Code, request login, read/copy auth
files, modify external repos, write to any real Obsidian vault, apply marker
writes, create vault directories, copy files, modify target files, use remotes,
push/fetch, install packages, make network calls, create commits, or create
tags.

Phase 11G is local static frontend generation only. Do not create autostart
entries or replace the old Recon Command Board in this phase. Do not run
`--apply` for command board work.
Phase 11E is documentation/report-only.
The existing apply behavior remains guarded by `--apply`, `--yes-write-to-vault`,
explicit `--vault-root`, and matching `--confirm-vault-root`. Maintenance
validation should use docs checks, dry-run checks, read-only vault listing, and
temporary-directory tests only unless the operator explicitly approves real
vault writes.

## Recommended Release Markers

Recommended commit message:

```text
Add Phase 11G Neon command board frontend
```

Recommended final tag:

```text
v0.11.0g-neon-command-board
```

## Next Recommended Phase

Phase 11 options: Obsidian integration, repo action policies, remote strategy,
or dedicated Codex/VS Code isolation research.
