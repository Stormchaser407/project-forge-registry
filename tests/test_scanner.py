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
        self.assertFalse(record["sync"]["do_not_sync"])
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
                "do_not_sync": True,
                "exclude_from_bulk_sync": True,
                "obsidian_note_policy": "high_level_notes_only",
                "extra_warnings": [
                    "system_bound_path",
                    "do_not_sync",
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
        self.assertTrue(result.do_not_sync)
        self.assertTrue(result.exclude_from_bulk_sync)
        self.assertEqual(result.obsidian_note_policy, "high_level_notes_only")

    def test_cerberus_named_project_is_protected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp) / "Cerberus"
            project_dir.mkdir()
            (project_dir / ".git").mkdir()
            (project_dir / "README.md").write_text("hello", encoding="utf-8")

            result = scan_project_dir(project_dir)

        self.assertEqual(result.recommended_category, "reconciliation_required")
        self.assertEqual(result.recommended_action, "review_required")
        self.assertTrue(result.do_not_sync)
        self.assertIn("cerberus_special_case_candidate", result.safety_warnings)
        self.assertIn("cerberus_name_requires_manual_reconciliation_review", result.safety_warnings)

    def test_cerberus_related_project_is_not_normal_active_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp) / "cerberus_case_workspace"
            project_dir.mkdir()
            (project_dir / ".git").mkdir()
            (project_dir / "README.md").write_text("hello", encoding="utf-8")

            result = scan_project_dir(project_dir)

        self.assertEqual(result.recommended_category, "unknown")
        self.assertEqual(result.recommended_action, "review_required")
        self.assertTrue(result.do_not_sync)
        self.assertIn("cerberus_special_case_candidate", result.safety_warnings)
        self.assertIn("cerberus_related_project_requires_manual_review", result.safety_warnings)


if __name__ == "__main__":
    unittest.main()
