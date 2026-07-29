# Project Forge Project Review

## Purpose

`project-forge-review-project` gives dashboard amber repos guarded terminal
commands for review and local commits.

The dashboard copies absolute-path commands so they can be pasted from any
terminal location. It does not execute them.

## Commands

Review status:

```bash
/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/scripts/project-forge-review-project --slug <slug> --status
```

Review diff summary:

```bash
/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/scripts/project-forge-review-project --slug <slug> --diff
```

Review recent commits:

```bash
/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/scripts/project-forge-review-project --slug <slug> --log
```

Commit preflight:

```bash
/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/scripts/project-forge-review-project --slug <slug> --commit-dry-run
```

Guarded commit template:

```bash
/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/scripts/project-forge-review-project --slug <slug> --commit \
  --confirm-slug <slug> \
  --yes-commit-reviewed \
  --message "describe reviewed changes"
```

## Commit Guards

Real commit requires:

- `--commit`
- non-empty `--message`
- `--confirm-slug` exactly matching `--slug`
- `--yes-commit-reviewed`

Commit automation is limited to projects whose inventory action is exactly
`dirty_review_first`. Projects with an explicit evidence-based protected
category and the Project Forge control repository are blocked even when invoked
directly from the CLI. A Cerberus name alone does not block review or commit
preflight.
Duplicate slugs are rejected as ambiguous.

By default, commit stages tracked changes only with `git add -u`.

Untracked files require both:

- `--include-untracked`
- `--yes-include-untracked`

Sensitive-looking paths such as `.env`, secrets, tokens, keys, certificates,
SQLite files, and database files block commit unless `--allow-sensitive-paths`
is explicitly provided after manual review.

## Safety Model

Status, diff, log, and commit preflight are read-only.

Commit is the only mutating mode. It never pushes, fetches, edits remotes,
installs packages, launches VS Code, writes Obsidian vault files, or creates
tags.
