# Project Forge Dashboard Inventory

## Purpose

The dashboard inventory command builds a read-only dashboard feed from existing
Project Forge artifacts.

It produces:

- `artifacts/dashboard_inventory.json`
- `artifacts/dashboard_inventory_report.md`

The feed contains one project record per discovered repo.

## Command

Run:

    PYTHONPATH=src python3 -m project_forge_registry.dashboard_inventory

Optional paths:

    PYTHONPATH=src python3 -m project_forge_registry.dashboard_inventory \
      --repo-discovery-csv artifacts/repo_discovery_inventory.csv \
      --embed-plan-csv artifacts/embed_plan_inventory.csv \
      --json-path artifacts/dashboard_inventory.json \
      --report-path artifacts/dashboard_inventory_report.md

## Inputs

Required:

- `artifacts/repo_discovery_inventory.csv`

Optional:

- `artifacts/embed_plan_inventory.csv`
- `artifacts/tool_readiness_report.md`
- `artifacts/project_sync_report.md`

The optional reports are linked for dashboard navigation. Missing optional
artifacts do not block inventory generation when discovery data exists.

## Project Record Fields

Each project record includes:

- `slug`
- `path`
- `category`
- `git_status`
- `has_readme`
- `has_agents`
- `has_code_workspace`
- `has_project_forge_marker`
- `remote_count`
- `embed_decision`
- `repo_light`
- `docs_light`
- `risk_light`
- `overall_status`
- `recommended_action`
- `vscode_target`
- `marker_yaml_path`
- `marker_doc_path`
- `report_links`

## Light Model

### Repo Light

- `green`: clean `known_embedded` or clean `clean_candidate`
- `amber`: dirty candidates or dirty repos
- `blue`: Project Forge control repo
- `red`: unknown or problem states

### Docs Light

- `green`: Project Forge marker or docs marker exists
- `amber`: README exists but no Project Forge marker exists
- `gray`: no README or Project Forge marker was detected

### Risk Light

- `green`: clean `known_embedded` repos and clean candidates
- `amber`: dirty repos or clean candidates with existing remotes needing review
- `red`: protected manual review repos
- `blue`: Project Forge control repo

## Recommended Actions

- `embedded_ready`
- `candidate_review`
- `dirty_review_first`
- `protected_manual_review`
- `control_repo_no_embed`
- `unknown_review`

## VS Code Target

`vscode_target` is the repo path by default.

If a `.code-workspace` file exists in the repo root, the first deterministic
workspace path is used instead.

The dashboard inventory phase does not launch VS Code.

## Safety

The command is read-only.

It does not:

- write external repos
- apply changes
- write marker files
- add or modify remotes
- push or fetch
- contact GitHub or Codeberg
- install packages
- handle Cerberus beyond reporting existing discovery categories
