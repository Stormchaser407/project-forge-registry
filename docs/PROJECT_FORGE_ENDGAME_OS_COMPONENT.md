# Project Forge as an Endgame OS Component

Date: 2026-08-16

Lifecycle: active

Canonical repository: `project-forge-registry`

## Decision

Project Forge remains an independent repository with its existing name and
charter. Within the Endgame architecture it is the registry/fleet/control-plane
component: it can discover and report technical repository, mirror, deployment
node, workspace, and readiness state, and it can expose guarded technical
operator workflows within its charter.

This component relationship does not merge Project Forge into the Endgame OS
repository and does not rename it. Endgame OS may consume a defined interface
from Project Forge later, but no such production integration is claimed by this
record.

## Ownership boundary

| Owner | Responsibility |
|---|---|
| Endgame OS | Operator-facing doctrine, control layer, and command grammar |
| Endgame Core | Installable machinery and capability resolution |
| Endgame Harness | Execution and review discipline |
| Project Forge | Technical registry, fleet, and control-plane evidence/workflows |
| Project Monolith | First Endgame Experience and workstation UX component |

Project Forge does not own:

- Todoist task truth or task mutation;
- calendars or fixed-time commitments;
- weekly planning, personal prioritization, or capacity allocation;
- another repository's internal roadmap, implementation truth, or release
  decision; or
- universal orchestration of the Endgame ecosystem.

Those exclusions preserve `PROJECT_CHARTER.md`; the Endgame component label is
not a scope expansion and does not revive the superseded universal-planner
mission.

## Intended interface direction

A future Endgame OS interface may read bounded Project Forge registry or fleet
evidence through an explicitly versioned, read-only contract. Before that can
be treated as an executable integration, a separate transaction must define:

- data ownership and versioning;
- freshness and provenance evidence;
- unavailable, ambiguous, malformed, and stale states;
- privacy and sensitive-data exclusion;
- review/authorization boundaries; and
- whether any guarded mutation belongs to Project Forge, Endgame Harness, or a
  separately owned provider.

Until then, generated dashboards and inventories remain Project Forge evidence
surfaces. They are not Endgame Core capability descriptors, provider
attestations, execution authorization, or permission to inspect/modify another
repository.

## Current evidence posture

The five generated artifacts reviewed on 2026-08-16 form a coherent snapshot:
their discovery rows, summary counts, dashboard JSON, report, and rendered HTML
agree on the changed classifications. The sources declare `dry-run` or
`read-only` modes. The snapshot records conditions at generation time and may
become stale as repositories change; it is not a live control-plane service.

## Non-goals of this transition

- no Project Forge rename;
- no charter expansion;
- no Todoist, calendar, vault, launcher, or other external-system mutation;
- no execution of dashboard copy commands;
- no claim that Endgame OS or this future integration is mature, shipped, or
  production-ready; and
- no archive, deletion, force push, or history rewrite.
