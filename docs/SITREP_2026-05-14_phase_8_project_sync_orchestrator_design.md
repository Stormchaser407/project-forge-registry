# SITREP 2026-05-14 Phase 8 Project Sync Orchestrator Design

Working title: **Cash Synctacular Triple Whammy**

This document defines a design-only orchestration plan for coordinating Project Forge workflows under a single command surface.

This is not implementation approval. No sync, push, remote setup, or broad apply is authorized by this document.

## 1. Purpose

- Design a safe orchestration layer that coordinates proven Project Forge lanes for one slug at a time.
- Provide a command-board style runner that executes gated checks and reports status clearly.
- Reduce operator overhead by sequencing existing tools in a consistent, auditable order.

## 2. Non-goals

- Not a “magic do-everything” command in initial versions.
- Not an auto-push system.
- Not an auto-remote-setup system.
- Not multi-project bulk sync initially.
- Not Cerberus handling.
- Not unknown/review_required auto-processing in initial versions.

## 3. Current Building Blocks Available

- Phase 1: scanner/classifier (`project-forge-registry`)
- Phase 2: workspace/launcher generation (`project-forge-workspace-generate`)
- Phase 3: passport generation (`project-forge-passport-generate`)
- Phase 4: mirror proposal generation (`project-forge-obsidian-mirror-generate`)
- Phase 4b: mirror -> vault docs sync (`project-forge-obsidian-sync`)
- Phase 5: export planner/apply (`project-forge-export-sync`)
- Phase 7: remote plan/verify (`project-forge-remote-plan`, `project-forge-remote-verify`)
- Phase 7b: push-ready gate (`project-forge-push-ready`)

## 4. Proposed Command Name

- `project-sync`

## 5. Proposed CLI Options

- `--slug <slug>`
- `--dry-run`
- `--apply`
- `--refresh-scan`
- `--refresh-workspace`
- `--refresh-passport`
- `--refresh-mirror`
- `--sync-obsidian`
- `--export-docs`
- `--remote-plan`
- `--remote-verify`
- `--push-ready`
- `--allow-remote-setup`
- `--allow-push`
- `--report-name <filename>`
- `--stop-on-warning`
- `--include-category <category>`
- `--exclude-category <category>`

## 6. Default Mode Behavior

- Default mode is `--dry-run`.
- Default scope is one slug (`--slug` required initially).
- Default orchestrator behavior is report-first and no external mutation.
- No hidden apply behavior.

## 7. Single-Slug Workflow

Initial supported workflow is one project slug at a time.

Design rule:

- each sub-lane is run in read-only or dry-run mode first
- lane outputs feed combined orchestration reporting
- failures or gate misses stop downstream apply-capable steps

## 8. Multi-Project Workflow, Future Only

Future extension only; out-of-scope for initial implementation.

Potential future support:

- category-driven slug selection
- explicit include/exclude filters
- ordered execution waves with per-slug reports

Safety requirement:

- no multi-project apply until single-slug orchestration is proven and approved.

## 9. Dry-Run Sequence

Recommended single-slug dry-run order:

1. Validate slug/passport.
2. Run/inspect project classification state.
3. Workspace/launcher dry-run if relevant.
4. Passport dry-run or validation.
5. Obsidian mirror dry-run.
6. Obsidian docs sync dry-run.
7. Export docs dry-run.
8. Remote plan dry-run.
9. Remote verify dry-run.
10. Push-ready dry-run.
11. Generate combined `project-sync` report.

## 10. Apply Sequence, Future/Gated Only

Initial orchestration implementation should avoid broad apply.

Future apply sequence must be explicit and lane-gated:

- apply only lanes explicitly enabled by flags
- apply only after each lane’s gate passes
- require confirmations for remote-related actions
- no implicit “final push” stage

## 11. Safety Gates

Global orchestration gates:

- dry-run default
- explicit slug required
- protected-project checks
- no deletes
- no code copy into Obsidian
- no repo-root README overwrite from export lane
- no hidden side effects
- per-lane report must exist after run

## 12. Remote Gates

Remote-related lanes must remain read-only in early orchestration versions.

Required remote gates:

