# CODEX HANDOFF

## Mission

Preserve the Phase 10.7A Codex workspace/profile selector probe checkpoint for
`project-forge-registry`.

## Branch

`main`

## Current State

Phase 10.7A adds a safe read-only Codex profile probe:

- `scripts/project-forge-codex-profile-probe`

The probe supports:

- `--help`
- `--profile personal`
- `--profile business`
- `--profile plain`
- `--interactive`

The phase also adds:

- `config/codex_profiles.example.yml`
- `docs/PROJECT_FORGE_CODEX_PROFILES.md`
- `.gitignore` entry for `config/codex_profiles.local.yml`

No local config file was created.

## Probe Results

`personal`:

- label: `Personal Codex workspace`
- proposed CODEX_HOME: `/home/cole/.codex-personal`
- CODEX_HOME exists: `no`
- likely auth file exists: `no`
- codex command available: `yes`

`business`:

- label: `Business Codex workspace`
- proposed CODEX_HOME: `/home/cole/.codex-business`
- CODEX_HOME exists: `no`
- likely auth file exists: `no`
- codex command available: `yes`

`plain`:

- label: `Plain editor / no Codex assumption`
- proposed CODEX_HOME: `none`
- CODEX_HOME exists: `not checked`
- likely auth file exists: `not checked`
- codex command available: `yes`

## Files Changed

- `.gitignore`
- `CODEX_HANDOFF.md`
- `README.md`
- `config/codex_profiles.example.yml`
- `docs/PROJECT_FORGE_CODEX_PROFILES.md`
- `scripts/project-forge-codex-profile-probe`
- `tests/test_codex_profile_probe.py`

## Commands Run

```bash
git status --short
git branch --show-current
git log -1 --oneline
git tag --points-at HEAD
git remote -v
bash -n scripts/project-forge-codex-profile-probe
PYTHONPATH=src python3 -m unittest tests.test_codex_profile_probe
./scripts/project-forge-codex-profile-probe --help
PYTHONPATH=src python3 -m unittest discover -s tests
./scripts/project-forge-codex-profile-probe --profile personal
./scripts/project-forge-codex-profile-probe --profile business
./scripts/project-forge-codex-profile-probe --profile plain
git status --short
```

## Verification

```text
Ran 202 tests in 0.291s

OK
```

## Boundaries Observed

- No tokens were read.
- No auth file contents were printed.
- No auth filenames were printed by the probe.
- No auth files were copied or modified.
- No Codex login was attempted.
- No Codex command was executed except `command -v codex`.
- No VS Code launch was attempted.
- No external project repos were modified.
- No apply path was run.
- No marker files were written.
- No push, fetch, remote inspection, or remote configuration was attempted.
- No GitHub or Codeberg contact was attempted.
- No package install was attempted.
- No network calls were made.
- No commit was made.
- No tags were created.
- No Cerberus handling was performed.

## Blockers

None for Phase 10.7A.

## Recommended Next Step

Review and commit the Phase 10.7A checkpoint.

Suggested commit message:

```text
Add Codex profile probe
```

Suggested tag after commit:

```text
v0.10.7a-codex-profile-probe
```
