# Project Forge Cold Start Desktop Launcher

## Purpose

`scripts/project-forge-install-cold-start-desktop` installs a user-local desktop
entry for Project Forge Cold Start and a self-contained Neon District SVG icon.

The launcher opens a terminal and runs Cold Start with dashboard open behavior.

## Commands

Preview without writing files:

    ./scripts/project-forge-install-cold-start-desktop --dry-run

Install the user-local files:

    ./scripts/project-forge-install-cold-start-desktop

Help:

    ./scripts/project-forge-install-cold-start-desktop --help

## Files Created In Default Mode

- `~/.local/share/icons/neon-district-project-forge/project-forge-cold-start.svg`
- `~/Desktop/project-forge-cold-start.desktop`
- `~/.local/share/applications/project-forge-cold-start.desktop`

The desktop files are marked executable.

## Desktop Entry

The generated launcher uses:

```ini
Name=Project Forge Cold Start
Comment=Resume Project Forge with status, tests, sync, and dashboard refresh
Exec=bash -lc 'cd "/mnt/storage/Cole/Projects/project-forge-registry" && ./scripts/project-forge-cold-start --open-dashboard; echo; echo "Press Enter to close..."; read'
Terminal=true
Categories=Development;Utility;
StartupNotify=true
```

`Icon=` points to the generated SVG icon in the user-local icon directory.

## Icon

The generated SVG is self-contained and uses a Neon District dystopian command
board style:

- dark background
- cyan, green, magenta, and amber accents
- forge/anvil shape
- terminal/dashboard frame
- no external image references
- no external font files
- no raster image requirement

## Cache Refresh

After writing files, the installer attempts optional local cache refreshes:

- `update-desktop-database ~/.local/share/applications`
- `kbuildsycoca6`

Both are best-effort. Missing commands or refresh failures do not fail the
installer.

## Safety Model

The default write mode writes only the expected user-local desktop and icon
files listed above.

It does not:

- write external project repos
- apply changes
- write marker files
- add or modify remotes
- push or fetch
- install packages
- make network calls
- launch VS Code
- run Cold Start during install
- open the dashboard during install
- create commits
- create tags

## Operator Note

Validation for Phase 10.8B should use `--dry-run` unless the operator explicitly
approves writing the desktop launcher and icon files.
