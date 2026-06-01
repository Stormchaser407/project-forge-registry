from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from project_forge_registry.neon_command_board_launcher_apply_preflight import (
    APPROVAL_PHRASE,
    build_preflight,
    render_report,
    run_preflight,
)


def write_prior_artifacts(root: Path) -> None:
    artifacts = root / "artifacts"
    artifacts.mkdir()
    (artifacts / "neon_command_board_launcher_discovery.json").write_text(
        json.dumps(
            {
                "phase": "Phase 11H.1",
                "mode": "dry-run discovery",
                "mutates_state": False,
                "candidates": [
                    {
                        "category": "user_desktop_entry",
                        "target": "user_applications",
                        "path": "~/.local/share/applications/project-forge-command-board.desktop",
                        "status": "review_only",
                        "matched_terms": ["Project Forge", "project-forge"],
                    },
                    {
                        "category": "repo_launcher",
                        "target": "repo_scripts",
                        "path": "scripts/project-forge-neon-command-board",
                        "status": "review_neon_candidate",
                        "matched_terms": ["project-forge-neon-command-board"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (artifacts / "neon_command_board_replacement_review_plan.json").write_text(
        json.dumps(
            {
                "phase": "Phase 11H.2",
                "mode": "planning_only",
                "old_target_candidates": [
                    {
                        "path": "~/.local/share/applications/project-forge-command-board.desktop",
                        "operator_review_required": True,
                    }
                ],
                "neon_target_candidates": [
                    {
                        "wrapper_command": "./scripts/project-forge-neon-command-board",
                        "module_command": "PYTHONPATH=src python3 -m project_forge_registry.neon_command_board",
                        "output_artifact": "artifacts/neon_command_board.html",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (artifacts / "neon_command_board_guarded_launcher_apply_design.json").write_text(
        json.dumps(
            {
                "phase": "Phase 11H.3",
                "mode": "design_only",
                "design_only": True,
                "future_approval_phrase": APPROVAL_PHRASE,
            }
        ),
        encoding="utf-8",
    )


class NeonCommandBoardLauncherApplyPreflightTests(unittest.TestCase):
    def test_builds_dry_run_preflight_without_real_apply(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            write_prior_artifacts(root)

            preflight = build_preflight(root=root)

            self.assertEqual(preflight["phase"], "Phase 11H.4")
            self.assertEqual(preflight["mode"], "dry-run/preflight only")
            self.assertTrue(preflight["dry_run"])
            self.assertTrue(preflight["preflight_only"])
            self.assertFalse(preflight["real_apply_available"])
            self.assertFalse(preflight["mutates_state"])
            self.assertEqual(preflight["approval_phrase_status"], "inert_in_11h4")
            self.assertEqual(len(preflight["candidate_targets"]), 2)
            self.assertEqual(len(preflight["proposed_targets"]), 1)
            self.assertFalse(preflight["simulated_backup_manifest"][0]["backup_created"])
            self.assertFalse(preflight["all_or_nothing_preflight"]["passes_for_real_apply"])

    def test_missing_prior_artifacts_are_refusal_not_destructive_failure(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            (root / "artifacts").mkdir()

            preflight = build_preflight(root=root)

            checked = preflight["prior_artifacts_checked"]
            self.assertTrue(any(not item["present"] for item in checked))
            self.assertEqual(preflight["candidate_targets"], [])
            self.assertEqual(preflight["proposed_targets"], [])
            triggered = preflight["all_or_nothing_preflight"]["triggered_refusals"]
            self.assertIn("missing prior artifact", triggered)
            self.assertIn("candidate discovery unavailable", triggered)

    def test_run_writes_markdown_and_json_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            write_prior_artifacts(root)
            report_path = root / "artifacts" / "preflight.md"
            json_path = root / "artifacts" / "preflight.json"

            run_preflight(root=root, report_path=report_path, json_path=json_path)

            self.assertTrue(report_path.exists())
            self.assertTrue(json_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["phase"], "Phase 11H.4")
            self.assertIn("dry-run/preflight only", report_path.read_text(encoding="utf-8"))

    def test_report_contains_required_safety_language(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            write_prior_artifacts(root)
            report = render_report(build_preflight(root=root))

            for text in (
                "Phase 11H.4",
                "dry-run/preflight only",
                "no real apply",
                "no replacement",
                "no mutation",
                "no backups created",
                "simulated backup manifest",
                "simulated rollback plan",
                "no autostart changes",
                "no systemd changes",
                "no desktop entry changes",
                "no --open",
                "no launch behavior",
                "no vault writes",
                "approval phrase inert in 11H.4",
                "real apply remains future phase only",
                "all-or-nothing preflight",
                APPROVAL_PHRASE,
            ):
                self.assertIn(text, report)

    def test_apply_flag_is_rejected_by_parser(self) -> None:
        from project_forge_registry.neon_command_board_launcher_apply_preflight import main

        with redirect_stdout(StringIO()):
            self.assertEqual(main(["--apply"]), 2)

    def test_unsafe_patterns_are_absent_from_report(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as repo_tmp:
            root = Path(repo_tmp)
            write_prior_artifacts(root)
            report = render_report(build_preflight(root=root))

            unsafe_patterns = (
                "vscode:" + "//",
                "file:" + "//",
                "on" + "click=",
                "java" + "script:",
            )
            for unsafe in unsafe_patterns:
                self.assertNotIn(unsafe, report)


if __name__ == "__main__":
    unittest.main()
