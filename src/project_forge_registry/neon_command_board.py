"""Phase 11G static Neon District command board for Project Forge.

The board is local-first and display-only. It reads repo-local artifacts and
writes static HTML, a Markdown report, and a JSON manifest.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any


DEFAULT_INVENTORY_JSON = Path("artifacts/dashboard_inventory.json")
DEFAULT_DRY_RUN_JSON = Path("artifacts/obsidian_vault_apply_dry_run.json")
DEFAULT_PLAN_JSON = Path("artifacts/obsidian_vault_apply_plan.json")
DEFAULT_REAL_APPLY_REPORT = Path("artifacts/obsidian_vault_real_apply_report.md")
DEFAULT_MAINTENANCE_REPORT = Path("artifacts/obsidian_vault_maintenance_policy_report.md")
DEFAULT_OUTPUT_HTML = Path("artifacts/neon_command_board.html")
DEFAULT_REPORT_PATH = Path("artifacts/neon_command_board_report.md")
DEFAULT_MANIFEST_PATH = Path("artifacts/neon_command_board_manifest.json")

PHASE_STATE = "Phase 11G: Neon command board"
THEME_LABEL = "Neon District / Punk Union"

COMMAND_CARDS = [
    ("Cold Start", "./scripts/project-forge-cold-start"),
    ("Classic Dashboard", "./scripts/project-forge-dashboard --no-open"),
    ("Obsidian Artifact Mirror", "PYTHONPATH=src python3 -m project_forge_registry.obsidian_mirror"),
    ("Vault Apply Plan", "PYTHONPATH=src python3 -m project_forge_registry.obsidian_vault_plan"),
    ("Vault Dry-Run Review", "PYTHONPATH=src python3 -m project_forge_registry.obsidian_vault_apply --dry-run"),
    (
        "Plain Project Open Dry-Run",
        "./scripts/project-forge-open-project --slug lifesaver-ledger --profile plain --dry-run",
    ),
]

PANEL_NAMES = [
    "System State",
    "Project Inventory",
    "Obsidian Memory Layer",
    "Safety Doctrine",
    "Actions / Command Copy Cards",
    "Warnings / Blockers",
    "Phase Roadmap",
]


@dataclass(frozen=True, slots=True)
class BoardData:
    commit: str
    tag: str
    checkpoint: str
    repo_status: str
    inventory_summary: dict[str, int]
    vault_root: str
    vault_entries_reviewed: int
    vault_would_create: int
    vault_skip_identical: int
    vault_blocked: int
    artifact_mirror_status: str
    vault_plan_status: str
    real_apply_status: str
    maintenance_status: str
    warnings: tuple[str, ...]
    managed_notes: tuple[str, ...]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = repo_root() / candidate
    return candidate.resolve()


def html_escape(value: Any) -> str:
    return escape("" if value is None else str(value), quote=True)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def git_text(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root(),
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "unavailable"
    if result.returncode != 0:
        return "unavailable"
    return result.stdout.strip() or "none"


def git_status_short() -> str:
    status = git_text(["status", "--short"])
    if status in {"none", ""}:
        return "clean"
    if status == "unavailable":
        return status
    return "dirty"


def latest_matching_tag(pattern: str) -> str:
    tag = git_text(["tag", "--list", pattern, "--sort=-creatordate"])
    if tag in {"none", "unavailable"}:
        return tag
    return tag.splitlines()[0]


def projects(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_projects = payload.get("projects", [])
    return [project for project in raw_projects if isinstance(project, dict)]


def count_action(payload: dict[str, Any], action: str) -> int:
    return len([project for project in projects(payload) if project.get("recommended_action") == action])


def inventory_summary(payload: dict[str, Any]) -> dict[str, int]:
    all_projects = projects(payload)
    return {
        "total_projects": len(all_projects),
        "known_embedded": count_action(payload, "embedded_ready"),
        "dirty_review": count_action(payload, "dirty_review_first"),
        "protected_review": count_action(payload, "protected_manual_review"),
        "candidate_review": count_action(payload, "candidate_review"),
    }


def status_for_file(path: Path, label: str) -> str:
    return f"{label}: present" if path.exists() else f"{label}: missing"


def managed_notes_from_dry_run(payload: dict[str, Any]) -> tuple[str, ...]:
    names = []
    for entry in payload.get("entries", []):
        if isinstance(entry, dict):
            target_path = entry.get("target_path")
            if isinstance(target_path, str) and target_path:
                names.append(Path(target_path).name)
    return tuple(sorted(names))


def collect_board_data(
    *,
    inventory_json: Path,
    dry_run_json: Path,
    plan_json: Path,
    real_apply_report: Path,
    maintenance_report: Path,
) -> BoardData:
    inventory = read_json(inventory_json)
    dry_run = read_json(dry_run_json)
    summary = inventory_summary(inventory)
    status = git_status_short()
    checkpoint = latest_matching_tag("checkpoint-*-phase-11e-*")
    warnings: list[str] = []
    if status != "clean":
        warnings.append("dirty repo warning: working tree has local changes")
    if checkpoint in {"none", "unavailable"}:
        warnings.append("missing checkpoint warning: Phase 11E checkpoint not detected")
    if int(dry_run.get("blocked", 0) or 0) > 0:
        warnings.append("vault conflict warning: dry-run reports blocked entries")
    if summary["dirty_review"] > 0:
        warnings.append(f"dirty project review count: {summary['dirty_review']}")
    if summary["protected_review"] > 0:
        warnings.append(f"protected project review count: {summary['protected_review']}")
    if summary["candidate_review"] > 0:
        warnings.append(f"candidate project review count: {summary['candidate_review']}")

    vault_root = str(dry_run.get("vault_root") or read_json(plan_json).get("vault_root") or "unknown")
    return BoardData(
        commit=git_text(["log", "-1", "--oneline"]),
        tag=latest_matching_tag("v0.11.*"),
        checkpoint=checkpoint,
        repo_status=status,
        inventory_summary=summary,
        vault_root=vault_root,
        vault_entries_reviewed=int(dry_run.get("entries_reviewed", 0) or 0),
        vault_would_create=int(dry_run.get("would_create", 0) or 0),
        vault_skip_identical=int(dry_run.get("would_skip_identical", dry_run.get("would_skip", 0)) or 0),
        vault_blocked=int(dry_run.get("blocked", 0) or 0),
        artifact_mirror_status=status_for_file(resolve_repo_path("artifacts/obsidian_mirror_report.md"), "artifact mirror"),
        vault_plan_status=status_for_file(plan_json, "vault plan"),
        real_apply_status=status_for_file(real_apply_report, "real vault apply"),
        maintenance_status=status_for_file(maintenance_report, "maintenance/no-clobber policy"),
        warnings=tuple(warnings),
        managed_notes=managed_notes_from_dry_run(dry_run),
    )


def metric_card(label: str, value: Any, accent: str = "cyan") -> str:
    return f"""
