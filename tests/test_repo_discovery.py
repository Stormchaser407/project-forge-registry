from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from project_forge_registry.repo_discovery import (
    classify_repo,
    derive_final_status,
    discover_repos,
    has_project_forge_marker,
    normalize_slug,
    run_discovery,
    should_exclude,
)


class RepoDiscoveryTests(unittest.TestCase):
    def test_normalize_slug(self) -> None:
        self.assertEqual(normalize_slug(Path("My Project")), "my_project")

    def test_should_exclude_default_system_paths(self) -> None:
        self.assertTrue(should_exclude(Path("/proc/test")))
        self.assertTrue(should_exclude(Path("/nix/store/test")))
        self.assertTrue(should_exclude(Path("/tmp/example/node_modules/pkg")))

    def test_should_exclude_operator_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            excluded = root / "archive"
            candidate = excluded / "repo"
            self.assertTrue(should_exclude(candidate, [excluded]))

    def test_has_project_forge_marker_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".project-forge.yml").write_text("slug: demo\n", encoding="utf-8")
            self.assertTrue(has_project_forge_marker(repo))

    def test_has_project_forge_marker_doc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "docs").mkdir()
            (repo / "docs" / "PROJECT_FORGE.md").write_text("# Project Forge\n", encoding="utf-8")
            self.assertTrue(has_project_forge_marker(repo))

    def test_classify_protected_cerberus(self) -> None:
        repo = Path("/tmp/CerberusThing")
        self.assertEqual(classify_repo(repo, "clean", False), "protected_manual_review")

    def test_classify_control_repo(self) -> None:
        repo = Path("/tmp/project-forge-registry")
        self.assertEqual(classify_repo(repo, "clean", False), "control_repo")

    def test_classify_known_embedded(self) -> None:
        repo = Path("/tmp/demo")
        self.assertEqual(classify_repo(repo, "clean", True), "known_embedded")

    def test_classify_dirty_candidate(self) -> None:
        repo = Path("/tmp/demo")
        self.assertEqual(classify_repo(repo, "dirty", False), "dirty_candidate_review_first")

    def test_classify_clean_candidate(self) -> None:
        repo = Path("/tmp/demo")
        self.assertEqual(classify_repo(repo, "clean", False), "clean_candidate")

    def test_derive_final_status_no_repos(self) -> None:
        self.assertEqual(derive_final_status([]), "no_repos_found")

    @patch("project_forge_registry.repo_discovery.git_status", return_value="clean")
    @patch("project_forge_registry.repo_discovery.remote_count", return_value=0)
    def test_discover_repos_finds_git_repo(self, _remote_count, _git_status) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "demo"
            repo.mkdir()
            (repo / ".git").mkdir()
            (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
            (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
            (repo / "demo.code-workspace").write_text("{}", encoding="utf-8")

            repos = discover_repos([root])

        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0].slug, "demo")
        self.assertTrue(repos[0].has_readme)
        self.assertTrue(repos[0].has_agents)
        self.assertTrue(repos[0].has_code_workspace)
        self.assertEqual(repos[0].category, "clean_candidate")

    @patch("project_forge_registry.repo_discovery.git_status", return_value="clean")
    @patch("project_forge_registry.repo_discovery.remote_count", return_value=0)
    def test_run_discovery_writes_report_and_csv(self, _remote_count, _git_status) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "demo"
            repo.mkdir()
            (repo / ".git").mkdir()
            report_path = root / "report.md"
            csv_path = root / "inventory.csv"

            summary = run_discovery([root], [], report_path, csv_path)

            report = report_path.read_text(encoding="utf-8")
            csv_text = csv_path.read_text(encoding="utf-8")

        self.assertEqual(summary.final_status, "ready_for_operator_review")
        self.assertIn("# Project Forge Repo Discovery Report", report)
        self.assertIn("- Discovery was dry-run/report-only.", report)
        self.assertIn("slug,path,git_status", csv_text)


if __name__ == "__main__":
    unittest.main()
