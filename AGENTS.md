# AGENTS.md

## Mission

This repository is the safety-first operational registry for technical projects,
repositories, deployment nodes, mirrors, workspaces, and machine readiness.

`PROJECT_CHARTER.md` is the canonical mission and authority boundary. Read it
before proposing architecture, roadmap, dashboard, integration, or scope changes.

`docs/REPOSITORY_LIFECYCLE_STANDARD.md` defines the compliance and archive gate
for repositories materially reviewed through Project Forge or C2 reconciliation.

Project Forge does not own personal planning, weekly prioritization, calendars,
or the complete roadmaps of other projects. Those boundaries must remain visible
in current-facing documentation and operator surfaces.

## Core Rules

- Follow `PROJECT_CHARTER.md`; do not silently broaden Project Forge into a universal planner or personal operating system.
- Apply `docs/REPOSITORY_LIFECYCLE_STANDARD.md` to any repository materially reviewed: leave it compliant with an explicit lifecycle status or archive/supersede it with preservation evidence.
- Do not leave reviewed repositories in an ambiguous merely-unarchived state.
- Treat “command center” as a technical operator-surface label only, not a grant of planning authority.
- Dry-run first.
- Never push, mirror, or configure remotes without explicit user approval.
- Never copy code into Obsidian.
- Treat `/home/cole/main_vault/10 Projects/<project-slug>` as the only canonical Obsidian project mirror path.
- Never overwrite files without backups.
- Prefer additive changes over in-place mutation.
- Produce reports before applying changes.
- Do not modify scanned project folders during discovery phases.
- Do not initialize git in existing folders during discovery phases.
- Treat secrets, env files, and database files as sensitive by default.
- Treat `system_bound_project` as non-movable and excluded from bulk sync automation by default.
- Treat `reconciliation_required` as compare-only, non-deletable, and non-mergeable by default.
- Treat Cerberus as a special case: `/home/cole/cerberus` is system-bound, `/mnt/storage/Cole/cerberus` is reconciliation-required, neither should receive automated move/delete behavior, and neither should receive GitHub or Codeberg sync automation at this phase.
- For Cerberus Obsidian material, allow only high-level notes: `project home`, `workspace map`, `runbook index`, and `reconciliation note`.
- Never copy Cerberus `recon/raw`, `recon/cases`, `exports`, `logs`, `databases`, or operational files into Obsidian.

## Authority Boundaries

- Project Forge owns technical discovery, classification, readiness, repository compliance reporting, and guarded technical operator workflows.
- Individual repositories and verified runtime state own technical roadmaps and implementation truth.
- Todoist owns immediate actionable commitments.
- Google Calendar owns fixed time commitments.
- The Sunday Outlook/C2 process owns cross-system prioritization and reconciliation.
- Obsidian owns durable context, decisions, learning, and doctrine.
- ChatGPT conversations provide intelligence and history, not permanent project authority.

## Expected Agent Behavior

- Start by reading `PROJECT_CHARTER.md`, `PROJECT_STATUS.md`, `docs/REPOSITORY_LIFECYCLE_STANDARD.md`, existing docs, and generated artifacts.
- When a repository is materially discussed, identify its canonical repo, assign a lifecycle status, and complete either the retrofit gate or the archive/supersession gate before calling it reconciled.
- Keep scanning and proposal steps read-only against user project directories.
- Write outputs to this repository unless the user explicitly approves a broader scope.
- When proposing Obsidian paths, always use `/home/cole/main_vault/10 Projects/<project-slug>`.
- Flag risky folders for manual review instead of guessing.
- Favor simple, inspectable formats and minimal dependencies.
- If a scanned path matches a known special-case constraint, preserve the exact override in generated proposals and reports.
- Reject scope expansion based only on convenience; require the decision process defined in `PROJECT_CHARTER.md`.
- Do not equate repository lifecycle with immediate personal priority; compliant active repositories do not automatically enter Todoist.

## Implementation Preferences

- Python 3.13 compatible.
- Prefer `argparse`, `pathlib`, `json`, and standard library tools.
- If YAML support is needed, prefer a small safe writer unless a dependency is explicitly approved.
