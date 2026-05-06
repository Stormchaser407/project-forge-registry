from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from project_forge_registry.passport_generation import (
    apply_generation_plan,
    build_generation_plan,
    build_parser,
    create_generation_plan_from_args,
    ensure_allowed_target,
    normalize_report_name,
    render_passport_yaml,
    repository_artifacts_root,
    resolve_artifacts_dir,
)
from project_forge_registry.passport_models import PassportProjectRecord
from project_forge_registry.passport_reporting import write_passport_generation_report


class PassportGenerationTests(unittest.TestCase):
    def make_record(
        self,
        slug: str,
        *,
        category: str = "active_project",
        status: str = "review",
        registry_action: str = "register_full",
        local_path: str | None = None,
        do_not_sync: bool = False,
        safety_warnings: tuple[str, ...] = (),
    ) -> PassportProjectRecord:
        return PassportProjectRecord(
            slug=slug,
            name=slug.replace("_", " "),
            local_path=local_path or f"/projects/{slug}",
            category=category,
            status=status,
            registry_action=registry_action,
            canonical_path=None,
            has_git=True,
            do_not_move=False,
            do_not_delete=False,
            do_not_sync=do_not_sync,
            exclude_from_bulk_sync=False,
            obsidian_note_policy="docs_only",
            safety_warnings=safety_warnings,
        )

    def make_plan(
        self,
        records: list[PassportProjectRecord],
        *,
        include_categories: set[str] | None = None,
        exclude_categories: set[str] | None = None,
        include_slugs: set[str] | None = None,
        exclude_slugs: set[str] | None = None,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            artifacts_base = repository_artifacts_root() / "test-artifacts"
            return build_generation_plan(
                records=records,
                mode="dry-run",
                input_json_path=tmp_path / "input.json",
                artifacts_dir=artifacts_base,
                report_name="report.md",
                include_slugs=include_slugs or set(),
                exclude_slugs=exclude_slugs or set(),
                include_categories=include_categories or set(),
                exclude_categories=exclude_categories or set(),
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
        self.assertIn("classification=vendor_clone", skipped["vendor"])
        self.assertIn("classification=lab", skipped["lab"])

    def test_forced_skip_categories_always_skip(self) -> None:
        records = [
            self.make_record("bound", category="system_bound_project"),
            self.make_record("reconcile", category="reconciliation_required", registry_action="workspace_only"),
        ]
        plan = self.make_plan(records, include_categories={"system_bound_project", "reconciliation_required"})

        skipped = {entry.record.slug: entry.reasons for entry in plan.skipped_entries}
        self.assertIn("classification=system_bound_project", skipped["bound"])
        self.assertIn("classification=reconciliation_required", skipped["reconcile"])

    def test_do_not_sync_and_cerberus_are_explicit_skip_reasons(self) -> None:
        record = self.make_record(
            "cerberus_helper",
            category="active_project",
            local_path="/projects/cerberus-helper",
            do_not_sync=True,
            safety_warnings=("cerberus_special_case_candidate",),
        )
        plan = self.make_plan([record])

        reasons = plan.skipped_entries[0].reasons
        self.assertIn("do_not_sync=true", reasons)
        self.assertIn("safety_warning=cerberus_special_case_candidate", reasons)
        self.assertIn("cerberus_protected", reasons)

    def test_path_guard_rejects_nested_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaises(ValueError):
                ensure_allowed_target(base / "nested" / "demo.project.yml", base, "demo.project.yml")

    def test_artifacts_dir_must_stay_inside_repo_artifacts(self) -> None:
        with self.assertRaises(ValueError):
            resolve_artifacts_dir("/tmp/not-allowed")

    def test_report_name_must_be_filename(self) -> None:
        with self.assertRaises(ValueError):
            normalize_report_name("../report.md")

    def test_rendered_yaml_contains_required_schema_sections(self) -> None:
        yaml_text = render_passport_yaml(self.make_record("demo"))

        self.assertIn("project:", yaml_text)
        self.assertIn("schema_version: 0.1", yaml_text)
        self.assertIn("paths:", yaml_text)
        self.assertIn("launch:", yaml_text)
        self.assertIn("git:", yaml_text)
        self.assertIn("sync:", yaml_text)
        self.assertIn("visibility:", yaml_text)
        self.assertIn("automation:", yaml_text)
        self.assertIn("safety:", yaml_text)

    def test_backup_paths_are_planned_for_existing_proposals(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passports_dir = artifacts_dir / "project_passports"
            passports_dir.mkdir()
            (passports_dir / "demo.project.yml").write_text("old", encoding="utf-8")

            plan = build_generation_plan(
                records=[self.make_record("demo")],
                mode="apply",
                input_json_path=artifacts_dir / "input.json",
                artifacts_dir=artifacts_dir,
                report_name="report.md",
                include_slugs=set(),
                exclude_slugs=set(),
                include_categories=set(),
                exclude_categories=set(),
                backup_suffix="stamp",
            )

            entry = plan.eligible_entries[0]
            self.assertEqual(entry.planned_backup_count, 1)
            assert entry.file_action is not None
            self.assertEqual(entry.file_action.backup_path.name, "demo.project.yml.bak.stamp")

    def test_dry_run_only_writes_report(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_json = tmp_path / "input.json"
            input_json.write_text(
                json.dumps(
                    {
                        "projects": [
                            {
                                "safe_slug": "demo",
                                "folder_name": "demo",
                                "path": "/projects/demo",
                                "recommended_category": "active_project",
                                "recommended_status": "review",
                                "recommended_action": "register_full",
                                "has_git": True,
                                "do_not_move": False,
                                "do_not_delete": False,
                                "do_not_sync": False,
                                "exclude_from_bulk_sync": False,
                                "obsidian_note_policy": "docs_only",
                                "safety_warnings": [],
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
                ]
            )
            plan = create_generation_plan_from_args(args, parser)
            plan.artifacts_dir.mkdir(parents=True, exist_ok=True)
            write_passport_generation_report(plan.report_path, plan)

            self.assertTrue(plan.report_path.exists())
            self.assertFalse((Path(artifacts_tmp) / "project_passports").exists())

    def test_apply_writes_passports_and_backups_inside_artifacts(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passports_dir = artifacts_dir / "project_passports"
            passports_dir.mkdir()
            existing_proposal = passports_dir / "demo.project.yml"
            existing_proposal.write_text("old-passport", encoding="utf-8")

            plan = build_generation_plan(
                records=[self.make_record("demo")],
                mode="apply",
                input_json_path=artifacts_dir / "input.json",
                artifacts_dir=artifacts_dir,
                report_name="report.md",
                include_slugs=set(),
                exclude_slugs=set(),
                include_categories=set(),
                exclude_categories=set(),
                backup_suffix="stamp",
            )

            apply_generation_plan(plan)
            write_passport_generation_report(plan.report_path, plan)

            proposal_text = existing_proposal.read_text(encoding="utf-8")

            self.assertIn("slug: demo", proposal_text)
            self.assertIn("created_by: project-forge-registry", proposal_text)
            self.assertTrue((passports_dir / "demo.project.yml.bak.stamp").exists())
            self.assertTrue(plan.report_path.exists())
            self.assertEqual(plan.written_count, 1)
            self.assertEqual(plan.backup_count, 1)


if __name__ == "__main__":
    unittest.main()