<div class="metric accent-{html_escape(accent)}">
  <span>{html_escape(label)}</span>
  <strong>{html_escape(value)}</strong>
</div>
""".strip()


def status_row(label: str, value: Any) -> str:
    return f"""
<div class="status-row">
  <span>{html_escape(label)}</span>
  <code>{html_escape(value)}</code>
</div>
""".strip()


def command_card(label: str, command: str) -> str:
    return f"""
<article class="command-card">
  <span>{html_escape(label)}</span>
  <code>{html_escape(command)}</code>
</article>
""".strip()


def render_html(data: BoardData) -> str:
    summary = data.inventory_summary
    warnings = "\n".join(f"<li>{html_escape(warning)}</li>" for warning in data.warnings)
    if not warnings:
        warnings = "<li>No blockers detected in repo-local command board inputs.</li>"
    notes = "\n".join(f"<li>{html_escape(note)}</li>" for note in data.managed_notes)
    if not notes:
        notes = "<li>No managed note list detected.</li>"
    commands = "\n".join(command_card(label, command) for label, command in COMMAND_CARDS)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Project Forge Neon Command Board</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #08070d;
      --panel: #11101a;
      --panel-2: #171322;
      --line: rgba(37, 247, 255, 0.22);
      --text: #f5f0ff;
      --muted: #a7a0ba;
      --cyan: #25f7ff;
      --magenta: #ff3fd7;
      --violet: #9b5cff;
      --amber: #ffd166;
      --red: #ff3b5f;
      --green: #52ff9d;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        linear-gradient(180deg, rgba(37, 247, 255, 0.12), transparent 320px),
        linear-gradient(135deg, rgba(255, 63, 215, 0.14), transparent 42%),
        var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    .shell {{
      width: min(1460px, calc(100vw - 28px));
      margin: 0 auto;
      padding: 28px 0 54px;
    }}
    .hero {{
      min-height: 260px;
      display: grid;
      align-content: end;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 30px;
      background:
        linear-gradient(135deg, rgba(17, 16, 26, 0.96), rgba(23, 19, 34, 0.9)),
        repeating-linear-gradient(90deg, rgba(37, 247, 255, 0.08) 0 1px, transparent 1px 42px);
      box-shadow: 0 0 42px rgba(37, 247, 255, 0.16), inset 0 0 0 1px rgba(255,255,255,0.03);
    }}
    .eyebrow {{
      margin: 0 0 10px;
      color: var(--cyan);
      font-size: 0.78rem;
      font-weight: 900;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2.4rem, 6vw, 5.4rem);
      line-height: 0.95;
      letter-spacing: 0;
      text-shadow: 0 0 24px rgba(255, 63, 215, 0.26);
    }}
    .tagline {{
      max-width: 76ch;
      margin: 18px 0 0;
      color: var(--muted);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 14px;
      margin-top: 14px;
    }}
    section {{
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(17, 16, 26, 0.9);
      padding: 18px;
      box-shadow: 0 18px 42px rgba(0,0,0,0.34);
    }}
    .span-4 {{ grid-column: span 4; }}
    .span-6 {{ grid-column: span 6; }}
    .span-8 {{ grid-column: span 8; }}
    .span-12 {{ grid-column: span 12; }}
    h2 {{
      margin: 0 0 14px;
      color: var(--cyan);
      font-size: 0.95rem;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .metric {{
      min-height: 92px;
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 8px;
      padding: 14px;
      background: rgba(8, 7, 13, 0.62);
    }}
    .metric span, .command-card span {{
      display: block;
      color: var(--muted);
      font-size: 0.72rem;
      font-weight: 900;
      text-transform: uppercase;
    }}
    .metric strong {{
      display: block;
      margin-top: 12px;
      font-size: 2.1rem;
      line-height: 1;
    }}
    .accent-cyan strong {{ color: var(--cyan); }}
    .accent-magenta strong {{ color: var(--magenta); }}
    .accent-violet strong {{ color: var(--violet); }}
    .accent-amber strong {{ color: var(--amber); }}
    .accent-red strong {{ color: var(--red); }}
    .accent-green strong {{ color: var(--green); }}
    .status-list {{
      display: grid;
      gap: 8px;
    }}
    .status-row {{
      display: grid;
      grid-template-columns: minmax(120px, 0.38fr) minmax(0, 1fr);
      gap: 10px;
      align-items: start;
    }}
    .status-row span {{
      color: var(--muted);
      font-size: 0.72rem;
      font-weight: 900;
      text-transform: uppercase;
    }}
    code {{
      display: block;
      min-width: 0;
      padding: 9px 10px;
      border: 1px solid rgba(37, 247, 255, 0.16);
      border-radius: 6px;
      background: rgba(8, 7, 13, 0.9);
      color: #ecfaff;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-size: 0.82rem;
    }}
    ul {{
      margin: 0;
      padding-left: 18px;
      color: var(--text);
    }}
    li + li {{ margin-top: 8px; }}
    .doctrine li::marker {{ color: var(--amber); }}
    .warnings li::marker {{ color: var(--red); }}
    .command-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .command-card {{
      min-width: 0;
      border: 1px solid rgba(255, 63, 215, 0.18);
      border-radius: 8px;
      padding: 14px;
      background: rgba(23, 19, 34, 0.78);
    }}
    .command-card code {{ margin-top: 8px; }}
    .roadmap {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }}
    .roadmap div {{
      border: 1px solid rgba(155, 92, 255, 0.22);
      border-radius: 8px;
      padding: 14px;
      background: rgba(8, 7, 13, 0.58);
    }}
    .roadmap strong {{ color: var(--violet); }}
    .safety-note {{
      color: var(--muted);
      margin: 12px 0 0;
    }}
    @media (max-width: 980px) {{
      .span-4, .span-6, .span-8 {{ grid-column: span 12; }}
      .command-grid, .roadmap {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 620px) {{
      .shell {{ width: min(100vw - 18px, 1460px); padding-top: 18px; }}
      .hero, section {{ padding: 16px; }}
      .metric-grid {{ grid-template-columns: 1fr; }}
      .status-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <p class="eyebrow">{THEME_LABEL} / local-first operator cockpit</p>
      <h1>Project Forge Neon Command Board</h1>
      <p class="tagline">A beautiful system with teeth: readable state, copy-paste commands, sharp warnings, and no hidden actions.</p>
    </header>

    <div class="grid">
      <section class="span-6">
        <h2>System State</h2>
        <div class="status-list">
          {status_row("current commit", data.commit)}
          {status_row("latest tag", data.tag)}
          {status_row("checkpoint", data.checkpoint)}
          {status_row("repo status", data.repo_status)}
          {status_row("phase", PHASE_STATE)}
        </div>
      </section>

      <section class="span-6">
        <h2>Project Inventory</h2>
        <div class="metric-grid">
          {metric_card("total projects", summary["total_projects"], "cyan")}
          {metric_card("known embedded", summary["known_embedded"], "green")}
          {metric_card("dirty review", summary["dirty_review"], "amber")}
          {metric_card("protected review", summary["protected_review"], "red")}
          {metric_card("candidate review", summary["candidate_review"], "magenta")}
          {metric_card("source", "dashboard_inventory.json", "violet")}
        </div>
      </section>

      <section class="span-8">
        <h2>Obsidian Memory Layer</h2>
        <div class="status-list">
          {status_row("artifact mirror status", data.artifact_mirror_status)}
          {status_row("vault plan status", data.vault_plan_status)}
          {status_row("real vault apply status", data.real_apply_status)}
          {status_row("maintenance/no-clobber policy status", data.maintenance_status)}
          {status_row("vault root path", data.vault_root)}
          {status_row("steady state", f"{data.vault_entries_reviewed} notes reviewed; {data.vault_skip_identical} skip-identical; {data.vault_would_create} create; {data.vault_blocked} blocked")}
        </div>
      </section>

      <section class="span-4">
        <h2>Managed Vault Notes</h2>
        <ul>{notes}</ul>
      </section>

      <section class="span-6 doctrine">
        <h2>Safety Doctrine</h2>
        <ul>
          <li>dry-run first</li>
          <li>create-only</li>
          <li>skip identical</li>
          <li>block different</li>
          <li>human-edited vault notes win</li>
          <li>no silent overwrite</li>
          <li>no delete</li>
        </ul>
      </section>

      <section class="span-6 warnings">
        <h2>Warnings / Blockers</h2>
        <ul>{warnings}</ul>
      </section>

      <section class="span-12">
        <h2>Actions / Command Copy Cards</h2>
        <div class="command-grid">{commands}</div>
        <p class="safety-note">These are copy-paste commands only. The real guarded vault write command is not shown; operator approval is required.</p>
      </section>

      <section class="span-12">
        <h2>Phase Roadmap</h2>
        <div class="roadmap">
          <div><strong>Phase 11G:</strong> Neon command board.</div>
          <div><strong>Phase 11H:</strong> launcher/autostart replacement for old Recon Command Board.</div>
          <div><strong>Future:</strong> backup-before-update, manual merge workflow, no-clobber update tooling.</div>
        </div>
      </section>
    </div>
  </main>
</body>
</html>
"""


