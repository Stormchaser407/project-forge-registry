# Project Forge Charter

**Status:** Active — narrowed scope  
**Approved:** 2026-07-23 (America/New_York)  
**Authority:** This document is the canonical mission and scope boundary for Project Forge.

## Canonical Mission

Project Forge is the operational registry for technical projects, repositories,
deployment nodes, mirrors, and machine readiness.

It discovers, classifies, reports, and safely exposes technical state. It may
provide guarded operator commands and technical dashboards, but it does not own
personal planning, weekly prioritization, calendars, or the complete roadmap for
all projects.

Project Forge may emit evidence-backed technical follow-up signals. The operator
or Master Scheduler decides whether a signal becomes work; Todoist owns any
resulting actionable commitment.

## What Project Forge Owns

- Technical project and repository discovery.
- Local path, Git state, mirror, launcher, workspace, and readiness reporting.
- Safety classifications and protected-project handling.
- Guarded technical command surfaces and dry-run-first operational workflows.
- Read-only or controlled documentation mirrors for technical project state.
- Evidence about whether a technical project can be safely resumed, reviewed,
  synchronized, deployed, or maintained.

## What Project Forge Does Not Own

- Personal or household planning.
- Weekly prioritization and capacity planning.
- Calendar commitments, travel, wake requirements, or protected sleep.
- The complete roadmap for every project.
- Career, legal, financial, health, or administrative commitments.
- Replacement of Todoist, Google Calendar, the Sunday Outlook/C2 process, or an
  individual project's authoritative repository.

## Cross-System Authority Map

| System | Authority |
|---|---|
| Project Forge | Technical project, repository, mirror, deployment-node, and fleet condition |
| Individual repositories and verified runtime state | Technical roadmap, implementation, and operational truth |
| Todoist | Actionable-work truth and execution commitments |
| Google Calendar | Fixed time commitments, travel, wake requirements, and protected sleep |
| Master Scheduler (including Sunday Outlook / C2 review) | Cross-system governance, planning, prioritization, and reconciliation |
| Obsidian | Durable context, decisions, learning, doctrine, and human-readable project knowledge |
| ChatGPT conversations | Intelligence, analysis, and event history; not permanent project authority |

## Follow-Up Signal Boundary

Project Forge detects and reports a technical follow-up signal. Master Scheduler
or the operator decides whether it becomes actionable. Todoist owns the
resulting actionable commitment.

Signals are evidence records, not tasks. Project Forge does not assign personal
priority, due dates, or commitments and does not silently export to Todoist.

## Superseded Mission

The earlier concept of Project Forge as a universal command center, master
planner, personal operating system, or single screen for nearly all personal
and project activity is formally retired.

Historical documents may retain that language as evidence of the project's
evolution. Current-facing documentation, dashboards, agent instructions, and
future implementation work must not present that superseded mission as active.

## Interpretation of “Command Center”

The term **command center** may remain in launcher, workspace, dashboard, or note
names when it refers to a local technical operator surface. It does not grant
Project Forge authority over personal planning, calendars, Todoist, or the full
roadmaps of other projects.

## Scope-Change Rule

Any future expansion beyond this charter requires an explicit architectural
decision that:

1. identifies the concrete failure in the current division of authority;
2. explains why an existing authoritative system cannot solve it;
3. defines the smallest justified expansion;
4. records the decision in this charter or a linked decision record; and
5. avoids silently turning Project Forge back into a universal planner.

Convenience alone is not sufficient justification for scope expansion.

## Preservation Rule

Narrowing the mission does not require deleting working capabilities. Existing
technical discovery, dashboards, launchers, mirrors, reports, and guarded
operator workflows should be retained when they serve the canonical mission.
