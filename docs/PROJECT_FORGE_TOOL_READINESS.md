# Project Forge Tool Readiness

## Purpose

The tool readiness checker is the onboarding diagnostic for Project Forge.

It answers:

- Which required tools are installed?
- Which recommended tools are missing?
- What should the operator install or configure next?

It does not install anything.

## Command

Run:

    PYTHONPATH=src python3 -m project_forge_registry.tool_readiness

The report is written to:

    artifacts/tool_readiness_report.md

## Safety

The checker is read-only.

It does not:

- install packages
- run package managers
- add or modify remotes
- push or fetch
- write to external project folders
- contact GitHub or Codeberg
- touch Cerberus

## Required Tools

- Git
- Python 3
- shell or terminal

## Recommended Tools

- VS Code or Codium
- Obsidian
- GitHub CLI
- xdg-open
- desktop-file-validate
- PowerShell for Windows-oriented workflows

## Status Values

- ready: tool was found
- missing_required: required tool was not found
- missing_optional: optional tool was not found

## Final Status Values

- ready: all checked tools are available
- ready_with_optional_gaps: required tools are available but optional tools are missing
- blocked: at least one required tool is missing

## Operator Rule

Missing optional tools are not failure.

They are onboarding guidance.
