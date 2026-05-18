from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "project-forge-install-cold-start-desktop"


class ColdStartDesktopInstallerTests(unittest.TestCase):
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
            "./scripts/project-forge-install-cold-start-desktop [--dry-run]",
            proc.stdout,
        )
        self.assertIn("--dry-run", proc.stdout)

    def test_dry_run_does_not_write_to_user_locations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            proc = subprocess.run(
                [str(SCRIPT), "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "HOME": str(home)},
            )

            self.assertEqual(proc.returncode, 0)
            self.assertIn("Dry run only. No files were written.", proc.stdout)
            self.assertFalse((home / ".local").exists())
            self.assertFalse((home / "Desktop").exists())

    def test_script_contains_expected_target_paths(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn(".local/share/icons/neon-district-project-forge", text)
        self.assertIn("project-forge-cold-start.svg", text)
        self.assertIn("Desktop", text)
        self.assertIn(".local/share/applications", text)
        self.assertIn("project-forge-cold-start.desktop", text)

    def test_desktop_template_contains_required_fields(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("Name=Project Forge Cold Start", text)
        self.assertIn(
            "Comment=Resume Project Forge with status, tests, sync, and dashboard refresh",
            text,
        )
        self.assertIn("Exec=$EXEC_LINE", text)
        self.assertIn('cd "/mnt/storage/Cole/Projects/project-forge-registry"', text)
        self.assertIn("./scripts/project-forge-cold-start --open-dashboard", text)
        self.assertIn('echo "Press Enter to close..."', text)
        self.assertIn("read", text)
        self.assertIn("Icon=$ICON_PATH", text)
        self.assertIn("Terminal=true", text)
        self.assertIn("Categories=Development;Utility;", text)
        self.assertIn("StartupNotify=true", text)

    def test_optional_cache_refresh_commands_are_non_fatal(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("command -v update-desktop-database", text)
        self.assertIn("update-desktop-database \"$APP_DIR\" >/dev/null 2>&1 || true", text)
        self.assertIn("command -v kbuildsycoca6", text)
        self.assertIn("kbuildsycoca6 >/dev/null 2>&1 || true", text)

    def test_svg_template_is_self_contained(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("<svg xmlns=", text)
        self.assertIn("Project Forge Cold Start", text)
        self.assertIn("stop-color=\"#05070d\"", text)
        self.assertIn("#20e8ff", text)
        self.assertIn("#42ff9b", text)
        self.assertIn("#ff4fd8", text)
        self.assertIn("#ffc857", text)
        self.assertNotIn("href=\"http", text)
        self.assertNotIn("href=\"file:", text)

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


if __name__ == "__main__":
    unittest.main()
