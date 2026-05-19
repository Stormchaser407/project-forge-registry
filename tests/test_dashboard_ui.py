from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from project_forge_registry.dashboard_ui import (
    LOCAL_REPORT_LINKS,
    load_dashboard_inventory,
    render_dashboard_html,
    run_dashboard_ui,
)


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
            "personal": f"./scripts/project-forge-open-project --slug {slug} --profile personal --dry-run",
            "business": f"./scripts/project-forge-open-project --slug {slug} --profile business --dry-run",
            "plain": f"./scripts/project-forge-open-project --slug {slug} --profile plain --dry-run",
        },
        "launch_policy": launch_policy,
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
        self.assertIn("Launch Commands", html)

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
            "./scripts/project-forge-open-project --slug embedded --profile personal --dry-run",
            html,
        )
        self.assertIn(
            "./scripts/project-forge-open-project --slug embedded --profile business --dry-run",
            html,
        )
        self.assertIn(
            "./scripts/project-forge-open-project --slug embedded --profile plain --dry-run",
            html,
        )

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

    def test_output_contains_safety_statement(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertIn("Phase 10.7D is static and read-only", html)
        self.assertIn("does not launch VS Code", html)
        self.assertIn("write marker files", html)
        self.assertIn("execute commands", html)

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

    def test_dashboard_html_does_not_include_open_or_executable_links(self) -> None:
        html = render_dashboard_html(fixture_payload())

        self.assertNotIn("--open", html)
        self.assertNotIn("vscode://", html)
        self.assertNotIn("file://", html)
        self.assertNotIn("<script", html)

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
