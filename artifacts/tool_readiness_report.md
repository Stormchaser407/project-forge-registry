# Project Forge Tool Readiness Report

- platform: `Linux-7.0.6-zen1-x86_64-with-glibc2.40`
- final_status: `ready_with_optional_gaps`
- mode: `read-only`

## Summary

- required_tools_missing: `0`
- optional_tools_missing: `2`
- tools_checked: `8`

## Tool Status

| Tool | Required | Status | Command | Version |
|---|---:|---|---|---|
| Git | yes | ready | `git` | git version 2.51.2 |
| Python 3 | yes | ready | `python3` | Python 3.13.12 |
| VS Code / Codium | no | ready | `code` | 1.119.0 |
| Obsidian | no | ready | `obsidian` | n/a |
| GitHub CLI | no | ready | `gh` | gh version 2.83.2 (nixpkgs) |
| xdg-open | no | ready | `xdg-open` | xdg-open 1.2.1 |
| desktop-file-validate | no | missing_optional | `not found` | n/a |
| PowerShell | no | missing_optional | `not found` | n/a |

## Details

### Git

- required: `true`
- available: `true`
- status: `ready`
- command_found: `git`
- version: `git version 2.51.2`
- purpose: Version control and repo status checks.
- setup_guidance: Install Git for your platform.

### Python 3

- required: `true`
- available: `true`
- status: `ready`
- command_found: `python3`
- version: `Python 3.13.12`
- purpose: Run Project Forge scripts and tests.
- setup_guidance: Install Python 3.

### VS Code / Codium

- required: `false`
- available: `true`
- status: `ready`
- command_found: `code`
- version: `1.119.0`
- purpose: Open project folders from the future dashboard.
- setup_guidance: Install VS Code or VSCodium.

### Obsidian

- required: `false`
- available: `true`
- status: `ready`
- command_found: `obsidian`
- version: `n/a`
- purpose: Open and maintain project notes.
- setup_guidance: Install Obsidian if you want vault integration.

### GitHub CLI

- required: `false`
- available: `true`
- status: `ready`
- command_found: `gh`
- version: `gh version 2.83.2 (nixpkgs)`
- purpose: Future GitHub workflow support.
- setup_guidance: Install GitHub CLI only if you want CLI GitHub integration.

### xdg-open

- required: `false`
- available: `true`
- status: `ready`
- command_found: `xdg-open`
- version: `xdg-open 1.2.1`
- purpose: Open files and links from Linux desktop actions.
- setup_guidance: Usually provided by xdg-utils on Linux.

### desktop-file-validate

- required: `false`
- available: `false`
- status: `missing_optional`
- command_found: `not found`
- version: `n/a`
- purpose: Validate Linux desktop launcher files.
- setup_guidance: Usually provided by desktop-file-utils on Linux.

### PowerShell

- required: `false`
- available: `false`
- status: `missing_optional`
- command_found: `not found`
- version: `n/a`
- purpose: Windows-oriented future support and scripting.
- setup_guidance: Install PowerShell if using Windows workflows.

## Safety Statement

- No installs were performed.
- No package manager commands were run.
- No remotes were added or modified.
- No push/fetch occurred.
- No external project folders were modified.
- This report is advisory only.
