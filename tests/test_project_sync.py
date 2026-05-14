from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from project_forge_registry.project_sync import (
    build_parser,
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
                        command=["project-forge-workspace-generate", "--slug", "demo", "--dry-run"],
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
