from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from project_forge_registry.remote_policy import (
    build_parser,
    build_plan,
    build_verify,
    repository_root,
    resolve_repo_scoped_dir,
)
from project_forge_registry.remote_reporting import write_remote_plan_report, write_remote_verify_report


def write_passport(
    path: Path,
    *,
    slug: str = "demo",
    category: str = "active_project",
    status: str = "review",
    registry_action: str = "register_full",
    local_path: str = "/tmp/demo",
    allow_code_to_obsidian: bool = False,
    allow_secrets: bool = False,
    do_not_sync: bool = False,
    default_branch: str = "main",
    github_visibility: str = "private",
    codeberg_visibility: str = "private",
) -> None:
    path.write_text(
        "\n".join(
            [
                "project:",
                f"  slug: {slug}",
                '  name: "Demo Project"',
                f"  category: {category}",
                f"  status: {status}",
                f"  registry_action: {registry_action}",
                f"  local_path: {local_path}",
                "  created_by: project-forge-registry",
                "  schema_version: 0.1",
                "paths:",
                f"  local: {local_path}",
                "  workspace: /tmp/demo.code-workspace",
                f"  obsidian: /home/cole/main_vault/10 Projects/{slug}",
                "launch:",
                "  command: code-demo",
                "git:",
                f"  default_branch: {default_branch}",
                "  github: null",
                "  codeberg: null",
                "  mirror_mode: disabled_for_now",
                "sync:",
                "  obsidian_to_repo: export_only",
                "  repo_to_obsidian: docs_only",
                f"  allow_code_to_obsidian: {'true' if allow_code_to_obsidian else 'false'}",
                f"  allow_secrets: {'true' if allow_secrets else 'false'}",
                "visibility:",
                f"  github: {github_visibility}",
                f"  codeberg: {codeberg_visibility}",
                "  public_ready: false",
                "automation:",
                "  auto_doc_sync: false",
                "  auto_git_sync: false",
                "  require_safety_check_before_push: true",
                "safety:",
                "  warnings: []",
                "  do_not_move: false",
                "  do_not_delete: false",
                f"  do_not_sync: {'true' if do_not_sync else 'false'}",
                "  notes:",
                "    - generated_for_tests=true",
                "",
            ]
        ),
        encoding="utf-8",
    )


