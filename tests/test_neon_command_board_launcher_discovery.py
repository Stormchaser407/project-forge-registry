from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from project_forge_registry.neon_command_board_launcher_discovery import (
    collect_discovery,
    render_report,
    run_discovery,
)


def write_repo_fixture(root: Path) -> None:
    scripts = root / "scripts"
    docs = root / "docs"
    artifacts = root / "artifacts"
    scripts.mkdir()
    docs.mkdir()
    artifacts.mkdir()
    (scripts / "project-forge-neon-command-board").write_text(
        "PYTHONPATH=src python3 -m project_forge_registry.neon_command_board\n",
        encoding="utf-8",
    )
    (scripts / "project-forge-dashboard").write_text(
        "./project-forge-dashboard --no-open\n",
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project.scripts]",
                'project-forge-neon-command-board = "project_forge_registry.neon_command_board:main"',
            ]
        ),
        encoding="utf-8",
    )
    (docs / "PROJECT_FORGE_NEON_COMMAND_BOARD.md").write_text(
        "Neon command board with no command execution and no vault writes.\n",
        encoding="utf-8",
    )
    (artifacts / "neon_command_board_launcher_plan.md").write_text(
        "Phase 11H.0 launcher/autostart planning only.\n",
        encoding="utf-8",
    )


def write_home_fixture(home: Path) -> None:
    autostart = home / ".config" / "autostart"
    systemd = home / ".config" / "systemd" / "user"
    applications = home / ".local" / "share" / "applications"
    autostart.mkdir(parents=True)
    systemd.mkdir(parents=True)
    applications.mkdir(parents=True)
    (autostart / "project-forge.desktop").write_text(
        "[Desktop Entry]\nName=Project Forge\nExec=project-forge-dashboard --no-open\n",
        encoding="utf-8",
    )
    (systemd / "project-forge.service").write_text(
        "[Service]\nExecStart=project-forge-neon-command-board\n",
        encoding="utf-8",
    )
    (applications / "project-forge-neon.desktop").write_text(
        "[Desktop Entry]\nName=Neon command board\nExec=project-forge-neon-command-board\n",
        encoding="utf-8",
    )


class NeonCommandBoardLauncherDiscoveryTests(unittest.TestCase):
    def test_collects_repo_and_user_candidates_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp, tempfile.TemporaryDirectory(
            dir=Path.cwd()
        ) as home_tmp:
            root = Path(repo_tmp)
            home = Path(home_tmp)
            write_repo_fixture(root)
            write_home_fixture(home)

            discovery = collect_discovery(root=root, home=home)

            self.assertEqual(discovery["phase"], "Phase 11H.1")
            self.assertEqual(discovery["mode"], "dry-run discovery")
            self.assertTrue(discovery["read_only"])
            self.assertFalse(discovery["mutates_state"])
            self.assertGreaterEqual(len(discovery["candidates"]), 4)
            self.assertTrue(any(candidate["category"] == "user_autostart" for candidate in discovery["candidates"]))
            self.assertTrue(any(candidate["category"] == "user_systemd" for candidate in discovery["candidates"]))
            self.assertTrue(
                any(candidate["category"] == "user_desktop_entry" for candidate in discovery["candidates"])
            )
            self.assertFalse(discovery["safety"]["command_execution"])
            self.assertFalse(discovery["safety"]["systemd_changes"])
            self.assertFalse(discovery["safety"]["desktop_entry_changes"])

    def test_missing_external_directories_are_skipped_not_errors(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp, tempfile.TemporaryDirectory(
            dir=Path.cwd()
        ) as home_tmp:
            root = Path(repo_tmp)
            home = Path(home_tmp)
            write_repo_fixture(root)

            discovery = collect_discovery(root=root, home=home)

            skipped = {item["target"]: item["reason"] for item in discovery["skipped_targets"]}
            self.assertEqual(skipped["user_autostart"], "missing")
            self.assertEqual(skipped["user_systemd"], "missing")
            self.assertEqual(skipped["user_applications"], "missing")

    def test_run_writes_markdown_and_json_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp, tempfile.TemporaryDirectory(
            dir=Path.cwd()
        ) as home_tmp:
            root = Path(repo_tmp)
            home = Path(home_tmp)
            write_repo_fixture(root)
            write_home_fixture(home)
            report_path = root / "artifacts" / "discovery.md"
            json_path = root / "artifacts" / "discovery.json"

            run_discovery(root=root, home=home, report_path=report_path, json_path=json_path)

            self.assertTrue(report_path.exists())
            self.assertTrue(json_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["phase"], "Phase 11H.1")
            self.assertIn("dry-run discovery", report_path.read_text(encoding="utf-8"))

    def test_report_contains_required_safety_language(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp, tempfile.TemporaryDirectory(
            dir=Path.cwd()
        ) as home_tmp:
            root = Path(repo_tmp)
            home = Path(home_tmp)
            write_repo_fixture(root)
            discovery = collect_discovery(root=root, home=home)

            report = render_report(discovery)

            for text in (
                "Phase 11H.1",
                "dry-run discovery",
                "read-only",
                "no mutation",
                "no autostart replacement",
                "no systemd changes",
                "no desktop entry changes",
                "no vault writes",
                "no --open",
                "no command execution",
                "operator approval",
            ):
                self.assertIn(text, report)

    def test_unsafe_patterns_are_absent_from_report(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp, tempfile.TemporaryDirectory(
            dir=Path.cwd()
        ) as home_tmp:
            root = Path(repo_tmp)
            home = Path(home_tmp)
            write_repo_fixture(root)
            discovery = collect_discovery(root=root, home=home)
            report = render_report(discovery)

            unsafe_patterns = (
                "-" * 2 + "apply",
                "vscode:" + "//",
                "file:" + "//",
                "on" + "click=",
                "java" + "script:",
            )
            for unsafe in unsafe_patterns:
                self.assertNotIn(unsafe, report)


if __name__ == "__main__":
    unittest.main()
