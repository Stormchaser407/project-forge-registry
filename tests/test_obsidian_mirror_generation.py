from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from project_forge_registry.obsidian_mirror_generation import (
    apply_generation_plan,
    build_generation_plan,
    build_parser,
    create_generation_plan_from_args,
    load_passport_records,
    parse_simple_yaml,
    render_project_home,
    repository_artifacts_root,
    resolve_artifacts_dir,
)
from project_forge_registry.obsidian_mirror_models import ObsidianMirrorPassportRecord
from project_forge_registry.obsidian_mirror_reporting import write_obsidian_mirror_generation_report


def write_passport(
    path: Path,
    *,
    slug: str = "demo",
    name: str = "Demo Project",
    category: str = "active_project",
    status: str = "review",
    local_path: str = "/projects/demo",
    workspace_path: str = "/workspaces/demo.code-workspace",
    obsidian_path: str = "/home/cole/main_vault/10 Projects/demo",
    launcher_command: str = "code-demo",
    allow_code_to_obsidian: bool = False,
    allow_secrets: bool = False,
    do_not_sync: bool = False,
    warnings: list[str] | None = None,
) -> None:
    warning_items = warnings or []
    warning_block = ["  warnings: []"] if not warning_items else ["  warnings:", *(f"    - {item}" for item in warning_items)]
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
                f'  workspace: "{workspace_path}"',
                f'  obsidian: "{obsidian_path}"',
                "launch:",
                f"  command: {launcher_command}",
                "git:",
                "  default_branch: main",
                "  github: null",
                "  codeberg: null",
                "  mirror_mode: disabled_for_now",
                "sync:",
                "  obsidian_to_repo: export_only",
                "  repo_to_obsidian: docs_only",
                f"  allow_code_to_obsidian: {'true' if allow_code_to_obsidian else 'false'}",
                f"  allow_secrets: {'true' if allow_secrets else 'false'}",
                "visibility:",
                "  github: private",
                "  codeberg: private",
                "  public_ready: false",
                "automation:",
                "  auto_doc_sync: false",
                "  auto_git_sync: false",
                "  require_safety_check_before_push: true",
                "safety:",
                *warning_block,
                "  do_not_move: false",
                "  do_not_delete: false",
                f"  do_not_sync: {'true' if do_not_sync else 'false'}",
                "  notes:",
                "    - obsidian_note_policy=docs_only",
                "",
            ]
        ),
        encoding="utf-8",
    )


