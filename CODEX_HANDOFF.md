# Codex Handoff

## Mission

Preserve the Phase 10.7E dashboard copy-helper polish checkpoint for
`project-forge-registry`.

## Branch

`main`

## Current State

Phase 10.7E keeps the dashboard fully static and non-executing.

The launch area for eligible cards is now easier to copy from:

- heading: `Copy-Paste Launch Commands`
- safety note: `Dry-run only. Review output before manual open.`
- explicit context labels:
  - `Personal / CODEX_HOME ~/.codex-personal`
  - `Business / CODEX_HOME ~/.codex-business`
  - `Plain / no CODEX_HOME`
- one visually distinct monospace command block per profile

Blocked and restricted cards still render policy text only.

## Implemented Behavior

Eligible project categories:

- `known_embedded`
- `clean_candidate`

Blocked or restricted categories:

- `dirty_candidate_review_first`
- `protected_manual_review`
- `control_repo`
- unsupported or unknown categories

The dashboard remains display-only:

- no JavaScript
- no copy-to-clipboard code
- no executable buttons
- no command execution from HTML
- no `file://` links
- no `vscode://` links
- no `onclick`
- no `javascript:`
- no literal `--open` rendered in dashboard HTML

## Validation

Commands run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m project_forge_registry.dashboard_ui
./scripts/project-forge-dashboard --no-open
grep -n "Copy-Paste Launch Commands\|Personal /\|Business /\|Plain /\|Dry-run only" artifacts/dashboard.html | head -80
grep -n -- "--open\|vscode://\|file://\|<script\|onclick=\|javascript:" artifacts/dashboard.html || true
git status --short
```

Results:

- Unit tests passed: `Ran 231 tests in 0.802s`, `OK`.
- Dashboard HTML regenerated successfully at `artifacts/dashboard.html`.
- Grep confirmed copy-helper heading, labels, and dry-run note are present.
- Safety grep returned no matches for `--open`, `vscode://`, `file://`, `<script`, `onclick=`, or `javascript:`.

## Files Touched

- `src/project_forge_registry/dashboard_ui.py`
- `tests/test_dashboard_ui.py`
- `docs/PROJECT_FORGE_DASHBOARD_UI.md`
- `README.md`
- `artifacts/dashboard.html`
- `CODEX_HANDOFF.md`

Inventory code and `artifacts/dashboard_inventory.json` were not changed in this
phase.

## Working Tree

Latest observed `git status --short` before this handoff update:

```text
 M README.md
 M artifacts/dashboard.html
 M docs/PROJECT_FORGE_DASHBOARD_UI.md
 M src/project_forge_registry/dashboard_ui.py
 M tests/test_dashboard_ui.py
```

Re-run `git status --short` before committing to include this handoff file.

## Recommended Next Step

Review the improved copy-helper layout in `artifacts/dashboard.html`. If the
presentation feels right, the next stable follow-up tag after commit would be:

`v0.10.7e-dashboard-copy-helper-polish`
