from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from project_forge_registry.dashboard_inventory import REPO_ROOT
from project_forge_registry.dashboard_ui import (
    LOCAL_REPORT_LINKS,
    REPO_ROOT as DASHBOARD_REPO_ROOT,
    load_dashboard_inventory,
    render_dashboard_html,
    run_dashboard_ui,
)


OPEN_SCRIPT = str(REPO_ROOT / "scripts" / "project-forge-open-project")
REVIEW_SCRIPT = str(REPO_ROOT / "scripts" / "project-forge-review-project")
SCAN_SCRIPT = str(DASHBOARD_REPO_ROOT / "scripts" / "project-forge-scan-dashboard")


def fixture_project(
    slug: str,
    recommended_action: str,
    category: str = "clean_candidate",
    repo_light: str = "green",
    docs_light: str = "amber",
    risk_light: str = "amber",
) -> dict[str, object]:
    if category in {"known_embedded", "clean_candidate"}:
        launch_policy = {
            "status": "eligible",
            "message": "Dry-run launch commands available for personal, business, and plain.",
        }
    elif category == "control_repo":
        launch_policy = {
            "status": "restricted",
            "message": "Launch restricted by policy: control repo is dry-run only here, and profile-mode open is deferred.",
        }
    elif category == "protected_manual_review":
        launch_policy = {
            "status": "blocked",
            "message": "Launch blocked by policy: protected project requires manual review.",
        }
    else:
        launch_policy = {
            "status": "blocked",
            "message": "Launch blocked by policy: dirty candidate requires review first.",
        }
    review_commands = {}
    review_policy = {
        "status": "not_required",
        "message": "No dirty-review command shortcuts required for this project.",
    }
    if category == "dirty_candidate_review_first":
        review_commands = {
            "status": f"{REVIEW_SCRIPT} --slug {slug} --status",
            "diff": f"{REVIEW_SCRIPT} --slug {slug} --diff",
            "log": f"{REVIEW_SCRIPT} --slug {slug} --log",
            "commit_preflight": f"{REVIEW_SCRIPT} --slug {slug} --commit-dry-run",
            "commit_template": (
                f"{REVIEW_SCRIPT} --slug {slug} --commit "
                f"--confirm-slug {slug} --yes-commit-reviewed "
                '--message "describe reviewed changes"'
            ),
        }
        review_policy = {
            "status": "review_available",
            "message": "Review commands available. Commit requires explicit terminal confirmation.",
        }
    elif category == "protected_manual_review":
        review_policy = {
            "status": "manual_only",
            "message": "Protected project remains manual review only.",
        }

    return {
        "slug": slug,
        "path": f"/tmp/{slug}",
        "category": category,
        "git_status": "clean",
        "has_readme": True,
        "has_agents": False,
        "has_code_workspace": False,
        "has_project_forge_marker": category == "known_embedded",
        "remote_count": 1,
        "embed_decision": "already_embedded"
        if category == "known_embedded"
        else "candidate_not_selected",
        "repo_light": repo_light,
        "docs_light": docs_light,
        "risk_light": risk_light,
        "overall_status": recommended_action,
        "recommended_action": recommended_action,
        "vscode_target": f"/tmp/{slug}",
        "marker_yaml_path": f"/tmp/{slug}/.project-forge.yml",
        "marker_doc_path": f"/tmp/{slug}/docs/PROJECT_FORGE.md",
        "report_links": [],
        "launch_commands": {
            "personal": f"{OPEN_SCRIPT} --slug {slug} --profile personal --dry-run",
            "business": f"{OPEN_SCRIPT} --slug {slug} --profile business --dry-run",
            "plain": f"{OPEN_SCRIPT} --slug {slug} --profile plain --dry-run",
        },
        "launch_policy": launch_policy,
        "review_commands": review_commands,
        "review_policy": review_policy,
    }


