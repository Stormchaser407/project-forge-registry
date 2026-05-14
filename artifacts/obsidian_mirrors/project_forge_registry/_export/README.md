# project-forge-registry Export Staging

This folder is the controlled staging lane for docs-only export material.

## Purpose

- Hold markdown documentation intended for later approved Obsidian-to-repo doc workflows.
- Keep showroom content separate from operational code and sensitive artifacts.

## Allowed Content

- Markdown documentation only.
- High-level project notes, runbooks, decisions, and summaries.

## Never Place Here

- Source code files.
- Secrets, tokens, or env values.
- Databases, logs, binaries, caches, or operational exports.

## Current Policy

- `_export/docs/` remains reserved until the next approved phase.
- Any future bidirectional doc sync must pass explicit safety checks first.
