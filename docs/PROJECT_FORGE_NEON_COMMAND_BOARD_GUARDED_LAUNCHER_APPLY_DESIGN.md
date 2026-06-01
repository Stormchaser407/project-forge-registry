# Project Forge Neon Command Board Guarded Launcher Apply Design

## Purpose

Phase 11H.3 defines the future guarded launcher replacement apply contract for
Project Forge command board launcher work.

This phase is design-only. Phase 11H.3 performs no apply, no replacement, no
mutation, no autostart changes, no systemd changes, no desktop entry changes,
no `--open`, no launch behavior, no vault writes, and no remote operations.

This document is a contract for later implementation phases only. It does not
create an apply command and does not authorize any launcher replacement.

## Current Baseline

- Current phase: Phase 11H.2A - Obsidian no-clobber conflict record.
- Current HEAD: `5516b89 Record Obsidian no-clobber conflict after Phase 11H.2`.
- Current version tag: `v0.11.0h2a-obsidian-no-clobber-conflict`.
- Current checkpoint: `checkpoint-20260526-175044-phase-11h2a-obsidian-no-clobber-conflict`.
- Remote state: remote-banked on GitHub and Codeberg before this phase.
- Working tree expectation: clean before Phase 11H.3 design work.
- Obsidian conflict: `Project Forge - Command Center.md` differs in the real
  vault. The conflict is recorded and must not be resolved or confused with
  launcher replacement work in this phase.

## Future Apply Scope

A later phase may consider guarded replacement only for exact operator-reviewed
target paths in these file classes:

- approved user-local desktop entries
- approved user-local autostart entries
- approved user-local systemd user units

Future scope requires exact target path review before any generated apply,
preflight, backup, diff, or rollback plan is accepted. No path class is
approved by category alone.

## Absolute Non-Goals

Phase 11H.3 explicitly forbids:

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
- no browser, file-handler, or VS Code launch
- no vault writes
- no Obsidian conflict resolution
- no remotes, push, fetch, mirror, or network contact
- no command that creates, edits, enables, disables, removes, starts, stops, or
  reloads user launchers or user services

## Future Approval Phrase

The proposed exact approval phrase for a future phase is:

```text
APPROVE 11H.4 GUARDED LAUNCHER REPLACEMENT APPLY
```

Phase 11H.3 must not accept this phrase and must not perform replacement. The
phrase is reserved for a later explicitly approved phase and has no operational
effect in Phase 11H.3.

## Future Preflight Requirements

A future guarded launcher replacement phase must use an all-or-nothing
preflight. It must refuse to proceed unless all of these conditions are true:

- clean git status
- expected HEAD, tag, and checkpoint confirmed
- discovery artifact present
- replacement review plan present
- exact target paths confirmed by the operator
- backup paths defined before update
- rollback instructions generated before update
- all-or-nothing preflight passes
- no blocked or ambiguous targets
- operator approval required through the exact future approval phrase

## Future Backup Policy

Future apply behavior must use backup before update for every target that would
be overwritten or edited.

Required backup policy:

- backup before overwrite or edit
- timestamped backups
- backup manifest generated before mutation
- checksum or hash of the original content recorded before mutation
- no deletion behavior
- rollback command text generated but not executed automatically

## Future Diff And Review Policy

Future apply behavior must show proposed changes before apply.

Required diff/review policy:

- proposed changes shown before apply
- old content versus new content summarized
- changed files list generated
- refusal if the diff cannot be shown
- refusal if the changed file list cannot be produced

## Future Apply Refusal Conditions

A future guarded launcher replacement phase must refuse apply when any of these
conditions are true:

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
- blocked or ambiguous target
- diff cannot be shown
- backup manifest cannot be generated

## Future Rollback Design

Future rollback must be designed before apply.

Required rollback design:

- restore from backups
- verify file hashes after restore
- report rollback result
- do not delete backups automatically
- preserve backup manifest as audit evidence

## Required Generated Future Artifacts

A later implementation phase should generate these future artifacts:

- launcher replacement apply preflight report
- backup manifest
- diff/review report
- apply result report
- rollback instructions

## Safety Contract

Phase 11H.3 is design-only. It contains no apply, no replacement, no mutation,
no autostart changes, no systemd changes, no desktop entry changes, no
`--open`, no launch behavior, and no vault writes.

Future work requires operator approval required, all-or-nothing preflight,
backup before update, and rollback required before any real launcher replacement
phase can be considered.

## Recommended Next Phase

Phase 11H.4 should implement guarded apply dry-run/preflight only, not real
apply. Real apply should remain a later explicit approval phase after the
operator reviews the dry-run/preflight output, exact target paths, backup
manifest, diff/review report, and rollback instructions.
