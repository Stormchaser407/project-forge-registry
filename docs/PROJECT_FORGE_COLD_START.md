# Project Forge Cold Start

## Purpose

`scripts/project-forge-cold-start` is the operator resume script for Project
Forge.

It runs the standard status and safety checks without requiring the operator to
remember the command sequence.

## Command

Default read-only no-open mode:

    ./scripts/project-forge-cold-start

Open the dashboard after refresh when `xdg-open` is available:

    ./scripts/project-forge-cold-start --open-dashboard

Help:

    ./scripts/project-forge-cold-start --help

## What It Does

The script changes to the Project Forge repo root, then runs:

1. `git status --short`
2. recent commits
3. recent `v0.10*` tags
4. recent `checkpoint-*` tags
5. `PYTHONPATH=src python3 -m unittest discover -s tests`
6. `./scripts/project-sync-safe`
7. `./scripts/project-forge-dashboard --no-open`
8. dashboard path printout
9. final `git status --short`

When `--open-dashboard` is passed, step 7 uses:

    ./scripts/project-forge-dashboard --open

## Dashboard Path

The dashboard is regenerated at:

    artifacts/dashboard.html

## Safety Model

Cold Start is a status/resume/check script.

The default is no-open and read-only against external repos.

It does not create commits and does not create tags.

It does not:

- write external repos
- apply changes
- write marker files
- add or modify remotes
- push or fetch
- install packages
- make network calls
- launch VS Code
- run the checkpoint/tag script
- create a desktop launcher

## Relationship To Other Wrappers

Cold Start calls:

- `scripts/project-sync-safe`
- `scripts/project-forge-dashboard`

It does not replace `scripts/project-forge-checkpoint`. The checkpoint script is
for deliberate checkpoint/tag creation after a known-good clean state. Cold
Start is only for resuming work and proving the current local state.

## Operator Notes

Use Cold Start at the beginning of a Project Forge session when you want the
current repo status, tests, safe sync report, and refreshed dashboard in one
place.

Use `--open-dashboard` only when opening a local browser/file handler is safe in
the current environment.
