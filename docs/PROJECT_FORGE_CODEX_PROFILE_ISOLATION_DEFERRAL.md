# Project Forge Phase 10.7G Codex Profile Isolation Deferral

## Decision

Phase 10.7G defers deeper Personal/Business Codex profile isolation research until after the stable Phase 10 product closeout.

This is an intentional product-scope decision, not a failure.

## Current Stable Capability

Project Forge already supports:

- Codex profile probing
- Codex profile home bootstrap
- ignored local config for Personal, Business, and Plain profile labels
- controlled project open wrapper
- dashboard display of copy-paste dry-run launch commands
- first successful plain profile editor open test

The plain open test confirmed that Project Forge can safely open a known embedded project through the wrapper without setting `CODEX_HOME`.

## Reason for Deferral

Personal/Business Codex isolation may require more than setting `CODEX_HOME`.

Open questions include:

- whether VS Code reuses an already-running process
- whether VS Code extension host inherits the wrapper environment
- whether the OpenAI/Codex extension honors `CODEX_HOME`
- whether Codex extension auth uses VS Code user-data, OS credential storage, `~/.codex`, or `CODEX_HOME`
- whether separate VS Code user-data directories or VS Code profiles are required

These questions are valuable, but they are not required for a stable Project Forge local command center release.

## Product Boundary

Project Forge should not block Phase 10 completion on Codex account/workspace separation.

For now, the dashboard and wrapper may continue showing Personal, Business, and Plain dry-run commands as operator aids.

The supported stable behavior is:

- dry-run planning is safe
- plain project open works
- protected and dirty projects remain blocked
- Personal/Business profile homes exist for later research
- Personal/Business isolation is not yet guaranteed

## Deferred Future Work

A later phase may investigate one or more of:

- dedicated VS Code `--user-data-dir` wrappers
- dedicated VS Code profiles
- separate extension directories
- Codex CLI behavior under different `CODEX_HOME` values
- Codex extension behavior under different launch environments
- safe operator prompts for choosing Personal or Business context

## Safety Confirmation

This deferral phase does not:

- run Codex
- launch VS Code
- perform Codex login
- read, print, copy, or move auth/token files
- modify external repos
- perform apply actions
- add or modify remotes
- push or fetch
- install packages

## Next Recommendation

Proceed to Phase 10.9 closeout and treat Project Forge as a stable local command center milestone.
