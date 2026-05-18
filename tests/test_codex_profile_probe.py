from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "project-forge-codex-profile-probe"
DOC = REPO_ROOT / "docs" / "PROJECT_FORGE_CODEX_PROFILES.md"
EXAMPLE_CONFIG = REPO_ROOT / "config" / "codex_profiles.example.yml"
GITIGNORE = REPO_ROOT / ".gitignore"


class CodexProfileProbeTests(unittest.TestCase):
    def run_probe(self, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            return subprocess.run(
                [str(SCRIPT), *args],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "HOME": tmp},
            )

    def test_script_exists_and_is_executable(self) -> None:
        self.assertTrue(SCRIPT.exists())
        self.assertTrue(os.access(SCRIPT, os.X_OK))

    def test_help_works(self) -> None:
        proc = self.run_probe("--help")

        self.assertEqual(proc.returncode, 0)
        self.assertIn("PROJECT FORGE CODEX PROFILE PROBE", SCRIPT.read_text(encoding="utf-8"))
        self.assertIn("--profile personal", proc.stdout)
        self.assertIn("--interactive", proc.stdout)

    def test_profile_personal_prints_label_and_codex_home(self) -> None:
        proc = self.run_probe("--profile", "personal")

        self.assertEqual(proc.returncode, 0)
        self.assertIn("Selected profile: personal", proc.stdout)
        self.assertIn("Profile label: Personal Codex workspace", proc.stdout)
        self.assertIn("Proposed CODEX_HOME:", proc.stdout)
        self.assertIn(".codex-personal", proc.stdout)
        self.assertIn("no login/auth action was performed", proc.stdout)

    def test_profile_business_prints_label_and_codex_home(self) -> None:
        proc = self.run_probe("--profile", "business")

        self.assertEqual(proc.returncode, 0)
        self.assertIn("Selected profile: business", proc.stdout)
        self.assertIn("Profile label: Business Codex workspace", proc.stdout)
        self.assertIn(".codex-business", proc.stdout)

    def test_profile_plain_prints_no_codex_assumption(self) -> None:
        proc = self.run_probe("--profile", "plain")

        self.assertEqual(proc.returncode, 0)
        self.assertIn("Selected profile: plain", proc.stdout)
        self.assertIn("Plain editor / no Codex assumption", proc.stdout)
        self.assertIn("Proposed CODEX_HOME: none", proc.stdout)
        self.assertIn("Likely auth file exists: not checked", proc.stdout)

    def test_script_does_not_print_auth_file_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            codex_home = home / ".codex-personal"
            codex_home.mkdir()
            (codex_home / "auth.json").write_text(
                "SUPER_SECRET_TEST_TOKEN",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [str(SCRIPT), "--profile", "personal"],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "HOME": str(home)},
            )

        self.assertEqual(proc.returncode, 0)
        self.assertIn("Likely auth file exists: yes", proc.stdout)
        self.assertNotIn("SUPER_SECRET_TEST_TOKEN", proc.stdout)
        self.assertNotIn("auth.json", proc.stdout)

    def test_script_contains_no_forbidden_commands(self) -> None:
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
            "codex login",
        ]

        for needle in forbidden:
            self.assertNotIn(needle, text)

    def test_local_config_is_ignored(self) -> None:
        text = GITIGNORE.read_text(encoding="utf-8")

        self.assertIn("config/codex_profiles.local.yml", text)

    def test_example_config_contains_profiles(self) -> None:
        text = EXAMPLE_CONFIG.read_text(encoding="utf-8")

        self.assertIn("personal:", text)
        self.assertIn("Business Codex workspace", text)
        self.assertIn("Plain editor / no Codex assumption", text)
        self.assertIn("~/.codex-personal", text)
        self.assertIn("~/.codex-business", text)

    def test_docs_explain_single_account_workspace_selection(self) -> None:
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("one ChatGPT account", text)
        self.assertIn("Personal or Business", text)
        self.assertIn("does not automate", text)
        self.assertIn("does not print auth file contents", text)


if __name__ == "__main__":
    unittest.main()
