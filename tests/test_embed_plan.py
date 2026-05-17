from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from project_forge_registry.embed_plan import (
    RepoInventoryRow,
    build_plan,
    derive_final_status,
    run_embed_plan,
)


def row(
    slug: str,
    category: str = "clean_candidate",
    git_status: str = "clean",
    has_project_forge_marker: bool = False,
) -> RepoInventoryRow:
    return RepoInventoryRow(
        slug=slug,
        path=Path("/tmp") / slug,
        git_status=git_status,
        has_readme=True,
        has_agents=False,
        has_code_workspace=False,
        has_project_forge_marker=has_project_forge_marker,
        remote_count=0,
        category=category,
    )


class EmbedPlanTests(unittest.TestCase):
    def test_selected_clean_candidate_plans_marker_write(self) -> None:
        items = build_plan([row("demo")], {"demo"})

        self.assertEqual(items[0].decision, "plan_marker_write")
        self.assertTrue(items[0].eligible)
        self.assertTrue(items[0].selected)

    def test_unselected_clean_candidate_is_not_selected(self) -> None:
        items = build_plan([row("demo")], set())

        self.assertEqual(items[0].decision, "candidate_not_selected")
        self.assertFalse(items[0].selected)

    def test_dirty_selected_repo_blocks(self) -> None:
        items = build_plan([row("demo", git_status="dirty")], {"demo"})

        self.assertEqual(items[0].decision, "blocked_dirty")
        self.assertEqual(derive_final_status(items), "blocked")

    def test_protected_selected_repo_blocks(self) -> None:
        items = build_plan([row("cerberus", category="protected_manual_review")], {"cerberus"})

        self.assertEqual(items[0].decision, "blocked_protected")
        self.assertEqual(derive_final_status(items), "blocked")

    def test_control_repo_is_skipped(self) -> None:
        items = build_plan([row("project-forge-registry", category="control_repo")], {"project-forge-registry"})

        self.assertEqual(items[0].decision, "skip_control_repo")

    def test_final_status_incomplete_when_nothing_selected(self) -> None:
        items = build_plan([row("demo")], set())

        self.assertEqual(derive_final_status(items), "incomplete")

    def test_final_status_ready_when_selected_clean_candidate(self) -> None:
        items = build_plan([row("demo")], {"demo"})

        self.assertEqual(derive_final_status(items), "ready_for_operator_review")

    def test_final_status_ready_when_selected_repo_already_embedded(self) -> None:
        items = build_plan(
            [
                row(
                    "demo",
                    category="known_embedded",
                    has_project_forge_marker=True,
                )
            ],
            {"demo"},
        )

        self.assertEqual(items[0].decision, "already_embedded")
        self.assertFalse(items[0].eligible)
        self.assertEqual(derive_final_status(items), "ready_for_operator_review")

    def test_final_status_ready_when_all_selected_repos_already_embedded(self) -> None:
        items = build_plan(
            [
                row(
                    "demo-one",
                    category="known_embedded",
                    has_project_forge_marker=True,
                ),
                row(
                    "demo-two",
                    category="known_embedded",
                    has_project_forge_marker=True,
                ),
            ],
            {"demo-one", "demo-two"},
        )

        self.assertEqual([item.decision for item in items], ["already_embedded", "already_embedded"])
        self.assertEqual(derive_final_status(items), "ready_for_operator_review")

    def test_run_embed_plan_writes_report_and_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_csv = root / "inventory.csv"
            report = root / "report.md"
            output_csv = root / "plan.csv"

            input_csv.write_text(
                "slug,path,git_status,has_readme,has_agents,has_code_workspace,has_project_forge_marker,remote_count,category\n"
                "demo,/tmp/demo,clean,true,false,false,false,0,clean_candidate\n",
                encoding="utf-8",
            )

            final_status = run_embed_plan(input_csv, {"demo"}, report, output_csv)
            report_text = report.read_text(encoding="utf-8")
            csv_text = output_csv.read_text(encoding="utf-8")

        self.assertEqual(final_status, "ready_for_operator_review")
        self.assertIn("# Project Forge Embed Plan Report", report_text)
        self.assertIn("- No marker files were written.", report_text)
        self.assertIn("demo,/tmp/demo,true,true,plan_marker_write", csv_text)


if __name__ == "__main__":
    unittest.main()
