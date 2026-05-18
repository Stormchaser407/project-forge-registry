# Project Forge Codex Profile Bootstrap

## Purpose

The Codex profile bootstrap prepares local profile homes for the operator one-account, multiple-workspace model.

The operator uses one ChatGPT account, but may choose between Personal and Business context after login.

This phase does not automate authentication.

## Commands

Dry-run:

    ./scripts/project-forge-codex-profile-bootstrap --dry-run

Write local profile homes and ignored local config:

    ./scripts/project-forge-codex-profile-bootstrap --write

## Files and Directories

Write mode creates:

    ~/.codex-personal
    ~/.codex-business
    config/codex_profiles.local.yml

The local config file is git-ignored.

## Safety

The bootstrap does not:

- store tokens
- read tokens
- print auth file contents
- copy auth files
- run Codex login
- execute Codex
- launch VS Code
- touch remotes
- push/fetch
- install packages
- make network calls
- create commits
- create tags

## Operator Rule

Do not copy auth files between Personal and Business profiles unless that becomes a separate reviewed plan.

This phase only creates safe parking spaces for later profile-aware launch behavior.