def render_report(data: BoardData) -> str:
    warnings = "\n".join(f"- {warning}" for warning in data.warnings) or "- none"
    return f"""# Project Forge Neon Command Board Report

## Mode

static local command board

## Theme

{THEME_LABEL}

## Panels Generated

{chr(10).join(f"- {panel}" for panel in PANEL_NAMES)}

## System State

- current commit: `{data.commit}`
- latest meaningful tag: `{data.tag}`
- latest checkpoint: `{data.checkpoint}`
- repo status: `{data.repo_status}`
- phase: `{PHASE_STATE}`

## Project Inventory

- total projects: `{data.inventory_summary["total_projects"]}`
- known embedded: `{data.inventory_summary["known_embedded"]}`
- dirty review: `{data.inventory_summary["dirty_review"]}`
- protected review: `{data.inventory_summary["protected_review"]}`
- candidate review: `{data.inventory_summary["candidate_review"]}`
- source: `artifacts/dashboard_inventory.json`

## Obsidian Memory Layer

- artifact mirror status: `{data.artifact_mirror_status}`
- vault plan status: `{data.vault_plan_status}`
- real vault apply status: `{data.real_apply_status}`
- maintenance/no-clobber policy status: `{data.maintenance_status}`
- vault root path: `{data.vault_root}`
- steady state: `{data.vault_entries_reviewed}` notes reviewed, `{data.vault_skip_identical}` skip-identical, `{data.vault_blocked}` blocked

## Safety Doctrine

- dry-run first
- create-only
- skip identical
- block different
- human-edited vault notes win
- no silent overwrite
- no delete

## Warnings / Blockers

{warnings}

## Safety Confirmation

The generated frontend is static HTML/CSS with no JavaScript, no executable
buttons, no shell execution, no URL launch controls, no mutation actions, no
real vault writes, no marker writes, no remotes, no package installs, and no
network calls.
"""


