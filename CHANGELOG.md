# Changelog

## Unreleased

### Added

- Phase 11G Neon District / Punk Union static local command board generator, wrapper, docs, report, manifest, and tests.
- Phase 11H.5 guarded launcher replacement apply command capability with default dry-run reports, strict real-apply guards, wrapper, docs, entrypoint, and tempdir-only apply tests.
- Phase 11H.4 guarded launcher replacement apply dry-run/preflight command, docs, artifacts, wrapper, entrypoint, and tests with no real apply mode.
- Phase 11H.3 design-only guarded launcher replacement apply contract docs and artifacts with no apply, replacement, or mutation path.
- Phase 11H.2 operator-reviewed Neon launcher replacement plan artifacts with no apply or mutation path.
- Phase 11H.1 dry-run/read-only Neon command board launcher/autostart discovery command, docs, report, JSON artifact, wrapper, and tests.
- Phase 11H.0 documentation-first Neon command board launcher/autostart replacement plan and planning artifacts.
- Phase 11E Obsidian vault maintenance policy and no-clobber doctrine report.
- Phase 11C.1 Obsidian vault apply UX hardening with preflight summary output, stronger apply refusal messaging, and required `--confirm-vault-root` matching.
- Phase 11C guarded create-only Obsidian vault apply command with dry-run reports.
- Phase 11B dry-run real-vault apply planner for generated Obsidian artifact notes.
- Phase 11A dry-run Obsidian artifact mirror command, docs, tests, report, and manifest.
- Phase 10.9 closeout documentation for the Project Forge local command center.
- Operator release notes for Cold Start, dashboard refresh, and dry-run project open workflows.
- Closeout report artifact at `artifacts/phase_10_closeout_report.md`.

### Notes

- Phase 11G.1 clarifies Neon command board generation-time commit metadata and prefers checkpoint tags pointing at `HEAD`.
- Phase 11E documents that human-edited vault notes win by default; maintenance remains create-only, skip identical, block existing different, no silent overwrite, and no delete.
- Phase 11B.1 normalizes the vault apply plan JSON schema to use `vault_root` as the canonical proposed target root field.
- Current stable baseline before this closeout is `v0.10.7g-codex-profile-isolation-deferred`.
- Recommended final Phase 10 closeout tag is `v0.10.9-local-command-center-closeout`.
- Personal/Business Codex isolation remains deferred for a dedicated future research phase.