class RemotePolicyTests(unittest.TestCase):
    def temp_in_repo(self):
        return tempfile.TemporaryDirectory(dir=repository_root() / "artifacts")

    def test_parser_supports_plan_and_verify(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["plan", "--slug", "demo"])
        self.assertEqual(args.command, "plan")
        verify = parser.parse_args(["verify", "--slug", "demo", "--require-clean-tree"])
        self.assertEqual(verify.command, "verify")
        self.assertTrue(verify.require_clean_tree)

    def test_repo_scoped_dir_rejects_outside_repo(self) -> None:
        with self.assertRaises(ValueError):
            resolve_repo_scoped_dir("/tmp/not-allowed", "passport dir")

    def test_plan_needs_approval_for_review_status(self) -> None:
        with self.temp_in_repo() as tmp:
            artifacts = Path(tmp)
            passport_dir = artifacts / "project_passports"
            passport_dir.mkdir()
            write_passport(passport_dir / "demo.project.yml", local_path=str(artifacts))

            parser = build_parser()
            args = parser.parse_args(["plan", "--slug", "demo", "--passport-dir", str(passport_dir)])
            plan = build_plan(args)

            self.assertTrue(plan.eligible)
            self.assertEqual(plan.policy_status, "needs_approval")
            self.assertIn("operator_approval_required", plan.reasons)

    def test_plan_blocks_unknown_category(self) -> None:
        with self.temp_in_repo() as tmp:
            artifacts = Path(tmp)
            passport_dir = artifacts / "project_passports"
            passport_dir.mkdir()
            write_passport(
                passport_dir / "demo.project.yml",
                category="unknown",
                local_path=str(artifacts),
            )

            parser = build_parser()
            args = parser.parse_args(["plan", "--slug", "demo", "--passport-dir", str(passport_dir)])
            plan = build_plan(args)

            self.assertFalse(plan.eligible)
            self.assertEqual(plan.policy_status, "blocked")
            self.assertIn("classification=unknown", plan.reasons)

    def test_plan_blocks_cerberus(self) -> None:
        with self.temp_in_repo() as tmp:
            artifacts = Path(tmp)
            passport_dir = artifacts / "project_passports"
            passport_dir.mkdir()
            write_passport(
                passport_dir / "cerberus.project.yml",
                slug="cerberus",
                local_path=str(artifacts),
            )

            parser = build_parser()
            args = parser.parse_args(["plan", "--slug", "cerberus", "--passport-dir", str(passport_dir)])
            plan = build_plan(args)

            self.assertFalse(plan.eligible)
            self.assertIn("cerberus_protected", plan.reasons)

    def test_verify_reads_local_git_state(self) -> None:
        with self.temp_in_repo() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            passport_dir = root / "project_passports"
            passport_dir.mkdir()
            write_passport(passport_dir / "demo.project.yml", local_path=str(repo))

            from subprocess import run

            run(["git", "-C", str(repo), "init", "-b", "main"], check=True, capture_output=True, text=True)
            run(["git", "-C", str(repo), "config", "user.email", "tests@example.com"], check=True, capture_output=True, text=True)
            run(["git", "-C", str(repo), "config", "user.name", "Test User"], check=True, capture_output=True, text=True)
            (repo / "README.md").write_text("demo\n", encoding="utf-8")
            run(["git", "-C", str(repo), "add", "README.md"], check=True, capture_output=True, text=True)
            run(["git", "-C", str(repo), "commit", "-m", "init"], check=True, capture_output=True, text=True)

            parser = build_parser()
            args = parser.parse_args(
                [
                    "verify",
                    "--slug",
                    "demo",
                    "--passport-dir",
                    str(passport_dir),
                    "--require-clean-tree",
                ]
            )
            verify = build_verify(args)

            self.assertTrue(verify.remote_state.inside_git_repo)
            self.assertEqual(verify.remote_state.current_branch, "main")
            self.assertEqual(verify.remote_state.clean_working_tree, True)

    def test_verify_require_flags_report_pending_for_not_implemented_checks(self) -> None:
        with self.temp_in_repo() as tmp:
            root = Path(tmp)
            passport_dir = root / "project_passports"
            passport_dir.mkdir()
            write_passport(passport_dir / "demo.project.yml", local_path=str(root))

            parser = build_parser()
            args = parser.parse_args(
                [
                    "verify",
                    "--slug",
                    "demo",
                    "--passport-dir",
                    str(passport_dir),
                    "--require-tests-pass",
                    "--require-doc-reports-current",
                ]
            )
            verify = build_verify(args)

            checks = {check.name: check for check in verify.checks}
            self.assertFalse(checks["tests_pass_check"].passed)
            self.assertFalse(checks["docs_reports_current_check"].passed)
            self.assertIn("pending Phase 7b/8", checks["tests_pass_check"].detail)

    def test_reports_write_in_artifacts_parent(self) -> None:
        with self.temp_in_repo() as tmp:
            root = Path(tmp)
            passport_dir = root / "project_passports"
            passport_dir.mkdir()
            write_passport(passport_dir / "demo.project.yml", local_path=str(root))

            parser = build_parser()
            plan_args = parser.parse_args(["plan", "--slug", "demo", "--passport-dir", str(passport_dir)])
            plan = build_plan(plan_args)
            plan.report_path.parent.mkdir(parents=True, exist_ok=True)
            write_remote_plan_report(plan.report_path, plan)
            self.assertTrue(plan.report_path.exists())

            verify_args = parser.parse_args(["verify", "--slug", "demo", "--passport-dir", str(passport_dir)])
            verify = build_verify(verify_args)
            verify.report_path.parent.mkdir(parents=True, exist_ok=True)
            write_remote_verify_report(verify.report_path, verify)
            self.assertTrue(verify.report_path.exists())


if __name__ == "__main__":
    unittest.main()
