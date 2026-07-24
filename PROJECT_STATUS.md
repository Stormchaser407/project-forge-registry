# Project Forge Status

**Lifecycle:** Active  
**Operating mode:** Technical registry and guarded operator surface  
**Canonical repository:** `Stormchaser407/project-forge-registry`  
**Default branch:** `main`  
**Last governance verification:** 2026-07-23 (America/New_York)  
**GitHub compliance state:** Compliant — local synchronization pending  
**Canonical charter:** [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md)  
**Lifecycle standard:** [`docs/REPOSITORY_LIFECYCLE_STANDARD.md`](docs/REPOSITORY_LIFECYCLE_STANDARD.md)  
**Cerberus policy decision:** [`docs/decisions/2026-07-23-retire-cerberus-blanket-protection.md`](docs/decisions/2026-07-23-retire-cerberus-blanket-protection.md)

## Current Mission

Project Forge inventories and reports the condition of technical projects,
repositories, mirrors, deployment nodes, workspaces, launchers, and fleet
readiness. It supports dry-run-first and guarded technical workflows.

It does not own personal planning, weekly prioritization, calendars, or the full
roadmaps of other projects.

## Current Phase

The repository has a mature local registry, dashboard, launcher, workspace,
project-passport, Obsidian mirror, and guarded operator workflow history.

The current governance phase is **mission narrowing and lifecycle compliance**:

- preserve working technical capabilities;
- bind future agent work to the canonical charter;
- keep historical phase records intact;
- retire Project Forge as a universal planner or personal operating system;
- enforce the retrofit-or-archive gate for materially reviewed repositories;
- remove project-name-based Cerberus secrecy and protection;
- preserve ordinary evidence- and content-based safeguards;
- classify future scope additions against the charter before implementation.

## Cerberus Policy Migration

Project Forge no longer hides, blocks, or classifies a repository as protected
merely because its name, slug, or path contains `Cerberus`.

The migration updated:

- project scanning and discovery;
- stale discovery-category normalization;
- workspace generation;
- passport generation and legacy-record migration;
- Obsidian mirror and sync eligibility;
- export sync;
- remote policy;
- project-sync orchestration;
- embed planning;
- affected unit tests.

`cerberus_case_workspace` remains the current canonical Cerberus implementation
candidate. Older Cerberus-labeled repositories must be inspected and assigned an
explicit lifecycle state or archived/superseded under the repository lifecycle
standard.

Real credentials, keys, env files, databases, case data, raw evidence, exports,
and logs remain subject to ordinary content-based safeguards. Explicit passport
safety flags remain authoritative when set for a concrete reason.

## Verification

A temporary pull-request workflow applied the remaining large-module migration,
confirmed that active source files no longer contained the retired Cerberus name
vetoes, and ran the complete repository unit-test suite successfully. The
workflow and one-shot migration script were then removed from the branch; only
the verified product and test changes remain.

This verifies repository behavior on GitHub. It does not substitute for pulling
the commits and rebuilding Legion's local generated artifacts.

## Authoritative Surfaces

| Surface | Role |
|---|---|
| `README.md` | Current operator front door and links to canonical governance |
| `PROJECT_CHARTER.md` | Canonical mission and cross-system authority boundary |
| `PROJECT_STATUS.md` | Current lifecycle, phase, and compliance record |
| `AGENTS.md` | Required behavior for agents working in the repository |
| `docs/REPOSITORY_LIFECYCLE_STANDARD.md` | Compliance and archive gate for reviewed repositories |
| Cerberus policy decision | Evidence-based security and reconciliation rule |
| `docs/` | Architecture, phase history, runbooks, and decisions |
| verified repository/runtime evidence | Technical truth |
| generated `artifacts/` | Reports and derived operator surfaces; not higher authority than current governance |

## Superseded Doctrine

The following doctrines are retired:

- Project Forge as the universal planner or master personal command system;
- Project Forge as the single source of truth for every project;
- Cerberus-labeled repositories as an automatically secret or protected class;
- `protected_manual_review` when it exists only because a project name contains
  Cerberus.

The term **command center** may remain where it names a technical dashboard,
launcher, workspace, or operator surface. It does not imply authority over
Todoist, Google Calendar, the Sunday Outlook/C2 process, or another project's
roadmap.

Historical documents may retain the old doctrines as evidence of project
evolution. They are not current operational authority.

## Compliance Checklist

### GitHub governance and implementation retrofit

- [x] Current README is an operator front door rather than a phase-log dump.
- [x] Canonical mission and lifecycle status are explicit.
- [x] Superseded universal-planner doctrine is preserved and labeled.
- [x] Cross-system authority boundaries are explicit.
- [x] Repository lifecycle and archive standard is explicit.
- [x] Agent instructions enforce the charter and retrofit-or-archive rule.
- [x] Cerberus name-based protection is formally retired.
- [x] Scanner and discovery expose Cerberus repository state normally.
- [x] Legacy protected categories are normalized at active workflow boundaries.
- [x] Downstream workspace, mirror, export, remote, and sync gates no longer veto Cerberus names.
- [x] Ordinary content-based safeguards remain.
- [x] Full GitHub unit-test suite passed after migration.
- [x] Temporary migration workflow and script were removed.
- [x] Existing working capabilities and historical phase records remain available.
- [x] Current project mirror identifies the canonical charter, status, lifecycle standard, and Cerberus policy.
- [x] Project passport records the active lifecycle and canonical GitHub repository.

### Local synchronization and verification

- [ ] Local Legion checkout has pulled the governance and policy commits.
- [ ] Local full scan has regenerated discovery, passport, dashboard, and mirror artifacts.
- [ ] Real Obsidian Project Forge hub has been reviewed against the current charter and policy.
- [ ] Local tests and runtime commands have been rerun from Legion after synchronization.

The GitHub repository is compliant with the approved structure. The unchecked
items require access to Legion and are synchronization or runtime-verification
work, not unresolved architecture.

## Archive Gate

Project Forge is not an archive candidate while it remains the active technical
registry. If it is replaced later, archive only after recording:

- replacement system;
- final verified commit and runtime state;
- preserved reports and recovery instructions;
- migrated versus intentionally abandoned capabilities;
- Obsidian and launcher disposition;
- reason for retirement.
