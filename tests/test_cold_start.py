from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "project-forge-cold-start"
DOC = REPO_ROOT / "docs" / "PROJECT_FORGE_COLD_START.md"


class ColdStartTests(unittest.TestCase):
    def test_script_exists_and_is_executable(self) -> None:
        self.assertTrue(SCRIPT.exists())
        self.assertTrue(os.access(SCRIPT, os.X_OK))

    def test_help_output(self) -> None:
        proc = subprocess.run(
            [str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(proc.returncode, 0)
        self.assertIn("./scripts/project-forge-cold-start [--open-dashboard]", proc.stdout)
        self.assertIn("--open-dashboard", proc.stdout)
        self.assertIn("PROJECT FORGE COLD START", SCRIPT.read_text(encoding="utf-8"))

    def test_script_contains_expected_safe_calls(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("PYTHONPATH=src python3 -m unittest discover -s tests", text)
        self.assertIn("./scripts/project-sync-safe", text)
        self.assertIn("./scripts/project-forge-dashboard --no-open", text)
        self.assertIn("./scripts/project-forge-dashboard --open", text)
        self.assertIn("git status --short", text)
        self.assertIn("git --no-pager log --oneline -8", text)
        self.assertIn("git tag --list 'v0.10*'", text)
        self.assertIn("git tag --list 'checkpoint-*'", text)

    def test_script_does_not_contain_forbidden_commands(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        forbidden = [
            "git push",
            "git fetch",
            "git remote add",
            "git remote set-url",
            "git remote remove",
            "--apply",
            "--confirm-apply",
            "gh repo",
            "curl",
            "wget",
            "npm install",
            "pip install",
            " code ",
        ]

        for needle in forbidden:
            self.assertNotIn(needle, text)

    def test_docs_mention_read_only_default_behavior(self) -> None:
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("./scripts/project-forge-cold-start", text)
        self.assertIn("--open-dashboard", text)
        self.assertIn("read-only", text)
        self.assertIn("default is no-open", text)
        self.assertIn("does not create commits", text)
        self.assertIn("does not create tags", text)


if __name__ == "__main__":
    unittest.main()
