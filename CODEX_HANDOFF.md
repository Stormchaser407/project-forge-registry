# CODEX HANDOFF

## Mission

Preserve the Phase 10.8A Project Forge Cold Start checkpoint for
`project-forge-registry`.

## Branch

`main`

## Current State

Phase 10.8A adds a safe repo-local Cold Start wrapper:

- `scripts/project-forge-cold-start`

The wrapper is a status/resume/check script. It:

- changes to the Project Forge repo root
- prints `PROJECT FORGE COLD START`
- shows `git status --short`
- shows recent commits
- shows recent `v0.10*` tags
- shows recent `checkpoint-*` tags
- runs `PYTHONPATH=src python3 -m unittest discover -s tests`
- runs `./scripts/project-sync-safe`
- runs `./scripts/project-forge-dashboard --no-open` by default
- prints `artifacts/dashboard.html`
- prints final `git status --short`
- supports `--help`
- supports `--open-dashboard`

Validation did not run `--open-dashboard`.

Current Cold Start output summary:

- tests: `Ran 184 tests ... OK`
- project-sync final status: `ready_for_operator_review`
- dashboard projects: `74`
- known embedded: `4`
- dirty review: `3`
- protected review: `12`
- candidate review: `54`
- dashboard HTML: `artifacts/dashboard.html`

## Files Changed

- `CODEX_HANDOFF.md`
- `README.md`
- `docs/PROJECT_FORGE_COLD_START.md`
- `scripts/project-forge-cold-start`
- `tests/test_cold_start.py`

## Commands Run

```bash
git status --short
git branch --show-current
git log -1 --oneline
git tag --points-at HEAD
git remote -v
bash -n scripts/project-forge-cold-start
PYTHONPATH=src python3 -m unittest tests.test_cold_start
./scripts/project-forge-cold-start --help
PYTHONPATH=src python3 -m unittest discover -s tests
./scripts/project-forge-cold-start
git status --short
```

## Verification

```text
Ran 184 tests in 0.266s

OK
```

Cold Start itself also ran tests:

```text
Ran 184 tests in 0.424s

OK
```

`./scripts/project-forge-cold-start` completed successfully in default no-open
mode.

## Boundaries Observed

- No external project repos were modified.
- No apply path was run.
- No marker files were written.
- No push, fetch, remote inspection, or remote configuration was attempted.
- No GitHub or Codeberg contact was attempted.
- No package install was attempted.
- No network calls were made.
- No VS Code launch was attempted.
- `--open-dashboard` was not run.
- No commit was made.
- No tags were created.
- No Cerberus handling was performed.

Note: `project-sync-safe`, which Cold Start is required to call, wrote its
standard wrapper log under `/tmp/`.

## Blockers

None for Phase 10.8A.

## Recommended Next Step

Review and commit the Phase 10.8A checkpoint.

Suggested commit message:

```text
Add Project Forge Cold Start wrapper
```

Suggested tag after commit:

```text
v0.10.8a-cold-start
```
