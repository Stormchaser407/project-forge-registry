from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from project_forge_registry.obsidian_vault_apply import (
    build_parser,
    load_json_plan,
    main,
    run_apply_command,
)


NOTE_NAMES = [
    "Project Forge - Command Center.md",
    "Project Forge - Dashboard Summary.md",
    "Project Forge - Known Embedded Repos.md",
    "Project Forge - Deferred Items.md",
    "Project Forge - Phase 11 Planning.md",
]


def write_fixture(root: Path, vault_root: Path) -> tuple[Path, Path]:
    source_root = root / "artifacts" / "obsidian_mirror"
    source_root.mkdir(parents=True)
    entries = []
    for name in NOTE_NAMES:
        source_path = source_root / name
        source_path.write_text(f"# {name}\n", encoding="utf-8")
        entries.append(
            {
                "source_artifact_path": str(source_path.relative_to(Path.cwd())),
                "proposed_vault_target_path": str(vault_root / name),
                "action": "would_create",
                "target_exists": False,
                "reason": "fixture",
            }
        )
    plan_path = root / "artifacts" / "obsidian_vault_apply_plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "generated_by": "test",
                "mode": "dry-run vault apply plan",
                "vault_root": str(vault_root),
                "vault_root_exists": vault_root.exists(),
                "source_note_count": len(entries),
                "proposed_target_count": len(entries),
                "entries": entries,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return plan_path, source_root


