# Project Forge Status

**Lifecycle:** Active  
**Operating mode:** Technical registry and guarded operator surface  
**Canonical repository:** `Stormchaser407/project-forge-registry`  
**Default branch:** `main`  
**Last governance verification:** 2026-07-23 (America/New_York)  
**GitHub compliance state:** Compliant — local synchronization pending  
**Canonical charter:** [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md)  
**Lifecycle standard:** [`docs/REPOSITORY_LIFECYCLE_STANDARD.md`](docs/REPOSITORY_LIFECYCLE_STANDARD.md)

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
- remove or qualify current-facing claims that Project Forge is a universal
  planner or personal operating system;
- enforce the retrofit-or-archive gate for repositories materially reviewed;
- classify future scope additions against the charter before implementation.

## Authoritative Surfaces

| Surface | Role |
|---|---|
| `README.md` | Current operator front door and links to canonical governance |
| `PROJECT_CHARTER.md` | Canonical mission and cross-system authority boundary |
| `PROJECT_STATUS.md` | Current lifecycle, phase, and compliance record |
| `AGENTS.md` | Required behavior for agents working in the repository |
| `docs/REPOSITORY_LIFECYCLE_STANDARD.md` | Compliance and archive gate for reviewed repositories |
| `docs/` | Architecture, phase history, runbooks, and decisions |
| verified repository/runtime evidence | Technical truth |
| generated `artifacts/` | Reports and derived operator surfaces; not higher authority than the charter |

## Superseded Doctrine

The concept of Project Forge as the universal planner, master personal command
system, or single source of truth for all projects is retired.

The term **command center** may remain where it names a technical dashboard,
launcher, workspace, or operator surface. It does not imply authority over
Todoist, Google Calendar, the Sunday Outlook/C2 process, or another project's
roadmap.

## Compliance Checklist

### GitHub governance retrofit

- [x] Current README is an operator front door rather than a phase-log dump.
- [x] Canonical mission is explicit.
- [x] Lifecycle status is explicit.
- [x] Superseded mission is preserved and labeled.
- [x] Cross-system authority boundaries are explicit.
- [x] Repository lifecycle and archive standard is explicit.
- [x] Agent instructions enforce the charter and retrofit-or-archive rule.
- [x] Existing working capabilities are preserved.
- [x] Historical phase records remain available in docs, handoff, changelog, artifacts, and Git history.
- [x] Current project mirror identifies the canonical charter and status.
- [x] Project passport records the active lifecycle and canonical GitHub repository.
- [x] The historical command-center artifact is explicitly qualified as technical and non-planning authority.

### Local synchronization and verification

- [ ] Local Legion checkout has pulled the governance commits.
- [ ] Real Obsidian Project Forge hub has been reviewed against the charter after the local checkout is updated.
- [ ] Local tests and generated artifacts have been refreshed from Legion after the next working session.

The GitHub repository is compliant with the current structure. The unchecked
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
