"""Project Forge static dashboard renderer.

This module renders the dashboard inventory JSON into a self-contained local
HTML command board. It is intentionally operator-safe:
- no server
- no JavaScript file actions
- no external assets
- no external repo writes
- no apply or marker writes
"""

from __future__ import annotations

import argparse
import json
import shlex
from html import escape
from pathlib import Path
from typing import Any


DEFAULT_INVENTORY_JSON = Path("artifacts/dashboard_inventory.json")
DEFAULT_OUTPUT_HTML = Path("artifacts/dashboard.html")
REPO_ROOT = Path(__file__).resolve().parents[2]

LOCAL_REPORT_LINKS = [
    ("dashboard_inventory_report.md", "Dashboard inventory"),
    ("repo_discovery_report.md", "Repo discovery"),
    ("embed_plan_report.md", "Embed plan"),
    ("tool_readiness_report.md", "Tool readiness"),
    ("project_sync_report.md", "Project sync"),
]

TERM_DEFINITIONS = {
    "repo_light": "Repo light summarizes git/project state. Green is clean or embedded, amber needs review, red is blocked or unknown, and blue marks the control repo lane.",
    "docs_light": "Docs light summarizes documentation readiness. Green means a Project Forge marker exists, amber means README-only, and gray means docs were not detected.",
    "risk_light": "Risk light is the conservative operator warning level. Red and amber mean review before action.",
    "path": "Path is the local filesystem location Project Forge discovered for the project.",
    "category": "Category is the scanner's conservative bucket for the project, such as known embedded, clean candidate, protected, or control repo.",
    "overall_status": "Overall is the current summarized readiness state for the project in this dashboard feed.",
    "recommended_action": "Action is the next safe operator posture Project Forge recommends for this project.",
    "review_commands": "Review commands are local terminal commands for inspecting dirty repos before launch or commit.",
    "commit_preflight": "Commit preflight reports changed and sensitive-looking paths without staging or committing files.",
    "commit_template": "Commit template is intentionally a command you review in a terminal. It requires explicit confirmation flags and an edited message.",
    "scan_rebuild": "Scan and rebuild refreshes repo discovery first, then rebuilds dashboard inventory and HTML so stale dirty counts update after commits.",
    "dashboard_refresh": "Dashboard refresh rebuilds the HTML from the current discovery inventory. It does not rescan repo git status.",
    "embedded_ready": "Embedded ready means the project is already known to Project Forge and can show dry-run launch commands.",
    "candidate_review": "Candidate review means the project looks promising but still needs operator review before deeper automation.",
    "dirty_review_first": "Dirty review first means the project has uncommitted or uncertain local state. Review it manually before any launch or sync path.",
    "protected_manual_review": "Protected manual review means Project Forge intentionally blocks automation because the project is sensitive, system-bound, or otherwise special.",
    "control_repo_no_embed": "Control repo means this Project Forge repository itself. It stays restricted so the control plane does not accidentally manage itself.",
    "unknown_review": "Unknown review means Project Forge does not have enough safe context yet. Treat it as blocked until a human reviews it.",
    "dry_run": "Dry-run means report and preview only. It should not mutate project folders, remotes, vault files, or desktop entries.",
    "codex_home": "CODEX_HOME points Codex profile-aware launches at a specific local profile home. Profile isolation is still treated as a research boundary.",
    "vscode_target": "VS Code target is the folder or workspace file Project Forge would use for a planned editor launch.",
    "marker_yaml": "Marker YAML is the machine-readable Project Forge marker proposed or detected for a project.",
    "marker_doc": "Marker doc is the human-readable Project Forge marker note proposed or detected for a project.",
}

def term_key_for_label(label: str) -> str | None:
    return {
        "repo": "repo_light",
        "docs": "docs_light",
        "risk": "risk_light",
        "path": "path",
        "category": "category",
        "overall": "overall_status",
        "action": "recommended_action",
        "vscode target": "vscode_target",
        "marker yaml": "marker_yaml",
        "marker doc": "marker_doc",
        "review commands": "review_commands",
        "scan + rebuild": "scan_rebuild",
        "dashboard refresh": "dashboard_refresh",
        "dry-run": "dry_run",
        "CODEX_HOME": "codex_home",
    }.get(label)


def render_term(label: str, key: str | None = None) -> str:
    term_key = key or term_key_for_label(label)
    text = html_escape(label)
    if not term_key or term_key not in TERM_DEFINITIONS:
        return text
    definition = html_escape(TERM_DEFINITIONS[term_key])
    return (
        f'<button class="term-button" type="button" data-explain="{html_escape(term_key)}" '
        f'title="{definition}" aria-label="Explain {text}">{text}</button>'
    )


def render_term_span(label: str, key: str) -> str:
    definition = html_escape(TERM_DEFINITIONS[key])
    return (
        f'<span class="term-inline" data-explain="{html_escape(key)}" '
        f'title="{definition}">{html_escape(label)}</span>'
    )


def load_dashboard_inventory(json_path: Path) -> dict[str, Any]:
    """Load the required dashboard inventory JSON."""
    if not json_path.exists():
        raise FileNotFoundError(f"Dashboard inventory JSON not found: {json_path}")

    with json_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Dashboard inventory JSON must contain an object")
    projects = payload.get("projects")
    if not isinstance(projects, list):
        raise ValueError("Dashboard inventory JSON must contain a projects list")
    return payload


def html_escape(value: Any) -> str:
    return escape("" if value is None else str(value), quote=True)


def projects(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        project
        for project in payload.get("projects", [])
        if isinstance(project, dict)
    ]


def projects_by_action(
    payload: dict[str, Any],
    action: str,
) -> list[dict[str, Any]]:
    return [
        project
        for project in projects(payload)
        if project.get("recommended_action") == action
    ]


