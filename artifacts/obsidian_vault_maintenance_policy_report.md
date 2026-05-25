# Project Forge Obsidian Vault Maintenance Policy Report

## Phase

Phase 11E - Obsidian vault maintenance policy / no-clobber doctrine.

## Current Vault Root

```text
/mnt/storage/Cole/main_vault/10 Projects/Project Forge
```

## Managed Note List

- `Project Forge - Command Center.md`
- `Project Forge - Dashboard Summary.md`
- `Project Forge - Deferred Items.md`
- `Project Forge - Known Embedded Repos.md`
- `Project Forge - Phase 11 Planning.md`

## Current Maintenance Posture

human-edited vault notes win by default.

Generated artifact notes are machine output. Vault notes are operator-facing
memory and may become human-edited. The safe Project Forge posture is
no-clobber: create-only, skip identical, and block existing different.

## Allowed Actions

- create missing note, with guards
- skip identical
- block existing different

## Prohibited Actions

- silent overwrite
- delete
- unguarded update
- apply without exact vault root confirmation

The policy remains no delete for normal maintenance. Deletes are out of scope
and should remain unsupported.

## Future Possible Lanes

- backup-before-update mode
- backup before update
- diff report
- diff/review report
- manual merge workflow
- vault note provenance frontmatter
- protected human sections
- generated section markers
- snapshot before update

Any future update behavior must be a separate phase and separate command/flag
path, not implicit apply behavior. It must require explicit operator approval,
backup before update, a diff/review report, exact vault root confirmation, and
all-or-nothing preflight.

## Safety

This report is repo-local documentation only. It does not write to the real
vault, run apply, modify external repos, write markers, use remotes, push/fetch,
install packages, make network calls, launch VS Code, or handle Codex auth.
