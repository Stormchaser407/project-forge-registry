# Project Forge Obsidian Maintenance Policy

## Purpose

Phase 11E defines the Project Forge no-clobber doctrine for maintaining
Project Forge-managed Obsidian notes after the first approved real vault apply.

The core rule is simple: human-edited vault notes win by default.

Generated artifact notes are machine output. Vault notes are operator-facing
memory and may become human-edited after they are created. Project Forge must
not overwrite changed vault notes silently.

## Current Vault Root

```text
/mnt/storage/Cole/main_vault/10 Projects/Project Forge
```

## Managed Notes

- `Project Forge - Command Center.md`
- `Project Forge - Dashboard Summary.md`
- `Project Forge - Deferred Items.md`
- `Project Forge - Known Embedded Repos.md`
- `Project Forge - Phase 11 Planning.md`

## Maintenance Posture

The safe default is create-only plus skip identical plus block existing
different.

Allowed actions:

- create missing note, with the existing guarded apply requirements
- skip identical when a vault note already matches the generated artifact note
- block existing different when a vault note exists and differs from the
  generated artifact note

Prohibited actions:

- silent overwrite
- delete
- unguarded update
- apply without exact vault root confirmation

Deletes are out of scope and should remain unsupported.

## No-Clobber Doctrine

Project Forge must treat the real vault as operator memory, not as a disposable
build output directory.

- human-edited vault notes win by default
- generated artifact notes are machine output
- vault notes may contain operator edits that are not present in artifacts
- existing identical vault notes may be skipped safely
- existing different vault notes must be blocked by default
- no delete behavior should be added to normal maintenance
- create-only behavior remains the normal safe path
- future update behavior must not be implicit apply behavior

The current guarded apply command already matches this posture: it can create
missing files, skip identical files, and block existing different files. It does
not overwrite and does not delete.

## Future Update Requirements

Any future update mode, if ever added, must be a separate phase and a separate
command or flag path. It must not appear as an implicit extension of guarded
apply behavior.

Future update behavior requires all of the following:

- explicit operator approval
- backup before update
- diff/review report
- exact vault root confirmation
- all-or-nothing preflight

Future possible lanes:

- backup-before-update mode
- diff report
- manual merge workflow
- vault note provenance frontmatter
- protected human sections
- generated section markers
- snapshot before update

## Operator Rule

When in doubt, block existing different and report. The operator can then decide
whether to merge manually, refresh generated artifacts, or authorize a future
backup-before-update workflow in a separate phase.