def derive_summary(payload: dict[str, Any]) -> dict[str, int]:
    all_projects = projects(payload)
    return {
        "total_projects": len(all_projects),
        "known_embedded": len(projects_by_action(payload, "embedded_ready")),
        "dirty_review": len(projects_by_action(payload, "dirty_review_first")),
        "protected_review": len(
            projects_by_action(payload, "protected_manual_review")
        ),
        "candidate_review": len(projects_by_action(payload, "candidate_review")),
        "control_repo": len(projects_by_action(payload, "control_repo_no_embed")),
        "blocked_other": len(projects_by_action(payload, "unknown_review")),
    }


def css_class_token(value: Any) -> str:
    text = str(value or "unknown").lower()
    allowed = []
    for char in text:
        if char.isalnum() or char in {"-", "_"}:
            allowed.append(char)
        else:
            allowed.append("-")
    return "".join(allowed) or "unknown"


def render_status_light(label: str, color: Any) -> str:
    color_token = css_class_token(color)
    return (
        f'<span class="light-pair">'
        f'<span class="status-light light-{color_token}" aria-hidden="true"></span>'
        f'<span>{render_term(label)}: {html_escape(color)}</span>'
        f"</span>"
    )


def render_detail(label: str, value: Any) -> str:
    text = html_escape(value)
    if not text:
        text = "n/a"
    return (
        f'<div class="detail-row">'
        f'<span class="detail-label">{render_term(label)}</span>'
        f'<span class="detail-value">{text}</span>'
        f"</div>"
    )


def render_launch_panel(project: dict[str, Any]) -> str:
    policy = project.get("launch_policy")
    if not isinstance(policy, dict):
        return (
            '<section class="launch-panel">'
            '<h4>Launch Commands</h4>'
            '<p class="launch-blocked">Launch blocked by policy: unavailable.</p>'
            "</section>"
        )

    status = str(policy.get("status") or "blocked")
    message = html_escape(policy.get("message") or "Launch blocked by policy.")
    commands = project.get("launch_commands")

    if status == "eligible" and isinstance(commands, dict):
        rows: list[str] = []
        for label, detail, key in (
            ("Personal", f'{render_term("CODEX_HOME")} ~/.codex-personal', "personal"),
            ("Business", f'{render_term("CODEX_HOME")} ~/.codex-business', "business"),
            ("Plain", f'no {render_term("CODEX_HOME")}', "plain"),
        ):
            command = html_escape(commands.get(key) or "")
            command_attr = html_escape(commands.get(key) or "")
            rows.append(
                f'<div class="launch-row">'
                f'<div class="launch-row-top">'
                f'<span class="launch-label">{html_escape(label)} / {detail}</span>'
                f'<button class="copy-button" type="button" data-copy="{command_attr}" '
                f'title="Copy {html_escape(label)} dry-run command" '
                f'aria-label="Copy {html_escape(label)} dry-run command">Copy</button>'
                f"</div>"
                f'<code>{command}</code>'
                f"</div>"
            )
        commands_html = "\n".join(rows)
        return f"""
<section class="launch-panel">
  <h4>Copy-Paste Launch Commands</h4>
  <p class="launch-note">{render_term("dry-run", "dry_run")} only. Review output before manual open.</p>
  <div class="launch-grid">
    {commands_html}
  </div>
</section>
""".strip()

    return f"""
<section class="launch-panel">
  <h4>Copy-Paste Launch Commands</h4>
  <p class="launch-blocked">{message}</p>
</section>
""".strip()


def render_review_panel(project: dict[str, Any]) -> str:
    policy = project.get("review_policy")
    commands = project.get("review_commands")
    if not isinstance(policy, dict) or not isinstance(commands, dict) or not commands:
        return ""

    status = str(policy.get("status") or "not_required")
    message = html_escape(policy.get("message") or "")
    if status != "review_available":
        return ""

    labels = [
        ("Status", "git status summary", "status", "Inspect current git status"),
        ("Diff", "changed files", "diff", "Inspect unstaged/staged diff summary"),
        ("Log", "recent commits", "log", "Inspect recent commits"),
        ("Preflight", "commit dry-run", "commit_preflight", "Preview commit safety checks"),
        ("Commit", "template", "commit_template", "Copy guarded commit command template"),
    ]
    rows = []
    for label, detail, key, title in labels:
        command = html_escape(commands.get(key) or "")
        if not command:
            continue
        detail_html = render_term(detail, key) if key in {"commit_preflight", "commit_template"} else html_escape(detail)
        rows.append(
            f'<div class="review-row">'
            f'<div class="review-row-top">'
            f'<span class="review-label">{html_escape(label)} / {detail_html}</span>'
            f'<button class="copy-button" type="button" data-copy="{command}" '
            f'title="{html_escape(title)}" aria-label="{html_escape(title)}">Copy</button>'
            f"</div>"
            f"<code>{command}</code>"
            f"</div>"
        )

    return f"""
<section class="review-panel">
  <h4>{render_term("review commands", "review_commands")}</h4>
  <p class="review-note">{message}</p>
  <div class="review-grid">
    {"".join(rows)}
  </div>
</section>
""".strip()


def render_action_term(action: str) -> str:
    if action in TERM_DEFINITIONS:
        return render_term(action, action)
    return html_escape(action)