- remote eligibility policy pass
- local git state known
- clean-tree check when required
- push-ready status at most `ready_for_operator_review`
- operator approval explicitly pending

No automatic push, no automatic remote setup.

## 13. Obsidian/Docs Gates

For Obsidian mirror sync lane:

- markdown-only constraints
- mirror source path validation
- no non-doc content
- no unintended vault path writes

For orchestration dry-run:

- report should show whether Obsidian lane is skipped, blocked, or dry-run ready.

## 14. Export-Sync Gates

Export lane constraints:

- source restricted to `_export/docs/` by default
- destination restricted to `<local_path>/docs/`
- no repo-root README overwrite
- no deletes
- markdown-only
- report evidence required

## 15. Push-Ready Relationship

`project-sync` should consume `push-ready` results as a downstream gate.

Important policy:

- push-ready result informs operator review readiness
- `project-sync` must not interpret this as permission to push
- final state in early versions should remain planning/review-oriented

## 16. Report Contents

Proposed combined report default:

- `artifacts/project_sync_report.md`

Required content:

- mode
- slug
- each lane executed/skipped
- gate outcomes per lane
- reason blocks for blocked/incomplete lanes
- references to lane reports generated
- final orchestration status (`blocked`, `incomplete`, `ready_for_operator_review`)
- explicit statement that no push/remote mutation occurred unless a future gated apply flow says otherwise

## 17. Failure Behavior

- Fail closed on missing passport or protected-project match.
- If `--stop-on-warning` is set, halt at first warning-level gate miss.
- Otherwise continue read-only checks and mark downstream as blocked/incomplete in report.
- Never continue into apply-capable lanes when required gates are failing.

## 18. Restart/Checkpoint Behavior

- Write orchestration report incrementally by lane or at least after each major stage.
- Include a checkpoint section:
- completed lanes
- blocked lanes
- pending lanes
- exact rerun command

This supports reliable resume after interruption.

## 19. Operator Approval Points

Explicit approval points for future apply-capable orchestration:

1. Obsidian sync apply
2. Export sync apply
3. Remote setup actions
4. Any push-related action

No approval, no apply.

## 20. Protected Project Handling

Always protected by default:

- Cerberus and Cerberus-related paths
- `reconciliation_required`
- `system_bound_project`
- `unknown`
- `review_required` unless future explicit approval model is added

Behavior:

- report as blocked with reason
- do not execute mutation lanes

## 21. Proposed Tests

- parser defaults (`dry-run`, slug requirements)
- lane sequencing order in dry-run mode
- protected-project immediate block behavior
- per-lane skip/blocked annotation accuracy
- combined report includes lane report references
- `--stop-on-warning` behavior
- no mutation side effects in dry-run mode
- aggregate status derivation correctness

## 22. Open Questions

1. Should `project-sync` default to running all lanes in dry-run, or only lanes explicitly requested by flags?
2. Should `--refresh-scan` be on by default, or only when explicitly requested?
3. How strict should lane dependency be (hard fail vs soft continue) when upstream evidence is stale?
4. Should `project-sync` generate one monolithic report only, or always require sub-reports plus summary?
5. For future apply mode, should there be a mandatory interactive approval step per lane even when `--apply` is provided?

## 23. Recommended Implementation Phases

### Phase 8.1: Orchestration Dry-Run Wrapper (Single Slug)

- Implement command parsing and lane orchestration state machine.
- Dry-run only.
- No apply and no remote mutations.

### Phase 8.2: Combined Reporting and Checkpointing

- Add robust combined report generation with lane-by-lane status.
- Add restart/checkpoint instructions and rerun snippets.

### Phase 8.3: Controlled Apply Hooks (Still Local/Docs Lanes First)

- Allow explicit apply for selected non-remote lanes only.
- Preserve per-lane gates and approval requirements.

### Phase 8.4: Remote-Aware Orchestration (Read-Only + Operator-Gated)

- Integrate remote plan/verify/push-ready lanes with stronger gate semantics.
- Keep push and remote setup manual and explicitly approved.

## Final Design Position

`project-sync` should begin as a **command board runner**, not a magical automation switch. It coordinates proven lanes, surfaces gate failures early, and prevents silent broad actions.
