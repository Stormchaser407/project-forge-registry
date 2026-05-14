# SITREP 2026-05-14 Phase 6 Remote Policy Design

This document records the Phase 6 design for GitHub + Codeberg remote governance in Project Forge Registry.

This is design-only. It does not authorize remote creation, remote modification, pushes, repository creation, or external sync actions.

## 1. Purpose

- Define safety gates and policy defaults for future remote operations.
- Establish GitHub as primary collaboration workspace and Codeberg as resilience mirror policy.
- Ensure remote actions are explicit, auditable, and approval-driven.

## 2. Non-Goals

- No implementation of remote commands in this phase.
- No adding/modifying/removing remotes.
- No push/pull/fetch side effects.
- No GitHub/Codeberg repo creation.
- No broad multi-project sync execution.

## 3. Current Assumptions

- Local repo remains operational source of truth unless explicitly configured otherwise.
- GitHub is intended for collaboration and agent workflows.
- Codeberg is intended for resilience/mirror posture.
- Existing safety model is dry-run-first and report-first.

## 4. Remote Model

Target architecture (future, policy-governed):

- local repo <-> GitHub primary
- local repo -> Codeberg mirror

Phase 6 scope is policy and gates only.

## 5. Project Eligibility Rules

Eligible by default (future remote enablement candidates):

- `active_project`
- `operated_tool`

Additional baseline checks:

- passport exists and validates
- project path exists
- no Cerberus relationship
- no forced safety flags (`do_not_sync`, `allow_secrets`, `allow_code_to_obsidian`)
- explicit operator approval recorded for remote setup/push-ready

## 6. Forbidden/Protected Project Rules

Always protected by default:

- Cerberus and Cerberus-related paths
- `reconciliation_required`
- `system_bound_project`
- `unknown`
- `registry_action=review_required`

Protected projects must be skipped with explicit reasons in reports.

## 7. Visibility Policy

Defaults:

- GitHub visibility: `private`
- Codeberg visibility: `private`

No public visibility assumptions. Public readiness must be explicitly declared and approved per project.

## 8. Naming Policy

Defaults:

- GitHub remote name: `origin`
- Codeberg remote name: `codeberg`
- default branch: `main`

Repository naming should prefer passport slug normalization unless explicitly overridden.

## 9. GitHub Policy

- GitHub is the primary collaboration remote.
- Remote setup must be explicit and report-driven.
- No force-push policy.
- No history rewrite policy in automation lanes.
- Pushes disabled by default until push-ready gates pass.

## 10. Codeberg Policy

- Codeberg is resilience mirror by policy default.
- Must not be treated as an automatic public release channel.
- Pushes to Codeberg require explicit approval and push-ready status.
- Mirror mode must be declared in reports (`disabled`, `planned`, `approved`, `active`).

## 11. Branch Policy

- Default branch: `main`.
- No automated branch deletion.
- No automated branch rewriting.
- Optional future support: protected branch checks before push-ready.

## 12. Commit/Push Safety Checks

Before any push-ready status can be reported:

- working tree must be clean
- required tests must pass
- required docs/sync reports must be current
- project must be eligible and approved
- no protected-project conditions

Push behavior in initial implementation:

- never automatic
- always explicit user-confirmed action

## 13. Secret/Sensitive-File Checks

Never push:

- `.env*`
- secrets/tokens/credentials
- logs
- databases
- caches
- raw operational data

Required safeguards (future implementation):

- denylist path/extension scanner
- optional content heuristics for credential-like patterns
- report of blocked files and reasons

## 14. Obsidian/Docs Sync Relationship

Push-ready status should require current documentation sync evidence:

- latest Obsidian mirror sync report (Phase 4b) status
- latest `_export -> repo docs` report (Phase 5 lane) status

Policy intent:

- remote readiness should reflect documentation hygiene, not only code/test state.

## 15. Proposed Passport Additions

Suggested fields (future schema revision):

