# Project Forge Codex Profiles

## Purpose

Project Forge can later support a local choice between Codex workspace contexts
before launching Codex or VS Code workflows.

The current operator model is one ChatGPT account with a workspace/context
choice after login, such as Personal or Business. Phase 10.7A does not automate
that login flow. It only probes local profile assumptions safely.

## Command

Personal workspace probe:

    ./scripts/project-forge-codex-profile-probe --profile personal

Business workspace probe:

    ./scripts/project-forge-codex-profile-probe --profile business

Plain editor / no Codex assumption:

    ./scripts/project-forge-codex-profile-probe --profile plain

Interactive selector:

    ./scripts/project-forge-codex-profile-probe --interactive

Help:

    ./scripts/project-forge-codex-profile-probe --help

## Built-In Profiles

The probe currently uses built-in defaults:

| Profile | Label | Proposed `CODEX_HOME` |
|---|---|---|
| `personal` | Personal Codex workspace | `~/.codex-personal` |
| `business` | Business Codex workspace | `~/.codex-business` |
| `plain` | Plain editor / no Codex assumption | empty |

The probe prints the selected label, proposed `CODEX_HOME`, whether that
directory exists, whether a likely auth file exists, and whether `codex` is on
`PATH`.

It does not print auth file contents.

## Config Files

Example config:

    config/codex_profiles.example.yml

Future local override:

    config/codex_profiles.local.yml

The local override is git-ignored and must not be committed.

Do not store raw tokens, auth JSON, session cookies, copied credential files, or
private account material in either config file.

## Safety Model

The probe is read-only and local.

It does not:

- store tokens
- read token contents
- print auth JSON
- copy auth files
- run `codex login`
- execute Codex commands beyond checking `command -v codex`
- launch VS Code
- write external repos
- apply changes
- write marker files
- add or modify remotes
- push or fetch
- install packages
- make network calls
- create commits
- create tags

## Next Phase

A later phase can use this profile model to launch wrappers with an explicit
operator-selected `CODEX_HOME`. That phase should keep profile selection
separate from token storage and login execution.
