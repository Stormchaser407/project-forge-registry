# Project Forge Registry

Project Forge is the safety-first operational registry for technical projects,
repositories, deployment nodes, mirrors, workspaces, launchers, and machine
readiness.

**Lifecycle:** Active  
**Mission:** Technical registry and guarded operator surface  
**Canonical branch:** `main`

## Start Here

- [Project Charter](PROJECT_CHARTER.md) — canonical mission, scope, and authority boundaries
- [Project Status](PROJECT_STATUS.md) — lifecycle, current phase, and compliance state
- [Agent Instructions](AGENTS.md) — required behavior for agents working in this repository
- [Repository Lifecycle Standard](docs/REPOSITORY_LIFECYCLE_STANDARD.md) — retrofit-or-archive gate for reviewed repositories
- [Cerberus Protection Reversal](docs/decisions/2026-07-23-retire-cerberus-blanket-protection.md) — project names are not security boundaries
- [Current Codex Handoff](CODEX_HANDOFF.md) — detailed implementation and phase context
- [Changelog](CHANGELOG.md) — historical implementation record

## Canonical Mission

Project Forge discovers, classifies, reports, and safely exposes technical state.
It can provide guarded commands and technical dashboards, but it does **not** own:

- personal or household planning;
- weekly prioritization or capacity planning;
- calendar commitments;
- the complete roadmaps of other projects;
- replacement of Todoist, Google Calendar, Sunday Outlook/C2, Obsidian, or an
  individual project's authoritative repository.

The earlier concept of Project Forge as a universal planner or personal operating
system is formally retired. Existing **command center** names refer only to local
technical operator surfaces.

## Authority Boundaries

| System | Authority |
|---|---|
| Project Forge | Technical project, repository, mirror, deployment-node, and fleet condition |
| Individual repositories and verified runtime state | Technical roadmap, implementation, and operational truth |
| Todoist | Immediate actionable commitments |
| Google Calendar | Fixed time commitments, travel, wake requirements, and protected sleep |
| Sunday Outlook / C2 Review | Cross-system prioritization and reconciliation |
| Obsidian | Durable context, decisions, learning, doctrine, and project knowledge |
| ChatGPT conversations | Intelligence and event history; not permanent project authority |

## Core Capabilities

Project Forge currently supports or preserves mature work for:

- project-root scanning and candidate discovery;
- technical lifecycle and safety classification;
- repository, dirty-tree, mirror, launcher, and workspace reporting;
- evidence-based handling for system-bound and reconciliation-required projects;
- VS Code workspace and launcher generation;
- project passport generation;
- controlled Obsidian technical mirrors;
- guarded review, commit-preflight, cold-start, and resume workflows;
- static local dashboards and command-copy operator surfaces;
- dry-run-first remote and synchronization policy checks;
- repository compliance assessment under the lifecycle standard.

Detailed phase history remains in `docs/`, `CODEX_HANDOFF.md`, generated
`artifacts/`, `CHANGELOG.md`, and Git history.

## Quick Start

From the repository root on Legion:

```bash
./scripts/project-forge-cold-start
```

Refresh known repository state and rebuild the dashboard:

```bash
./scripts/project-forge-scan-dashboard --no-open
```

Run a full project scan only when broad discovery is actually needed:

```bash
./scripts/project-scan
```

Build the static dashboard without opening it:

```bash
./scripts/project-forge-dashboard --no-open
```

Preview opening an eligible project:

```bash
./scripts/project-forge-open-project \
  --slug project_forge_registry \
  --profile plain \
  --dry-run
```

Run the test suite:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Safety Model

- Dry-run first.
- Review reports before apply.
- Do not mutate scanned project directories during discovery.
- Do not initialize Git in existing folders during discovery.
- Do not copy source code, credentials, databases, logs, raw evidence, exports, or case material into Obsidian.
- Do not push, mirror, create remotes, or change remote policy without explicit approval.
- Back up existing files before approved overwrite paths.
- Keep generated artifacts lower in authority than the charter, status, and verified repository/runtime evidence.
- Preserve exact overrides only when current evidence justifies them.

### Evidence-Based Safeguards

`system_bound_project` means a project is actually tied to NixOS, Home Manager,
systemd, launchers, services, mounted storage, or another live dependency. The
classification must be supported by current evidence rather than inferred from a
project name.

`reconciliation_required` means duplicate or overlapping project material has
actually been identified and needs comparison before mutation. It must not become
a permanent holding pen for projects nobody has looked at lately.

Cerberus is **not** a special hidden or protected class. Repositories containing
`Cerberus` in their name, slug, or path are scanned, displayed, classified, and
reconciled normally. `cerberus_case_workspace` is the current canonical
implementation candidate; older Cerberus repositories are expected to be
retrofitted, marked superseded/reference/dormant, or archived based on evidence.

Real credentials, databases, logs, exports, raw evidence, and case material still
receive the same ordinary content-based protection applied to every project.

## Repository Compliance Gate

Any repository materially reviewed through Project Forge or C2 reconciliation
must leave the process either:

1. compliant with an explicit lifecycle status and canonical governance files; or
2. archived/superseded with preservation and replacement evidence.

See [Repository Lifecycle and Compliance Standard](docs/REPOSITORY_LIFECYCLE_STANDARD.md).

Repository compliance does not imply immediate personal priority. A technically
active repository does not automatically enter Todoist or the current execution
horizon.

## Generated Artifacts

Common generated surfaces include:

- `artifacts/project_scan_report.md`
- `artifacts/project_scan_report.json`
- `artifacts/projects_proposed.yml`
- `artifacts/project_passports/`
- `artifacts/obsidian_mirrors/`
- `artifacts/dashboard_inventory.json`
- `artifacts/dashboard.html`
- `artifacts/neon_command_board.html`

Generated artifacts are evidence and operator aids. They do not override
`PROJECT_CHARTER.md`, `PROJECT_STATUS.md`, or verified live state.

Older generated artifacts may still contain retired Cerberus protection labels
until Legion performs a fresh scan and artifact rebuild. Current code and policy
must normalize or replace those labels rather than treating them as authority.

## Obsidian Boundary

Canonical technical mirrors use:

```text
/mnt/storage/Cole/main_vault/10 Projects/<project-folder>/
```

The safe default is markdown-only, docs-only, dry-run-first, no-delete, and
no-clobber. Human-edited vault notes win by default. Any future update mode must
require explicit approval, backup, diff review, exact vault-root confirmation,
and all-or-nothing preflight.

## Local Synchronization Note

The GitHub repository contains the approved 2026-07-23 governance retrofit and
Cerberus protection reversal. Legion's local checkout and the real Obsidian
Project Forge hub still require a normal pull, fresh scan, test run, and artifact
rebuild before those local surfaces can be considered synchronized.

Do not treat that local sync requirement as unresolved architecture; the
canonical GitHub policy is already established.

## Historical Documentation

The previous README grew into a long phase-by-phase implementation log. That
history remains available through:

- `docs/`
- `CODEX_HANDOFF.md`
- `CHANGELOG.md`
- generated `artifacts/`
- Git history before the 2026-07-23 README retrofit

Historical SITREPs and archaeology reports may describe the retired Cerberus
blanket-protection model. They are evidence of project evolution, not current
operator doctrine.

Use the current README as the operator front door and the historical documents
for deep implementation archaeology.
