from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from project_forge_registry.obsidian_mirror import (
    NOTE_FILENAMES,
    build_parser,
    load_dashboard_inventory,
    main,
    render_notes,
    run_obsidian_mirror,
)


def write_inventory(path: Path) -> None:
    payload = {
        "generated_by": "test",
        "mode": "read-only",
        "summary": {
            "total_projects": 4,
            "count_by_category": {
                "clean_candidate": 1,
                "dirty_candidate_review_first": 1,
                "known_embedded": 1,
                "protected_manual_review": 1,
            },
            "known_embedded_count": 1,
            "dirty_review_count": 1,
            "protected_review_count": 1,
        },
        "projects": [
            {
                "slug": "lifesaver-ledger",
                "path": "/projects/lifesaver-ledger",
                "category": "known_embedded",
                "git_status": "clean",
                "recommended_action": "embedded_ready",
                "launch_policy": {"status": "eligible"},
            },
            {
                "slug": "candidate",
                "path": "/projects/candidate",
                "category": "clean_candidate",
                "git_status": "clean",
                "recommended_action": "candidate_review",
                "launch_policy": {"status": "eligible"},
            },
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class ObsidianMirrorTests(unittest.TestCase):
    def test_parser_defaults_to_artifact_paths(self) -> None:
        args = build_parser().parse_args([])

        self.assertEqual(args.output_dir, "artifacts/obsidian_mirror")
        self.assertEqual(args.report_path, "artifacts/obsidian_mirror_report.md")
        self.assertEqual(args.manifest_path, "artifacts/obsidian_mirror_manifest.json")

    def test_missing_dashboard_inventory_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            missing = Path(tmp) / "missing.json"
            with self.assertRaisesRegex(FileNotFoundError, "Required dashboard inventory not found"):
                load_dashboard_inventory(missing)

    def test_cli_missing_dashboard_inventory_exits_clearly(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            missing = Path(tmp) / "missing.json"
            stderr = StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
                main(["--dashboard-inventory", str(missing)])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("project-forge-obsidian-mirror failed", stderr.getvalue())

    def test_mirror_command_creates_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            root = Path(tmp)
            inventory_path = root / "dashboard_inventory.json"
            output_dir = root / "obsidian_mirror"
            report_path = root / "obsidian_mirror_report.md"
            manifest_path = root / "obsidian_mirror_manifest.json"
            write_inventory(inventory_path)

            result = run_obsidian_mirror(
                dashboard_inventory=inventory_path,
                output_dir=output_dir,
                report_path=report_path,
                manifest_path=manifest_path,
                source_paths=[inventory_path],
            )

            self.assertTrue(output_dir.is_dir())
            self.assertEqual(len(result.note_paths), 5)
            self.assertTrue((output_dir / NOTE_FILENAMES["command_center"]).exists())
            self.assertTrue((output_dir / NOTE_FILENAMES["dashboard_summary"]).exists())
            self.assertTrue((output_dir / NOTE_FILENAMES["known_embedded"]).exists())
            self.assertTrue((output_dir / NOTE_FILENAMES["deferred_items"]).exists())
            self.assertTrue((output_dir / NOTE_FILENAMES["phase_11_planning"]).exists())
            self.assertTrue(report_path.exists())
            self.assertTrue(manifest_path.exists())

    def test_manifest_contains_generated_file_list(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            root = Path(tmp)
            inventory_path = root / "dashboard_inventory.json"
            output_dir = root / "obsidian_mirror"
            manifest_path = root / "obsidian_mirror_manifest.json"
            write_inventory(inventory_path)

            run_obsidian_mirror(
                dashboard_inventory=inventory_path,
                output_dir=output_dir,
                report_path=root / "obsidian_mirror_report.md",
                manifest_path=manifest_path,
                source_paths=[inventory_path],
            )

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["mode"], "dry-run artifact mirror")
            self.assertEqual(manifest["summary"]["total_notes_generated"], 5)
            self.assertEqual(len(manifest["generated_files"]), 5)
            self.assertIn(str((output_dir / NOTE_FILENAMES["command_center"]).relative_to(Path.cwd())), manifest["generated_files"])

    def test_notes_include_wiki_links_frontmatter_and_tags(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            inventory_path = Path(tmp) / "dashboard_inventory.json"
            write_inventory(inventory_path)
            state = run_obsidian_mirror(
                dashboard_inventory=inventory_path,
                output_dir=Path(tmp) / "obsidian_mirror",
                report_path=Path(tmp) / "report.md",
                manifest_path=Path(tmp) / "manifest.json",
                source_paths=[inventory_path],
            ).state

            notes = render_notes(state)
            combined = "\n".join(notes.values())
            self.assertIn('status: "dry-run artifact"', combined)
            self.assertIn("- project-forge", combined)
            self.assertIn("- phase-11", combined)
            self.assertIn("- dry-run", combined)
            self.assertIn("[[Project Forge - Dashboard Summary]]", combined)
            self.assertIn("[[Project Forge - Known Embedded Repos]]", combined)
            self.assertIn("[[Project Forge - Deferred Items]]", combined)
            self.assertIn("[[Project Forge - Phase 11 Planning]]", combined)

    def test_report_contains_safety_statement_and_counts(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            root = Path(tmp)
            inventory_path = root / "dashboard_inventory.json"
            report_path = root / "obsidian_mirror_report.md"
            write_inventory(inventory_path)

            run_obsidian_mirror(
                dashboard_inventory=inventory_path,
                output_dir=root / "obsidian_mirror",
                report_path=report_path,
                manifest_path=root / "obsidian_mirror_manifest.json",
                source_paths=[inventory_path],
            )

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("- mode: `dry-run artifact mirror`", report)
            self.assertIn("- total notes generated: `5`", report)
            self.assertIn("- known embedded repo count: `1`", report)
            self.assertIn("- no real Obsidian vault writes", report)
            self.assertIn("- no external repo writes", report)
            self.assertIn("- no apply", report)

    def test_generated_content_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            root = Path(tmp)
            inventory_path = root / "dashboard_inventory.json"
            write_inventory(inventory_path)

            first = run_obsidian_mirror(
                dashboard_inventory=inventory_path,
                output_dir=root / "one",
                report_path=root / "one_report.md",
                manifest_path=root / "one_manifest.json",
                source_paths=[inventory_path],
            )
            second = run_obsidian_mirror(
                dashboard_inventory=inventory_path,
                output_dir=root / "two",
                report_path=root / "two_report.md",
                manifest_path=root / "two_manifest.json",
                source_paths=[inventory_path],
            )

            first_notes = sorted(path.read_text(encoding="utf-8") for path in first.note_paths)
            second_notes = sorted(path.read_text(encoding="utf-8") for path in second.note_paths)
            self.assertEqual(first_notes, second_notes)

    def test_outputs_do_not_reference_real_vault_target(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            root = Path(tmp)
            inventory_path = root / "dashboard_inventory.json"
            output_dir = root / "obsidian_mirror"
            report_path = root / "report.md"
            write_inventory(inventory_path)

            run_obsidian_mirror(
                dashboard_inventory=inventory_path,
                output_dir=output_dir,
                report_path=report_path,
                manifest_path=root / "manifest.json",
                source_paths=[inventory_path],
            )

            combined = report_path.read_text(encoding="utf-8") + "\n".join(
                path.read_text(encoding="utf-8") for path in sorted(output_dir.glob("*.md"))
            )
            self.assertNotIn("/mnt/storage/Cole/main_vault", combined)


if __name__ == "__main__":
    unittest.main()
