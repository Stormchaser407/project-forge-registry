---
title: "SteelSeries_RGB - Demo Script"
aliases:
  - "SteelSeries_RGB - Demo Script"
---
# SteelSeries_RGB - Demo Script

## Thirty-Second Version

`SteelSeries_RGB` is documented as a hardware-lighting project with a safety-first showroom layer. This demo explains current known context without claiming unverified runtime behavior.

## Why This Exists

- Hardware-focused projects need clear operational boundaries.
- Showroom docs make handoff and status reviews easier without exposing sensitive internals.

## Demo Flow

1. Open workspace and launcher.
2. Summarize verified high-level goals.
3. Call out `needs review` capability areas.
4. Run dry-run sync command and show report path.

## Demo Commands

```bash
code "/home/cole/.config/Code/User/workspaces/steelseries_rgb.code-workspace"
code-steelseries_rgb
PYTHONPATH=src python3 -m project_forge_registry.obsidian_sync --dry-run --slug steelseries_rgb
```

## Known vs Needs Review

- Known: project is active, mirrored in docs, and handled via controlled sync lanes.
- Needs review: precise hardware support matrix, runtime write behavior, and environment assumptions.

## Next Build Step

Integrate verified capability and safety notes from approved qualification records.
