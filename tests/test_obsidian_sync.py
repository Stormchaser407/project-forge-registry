from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from project_forge_registry.obsidian_sync import (
    apply_sync_plan,
    build_parser,
    build_sync_plan,
    create_sync_plan_from_args,
    repository_artifacts_root,
    resolve_repo_scoped_dir,
)
from project_forge_registry.obsidian_sync_reporting import write_obsidian_sync_report


def write_passport(
    path: Path,
    *,
    slug: str = "demo",
    name: str = "Demo Project",
    category: str = "active_project",
    status: str = "review",
    local_path: str = "/projects/demo",
    obsidian_path: str = "/home/cole/main_vault/10 Projects/demo",
    allow_code_to_obsidian: bool = False,
    allow_secrets: bool = False,
    do_not_sync: bool = False,
) -> None:
    path.write_text(
        "\n".join(
            [
                "project:",
                f"  slug: {slug}",
                f'  name: "{name}"',
                f"  category: {category}",
                f"  status: {status}",
                "  registry_action: register_full",
                f'  local_path: "{local_path}"',
                "  created_by: project-forge-registry",
                "  schema_version: 0.1",
                "paths:",
                f'  local: "{local_path}"',
                "  workspace: /tmp/demo.code-workspace",
                f'  obsidian: "{obsidian_path}"',
                "launch:",
                "  command: code-demo",
                "sync:",
                "  obsidian_to_repo: export_only",
                "  repo_to_obsidian: docs_only",
                f"  allow_code_to_obsidian: {'true' if allow_code_to_obsidian else 'false'}",
                f"  allow_secrets: {'true' if allow_secrets else 'false'}",
                "safety:",
                "  warnings: []",
                f"  do_not_sync: {'true' if do_not_sync else 'false'}",
                "",
            ]
        ),
        encoding="utf-8",
    )


class ObsidianSyncTests(unittest.TestCase):
    def test_default_mode_is_dry_run(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--slug", "demo"])
        self.assertFalse(args.apply)
        self.assertFalse(args.dry_run)

    def test_repo_scoped_paths_reject_outside_repo(self) -> None:
        with self.assertRaises(ValueError):
            resolve_repo_scoped_dir("/tmp/outside", "mirror dir")

    def test_dry_run_plans_markdown_only_and_records_exclusions(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            mirror_dir = artifacts_dir / "obsidian_mirrors"
            source_dir = mirror_dir / "demo"
            passport_dir.mkdir(parents=True)
            source_dir.mkdir(parents=True)

            write_passport(passport_dir / "demo.project.yml")
            (source_dir / "Project Home.md").write_text("# Home\n", encoding="utf-8")
            (source_dir / "notes.py").write_text("print('x')\n", encoding="utf-8")
            (source_dir / "Runbook.md.bak.20260513").write_text("old\n", encoding="utf-8")
            (source_dir / ".env").write_text("SECRET=x\n", encoding="utf-8")
            (source_dir / "_export").mkdir(parents=True)
            (source_dir / "_export" / "README.md").write_text("# export\n", encoding="utf-8")
            (source_dir / "node_modules").mkdir(parents=True)
            (source_dir / "node_modules" / "keep.md").write_text("# blocked\n", encoding="utf-8")

            plan = build_sync_plan(
                mode="dry-run",
                slug="demo",
                passport_dir=passport_dir,
                mirror_dir=mirror_dir,
                vault_project_root=Path(vault_tmp),
                report_name="obsidian_sync_report.md",
                backup_suffix="stamp",
            )

            self.assertTrue(plan.entry.eligible)
            self.assertEqual(plan.files_planned, 2)
            self.assertEqual(plan.files_copied, 0)
            excluded_reasons = {item.reason for item in plan.entry.excluded_files}
            self.assertIn("excluded_suffix=.py", excluded_reasons)
            self.assertIn("excluded_bak_file", excluded_reasons)
            self.assertIn("excluded_env_file", excluded_reasons)
            self.assertIn("excluded_directory", excluded_reasons)

    def test_apply_copies_markdown_and_creates_backup_on_overwrite(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            mirror_dir = artifacts_dir / "obsidian_mirrors"
            source_dir = mirror_dir / "demo"
            destination_root = Path(vault_tmp)
            destination_dir = destination_root / "demo"

            passport_dir.mkdir(parents=True)
            source_dir.mkdir(parents=True)
            destination_dir.mkdir(parents=True)

            write_passport(passport_dir / "demo.project.yml")
            (source_dir / "Project Home.md").write_text("# New Home\n", encoding="utf-8")
            (destination_dir / "Project Home.md").write_text("# Old Home\n", encoding="utf-8")

            plan = build_sync_plan(
                mode="apply",
                slug="demo",
                passport_dir=passport_dir,
                mirror_dir=mirror_dir,
                vault_project_root=destination_root,
                report_name="obsidian_sync_report.md",
                backup_suffix="stamp",
            )

            apply_sync_plan(plan)

            self.assertEqual(plan.files_planned, 1)
            self.assertEqual(plan.files_copied, 1)
            self.assertEqual(plan.backups_created, 1)
            self.assertTrue((destination_dir / "Project Home.md.bak.stamp").exists())
            self.assertEqual((destination_dir / "Project Home.md").read_text(encoding="utf-8"), "# New Home\n")

    def test_cerberus_slug_is_protected_and_not_applied(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            mirror_dir = artifacts_dir / "obsidian_mirrors"
            source_dir = mirror_dir / "cerberus"
            passport_dir.mkdir(parents=True)
            source_dir.mkdir(parents=True)

            write_passport(
                passport_dir / "cerberus.project.yml",
                slug="cerberus",
                local_path="/home/cole/cerberus",
            )
            (source_dir / "Project Home.md").write_text("# Do Not Sync\n", encoding="utf-8")

            plan = build_sync_plan(
                mode="apply",
                slug="cerberus",
                passport_dir=passport_dir,
                mirror_dir=mirror_dir,
                vault_project_root=Path(vault_tmp),
                report_name="obsidian_sync_report.md",
                backup_suffix="stamp",
            )

            apply_sync_plan(plan)
            self.assertFalse(plan.entry.eligible)
            self.assertIn("cerberus_protected", plan.entry.reasons)
            self.assertEqual(plan.files_copied, 0)

    def test_cli_dry_run_writes_report_without_writing_vault(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            mirror_dir = artifacts_dir / "obsidian_mirrors"
            source_dir = mirror_dir / "demo"
            passport_dir.mkdir(parents=True)
            source_dir.mkdir(parents=True)

            write_passport(passport_dir / "demo.project.yml")
            (source_dir / "Project Home.md").write_text("# Home\n", encoding="utf-8")

            parser = build_parser()
            args = parser.parse_args(
                [
                    "--slug",
                    "demo",
                    "--dry-run",
                    "--passport-dir",
                    str(passport_dir),
                    "--mirror-dir",
                    str(mirror_dir),
                    "--vault-project-root",
                    str(Path(vault_tmp)),
                ]
            )
            plan = create_sync_plan_from_args(args, parser)
            write_obsidian_sync_report(plan.report_path, plan)

            self.assertTrue(plan.report_path.exists())
            self.assertFalse((Path(vault_tmp) / "demo").exists())


if __name__ == "__main__":
    unittest.main()
