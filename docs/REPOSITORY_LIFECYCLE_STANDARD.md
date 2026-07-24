# Repository Lifecycle and Compliance Standard

**Version:** 1.0  
**Approved:** 2026-07-23 (America/New_York)  
**Owner:** Project Forge technical registry  
**Scope:** Repositories materially reviewed during C2 reconciliation, Project
Forge review, or agent-assisted project work.

## Policy

A repository that is materially reviewed must leave the reconciliation process
in one of two durable conditions:

1. **Compliant and assigned an explicit lifecycle status**, or
2. **Archived or superseded with preservation evidence.**

No reviewed repository should remain indefinitely in an ambiguous state such as
“probably active,” “interesting,” “old but maybe useful,” or merely unarchived.

This policy governs technical repository state. It does not make Project Forge
the owner of personal prioritization or the strategic roadmap of every project.

## Lifecycle States

| Status | Meaning |
|---|---|
| `active` | Receiving deliberate implementation or governance work now |
| `maintenance` | Working system requiring occasional care, not active expansion |
| `waiting` | Active outcome blocked by an external dependency or decision |
| `incubator` | Serious technical possibility, not yet committed to implementation |
| `dormant` | Preserved and resumable, but outside the current execution horizon |
| `reference` | Upstream fork, vendor code, research source, or retained example |
| `superseded` | Replaced by a named canonical repository or system |
| `completed` | Intended technical outcome delivered; retained for record or reuse |
| `archived` | Frozen and removed from active discovery and normal operational alerts |

## Minimum Structure for a Compliant Live Repository

A repository in `active`, `maintenance`, `waiting`, `incubator`, or `dormant`
state should expose the following canonical surfaces. Existing equivalent files
may satisfy the requirement; uniform filenames are preferred but not mandatory
when migration would cause unnecessary churn.

### Required

- `README.md`
  - purpose;
  - basic operator orientation;
  - links to canonical governance and status files.
- `PROJECT_CHARTER.md`
  - canonical mission;
  - scope and non-goals;
  - authority boundaries;
  - superseded mission or predecessor where relevant.
- `PROJECT_STATUS.md`
  - lifecycle status;
  - canonical repository and branch;
  - last governance verification;
  - current phase;
  - known blockers and next verification point.
- `AGENTS.md`
  - repository-specific safety and agent behavior;
  - instruction to read charter and status first;
  - preservation and write constraints.

### Required When Applicable

- architecture documentation;
- runbook, recovery, or cold-start instructions;
- decisions or ADR history;
- test/build verification instructions;
- deployment/runtime inventory;
- secrets and data-handling policy;
- mirror/remote policy;
- Obsidian or documentation-sync policy.

The structure may be compact for a small repository. Compliance is about clear
authority and recoverability, not manufacturing paperwork until the repo needs a
human resources department.

## Compliance Evidence

`PROJECT_STATUS.md` should include a checklist or equivalent record confirming:

- lifecycle state is explicit;
- canonical mission is explicit;
- canonical replacement or predecessor is named when relevant;
- current agent instructions are aligned;
- build/test/runtime evidence is recorded or marked unavailable;
- local and remote synchronization state is known;
- historical material is distinguished from current doctrine;
- remaining local-only verification work is explicit.

## Archive and Supersession Gate

A repository may be archived or marked superseded only after preserving:

```text
Canonical name:
Final lifecycle status:
Archive or supersession reason:
Date last verified:
Final branch and commit:
Canonical replacement:
Important assets preserved:
Build/test/runtime state:
Secrets excluded or removed:
Known recovery path:
What migrated:
What intentionally did not migrate:
Unresolved risks:
Resume conditions, if any:
Related repositories and documentation:
```

### GitHub Archive Procedure

When archiving is appropriate:

- place a prominent archive or supersession notice in `README.md`;
- name the canonical replacement, if one exists;
- preserve final status and recovery evidence;
- remove the repository from active Project Forge alerting;
- use GitHub's archive flag only after preservation is complete;
- do not delete the repository merely to reduce visual clutter.

### Reference Forks

Forks and vendor/reference repositories should be classified `reference` rather
than treated as active obligations. Record:

- upstream source;
- reason retained;
- whether local modifications exist;
- whether updates are expected;
- whether the fork can be archived without losing unique work.

## Reconciliation Workflow

For each repository discussed:

1. identify the canonical repository and any duplicates;
2. inspect recent commits, current-facing documentation, and known runtime state;
3. assign a lifecycle status;
4. decide **retrofit** or **archive/supersede**;
5. apply the minimum compliant structure or archive gate;
6. record local-only follow-up that cannot be completed through the connector;
7. verify the resulting GitHub state;
8. only then mark the repository reconciled.

## Project Forge Enforcement Boundary

Project Forge may:

- discover repositories;
- report compliance status;
- identify missing governance surfaces;
- classify technical lifecycle state;
- generate guarded retrofit proposals;
- exclude archived repositories from normal active alerts;
- preserve links to canonical replacements.

Project Forge may not infer personal priority from repository compliance. A
compliant active repository is technically alive; it is not automatically on the
user's immediate Todoist horizon.
