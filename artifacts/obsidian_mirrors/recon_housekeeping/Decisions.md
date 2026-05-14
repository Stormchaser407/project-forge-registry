---
title: "recon_housekeeping - Decisions"
aliases:
  - "recon_housekeeping - Decisions"
---
# recon_housekeeping - Decisions

## Decision Log

## 2026-05-14: Keep Housekeeping Documentation High-Signal

- Decision: mirror docs should prioritize decisions, risks, and status over implementation noise.
- Why: housekeeping work is coordination-heavy and benefits from concise, durable context.

## 2026-05-14: Review Before Cleanup

- Decision: do not treat scan/classification output as self-authorizing cleanup action.
- Why: false positives in consolidation can cause real loss.

## 2026-05-14: Dry-Run Sync Only In This Lane

- Decision: keep Obsidian sync planning in dry-run mode by default.
- Why: preserves safe staging and prevents accidental vault mutation.

## Needs Review

- Which cleanup decisions are ready for “operator-approved action” status.
- Which archaeology notes should be promoted to long-term runbook guidance.
