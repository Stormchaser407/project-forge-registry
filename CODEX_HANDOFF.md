# Codex Handoff

## Mission

Preserve the Phase 11B dry-run Obsidian vault apply plan state.

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

Phase 11C apply behavior is implemented for future operator use, but remains
guarded by `--apply`, `--yes-write-to-vault`, and explicit `--vault-root`.
Validation should use dry-run and temporary-directory tests only unless the
operator explicitly approves real vault writes.

## Recommended Release Markers

Recommended commit message:

```text
Add Phase 11C guarded Obsidian vault apply command
```

Recommended final tag:

```text
v0.11.0c-guarded-obsidian-vault-apply
```

## Next Recommended Phase

Phase 11 options: Obsidian integration, repo action policies, remote strategy,
or dedicated Codex/VS Code isolation research.
