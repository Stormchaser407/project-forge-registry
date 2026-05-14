---
title: "project-forge-registry - Architecture"
aliases:
  - "project-forge-registry - Architecture"
---
# project-forge-registry - Architecture

## System Intent

Project Forge Registry is a staged workflow engine for project discovery, classification, and controlled automation rollout.

## Phase Pipeline

1. Phase 1: scanner and classifier
2. Phase 2: workspace and launcher generation
3. Phase 3: passport proposal generation
4. Phase 4: Obsidian mirror proposal generation
5. Phase 4b: controlled markdown-only Obsidian sync
6. Future: policy-gated remote sync and project-sync automation

## Core Components

- Scanner layer:
  - Reads project roots and emits normalized inventory reports.
- Classification layer:
  - Assigns category, status, action, and safety warnings.
- Safety layer:
  - Applies skip rules and protects special cases such as Cerberus.
- Artifact generators:
  - Produce workspace/launcher, passport, and mirror proposal outputs.
- Sync layer:
  - Copies markdown-only docs from mirror proposals to approved vault targets.

## Data and Control Boundaries

- Source-of-truth inputs are local filesystem observations and generated artifacts.
- Generated artifacts stay inside this repository during planning/generation phases.
- Docs sync path is constrained to approved Obsidian project roots.
- Remote sync is disabled until policy gates are explicitly approved.

## Safety Model

- Dry-run is the default mode.
- Apply paths are narrowly constrained.
- Destination deletion is not part of docs sync behavior.
- Non-markdown and sensitive file patterns are excluded from docs sync.
- Cerberus system/reconciliation paths are protected from normal lanes.

## Operator Entry Points

```bash
./scripts/project-scan
PYTHONPATH=src python3 -m project_forge_registry.workspace_generation --dry-run --input-json artifacts/project_scan_report.json
PYTHONPATH=src python3 -m project_forge_registry.passport_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug project_forge_registry
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Showroom Layer Notes

The mirror docs are designed to be readable by operators and reviewers first, while still reflecting the real technical workflow and safety constraints.
