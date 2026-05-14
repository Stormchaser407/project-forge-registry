# SITREP 2026-05-14 Phase 10 Intake And Dashboard Design

Phase 10 turns Project Forge from a local command-board repo into an intake-driven project operations dashboard.

This phase is design-only. It does not approve implementation, external repo writes, apply behavior, remotes, push/fetch, hardware identifiers, secret scanning, package installs, or Cerberus handling.

## 1. Purpose

- Create a first-run intake process.
- Add onboarding for required and optional tools.
- Design optional authorized repo discovery.
- Define safe repo embed markers.
- Define a Neon District dashboard to replace the old Recon Command Board.
- Keep Phase 11 portability/public-release requirements visible.

## 2. Core Principle

Project Forge should onboard like a good instructor: explain what matters, check what exists, show what is missing, offer the next safe move, and never grab the steering wheel unless invited.

## 3. First-Run Intake Wizard

The intake wizard should guide the user through:

1. Explain Project Forge.
2. Check required tools.
3. Guide missing setup.
4. Configure project roots.
5. Configure Obsidian vault root.
6. Configure editor command.
7. Offer authorized repo discovery.
8. Review discovered repos.
9. Approve embed plans.
10. Open the dashboard.

## 4. Onboarding Modes

- explain: describe the system and concepts.
- check: inspect tool availability without installing anything.
- guide: print platform-specific setup instructions.
- install: future assisted install mode, explicit approval only.

No silent installs. No package manager changes without explicit approval.

## 5. Tool Readiness Checks

Required baseline tools:

- Git
- Python 3
- shell or terminal

Recommended tools:

- VS Code or Codium
- Obsidian
- GitHub CLI
- GitHub Desktop, especially for Windows users
- PowerShell and Windows Terminal on Windows
- xdg-open and desktop launcher support on Linux

Platform guidance should cover Linux/NixOS, Ubuntu/Debian-style Linux, Windows, and macOS.

## 6. Config Model

Public-safe example config:

    config/project_forge.example.yml

Local ignored config:

    config/project_forge.local.yml

Config fields should include:

- projects_root
- vault_project_root
- default_slug
- editor_command
- dashboard_host
- dashboard_port
- theme
- scan_roots
- excluded_paths
- allow_apply: false
- allow_push: false

## 7. Authorized Repo Discovery Scan

Repo discovery must be optional, one-time, authorized, and dry-run-first.

It may detect:

- .git directories
- README files
- AGENTS.md
- .code-workspace files
- existing Project Forge markers

It must not:

- read secrets
- index file contents by default
- collect hardware identifiers
- write to discovered repos
- traverse dangerous system paths

Default exclusions should include /proc, /sys, /dev, /run, /nix/store, node_modules, .venv, __pycache__, .cache, Trash, and Steam libraries unless explicitly included.

## 8. Discovered Repo Categories

- known_embedded
- clean_candidate
- dirty_candidate_review_first
- protected_manual_review
- unknown_structure
- ignored_by_policy

## 9. Embed Marker Model

Machine marker:

    .project-forge.yml

Human marker:

    docs/PROJECT_FORGE.md

Marker fields:

- slug
- project_name
- managed_by
- embed_status
- editor_command
- safe_default_profile
- allow_apply: false
- allow_push: false

Embedding requires separate approval. Discovery does not imply embedding.

## 10. Dashboard Architecture

The dashboard replaces the old Recon Command Board with a project-aware mission control wall.

Each card should show:

- project name
- slug
- path
- repo/local light
- docs/Obsidian light
- risk/remote light
- last check time
- final status
- safe action buttons

## 11. Neon District Three-Light Model

| Light | Meaning | Good | Attention | Blocked |
|---|---|---|---|---|
| Repo / Local | Git repo, clean state, embed marker, workspace launch. | cyan/green | amber | magenta/red |
| Docs / Obsidian | Obsidian sync, export docs, report freshness. | cyan/green | amber | magenta/red |
| Risk / Remote | remote posture, push readiness, protection state. | cyan/green | amber | magenta/red |

## 12. Dashboard Actions

Allowed actions:

- Open VS Code
- Run safe check
- Open reports
- Open command board
- Open Obsidian docs

Disabled future actions:

- Apply
- Push
- Remote setup
- Public release

## 13. Proposed Commands

- project-forge-intake
- project-forge-check-tools
- project-forge-discover-repos
- project-forge-embed-plan
- project-forge-embed-apply
- project-forge-dashboard

## 14. Phase 11 Portability Notes

Phase 10 should avoid hardcoded personal paths where practical. Phase 11 will make Project Forge machine-agnostic through config, public-safe docs, bootstrap scripts, install guidance, and release checks.

## 15. Implementation Roadmap

- Phase 10.1: config schema and example local config.
- Phase 10.2: tool readiness checker.
- Phase 10.3: authorized repo discovery dry-run.
- Phase 10.4: embed plan and approved marker apply.
- Phase 10.5: dashboard inventory/status API.
- Phase 10.6: Neon District dashboard UI.
- Phase 10.7: VS Code launch actions.
- Phase 10.x: Cold Start script and desktop launcher.

## 16. Open Questions

- Should embed markers be YAML-only, Markdown-only, or both?
- Should the first dashboard be static HTML, FastAPI, or Textual/TUI?
- Should repo discovery scan only configured project roots by default?
- Should new folder auto-detection notify only or propose embed plans automatically?
