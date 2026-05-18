from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "project-forge-codex-profile-bootstrap"
DOC = ROOT / "docs" / "PROJECT_FORGE_CODEX_PROFILE_BOOTSTRAP.md"
GITIGNORE = ROOT / ".gitignore"


class CodexProfileBootstrapTests(unittest.TestCase):
    def test_script_exists_and_is_executable(self) -> None:
        self.assertTrue(SCRIPT.exists())
        self.assertTrue(os.access(SCRIPT, os.X_OK))

    def test_help_works(self) -> None:
        proc = subprocess.run(
            [str(SCRIPT), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("project-forge-codex-profile-bootstrap", proc.stdout)
        self.assertIn("--dry-run", proc.stdout)
        self.assertIn("--write", proc.stdout)

    def test_dry_run_does_not_write_to_temp_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["HOME"] = tmp
            proc = subprocess.run(
                [str(SCRIPT), "--dry-run"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
            home = Path(tmp)
            self.assertFalse((home / ".codex-personal").exists())
            self.assertFalse((home / ".codex-business").exists())
        self.assertIn("Dry run only", proc.stdout)

    def test_script_contains_expected_profile_paths(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn(".codex-personal", text)
        self.assertIn(".codex-business", text)
        self.assertIn("codex_profiles.local.yml", text)

    def test_script_safety_language_present(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("no token reading", text)
        self.assertIn("no auth file copying", text)
        self.assertIn("no Codex execution", text)
        self.assertIn("no VS Code launch", text)

    def test_local_config_is_ignored(self) -> None:
        text = GITIGNORE.read_text(encoding="utf-8")
        self.assertIn("config/codex_profiles.local.yml", text)

    def test_docs_describe_bootstrap_safety(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("one-account, multiple-workspace", text)
        self.assertIn("does not automate authentication", text)
        self.assertIn("Do not copy auth files", text)

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
            "curl ",
            "wget ",
            "npm install",
            "pip install",
            "code ",
            "codex login",
        ]
        for needle in forbidden:
            self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
