# Project Forge Phase 10.7F Plain Open Test Findings

## Summary

Phase 10.7F performed the first controlled local editor open test through Project Forge.

Test target:

- slug: `lifesaver-ledger`
- category: `known_embedded`
- profile: `plain`
- command mode: `--open`

The plain profile does not set `CODEX_HOME`.

## Commands Verified

Dry-run command:

```bash
./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --dry-run
```

Actual controlled open command:

```bash
./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --open
```

## Observed Result

- VS Code was available at `/run/current-system/sw/bin/code`.
- The wrapper resolved `lifesaver-ledger` correctly.
- The wrapper selected `plain` profile.
- The wrapper reported `Proposed CODEX_HOME: none`.
- The wrapper reported the project as eligible.
- The wrapper requested editor launch.
- VS Code processes were observed after launch.
- The Project Forge repo remained clean after the open test.

## Policy Checks

Before opening the known embedded repo, Phase 10.7F confirmed:

- protected repo example `cerberus` remained blocked
- dirty repo example `djfiddlesticks-website` remained blocked
- only `lifesaver-ledger` with `plain` profile was opened

## Important Observation

Existing VS Code processes showed OpenAI/Codex extension app-server processes.

This does not mean Project Forge launched Codex. It means the normal VS Code session already had the extension active in the default VS Code user-data environment.

This matters for later Personal/Business profile tests because VS Code extension behavior may depend on VS Code user-data or OS credential storage, not only `CODEX_HOME`.

## Safety Confirmation

- Plain profile was used.
- No `CODEX_HOME` was set by Project Forge for the plain launch.
- Project Forge did not request Codex login.
- Project Forge did not read, print, or copy token/auth files.
- Project Forge did not touch remotes.
- Project Forge did not push or fetch.
- Project Forge did not install packages.
- Project Forge did not perform apply or marker writes.

## Next Recommendation

Proceed to Phase 10.7G only after accepting this finding: plain editor launch works, but VS Code may already run the OpenAI/Codex extension independent of Project Forge profile selection.

Phase 10.7G should test Personal and Business profile behavior carefully and document whether `CODEX_HOME` affects the VS Code extension, the Codex CLI, both, or neither.
