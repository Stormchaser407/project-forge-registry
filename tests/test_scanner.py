from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from project_forge_registry.reporting import build_registry_record
from project_forge_registry import scanner
from project_forge_registry.scanner import scan_project_dir, slugify


class ScannerTests(unittest.TestCase):
    def test_slugify_basic(self) -> None:
        self.assertEqual(slugify("My Cool Project!"), "my_cool_project")

    def test_scan_project_dir_detects_expected_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp) / "Example Project"
            project_dir.mkdir()
            (project_dir / ".git").mkdir()
            (project_dir / "README.md").write_text("hello", encoding="utf-8")
            (project_dir / "package.json").write_text("{}", encoding="utf-8")
            (project_dir / ".env").write_text("SECRET=1", encoding="utf-8")
            (project_dir / "node_modules").mkdir()
            (project_dir / "app.db").write_text("", encoding="utf-8")

            result = scan_project_dir(project_dir)

        self.assertTrue(result.has_git)
        self.assertTrue(result.has_readme)
        self.assertTrue(result.has_package_json)
        self.assertTrue(result.has_env_files)
        self.assertTrue(result.has_node_modules)
        self.assertTrue(result.has_sqlite_or_db_files)
        self.assertIn("node", result.likely_stack)
        self.assertIn("contains_env_files", result.safety_warnings)
        self.assertEqual(result.recommended_action, "review_required")

    def test_registry_record_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp) / "sample"
            project_dir.mkdir()
            result = scan_project_dir(project_dir)

        record = build_registry_record(result)

        self.assertEqual(record["status"], "review")
        self.assertEqual(record["classification"], result.recommended_category)
        self.assertFalse(record["sync"]["allow_code_to_obsidian"])
        self.assertTrue(record["automation"]["require_safety_check_before_push"])

    def test_system_bound_override_for_cerberus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp) / "cerberus"
            project_dir.mkdir()
            original = dict(scanner.PATH_CLASSIFICATION_OVERRIDES)
            scanner.PATH_CLASSIFICATION_OVERRIDES[str(project_dir.resolve())] = {
                "recommended_category": "system_bound_project",
                "recommended_status": "active_special_case",
                "recommended_action": "document_only_for_now",
                "canonical_path": str(project_dir.resolve()),
                "do_not_move": True,
                "do_not_delete": False,
                "exclude_from_bulk_sync": True,
                "obsidian_note_policy": "high_level_notes_only",
                "extra_warnings": [
                    "system_bound_path",
                    "no_bulk_sync_automation",
                    "obsidian_high_level_notes_only",
                ],
            }
            try:
                result = scan_project_dir(project_dir)
            finally:
                scanner.PATH_CLASSIFICATION_OVERRIDES.clear()
                scanner.PATH_CLASSIFICATION_OVERRIDES.update(original)

        self.assertEqual(result.recommended_category, "system_bound_project")
        self.assertEqual(result.recommended_status, "active_special_case")
        self.assertEqual(result.recommended_action, "document_only_for_now")
        self.assertTrue(result.do_not_move)
        self.assertTrue(result.exclude_from_bulk_sync)
        self.assertEqual(result.obsidian_note_policy, "high_level_notes_only")


if __name__ == "__main__":
    unittest.main()