class ObsidianVaultApplyTests(unittest.TestCase):
    def test_default_command_is_dry_run(self) -> None:
        args = build_parser().parse_args([])

        self.assertFalse(args.apply)
        self.assertFalse(args.dry_run)

    def test_dry_run_writes_only_repo_local_reports(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan_path, source_root = write_fixture(root, vault_root)
            report_path = root / "artifacts" / "dry_run.md"
            json_path = root / "artifacts" / "dry_run.json"

            result = run_apply_command(
                plan_path=plan_path,
                source_root=source_root,
                vault_root=None,
                apply_requested=False,
                yes_write_to_vault=False,
                report_path=report_path,
                json_path=json_path,
            )

            self.assertEqual(result.mode, "dry-run")
            self.assertTrue(report_path.exists())
            self.assertTrue(json_path.exists())
            self.assertFalse(vault_root.exists())

    def test_apply_without_yes_write_to_vault_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan_path, source_root = write_fixture(root, vault_root)

            with self.assertRaisesRegex(ValueError, "--apply requires --yes-write-to-vault"):
                run_apply_command(
                    plan_path=plan_path,
                    source_root=source_root,
                    vault_root=vault_root,
                    apply_requested=True,
                    yes_write_to_vault=False,
                    report_path=root / "artifacts" / "apply.md",
                    json_path=root / "artifacts" / "apply.json",
                )

    def test_apply_with_missing_source_is_rejected_before_writes(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan_path, source_root = write_fixture(root, vault_root)
            missing_source = source_root / NOTE_NAMES[0]
            missing_source.unlink()

            with self.assertRaisesRegex(ValueError, "apply preflight blocked"):
                run_apply_command(
                    plan_path=plan_path,
                    source_root=source_root,
                    vault_root=vault_root,
                    apply_requested=True,
                    yes_write_to_vault=True,
                    report_path=root / "artifacts" / "apply.md",
                    json_path=root / "artifacts" / "apply.json",
                )

            self.assertFalse(vault_root.exists())

    def test_plan_mode_must_be_dry_run_vault_apply_plan(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan_path, _source_root = write_fixture(root, vault_root)
            payload = json.loads(plan_path.read_text(encoding="utf-8"))
            payload["mode"] = "apply"
            plan_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "vault apply plan mode must be"):
                load_json_plan(plan_path)

    def test_plan_entries_are_required(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan_path, _source_root = write_fixture(root, vault_root)
            payload = json.loads(plan_path.read_text(encoding="utf-8"))
            payload["entries"] = []
            plan_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "non-empty entries list"):
                load_json_plan(plan_path)

    def test_apply_with_existing_different_target_is_rejected_before_writes(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan_path, source_root = write_fixture(root, vault_root)
            vault_root.mkdir()
            existing = vault_root / NOTE_NAMES[0]
            existing.write_text("different\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "apply preflight blocked"):
                run_apply_command(
                    plan_path=plan_path,
                    source_root=source_root,
                    vault_root=vault_root,
                    apply_requested=True,
                    yes_write_to_vault=True,
                    report_path=root / "artifacts" / "apply.md",
                    json_path=root / "artifacts" / "apply.json",
                )

            self.assertEqual(existing.read_text(encoding="utf-8"), "different\n")
            self.assertEqual(len(list(vault_root.glob("*.md"))), 1)

    def test_apply_with_temp_vault_root_creates_files_with_required_flags(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan_path, source_root = write_fixture(root, vault_root)

            result = run_apply_command(
                plan_path=plan_path,
                source_root=source_root,
                vault_root=vault_root,
                apply_requested=True,
                yes_write_to_vault=True,
                report_path=root / "artifacts" / "apply.md",
                json_path=root / "artifacts" / "apply.json",
            )

            self.assertEqual({entry.action for entry in result.entries}, {"created"})
            self.assertEqual(len(list(vault_root.glob("*.md"))), 5)

    def test_apply_is_all_or_nothing(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan_path, source_root = write_fixture(root, vault_root)
            (source_root / NOTE_NAMES[-1]).unlink()

            with self.assertRaisesRegex(ValueError, "apply preflight blocked"):
                run_apply_command(
                    plan_path=plan_path,
                    source_root=source_root,
                    vault_root=vault_root,
                    apply_requested=True,
                    yes_write_to_vault=True,
                    report_path=root / "artifacts" / "apply.md",
                    json_path=root / "artifacts" / "apply.json",
                )

            self.assertFalse(vault_root.exists())

    def test_identical_existing_target_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan_path, source_root = write_fixture(root, vault_root)
            vault_root.mkdir()
            identical = vault_root / NOTE_NAMES[0]
            identical.write_text((source_root / NOTE_NAMES[0]).read_text(encoding="utf-8"), encoding="utf-8")

            result = run_apply_command(
                plan_path=plan_path,
                source_root=source_root,
                vault_root=vault_root,
                apply_requested=False,
                yes_write_to_vault=False,
                report_path=root / "artifacts" / "dry_run.md",
                json_path=root / "artifacts" / "dry_run.json",
            )

            by_name = {entry.target_path.name: entry for entry in result.entries}
            self.assertEqual(by_name[NOTE_NAMES[0]].action, "would_skip_identical")

    def test_reports_include_safety_statement_and_json_is_valid(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan_path, source_root = write_fixture(root, vault_root)
            report_path = root / "artifacts" / "dry_run.md"
            json_path = root / "artifacts" / "dry_run.json"

            run_apply_command(
                plan_path=plan_path,
                source_root=source_root,
                vault_root=None,
                apply_requested=False,
                yes_write_to_vault=False,
                report_path=report_path,
                json_path=json_path,
            )

            report = report_path.read_text(encoding="utf-8")
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertIn("no real vault writes in dry-run", report)
            self.assertIn("create-only", report)
            self.assertIn("no overwrite", report)
            self.assertIn("no delete", report)
            self.assertTrue(payload["safety"]["all_or_nothing"])
            self.assertEqual(len(payload["entries"]), 5)

    def test_cli_apply_without_yes_exits_cleanly(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, tempfile.TemporaryDirectory() as vault_tmp:
            root = Path(tmp)
            vault_root = Path(vault_tmp) / "Project Forge"
            plan_path, source_root = write_fixture(root, vault_root)
            stderr = StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
                main(
                    [
                        "--apply",
                        "--vault-root",
                        str(vault_root),
                        "--plan",
                        str(plan_path),
                        "--source-root",
                        str(source_root),
                    ]
                )

            self.assertEqual(raised.exception.code, 2)
            self.assertIn("--apply requires --yes-write-to-vault", stderr.getvalue())
            self.assertFalse(vault_root.exists())

    def test_real_vault_path_is_never_used_in_tests(self) -> None:
        self.assertNotIn("/mnt/storage/Cole/main_vault", str(Path(tempfile.gettempdir())))


if __name__ == "__main__":
    unittest.main()