def write_manifest(path: Path, data: BoardData) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_by": "project_forge_registry.neon_command_board",
        "mode": "static local command board",
        "theme": THEME_LABEL,
        "phase": PHASE_STATE,
        "panels_generated": PANEL_NAMES,
        "outputs": {
            "html": str(DEFAULT_OUTPUT_HTML),
            "report": str(DEFAULT_REPORT_PATH),
            "manifest": str(DEFAULT_MANIFEST_PATH),
        },
        "system_state": {
            "commit": data.commit,
            "latest_tag": data.tag,
            "checkpoint": data.checkpoint,
            "repo_status": data.repo_status,
        },
        "project_inventory": data.inventory_summary,
        "obsidian_memory_layer": {
            "vault_root": data.vault_root,
            "entries_reviewed": data.vault_entries_reviewed,
            "would_create": data.vault_would_create,
            "skip_identical": data.vault_skip_identical,
            "blocked": data.vault_blocked,
            "managed_notes": list(data.managed_notes),
        },
        "safety": {
            "display_only": True,
            "javascript": False,
            "executes_shell_commands": False,
            "mutates_state": False,
            "real_vault_writes": False,
            "external_repo_writes": False,
            "remotes_push_fetch": False,
            "network_calls": False,
            "vs_code_launch": False,
            "autostart_replacement": False,
        },
        "warnings": list(data.warnings),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_neon_command_board(
    *,
    inventory_json: Path = DEFAULT_INVENTORY_JSON,
    dry_run_json: Path = DEFAULT_DRY_RUN_JSON,
    plan_json: Path = DEFAULT_PLAN_JSON,
    real_apply_report: Path = DEFAULT_REAL_APPLY_REPORT,
    maintenance_report: Path = DEFAULT_MAINTENANCE_REPORT,
    output_html: Path = DEFAULT_OUTPUT_HTML,
    report_path: Path = DEFAULT_REPORT_PATH,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
) -> BoardData:
    data = collect_board_data(
        inventory_json=resolve_repo_path(inventory_json),
        dry_run_json=resolve_repo_path(dry_run_json),
        plan_json=resolve_repo_path(plan_json),
        real_apply_report=resolve_repo_path(real_apply_report),
        maintenance_report=resolve_repo_path(maintenance_report),
    )
    output_html = resolve_repo_path(output_html)
    report_path = resolve_repo_path(report_path)
    manifest_path = resolve_repo_path(manifest_path)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(render_html(data), encoding="utf-8")
    report_path.write_text(render_report(data), encoding="utf-8")
    write_manifest(manifest_path, data)
    return data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-neon-command-board")
    parser.add_argument("--inventory-json", default=str(DEFAULT_INVENTORY_JSON))
    parser.add_argument("--dry-run-json", default=str(DEFAULT_DRY_RUN_JSON))
    parser.add_argument("--plan-json", default=str(DEFAULT_PLAN_JSON))
    parser.add_argument("--real-apply-report", default=str(DEFAULT_REAL_APPLY_REPORT))
    parser.add_argument("--maintenance-report", default=str(DEFAULT_MAINTENANCE_REPORT))
    parser.add_argument("--output-html", default=str(DEFAULT_OUTPUT_HTML))
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST_PATH))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    data = run_neon_command_board(
        inventory_json=Path(args.inventory_json),
        dry_run_json=Path(args.dry_run_json),
        plan_json=Path(args.plan_json),
        real_apply_report=Path(args.real_apply_report),
        maintenance_report=Path(args.maintenance_report),
        output_html=Path(args.output_html),
        report_path=Path(args.report_path),
        manifest_path=Path(args.manifest_path),
    )
    print("project-forge-neon-command-board completed")
    print("mode: static local command board")
    print(f"output html path: {resolve_repo_path(args.output_html)}")
    print(f"report path: {resolve_repo_path(args.report_path)}")
    print(f"manifest path: {resolve_repo_path(args.manifest_path)}")
    print(f"panels generated: {', '.join(PANEL_NAMES)}")
    print("safety confirmation: static display-only; no JavaScript; no command execution; no vault writes")
    print(f"repo status: {data.repo_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
