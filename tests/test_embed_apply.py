from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from project_forge_registry.embed_apply import (
    EmbedApplyRow,
    apply_marker,
    derive_final_status,
    is_safe_apply_row,
)


def row(slug: str = "demo") -> EmbedApplyRow:
    return EmbedApplyRow(
        slug=slug,
        path=Path("/tmp") / slug,
        selected=True,
        eligible=True,
        decision="plan_marker_write",
        reason="ok",
        marker_yaml=Path("/tmp") / slug / ".project-forge.yml",
        marker_doc=Path("/tmp") / slug / "docs" / "PROJECT_FORGE.md",
        category="clean_candidate",
        git_status="clean",
    )


class EmbedApplyTests(unittest.TestCase):
    def test_safe_apply_row_accepts_selected_clean_candidate(self) -> None:
        safe, reason = is_safe_apply_row(row())
        self.assertTrue(safe)
        self.assertEqual(reason, "ok")

    def test_safe_apply_row_rejects_unselected(self) -> None:
        item = row()
        item = EmbedApplyRow(
            item.slug, item.path, False, item.eligible, item.decision, item.reason,
            item.marker_yaml, item.marker_doc, item.category, item.git_status
        )
        safe, reason = is_safe_apply_row(item)
        self.assertFalse(safe)
        self.assertEqual(reason, "not selected")

    def test_safe_apply_row_rejects_protected(self) -> None:
        item = row("cerberus")
        item = EmbedApplyRow(
            item.slug, Path("/tmp/cerberus"), item.selected, item.eligible, item.decision,
            item.reason, item.marker_yaml, item.marker_doc, "protected_manual_review", item.git_status
        )
        safe, reason = is_safe_apply_row(item)
        self.assertFalse(safe)
        self.assertIn("category", reason)

    def test_apply_marker_writes_files_for_clean_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            repo.mkdir()
            (repo / ".git").mkdir()

            item = EmbedApplyRow(
                slug="demo",
                path=repo,
                selected=True,
                eligible=True,
                decision="plan_marker_write",
                reason="ok",
                marker_yaml=repo / ".project-forge.yml",
                marker_doc=repo / "docs" / "PROJECT_FORGE.md",
                category="clean_candidate",
                git_status="clean",
            )

            with patch("project_forge_registry.embed_apply.git_status", return_value="clean"):
                result = apply_marker(item)

            self.assertEqual(result.status, "written")
            self.assertTrue((repo / ".project-forge.yml").exists())
            self.assertTrue((repo / "docs" / "PROJECT_FORGE.md").exists())

    def test_apply_marker_blocks_existing_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            repo.mkdir()
            (repo / ".git").mkdir()
            (repo / ".project-forge.yml").write_text("existing\n", encoding="utf-8")

            item = EmbedApplyRow(
                slug="demo",
                path=repo,
                selected=True,
                eligible=True,
                decision="plan_marker_write",
                reason="ok",
                marker_yaml=repo / ".project-forge.yml",
                marker_doc=repo / "docs" / "PROJECT_FORGE.md",
                category="clean_candidate",
                git_status="clean",
            )

            with patch("project_forge_registry.embed_apply.git_status", return_value="clean"):
                result = apply_marker(item)

            self.assertEqual(result.status, "blocked")
            self.assertIn("already exists", result.note)

    def test_final_status_applied_for_written(self) -> None:
        result = apply_marker
        self.assertEqual(
            derive_final_status([
                type("R", (), {"status": "written"})(),
            ]),
            "applied_for_operator_review",
        )


if __name__ == "__main__":
    unittest.main()
