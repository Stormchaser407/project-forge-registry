from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from project_forge_registry.project_review import (
    load_project,
    render_commit_preflight,
    render_diff,
    render_status,
    run_commit,
)


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def init_repo(repo: Path) -> None:
    repo.mkdir()
    run(["git", "init"], cwd=repo)
    run(["git", "config", "user.email", "project-forge@example.invalid"], cwd=repo)
    run(["git", "config", "user.name", "Project Forge Test"], cwd=repo)
    (repo / "README.md").write_text("initial\n", encoding="utf-8")
    run(["git", "add", "README.md"], cwd=repo)
    run(["git", "commit", "-m", "init"], cwd=repo)


def write_inventory(
    path: Path,
    repo: Path,
    *,
    category: str = "dirty_candidate_review_first",
    recommended_action: str = "dirty_review_first",
) -> None:
    payload = {
        "projects": [
            {
                "slug": "dirty",
                "path": str(repo),
                "category": category,
                "git_status": "dirty",
                "recommended_action": recommended_action,
            }
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


class ProjectReviewTests(unittest.TestCase):
    def test_exact_protected_path_is_rejected_before_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            inventory = Path(tmp) / "dashboard_inventory.json"
            write_inventory(inventory, Path("/home/cole/cerberus"))

            with self.assertRaisesRegex(
                ValueError,
                "exact protected filesystem path",
            ):
                load_project(inventory, "dirty")

    def test_duplicate_slug_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            init_repo(repo)
            inventory = root / "dashboard_inventory.json"
            payload = {
                "projects": [
                    {"slug": "duplicate", "path": str(repo)},
                    {"slug": "duplicate", "path": str(repo)},
                ]
            }
            inventory.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Ambiguous project slug"):
                load_project(inventory, "duplicate")

    def test_status_and_diff_render_for_dirty_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            init_repo(repo)
            (repo / "README.md").write_text("changed\n", encoding="utf-8")
            inventory = root / "dashboard_inventory.json"
            write_inventory(inventory, repo)

            project = load_project(inventory, "dirty")
            status = render_status(project)
            diff = render_diff(project)

        self.assertIn("Slug: dirty", status)
        self.assertIn(" M README.md", status)
        self.assertIn("README.md", diff)
        self.assertIn("Unstaged diff stat", diff)

    def test_commit_preflight_flags_sensitive_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            init_repo(repo)
            (repo / ".env").write_text("TOKEN=x\n", encoding="utf-8")
            inventory = root / "dashboard_inventory.json"
            write_inventory(inventory, repo)

            project = load_project(inventory, "dirty")
            preflight = render_commit_preflight(project)

        self.assertIn("Commit preflight only", preflight)
        self.assertIn(".env", preflight)
        self.assertIn("Sensitive path flags", preflight)

    def test_commit_requires_confirmations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            init_repo(repo)
            (repo / "README.md").write_text("changed\n", encoding="utf-8")
            inventory = root / "dashboard_inventory.json"
            write_inventory(inventory, repo)

            project = load_project(inventory, "dirty")
            with self.assertRaises(ValueError):
                run_commit(
                    project=project,
                    message="reviewed",
                    confirm_slug="wrong",
                    yes_commit_reviewed=True,
                    include_untracked=False,
                    yes_include_untracked=False,
                    allow_sensitive_paths=False,
                )

    def test_commit_blocks_protected_and_control_repos(self) -> None:
        for category, action in (
            ("protected_manual_review", "protected_manual_review"),
            ("control_repo", "control_repo_no_embed"),
        ):
            with self.subTest(category=category), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                repo = root / "repo"
                init_repo(repo)
                (repo / "README.md").write_text("changed\n", encoding="utf-8")
                inventory = root / "dashboard_inventory.json"
                write_inventory(
                    inventory,
                    repo,
                    category=category,
                    recommended_action=action,
                )
                project = load_project(inventory, "dirty")

                with self.assertRaisesRegex(ValueError, "Commit automation is blocked"):
                    run_commit(
                        project=project,
                        message="reviewed",
                        confirm_slug="dirty",
                        yes_commit_reviewed=True,
                        include_untracked=False,
                        yes_include_untracked=False,
                        allow_sensitive_paths=False,
                    )

    def test_commit_blocks_non_dirty_review_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            init_repo(repo)
            (repo / "README.md").write_text("changed\n", encoding="utf-8")
            inventory = root / "dashboard_inventory.json"
            write_inventory(
                inventory,
                repo,
                category="clean_candidate",
                recommended_action="candidate_review",
            )
            project = load_project(inventory, "dirty")

            with self.assertRaisesRegex(ValueError, "only for dirty-review projects"):
                run_commit(
                    project=project,
                    message="reviewed",
                    confirm_slug="dirty",
                    yes_commit_reviewed=True,
                    include_untracked=False,
                    yes_include_untracked=False,
                    allow_sensitive_paths=False,
                )

    def test_commit_tracked_changes_after_guards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            init_repo(repo)
            (repo / "README.md").write_text("changed\n", encoding="utf-8")
            inventory = root / "dashboard_inventory.json"
            write_inventory(inventory, repo)

            project = load_project(inventory, "dirty")
            output = run_commit(
                project=project,
                message="review dirty changes",
                confirm_slug="dirty",
                yes_commit_reviewed=True,
                include_untracked=False,
                yes_include_untracked=False,
                allow_sensitive_paths=False,
            )
            log = run(["git", "log", "-1", "--oneline"], cwd=repo).stdout

        self.assertIn("Commit created", output)
        self.assertIn("review dirty changes", log)


if __name__ == "__main__":
    unittest.main()