def fixture_payload() -> dict[str, object]:
    return {
        "generated_by": "test",
        "mode": "read-only",
        "projects": [
            fixture_project(
                "embedded",
                "embedded_ready",
                category="known_embedded",
                docs_light="green",
                risk_light="green",
            ),
            fixture_project(
                "dirty",
                "dirty_review_first",
                category="dirty_candidate_review_first",
                repo_light="amber",
                risk_light="amber",
            ),
            fixture_project(
                "protected",
                "protected_manual_review",
                category="protected_manual_review",
                repo_light="red",
                risk_light="red",
            ),
            fixture_project("candidate", "candidate_review"),
            fixture_project(
                "control",
                "control_repo_no_embed",
                category="control_repo",
                repo_light="blue",
                risk_light="blue",
            ),
        ],
    }


class DashboardUiTests(unittest.TestCase):
    def test_load_dashboard_inventory_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dashboard_inventory.json"
            path.write_text(json.dumps(fixture_payload()), encoding="utf-8")

            payload = load_dashboard_inventory(path)

        self.assertEqual(len(payload["projects"]), 5)

    def test_render_html_from_small_fixture(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn("<title>Project Forge Command Board</title>", html)
        self.assertIn("total projects", html)
        self.assertIn("Known Embedded Projects", html)
        self.assertIn("Candidate Review Projects", html)
        self.assertIn("Control Repo", html)
        self.assertIn("Copy-Paste Launch Commands", html)
        self.assertIn("dashboard-controls", html)
        self.assertIn('data-dashboard-search', html)
        self.assertIn('data-dashboard-sort', html)
        self.assertIn('data-clear-dashboard', html)
        self.assertIn("glossary-panel", html)
        self.assertIn("Scan Button", html)

    def test_renders_scan_rebuild_operator_command(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn(f"{SCAN_SCRIPT} --no-open", html)
        self.assertIn("Static HTML cannot execute shell commands directly", html)
        self.assertIn('data-explain="scan_rebuild"', html)

    def test_escapes_html_special_characters(self) -> None:
        payload = {
            "projects": [
                fixture_project(
                    '<script>alert("x")</script>',
                    "candidate_review",
                ),
            ]
        }

        html = render_dashboard_html(payload)

        self.assertIn("&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;", html)
        self.assertNotIn('<script>alert("x")</script>', html)
        self.assertIn(
            "--slug &lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; --profile personal --dry-run",
            html,
        )

    def test_renders_known_embedded_cards(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn("embedded", html)
        self.assertIn("embedded_ready", html)
        self.assertIn("known_embedded", html)

    def test_eligible_project_renders_three_dry_run_commands(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn(
            f"{OPEN_SCRIPT} --slug embedded --profile personal --dry-run",
            html,
        )
        self.assertIn(
            f"{OPEN_SCRIPT} --slug embedded --profile business --dry-run",
            html,
        )
        self.assertIn(
            f"{OPEN_SCRIPT} --slug embedded --profile plain --dry-run",
            html,
        )

    def test_eligible_project_renders_copy_helper_labels(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn("Personal /", html)
        self.assertIn("~/.codex-personal", html)
        self.assertIn("Business /", html)
        self.assertIn("~/.codex-business", html)
        self.assertIn("Plain / no", html)
        self.assertIn('class="copy-button"', html)
        self.assertIn('data-explain="codex_home"', html)

    def test_eligible_project_renders_dry_run_safety_note(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn("Review output before manual open.", html)
        self.assertIn('data-explain="dry_run"', html)

    def test_blocked_project_renders_policy_message(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn(
            "Launch blocked by policy: dirty candidate requires review first.",
            html,
        )
        self.assertIn(
            "Launch blocked by policy: protected project requires manual review.",
            html,
        )

    def test_dirty_project_renders_review_command_buttons(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn("Review commands available.", html)
        self.assertIn(f"{REVIEW_SCRIPT} --slug dirty --status", html)
        self.assertIn(f"{REVIEW_SCRIPT} --slug dirty --diff", html)
        self.assertIn(f"{REVIEW_SCRIPT} --slug dirty --log", html)
        self.assertIn(f"{REVIEW_SCRIPT} --slug dirty --commit-dry-run", html)
        self.assertIn("--yes-commit-reviewed", html)
        self.assertIn('data-explain="review_commands"', html)
        self.assertIn('data-explain="commit_preflight"', html)

    def test_blocked_project_does_not_render_launch_command_blocks(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertNotIn(
            f"{OPEN_SCRIPT} --slug dirty --profile personal --dry-run",
            html,
        )
        self.assertNotIn(
            f"{OPEN_SCRIPT} --slug protected --profile personal --dry-run",
            html,
        )

    def test_control_repo_renders_restricted_note(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn(
            "Launch restricted by policy: control repo is dry-run only here, and profile-mode open is deferred.",
            html,
        )

    def test_renders_status_lights(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn("status-light light-green", html)
        self.assertIn("status-light light-amber", html)
        self.assertIn("status-light light-red", html)
        self.assertIn('data-explain="repo_light"', html)
        self.assertIn('data-explain="docs_light"', html)
        self.assertIn('data-explain="risk_light"', html)

    def test_renders_embedded_term_explanations(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn("Term guide", html)
        self.assertIn("All dashboard terms", html)
        self.assertIn("Dry-run means report and preview only.", html)
        self.assertIn("Repo light summarizes git/project state.", html)
        self.assertIn('data-glossary-item="recommended_action"', html)

    def test_renders_clickable_summary_filters_and_collapses(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn('data-summary-filter="embedded_ready"', html)
        self.assertIn('data-summary-filter="protected_manual_review"', html)
        self.assertIn('data-section-toggle', html)
        self.assertIn('data-card-toggle', html)

    def test_output_contains_safety_statement(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn("Phase 11 dashboard interaction is local-only", html)
        self.assertIn("does not launch VS Code", html)
        self.assertIn("write marker files", html)
        self.assertIn("execute project commands", html)

    def test_missing_inventory_file_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.json"

            with self.assertRaises(FileNotFoundError) as ctx:
                load_dashboard_inventory(missing)

        self.assertIn("Dashboard inventory JSON not found", str(ctx.exception))

    def test_report_links_are_relative_local_only(self) -> None:
        html = render_dashboard_html(fixture_payload())

        for href, _label in LOCAL_REPORT_LINKS:
            self.assertIn(f'href="{href}"', html)
            self.assertFalse(href.startswith("/"))
            self.assertFalse(href.startswith("file:"))
            self.assertFalse(href.startswith("http:"))
            self.assertFalse(href.startswith("https:"))

        self.assertNotIn("file://", html)
        self.assertNotIn("https://", html)
        self.assertNotIn("http://", html)

    def test_dashboard_html_keeps_interaction_local_only(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertNotIn("--open", html)
        self.assertNotIn("vscode://", html)
        self.assertNotIn("file://", html)
        self.assertNotIn("onclick=", html)
        self.assertNotIn("javascript:", html)
        self.assertIn("<script>", html)
        self.assertIn("navigator.clipboard.writeText", html)
        self.assertIn("data-filter", html)
        self.assertIn("setFilter", html)
        self.assertIn("sortCards", html)
        self.assertIn("explainTerm", html)

    def test_run_dashboard_ui_writes_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inventory = root / "dashboard_inventory.json"
            output = root / "dashboard.html"
            inventory.write_text(json.dumps(fixture_payload()), encoding="utf-8")

            summary = run_dashboard_ui(inventory, output)
            html = output.read_text(encoding="utf-8")

        self.assertEqual(summary["total_projects"], 5)
        self.assertEqual(summary["known_embedded"], 1)
        self.assertEqual(summary["control_repo"], 1)
        self.assertIn("Project Forge Command Board", html)


if __name__ == "__main__":
    unittest.main()