class ObsidianMirrorGenerationTests(unittest.TestCase):
    def make_record(
        self,
        slug: str,
        *,
        name: str | None = None,
        category: str = "active_project",
        allow_code_to_obsidian: bool = False,
        allow_secrets: bool = False,
        do_not_sync: bool = False,
    ) -> ObsidianMirrorPassportRecord:
        return ObsidianMirrorPassportRecord(
            slug=slug,
            name=name or slug.replace("_", " ").title(),
            category=category,
            status="review",
            local_path=f"/projects/{slug}",
            workspace_path=f"/workspaces/{slug}.code-workspace",
            obsidian_path=f"/home/cole/main_vault/10 Projects/{slug}",
            launcher_command=f"code-{slug}",
            obsidian_to_repo="export_only",
            repo_to_obsidian="docs_only",
            allow_code_to_obsidian=allow_code_to_obsidian,
            allow_secrets=allow_secrets,
            do_not_move=False,
            do_not_delete=False,
            do_not_sync=do_not_sync,
            warnings=(),
            passport_path=Path(f"/passports/{slug}.project.yml"),
        )

    def make_plan(
        self,
        records: list[ObsidianMirrorPassportRecord],
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
                passport_dir=tmp_path / "project_passports",
                artifacts_dir=artifacts_base,
                report_name="report.md",
                include_slugs=include_slugs or set(),
                exclude_slugs=exclude_slugs or set(),
                include_categories=include_categories or set(),
                exclude_categories=exclude_categories or set(),
                backup_suffix="testsuffix",
            )

    def test_parse_simple_yaml_reads_generated_shape(self) -> None:
        payload = parse_simple_yaml(
            "\n".join(
                [
                    "project:",
                    "  slug: demo",
                    '  name: "Demo Project"',
                    "sync:",
                    "  allow_code_to_obsidian: false",
                    "safety:",
                    "  warnings:",
                    "    - one",
                    "    - two",
                    "",
                ]
            )
        )

        self.assertEqual(payload["project"]["slug"], "demo")
        self.assertEqual(payload["project"]["name"], "Demo Project")
        self.assertEqual(payload["sync"]["allow_code_to_obsidian"], False)
        self.assertEqual(payload["safety"]["warnings"], ["one", "two"])

    def test_load_passport_records_reads_passport_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            passport_dir = Path(tmp)
            write_passport(passport_dir / "demo.project.yml")

            records = load_passport_records(passport_dir)

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].slug, "demo")
            self.assertEqual(records[0].launcher_command, "code-demo")

    def test_default_eligible_categories(self) -> None:
        records = [
            self.make_record("active", category="active_project"),
            self.make_record("tool", category="operated_tool"),
            self.make_record("vendor", category="vendor_clone"),
        ]
        plan = self.make_plan(records)

        self.assertEqual({entry.record.slug for entry in plan.eligible_entries}, {"active", "tool"})
        self.assertIn("classification=vendor_clone", plan.skipped_entries[0].reasons)

    def test_sync_protection_flags_skip_generation(self) -> None:
        records = [
            self.make_record("codecopy", allow_code_to_obsidian=True),
            self.make_record("secrets", allow_secrets=True),
            self.make_record("nosync", do_not_sync=True),
        ]
        plan = self.make_plan(records)
        reasons = {entry.record.slug: entry.reasons for entry in plan.skipped_entries}

        self.assertIn("sync.allow_code_to_obsidian=true", reasons["codecopy"])
        self.assertIn("sync.allow_secrets=true", reasons["secrets"])
        self.assertIn("safety.do_not_sync=true", reasons["nosync"])

    def test_cerberus_related_records_are_protected(self) -> None:
        plan = self.make_plan([self.make_record("cerberus_helper")])

        self.assertEqual(len(plan.eligible_entries), 0)
        self.assertIn("cerberus_protected", plan.skipped_entries[0].reasons)

    def test_project_home_contains_required_links_and_sections(self) -> None:
        text = render_project_home(self.make_record("demo", name="Demo Project"))

        self.assertIn("[[Project Command Board]]", text)
        self.assertIn("[[Demo Project - Demo Script]]", text)
        self.assertIn("## Purpose", text)
        self.assertIn("## Current Risks / Watch Items", text)
        self.assertIn("## Links and Commands", text)

    def test_explicit_category_include_allows_vendor_clone(self) -> None:
        plan = self.make_plan(
            [self.make_record("vendor", category="vendor_clone")],
            include_categories={"vendor_clone"},
        )

        self.assertEqual({entry.record.slug for entry in plan.eligible_entries}, {"vendor"})

    def test_artifacts_dir_must_stay_inside_repo_artifacts(self) -> None:
        with self.assertRaises(ValueError):
            resolve_artifacts_dir("/tmp/not-allowed")

    def test_dry_run_only_writes_report(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as passport_tmp:
            passport_dir = Path(passport_tmp)
            write_passport(passport_dir / "demo.project.yml")

            parser = build_parser()
            args = parser.parse_args(
                [
                    "--dry-run",
                    "--passport-dir",
                    str(passport_dir),
                    "--artifacts-dir",
                    str(Path(artifacts_tmp)),
                ]
            )
            plan = create_generation_plan_from_args(args, parser)
            plan.artifacts_dir.mkdir(parents=True, exist_ok=True)
            write_obsidian_mirror_generation_report(plan.report_path, plan)

            self.assertTrue(plan.report_path.exists())
            self.assertFalse((Path(artifacts_tmp) / "obsidian_mirrors").exists())

    def test_apply_writes_mirror_files_inside_artifacts(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as passport_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = Path(passport_tmp)
            write_passport(passport_dir / "demo.project.yml")

            plan = build_generation_plan(
                records=load_passport_records(passport_dir),
                mode="apply",
                passport_dir=passport_dir,
                artifacts_dir=artifacts_dir,
                report_name="report.md",
                include_slugs=set(),
                exclude_slugs=set(),
                include_categories=set(),
                exclude_categories=set(),
                backup_suffix="stamp",
            )

            apply_generation_plan(plan)
            write_obsidian_mirror_generation_report(plan.report_path, plan)

            mirror_dir = artifacts_dir / "obsidian_mirrors" / "demo"
            self.assertTrue((mirror_dir / "Demo Project - Project Home.md").exists())
            self.assertTrue((mirror_dir / "Demo Script.md").exists())
            self.assertTrue((mirror_dir / "_export" / "README.md").exists())
            self.assertTrue((mirror_dir / "_export" / "docs").exists())
            self.assertEqual(plan.written_count, 9)


if __name__ == "__main__":
    unittest.main()
