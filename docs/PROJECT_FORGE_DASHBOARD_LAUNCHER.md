# Project Forge Dashboard Launcher

## Purpose

`scripts/project-forge-dashboard` is the safe local wrapper for the Project
Forge command board.

It refreshes the dashboard data, regenerates the static HTML, and optionally
opens the local dashboard with `xdg-open`.

## Commands

Default no-open mode:

    ./scripts/project-forge-dashboard

Explicit no-open mode:

    ./scripts/project-forge-dashboard --no-open

Open locally when `xdg-open` is available:

    ./scripts/project-forge-dashboard --open

Help:

    ./scripts/project-forge-dashboard --help

## What It Runs

The wrapper changes to the repository root, then runs:

    PYTHONPATH=src python3 -m project_forge_registry.dashboard_inventory
    PYTHONPATH=src python3 -m project_forge_registry.dashboard_ui

It prints the final dashboard path:

    artifacts/dashboard.html

## Open Behavior

`--no-open` is the default behavior.

With `--open`, the wrapper uses `xdg-open` only when it is already available on
the machine. If `xdg-open` is unavailable, the wrapper prints the dashboard path
and exits cleanly.

No VS Code launching occurs in this phase. Project paths and VS Code targets
remain display-only inside the dashboard.

## Safety Model

The wrapper is a local read-only dashboard refresh.

It does not:

- write files outside Project Forge artifacts
- write external repos
- apply changes
- write marker files
- add or modify remotes
- push or fetch
- install packages
- make network calls
- contact GitHub or Codeberg
- launch VS Code
- generate `file://` links inside the dashboard

## Outputs

- `artifacts/dashboard_inventory.json`
- `artifacts/dashboard_inventory_report.md`
- `artifacts/dashboard.html`

## Next Phase

Future phases can add launch wrappers and explicit dashboard actions. Those
actions should remain opt-in, wrapper-backed, and dry-run-first until separately
approved.
