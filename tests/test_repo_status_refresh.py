from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from project_forge_registry.repo_status_refresh import (
    is_git_work_tree,
    refresh_known_rows,
    resolve_known_repo_path,
    run_refresh,
)


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


class RepoStatusRefreshTests(unittest.TestCase):
    def test_resolves_legacy_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            current_root = Path(tmp)
            current_repo = current_root / "demo"
            current_repo.mkdir()
            legacy_root = Path("/mnt/storage/Cole/Projects")

            with (
                patch(
                    "project_forge_registry.repo_status_refresh.PROJECT_ROOT_FALLBACK",
                    current_root,
                ),
                patch(
                    "project_forge_registry.repo_status_refresh.PATH_PREFIX_FALLBACKS",
                    ((legacy_root, current_root),),
                ),
            ):
                resolved = resolve_known_repo_path(legacy_root / "demo", "demo")

        self.assertEqual(resolved, current_repo)

    @patch(
        "project_forge_registry.repo_status_refresh.subprocess.run",
        side_effect=subprocess.TimeoutExpired("git", 3),
    )
    def test_git_probe_timeout_is_not_a_work_tree(self, _run) -> None:
        self.assertFalse(is_git_work_tree(Path("/tmp/demo")))

    def test_missing_known_repo_becomes_explicit_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"
            repos = refresh_known_rows(
                [{"slug": "missing", "path": str(missing)}]
            )

        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0].git_status, "unknown")
        self.assertEqual(repos[0].category, "unknown_structure")

    def test_run_refresh_writes_current_inventory_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "demo"
            repo.mkdir()
            run(["git", "init"], repo)
            input_csv = root / "input.csv"
            output_csv = root / "output.csv"
            report = root / "report.md"
            input_csv.write_text(
                "slug,path,git_status,has_readme,has_agents,has_code_workspace,"
                "has_project_forge_marker,remote_count,category\n"
                f"demo,{repo},unknown,false,false,false,false,0,unknown_structure\n",
                encoding="utf-8",
            )

            repos = run_refresh(input_csv, output_csv, report)

            csv_text = output_csv.read_text(encoding="utf-8")
            report_text = report.read_text(encoding="utf-8")

        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0].git_status, "clean")
        self.assertNotIn("\r", csv_text)
        self.assertIn("# Project Forge Repo Discovery Report", report_text)


if __name__ == "__main__":
    unittest.main()
