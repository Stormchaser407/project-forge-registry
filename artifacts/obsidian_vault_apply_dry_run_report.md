# Project Forge Obsidian Vault Apply Dry-Run Report

## Preflight Summary

- mode: `dry-run`
- vault root: `/home/cole/main_vault/10 Projects/project_forge_registry`
- apply requested: `false`
- guard flag present: `false`
- entries reviewed: `5`
- would_create count: `0`
- would_skip_identical count: `0`
- blocked: `5`
- plan path: `artifacts/obsidian_vault_apply_plan.json`
- source root: `artifacts/obsidian_mirror`
- json path: `artifacts/obsidian_vault_apply_dry_run.json`

Review this report before running any apply command.

## Entry Review

| Source | Target | Action | Target exists | Reason |
|---|---|---|---|---|
| `artifacts/obsidian_mirror/Project Forge - Command Center.md` | `/home/cole/main_vault/10 Projects/project_forge_registry/Project Forge - Command Center.md` | `blocked_target_unavailable` | `false` | `target path unavailable: [Errno 13] Permission denied: '/home/cole/main_vault/10 Projects/project_forge_registry/Project Forge - Command Center.md'` |
| `artifacts/obsidian_mirror/Project Forge - Dashboard Summary.md` | `/home/cole/main_vault/10 Projects/project_forge_registry/Project Forge - Dashboard Summary.md` | `blocked_target_unavailable` | `false` | `target path unavailable: [Errno 13] Permission denied: '/home/cole/main_vault/10 Projects/project_forge_registry/Project Forge - Dashboard Summary.md'` |
| `artifacts/obsidian_mirror/Project Forge - Deferred Items.md` | `/home/cole/main_vault/10 Projects/project_forge_registry/Project Forge - Deferred Items.md` | `blocked_target_unavailable` | `false` | `target path unavailable: [Errno 13] Permission denied: '/home/cole/main_vault/10 Projects/project_forge_registry/Project Forge - Deferred Items.md'` |
| `artifacts/obsidian_mirror/Project Forge - Known Embedded Repos.md` | `/home/cole/main_vault/10 Projects/project_forge_registry/Project Forge - Known Embedded Repos.md` | `blocked_target_unavailable` | `false` | `target path unavailable: [Errno 13] Permission denied: '/home/cole/main_vault/10 Projects/project_forge_registry/Project Forge - Known Embedded Repos.md'` |
| `artifacts/obsidian_mirror/Project Forge - Phase 11 Planning.md` | `/home/cole/main_vault/10 Projects/project_forge_registry/Project Forge - Phase 11 Planning.md` | `blocked_target_unavailable` | `false` | `target path unavailable: [Errno 13] Permission denied: '/home/cole/main_vault/10 Projects/project_forge_registry/Project Forge - Phase 11 Planning.md'` |

## Safety Statement

- no real vault writes in dry-run
- apply requires --apply and --yes-write-to-vault
- create-only first implementation
- no overwrite
- no delete
- all-or-nothing preflight before apply writes
- no external repo writes
- no marker writes
- no remotes
- no push/fetch
- no package installs
- no network calls
- no VS Code launch
- no Codex login/auth handling

## Policy

- default command is dry-run
- --apply is rejected unless --yes-write-to-vault is also present
- --apply requires explicit --vault-root
- --apply requires --confirm-vault-root to exactly match --vault-root
- apply is create-only
- no overwrite behavior is implemented
- no delete behavior is implemented
- all-or-nothing preflight blocks every write if any entry is blocked
