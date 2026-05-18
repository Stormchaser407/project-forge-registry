# Codex Handoff

## Mission

Preserve the Phase 10.7B Codex profile bootstrap checkpoint for `project-forge-registry`.

## Branch

`main`

## Current State

Phase 10.7B adds a safe local bootstrap script:

- `scripts/project-forge-codex-profile-bootstrap`

The bootstrap supports `--help`, `--dry-run`, and `--write`.

Dry-run mode prints planned profile homes and local config path without writing files.

Write mode creates only:

- `~/.codex-personal`
- `~/.codex-business`
- `config/codex_profiles.local.yml`

The local config is git-ignored.

## Boundaries

- No tokens are stored by the script.
- No tokens are read.
- No auth file contents are printed.
- No auth files are copied.
- No Codex login is attempted.
- No Codex command is executed.
- No VS Code launch is attempted.
- No external project repos are modified.
- No remotes, push/fetch, package installs, network calls, commits, or tags.
