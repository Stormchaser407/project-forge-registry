# SITREP 2026-05-06 Housekeeping

This document is a formal constraint record for housekeeping, registry planning, and future automation.

## Classification Rules

### `system_bound_project`

- Active or important project.
- May live outside `/mnt/storage/Cole/Projects` intentionally.
- May be referenced by NixOS, Home Manager, systemd, launchers, services, or scripts.
- Must not be moved automatically.
- Must not be bulk-registered into normal sync automation.
- Registry action should default to `document_only_for_now`.

### `reconciliation_required`

- Duplicate, old copy, or partially overlapping folder.
- May contain storage-only operational material.
- Must not be deleted automatically.
- Must not be merged automatically.
- Registry action should default to `compare_only`.

## Specific Cerberus Handling

### `/home/cole/cerberus`

- classification: `system_bound_project`
- status: `active_special_case`
- canonical_path: `/home/cole/cerberus`
- do_not_move: `true`
- registry_action: `document_only_for_now`

### `/mnt/storage/Cole/cerberus`

- classification: `reconciliation_required`
- status: `old_copy_with_possible_operational_material`
- do_not_delete: `true`
- registry_action: `compare_only`

## Additional Safety Constraints

- Do not move Cerberus.
- Do not delete the storage copy.
- Do not create GitHub or Codeberg sync automation for Cerberus.
- Do not copy `recon/raw`, `recon/cases`, `exports`, `logs`, `databases`, or operational files into Obsidian.
- For Obsidian, Cerberus should only receive high-level notes:
- `project home`
- `workspace map`
- `runbook index`
- `reconciliation note`
