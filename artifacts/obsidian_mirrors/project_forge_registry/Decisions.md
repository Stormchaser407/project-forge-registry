---
title: "project-forge-registry - Decisions"
aliases:
  - "project-forge-registry - Decisions"
---
# project-forge-registry - Decisions

## Decision Log

## 2026-05-06: Dry-Run-First Is The Default

- Decision: all new workflow phases default to planning mode.
- Why: this prevents accidental broad writes and keeps review checkpoints clear.

## 2026-05-06: Registry Before Automation

- Decision: build and validate a registry model before enabling broad sync automation.
- Why: automation quality depends on a trustworthy project inventory and classification layer.

## 2026-05-06: No Code In Obsidian Mirrors

- Decision: Obsidian lanes are docs-only.
- Why: avoids leaking implementation details, secrets, and operational files into the knowledge layer.

## 2026-05-06: Obsidian As Showroom and Memory Layer

- Decision: generated mirror docs are written for human review, handoff, and operational continuity.
- Why: this improves project visibility and keeps decisions discoverable.

## 2026-05-06: GitHub/Codeberg Deferred Until Safety Gates

- Decision: remote sync policy remains out of scope until local safety controls are stable.
- Why: avoid early coupling to remote systems before local correctness is proven.

## 2026-05-06: Cerberus Protected As Special Case

- Decision: Cerberus paths stay in protected, manual-review lanes.
- Why: system-bound and reconciliation-required patterns do not fit bulk automation assumptions.

## 2026-05-13: Controlled Markdown-Only Sync Lane

- Decision: introduce `project-forge-obsidian-sync` with strict markdown filtering and path guards.
- Why: formalizes docs sync without enabling code/secrets transfer.

## 2026-05-13: Prevent Test Side Effects On Tracked Sync Report

- Decision: tests must write sync reports into temporary artifacts directories, not tracked repo artifacts.
- Why: full test runs must not dirty the repository.
