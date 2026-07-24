# Decision: Retire Cerberus Blanket Protection

**Date:** 2026-07-23 (America/New_York)  
**Status:** Approved  
**Decision owner:** Cash

## Context

Early Project Forge phases treated paths and repositories containing the word
`Cerberus` as a special protected class. That policy hid or blocked ordinary Git
status, workspace, passport, mirror, launch, remote-policy, and synchronization
workflows based primarily on the project name.

The original assumption no longer matches the operating environment:

- Cash is the sole normal operator of the machines;
- the repositories are personal technical projects rather than enterprise or
  national-security systems;
- the canonical surviving implementation is expected to be Cerberus Case
  Workspace, while most older Cerberus-labeled repositories will likely be
  superseded or archived;
- Project Forge now has a repository lifecycle standard specifically intended to
  expose, classify, retrofit, or archive ambiguous repositories.

A project name is not a security boundary. Blanket protection now prevents the
very reconciliation Project Forge is supposed to support.

## Decision

Project Forge must not hide, suppress, block, or classify a repository as
protected merely because its slug, folder, path, or repository name contains
`Cerberus`.

Cerberus-labeled repositories receive the same discovery, status reporting,
lifecycle classification, retrofit, and archive treatment as other personal
repositories.

## What Remains Protected

Ordinary evidence- and content-based safeguards remain in force for every
project, including Cerberus Case Workspace:

- `.env`, credential, token, key, and certificate paths require review;
- databases, logs, exports, raw evidence, case data, and personally sensitive
  material must not be copied into public documentation or Obsidian mirrors by
  default;
- destructive deletion, force-push, and unreviewed bulk mutation remain blocked;
- explicit passport flags such as `do_not_sync=true` remain authoritative when
  intentionally set for a concrete reason;
- public/private repository decisions remain deliberate rather than inferred.

These safeguards are based on actual data and requested operations, not the word
`Cerberus`.

## Legacy Migration

New scans and discovery runs must not emit:

- `cerberus_special_case_candidate`;
- `protected_manual_review` solely due to a Cerberus name;
- automatic Cerberus `do_not_sync` or bulk-sync exclusions;
- Cerberus-specific high-level-note-only policies.

Until Legion regenerates local artifacts, current code should normalize legacy
`protected_manual_review` categories and remove retired Cerberus-name warnings
where practical.

Historical archaeology reports, SITREPs, and phase records may retain the old
policy as history. They must not be treated as current doctrine.

## Canonical Cerberus Direction

`cerberus_case_workspace` is the current canonical implementation candidate.
Older Cerberus-labeled repositories are not presumed secret or active. Each must
be inspected and leave reconciliation as one of:

- retrofitted and assigned an explicit lifecycle state;
- marked `reference` or `dormant` with a reason;
- marked `superseded` by the canonical implementation; or
- archived after preservation and lineage review.

## Consequences

- Project Forge can display the real status of all Cerberus-labeled repositories.
- Repository names no longer create hidden lanes or artificial red status.
- Reconciliation can proceed repo by repo under the lifecycle standard.
- Real case data and secrets continue to receive ordinary content-based
  protection.
- Enterprise-grade controls may be added later when a concrete threat model,
  team, customer, or compliance requirement justifies them.