def render_project_card(project: dict[str, Any]) -> str:
    slug = html_escape(project.get("slug", "unknown"))
    status = css_class_token(project.get("recommended_action", "unknown_review"))
    raw_slug = str(project.get("slug", "unknown"))
    raw_action = str(project.get("recommended_action", "unknown_review"))
    raw_category = str(project.get("category", "unknown"))
    raw_path = str(project.get("path", ""))
    raw_repo_light = str(project.get("repo_light", "gray"))
    raw_docs_light = str(project.get("docs_light", "gray"))
    raw_risk_light = str(project.get("risk_light", "gray"))
    search_text = html_escape(
        " ".join([raw_slug, raw_action, raw_category, raw_path]).lower()
    )
    lights = "\n".join(
        [
            render_status_light("repo", project.get("repo_light", "gray")),
            render_status_light("docs", project.get("docs_light", "gray")),
            render_status_light("risk", project.get("risk_light", "gray")),
        ]
    )

    details = "\n".join(
        [
            render_detail("path", project.get("path")),
            render_detail("category", project.get("category")),
            render_detail("overall", project.get("overall_status")),
            render_detail("action", project.get("recommended_action")),
            render_detail("vscode target", project.get("vscode_target")),
            render_detail("marker yaml", project.get("marker_yaml_path")),
            render_detail("marker doc", project.get("marker_doc_path")),
        ]
    )
    launch_panel = render_launch_panel(project)
    review_panel = render_review_panel(project)

    return f"""
<article class="project-card card-{status}" data-action="{html_escape(raw_action)}" data-slug="{html_escape(raw_slug.lower())}" data-risk="{html_escape(raw_risk_light)}" data-docs="{html_escape(raw_docs_light)}" data-repo="{html_escape(raw_repo_light)}" data-search="{search_text}">
  <div class="card-topline">
    <h3>{slug}</h3>
    <div class="card-actions">
      <span class="status-chip">{render_action_term(raw_action)}</span>
      <button class="card-toggle" type="button" data-card-toggle aria-expanded="true">Details</button>
    </div>
  </div>
  <div class="card-body" data-card-body>
    <div class="light-strip">
      {lights}
    </div>
    <div class="detail-grid">
      {details}
    </div>
    {review_panel}
    {launch_panel}
  </div>
</article>
""".strip()


def render_project_section(
    title: str,
    section_class: str,
    section_projects: list[dict[str, Any]],
) -> str:
    if section_projects:
        cards = "\n".join(render_project_card(project) for project in section_projects)
    else:
        cards = '<p class="empty-section">No projects in this lane.</p>'

    return f"""
<section class="project-section {html_escape(section_class)}" data-section>
  <div class="section-heading">
    <button class="section-toggle" type="button" data-section-toggle aria-expanded="true">
      <span>{html_escape(title)}</span>
      <strong>{len(section_projects)}</strong>
    </button>
  </div>
  <div class="project-grid">
    {cards}
  </div>
</section>
""".strip()


def render_summary_cards(summary: dict[str, int]) -> str:
    labels = [
        ("total projects", "total_projects", "cyan", "all", None),
        ("known embedded", "known_embedded", "green", "embedded_ready", "embedded_ready"),
        ("dirty review", "dirty_review", "amber", "dirty_review_first", "dirty_review_first"),
        ("protected review", "protected_review", "magenta", "protected_manual_review", "protected_manual_review"),
        ("candidate review", "candidate_review", "cyan", "candidate_review", "candidate_review"),
        ("control repo", "control_repo", "cyan", "control_repo_no_embed", "control_repo_no_embed"),
        ("blocked other", "blocked_other", "amber", "unknown_review", "unknown_review"),
    ]
    cards = []
    for label, key, accent, filter_action, term_key in labels:
        label_html = render_term_span(label, term_key) if term_key else html_escape(label)
        cards.append(
            f"""
<button class="summary-card accent-{accent}" type="button" data-summary-filter="{html_escape(filter_action)}">
  <span>{label_html}</span>
  <strong>{summary.get(key, 0)}</strong>
</button>
""".strip()
        )
    return "\n".join(cards)


def render_report_links() -> str:
    links = []
    for href, label in LOCAL_REPORT_LINKS:
        links.append(f'<a href="{html_escape(href)}">{html_escape(label)}</a>')
    return "\n".join(links)


def dashboard_command(script_name: str, *args: str) -> str:
    parts = [str(REPO_ROOT / "scripts" / script_name), *args]
    return " ".join(shlex.quote(part) for part in parts)


def render_operator_commands() -> str:
    commands = [
        (
            "Scan + Rebuild",
            "Rescan repos and rebuild dashboard without opening local HTML",
            "scan + rebuild",
            "Copy scan and rebuild command",
            dashboard_command("project-forge-scan-dashboard", "--no-open"),
        ),
        (
            "Refresh HTML",
            "Rebuild from current discovery inventory only",
            "dashboard refresh",
            "Copy dashboard refresh command",
            dashboard_command("project-forge-dashboard", "--no-open"),
        ),
    ]
    rows = []
    for label, detail, term_label, title, command in commands:
        command_html = html_escape(command)
        rows.append(
            f'<div class="operator-row">'
            f'<div class="operator-row-top">'
            f'<span class="operator-label">{html_escape(label)} / {render_term(term_label)}</span>'
            f'<button class="copy-button" type="button" data-copy="{command_html}" '
            f'title="{html_escape(title)}" aria-label="{html_escape(title)}">Copy</button>'
            f"</div>"
            f'<p class="operator-detail">{html_escape(detail)}</p>'
            f"<code>{command_html}</code>"
            f"</div>"
        )
    return f"""
<section class="operator-panel" aria-label="Operator commands">
  <div>
    <p class="operator-kicker">After commits</p>
    <h2>Scan Button</h2>
    <p class="operator-note">Static HTML cannot execute shell commands directly, so these buttons copy safe terminal commands. Use Scan + Rebuild after committing a dirty repo.</p>
  </div>
  <div class="operator-grid">
    {"".join(rows)}
  </div>
</section>
""".strip()


