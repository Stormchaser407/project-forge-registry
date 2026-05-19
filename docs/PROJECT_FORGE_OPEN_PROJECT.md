# Project Forge Open Project

## Purpose

`project-forge-open-project` is a controlled local launch wrapper for opening a
project listed in `artifacts/dashboard_inventory.json` with an explicit profile
context.

It is designed for the operator model where one ChatGPT account can choose a
Personal or Business workspace/context after login. This wrapper does not handle
login and does not run Codex.

## Commands

Dry-run with Personal context:

```bash
./scripts/project-forge-open-project --slug lifesaver-ledger --profile personal --dry-run
```

Dry-run with Business context:

```bash
./scripts/project-forge-open-project --slug lifesaver-ledger --profile business --dry-run
```

Dry-run with plain editor context:

```bash
./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --dry-run
```

Explicit editor launch, after reviewing the dry-run output:

```bash
./scripts/project-forge-open-project --slug lifesaver-ledger --profile personal --open
```

Override the editor command:

```bash
./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --dry-run --editor codium
```

## Profile Behavior

| Profile | Launch environment |
|---|---|
| `personal` | Sets `CODEX_HOME` to `~/.codex-personal` for an explicit `--open` launch. |
| `business` | Sets `CODEX_HOME` to `~/.codex-business` for an explicit `--open` launch. |
| `plain` | Does not set `CODEX_HOME`; opens only the selected editor target. |

Dry-run prints the proposed profile value but does not launch an editor.

## Target Resolution

The wrapper reads only `artifacts/dashboard_inventory.json`.

For the selected slug it prints:

- slug
- project path
- resolved VS Code target
- selected profile
- proposed `CODEX_HOME` or `none`
- editor command
- eligibility decision and reason

If `vscode_target` is present in the dashboard inventory, that is the default
launch target. If the project root has a `.code-workspace` file and the
inventory target is not already a workspace file, the workspace file is used.

The dashboard inventory is never modified.

## Eligibility Policy

Allowed in this phase:

- `known_embedded`
- `clean_candidate`

Conditionally allowed:

- `control_repo` is dry-run safe for any profile.
- `control_repo` can be opened only with the `plain` profile in this phase.

Blocked in this phase:

- `dirty_candidate_review_first`
- `protected_manual_review`
- `unknown` or unsupported categories
- projects without a launch target

Blocked projects exit nonzero and print the policy reason.

## Editor Selection

Default editor selection is:

1. `code`, if available
2. `codium`, if available
3. missing editor message

`--editor` accepts a single command name or absolute path and is passed directly
as an executable, without shell evaluation.

## Safety

Default mode is dry-run.

No Codex login is attempted.

The wrapper does not:

- run Codex
- attempt Codex login
- read token contents
- print auth file contents
- copy auth files
- modify dashboard inventory
- write marker files
- touch remotes
- contact GitHub or Codeberg
- install packages
- mutate external project repos

Validation for this phase must not run `--open`.

## Dashboard Display

Phase 10.7D reuses this wrapper as dashboard command text only.

The static dashboard may display copy-paste dry-run commands for eligible
projects, but it does not execute them, does not generate clickable launcher
actions, and does not expose `--open` from HTML.
