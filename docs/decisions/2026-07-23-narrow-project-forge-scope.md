# Decision: Narrow Project Forge to Technical Registry Authority

**Date:** 2026-07-23 (America/New_York)  
**Status:** Approved  
**Decision owner:** Cash  
**Canonical policy:** `PROJECT_CHARTER.md`

## Context

Project Forge accumulated language and ambitions suggesting that it might become
a universal command center for personal activity, project planning, calendars,
roadmaps, and technical operations.

That model created overlapping authority with Todoist, Google Calendar, the
Sunday Outlook/C2 process, individual repositories, and Obsidian. It also made
technical discovery and readiness reporting appear responsible for decisions it
could not reliably own.

## Decision

Project Forge remains active, but its mission is narrowed to the operational
registry for technical projects, repositories, deployment nodes, mirrors,
workspaces, launchers, and machine readiness.

It may provide technical dashboards and guarded operator command surfaces. It
does not own personal planning, weekly prioritization, calendars, or the complete
roadmaps of other projects.

## Authority Division

- Project Forge: technical project and fleet condition.
- Individual repositories and verified runtime state: technical truth.
- Todoist: immediate actionable commitments.
- Google Calendar: fixed time commitments.
- Sunday Outlook/C2: cross-system prioritization and reconciliation.
- Obsidian: durable context, decisions, learning, and doctrine.
- ChatGPT conversations: intelligence and event history.

## Consequences

### Retained

- project discovery and classification;
- repository and dirty-state reporting;
- launcher and workspace generation;
- project passports;
- technical dashboards;
- guarded review and resume commands;
- controlled Obsidian technical mirrors;
- fleet and deployment-node readiness reporting.

### Retired

- Project Forge as master life planner;
- Project Forge as universal roadmap owner;
- Project Forge as replacement for Todoist or Calendar;
- Project Forge as the sole command surface for all personal and professional
  activity.

### Naming

Existing “command center” names may remain when they refer to technical operator
surfaces. Their meaning is constrained by `PROJECT_CHARTER.md`.

## Reversal Rule

This decision may be changed only through a new explicit architecture decision
that identifies a concrete failure in the current authority model and defines
the smallest justified change. Convenience alone is insufficient.
