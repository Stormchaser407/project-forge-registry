from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from project_forge_registry.neon_command_board import (
    collect_board_data,
    render_html,
    run_neon_command_board,
)


NOTE_NAMES = [
    "Project Forge - Command Center.md",
    "Project Forge - Dashboard Summary.md",
    "Project Forge - Deferred Items.md",
    "Project Forge - Known Embedded Repos.md",
    "Project Forge - Phase 11 Planning.md",
]


def write_inputs(root: Path) -> dict[str, Path]:
    artifacts = root / "artifacts"
    artifacts.mkdir()
    inventory = artifacts / "dashboard_inventory.json"
    inventory.write_text(
        json.dumps(
            {
                "projects": [
                    {"slug": "embedded", "recommended_action": "embedded_ready"},
                    {"slug": "dirty", "recommended_action": "dirty_review_first"},
                    {"slug": "protected", "recommended_action": "protected_manual_review"},
                    {"slug": "candidate", "recommended_action": "candidate_review"},
                    {"slug": "candidate-2", "recommended_action": "candidate_review"},
                ]
            }
        ),
        encoding="utf-8",
    )
    dry_run = artifacts / "obsidian_vault_apply_dry_run.json"
    dry_run.write_text(
        json.dumps(
            {
                "vault_root": "/tmp/vault/Project Forge",
                "entries_reviewed": 5,
                "would_create": 0,
                "would_skip_identical": 5,
                "blocked": 0,
                "entries": [
                    {"target_path": f"/tmp/vault/Project Forge/{name}"}
                    for name in NOTE_NAMES
                ],
            }
        ),
        encoding="utf-8",
    )
    plan = artifacts / "obsidian_vault_apply_plan.json"
    plan.write_text(json.dumps({"vault_root": "/tmp/vault/Project Forge"}), encoding="utf-8")
    real_apply = artifacts / "obsidian_vault_real_apply_report.md"
    real_apply.write_text("# real apply\n", encoding="utf-8")
    maintenance = artifacts / "obsidian_vault_maintenance_policy_report.md"
    maintenance.write_text("human-edited vault notes win\n", encoding="utf-8")
    return {
        "inventory": inventory,
        "dry_run": dry_run,
        "plan": plan,
        "real_apply": real_apply,
        "maintenance": maintenance,
        "html": artifacts / "neon_command_board.html",
        "report": artifacts / "neon_command_board_report.md",
        "manifest": artifacts / "neon_command_board_manifest.json",
    }


class NeonCommandBoardTests(unittest.TestCase):
    def test_generates_html_report_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            paths = write_inputs(Path(tmp))

            run_neon_command_board(
                inventory_json=paths["inventory"],
                dry_run_json=paths["dry_run"],
                plan_json=paths["plan"],
                real_apply_report=paths["real_apply"],
                maintenance_report=paths["maintenance"],
                output_html=paths["html"],
                report_path=paths["report"],
                manifest_path=paths["manifest"],
            )

            self.assertTrue(paths["html"].exists())
            self.assertTrue(paths["report"].exists())
            self.assertTrue(paths["manifest"].exists())
            json.loads(paths["manifest"].read_text(encoding="utf-8"))

    def test_required_panels_and_theme_markers_are_present(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            paths = write_inputs(Path(tmp))
            data = collect_board_data(
                inventory_json=paths["inventory"],
                dry_run_json=paths["dry_run"],
                plan_json=paths["plan"],
                real_apply_report=paths["real_apply"],
                maintenance_report=paths["maintenance"],
            )

            html = render_html(data)

            for text in (
                "Neon District / Punk Union",
                "System State",
                "Project Inventory",
                "Obsidian Memory Layer",
                "Safety Doctrine",
                "Actions / Command Copy Cards",
                "Warnings / Blockers",
                "Phase Roadmap",
            ):
                self.assertIn(text, html)

    def test_safety_doctrine_and_command_cards_are_present(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            paths = write_inputs(Path(tmp))
            data = collect_board_data(
                inventory_json=paths["inventory"],
                dry_run_json=paths["dry_run"],
                plan_json=paths["plan"],
                real_apply_report=paths["real_apply"],
                maintenance_report=paths["maintenance"],
            )
            html = render_html(data)

            self.assertIn("dry-run first", html)
            self.assertIn("create-only", html)
            self.assertIn("skip identical", html)
            self.assertIn("block different", html)
            self.assertIn("human-edited vault notes win", html)
            self.assertIn("no silent overwrite", html)
            self.assertIn("no delete", html)
            self.assertIn("./scripts/project-forge-cold-start", html)
            self.assertIn("PYTHONPATH=src python3 -m project_forge_registry.obsidian_vault_apply --dry-run", html)

    def test_unsafe_patterns_are_not_in_generated_html(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            paths = write_inputs(Path(tmp))
            data = collect_board_data(
                inventory_json=paths["inventory"],
                dry_run_json=paths["dry_run"],
                plan_json=paths["plan"],
                real_apply_report=paths["real_apply"],
                maintenance_report=paths["maintenance"],
            )
            html = render_html(data)

            for unsafe in (
                "--apply",
                "vscode://",
                "file://",
                "onclick=",
                "javascript:",
                "child_process",
                "subprocess",
                "exec(",
            ):
                self.assertNotIn(unsafe, html)

    def test_inventory_counts_and_obsidian_status_are_reflected(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            paths = write_inputs(Path(tmp))
            data = collect_board_data(
                inventory_json=paths["inventory"],
                dry_run_json=paths["dry_run"],
                plan_json=paths["plan"],
                real_apply_report=paths["real_apply"],
                maintenance_report=paths["maintenance"],
            )
            html = render_html(data)

            self.assertIn("<strong>5</strong>", html)
            self.assertIn("known embedded", html)
            self.assertIn("dirty review", html)
            self.assertIn("protected review", html)
            self.assertIn("candidate review", html)
            self.assertIn("5 notes reviewed; 5 skip-identical; 0 create; 0 blocked", html)
            self.assertIn("/tmp/vault/Project Forge", html)

    def test_manifest_is_deterministic_enough_for_tests(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            paths = write_inputs(Path(tmp))

            run_neon_command_board(
                inventory_json=paths["inventory"],
                dry_run_json=paths["dry_run"],
                plan_json=paths["plan"],
                real_apply_report=paths["real_apply"],
                maintenance_report=paths["maintenance"],
                output_html=paths["html"],
                report_path=paths["report"],
                manifest_path=paths["manifest"],
            )
            manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))

            self.assertEqual(manifest["mode"], "static local command board")
            self.assertEqual(manifest["theme"], "Neon District / Punk Union")
            self.assertFalse(manifest["safety"]["javascript"])
            self.assertFalse(manifest["safety"]["mutates_state"])
            self.assertEqual(manifest["project_inventory"]["total_projects"], 5)


if __name__ == "__main__":
    unittest.main()
