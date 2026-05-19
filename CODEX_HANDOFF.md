# Codex Handoff

## Mission

Preserve the Phase 10.7D dashboard launch-command display checkpoint for
`project-forge-registry`.

## Branch

`main`

## Current State

Phase 10.7D keeps dashboard launch behavior display-only.

Dashboard inventory now includes deterministic launch-display metadata:

- `launch_commands`
- `launch_policy`

The static dashboard renders that metadata as escaped text inside a
`Launch Commands` block on each project card.

## Implemented Behavior

Eligible categories render three copy-paste dry-run commands:

- `known_embedded`
- `clean_candidate`

Displayed command forms:

- `./scripts/project-forge-open-project --slug <slug> --profile personal --dry-run`
- `./scripts/project-forge-open-project --slug <slug> --profile business --dry-run`
- `./scripts/project-forge-open-project --slug <slug> --profile plain --dry-run`

Blocked or restricted categories render policy text instead:

- `dirty_candidate_review_first`
- `protected_manual_review`
- `control_repo`
- unsupported or unknown categories

The dashboard includes sections for:

- Known Embedded Projects
- Dirty Review Projects
- Protected Review Projects
- Candidate Review Projects
- Control Repo
- Blocked Other

## Safety

This phase remains display-only.

- No command execution from HTML
- No clickable launch buttons
- No JavaScript launch behavior
- No `file://` links
- No `vscode://` links
- No `--open` rendered in dashboard HTML
- No VS Code launch
- No external repo writes
- No remotes, push/fetch, package installs, network calls, commits, or tags

## Validation

Commands run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m project_forge_registry.dashboard_inventory
PYTHONPATH=src python3 -m project_forge_registry.dashboard_ui
./scripts/project-forge-dashboard --no-open
grep -n "project-forge-open-project" artifacts/dashboard.html | head -40
grep -n -- "--open\|vscode://\|file://\|<script" artifacts/dashboard.html || true
git status --short
```

Results:

- Unit tests passed: `Ran 228 tests in 1.064s`, `OK`.
- Inventory regenerated successfully.
- Dashboard HTML regenerated successfully at `artifacts/dashboard.html`.
- Grep confirmed displayed dry-run commands are present.
- Safety grep returned no matches for `--open`, `vscode://`, `file://`, or `<script`.

## Files Touched

- `src/project_forge_registry/dashboard_inventory.py`
- `src/project_forge_registry/dashboard_ui.py`
- `tests/test_dashboard_inventory.py`
- `tests/test_dashboard_ui.py`
- `docs/PROJECT_FORGE_DASHBOARD_UI.md`
- `docs/PROJECT_FORGE_OPEN_PROJECT.md`
- `artifacts/dashboard_inventory.json`
- `artifacts/dashboard.html`
- `README.md`
- `CODEX_HANDOFF.md`

## Working Tree

Latest observed `git status --short` before this handoff update:

```text
 M README.md
 M artifacts/dashboard.html
 M artifacts/dashboard_inventory.json
 M docs/PROJECT_FORGE_DASHBOARD_UI.md
 M docs/PROJECT_FORGE_OPEN_PROJECT.md
 M src/project_forge_registry/dashboard_inventory.py
 M src/project_forge_registry/dashboard_ui.py
 M tests/test_dashboard_inventory.py
 M tests/test_dashboard_ui.py
```

Re-run `git status --short` before committing to include this handoff file.

## Recommended Next Step

Review the static dashboard copy and decide whether the next phase should stay
display-only or add non-executing copy helpers. If this checkpoint is accepted,
the stable follow-up tag after commit would be:

`v0.10.7d-dashboard-launch-display`
