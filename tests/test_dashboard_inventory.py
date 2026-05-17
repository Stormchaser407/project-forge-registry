from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from project_forge_registry.dashboard_inventory import (
    build_dashboard_inventory,
    derive_docs_light,
    derive_recommended_action,
    derive_repo_light,
    derive_risk_light,
    find_vscode_target,
    load_embed_plan_inventory,
    load_repo_discovery_inventory,
    run_dashboard_inventory,
    write_json,
    write_report,
)


def write_discovery_csv(path: Path, rows: list[str]) -> None:
    path.write_text(
        "slug,path,git_status,has_readme,has_agents,has_code_workspace,"
        "has_project_forge_marker,remote_count,category\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )


def write_embed_csv(path: Path, rows: list[str]) -> None:
    path.write_text(
        "slug,path,selected,eligible,decision,reason,marker_yaml,marker_doc,"
        "category,git_status\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )


class DashboardInventoryTests(unittest.TestCase):
    def test_load_repo_discovery_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "repo_discovery_inventory.csv"
            write_discovery_csv(
                csv_path,
                [
                    "demo,/tmp/demo,clean,true,false,false,false,2,clean_candidate",
                ],
            )

            rows = load_repo_discovery_inventory(csv_path)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].slug, "demo")
        self.assertEqual(rows[0].path, Path("/tmp/demo"))
        self.assertTrue(rows[0].has_readme)
        self.assertFalse(rows[0].has_project_forge_marker)
        self.assertEqual(rows[0].remote_count, 2)

    def test_load_embed_plan_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "embed_plan_inventory.csv"
            write_embed_csv(
                csv_path,
                [
                    "demo,/tmp/demo,true,false,already_embedded,done,"
                    "/tmp/demo/.project-forge.yml,"
                    "/tmp/demo/docs/PROJECT_FORGE.md,known_embedded,clean",
                ],
            )

            rows = load_embed_plan_inventory(csv_path)

        self.assertEqual(rows["demo"].decision, "already_embedded")
        self.assertEqual(rows["demo"].marker_yaml, Path("/tmp/demo/.project-forge.yml"))

    def test_merges_embed_decision_into_project_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery_csv = root / "repo_discovery_inventory.csv"
            embed_csv = root / "embed_plan_inventory.csv"
            write_discovery_csv(
                discovery_csv,
                [
                    f"demo,{root / 'demo'},clean,true,false,false,true,0,known_embedded",
                ],
            )
            write_embed_csv(
                embed_csv,
                [
                    f"demo,{root / 'demo'},true,false,already_embedded,done,"
                    f"{root / 'demo' / '.project-forge.yml'},"
                    f"{root / 'demo' / 'docs' / 'PROJECT_FORGE.md'},"
                    "known_embedded,clean",
                ],
            )

            projects = build_dashboard_inventory(
                load_repo_discovery_inventory(discovery_csv),
                load_embed_plan_inventory(embed_csv),
            )

        self.assertEqual(projects[0].embed_decision, "already_embedded")
        self.assertEqual(projects[0].marker_doc_path.name, "PROJECT_FORGE.md")

    def test_derives_lights(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery_csv = root / "repo_discovery_inventory.csv"
            write_discovery_csv(
                discovery_csv,
                [
                    "embedded,/tmp/embedded,clean,true,false,false,true,1,known_embedded",
                    "candidate,/tmp/candidate,clean,true,false,false,false,1,clean_candidate",
                    "dirty,/tmp/dirty,dirty,true,false,false,false,1,dirty_candidate_review_first",
                    "protected,/tmp/cerberus,clean,true,false,false,false,0,protected_manual_review",
                    "unknown,/tmp/unknown,unknown,false,false,false,false,0,unknown_structure",
                    "control,/tmp/project-forge-registry,clean,true,false,false,false,0,control_repo",
                ],
            )

            rows = {row.slug: row for row in load_repo_discovery_inventory(discovery_csv)}

        self.assertEqual(derive_repo_light(rows["embedded"]), "green")
        self.assertEqual(derive_docs_light(rows["embedded"]), "green")
        self.assertEqual(derive_risk_light(rows["embedded"]), "green")
        self.assertEqual(derive_repo_light(rows["candidate"]), "green")
        self.assertEqual(derive_docs_light(rows["candidate"]), "amber")
        self.assertEqual(derive_risk_light(rows["candidate"]), "amber")
        self.assertEqual(derive_risk_light(rows["dirty"]), "amber")
        self.assertEqual(derive_risk_light(rows["protected"]), "red")
        self.assertEqual(derive_docs_light(rows["unknown"]), "gray")
        self.assertEqual(derive_risk_light(rows["control"]), "blue")

    def test_derives_recommended_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery_csv = root / "repo_discovery_inventory.csv"
            write_discovery_csv(
                discovery_csv,
                [
                    "embedded,/tmp/embedded,clean,true,false,false,true,1,known_embedded",
                    "candidate,/tmp/candidate,clean,true,false,false,false,1,clean_candidate",
                    "dirty,/tmp/dirty,dirty,true,false,false,false,1,dirty_candidate_review_first",
                    "protected,/tmp/cerberus,clean,true,false,false,false,0,protected_manual_review",
                    "control,/tmp/project-forge-registry,clean,true,false,false,false,0,control_repo",
                    "unknown,/tmp/unknown,unknown,false,false,false,false,0,unknown_structure",
                ],
            )

            rows = {row.slug: row for row in load_repo_discovery_inventory(discovery_csv)}

        self.assertEqual(derive_recommended_action(rows["embedded"]), "embedded_ready")
        self.assertEqual(derive_recommended_action(rows["candidate"]), "candidate_review")
        self.assertEqual(derive_recommended_action(rows["dirty"]), "dirty_review_first")
        self.assertEqual(
            derive_recommended_action(rows["protected"]),
            "protected_manual_review",
        )
        self.assertEqual(
            derive_recommended_action(rows["control"]),
            "control_repo_no_embed",
        )
        self.assertEqual(derive_recommended_action(rows["unknown"]), "unknown_review")

    def test_detects_code_workspace_preference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "zeta.code-workspace").write_text("{}", encoding="utf-8")
            (repo / "alpha.code-workspace").write_text("{}", encoding="utf-8")

            target = find_vscode_target(repo)

        self.assertEqual(target.name, "alpha.code-workspace")

    def test_writes_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery_csv = root / "repo_discovery_inventory.csv"
            json_path = root / "dashboard_inventory.json"
            write_discovery_csv(
                discovery_csv,
                [
                    f"demo,{root / 'demo'},clean,true,false,false,false,0,clean_candidate",
                ],
            )
            projects = build_dashboard_inventory(load_repo_discovery_inventory(discovery_csv))

            write_json(json_path, projects)
            payload = json.loads(json_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["summary"]["total_projects"], 1)
        self.assertEqual(payload["projects"][0]["slug"], "demo")
        self.assertEqual(payload["projects"][0]["repo_light"], "green")

    def test_writes_markdown_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery_csv = root / "repo_discovery_inventory.csv"
            report_path = root / "dashboard_inventory_report.md"
            json_path = root / "dashboard_inventory.json"
            write_discovery_csv(
                discovery_csv,
                [
                    "embedded,/tmp/embedded,clean,true,false,false,true,0,known_embedded",
                    "dirty,/tmp/dirty,dirty,true,false,false,false,0,dirty_candidate_review_first",
                    "protected,/tmp/cerberus,clean,true,false,false,false,0,protected_manual_review",
                ],
            )
            projects = build_dashboard_inventory(load_repo_discovery_inventory(discovery_csv))

            write_report(report_path, json_path, projects)
            report = report_path.read_text(encoding="utf-8")

        self.assertIn("# Project Forge Dashboard Inventory Report", report)
        self.assertIn("- total_projects: `3`", report)
        self.assertIn("## Known Embedded Projects", report)
        self.assertIn("## Dirty Review Projects", report)
        self.assertIn("## Protected Review Projects", report)
        self.assertIn("- No external repos were modified.", report)

    def test_missing_optional_embed_plan_still_works(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery_csv = root / "repo_discovery_inventory.csv"
            json_path = root / "dashboard_inventory.json"
            report_path = root / "dashboard_inventory_report.md"
            write_discovery_csv(
                discovery_csv,
                [
                    f"demo,{root / 'demo'},clean,true,false,false,false,0,clean_candidate",
                ],
            )

            projects = run_dashboard_inventory(
                discovery_csv,
                root / "missing_embed_plan_inventory.csv",
                json_path,
                report_path,
            )

        self.assertEqual(len(projects), 1)
        self.assertIsNone(projects[0].embed_decision)

    def test_missing_required_discovery_inventory_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.csv"

            with self.assertRaises(FileNotFoundError) as ctx:
                load_repo_discovery_inventory(missing)

        self.assertIn("Required repo discovery inventory not found", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
