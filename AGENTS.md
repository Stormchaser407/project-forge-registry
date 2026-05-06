# AGENTS.md

## Mission

This repository is the safety-first control plane for a personal project registry and workspace automation system.

## Core Rules

- Dry-run first.
- Never push, mirror, or configure remotes without explicit user approval.
- Never copy code into Obsidian.
- Treat `/home/cole/main_vault/10 Projects/<project-slug>` as the only canonical Obsidian project mirror path.
- Never overwrite files without backups.
- Prefer additive changes over in-place mutation.
- Produce reports before applying changes.
- Do not modify scanned project folders during discovery phases.
- Do not initialize git in existing folders during discovery phases.
- Treat secrets, env files, and database files as sensitive by default.
- Treat `system_bound_project` as non-movable and excluded from bulk sync automation by default.
- Treat `reconciliation_required` as compare-only, non-deletable, and non-mergeable by default.
- Treat Cerberus as a special case: `/home/cole/cerberus` is system-bound, `/mnt/storage/Cole/cerberus` is reconciliation-required, neither should receive automated move/delete behavior, and neither should receive GitHub or Codeberg sync automation at this phase.
- For Cerberus Obsidian material, allow only high-level notes: `project home`, `workspace map`, `runbook index`, and `reconciliation note`.
- Never copy Cerberus `recon/raw`, `recon/cases`, `exports`, `logs`, `databases`, or operational files into Obsidian.

## Expected Agent Behavior

- Start by reading existing docs and generated artifacts.
- Keep scanning and proposal steps read-only against user project directories.
- Write outputs to this repository unless the user explicitly approves a broader scope.
- When proposing Obsidian paths, always use `/home/cole/main_vault/10 Projects/<project-slug>`.
- Flag risky folders for manual review instead of guessing.
- Favor simple, inspectable formats and minimal dependencies.
- If a scanned path matches a known special-case constraint, preserve the exact override in generated proposals and reports.

## Implementation Preferences

- Python 3.13 compatible.
- Prefer `argparse`, `pathlib`, `json`, and standard library tools.
- If YAML support is needed, prefer a small safe writer unless a dependency is explicitly approved.
