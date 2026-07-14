from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "project-forge-install-dashboard-desktop"


class DashboardDesktopInstallerTests(unittest.TestCase):
    def test_installer_script_exists_and_is_executable(self) -> None:
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
        self.assertIn(
            "./scripts/project-forge-install-dashboard-desktop [--dry-run|--install]",
            proc.stdout,
        )
        self.assertIn("--dry-run", proc.stdout)
        self.assertIn("--install", proc.stdout)

    def test_default_dry_run_does_not_write_user_locations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            proc = subprocess.run(
                [str(SCRIPT)],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "HOME": str(home)},
            )

            self.assertEqual(proc.returncode, 0)
            self.assertIn("Mode: dry-run", proc.stdout)
            self.assertIn("Dry run only. No files were written.", proc.stdout)
            self.assertFalse((home / ".local").exists())
            self.assertFalse((home / "Desktop").exists())

    def test_install_writes_expected_temp_home_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            proc = subprocess.run(
                [str(SCRIPT), "--install"],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "HOME": str(home)},
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            app_entry = home / ".local/share/applications/project-forge-dashboard.desktop"
            desktop_entry = home / "Desktop/project-forge-dashboard.desktop"
            icon = home / ".local/share/icons/neon-district-project-forge/project-forge-dashboard.svg"

            self.assertTrue(app_entry.exists())
            self.assertTrue(desktop_entry.exists())
            self.assertTrue(icon.exists())
            desktop_text = app_entry.read_text(encoding="utf-8")
            self.assertIn("Name=Project Forge Dashboard", desktop_text)
            self.assertIn("./scripts/project-forge-dashboard --open", desktop_text)
            self.assertIn("Terminal=false", desktop_text)

    def test_install_backs_up_existing_different_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            app_dir = home / ".local/share/applications"
            app_dir.mkdir(parents=True)
            existing = app_dir / "project-forge-dashboard.desktop"
            existing.write_text("old-dashboard-entry\n", encoding="utf-8")

            proc = subprocess.run(
                [str(SCRIPT), "--install"],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "HOME": str(home)},
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            backups = list(app_dir.glob("project-forge-dashboard.desktop.bak.*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "old-dashboard-entry\n")

    def test_script_does_not_contain_forbidden_commands(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        forbidden = [
            "git push",
            "git fetch",
            "git remote add",
            "git remote set-url",
            "git remote remove",
            "gh repo",
            "curl",
            "wget",
            "npm install",
            "pip install",
            " code ",
        ]

        for needle in forbidden:
            self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
