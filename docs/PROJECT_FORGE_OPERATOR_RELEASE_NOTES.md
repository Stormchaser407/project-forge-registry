# Project Forge Operator Release Notes

## Release

Phase 10.9 closes Project Forge as a local command center release.

The release keeps the operator path simple:

- run Cold Start
- refresh the static dashboard
- inspect display-only launch commands
- dry-run a controlled project open
- defer Codex Personal/Business isolation until a dedicated research phase

## What Is Ready

- `./scripts/project-forge-cold-start` resumes the repo with status, tests,
  safe sync dry-run, dashboard refresh, dashboard path output, and final status.
- `./scripts/project-forge-dashboard --no-open` refreshes
  `artifacts/dashboard_inventory.json`, `artifacts/dashboard_inventory_report.md`,
  and `artifacts/dashboard.html`.
- `artifacts/dashboard.html` is the static Neon District command center.
- Dashboard launch commands are copy-paste text only.
- `./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --dry-run`
  previews a controlled open without launching VS Code.
- Personal and Business profile homes exist for later research.
- Plain editor open has been tested.

## Safety Notes

The closeout release does not:

- apply changes
- write marker files
- modify external repos
- run `--open` by default
- launch VS Code from validation
- run Codex
- perform Codex login
- read, print, copy, or move token/auth files
- push, fetch, create remotes, or contact GitHub/Codeberg
- install packages
- make network calls

## Operator Commands

```bash
./scripts/project-forge-cold-start
./scripts/project-forge-dashboard --no-open
./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --dry-run
```

Dashboard:

```text
artifacts/dashboard.html
```

## Known Embedded Pilot Repos

- `lifesaver-ledger`
- `media-dedupe`
- `neon-district`
- `recon_housekeeping`

## Deferred

- Obsidian command center integration
- repo action policies
- remote strategy
- Codex/VS Code Personal and Business isolation research

## Recommended Checkpoint

Recommended commit message:

```text
Document Phase 10 local command center closeout
```

Recommended tag after commit:

```text
v0.10.9-local-command-center-closeout
```
