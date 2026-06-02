from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from project_forge_registry.neon_command_board_launcher_apply import (
    APPROVAL_PHRASE,
    APPROVED_TARGET,
    ApplyOptions,
    build_payload,
    main,
    render_report,
    run_apply,
)


def write_preflight(root: Path, target: str = APPROVED_TARGET) -> None:
    artifacts = root / "artifacts"
    artifacts.mkdir()
    (artifacts / "neon_command_board_launcher_apply_preflight.json").write_text(
        json.dumps(
            {
                "phase": "Phase 11H.4",
                "mode": "dry-run/preflight only",
                "proposed_targets": [
                    {
                        "path": target,
                        "category": "user_desktop_entry",
                        "preflight_status": "review_required_no_apply",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


class NeonCommandBoardLauncherApplyTests(unittest.TestCase):
    def test_default_dry_run_refuses_real_apply_and_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            write_preflight(root)
            report_path = root / "artifacts" / "apply.md"
            json_path = root / "artifacts" / "apply.json"

            payload, code = run_apply(
                root=root,
                options=ApplyOptions(),
                report_path=report_path,
                json_path=json_path,
            )

            self.assertEqual(code, 0)
            self.assertTrue(payload["dry_run"])
            self.assertFalse(payload["apply_requested"])
            self.assertFalse(payload["real_apply_available"])
            self.assertFalse(payload["mutates_state"])
            self.assertTrue(report_path.exists())
            self.assertTrue(json_path.exists())

    def test_apply_only_refuses_without_other_guards(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            write_preflight(root)

            payload, code = run_apply(root=root, options=ApplyOptions(apply_requested=True))

            self.assertEqual(code, 2)
            self.assertTrue(payload["apply_requested"])
            self.assertFalse(payload["real_apply_available"])
            self.assertFalse(payload["mutates_state"])

    def test_approval_without_target_confirmation_refuses(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            write_preflight(root)

            payload, code = run_apply(
                root=root,
                options=ApplyOptions(
                    apply_requested=True,
                    yes_replace_launcher=True,
                    approval_phrase=APPROVAL_PHRASE,
                    target_path=APPROVED_TARGET,
                    clean_git_tree_confirmed=True,
                    expected_tag="v0.11.0h4-launcher-apply-preflight-dry-run",
                ),
            )

            self.assertEqual(code, 2)
            self.assertFalse(payload["real_apply_available"])
            triggered = [item["condition"] for item in payload["refusal_conditions"] if item["triggered"]]
            self.assertIn("exact target path confirmation required", triggered)

    def test_target_without_approval_phrase_refuses(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            write_preflight(root)

            payload, code = run_apply(
                root=root,
                options=ApplyOptions(
                    apply_requested=True,
                    yes_replace_launcher=True,
                    target_path=APPROVED_TARGET,
                    confirm_target_path=APPROVED_TARGET,
                    clean_git_tree_confirmed=True,
                    expected_tag="v0.11.0h4-launcher-apply-preflight-dry-run",
                ),
            )

            self.assertEqual(code, 2)
            triggered = [item["condition"] for item in payload["refusal_conditions"] if item["triggered"]]
            self.assertIn("exact approval phrase required", triggered)

    def test_guarded_apply_path_only_mutates_temp_fixture(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            write_preflight(root)
            target = root / "target.desktop"
            backup = root / "target.desktop.bak"
            target.write_text("old desktop content\n", encoding="utf-8")

            payload, code = run_apply(
                root=root,
                report_path=root / "artifacts" / "apply.md",
                json_path=root / "artifacts" / "apply.json",
                options=ApplyOptions(
                    apply_requested=True,
                    yes_replace_launcher=True,
                    approval_phrase=APPROVAL_PHRASE,
                    target_path=APPROVED_TARGET,
                    confirm_target_path=APPROVED_TARGET,
                    expected_tag="v0.11.0h4-launcher-apply-preflight-dry-run",
                    clean_git_tree_confirmed=True,
                    real_target_path=target,
                    backup_path=backup,
                    replacement_content="new desktop content\n",
                ),
            )

            self.assertEqual(code, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["mutates_state"])
            self.assertEqual(target.read_text(encoding="utf-8"), "new desktop content\n")
            self.assertEqual(backup.read_text(encoding="utf-8"), "old desktop content\n")

    def test_report_contains_required_safety_language(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            write_preflight(root)
            report = render_report(build_payload(root=root, options=ApplyOptions()))

            for text in (
                "Phase 11H.5",
                "guarded launcher replacement apply",
                "default dry-run",
                "no real apply unless all guards pass",
                "no mutation during dry-run",
                "no launch behavior",
                "no --open",
                "no systemd changes",
                "no desktop entry changes unless explicitly approved",
                "no autostart changes unless explicitly approved",
                "backup before overwrite",
                "rollback required",
                "no delete",
                "no vault writes",
                "exact approval phrase required",
                "exact target path confirmation required",
                "clean git tree required",
                APPROVAL_PHRASE,
            ):
                self.assertIn(text, report)

    def test_cli_refusal_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            write_preflight(root)
            report_path = root / "artifacts" / "cli.md"
            json_path = root / "artifacts" / "cli.json"

            with redirect_stdout(StringIO()):
                self.assertEqual(
                    main(
                        [
                            "--apply",
                            "--report-path",
                            str(report_path),
                            "--json-path",
                            str(json_path),
                        ]
                    ),
                    2,
                )


if __name__ == "__main__":
    unittest.main()
