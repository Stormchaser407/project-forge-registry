# Project Forge Dashboard UI

## Purpose

The dashboard UI renderer turns the Project Forge dashboard inventory feed into
a local static HTML command board.

Input:

- `artifacts/dashboard_inventory.json`

Output:

- `artifacts/dashboard.html`

No server is required in Phase 10.6A.

## Command

Run:

    PYTHONPATH=src python3 -m project_forge_registry.dashboard_ui

Console entrypoint after package install:

    project-forge-dashboard-ui

Optional paths:

    PYTHONPATH=src python3 -m project_forge_registry.dashboard_ui \
      --inventory-json artifacts/dashboard_inventory.json \
      --output-html artifacts/dashboard.html

## Visual Model

The page uses a Neon District command-board style:

- dark background
- neon cyan, green, amber, blue, red, and magenta accents
- project cards
- glowing three-light indicators
- local report links
- display-only project paths and VS Code targets

The HTML is self-contained. It does not use external CDNs, fonts, scripts,
images, or stylesheets.

## Lights

### Repo Light

- `green`: clean embedded repos or clean candidates
- `amber`: dirty repos or review-needed repo state
- `red`: protected, blocked, or unknown problem states
- `blue`: control repo or neutral system lane
- `gray`: missing or unknown light value

### Docs Light

- `green`: Project Forge marker or docs marker exists
- `amber`: README exists but Project Forge marker is missing
- `gray`: no README or Project Forge marker was detected

### Risk Light

- `green`: embedded-ready or low-risk clean state
- `amber`: attention or review needed
- `red`: protected or blocked state
- `blue`: control repo or neutral state
- `gray`: unknown or missing value

## Phase 10.6A Safety Model

The dashboard UI is static and read-only.

It does not:

- launch VS Code
- write files outside `artifacts/dashboard.html`
- apply changes
- write marker files
- modify external repos
- add or modify remotes
- push or fetch
- contact GitHub or Codeberg
- install packages
- run JavaScript actions that mutate files

Project paths, marker paths, and VS Code targets are shown as text only.

Allowed links are local report files beside `dashboard.html`:

- `dashboard_inventory_report.md`
- `repo_discovery_report.md`
- `embed_plan_report.md`
- `tool_readiness_report.md`
- `project_sync_report.md`

The renderer intentionally does not generate `file://`, `http://`, or
`https://` links.

## Next Phase

The next phase can add launch wrappers and dashboard actions safely.

Those actions should be implemented as explicit wrapper commands with the same
dry-run-first, report-first Project Forge policy. Phase 10.6A only proves the
static command-board surface.