def render_dashboard_controls(summary: dict[str, int]) -> str:
    filters = [
        ("all", "All", summary.get("total_projects", 0)),
        ("embedded_ready", "Embedded", summary.get("known_embedded", 0)),
        ("candidate_review", "Candidates", summary.get("candidate_review", 0)),
        ("dirty_review_first", "Dirty", summary.get("dirty_review", 0)),
        ("protected_manual_review", "Protected", summary.get("protected_review", 0)),
        ("control_repo_no_embed", "Control", summary.get("control_repo", 0)),
        ("unknown_review", "Blocked", summary.get("blocked_other", 0)),
    ]
    buttons = []
    for action, label, count in filters:
        selected = "true" if action == "all" else "false"
        buttons.append(
            f'<button class="filter-button" type="button" data-filter="{html_escape(action)}" '
            f'aria-pressed="{selected}">{html_escape(label)} <span>{count}</span></button>'
        )

    return f"""
<section class="dashboard-controls" aria-label="Dashboard controls">
  <label class="search-box">
    <span>Search</span>
    <input data-dashboard-search type="search" placeholder="Project, action, category, path">
  </label>
  <label class="sort-box">
    <span>Sort</span>
    <select data-dashboard-sort>
      <option value="lane">Lane order</option>
      <option value="slug">Project name</option>
      <option value="risk">Risk light</option>
      <option value="docs">Docs light</option>
    </select>
  </label>
  <div class="filter-strip" aria-label="Project filters">
    {"".join(buttons)}
  </div>
  <button class="clear-button" type="button" data-clear-dashboard>Reset</button>
</section>
""".strip()


def render_glossary_panel() -> str:
    glossary_items = []
    for key in sorted(TERM_DEFINITIONS):
        glossary_items.append(
            f"""
<article class="glossary-item" data-glossary-item="{html_escape(key)}">
  <h3>{html_escape(key.replace("_", " "))}</h3>
  <p>{html_escape(TERM_DEFINITIONS[key])}</p>
</article>
""".strip()
        )

    return f"""
<section class="glossary-panel" aria-label="Embedded glossary">
  <div class="glossary-focus" data-glossary-focus>
    <span>Term guide</span>
    <strong>Click dotted terms to explain them here.</strong>
  </div>
  <details>
    <summary>All dashboard terms</summary>
    <div class="glossary-grid">
      {"".join(glossary_items)}
    </div>
  </details>
</section>
""".strip()


