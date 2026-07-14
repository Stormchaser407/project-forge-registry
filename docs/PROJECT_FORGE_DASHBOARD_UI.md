# Project Forge Dashboard UI

## Purpose

The dashboard UI renderer turns the Project Forge dashboard inventory feed into
a local HTML command board.

Input:

- `artifacts/dashboard_inventory.json`

Live discovery paths are authoritative for repository and marker locations.
Legacy embed-plan decisions are retained only when their rebased marker target
still matches the currently discovered repository; stale `/mnt/storage` marker
links are never rendered into the dashboard.

Output:

- `artifacts/dashboard.html`

No server is required.

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
- sticky local controls
- embedded term guide
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

## Local Interaction

The generated dashboard includes local-only interaction:

- search by project, action, category, or path
- filter by project lane
- click summary counters to filter by lane
- sort cards by lane order, project name, risk light, or docs light
- collapse and expand project sections
- collapse and expand individual project cards
- click dotted dashboard terms to show embedded explanations
- expand the full dashboard term glossary
- copy a scan-and-rebuild command after project commits
- copy review/status/diff/log/commit-preflight command shortcuts for dirty amber repos
- copy eligible dry-run launch commands to the clipboard

These controls run inside the generated HTML. They do not execute commands,
launch URLs, write files, or contact the network.

## Embedded Term Guide

The dashboard embeds explanations for common Project Forge terms, including:

- repo, docs, and risk lights
- dry-run
- CODEX_HOME
- VS Code target
- marker YAML and marker doc
- embedded, candidate, dirty, protected, control, and blocked lanes

Term explanations are rendered in the HTML itself and mirrored into the local
JavaScript state so clicking a dotted term can focus the guide panel without a
network request.

## Copy Helper Display

The launch area remains non-executing, but it makes the correct dry-run command
easy to copy from each eligible card.

Eligible project categories show a `Copy-Paste Launch Commands` block with:

- `Personal / CODEX_HOME ~/.codex-personal`
- `Business / CODEX_HOME ~/.codex-business`
- `Plain / no CODEX_HOME`

The block also shows a short safety note:

- `Dry-run only. Review output before manual open.`

The displayed commands follow this pattern:

```bash
./scripts/project-forge-open-project --slug <slug> --profile personal --dry-run
./scripts/project-forge-open-project --slug <slug> --profile business --dry-run
./scripts/project-forge-open-project --slug <slug> --profile plain --dry-run
```

Blocked project categories show a policy message instead of commands.

- `dirty_candidate_review_first`: blocked display
- `protected_manual_review`: blocked display
- `control_repo`: restricted dry-run note only
- unknown or unsupported categories: blocked display

These commands are rendered in distinct monospace blocks with clipboard copy
buttons. The dashboard does not create launch handlers, executable anchors,
`file://` links, or `vscode://` links.

## Dirty Review Commands

Dirty amber repos render a `Review Commands` panel with copy buttons for:

- git status summary
- changed-file diff summary
- recent commits
- commit preflight
- guarded commit command template

The dashboard copies command text only. The guarded commit command must be
reviewed and run in a terminal. It requires explicit confirmation flags and an
edited commit message.

See:

```text
docs/PROJECT_FORGE_PROJECT_REVIEW.md
```

## Scan Button

The dashboard renders a top-level `Scan Button` operator panel with commands
for:

- scan + rebuild without opening the dashboard
- refresh dashboard HTML from the current discovery inventory only

Use `Scan + Rebuild` after committing a dirty amber repo. It runs repo
discovery first, then rebuilds the dashboard inventory and HTML so stale dirty
counts can clear.

The dashboard copies command text only. Static local HTML cannot safely execute
shell commands directly.

See:

```text
docs/PROJECT_FORGE_DASHBOARD_SCAN.md
```

## Safety Model

The dashboard UI is local-only and read-only against project files.

It does not:

- launch VS Code
- execute project commands
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
Launch commands are shown as text and may be copied to the clipboard.

The renderer intentionally does not place the literal `--open` flag in
dashboard HTML, even in helper text, so the display stays aligned with the
non-executing validation boundary for this phase.

Allowed links are local report files beside `dashboard.html`:

- `dashboard_inventory_report.md`
- `repo_discovery_report.md`
- `embed_plan_report.md`
- `tool_readiness_report.md`
- `project_sync_report.md`

The renderer intentionally does not generate `file://`, `http://`, or
`https://` links.

## Next Phase

Future launch behavior should keep the same dry-run-first, explicit-opt-in
Project Forge policy.
