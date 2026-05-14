from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path

from project_forge_registry.project_sync import (
    build_parser,
    build_lane_specs,
    derive_final_status,
    determine_lane_selection_mode,
    detect_protected_project,
    parse_mode,
    repository_root,
    resolve_repo_scoped_dir,
    write_report,
    LaneResult,
)


class ProjectSyncTests(unittest.TestCase):
    def test_default_mode_is_dry_run(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--slug", "demo"])
        self.assertEqual(parse_mode(args, parser), "dry-run")

    def test_apply_is_rejected_in_phase_8_4(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--slug", "demo", "--apply"])
        with self.assertRaises(SystemExit):
            parse_mode(args, parser)

    def test_default_profile_selects_safe_dry_run_lanes_only(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--slug", "demo"])

        specs = {spec.key: spec for spec in build_lane_specs(args)}

        self.assertEqual(determine_lane_selection_mode(args), "default_profile")
        self.assertFalse(specs["refresh_scan"].requested)
        self.assertFalse(specs["refresh_workspace"].requested)
        self.assertFalse(specs["refresh_passport"].requested)
        self.assertFalse(specs["refresh_mirror"].requested)
        self.assertTrue(specs["sync_obsidian"].requested)
        self.assertTrue(specs["export_docs"].requested)
        self.assertTrue(specs["remote_plan"].requested)
        self.assertTrue(specs["remote_verify"].requested)
        self.assertTrue(specs["push_ready"].requested)

    def test_explicit_lane_flags_select_only_requested_lanes(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--slug", "demo", "--sync-obsidian", "--remote-plan"])

        specs = {spec.key: spec for spec in build_lane_specs(args)}

        self.assertEqual(determine_lane_selection_mode(args), "explicit")
        self.assertTrue(specs["sync_obsidian"].requested)
        self.assertTrue(specs["remote_plan"].requested)
        self.assertFalse(specs["export_docs"].requested)
        self.assertFalse(specs["remote_verify"].requested)
        self.assertFalse(specs["push_ready"].requested)
        self.assertFalse(specs["refresh_workspace"].requested)

    def test_internal_lanes_use_python_module_commands(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "--slug",
                "demo",
                "--refresh-workspace",
                "--refresh-passport",
                "--refresh-mirror",
                "--sync-obsidian",
                "--export-docs",
                "--remote-plan",
                "--remote-verify",
                "--push-ready",
            ]
        )

        commands = {spec.key: spec.command for spec in build_lane_specs(args)}

        expected_modules = {
            "refresh_workspace": "project_forge_registry.workspace_generation",
            "refresh_passport": "project_forge_registry.passport_generation",
            "refresh_mirror": "project_forge_registry.obsidian_mirror_generation",
            "sync_obsidian": "project_forge_registry.obsidian_sync",
            "export_docs": "project_forge_registry.export_sync",
            "remote_plan": "project_forge_registry.remote_policy",
            "remote_verify": "project_forge_registry.remote_policy",
            "push_ready": "project_forge_registry.remote_policy",
        }
        for key, module_name in expected_modules.items():
            command = commands[key]
            self.assertIsNotNone(command)
            self.assertEqual(command[:3], [sys.executable, "-m", module_name])

        self.assertIn("--include-slug", commands["refresh_workspace"])
        self.assertIn("--include-slug", commands["refresh_passport"])
        self.assertIn("--include-slug", commands["refresh_mirror"])
        self.assertIn("plan", commands["remote_plan"])
        self.assertIn("verify", commands["remote_verify"])
        self.assertIn("push-ready", commands["push_ready"])

    def test_internal_lanes_use_project_sync_report_names(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "--slug",
                "demo",
                "--refresh-workspace",
                "--refresh-passport",
                "--refresh-mirror",
                "--sync-obsidian",
                "--export-docs",
                "--remote-plan",
                "--remote-verify",
                "--push-ready",
            ]
        )

        specs = {spec.key: spec for spec in build_lane_specs(args)}
        expected_report_names = {
            "refresh_workspace": "project_sync_workspace_generation_report.md",
            "refresh_passport": "project_sync_passport_generation_report.md",
            "refresh_mirror": "project_sync_obsidian_mirror_generation_report.md",
            "sync_obsidian": "project_sync_obsidian_sync_report.md",
            "export_docs": "project_sync_export_sync_report.md",
            "remote_plan": "project_sync_remote_plan_report.md",
            "remote_verify": "project_sync_remote_verify_report.md",
            "push_ready": "project_sync_push_ready_report.md",
        }
        canonical_report_names = {
            "workspace_launcher_generation_report.md",
            "project_passport_generation_report.md",
            "obsidian_mirror_generation_report.md",
            "obsidian_sync_report.md",
            "export_sync_report.md",
            "remote_plan_report.md",
            "remote_verify_report.md",
            "push_ready_report.md",
        }

        for key, report_name in expected_report_names.items():
            command = specs[key].command
            self.assertIsNotNone(command)
            self.assertEqual(specs[key].report_name, report_name)
            self.assertIn("--report-name", command)
            self.assertIn(report_name, command)
            self.assertTrue(canonical_report_names.isdisjoint(command))

    def test_repo_scoped_paths_reject_outside_repo(self) -> None:
        with self.assertRaises(ValueError):
            resolve_repo_scoped_dir("/tmp/outside", "passport dir")

    def test_unrequested_skipped_lanes_do_not_make_final_status_incomplete(self) -> None:
        results = [
            LaneResult("sync_obsidian", "Obsidian Sync", True, "passed", ["python"], 0, "ok"),
            LaneResult("export_docs", "Export Docs", True, "passed", ["python"], 0, "ok"),
            LaneResult("remote_plan", "Remote Plan", False, "skipped", ["python"], None, "not requested"),
        ]

        self.assertEqual(derive_final_status(False, results), "ready_for_operator_review")

    def test_final_status_never_uses_ready_to_push(self) -> None:
        passing_results = [
            LaneResult("sync_obsidian", "Obsidian Sync", True, "passed", ["python"], 0, "ok"),
            LaneResult("push_ready", "Push Ready", True, "passed", ["python"], 0, "ok"),
        ]
        failing_results = [
            LaneResult("sync_obsidian", "Obsidian Sync", True, "failed", ["python"], 1, "lane_failed"),
        ]

        statuses = {
            derive_final_status(False, passing_results),
            derive_final_status(False, failing_results),
            derive_final_status(True, passing_results),
        }
        self.assertNotIn("ready_to_push", statuses)

    def test_requested_failed_lane_blocks_final_status(self) -> None:
        results = [
            LaneResult("sync_obsidian", "Obsidian Sync", True, "passed", ["python"], 0, "ok"),
            LaneResult("export_docs", "Export Docs", True, "failed", ["python"], 1, "lane_failed"),
            LaneResult("remote_plan", "Remote Plan", False, "skipped", ["python"], None, "not requested"),
        ]

        self.assertEqual(derive_final_status(False, results), "blocked")

    def test_requested_skipped_lane_marks_final_status_incomplete(self) -> None:
        results = [
            LaneResult("refresh_scan", "Refresh Classification", True, "skipped", None, None, "missing evidence"),
            LaneResult("remote_plan", "Remote Plan", False, "skipped", ["python"], None, "not requested"),
        ]

        self.assertEqual(derive_final_status(False, results), "incomplete")

    def test_detect_protected_project_from_slug_and_passport(self) -> None:
        with tempfile.TemporaryDirectory(dir=repository_root() / "artifacts") as artifacts_tmp:
            passport_dir = Path(artifacts_tmp) / "project_passports"
            passport_dir.mkdir(parents=True)
            passport_path = passport_dir / "cerberus.project.yml"
            passport_path.write_text(
                "\n".join(
                    [
                        "project:",
                        "  slug: cerberus",
                        '  name: "Cerberus"',
                        "  category: active_project",
                        "  status: review",
                        "  registry_action: register_full",
                        '  local_path: "/home/cole/cerberus"',
                        "safety:",
                        "  warnings: []",
                        "  do_not_sync: false",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            reasons = detect_protected_project(passport_path, "cerberus")
            self.assertIn("cerberus_protected", reasons)

    def test_report_writer_outputs_status(self) -> None:
        with tempfile.TemporaryDirectory(dir=repository_root() / "artifacts") as artifacts_tmp:
            report_path = Path(artifacts_tmp) / "project_sync_report.md"
            write_report(
                report_path,
                mode="dry-run",
                slug="demo",
                lane_selection_mode="default_profile",
                passport_path=Path("artifacts/project_passports/demo.project.yml"),
                protected_reasons=[],
                results=[
                    LaneResult(
                        key="refresh_workspace",
                        title="Refresh Workspace",
                        requested=True,
                        status="passed",
                        command=[
                            sys.executable,
                            "-m",
                            "project_forge_registry.workspace_generation",
                            "--dry-run",
                            "--include-slug",
                            "demo",
                        ],
                        return_code=0,
                        note="ok",
                        report_name="project_sync_workspace_generation_report.md",
                    ),
                    LaneResult(
                        key="remote_plan",
                        title="Remote Plan",
                        requested=False,
                        status="skipped",
                        command=[
                            sys.executable,
                            "-m",
                            "project_forge_registry.remote_policy",
                            "plan",
                            "--dry-run",
                            "--slug",
                            "demo",
                        ],
                        return_code=None,
                        note="not requested",
                        report_name="project_sync_remote_plan_report.md",
                    )
                ],
                final_status="ready_for_operator_review",
            )
            text = report_path.read_text(encoding="utf-8")
            self.assertIn("# Project Sync Report (Phase 8.4)", text)
            self.assertIn("lane_selection: `default_profile`", text)
            self.assertIn("selection_note: `safe default dry-run profile`", text)
            self.assertIn("final_status: `ready_for_operator_review`", text)
            self.assertIn("## Requested Lanes", text)
            self.assertIn("- refresh_workspace: `passed`", text)
            self.assertIn("## Unrequested Skipped Lanes", text)
            self.assertIn("- remote_plan", text)
            self.assertIn("## Passed Lanes", text)
            self.assertIn("## Failed Or Incomplete Lanes", text)
            self.assertIn("- none", text)
            self.assertIn("## Child Lane Reports", text)
            self.assertIn("- refresh_workspace: `artifacts/project_sync_workspace_generation_report.md`", text)
            self.assertIn("- child_report: `n/a`", text)
            self.assertNotIn("- remote_plan: `artifacts/project_sync_remote_plan_report.md`", text)


if __name__ == "__main__":
    unittest.main()
