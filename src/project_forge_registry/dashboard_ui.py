"""Project Forge static dashboard renderer.

This module renders the dashboard inventory JSON into a self-contained static
HTML command board. It is intentionally display-only:
- no server
- no JavaScript file actions
- no external assets
- no external repo writes
- no apply or marker writes
"""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path
from typing import Any


DEFAULT_INVENTORY_JSON = Path("artifacts/dashboard_inventory.json")
DEFAULT_OUTPUT_HTML = Path("artifacts/dashboard.html")

LOCAL_REPORT_LINKS = [
    ("dashboard_inventory_report.md", "Dashboard inventory"),
    ("repo_discovery_report.md", "Repo discovery"),
    ("embed_plan_report.md", "Embed plan"),
    ("tool_readiness_report.md", "Tool readiness"),
    ("project_sync_report.md", "Project sync"),
]


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
        f'<span>{html_escape(label)}: {html_escape(color)}</span>'
        f"</span>"
    )


def render_detail(label: str, value: Any) -> str:
    text = html_escape(value)
    if not text:
        text = "n/a"
    return (
        f'<div class="detail-row">'
        f'<span class="detail-label">{html_escape(label)}</span>'
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
        for label, key in (
            ("Personal", "personal"),
            ("Business", "business"),
            ("Plain", "plain"),
        ):
            command = html_escape(commands.get(key) or "")
            rows.append(
                f'<div class="launch-row">'
                f'<span class="launch-label">{html_escape(label)}</span>'
                f'<code>{command}</code>'
                f"</div>"
            )
        commands_html = "\n".join(rows)
        return f"""
<section class="launch-panel">
  <h4>Launch Commands</h4>
  <p class="launch-note">{message}</p>
  <div class="launch-grid">
    {commands_html}
  </div>
</section>
""".strip()

    return f"""
<section class="launch-panel">
  <h4>Launch Commands</h4>
  <p class="launch-blocked">{message}</p>
</section>
""".strip()


def render_project_card(project: dict[str, Any]) -> str:
    slug = html_escape(project.get("slug", "unknown"))
    status = css_class_token(project.get("recommended_action", "unknown_review"))
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

    return f"""
<article class="project-card card-{status}">
  <div class="card-topline">
    <h3>{slug}</h3>
    <span class="status-chip">{html_escape(project.get("recommended_action"))}</span>
  </div>
  <div class="light-strip">
    {lights}
  </div>
  <div class="detail-grid">
    {details}
  </div>
  {launch_panel}
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
<section class="project-section {html_escape(section_class)}">
  <div class="section-heading">
    <h2>{html_escape(title)}</h2>
    <span>{len(section_projects)}</span>
  </div>
  <div class="project-grid">
    {cards}
  </div>
</section>
""".strip()


def render_summary_cards(summary: dict[str, int]) -> str:
    labels = [
        ("total projects", "total_projects", "cyan"),
        ("known embedded", "known_embedded", "green"),
        ("dirty review", "dirty_review", "amber"),
        ("protected review", "protected_review", "magenta"),
        ("candidate review", "candidate_review", "cyan"),
        ("control repo", "control_repo", "cyan"),
        ("blocked other", "blocked_other", "amber"),
    ]
    cards = []
    for label, key, accent in labels:
        cards.append(
            f"""
<div class="summary-card accent-{accent}">
  <span>{html_escape(label)}</span>
  <strong>{summary.get(key, 0)}</strong>
</div>
""".strip()
        )
    return "\n".join(cards)


def render_report_links() -> str:
    links = []
    for href, label in LOCAL_REPORT_LINKS:
        links.append(f'<a href="{html_escape(href)}">{html_escape(label)}</a>')
    return "\n".join(links)


def render_dashboard_html(payload: dict[str, Any]) -> str:
    summary = derive_summary(payload)
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
        linear-gradient(180deg, rgba(32, 232, 255, 0.08), transparent 24rem),
        radial-gradient(circle at 18% 8%, rgba(255, 79, 216, 0.14), transparent 24rem),
        var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
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
      background: linear-gradient(135deg, rgba(13, 17, 24, 0.96), rgba(17, 24, 39, 0.9));
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
      min-height: 112px;
      padding: 18px;
      border-radius: 8px;
      background: rgba(13, 17, 24, 0.92);
      border: 1px solid var(--line);
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
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

    .section-heading {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
      margin: 34px 0 12px;
      border-bottom: 1px solid var(--line);
    }}

    .section-heading h2 {{
      margin: 0 0 10px;
      font-size: 1.1rem;
      text-transform: uppercase;
      color: var(--text);
      letter-spacing: 0.08em;
    }}

    .section-heading span {{
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

    .launch-panel h4 {{
      margin: 0 0 10px;
      font-size: 0.84rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--cyan);
    }}

    .launch-note,
    .launch-blocked {{
      margin: 0 0 12px;
      color: var(--muted);
      font-size: 0.84rem;
    }}

    .launch-blocked {{
      color: #ffd7de;
    }}

    .launch-grid {{
      display: grid;
      gap: 10px;
    }}

    .launch-row {{
      display: grid;
      gap: 6px;
      min-width: 0;
    }}

    .launch-label {{
      color: var(--muted);
      font-size: 0.72rem;
      text-transform: uppercase;
      font-weight: 800;
    }}

    .launch-row code {{
      display: block;
      padding: 10px 12px;
      border-radius: 6px;
      border: 1px solid rgba(125, 245, 255, 0.14);
      background: rgba(7, 9, 13, 0.72);
      color: #dcecff;
      font-size: 0.8rem;
      line-height: 1.45;
      overflow-wrap: anywhere;
      white-space: pre-wrap;
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

    @media (max-width: 860px) {{
      .summary-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
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

      .detail-row {{
        grid-template-columns: 1fr;
      }}

      .status-chip {{
        max-width: 100%;
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

    {render_project_section("Known Embedded Projects", "known-embedded", known_embedded)}
    {render_project_section("Dirty Review Projects", "dirty-review", dirty_review)}
    {render_project_section("Protected Review Projects", "protected-review", protected_review)}
    {render_project_section("Candidate Review Projects", "candidate-review", candidate_review)}
    {render_project_section("Control Repo", "control-repo", control_repo)}
    {render_project_section("Blocked Other", "blocked-other", blocked_other)}

    <section class="safety">
      <strong>Safety:</strong> Phase 10.7D is static and read-only. This page does not launch VS Code, execute commands, write marker files, apply changes, touch remotes, push, fetch, contact GitHub or Codeberg, install packages, or modify external repos.
    </section>
  </main>
</body>
</html>
"""


def write_dashboard_html(output_path: Path, payload: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_dashboard_html(payload), encoding="utf-8")


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
    print("mode: static read-only")
    print(f"html written: {output_html.resolve()}")
    print(f"total projects: {summary['total_projects']}")
    print(f"known embedded: {summary['known_embedded']}")
    print(f"dirty review: {summary['dirty_review']}")
    print(f"protected review: {summary['protected_review']}")
    print(f"candidate review: {summary['candidate_review']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
