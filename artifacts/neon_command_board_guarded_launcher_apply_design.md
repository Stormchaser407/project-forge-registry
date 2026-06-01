# Neon Command Board Guarded Launcher Apply Design

## Phase

Phase 11H.3 - design-only guarded launcher replacement apply contract.

## Purpose

Define the future guarded launcher replacement apply contract for a later
Project Forge launcher phase.

Phase 11H.3 is design-only. It performs no apply, no replacement, no mutation,
no autostart changes, no systemd changes, no desktop entry changes, no
`--open`, no launch behavior, no vault writes, and no remotes.

## Current Baseline

- Baseline phase: Phase 11H.2A - Obsidian no-clobber conflict record.
- HEAD: `5516b89 Record Obsidian no-clobber conflict after Phase 11H.2`.
- Version tag: `v0.11.0h2a-obsidian-no-clobber-conflict`.
- Checkpoint: `checkpoint-20260526-175044-phase-11h2a-obsidian-no-clobber-conflict`.
- Remote state: remote-banked on GitHub and Codeberg before this design phase.
- Obsidian no-clobber conflict: recorded, not resolved, and not part of
  launcher replacement work.

## Future Apply Scope

A future phase may touch only exact operator-approved targets in these classes:

- approved user-local desktop entries
- approved user-local autostart entries
- approved user-local systemd user units

Exact target path review is required first. Category-level approval is not
enough.

## Absolute Non-Goals

- no apply
- no replacement
- no mutation
- no launcher replacement
- no autostart changes
- no autostart mutation
- no systemd changes
- no systemd mutation
- no desktop entry changes
- no desktop entry mutation
- no `--open`
- no launch behavior
- no vault writes
- no Obsidian conflict resolution
- no remotes

## Future Approval Phrase

Reserved exact phrase for a future phase:

```text
APPROVE 11H.4 GUARDED LAUNCHER REPLACEMENT APPLY
```

Phase 11H.3 must not accept this phrase and must not perform replacement.

## Future Preflight Requirements

- clean git status
- expected HEAD, tag, and checkpoint confirmed
- discovery artifact present
- replacement review plan present
- exact target paths confirmed
- backup paths defined
- rollback instructions generated
- all-or-nothing preflight
- no blocked or ambiguous targets
- operator approval required through the exact future approval phrase

## Future Backup Policy

- backup before overwrite or edit
- backup before update
- timestamped backups
- backup manifest
- checksum or hash of original content
- no deletion behavior
- rollback command text generated but not executed

## Future Diff And Review Policy

- proposed changes shown before apply
- old content versus new content summarized
- changed files list
- refusal if diff cannot be shown

## Future Apply Refusal Conditions

- dirty repo
- missing approved target
- target path outside approved user-local directories
- symlink ambiguity
- unreadable target
- missing backup path
- missing rollback plan
- missing exact approval phrase
- generated plan older than latest discovery
- Obsidian conflict confused with launcher work
- any request to run `--open` or launch UI as part of apply

## Future Rollback Design

- restore from backups
- verify file hashes
- report rollback result
- do not delete backups automatically

## Required Generated Future Artifacts

- launcher replacement apply preflight report
- backup manifest
- diff/review report
- apply result report
- rollback instructions

## Recommended Next Phase

Phase 11H.4 should implement guarded apply dry-run/preflight only, not real
apply. Real apply should remain a later explicit approval phase.

## Safety

This artifact is design-only. It documents no apply, no replacement, no
mutation, no autostart changes, no systemd changes, no desktop entry changes,
no `--open`, no launch behavior, and no vault writes.

Future work requires operator approval required, all-or-nothing preflight,
backup before update, and rollback required.
