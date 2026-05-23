from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from project_forge_registry.obsidian_vault_plan import (
    DEFAULT_VAULT_ROOT,
    build_parser,
    load_manifest,
    main,
    run_vault_plan,
)


NOTE_NAMES = [
    "Project Forge - Command Center.md",
    "Project Forge - Dashboard Summary.md",
    "Project Forge - Known Embedded Repos.md",
    "Project Forge - Deferred Items.md",
    "Project Forge - Phase 11 Planning.md",
]


def write_mirror_fixture(root: Path) -> Path:
    mirror_dir = root / "artifacts" / "obsidian_mirror"
    mirror_dir.mkdir(parents=True)
    generated_files: list[str] = []
    for name in NOTE_NAMES:
        note_path = mirror_dir / name
        note_path.write_text(f"# {name}\n", encoding="utf-8")
        generated_files.append(str(note_path.relative_to(Path.cwd())))

    manifest_path = root / "artifacts" / "obsidian_mirror_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "generated_by": "test",
                "mode": "dry-run artifact mirror",
                "generated_files": generated_files,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest_path


class ObsidianVaultPlanTests(unittest.TestCase):
    def test_parser_defaults_to_phase_11b_paths(self) -> None:
        args = build_parser().parse_args([])

        self.assertEqual(args.manifest_path, "artifacts/obsidian_mirror_manifest.json")
        self.assertEqual(args.report_path, "artifacts/obsidian_vault_apply_plan.md")
        self.assertEqual(args.json_path, "artifacts/obsidian_vault_apply_plan.json")
        self.assertEqual(args.vault_root, str(DEFAULT_VAULT_ROOT))

    def test_missing_manifest_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            missing = Path(tmp) / "missing.json"
            with self.assertRaisesRegex(FileNotFoundError, "Required mirror manifest not found"):
                load_manifest(missing)

    def test_cli_missing_manifest_exits_clearly(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            missing = Path(tmp) / "missing.json"
            stderr = StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
                main(["--manifest-path", str(missing)])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("project-forge-obsidian-vault-plan failed", stderr.getvalue())

    def test_planner_creates_markdown_report_and_json_plan(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            manifest_path = write_mirror_fixture(root)
            report_path = root / "artifacts" / "obsidian_vault_apply_plan.md"
            json_path = root / "artifacts" / "obsidian_vault_apply_plan.json"

            plan = run_vault_plan(
                manifest_path=manifest_path,
                vault_root=Path(vault_tmp) / "Project Forge",
                report_path=report_path,
                json_path=json_path,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(json_path.exists())
            self.assertEqual(plan.source_note_count, 5)
            self.assertEqual(plan.proposed_target_count, 5)

    def test_plan_includes_all_five_notes_and_targets(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            manifest_path = write_mirror_fixture(root)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan = run_vault_plan(
                manifest_path=manifest_path,
                vault_root=vault_root,
                report_path=root / "artifacts" / "plan.md",
                json_path=root / "artifacts" / "plan.json",
            )

            targets = {entry.proposed_vault_target_path for entry in plan.entries}
            self.assertEqual({path.name for path in targets}, set(NOTE_NAMES))
            self.assertTrue(all(str(target).startswith(str(vault_root)) for target in targets))
            self.assertEqual({entry.action for entry in plan.entries}, {"would_create"})

    def test_existing_target_is_planned_as_update_without_writing(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            manifest_path = write_mirror_fixture(root)
            vault_root = Path(vault_tmp) / "Project Forge"
            vault_root.mkdir()
            existing = vault_root / NOTE_NAMES[0]
            existing.write_text("existing\n", encoding="utf-8")

            plan = run_vault_plan(
                manifest_path=manifest_path,
                vault_root=vault_root,
                report_path=root / "artifacts" / "plan.md",
                json_path=root / "artifacts" / "plan.json",
            )

            by_name = {entry.proposed_vault_target_path.name: entry for entry in plan.entries}
            self.assertEqual(by_name[NOTE_NAMES[0]].action, "would_update")
            self.assertEqual(existing.read_text(encoding="utf-8"), "existing\n")

    def test_no_real_vault_writes_occur_for_configurable_root(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            manifest_path = write_mirror_fixture(root)
            vault_root = Path(vault_tmp) / "Missing Project Forge"

            run_vault_plan(
                manifest_path=manifest_path,
                vault_root=vault_root,
                report_path=root / "artifacts" / "plan.md",
                json_path=root / "artifacts" / "plan.json",
            )

            self.assertFalse(vault_root.exists())

    def test_json_plan_contains_proposed_target_paths(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            manifest_path = write_mirror_fixture(root)
            json_path = root / "artifacts" / "plan.json"
            vault_root = Path(vault_tmp) / "Project Forge"

            run_vault_plan(
                manifest_path=manifest_path,
                vault_root=vault_root,
                report_path=root / "artifacts" / "plan.md",
                json_path=json_path,
            )

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["mode"], "dry-run vault apply plan")
            self.assertEqual(payload["vault_root"], str(vault_root))
            self.assertIn("vault_root_exists", payload)
            self.assertEqual(payload["source_note_count"], 5)
            self.assertEqual(payload["proposed_target_count"], 5)
            self.assertNotIn("vault_root_planned", payload)
            self.assertEqual(len(payload["entries"]), 5)
            for entry in payload["entries"]:
                self.assertIn("source_artifact_path", entry)
                self.assertIn("proposed_vault_target_path", entry)
                self.assertIn("action", entry)
                self.assertIn("target_exists", entry)
                self.assertIn("reason", entry)
                self.assertIn(str(vault_root), entry["proposed_vault_target_path"])

    def test_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            manifest_path = write_mirror_fixture(root)
            vault_root = Path(vault_tmp) / "Project Forge"

            run_vault_plan(
                manifest_path=manifest_path,
                vault_root=vault_root,
                report_path=root / "artifacts" / "one.md",
                json_path=root / "artifacts" / "one.json",
            )
            run_vault_plan(
                manifest_path=manifest_path,
                vault_root=vault_root,
                report_path=root / "artifacts" / "two.md",
                json_path=root / "artifacts" / "two.json",
            )

            one = json.loads((root / "artifacts" / "one.json").read_text(encoding="utf-8"))
            two = json.loads((root / "artifacts" / "two.json").read_text(encoding="utf-8"))
            one["report_path"] = "normalized"
            two["report_path"] = "normalized"
            self.assertEqual(one, two)

    def test_report_includes_safety_statement_and_proposed_root(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            manifest_path = write_mirror_fixture(root)
            report_path = root / "artifacts" / "plan.md"
            vault_root = Path(vault_tmp) / "Project Forge"

            run_vault_plan(
                manifest_path=manifest_path,
                vault_root=vault_root,
                report_path=report_path,
                json_path=root / "artifacts" / "plan.json",
            )

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("dry-run vault apply plan", report)
            self.assertIn("vault_root", report)
            self.assertIn(str(vault_root), report)
            self.assertIn("no real vault writes", report)
            self.assertIn("Phase 11B is planning only", report)


if __name__ == "__main__":
    unittest.main()
