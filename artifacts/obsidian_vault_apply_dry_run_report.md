# Project Forge Obsidian Vault Apply Dry-Run Report

## Preflight Summary

- mode: `dry-run`
- vault root: `/mnt/storage/Cole/main_vault/10 Projects/Project Forge`
- apply requested: `false`
- guard flag present: `false`
- entries reviewed: `5`
- would_create count: `0`
- would_skip_identical count: `5`
- blocked: `0`
- plan path: `artifacts/obsidian_vault_apply_plan.json`
- source root: `artifacts/obsidian_mirror`
- json path: `artifacts/obsidian_vault_apply_dry_run.json`

Review this report before running any apply command.

## Entry Review

| Source | Target | Action | Target exists | Reason |
|---|---|---|---|---|
| `artifacts/obsidian_mirror/Project Forge - Command Center.md` | `/mnt/storage/Cole/main_vault/10 Projects/Project Forge/Project Forge - Command Center.md` | `would_skip_identical` | `true` | `target exists with identical content` |
| `artifacts/obsidian_mirror/Project Forge - Dashboard Summary.md` | `/mnt/storage/Cole/main_vault/10 Projects/Project Forge/Project Forge - Dashboard Summary.md` | `would_skip_identical` | `true` | `target exists with identical content` |
| `artifacts/obsidian_mirror/Project Forge - Deferred Items.md` | `/mnt/storage/Cole/main_vault/10 Projects/Project Forge/Project Forge - Deferred Items.md` | `would_skip_identical` | `true` | `target exists with identical content` |
| `artifacts/obsidian_mirror/Project Forge - Known Embedded Repos.md` | `/mnt/storage/Cole/main_vault/10 Projects/Project Forge/Project Forge - Known Embedded Repos.md` | `would_skip_identical` | `true` | `target exists with identical content` |
| `artifacts/obsidian_mirror/Project Forge - Phase 11 Planning.md` | `/mnt/storage/Cole/main_vault/10 Projects/Project Forge/Project Forge - Phase 11 Planning.md` | `would_skip_identical` | `true` | `target exists with identical content` |

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