- `git.github_enabled: bool`
- `git.codeberg_enabled: bool`
- `git.github_remote_name: string` (default `origin`)
- `git.codeberg_remote_name: string` (default `codeberg`)
- `git.default_branch: string` (default `main`)
- `git.visibility_github: private|public`
- `git.visibility_codeberg: private|public`
- `git.remote_policy_state: disabled|planned|approved|active`
- `git.push_policy: manual_only|approved_manual`
- `git.requires_push_ready_report: bool`

## 16. Proposed Command Names

- `project-forge-remote-plan`
- `project-forge-remote-verify`
- `project-forge-remote-setup`
- `project-forge-push-ready`

## 17. Proposed CLI Options

### `project-forge-remote-plan`

- `--slug <slug>`
- `--passport-dir <path>`
- `--report-name <filename>`
- `--dry-run`

### `project-forge-remote-verify`

- `--slug <slug>`
- `--passport-dir <path>`
- `--require-clean-tree`
- `--require-tests-pass`
- `--require-doc-reports-current`
- `--report-name <filename>`

### `project-forge-remote-setup`

- `--slug <slug>`
- `--github-remote-name <name>`
- `--codeberg-remote-name <name>`
- `--github-url <url>`
- `--codeberg-url <url>`
- `--dry-run`
- `--apply`

### `project-forge-push-ready`

- `--slug <slug>`
- `--passport-dir <path>`
- `--report-name <filename>`
- `--dry-run`

## 18. Proposed Reports

Default artifact candidates:

- `artifacts/remote_plan_report.md`
- `artifacts/remote_verify_report.md`
- `artifacts/remote_setup_report.md`
- `artifacts/push_ready_report.md`

Each report should include:

- mode
- slug
- passport file used
- eligibility and skip reasons
- remote intent/state
- safety checks passed/failed
- required approvals present/missing
- recommended next action

## 19. Proposed Tests

- parser defaults to dry-run for planning commands
- eligibility filtering by category and registry action
- Cerberus hard-protection checks
- clean-tree prerequisite checks
- tests-pass prerequisite checks
- docs-report freshness prerequisite checks
- remote-name policy defaults (`origin`, `codeberg`)
- default branch policy (`main`)
- sensitive file gate behavior
- push-ready report correctness for pass/fail paths

## 20. Operator Approval Gates

Minimum approval gates before any push command is considered:

1. Project explicitly approved for remote policy activation.
2. Working tree clean.
3. Required tests pass.
4. Documentation sync reports current.
5. Sensitive file scan clear.
6. Push-ready report reviewed and approved.

No gate, no push.

## 21. Open Questions

1. Codeberg strategy:
- A: independent second remote pushed directly from local
- B: mirror managed from GitHub
- C: support both, default to local dual-push only after explicit approval

Safest default recommendation:

- C, with staged rollout policy:
- start with planning support for both models
- default operational state remains `manual_only` and disabled until explicit approval
- initial implementation should require per-slug approval before any dual-push behavior

2. Should push-ready require both GitHub and Codeberg configured, or allow GitHub-only readiness?

3. Should public visibility ever be allowed by default for any category?

4. How strict should docs-report freshness be (timestamp threshold vs latest-run marker)?

## 22. Recommended Implementation Phases

### Phase 6.1: Planner + Verify (No Remote Mutation)

- Implement `project-forge-remote-plan` and `project-forge-remote-verify`.
- Dry-run/report-only.
- No remote add/change/push.

### Phase 6.2: Controlled Remote Setup (Dry-Run First)

- Implement `project-forge-remote-setup` with strict path/project gating.
- Apply mode requires explicit user approval each run.

### Phase 6.3: Push-Ready Reporting

- Implement `project-forge-push-ready` evaluation.
- Report-only output; still no automatic push behavior.

### Phase 6.4: Optional Manual Push Orchestration

- Add explicit operator-triggered push commands only after policy review.
- Maintain no-force, no-rewrite, no-protected-project guarantees.

## Status

- Phase 6 remote policy design recorded.
- No remote operations performed.
- No external remote systems touched by this document.
