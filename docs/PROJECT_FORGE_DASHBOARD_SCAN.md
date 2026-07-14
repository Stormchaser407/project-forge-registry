# Project Forge Dashboard Scan

## Purpose

`project-forge-scan-dashboard` refreshes stale dashboard status after project
state changes, such as committing a dirty amber repo.

It performs the safe refresh chain:

1. read-only known-repository status refresh
2. dashboard inventory rebuild
3. static dashboard HTML render
4. optional local dashboard open

Broad filesystem discovery is explicit through `--full-scan` or
`--scan-root PATH`.

## Commands

Refresh the known inventory and rebuild without opening:

```bash
/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/scripts/project-forge-scan-dashboard --no-open
```

Refresh and reopen the local dashboard:

```bash
/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/scripts/project-forge-scan-dashboard --open
```

Override scan roots and exclude a managed source forest when needed:

```bash
/run/media/cash/WD_BLACK_4TB/Cole/Projects/project-forge-registry/scripts/project-forge-scan-dashboard \
  --scan-root /run/media/cash/WD_BLACK_4TB/Cole/Projects \
  --exclude /run/media/cash/WD_BLACK_4TB/Cole/Projects/crdroid/source \
  --no-open
```

Use `--exclude PATH` more than once when a scan root contains managed source
forests, such as Android `repo` workspaces, whose component repositories should
not each appear as independent Forge projects.

## Dashboard Button

The dashboard renders a `Scan Button` operator panel. Because static local HTML
cannot safely execute shell commands, the button copies the scan command for
terminal review and execution.

## Safety Model

The scan wrapper is read-only against discovered repos.

It does not:

- write to discovered repos
- apply marker files
- touch remotes
- push or fetch
- install packages
- contact network services
- launch VS Code
- create commits
- create tags