def render_dashboard_html(payload: dict[str, Any]) -> str:
    summary = derive_summary(payload)
    term_definitions_json = json.dumps(TERM_DEFINITIONS, sort_keys=True)
    known_embedded = projects_by_action(payload, "embedded_ready")
    dirty_review = projects_by_action(payload, "dirty_review_first")
    protected_review = projects_by_action(payload, "protected_manual_review")
    candidate_review = projects_by_action(payload, "candidate_review")
    control_repo = projects_by_action(payload, "control_repo_no_embed")
    blocked_other = projects_by_action(payload, "unknown_review")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Project Forge Command Board</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #07090d;
      --panel: #0d1118;
      --panel-2: #111827;
      --panel-glass: rgba(13, 17, 24, 0.76);
      --text: #edf7ff;
      --muted: #8ea4b8;
      --cyan: #20e8ff;
      --green: #42ff9b;
      --amber: #ffc857;
      --magenta: #ff4fd8;
      --red: #ff3864;
      --blue: #5da8ff;
      --gray: #6b7280;
      --line: rgba(125, 245, 255, 0.18);
      --shadow: rgba(32, 232, 255, 0.18);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      background:
        linear-gradient(180deg, rgba(32, 232, 255, 0.09), transparent 25rem),
        linear-gradient(135deg, rgba(255, 200, 87, 0.06), transparent 35rem),
        repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.018) 0 1px, transparent 1px 72px),
        var(--bg);
      color: var(--text);
      font-family: "Aptos", "Barlow", "IBM Plex Sans", "Segoe UI", sans-serif;
      line-height: 1.5;
    }}

    a {{
      color: var(--cyan);
      text-decoration: none;
    }}

    a:hover {{
      text-decoration: underline;
    }}

    .shell {{
      width: min(1440px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 32px 0 56px;
    }}

    .hero {{
      border: 1px solid var(--line);
      background:
        linear-gradient(135deg, rgba(13, 17, 24, 0.96), rgba(17, 24, 39, 0.9)),
        linear-gradient(90deg, rgba(32, 232, 255, 0.12), transparent 44%);
      box-shadow: 0 0 44px var(--shadow), inset 0 0 0 1px rgba(255, 255, 255, 0.03);
      padding: 28px;
      border-radius: 8px;
    }}

    .eyebrow {{
      margin: 0 0 8px;
      color: var(--cyan);
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(2rem, 5vw, 4.4rem);
      line-height: 1;
      letter-spacing: 0;
      text-shadow: 0 0 22px rgba(32, 232, 255, 0.28);
    }}

    .hero-copy {{
      max-width: 72ch;
      margin: 18px 0 0;
      color: var(--muted);
      font-size: 1rem;
    }}

    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0;
    }}

    .summary-card {{
      appearance: none;
      text-align: left;
      color: inherit;
      min-height: 112px;
      padding: 18px;
      border-radius: 8px;
      background: var(--panel-glass);
      border: 1px solid var(--line);
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
      cursor: pointer;
    }}

    .summary-card span {{
      display: block;
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      font-weight: 800;
    }}

    .summary-card strong {{
      display: block;
      margin-top: 12px;
      font-size: 2.4rem;
      line-height: 1;
    }}

    .summary-card:hover,
    .summary-card:focus-visible {{
      border-color: var(--cyan);
      outline: none;
      transform: translateY(-1px);
    }}

    .accent-cyan strong {{ color: var(--cyan); }}
    .accent-green strong {{ color: var(--green); }}
    .accent-amber strong {{ color: var(--amber); }}
    .accent-magenta strong {{ color: var(--magenta); }}

    .report-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 20px 0 28px;
    }}

    .report-links a {{
      padding: 9px 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(13, 17, 24, 0.72);
      font-size: 0.9rem;
    }}

    .operator-panel {{
      display: grid;
      grid-template-columns: minmax(220px, 0.72fr) minmax(320px, 1.28fr);
      gap: 16px;
      align-items: stretch;
      margin: 0 0 22px;
      padding: 18px;
      border: 1px solid rgba(255, 200, 87, 0.3);
      border-radius: 8px;
      background:
        linear-gradient(135deg, rgba(255, 200, 87, 0.13), transparent 42%),
        rgba(13, 17, 24, 0.78);
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
    }}

    .operator-kicker {{
      margin: 0 0 6px;
      color: var(--amber);
      font-size: 0.72rem;
      font-weight: 900;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    .operator-panel h2 {{
      margin: 0;
      font-size: clamp(1.3rem, 2.5vw, 2.1rem);
      line-height: 1;
    }}

    .operator-note,
    .operator-detail {{
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 0.9rem;
    }}

    .operator-grid {{
      display: grid;
      gap: 10px;
    }}

    .operator-row {{
      padding: 12px;
      border: 1px solid rgba(125, 245, 255, 0.16);
      border-radius: 8px;
      background: rgba(7, 9, 13, 0.64);
    }}

    .operator-row-top {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
    }}

    .operator-label {{
      color: var(--text);
      font-size: 0.84rem;
      font-weight: 900;
      text-transform: uppercase;
    }}

    .operator-row code {{
      display: block;
      margin-top: 10px;
      overflow-x: auto;
      color: var(--cyan);
      font-size: 0.82rem;
      white-space: nowrap;
    }}

    .dashboard-controls {{
      position: sticky;
      top: 0;
      z-index: 4;
      display: grid;
      grid-template-columns: minmax(220px, 420px) minmax(150px, 220px) minmax(0, 1fr) auto;
      gap: 12px;
      align-items: stretch;
      margin: 0 0 22px;
      padding: 12px;
      border: 1px solid rgba(125, 245, 255, 0.14);
      border-radius: 8px;
      background: rgba(7, 9, 13, 0.9);
      backdrop-filter: blur(12px);
    }}

    .search-box {{
      display: grid;
      gap: 6px;
      min-width: 0;
    }}

    .sort-box {{
      display: grid;
      gap: 6px;
      min-width: 0;
    }}

    .search-box span,
    .sort-box span {{
      color: var(--muted);
      font-size: 0.7rem;
      font-weight: 800;
      text-transform: uppercase;
    }}

    .search-box input,
    .sort-box select {{
      width: 100%;
      min-height: 42px;
      padding: 0 12px;
      border: 1px solid rgba(125, 245, 255, 0.22);
      border-radius: 6px;
      background: rgba(13, 17, 24, 0.94);
      color: var(--text);
      font: inherit;
      outline: none;
    }}

    .search-box input:focus,
    .sort-box select:focus {{
      border-color: var(--cyan);
      box-shadow: 0 0 0 3px rgba(32, 232, 255, 0.12);
    }}

    .filter-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-content: center;
    }}

    .filter-button,
    .copy-button,
    .clear-button,
    .card-toggle,
    .section-toggle {{
      border: 1px solid rgba(125, 245, 255, 0.18);
      border-radius: 6px;
      background: rgba(17, 24, 39, 0.86);
      color: var(--text);
      cursor: pointer;
      font: inherit;
      font-size: 0.8rem;
      font-weight: 800;
    }}

    .filter-button {{
      min-height: 42px;
      padding: 0 12px;
    }}

    .filter-button span {{
      color: var(--cyan);
      margin-left: 6px;
    }}

    .filter-button[aria-pressed="true"] {{
      border-color: var(--cyan);
      background: rgba(32, 232, 255, 0.12);
      box-shadow: inset 0 -2px 0 var(--cyan);
    }}

    .copy-button {{
      min-width: 62px;
      min-height: 32px;
      padding: 0 10px;
      color: var(--cyan);
    }}

    .clear-button {{
      align-self: end;
      min-height: 42px;
      padding: 0 14px;
      color: var(--amber);
    }}

    .copy-button.is-copied {{
      border-color: var(--green);
      color: var(--green);
    }}

    .term-button,
    .term-inline {{
      border: 0;
      padding: 0;
      border-bottom: 1px dotted currentColor;
      background: transparent;
      color: inherit;
      cursor: help;
      font: inherit;
      font-weight: inherit;
      text-transform: inherit;
    }}

    .term-button:focus-visible {{
      outline: 2px solid var(--cyan);
      outline-offset: 3px;
    }}

    .glossary-panel {{
      display: grid;
      gap: 12px;
      margin: 0 0 26px;
      padding: 14px;
      border: 1px solid rgba(125, 245, 255, 0.14);
      border-radius: 8px;
      background: rgba(13, 17, 24, 0.68);
    }}

    .glossary-focus {{
      display: grid;
      grid-template-columns: 120px minmax(0, 1fr);
      gap: 12px;
      align-items: baseline;
    }}

    .glossary-focus span {{
      color: var(--cyan);
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
    }}

    .glossary-focus strong {{
      color: #dcecff;
      font-size: 0.94rem;
      overflow-wrap: anywhere;
    }}

    .glossary-panel summary {{
      cursor: pointer;
      color: var(--muted);
      font-weight: 800;
      text-transform: uppercase;
      font-size: 0.78rem;
    }}

    .glossary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 10px;
      margin-top: 12px;
    }}

    .glossary-item {{
      padding: 12px;
      border: 1px solid rgba(125, 245, 255, 0.12);
      border-radius: 8px;
      background: rgba(7, 9, 13, 0.56);
    }}

    .glossary-item.is-focused {{
      border-color: var(--cyan);
      box-shadow: 0 0 20px rgba(32, 232, 255, 0.12);
    }}

    .glossary-item h3 {{
      margin: 0 0 6px;
      color: var(--cyan);
      font-size: 0.82rem;
      text-transform: uppercase;
    }}

    .glossary-item p {{
      margin: 0;
      color: var(--muted);
      font-size: 0.86rem;
    }}

    .section-heading {{
      margin: 34px 0 12px;
      border-bottom: 1px solid var(--line);
    }}

    .section-toggle {{
      width: 100%;
      min-height: 46px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin: 0 0 10px;
      padding: 0;
      border: 0;
      background: transparent;
      border-radius: 0;
      color: var(--text);
      cursor: pointer;
    }}

    .section-toggle span {{
      font-size: 1.1rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .section-toggle strong {{
      color: var(--cyan);
      font-weight: 800;
    }}

    .project-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 14px;
    }}

    .project-card {{
      min-width: 0;
      padding: 16px;
      border-radius: 8px;
      background: linear-gradient(180deg, rgba(17, 24, 39, 0.96), rgba(9, 13, 20, 0.96));
      border: 1px solid rgba(125, 245, 255, 0.16);
      box-shadow: 0 18px 40px rgba(0, 0, 0, 0.32);
    }}

    .card-embedded_ready {{
      border-color: rgba(66, 255, 155, 0.38);
      box-shadow: 0 0 22px rgba(66, 255, 155, 0.08);
    }}

    .card-dirty_review_first {{
      border-color: rgba(255, 200, 87, 0.42);
    }}

    .card-protected_manual_review {{
      border-color: rgba(255, 79, 216, 0.46);
      box-shadow: 0 0 24px rgba(255, 79, 216, 0.1);
    }}

    .card-topline {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}

    .card-topline h3 {{
      margin: 0;
      min-width: 0;
      overflow-wrap: anywhere;
      font-size: 1.02rem;
      color: var(--text);
    }}

    .card-actions {{
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 8px;
      min-width: 0;
    }}

    .status-chip {{
      flex: 0 0 auto;
      max-width: 50%;
      padding: 4px 8px;
      border-radius: 999px;
      border: 1px solid var(--line);
      color: var(--cyan);
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      overflow-wrap: anywhere;
    }}

    .card-toggle {{
      min-height: 28px;
      padding: 0 8px;
      color: var(--muted);
      font-size: 0.72rem;
      text-transform: uppercase;
    }}

    .light-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 9px;
      margin-bottom: 14px;
    }}

    .light-pair {{
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: var(--muted);
      font-size: 0.82rem;
    }}

    .status-light {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      display: inline-block;
      background: var(--gray);
      box-shadow: 0 0 12px var(--gray);
    }}

    .light-green {{ background: var(--green); box-shadow: 0 0 14px var(--green); }}
    .light-amber {{ background: var(--amber); box-shadow: 0 0 14px var(--amber); }}
    .light-red {{ background: var(--red); box-shadow: 0 0 14px var(--red); }}
    .light-magenta {{ background: var(--magenta); box-shadow: 0 0 14px var(--magenta); }}
    .light-blue {{ background: var(--blue); box-shadow: 0 0 14px var(--blue); }}
    .light-gray {{ background: var(--gray); box-shadow: 0 0 10px var(--gray); }}

    .detail-grid {{
      display: grid;
      gap: 7px;
    }}

    .detail-row {{
      display: grid;
      grid-template-columns: 116px minmax(0, 1fr);
      gap: 10px;
      min-width: 0;
      font-size: 0.86rem;
    }}

    .detail-label {{
      color: var(--muted);
      text-transform: uppercase;
      font-size: 0.7rem;
      font-weight: 800;
    }}

    .detail-value {{
      min-width: 0;
      color: #dcecff;
      overflow-wrap: anywhere;
    }}

    .empty-section {{
      margin: 0;
      padding: 18px;
      border: 1px dashed var(--line);
      border-radius: 8px;
      color: var(--muted);
    }}

    .launch-panel {{
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid rgba(125, 245, 255, 0.14);
    }}

    .review-panel {{
      margin-top: 16px;
      padding: 14px;
      border: 1px solid rgba(255, 200, 87, 0.24);
      border-radius: 8px;
      background: rgba(255, 200, 87, 0.05);
    }}

    .launch-panel h4,
    .review-panel h4 {{
      margin: 0 0 10px;
      font-size: 0.88rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--cyan);
    }}

    .launch-note,
    .launch-blocked,
    .review-note {{
      margin: 0 0 12px;
      color: var(--muted);
      font-size: 0.84rem;
    }}

    .launch-blocked {{
      color: #ffd7de;
    }}

    .launch-grid,
    .review-grid {{
      display: grid;
      gap: 10px;
    }}

    .launch-row,
    .review-row {{
      display: grid;
      gap: 6px;
      min-width: 0;
      padding: 10px 12px 12px;
      border-radius: 8px;
      border: 1px solid rgba(125, 245, 255, 0.12);
      background: rgba(13, 17, 24, 0.5);
    }}

    .launch-row-top,
    .review-row-top {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: center;
    }}

    .launch-label,
    .review-label {{
      color: var(--muted);
      font-size: 0.72rem;
      text-transform: uppercase;
      font-weight: 800;
    }}

    .launch-row code,
    .review-row code {{
      display: block;
      padding: 10px 12px;
      border-radius: 6px;
      border: 1px solid rgba(125, 245, 255, 0.18);
      background: rgba(7, 9, 13, 0.9);
      color: #dcecff;
      font-size: 0.8rem;
      line-height: 1.45;
      overflow-wrap: anywhere;
      white-space: pre-wrap;
    }}

    .project-card.is-hidden,
    .project-section.is-hidden {{
      display: none;
    }}

    .project-section.is-collapsed .project-grid,
    .project-card.is-collapsed .card-body {{
      display: none;
    }}

    .project-section.is-collapsed .section-toggle {{
      color: var(--muted);
    }}

    .safety {{
      margin-top: 34px;
      padding: 18px;
      border: 1px solid rgba(255, 200, 87, 0.28);
      border-radius: 8px;
      background: rgba(255, 200, 87, 0.05);
      color: var(--muted);
    }}

    .safety strong {{
      color: var(--amber);
    }}

    .toast {{
      position: fixed;
      right: 18px;
      bottom: 18px;
      z-index: 5;
      min-width: 220px;
      max-width: min(420px, calc(100vw - 36px));
      padding: 12px 14px;
      border: 1px solid rgba(66, 255, 155, 0.36);
      border-radius: 8px;
      background: rgba(7, 9, 13, 0.96);
      color: var(--green);
      box-shadow: 0 0 24px rgba(66, 255, 155, 0.12);
      opacity: 0;
      transform: translateY(10px);
      pointer-events: none;
      transition: opacity 160ms ease, transform 160ms ease;
    }}

    .toast.is-visible {{
      opacity: 1;
      transform: translateY(0);
    }}

    @media (max-width: 860px) {{
      .summary-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}

      .dashboard-controls {{
        position: static;
        grid-template-columns: 1fr 1fr;
      }}

      .filter-strip {{
        grid-column: 1 / -1;
      }}
    }}

    @media (max-width: 560px) {{
      .shell {{
        width: min(100vw - 20px, 1440px);
        padding-top: 18px;
      }}

      .hero {{
        padding: 20px;
      }}

      .summary-grid,
      .project-grid {{
        grid-template-columns: 1fr;
      }}

      .operator-panel {{
        grid-template-columns: 1fr;
      }}

      .dashboard-controls {{
        grid-template-columns: 1fr;
      }}

      .filter-strip {{
        grid-column: auto;
      }}

      .glossary-focus {{
        grid-template-columns: 1fr;
      }}

      .detail-row {{
        grid-template-columns: 1fr;
      }}

      .status-chip {{
        max-width: 100%;
      }}

      .card-topline,
      .launch-row-top,
      .operator-row-top {{
        flex-direction: column;
        align-items: stretch;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <p class="eyebrow">Neon District / read-only command surface</p>
      <h1>Project Forge Command Board</h1>
      <p class="hero-copy">A static dashboard rendered from Project Forge artifacts. It shows the system state, exposes no file mutation actions, and keeps launch behavior display-only for Phase 10.7D.</p>
    </header>

    <section class="summary-grid" aria-label="Dashboard summary">
      {render_summary_cards(summary)}
    </section>

    <nav class="report-links" aria-label="Local reports">
      {render_report_links()}
    </nav>

    {render_operator_commands()}
    {render_dashboard_controls(summary)}
    {render_glossary_panel()}

    {render_project_section("Known Embedded Projects", "known-embedded", known_embedded)}
    {render_project_section("Dirty Review Projects", "dirty-review", dirty_review)}
    {render_project_section("Protected Review Projects", "protected-review", protected_review)}
    {render_project_section("Candidate Review Projects", "candidate-review", candidate_review)}
    {render_project_section("Control Repo", "control-repo", control_repo)}
    {render_project_section("Blocked Other", "blocked-other", blocked_other)}

    <section class="safety">
      <strong>Safety:</strong> Phase 11 dashboard interaction is local-only. This page filters cards and can copy dry-run commands, but it does not launch VS Code, execute project commands, write marker files, apply changes, touch remotes, push, fetch, contact GitHub or Codeberg, install packages, or modify external repos.
    </section>
    <div class="toast" data-dashboard-toast role="status" aria-live="polite"></div>
  </main>
  <script>
    (() => {{
      const termDefinitions = {term_definitions_json};
      const cards = Array.from(document.querySelectorAll(".project-card"));
      const sections = Array.from(document.querySelectorAll("[data-section]"));
      const filterButtons = Array.from(document.querySelectorAll("[data-filter]"));
      const summaryButtons = Array.from(document.querySelectorAll("[data-summary-filter]"));
      const searchInput = document.querySelector("[data-dashboard-search]");
      const sortSelect = document.querySelector("[data-dashboard-sort]");
      const clearButton = document.querySelector("[data-clear-dashboard]");
      const glossaryFocus = document.querySelector("[data-glossary-focus]");
      const glossaryItems = Array.from(document.querySelectorAll("[data-glossary-item]"));
      const toast = document.querySelector("[data-dashboard-toast]");
      let activeFilter = "all";
      let toastTimer = 0;
      const lightOrder = {{ red: 0, amber: 1, gray: 2, blue: 3, green: 4 }};

      cards.forEach((card, index) => {{
        card.dataset.order = String(index);
      }});

      const showToast = (message) => {{
        if (!toast) return;
        toast.textContent = message;
        toast.classList.add("is-visible");
        window.clearTimeout(toastTimer);
        toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 1600);
      }};

      const setFilter = (filter) => {{
        activeFilter = filter || "all";
        filterButtons.forEach((item) => {{
          item.setAttribute("aria-pressed", String(item.dataset.filter === activeFilter));
        }});
        applyFilters();
      }};

      const applyFilters = () => {{
        const query = (searchInput?.value || "").trim().toLowerCase();
        cards.forEach((card) => {{
          const matchesFilter = activeFilter === "all" || card.dataset.action === activeFilter;
          const matchesSearch = !query || (card.dataset.search || "").includes(query);
          card.classList.toggle("is-hidden", !(matchesFilter && matchesSearch));
        }});
        sections.forEach((section) => {{
          const visibleCards = section.querySelectorAll(".project-card:not(.is-hidden)").length;
          section.classList.toggle("is-hidden", visibleCards === 0);
        }});
      }};

      const sortCards = () => {{
        const mode = sortSelect?.value || "lane";
        sections.forEach((section) => {{
          const grid = section.querySelector(".project-grid");
          if (!grid) return;
          const sectionCards = Array.from(grid.querySelectorAll(".project-card"));
          sectionCards.sort((a, b) => {{
            if (mode === "slug") {{
              return (a.dataset.slug || "").localeCompare(b.dataset.slug || "");
            }}
            if (mode === "risk") {{
              return (lightOrder[a.dataset.risk || "gray"] ?? 2) - (lightOrder[b.dataset.risk || "gray"] ?? 2)
                || (a.dataset.slug || "").localeCompare(b.dataset.slug || "");
            }}
            if (mode === "docs") {{
              return (lightOrder[a.dataset.docs || "gray"] ?? 2) - (lightOrder[b.dataset.docs || "gray"] ?? 2)
                || (a.dataset.slug || "").localeCompare(b.dataset.slug || "");
            }}
            return Number(a.dataset.order || 0) - Number(b.dataset.order || 0);
          }});
          sectionCards.forEach((card) => grid.appendChild(card));
        }});
      }};

      const explainTerm = (key) => {{
        const definition = termDefinitions[key];
        if (!definition || !glossaryFocus) return;
        glossaryFocus.innerHTML = `<span>${{key.replaceAll("_", " ")}}</span><strong>${{definition}}</strong>`;
        glossaryItems.forEach((item) => {{
          item.classList.toggle("is-focused", item.dataset.glossaryItem === key);
        }});
      }};

      filterButtons.forEach((button) => {{
        button.addEventListener("click", () => {{
          setFilter(button.dataset.filter || "all");
        }});
      }});

      summaryButtons.forEach((button) => {{
        button.addEventListener("click", () => setFilter(button.dataset.summaryFilter || "all"));
      }});

      searchInput?.addEventListener("input", applyFilters);
      sortSelect?.addEventListener("change", () => {{
        sortCards();
        applyFilters();
      }});

      clearButton?.addEventListener("click", () => {{
        if (searchInput) searchInput.value = "";
        if (sortSelect) sortSelect.value = "lane";
        sections.forEach((section) => section.classList.remove("is-collapsed"));
        cards.forEach((card) => card.classList.remove("is-collapsed"));
        document.querySelectorAll("[data-section-toggle], [data-card-toggle]").forEach((button) => {{
          button.setAttribute("aria-expanded", "true");
        }});
        sortCards();
        setFilter("all");
        showToast("Dashboard reset");
      }});

      document.querySelectorAll("[data-explain]").forEach((term) => {{
        term.addEventListener("click", (event) => {{
          event.stopPropagation();
          explainTerm(term.dataset.explain || "");
        }});
      }});

      document.querySelectorAll("[data-section-toggle]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const section = button.closest("[data-section]");
          if (!section) return;
          const collapsed = section.classList.toggle("is-collapsed");
          button.setAttribute("aria-expanded", String(!collapsed));
        }});
      }});

      document.querySelectorAll("[data-card-toggle]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const card = button.closest(".project-card");
          if (!card) return;
          const collapsed = card.classList.toggle("is-collapsed");
          button.setAttribute("aria-expanded", String(!collapsed));
        }});
      }});

      document.querySelectorAll("[data-copy]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const command = button.dataset.copy || "";
          try {{
            await navigator.clipboard.writeText(command);
            button.classList.add("is-copied");
            showToast("Dry-run command copied");
            window.setTimeout(() => button.classList.remove("is-copied"), 1200);
          }} catch (_error) {{
            showToast("Select the command text to copy");
          }}
        }});
      }});
    }})();
  </script>
</body>
</html>
"""


def write_dashboard_html(output_path: Path, payload: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = render_dashboard_html(payload)
    normalized = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    output_path.write_text(normalized, encoding="utf-8")


def run_dashboard_ui(inventory_json: Path, output_html: Path) -> dict[str, int]:
    payload = load_dashboard_inventory(inventory_json)
    write_dashboard_html(output_html, payload)
    return derive_summary(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-dashboard-ui")
    parser.add_argument(
        "--inventory-json",
        default=str(DEFAULT_INVENTORY_JSON),
        help="Dashboard inventory JSON input path.",
    )
    parser.add_argument(
        "--output-html",
        default=str(DEFAULT_OUTPUT_HTML),
        help="Static dashboard HTML output path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_html = Path(args.output_html)
    summary = run_dashboard_ui(Path(args.inventory_json), output_html)

    print("project-forge-dashboard-ui completed")
    print("mode: local interactive read-only")
    print(f"html written: {output_html.resolve()}")
    print(f"total projects: {summary['total_projects']}")
    print(f"known embedded: {summary['known_embedded']}")
    print(f"dirty review: {summary['dirty_review']}")
    print(f"protected review: {summary['protected_review']}")
    print(f"candidate review: {summary['candidate_review']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
