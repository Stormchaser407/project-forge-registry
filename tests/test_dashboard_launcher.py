from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "scripts" / "project-forge-dashboard"
DOC = REPO_ROOT / "docs" / "PROJECT_FORGE_DASHBOARD_LAUNCHER.md"


class DashboardLauncherTests(unittest.TestCase):
    def test_wrapper_script_exists_and_is_executable(self) -> None:
        self.assertTrue(WRAPPER.exists())
        self.assertTrue(os.access(WRAPPER, os.X_OK))

    def test_help_output(self) -> None:
        proc = subprocess.run(
            [str(WRAPPER), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(proc.returncode, 0)
        self.assertIn("./scripts/project-forge-dashboard [--no-open|--open]", proc.stdout)
        self.assertIn("--no-open", proc.stdout)
        self.assertIn("--open", proc.stdout)

    def test_wrapper_contains_expected_safe_commands(self) -> None:
        text = WRAPPER.read_text(encoding="utf-8")

        self.assertIn("cd \"$REPO_ROOT\"", text)
        self.assertIn("PYTHONPATH=src python3 -m project_forge_registry.dashboard_inventory", text)
        self.assertIn("PYTHONPATH=src python3 -m project_forge_registry.dashboard_ui", text)
        self.assertIn("command -v xdg-open", text)
        self.assertIn("artifacts/dashboard.html", text)

    def test_wrapper_does_not_contain_mutating_project_commands(self) -> None:
        text = WRAPPER.read_text(encoding="utf-8")
        forbidden = [
            "git push",
            "git fetch",
            "git remote",
            "--apply",
            "project_forge_registry.embed_apply",
            "code ",
            "codium ",
            "curl ",
            "wget ",
        ]

        for needle in forbidden:
            self.assertNotIn(needle, text)

    def test_docs_mention_read_only_local_open_behavior(self) -> None:
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("./scripts/project-forge-dashboard --no-open", text)
        self.assertIn("./scripts/project-forge-dashboard --open", text)
        self.assertIn("read-only", text)
        self.assertIn("xdg-open", text)
        self.assertIn("No VS Code launching", text)


if __name__ == "__main__":
    unittest.main()
