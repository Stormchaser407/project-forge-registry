from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from project_forge_registry.export_sync import (
    apply_sync_plan,
    build_parser,
    build_sync_plan,
    create_sync_plan_from_args,
    parse_relative_export_path,
    repository_artifacts_root,
    resolve_repo_scoped_dir,
)
from project_forge_registry.export_sync_reporting import write_export_sync_report


def write_passport(
    path: Path,
    *,
    slug: str = "demo",
    name: str = "Demo Project",
    category: str = "active_project",
    status: str = "review",
    registry_action: str = "register_full",
    local_path: str = "/projects/demo",
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
                f"  registry_action: {registry_action}",
                f'  local_path: "{local_path}"',
                "  created_by: project-forge-registry",
                "  schema_version: 0.1",
                "paths:",
                f'  local: "{local_path}"',
                "  workspace: /tmp/demo.code-workspace",
                f'  obsidian: "/home/cole/main_vault/10 Projects/{slug}"',
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


class ExportSyncTests(unittest.TestCase):
    def test_default_mode_is_dry_run(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--slug", "demo"])
        self.assertFalse(args.apply)
        self.assertFalse(args.dry_run)

    def test_repo_scoped_paths_reject_outside_repo(self) -> None:
        with self.assertRaises(ValueError):
            resolve_repo_scoped_dir("/tmp/outside", "passport dir")

    def test_parse_relative_export_path_rejects_parent_traversal(self) -> None:
        with self.assertRaises(ValueError):
            parse_relative_export_path("../README.md")

    def test_default_scope_is_export_docs_only(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp, tempfile.TemporaryDirectory() as project_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            vault_root = Path(vault_tmp)
            export_docs_dir = vault_root / "demo" / "_export" / "docs"
            passport_dir.mkdir(parents=True)
            export_docs_dir.mkdir(parents=True)

            write_passport(passport_dir / "demo.project.yml", local_path=project_tmp)
            (vault_root / "demo" / "_export" / "README.md").write_text("# Root README\n", encoding="utf-8")
            (export_docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
            (export_docs_dir / "ignore.py").write_text("print('x')\n", encoding="utf-8")

            plan = build_sync_plan(
                mode="dry-run",
                slug="demo",
                passport_dir=passport_dir,
                vault_project_root=vault_root,
                repo_root_override=None,
                include_files=set(),
                exclude_files=set(),
                report_name="export_sync_report.md",
                backup_suffix="stamp",
            )

            self.assertTrue(plan.entry.eligible)
            self.assertEqual(plan.files_planned, 1)
            self.assertEqual(plan.entry.file_actions[0].destination_path.name, "guide.md")
            self.assertNotIn("README.md", str(plan.entry.file_actions[0].destination_path))
            reasons = {item.reason for item in plan.entry.excluded_files}
            self.assertIn("excluded_suffix=.py", reasons)

    def test_explicit_readme_include_maps_to_docs_readme(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp, tempfile.TemporaryDirectory() as project_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            vault_root = Path(vault_tmp)
            export_root = vault_root / "demo" / "_export"
            passport_dir.mkdir(parents=True)
            export_root.mkdir(parents=True)

            write_passport(passport_dir / "demo.project.yml", local_path=project_tmp)
            (export_root / "README.md").write_text("# Export Root README\n", encoding="utf-8")

            plan = build_sync_plan(
                mode="dry-run",
                slug="demo",
                passport_dir=passport_dir,
                vault_project_root=vault_root,
                repo_root_override=None,
                include_files={Path("README.md")},
                exclude_files=set(),
                report_name="export_sync_report.md",
                backup_suffix="stamp",
            )

            self.assertEqual(plan.files_planned, 1)
            self.assertEqual(plan.entry.file_actions[0].destination_path, Path(project_tmp).resolve() / "docs" / "README.md")

    def test_include_outside_docs_scope_is_excluded(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp, tempfile.TemporaryDirectory() as project_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            vault_root = Path(vault_tmp)
            export_root = vault_root / "demo" / "_export"
            passport_dir.mkdir(parents=True)
            export_root.mkdir(parents=True)

            write_passport(passport_dir / "demo.project.yml", local_path=project_tmp)
            (export_root / "notes.md").write_text("# Notes\n", encoding="utf-8")

            plan = build_sync_plan(
                mode="dry-run",
                slug="demo",
                passport_dir=passport_dir,
                vault_project_root=vault_root,
                repo_root_override=None,
                include_files={Path("notes.md")},
                exclude_files=set(),
                report_name="export_sync_report.md",
                backup_suffix="stamp",
            )

            self.assertEqual(plan.files_planned, 0)
            self.assertIn(
                "include_outside_allowed_scope",
                {item.reason for item in plan.entry.excluded_files},
            )

    def test_repo_root_override_must_stay_inside_docs_root(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp, tempfile.TemporaryDirectory() as project_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            vault_root = Path(vault_tmp)
            export_docs_dir = vault_root / "demo" / "_export" / "docs"
            passport_dir.mkdir(parents=True)
            export_docs_dir.mkdir(parents=True)
            write_passport(passport_dir / "demo.project.yml", local_path=project_tmp)
            (export_docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                build_sync_plan(
                    mode="dry-run",
                    slug="demo",
                    passport_dir=passport_dir,
                    vault_project_root=vault_root,
                    repo_root_override="../outside",
                    include_files=set(),
                    exclude_files=set(),
                    report_name="export_sync_report.md",
                    backup_suffix="stamp",
                )

    def test_safety_flags_and_category_can_skip_plan(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp, tempfile.TemporaryDirectory() as project_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            vault_root = Path(vault_tmp)
            export_docs_dir = vault_root / "demo" / "_export" / "docs"
            passport_dir.mkdir(parents=True)
            export_docs_dir.mkdir(parents=True)
            (export_docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")

            write_passport(
                passport_dir / "demo.project.yml",
                local_path=project_tmp,
                category="unknown",
                do_not_sync=True,
            )

            plan = build_sync_plan(
                mode="dry-run",
                slug="demo",
                passport_dir=passport_dir,
                vault_project_root=vault_root,
                repo_root_override=None,
                include_files=set(),
                exclude_files=set(),
                report_name="export_sync_report.md",
                backup_suffix="stamp",
            )

            self.assertFalse(plan.entry.eligible)
            self.assertIn("safety.do_not_sync=true", plan.entry.reasons)
            self.assertIn("classification=unknown", plan.entry.reasons)
            self.assertEqual(plan.files_planned, 0)

    def test_cerberus_slug_is_protected(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp, tempfile.TemporaryDirectory() as project_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            vault_root = Path(vault_tmp)
            export_docs_dir = vault_root / "cerberus" / "_export" / "docs"
            passport_dir.mkdir(parents=True)
            export_docs_dir.mkdir(parents=True)
            (export_docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")

            write_passport(
                passport_dir / "cerberus.project.yml",
                slug="cerberus",
                local_path=project_tmp,
            )

            plan = build_sync_plan(
                mode="dry-run",
                slug="cerberus",
                passport_dir=passport_dir,
                vault_project_root=vault_root,
                repo_root_override=None,
                include_files=set(),
                exclude_files=set(),
                report_name="export_sync_report.md",
                backup_suffix="stamp",
            )

            self.assertFalse(plan.entry.eligible)
            self.assertIn("cerberus_protected", plan.entry.reasons)

    def test_apply_copies_and_creates_backups(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp, tempfile.TemporaryDirectory() as project_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            vault_root = Path(vault_tmp)
            export_docs_dir = vault_root / "demo" / "_export" / "docs"
            destination_docs_dir = Path(project_tmp) / "docs"
            passport_dir.mkdir(parents=True)
            export_docs_dir.mkdir(parents=True)
            destination_docs_dir.mkdir(parents=True)

            write_passport(passport_dir / "demo.project.yml", local_path=project_tmp)
            (export_docs_dir / "guide.md").write_text("# New Guide\n", encoding="utf-8")
            (destination_docs_dir / "guide.md").write_text("# Old Guide\n", encoding="utf-8")

            plan = build_sync_plan(
                mode="apply",
                slug="demo",
                passport_dir=passport_dir,
                vault_project_root=vault_root,
                repo_root_override=None,
                include_files=set(),
                exclude_files=set(),
                report_name="export_sync_report.md",
                backup_suffix="stamp",
            )

            apply_sync_plan(plan)

            self.assertEqual(plan.files_planned, 1)
            self.assertEqual(plan.files_copied, 1)
            self.assertEqual(plan.backups_created, 1)
            self.assertTrue((destination_docs_dir / "guide.md.bak.stamp").exists())
            self.assertEqual((destination_docs_dir / "guide.md").read_text(encoding="utf-8"), "# New Guide\n")

    def test_cli_dry_run_writes_report_in_temp_artifacts(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp, tempfile.TemporaryDirectory() as project_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            vault_root = Path(vault_tmp)
            export_docs_dir = vault_root / "demo" / "_export" / "docs"
            passport_dir.mkdir(parents=True)
            export_docs_dir.mkdir(parents=True)
            write_passport(passport_dir / "demo.project.yml", local_path=project_tmp)
            (export_docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")

            parser = build_parser()
            args = parser.parse_args(
                [
                    "--slug",
                    "demo",
                    "--dry-run",
                    "--passport-dir",
                    str(passport_dir),
                    "--vault-project-root",
                    str(vault_root),
                ]
            )
            plan = create_sync_plan_from_args(args, parser)
            write_export_sync_report(plan.report_path, plan)

            self.assertTrue(plan.report_path.exists())
            self.assertEqual(plan.report_path.parent.resolve(), artifacts_dir.resolve())
            self.assertFalse((Path(project_tmp) / "docs" / "guide.md").exists())


if __name__ == "__main__":
    unittest.main()
