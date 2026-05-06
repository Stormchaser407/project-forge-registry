from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

from project_forge_registry.workspace_generation import (
    DEFAULT_PROTECTED_WORKSPACE,
    apply_generation_plan,
    build_generation_plan,
    build_parser,
    create_generation_plan_from_args,
    ensure_allowed_target,
    normalize_report_name,
    repository_artifacts_root,
    resolve_artifacts_dir,
)
from project_forge_registry.workspace_models import WorkspaceProjectRecord
from project_forge_registry.workspace_reporting import write_workspace_generation_report


class WorkspaceGenerationTests(unittest.TestCase):
    def make_record(
        self,
        slug: str,
        *,
        category: str = "active_project",
        registry_action: str = "register_full",
        local_path: str | None = None,
    ) -> WorkspaceProjectRecord:
        return WorkspaceProjectRecord(
            slug=slug,
            name=slug.replace("_", " "),
            local_path=local_path or f"/projects/{slug}",
            category=category,
            registry_action=registry_action,
            do_not_sync=False,
            safety_warnings=(),
        )

    def make_plan(
        self,
        records: list[WorkspaceProjectRecord],
        *,
        include_categories: set[str] | None = None,
        exclude_categories: set[str] | None = None,
        include_slugs: set[str] | None = None,
        exclude_slugs: set[str] | None = None,
        preserved_workspaces: set[str] | None = None,
        workspace_dir: Path | None = None,
        launcher_dir: Path | None = None,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workspace_base = workspace_dir or (tmp_path / "workspaces")
            launcher_base = launcher_dir or (tmp_path / "bin")
            artifacts_base = repository_artifacts_root() / "test-artifacts"
            return build_generation_plan(
                records=records,
                mode="dry-run",
                input_json_path=tmp_path / "input.json",
                artifacts_dir=artifacts_base,
                report_name="report.md",
                workspace_dir=workspace_base,
                launcher_dir=launcher_base,
                include_slugs=include_slugs or set(),
                exclude_slugs=exclude_slugs or set(),
                include_categories=include_categories or set(),
                exclude_categories=exclude_categories or set(),
                preserved_workspaces=preserved_workspaces or {DEFAULT_PROTECTED_WORKSPACE},
                backup_suffix="testsuffix",
            )

    def test_default_eligible_categories(self) -> None:
        records = [
            self.make_record("active", category="active_project"),
            self.make_record("tool", category="operated_tool", registry_action="workspace_only"),
            self.make_record("vendor", category="vendor_clone", registry_action="workspace_only"),
            self.make_record("lab", category="lab", registry_action="workspace_only"),
        ]
        plan = self.make_plan(records)

        eligible_slugs = {entry.record.slug for entry in plan.eligible_entries}
        skipped = {entry.record.slug: entry.reasons for entry in plan.skipped_entries}

        self.assertEqual(eligible_slugs, {"active", "tool"})
        self.assertIn("classification=vendor_clone_requires_explicit_include", skipped["vendor"])
        self.assertIn("classification=lab_requires_explicit_include", skipped["lab"])

    def test_explicit_category_includes_work_for_vendor_clone_and_lab(self) -> None:
        records = [
            self.make_record("vendor", category="vendor_clone", registry_action="workspace_only"),
            self.make_record("lab", category="lab", registry_action="workspace_only"),
        ]
        plan = self.make_plan(records, include_categories={"vendor_clone", "lab"})

        self.assertEqual({entry.record.slug for entry in plan.eligible_entries}, {"vendor", "lab"})

    def test_forced_skip_categories_always_skip(self) -> None:
        records = [
            self.make_record("bound", category="system_bound_project"),
            self.make_record("reconcile", category="reconciliation_required", registry_action="workspace_only"),
        ]
        plan = self.make_plan(records, include_categories={"system_bound_project", "reconciliation_required"})

        skipped = {entry.record.slug: entry.reasons for entry in plan.skipped_entries}
        self.assertIn("classification=system_bound_project", skipped["bound"])
        self.assertIn("classification=reconciliation_required", skipped["reconcile"])

    def test_preserved_workspace_name_skips_generation(self) -> None:
        record = self.make_record(
            "project-forge-command-center",
            local_path="/projects/project-forge-command-center",
        )
        plan = self.make_plan(records=[record])

        self.assertEqual(len(plan.eligible_entries), 0)
        self.assertIn(
            "preserved_workspace=project-forge-command-center.code-workspace",
            plan.skipped_entries[0].reasons,
        )

    def test_path_guard_rejects_nested_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaises(ValueError):
                ensure_allowed_target(base / "nested" / "demo.code-workspace", base, "demo.code-workspace")

    def test_artifacts_dir_must_stay_inside_repo_artifacts(self) -> None:
        with self.assertRaises(ValueError):
            resolve_artifacts_dir("/tmp/not-allowed")

    def test_report_name_must_be_filename(self) -> None:
        with self.assertRaises(ValueError):
            normalize_report_name("../report.md")

    def test_backup_paths_are_planned_for_existing_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workspace_dir = tmp_path / "workspaces"
            launcher_dir = tmp_path / "bin"
            workspace_dir.mkdir()
            launcher_dir.mkdir()
            (workspace_dir / "demo.code-workspace").write_text("old", encoding="utf-8")
            (launcher_dir / "code-demo").write_text("old", encoding="utf-8")

            plan = build_generation_plan(
                records=[self.make_record("demo")],
                mode="dry-run",
                input_json_path=tmp_path / "input.json",
                artifacts_dir=repository_artifacts_root() / "test-artifacts",
                report_name="report.md",
                workspace_dir=workspace_dir,
                launcher_dir=launcher_dir,
                include_slugs=set(),
                exclude_slugs=set(),
                include_categories=set(),
                exclude_categories=set(),
                preserved_workspaces={DEFAULT_PROTECTED_WORKSPACE},
                backup_suffix="stamp",
            )

        entry = plan.eligible_entries[0]
        self.assertEqual(entry.planned_backup_count, 2)
        self.assertEqual(entry.file_actions[0].backup_path.name, "demo.code-workspace.bak.stamp")
        self.assertEqual(entry.file_actions[1].backup_path.name, "code-demo.bak.stamp")

    def test_dry_run_only_writes_report(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_json = tmp_path / "input.json"
            workspace_dir = tmp_path / "workspaces"
            launcher_dir = tmp_path / "bin"
            input_json.write_text(
                json.dumps(
                    {
                        "projects": [
                            {
                                "safe_slug": "demo",
                                "folder_name": "demo",
                                "path": "/projects/demo",
                                "recommended_category": "active_project",
                                "recommended_action": "register_full",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            parser = build_parser()
            args = parser.parse_args(
                [
                    "--dry-run",
                    "--input-json",
                    str(input_json),
                    "--artifacts-dir",
                    str(Path(artifacts_tmp)),
                    "--workspace-dir",
                    str(workspace_dir),
                    "--launcher-dir",
                    str(launcher_dir),
                ]
            )
            plan = create_generation_plan_from_args(args, parser)
            plan.artifacts_dir.mkdir(parents=True, exist_ok=True)
            write_workspace_generation_report(plan.report_path, plan)

            self.assertTrue(plan.report_path.exists())
            self.assertFalse(workspace_dir.exists())
            self.assertFalse(launcher_dir.exists())

    def test_apply_writes_workspace_and_launcher_and_backups(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workspace_dir = tmp_path / "workspaces"
            launcher_dir = tmp_path / "bin"
            workspace_dir.mkdir()
            launcher_dir.mkdir()
            existing_workspace = workspace_dir / "demo.code-workspace"
            existing_launcher = launcher_dir / "code-demo"
            existing_workspace.write_text("old-workspace", encoding="utf-8")
            existing_launcher.write_text("old-launcher", encoding="utf-8")

            plan = build_generation_plan(
                records=[self.make_record("demo")],
                mode="apply",
                input_json_path=tmp_path / "input.json",
                artifacts_dir=Path(artifacts_tmp),
                report_name="report.md",
                workspace_dir=workspace_dir,
                launcher_dir=launcher_dir,
                include_slugs=set(),
                exclude_slugs=set(),
                include_categories=set(),
                exclude_categories=set(),
                preserved_workspaces={DEFAULT_PROTECTED_WORKSPACE},
                backup_suffix="stamp",
            )

            apply_generation_plan(plan)
            write_workspace_generation_report(plan.report_path, plan)

            workspace_text = existing_workspace.read_text(encoding="utf-8")
            launcher_text = existing_launcher.read_text(encoding="utf-8")

            self.assertIn('"path": "/projects/demo"', workspace_text)
            self.assertIn('exec code "', launcher_text)
            self.assertTrue((workspace_dir / "demo.code-workspace.bak.stamp").exists())
            self.assertTrue((launcher_dir / "code-demo.bak.stamp").exists())
            self.assertTrue(plan.report_path.exists())
            self.assertEqual(plan.written_count, 2)
            self.assertEqual(plan.backup_count, 2)

    def test_excluded_action_is_skipped(self) -> None:
        plan = self.make_plan(
            [self.make_record("review", registry_action="review_required")],
        )

        self.assertEqual(len(plan.eligible_entries), 0)
        self.assertIn("registry_action=review_required", plan.skipped_entries[0].reasons)

    def test_do_not_sync_and_cerberus_warning_are_explicit_skip_reasons(self) -> None:
        record = WorkspaceProjectRecord(
            slug="cerberus",
            name="Cerberus",
            local_path="/projects/Cerberus",
            category="unknown",
            registry_action="review_required",
            do_not_sync=True,
            safety_warnings=("cerberus_special_case_candidate",),
        )
        plan = self.make_plan([record])

        reasons = plan.skipped_entries[0].reasons
        self.assertIn("do_not_sync=true", reasons)
        self.assertIn("safety_warning=cerberus_special_case_candidate", reasons)


if __name__ == "__main__":
    unittest.main()
