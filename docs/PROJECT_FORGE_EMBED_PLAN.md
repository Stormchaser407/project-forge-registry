# Project Forge Embed Plan

## Purpose

The embed plan is the dry-run planning phase for marking approved repositories as Project Forge managed.

It reads the repo discovery inventory and decides which selected repos would receive marker files in a later approved apply phase.

## Command

Example:

    PYTHONPATH=src python3 -m project_forge_registry.embed_plan --include-slug recon_housekeeping --include-slug media-dedupe

Reports:

    artifacts/embed_plan_report.md
    artifacts/embed_plan_inventory.csv

## Marker Files Planned

The apply phase may later write:

    .project-forge.yml
    docs/PROJECT_FORGE.md

This phase does not write those files.

## Safety

The embed plan is dry-run only.

It does not:

- write marker files
- modify external repos
- apply changes
- add or modify remotes
- push or fetch

## Decisions

- plan_marker_write
- candidate_not_selected
- already_embedded
- skip_control_repo
- blocked_protected
- blocked_dirty
- blocked_unknown

## Operator Rule

Discovery does not mean embed.

Planning does not mean apply.

Apply requires a separate approved phase.
