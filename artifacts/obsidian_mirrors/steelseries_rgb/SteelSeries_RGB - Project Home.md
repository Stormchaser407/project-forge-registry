---
project_slug: "steelseries_rgb"
category: "active_project"
status: "review"
local_path: "/mnt/storage/Cole/Projects/SteelSeries_RGB"
launcher_command: "code-steelseries_rgb"
workspace_path: "/home/cole/.config/Code/User/workspaces/steelseries_rgb.code-workspace"
sync_policy: "docs_only / export_only"
---

# SteelSeries_RGB - Project Home

- [[Project Command Board]]
- [[SteelSeries_RGB - Demo Script]]
- [[SteelSeries_RGB - Architecture]]
- [[SteelSeries_RGB - Decisions]]
- [[SteelSeries_RGB - Roadmap]]
- [[SteelSeries_RGB - Agent Handoff]]
- [[SteelSeries_RGB - Runbook]]
- [[SteelSeries_RGB - Changelog]]

## Purpose

`SteelSeries_RGB` is tracked as an RGB/hardware-lighting project and future visual sync candidate, with detailed implementation claims held behind review.

## Current Status

- Registry status: `review`
- Category: `active_project`
- Proposed mirror path: `/home/cole/main_vault/10 Projects/steelseries_rgb`
- Documentation lane: showroom/memory-layer docs with controlled markdown-only sync planning

## What This Project Does

- Supports RGB and lighting-scene workflow objectives.
- Is associated with future visual sync targets (including Neon District context).
- Requires direct project review before detailed capability claims are treated as verified.

## Why It Matters

- Hardware-adjacent workflows benefit from careful safety language and reproducible runbooks.
- Clear documentation improves handoff quality without exposing sensitive operational details.
- Controlled sync lanes allow visibility while keeping risk low.

## Current Risks / Watch Items

- Hardware interaction details and permissions posture need explicit verification before publishing specifics.
- Avoid overstating supported devices/scenes without test evidence.
- Keep docs free of source code, secrets, and operational artifacts.

## Next Actions

1. Validate current project capabilities and constraints from approved notes/artifacts.
2. Replace `needs review` sections with evidence-backed summaries.
3. Continue dry-run sync checks and keep apply out of scope until approved.

## Demo Notes

- Emphasize safety-first documentation and clear separation of known vs unverified behavior.
- Show command flow and reporting, not live hardware actions.

## Links and Commands

- Local path: `/mnt/storage/Cole/Projects/SteelSeries_RGB`
- Workspace path: `/home/cole/.config/Code/User/workspaces/steelseries_rgb.code-workspace`
- Launcher command: `code-steelseries_rgb`
- Sync policy: `docs_only / export_only`

```bash
code "/home/cole/.config/Code/User/workspaces/steelseries_rgb.code-workspace"
code-steelseries_rgb

PYTHONPATH=src python3 -m unittest discover -s tests
./scripts/project-scan
PYTHONPATH=src python3 -m project_forge_registry.workspace_generation --dry-run --input-json artifacts/project_scan_report.json
PYTHONPATH=src python3 -m project_forge_registry.passport_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror_generation --dry-run
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug steelseries_rgb
```
