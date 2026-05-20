# Codex Handoff

## Mission

Preserve the Phase 10.7F first controlled local open test findings.

## Current State

Phase 10.7F tested the controlled open wrapper with:

- slug: `lifesaver-ledger`
- profile: `plain`
- mode: `--open`

The wrapper resolved the project, kept `CODEX_HOME` unset, and requested a VS Code launch.

Protected and dirty project policy checks still blocked correctly before the open test.

## Important Finding

VS Code may already run OpenAI/Codex extension app-server processes in the normal VS Code user-data environment.

Do not assume `CODEX_HOME` controls the VS Code extension until Phase 10.7G tests it.

## Safety

- No Project Forge Codex login was requested.
- No auth/token files were read, printed, or copied.
- No remotes, push/fetch, package installs, apply actions, or marker writes.

## Next Recommended Phase

Phase 10.7G: controlled Personal/Business profile behavior test.
