from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "project-forge-open-project"
DOC = REPO_ROOT / "docs" / "PROJECT_FORGE_OPEN_PROJECT.md"
INVENTORY = REPO_ROOT / "artifacts" / "dashboard_inventory.json"


def inventory_projects() -> list[dict[str, object]]:
    payload = json.loads(INVENTORY.read_text(encoding="utf-8"))
    return list(payload["projects"])


def first_slug_for_category(category: str) -> str | None:
    for project in inventory_projects():
        if project.get("category") == category:
            return str(project["slug"])
    return None


class OpenProjectTests(unittest.TestCase):
    def run_open_project(self, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            return subprocess.run(
                [str(SCRIPT), *args],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "HOME": tmp},
            )

    def test_script_exists_and_is_executable(self) -> None:
        self.assertTrue(SCRIPT.exists())
        self.assertTrue(os.access(SCRIPT, os.X_OK))

    def test_help_works(self) -> None:
        proc = self.run_open_project("--help")

        self.assertEqual(proc.returncode, 0)
        self.assertIn("project-forge-open-project", proc.stdout)
        self.assertIn("--slug <slug>", proc.stdout)
        self.assertIn("--profile <name>", proc.stdout)
        self.assertIn("--open", proc.stdout)

    def test_dry_run_known_embedded_slug_works(self) -> None:
        slug = first_slug_for_category("known_embedded")
        self.assertIsNotNone(slug)

        proc = self.run_open_project("--slug", slug or "", "--profile", "personal", "--dry-run")

        self.assertEqual(proc.returncode, 0)
        self.assertIn(f"Slug: {slug}", proc.stdout)
        self.assertIn("Category: known_embedded", proc.stdout)
        self.assertIn("Eligibility decision: yes", proc.stdout)
        self.assertIn("Dry run only. No editor was launched.", proc.stdout)

    def test_dry_run_clean_candidate_slug_works_when_present(self) -> None:
        slug = first_slug_for_category("clean_candidate")
        if slug is None:
            self.skipTest("dashboard inventory has no clean_candidate fixture")

        proc = self.run_open_project("--slug", slug, "--profile", "business", "--dry-run")

        self.assertEqual(proc.returncode, 0)
        self.assertIn(f"Slug: {slug}", proc.stdout)
        self.assertIn("Category: clean_candidate", proc.stdout)
        self.assertIn("Eligibility decision: yes", proc.stdout)

    def test_dirty_repo_blocked(self) -> None:
        slug = first_slug_for_category("dirty_candidate_review_first")
        self.assertIsNotNone(slug)

        proc = self.run_open_project("--slug", slug or "", "--profile", "plain", "--dry-run")

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Eligibility decision: no", proc.stdout)
        self.assertIn("dirty candidate requires review first", proc.stdout)

    def test_protected_repo_blocked(self) -> None:
        slug = first_slug_for_category("protected_manual_review")
        self.assertIsNotNone(slug)

        proc = self.run_open_project("--slug", slug or "", "--profile", "plain", "--dry-run")

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Eligibility decision: no", proc.stdout)
        self.assertIn("protected project requires manual review", proc.stdout)

    def test_unknown_slug_fails_clearly(self) -> None:
        proc = self.run_open_project("--slug", "definitely-not-a-real-project", "--profile", "plain")

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("unknown project slug", proc.stderr)

    def test_personal_profile_dry_run_mentions_codex_home(self) -> None:
        proc = self.run_open_project("--slug", "lifesaver-ledger", "--profile", "personal")

        self.assertEqual(proc.returncode, 0)
        self.assertIn("Selected profile: personal", proc.stdout)
        self.assertIn(".codex-personal", proc.stdout)

    def test_business_profile_dry_run_mentions_codex_home(self) -> None:
        proc = self.run_open_project("--slug", "lifesaver-ledger", "--profile", "business")

        self.assertEqual(proc.returncode, 0)
        self.assertIn("Selected profile: business", proc.stdout)
        self.assertIn(".codex-business", proc.stdout)

    def test_plain_profile_dry_run_mentions_no_codex_home(self) -> None:
        proc = self.run_open_project("--slug", "lifesaver-ledger", "--profile", "plain")

        self.assertEqual(proc.returncode, 0)
        self.assertIn("Selected profile: plain", proc.stdout)
        self.assertIn("Proposed CODEX_HOME: none", proc.stdout)

    def test_dry_run_does_not_launch_editor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "launched"
            editor = Path(tmp) / "editor-probe"
            editor.write_text(
                "#!/usr/bin/env bash\n"
                f"printf launched > {marker}\n",
                encoding="utf-8",
            )
            editor.chmod(0o700)

            proc = self.run_open_project(
                "--slug",
                "lifesaver-ledger",
                "--profile",
                "plain",
                "--dry-run",
                "--editor",
                str(editor),
            )

            self.assertEqual(proc.returncode, 0)
            self.assertFalse(marker.exists())
            self.assertIn("Dry run only. No editor was launched.", proc.stdout)

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
            "codex login",
            "cat auth",
            "cp auth",
            "mv auth",
        ]

        for needle in forbidden:
            self.assertNotIn(needle, text)

    def test_docs_describe_profile_launch_policy(self) -> None:
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("dashboard_inventory.json", text)
        self.assertIn("known_embedded", text)
        self.assertIn("dirty_candidate_review_first", text)
        self.assertIn("No Codex login", text)


if __name__ == "__main__":
    unittest.main()
