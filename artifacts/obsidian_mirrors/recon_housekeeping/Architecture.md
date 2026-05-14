---
title: "recon_housekeeping - Architecture"
aliases:
  - "recon_housekeeping - Architecture"
---
# recon_housekeeping - Architecture

## Overview

High-level architecture centers on planning and memory, not mutation: collect evidence, classify work, stage decisions, and hand off cleanly.

## Components

- Workspace and launcher entry points for operators.
- Registry-generated artifacts for scan/classification context.
- Showroom docs for handoff, risks, and next-step planning.

## Boundaries

- No direct external folder modifications from this docs lane.
- No source code or sensitive operational data in mirror docs.
- Sync remains dry-run-first until explicit apply authorization.

## Interfaces

- `./scripts/project-scan`
- phase generator dry-runs
- `project-forge-obsidian-sync --dry-run --slug recon_housekeeping`

## Needs Review

Internal implementation details of housekeeping scripts and heuristics should be documented only after direct repo review.
