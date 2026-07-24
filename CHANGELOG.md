# Changelog

## Unreleased

### Added

- Canonical `PROJECT_CHARTER.md`, `PROJECT_STATUS.md`, and repository lifecycle/compliance standard.
- Explicit cross-system authority map separating Project Forge, repositories, Todoist, Calendar, C2, Obsidian, and conversation history.
- Architecture decision retiring Project Forge's former universal-planner mission.
- Architecture decision retiring project-name-based Cerberus secrecy and protected status.
- Legacy category normalization for stale `protected_manual_review` discovery artifacts.
- Phase 11G Neon District / Punk Union static local command board generator, wrapper, docs, report, manifest, and tests.
- Phase 11H.5 guarded launcher replacement apply command capability with default dry-run reports, strict real-apply guards, wrapper, docs, entrypoint, and tempdir-only apply tests.
- Dashboard GUI polish with local search, lane filters, clickable summaries, sorting, collapsible sections/cards, embedded term explanations, clipboard copy controls, and a dry-run-first desktop launcher installer.
- Dirty-review dashboard command shortcuts plus guarded `project-forge-review-project` status, diff, log, commit-preflight, and confirmed commit workflow.
- Dashboard scan-and-rebuild operator button plus `project-forge-scan-dashboard` wrapper to refresh repo discovery before rebuilding stale dirty-review counts.
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

### Changed

- Project Forge is now explicitly a technical project/fleet registry and guarded operator surface, not a personal planner or universal roadmap owner.
- Every materially reviewed repository must leave reconciliation compliant with an explicit lifecycle state or archived/superseded with preservation evidence.
- Cerberus-labeled repositories are scanned, displayed, launched, mirrored, synchronized, and evaluated under the same evidence-based rules as other personal repositories.
- Scanner, discovery, workspace, passport, mirror, export, remote-policy, and project-sync gates no longer infer protection from the word `Cerberus`.
- Real credentials, env files, databases, case data, raw evidence, exports, and logs remain protected by ordinary content-based safeguards.
- The root README is now a current operator front door; detailed phase archaeology remains in docs, handoff files, artifacts, and Git history.

### Verification

- Full GitHub unit-test suite passed after the Cerberus policy migration.
- Active source was checked to ensure the retired `cerberus_protected` and `cerberus_special_case_candidate` vetoes no longer remain outside the explicit legacy-normalization helper.
- Temporary migration workflow and script were removed after verification.

### Notes

- Phase 11G.1 clarifies Neon command board generation-time commit metadata and prefers checkpoint tags pointing at `HEAD`.
- Phase 11E documents that human-edited vault notes win by default; maintenance remains create-only, skip identical, block existing different, no silent overwrite, and no delete.
- Phase 11B.1 normalizes the vault apply plan JSON schema to use `vault_root` as the canonical proposed target root field.
- Current stable baseline before this closeout is `v0.10.7g-codex-profile-isolation-deferred`.
- Recommended final Phase 10 closeout tag is `v0.10.9-local-command-center-closeout`.
- Personal/Business Codex isolation remains deferred for a dedicated future research phase.
