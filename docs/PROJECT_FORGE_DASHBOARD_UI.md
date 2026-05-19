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

## Phase 10.7E Copy Helper Display

Phase 10.7E keeps the launch area static and non-executing, but makes it
easier to copy the correct dry-run command from each eligible card.

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

These commands are rendered as text only in distinct monospace blocks. The
dashboard does not create buttons, launch handlers, executable anchors,
`file://` links, or `vscode://` links.

## Phase 10.7E Safety Model

The dashboard UI is static and read-only.

It does not:

- launch VS Code
- execute commands
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
Launch commands are also shown as text only.

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

The next phase can decide whether static copy helper polish is sufficient or
whether a non-JavaScript copy affordance is worth the added complexity. Any
future launch behavior should keep the same dry-run-first, explicit-opt-in
Project Forge policy.
