# Project Forge Repo Discovery

## Purpose

Repo discovery is the authorized, dry-run inventory phase for finding local Git repositories.

It is meant for the very real operator problem:

> I forgot where I stored all my repos on this computer.

## Command

Run with explicit scan roots:

    PYTHONPATH=src python3 -m project_forge_registry.repo_discovery --scan-root /mnt/storage/Cole/Projects

Reports are written to:

    artifacts/repo_discovery_report.md
    artifacts/repo_discovery_inventory.csv

## Safety

Repo discovery is read-only.

It does not:

- write to discovered repos
- index file contents
- scan secrets
- add or modify remotes
- push or fetch
- install packages
- contact GitHub or Codeberg

## What It Detects

For each discovered `.git` repository:

- slug
- path
- git status: clean, dirty, or unknown
- README presence
- AGENTS.md presence
- .code-workspace presence
- Project Forge marker presence
- remote count
- category

## Categories

- control_repo
- known_embedded
- clean_candidate
- dirty_candidate_review_first
- unknown_structure

Legacy `protected_manual_review` rows are normalized at downstream boundaries;
new discovery does not emit that category.

Repositories nested inside an already discovered Git repository are owned by
the outer repository and are not manufactured into separate projects.
Android-style `.repo` checkout farms are likewise excluded from per-repository
inventory. The exact protected paths `/home/cole/cerberus` and
`/mnt/storage/Cole/cerberus`, including descendants, are always excluded.

## Operator Rule

Discovery does not mean embed.

Embedding requires a separate approved phase.
