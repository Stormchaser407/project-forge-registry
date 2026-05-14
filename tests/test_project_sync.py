from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path

from project_forge_registry.project_sync import (
    build_parser,
    build_lane_specs,
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

    def test_apply_is_rejected_in_phase_8_1(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--slug", "demo", "--apply"])
        with self.assertRaises(SystemExit):
            parse_mode(args, parser)

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

    def test_repo_scoped_paths_reject_outside_repo(self) -> None:
        with self.assertRaises(ValueError):
            resolve_repo_scoped_dir("/tmp/outside", "passport dir")

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
                    )
                ],
                final_status="ready_for_operator_review",
            )
            text = report_path.read_text(encoding="utf-8")
            self.assertIn("# Project Sync Report (Phase 8.1)", text)
            self.assertIn("final_status: `ready_for_operator_review`", text)


if __name__ == "__main__":
    unittest.main()
